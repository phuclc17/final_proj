"""
Cua chan chat luong du lieu dau vao: chay SAU khi nap Bronze, TRUOC dbt.
  - Do moi    : nguon nao cham so voi ngay du lieu moi nhat (nguong theo nhip cua tung nguon)
  - Khoi luong: so dong cua ngay moi nhat so voi trung vi 14 ngay truoc
  - Tep loi   : tep khong doc duoc, tep sai hop dong du lieu, tep khong thuoc nguon nao trong lo vua nap
  - Day du    : ngay du lieu moi nhat, moi chi nhanh co du tep POS va cham cong (thieu tep de nham thanh doanh thu giam)
  - Cau truc  : truong/cot moi xuat hien hoac truong quen thuoc bien mat (so voi so dang ky cau truc)
Muc 'chan' -> thoat ma 1: bo dieu phoi dung lai, du lieu loi khong lan len Silver/Gold.
Ket qua ghi vao ops.dq_checks; so dang ky cau truc o ops.schema_registry.

  python -m pipeline.quality_gate --profile live
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

from . import dbutil

ROOT = Path(__file__).resolve().parent.parent
# nhip cap nhat cua tung nguon -> (so ngay cham toi da truoc khi canh bao, truoc khi chan); None = khong chan
CADENCE = {
    "pos_receipts": (1, 4), "app_orders": (1, 4), "timekeeping_punches": (1, 4), "weather_daily": (2, None),
    "grab_settlement": (8, None), "shopee_settlement": (8, None), "stock_counts": (15, None),
}
DAILY = [t for t, (warn, _) in CADENCE.items() if warn <= 1]
PAYLOAD_TABLES = {"pos_receipts", "app_orders", "weather_daily"}
META_COLS = {"_source_file", "_file_hash", "_row_number", "_batch_id", "_ingested_at", "_envelope"}
DATE_RE = re.compile(r"(20\d{2})-?(\d{2})-?(\d{2})")


def file_date(path):
    """Ngay du lieu cua tep theo ten tep; tep co 2 ngay (bao cao tuan) lay ngay cuoi."""
    found = [datetime(int(y), int(m), int(d)) for y, m, d in DATE_RE.findall(Path(path).name)]
    return max(found) if found else None


def num(x):
    """So nguyen kieu Viet Nam: 1.685."""
    return f"{int(x):,}".replace(",", ".")


def check(rows, kind, source, level, value, threshold, message):
    rows.append({"check": kind, "source": source, "level": level, "value": value, "threshold": threshold,
                 "message": message})


def gone_fields(con, table, batch):
    """Truong co trong lo gan nhat truoc do cua CUNG thu muc nguon ma lo nay khong con. So theo thu muc chu khong theo ca
    bang: mot bang co the gom nhieu phien ban dinh dang den bang nhieu duong, o cac lo khac nhau (POS cai tai may ban
    2.8 xuat tep, POS dam may ban 3.2 keo qua API)."""
    return con.sql(f"""
        with t as (select regexp_replace(_source_file, '/[^/]*$', '') as d, _batch_id as b, payload from bronze.{table}),
        cur as (select distinct d, unnest(json_keys(payload)) as f from t where b = '{batch}'),
        prev_b as (select d, max(b) as b from t where b < '{batch}' and d in (select d from cur) group by d),
        prev as (select distinct t.d, unnest(json_keys(t.payload)) as f from t join prev_b using (d, b))
        select distinct prev.f from prev anti join cur on prev.d = cur.d and prev.f = cur.f order by 1""").df().f.tolist()


def run_checks(con):
    """Tra ve bang ket qua kiem tra (khong ghi gi). Tach rieng de kiem thu don vi duoc."""
    rows = []
    log = con.sql("select bronze_table, file_path, row_count, status, error, batch_id, ingested_at "
                  "from bronze._ingest_log").df()
    if log.empty:
        check(rows, "khối lượng", "bronze", "chặn", 0, ">0", "Chưa có tệp nào được nạp.")
        return pd.DataFrame(rows)
    log["data_date"] = log.file_path.map(file_date)
    ok = log[log.status.isin(["loaded", "reloaded"])]

    # ---- ngay tham chieu: ngay moi nhat co it nhat mot nua so tep thuong ngay (mot tep le dat ten ngay tuong lai
    # khong duoc "keo" ngay tham chieu di)
    per_date = ok[ok.bronze_table.isin(DAILY)].groupby("data_date").size().sort_index()
    typical = per_date.tail(15).median() if len(per_date) else 0
    solid = per_date[per_date >= 0.5 * typical]
    ref = solid.index.max() if len(solid) else per_date.index.max()

    # ---- do moi
    for table, (warn, block) in CADENCE.items():
        d = ok[ok.bronze_table == table].data_date.max()
        if pd.isna(d):
            check(rows, "độ mới", table, "chặn" if block else "cảnh báo", None, f"≤{warn} ngày", "Chưa có dữ liệu.")
            continue
        lag = (ref - d).days
        level = "chặn" if block is not None and lag >= block else ("cảnh báo" if lag > warn else "đạt")
        check(rows, "độ mới", table, level, lag, f"≤{warn} ngày",
              f"Dữ liệu mới nhất {d:%d/%m/%Y}, chậm {lag} ngày so với {ref:%d/%m/%Y}.")

    # ---- khoi luong (nguon theo ngay)
    for table in DAILY:
        per_day = ok[ok.bronze_table == table].groupby("data_date").row_count.sum().sort_index()
        if per_day.empty:
            continue
        last, hist = per_day.iloc[-1], per_day.iloc[:-1].tail(14)
        if last == 0:
            check(rows, "khối lượng", table, "chặn", 0, ">0", f"Ngày {per_day.index[-1]:%d/%m/%Y} không có dòng nào.")
            continue
        if len(hist) < 5:
            continue
        ratio = last / hist.median()
        level = "cảnh báo" if ratio < 0.5 or ratio > 2 else "đạt"
        check(rows, "khối lượng", table, level, round(float(ratio), 2), "0,5–2 lần trung vị 14 ngày",
              f"Ngày {per_day.index[-1]:%d/%m/%Y}: {num(last)} dòng, trung vị 14 ngày trước {num(hist.median())}.")

    # ---- day du: moi ngay co trong lo vua nap (khong chi ngay moi nhat), chi nhanh nao da gui tep trong 7 ngay
    # truoc ma ngay do thieu hoac tep rong (chi nhanh moi khai truong hay da dong cua khong bi bao thieu)
    last_batch = log.sort_values("ingested_at").batch_id.iloc[-1]
    batch_dates = sorted(d for d in log[(log.batch_id == last_batch) & log.bronze_table.isin(DAILY)].data_date.dropna()
                         .unique() if pd.isna(ref) or d <= ref)
    seed = pd.read_csv(ROOT / "dbt" / "seeds" / "branch_code_map.csv", dtype=str)
    known = set(seed.pos_terminal_prefix) | set(seed.timekeeping_branch_code)   # may chua khai bao khong tinh la thieu
    miss, mass = [], []
    for day in batch_dates or ([ref] if pd.notna(ref) else []):
        for table, label in (("pos_receipts", "POS"), ("timekeeping_punches", "chấm công")):
            t = ok[ok.bronze_table == table]
            folder = t.file_path.str.split("/").str[1]
            have = set(folder[(t.data_date == day) & (t.row_count > 0)])   # tep rong coi nhu thieu
            recent = set(folder[(t.data_date < day) & (t.data_date >= day - pd.Timedelta(days=7))]) & known
            gone = sorted(recent - have)
            miss += [f"{pd.Timestamp(day):%d/%m} {f} thiếu tệp {label}" for f in gone]
            if recent and len(gone) >= max(3, -(-len(recent) // 3)):   # tu 1/3 so chi nhanh tro len
                mass.append(f"{pd.Timestamp(day):%d/%m} thiếu {label} của {len(gone)}/{len(recent)} chi nhánh")
    if pd.notna(ref):
        # thieu le te: canh bao, chi nhanh do khong bi ket luan su co. Thieu hang loat (API nguon sap, mat mang dien
        # rong): so sanh giua cac chi nhanh mat y nghia, ca dashboard lan bo phat hien deu sai -> chan truoc dbt, lan
        # chay sau (khi du lieu ve du) tu di tiep
        level = "chặn" if mass else "cảnh báo" if miss else "đạt"
        head = ("Thiếu hàng loạt: " + "; ".join(mass) + ". Dừng trước Silver, Gold để báo cáo không so sánh chi nhánh "
                "trên dữ liệu thiếu; lượt sau tự chạy tiếp khi dữ liệu về đủ. Chi tiết: ") if mass else ""
        check(rows, "đầy đủ", "pos, chấm công", level, len(miss), "0",
              (head + "; ".join(miss) + ". Doanh thu, giờ công của chi nhánh ngày đó sẽ thấp giả tạo cho tới khi tệp "
               "được gửi bổ sung; bộ phát hiện không kết luận sự cố dựa trên nguồn bị thiếu.") if miss else
              "Các ngày trong lô vừa nạp đủ tệp POS, chấm công của mọi chi nhánh.")

    # ---- tep loi, sai hop dong, khong nhan dang trong lo vua nap
    cur = log[log.batch_id == last_batch]
    for status, kind, label in (("failed", "tệp lỗi", "Tệp không đọc được"),
                                ("rejected", "sai hợp đồng", "Tệp sai hợp đồng dữ liệu, không nạp"),
                                ("unrecognized", "không nhận dạng", "Tệp không thuộc nguồn nào, không nạp")):
        bad = cur[cur.status == status]
        check(rows, kind, "bronze", "cảnh báo" if len(bad) else "đạt", len(bad), "0",
              f"Không có trong lô vừa nạp." if bad.empty else
              f"{label}: " + "; ".join(f"{p} ({str(e)[:140]})" for p, e in zip(bad.file_path.head(4), bad.error.head(4))))

    # ---- cau truc: so voi so dang ky
    con.execute("create schema if not exists ops")
    con.execute("create table if not exists ops.schema_registry (bronze_table varchar, field varchar, first_seen timestamp)")
    known = con.sql("select bronze_table, field from ops.schema_registry").df()
    first_time = known.empty
    current = []
    tables = con.sql("select table_name from duckdb_tables() where schema_name = 'bronze' and table_name <> '_ingest_log'").df()
    for t in tables.table_name:
        if t in PAYLOAD_TABLES:
            fields = con.sql(f"""select distinct unnest(json_keys(payload)) as f from bronze.{t}
                                 where _batch_id = '{last_batch}'""").df().f.tolist()
        else:
            fields = [c for c in con.sql(f"select column_name from information_schema.columns "
                                         f"where table_schema = 'bronze' and table_name = '{t}'").df().column_name
                      if c not in META_COLS and not c.startswith("_doc_line")]
        current += [(t, f) for f in fields]
    cur = pd.DataFrame(current, columns=["bronze_table", "field"])
    if first_time:
        check(rows, "cấu trúc", "bronze", "đạt", len(cur), "", f"Khởi tạo sổ đăng ký cấu trúc: {len(cur)} trường.")
    else:
        new = cur.merge(known, how="left", indicator=True).query("_merge == 'left_only'")
        for t, g in new.groupby("bronze_table"):
            check(rows, "cấu trúc", t, "cảnh báo", len(g), "0", "Trường mới xuất hiện: " + ", ".join(g.field.head(8)))
        any_gone = False
        for t in sorted(PAYLOAD_TABLES & set(cur.bronze_table)):
            gone = gone_fields(con, t, last_batch)
            if gone:
                any_gone = True
                check(rows, "cấu trúc", t, "cảnh báo", len(gone), "0", "Trường quen thuộc không còn trong lô mới: "
                      + ", ".join(gone[:8]))
        if new.empty and not any_gone:
            check(rows, "cấu trúc", "bronze", "đạt", 0, "0", "Không có thay đổi cấu trúc so với sổ đăng ký.")
    add = cur.merge(known, how="left", indicator=True).query("_merge == 'left_only'")[["bronze_table", "field"]]
    if len(add):
        con.register("newf", add)
        con.execute("insert into ops.schema_registry select bronze_table, field, now() from newf")
        con.unregister("newf")
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="live", choices=["calibration", "holdout", "live"])
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    db = ROOT / "data" / args.profile / "warehouse" / "fastfat.duckdb"
    run_id = args.run_id or f"{datetime.now():%Y%m%d_%H%M%S}"
    with dbutil.connect(db) as con:
        res = run_checks(con)
        res.insert(0, "run_id", run_id)
        res["checked_at"] = datetime.now()
        con.execute("""create table if not exists ops.dq_checks (run_id varchar, "check" varchar, source varchar,
                       level varchar, value double, threshold varchar, message varchar, checked_at timestamp)""")
        con.register("res", res)
        con.execute("insert into ops.dq_checks by name select * from res")
    counts = res.level.value_counts().to_dict()
    print(f"Kiem tra dau vao: {counts.get('đạt', 0)} dat, {counts.get('cảnh báo', 0)} canh bao, {counts.get('chặn', 0)} chan")
    for r in res[res.level != "đạt"].itertuples():
        print(f"  [{r.level}] {r.check} - {r.source}: {r.message}")
    sys.exit(1 if (res.level == "chặn").any() else 0)


if __name__ == "__main__":
    main()
