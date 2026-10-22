"""Tro ly phan tich (AI agent): tra loi cau hoi bang tieng Viet bang cach GOI CAC HAM PHAN TICH CO SAN cua he thong
(danh sach canh bao, truy vet, de xuat xu ly, KPI chi nhanh) va truy van SQL chi doc tren kho. Moi con so trong cau
tra loi phai lay tu ket qua cong cu; mo hinh chi dieu phoi va dien dat. Khong doc ground_truth/ hay simulator/.

Nha cung cap mo hinh chon bang bien moi truong:
  FASTFAT_LLM_PROVIDER=anthropic (mac dinh) + ANTHROPIC_API_KEY
  FASTFAT_LLM_PROVIDER=bedrock   + AWS_REGION va thong tin xac thuc AWS (bien moi truong, ~/.aws, hoac IAM role)
"""
import json
import math
import os
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import date

import duckdb
import numpy as np
import pandas as pd

from . import actions
from . import safe_sql
from . import config as C
from . import detect

MODEL = "claude-opus-5-5"
PRICE_IN, PRICE_OUT = 4.0, 20.0          # USD / 1 trieu token, gia Claude API cong khai cua Claude Opus 5.5
MAX_STEPS = 8                            # so vong goi cong cu toi da cho mot cau hoi
SQL_ROW_LIMIT, SQL_TIMEOUT = 200, 15


class NoCredentials(RuntimeError):
    pass


# ------------------------------------------------------------------ ket noi mo hinh
def configured():
    """Da cau hinh mo hinh chua (chi doc bien moi truong, khong nap thu vien). Ung dung an trang tro ly neu chua."""
    if os.environ.get("FASTFAT_LLM_PROVIDER", "anthropic").lower() == "bedrock":
        return bool(os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION"))
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def make_client():
    """(client, ten mo hinh, tham so them, ten nha cung cap). Bao NoCredentials neu chua cau hinh."""
    import anthropic
    provider = os.environ.get("FASTFAT_LLM_PROVIDER", "anthropic").lower()
    if provider == "bedrock":
        region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
        if not region:
            raise NoCredentials("Chưa đặt AWS_REGION cho Amazon Bedrock.")
        client = anthropic.AnthropicBedrockMantle(aws_region=region)
        return client, f"anthropic.{MODEL}", {}, "Amazon Bedrock"
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        raise NoCredentials("Chưa đặt ANTHROPIC_API_KEY.")
    # Claude API: neu mo hinh tu choi vi bo loc an toan, may chu tu chuyen sang mo hinh du phong
    return anthropic.Anthropic(), MODEL, {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}, \
        "Claude API"


# ------------------------------------------------------------------ cong cu
def _num(x, d=0):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(float(x), d) if d else int(round(float(x)))


def _monday(s):
    d = pd.Timestamp(s)
    return d - pd.Timedelta(days=d.weekday())


TOOLS = [
    {"name": "list_alerts",
     "description": "Danh sách cảnh báo và mục cần theo dõi do bộ phát hiện tìm ra, theo chi nhánh × tuần, kèm nghi vấn "
                    "nguyên nhân, điểm bằng chứng, ước tính thiệt hại (VND) và người phụ trách. Dùng khi hỏi chi nhánh "
                    "nào có vấn đề, nên ưu tiên xử lý gì, tình hình cảnh báo trong một khoảng thời gian.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["start_date", "end_date", "branch_id", "level"],
                      "properties": {
                          "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                          "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                          "branch_id": {"type": ["integer", "null"], "description": "1-11, null = toàn chuỗi"},
                          "level": {"type": "string", "enum": ["Cảnh báo", "Theo dõi", "tất cả"]}}}},
    {"name": "trace_branch_week",
     "description": "Truy vết một chi nhánh trong một tuần: doanh thu thực tế so với mức kỳ vọng (đã trừ biến động chung "
                    "của nhóm cùng hạng), phân rã theo kênh (số đơn, giá trị đơn), điểm của từng giả thuyết nguyên nhân "
                    "kèm bằng chứng, và đề xuất xử lý (xác minh, xử lý, theo dõi, ảnh hưởng ước tính).",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["branch_id", "week_start"],
                      "properties": {"branch_id": {"type": "integer"},
                                     "week_start": {"type": "string", "description": "Một ngày bất kỳ trong tuần, YYYY-MM-DD"}}}},
    {"name": "branch_kpis",
     "description": "KPI tổng hợp theo chi nhánh trong một khoảng ngày: doanh thu thuần, số đơn, AOV, COGS% định mức, "
                    "Labor% (lương giờ trực tiếp), cơ cấu kênh, và trung vị nhóm chi nhánh cùng hạng để so sánh.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["start_date", "end_date", "branch_id"],
                      "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"},
                                     "branch_id": {"type": ["integer", "null"], "description": "null = mọi chi nhánh"}}}},
    {"name": "list_tables",
     "description": "Danh sách bảng và cột của kho dữ liệu (schema gold, ops) để viết truy vấn SQL.",
     "input_schema": {"type": "object", "additionalProperties": False, "properties": {}}},
    {"name": "query_warehouse",
     "description": "Chạy MỘT câu SELECT (DuckDB SQL) chỉ đọc trên kho dữ liệu, tối đa 200 dòng. Chỉ dùng khi các công "
                    "cụ khác không trả lời được; gọi list_tables trước để biết tên cột.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["sql"],
                      "properties": {"sql": {"type": "string"}}}},
]
TOOLS = [{**t, "strict": True} for t in TOOLS]

from .safe_sql import FORBIDDEN, check_sql  # noqa: E402,F401  dung chung voi trang Kho du lieu


class ToolBox:
    def __init__(self, G, scores, alerts, ctx, db_file):
        self.G, self.scores, self.alerts, self.ctx, self.db_file = G, scores, alerts, ctx, str(db_file)
        b = G["dim_branch"].set_index("branch_id")
        self.branch = {int(i): f"CN{i} · {b.branch_name[i]} · hạng {b.store_class[i]}" for i in b.index}

    # -- tung cong cu
    def list_alerts(self, start_date, end_date, branch_id, level):
        a = self.alerts
        a = a[(a.week_start + pd.Timedelta(days=6) >= pd.Timestamp(start_date)) & (a.week_start <= pd.Timestamp(end_date))]
        a = a[a.level != "Bình thường"] if level == "tất cả" else a[a.level == level]
        if branch_id is not None:
            a = a[a.branch_id == branch_id]
        if a.empty:
            return {"so_dong": 0, "ghi_chu": "Không có cảnh báo trong khoảng này."}
        loss = actions.loss_table(self.G, self.ctx, a)
        a = a.merge(loss, on=["branch_id", "week_start"]).sort_values("est_loss", ascending=False).head(30)
        return {"so_dong": len(a), "sap_xep": "ước tính thiệt hại giảm dần", "dong": [
            {"tuan_bat_dau": f"{r.week_start:%Y-%m-%d}", "chi_nhanh": self.branch[int(r.branch_id)], "muc": r.level,
             "nghi_van": f"{r.cause} · {r.cause_name}", "diem": _num(r.score, 2),
             "uoc_tinh_thiet_hai_vnd": _num(r.est_loss), "phu_trach": r.owner,
             "doanh_thu_so_ky_vong_vnd": _num(r.gap_vs_expected), "bang_chung": r.evidence} for r in a.itertuples()]}

    def trace_branch_week(self, branch_id, week_start):
        w = _monday(week_start)
        kv = self.G["mart_kpi_vs_peers_weekly"]
        cur = kv[(kv.branch_id == branch_id) & (kv.week_start == w)].set_index("kpi")
        if cur.empty:
            weeks = detect.usable_weeks(self.G)
            return {"loi": f"Không có dữ liệu đánh giá cho CN{branch_id} tuần {w:%Y-%m-%d}. Các tuần đánh giá được: "
                           f"{weeks[0]:%Y-%m-%d} đến {weeks[-1]:%Y-%m-%d} (thứ Hai)."}

        def k(name):
            if name not in cur.index:
                return None
            r = cur.loc[name]
            return {"thuc_te": _num(r.value, 4), "ky_vong": _num(r.expected_value, 4), "z": _num(r.z, 2)}
        ns = cur.loc["net_sales"]
        channels = []
        for ch, label in C.CHANNELS:
            if f"net_sales_{ch}" in cur.index:
                s, o, a = (cur.loc[x] if x in cur.index else None for x in (f"net_sales_{ch}", f"orders_{ch}", f"aov_{ch}"))
                channels.append({"kenh": label, "doanh_thu_vnd": _num(s.value), "chenh_lech_vnd": _num(s.gap_vs_expected),
                                 "doanh_thu_so_ky_vong_pct": _num((np.exp(s.dev) - 1) * 100, 1) if pd.notna(s.dev) else None,
                                 "so_don_so_ky_vong_pct": _num((np.exp(o.dev) - 1) * 100, 1) if o is not None and pd.notna(o.dev) else None,
                                 "aov_so_ky_vong_pct": _num((np.exp(a.dev) - 1) * 100, 1) if a is not None and pd.notna(a.dev) else None})
        sc = self.scores[(self.scores.branch_id == branch_id) & (self.scores.week_start == w)].sort_values("score", ascending=False)
        lv = self.alerts[(self.alerts.branch_id == branch_id) & (self.alerts.week_start == w)]
        level = lv.level.iloc[0] if len(lv) else "Bình thường"
        top = sc[sc.cause != "BT"].iloc[0]
        cause = top.cause if top.score >= C.SCORE_ALERT else ("?" if level != "Bình thường" else None)
        rec = actions.recommend(self.G, self.ctx, branch_id, w, cause) if cause else None
        signals = {k_: k(k_) for k_ in ("kitchen_evening", "app_avg_prep_min", "app_store_cancel_rate", "grabfood_rating",
                                        "grabfood_pos_coverage", "shopeefood_pos_coverage", "void_rate", "cogs_pct", "labor_pct")}
        return {
            "chi_nhanh": self.branch[branch_id], "tuan": f"{w:%Y-%m-%d} đến {w + pd.Timedelta(days=6):%Y-%m-%d}",
            "muc": level, "nguong_diem_canh_bao": C.SCORE_ALERT,
            "doanh_thu": {"thuc_te_vnd": _num(ns.value), "ky_vong_vnd": _num(ns.expected_value),
                          "chenh_lech_vnd": _num(ns.gap_vs_expected), "chenh_lech_pct": _num((np.exp(ns.dev) - 1) * 100, 1),
                          "z": _num(ns.z, 2)},
            "theo_kenh": channels,
            "tin_hieu_van_hanh": {C.KPI_LABEL.get(k_, k_): v for k_, v in signals.items() if v},
            "gia_thuyet": [{"ma": r.cause, "ten": r.cause_name, "diem": _num(r.score, 2), "bang_chung": r.evidence}
                           for r in sc.itertuples()],
            "de_xuat_xu_ly": None if rec is None else {
                "nguyen_nhan": f"{rec.cause} · {rec.title}", "phu_trach": rec.owner, "thoi_han": rec.deadline,
                "anh_huong": [{"chi_so": l, "gia_tri": _num(v, 1) if u != "vnd" else _num(v), "don_vi": u, "cach_tinh": n}
                              for l, v, u, n in rec.impact],
                "xac_minh": rec.verify, "xu_ly": rec.act, "theo_doi": rec.watch}}

    def branch_kpis(self, start_date, end_date, branch_id):
        d = self.G["mart_branch_daily"]
        d = d[(d.date_day >= pd.Timestamp(start_date)) & (d.date_day <= pd.Timestamp(end_date))]
        if d.empty:
            return {"loi": "Không có dữ liệu trong khoảng ngày này."}
        g = d.groupby(["branch_id", "store_class"], as_index=False).agg(
            net_sales=("net_sales", "sum"), orders=("orders", "sum"), cogs=("cogs_standard", "sum"),
            labor=("labor_cost", "sum"), walkin=("net_sales_walkin", "sum"), app=("net_sales_app", "sum"),
            grab=("net_sales_grabfood", "sum"), shopee=("net_sales_shopeefood", "sum"), days=("date_day", "nunique"))
        g["aov"] = g.net_sales / g.orders
        g["cogs_pct"], g["labor_pct"] = g.cogs / g.net_sales * 100, g.labor / g.net_sales * 100
        med = g.groupby("store_class")[["net_sales", "aov", "cogs_pct", "labor_pct"]].median()
        if branch_id is not None:
            g = g[g.branch_id == branch_id]
        rows = []
        for r in g.itertuples():
            m = med.loc[r.store_class]
            rows.append({"chi_nhanh": self.branch[int(r.branch_id)], "so_ngay": int(r.days),
                         "doanh_thu_thuan_vnd": _num(r.net_sales), "so_don": int(r.orders), "aov_vnd": _num(r.aov),
                         "cogs_pct": _num(r.cogs_pct, 1), "labor_pct": _num(r.labor_pct, 1),
                         "co_cau_kenh_pct": {"Tại quầy": _num(r.walkin / r.net_sales * 100, 1),
                                             "App": _num(r.app / r.net_sales * 100, 1),
                                             "GrabFood": _num(r.grab / r.net_sales * 100, 1),
                                             "ShopeeFood": _num(r.shopee / r.net_sales * 100, 1)},
                         "trung_vi_nhom_cung_hang": {"doanh_thu_thuan_vnd": _num(m.net_sales), "aov_vnd": _num(m.aov),
                                                     "cogs_pct": _num(m.cogs_pct, 1), "labor_pct": _num(m.labor_pct, 1)}})
        return {"khoang": f"{start_date} đến {end_date}", "ghi_chu": "Labor% chỉ gồm lương giờ trực tiếp theo chấm công.",
                "chi_nhanh": rows}

    def list_tables(self):
        with self._connect() as con:
            df = con.sql("select schema_name, table_name, string_agg(column_name || ' ' || data_type, ', ' "
                         "order by column_index) as cols from duckdb_columns() where schema_name in ('gold', 'ops') "
                         "group by 1, 2 order by 1, 2").df()
        return {"bang": [{"ten": f"{r.schema_name}.{r.table_name}", "cot": r.cols} for r in df.itertuples()]}

    def query_warehouse(self, sql):
        s = check_sql(sql)
        with self._connect() as con:
            timer = threading.Timer(SQL_TIMEOUT, con.interrupt)
            timer.start()
            try:
                df = con.sql(f"select * from ({s}) as q limit {SQL_ROW_LIMIT + 1}").df()
            finally:
                timer.cancel()
        trunc = len(df) > SQL_ROW_LIMIT
        df = df.head(SQL_ROW_LIMIT)
        for c in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[c]):
                df[c] = df[c].dt.strftime("%Y-%m-%d")
        return {"so_dong": len(df), "bi_cat_bot": trunc, "cot": list(df.columns),
                "dong": json.loads(df.to_json(orient="values", force_ascii=False, double_precision=4))}

    def _connect(self):
        return safe_sql.connect(self.db_file)

    def run(self, name, args):
        fn = getattr(self, name, None)
        if fn is None or name not in {t["name"] for t in TOOLS}:
            raise ValueError(f"Không có công cụ {name}")
        return fn(**args)


# ------------------------------------------------------------------ vong lap agent
SYSTEM = """Bạn là trợ lý phân tích vận hành của chuỗi đồ ăn nhanh Fast&Fat (11 chi nhánh tại TP.HCM, hạng A/B/C theo quy mô; \
4 kênh bán: tại quầy, App riêng, GrabFood, ShopeeFood). Người hỏi là quản lý vận hành hoặc quản lý chi nhánh.

Dữ liệu: {profile}, từ {d0} đến {d1}. Tuần tính từ thứ Hai. Hôm nay theo dữ liệu là {d1}.

Hệ thống đã có bộ phát hiện sự cố. Các nhóm nguyên nhân:
- P1a: sàn thu hoa hồng cao hơn hợp đồng · P1b: đơn sàn hoàn thành nhưng không được ghi vào POS
- P2: hao hụt nguyên liệu tươi vượt định mức · P4: thất thoát nguyên liệu giá trị cao
- P3: thiếu nhân sự, bếp quá tải, mất đơn · P5: hủy, hoàn, giảm giá bất thường tại quầy (nghi vấn, không phải kết luận)
- "?": doanh thu lệch kỳ vọng nhưng chưa nguyên nhân nào đủ bằng chứng. Ngưỡng điểm cảnh báo: {thr}.
Mức kỳ vọng của doanh thu đã trừ biến động chung (lễ, mưa, mùa vụ) bằng cách so với nhóm chi nhánh cùng hạng.

Quy tắc:
1. Mọi con số trong câu trả lời phải lấy từ kết quả công cụ trong cuộc hội thoại này. Không ước lượng, không bịa số. \
Nếu công cụ không trả lời được, nói rõ là không có dữ liệu.
2. Ưu tiên các công cụ phân tích có sẵn; chỉ dùng query_warehouse khi chúng không đủ.
3. Với P5, chỉ nói "nghi vấn cần xác minh", không kết luận nhân viên gian lận.
4. Trả lời bằng tiếng Việt, ngắn gọn, đi thẳng vào việc cần làm. Tiền viết dạng "48,3 triệu đ"; ngày dạng dd/mm/yyyy; \
ghi rõ chi nhánh (CN và tên). Khi khuyến nghị, nêu người phụ trách và căn cứ.
5. Nếu câu hỏi mơ hồ về thời gian, dùng 4 tuần gần nhất của dữ liệu và nói rõ khoảng đã dùng."""


@dataclass
class Turn:
    answer: str = ""
    calls: list = field(default_factory=list)       # (ten, dau vao, ket qua dict | loi)
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    stop: str = ""

    @property
    def cost_usd(self):
        return (self.input_tokens * PRICE_IN + self.output_tokens * PRICE_OUT) / 1e6


def system_prompt(G, profile_label):
    dd = G["dim_date"].date_day
    return SYSTEM.format(profile=profile_label, d0=f"{dd.min():%d/%m/%Y}", d1=f"{dd.max():%d/%m/%Y}", thr=C.SCORE_ALERT)


def ask(client, model, extra, system, messages, box):
    """Mot luot hoi: them cau hoi vao messages (da co san), lap goi cong cu den khi mo hinh tra loi xong.
    messages duoc noi them (append-only) de giu nguyen cac khoi suy nghi cho luot sau."""
    import anthropic
    turn, t0 = Turn(), time.time()
    create = client.beta.messages.create if extra.get("betas") else client.messages.create
    for _ in range(MAX_STEPS):
        resp = create(model=model, max_tokens=16000, system=[{"type": "text", "text": system,
                                                              "cache_control": {"type": "ephemeral"}}],
                      tools=TOOLS, messages=messages, output_config={"effort": "medium"}, **extra)
        turn.input_tokens += resp.usage.input_tokens + (resp.usage.cache_read_input_tokens or 0) \
            + (resp.usage.cache_creation_input_tokens or 0)
        turn.output_tokens += resp.usage.output_tokens
        messages.append({"role": "assistant", "content": resp.content})
        turn.stop = resp.stop_reason
        if resp.stop_reason == "refusal":
            turn.answer = "Mô hình từ chối trả lời câu hỏi này."
            break
        uses = [b for b in resp.content if b.type == "tool_use"]
        if resp.stop_reason != "tool_use" or not uses:
            turn.answer = "\n".join(b.text for b in resp.content if b.type == "text").strip()
            break
        results = []
        for u in uses:
            try:
                out = box.run(u.name, dict(u.input))
                content, err = json.dumps(out, ensure_ascii=False, default=str), False
            except Exception as e:  # loi cong cu tra ve cho mo hinh de no tu sua (vd SQL sai ten cot)
                out, content, err = {"loi": str(e)}, f"Lỗi: {e}", True
            turn.calls.append((u.name, dict(u.input), out))
            results.append({"type": "tool_result", "tool_use_id": u.id, "content": content, "is_error": err})
        messages.append({"role": "user", "content": results})
    else:
        turn.answer = "Đã dừng sau số bước tối đa mà chưa có câu trả lời."
    turn.seconds = time.time() - t0
    return turn


# ------------------------------------------------------------------ kiem tra con so co can cu
NUM = re.compile(r"(?<![\w/])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?\s*(tỷ|triệu|nghìn|%)?", re.I)
DATE = re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b|\b\d{4}-\d{2}-\d{2}\b")


def _values(obj, out):
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float)):
        out.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            _values(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _values(v, out)
    elif isinstance(obj, str):
        for m in NUM.finditer(DATE.sub(" ", obj)):
            out.extend(_parse(m))


def _parse(m):
    whole, frac, unit = m.group(1), m.group(2), (m.group(3) or "").lower()
    v = float(whole.replace(".", "") + ("." + frac if frac else ""))
    mul = {"tỷ": 1e9, "triệu": 1e6, "nghìn": 1e3}.get(unit, 1)
    return [v * mul]


def grounding(answer, calls):
    """Ty le con so trong cau tra loi khop (sai so lam tron) voi mot gia tri trong ket qua cong cu.
    Bo qua ngay thang, so nho <= 31 (thu tu, so chi nhanh, so tuan). Tra ve (so khop, tong, danh sach so khong khop)."""
    pool = []
    for _, args, out in calls:
        _values(out, pool)
        _values(args, pool)
    pool = np.array(pool) if pool else np.array([0.0])
    text = DATE.sub(" ", answer)
    found, missing = 0, []
    for m in NUM.finditer(text):
        v = _parse(m)[0]
        if v <= 31 and not m.group(2) and not m.group(3):
            continue
        cand = [v, v / 100] if m.group(3) == "%" else [v]
        tol = lambda x: max(abs(x) * 0.006, 0.051 if m.group(2) else 0.51)
        ok = any(np.any(np.abs(np.abs(pool) - abs(c)) <= tol(c)) or np.any(np.abs(np.abs(pool) * 100 - abs(c)) <= tol(c))
                 for c in cand)
        found += ok
        if not ok:
            missing.append(m.group(0).strip())
    total = found + len(missing)
    return found, total, missing
