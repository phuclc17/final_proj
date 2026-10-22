"""Khuyen nghi xu ly cho mot canh bao: viec can xac minh, viec can lam, nguoi phu trach va anh huong uoc tinh.
Chi dung so lieu Gold va bang chung bo phat hien da tinh (khong doc ground_truth/). Moi con so la UOC TINH de
uu tien xu ly; quan ly phai xac minh truoc khi ket luan, nhat la voi nghi van lien quan den con nguoi (P5).

    ctx = actions.prepare(G)
    rec = actions.recommend(G, ctx, branch_id, week_start, cause)   # cause: P1a, P1b, P2, P3, P4, P5 hoac "?"
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import config as C
from . import detect

PLATFORMS = {"grabfood": "GrabFood", "shopeefood": "ShopeeFood"}


@dataclass
class Rec:
    cause: str
    title: str
    owner: str
    deadline: str
    impact: list = field(default_factory=list)   # (nhan, gia tri, don vi "vnd" | "don" | "ca", giai thich)
    verify: list = field(default_factory=list)
    act: list = field(default_factory=list)
    watch: list = field(default_factory=list)


def money(v):
    """So tien kieu Viet Nam, gon: 1,25 triệu đ / 850.000 đ."""
    if v is None or pd.isna(v):
        return "—"
    if abs(v) >= 1e6:
        return f"{v / 1e6:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".") + " triệu đ"
    return f"{v:,.0f}".replace(",", ".") + " đ"


def pct(v, d=1):
    return "—" if v is None or pd.isna(v) else f"{v * 100:.{d}f}".replace(".", ",") + "%"


def prepare(G):
    """Cac bang bang chung dung chung cho moi khuyen nghi (tinh mot lan)."""
    return {"inv": detect.inventory_z(G), "cash": detect.cashier_z(G), "mkt": detect.marketplace_gap_z(G),
            "mkt_all": detect.marketplace_gap_all(G)}


def recommend(G, ctx, branch, week, cause):
    fn = {"P1a": _p1a, "P1b": _p1b, "P2": _p2, "P3": _p3, "P4": _p4, "P5": _p5}.get(cause, _unknown)
    return fn(G, ctx, int(branch), pd.Timestamp(week))


def estimated_loss(rec):
    """Mot con so de sap xep danh sach canh bao: so tien co the thu hoi hoac dang mat.
    P1a: hoa hong thu thua luy ke; P1b: gia tri ban chua vao so; P2, P4: phan hao hut vuot muc thuong;
    P3 va chua xac dinh: phan doanh thu thap hon ky vong; P5: gia tri hoa don bi huy, hoan, giam gia (gia tri lien quan,
    chua phai so tien that thoat)."""
    idx = {"P1a": 1, "P1b": 2, "P2": 2, "P4": 2, "P5": 2}
    if rec.cause in idx:
        v = rec.impact[idx[rec.cause]][1] if len(rec.impact) > idx[rec.cause] else np.nan
        return 0.0 if pd.isna(v) else float(v)
    v = rec.impact[0][1] if rec.impact else np.nan      # P3, "?": doanh thu so voi ky vong
    return 0.0 if pd.isna(v) else float(max(-v, 0.0))


def loss_table(G, ctx, alerts):
    """Them cot uoc tinh thiet hai va nguoi phu trach cho cac dong canh bao, theo doi."""
    rows = []
    for r in alerts.itertuples():
        rec = recommend(G, ctx, r.branch_id, r.week_start, r.cause)
        rows.append((r.branch_id, r.week_start, estimated_loss(rec), rec.owner))
    return pd.DataFrame(rows, columns=["branch_id", "week_start", "est_loss", "owner"])


# ------------------------------------------------------------------ tien ich
def _wk(G, b):
    wk = G["mart_branch_weekly"]
    return wk[wk.branch_id == b].sort_values("week_start").set_index("week_start")


def _kpi(G, b, w):
    kv = G["mart_kpi_vs_peers_weekly"]
    return kv[(kv.branch_id == b) & (kv.week_start == w)].set_index("kpi")


def _row(df, b, w):
    r = df[(df.branch_id == b) & (df.week_start == w)]
    return None if r.empty else r.iloc[0]


def _inventory(G, ctx, b, w, group):
    """So tien hao hut cua ky kiem ke bao phu tuan w va phan vuot muc thuong. Muc thuong = ty le hao hut tren dinh muc
    (theo tien) trung vi cua cac chi nhanh khac CUNG KY x dinh muc cua chi nhanh nay: so cat ngang nhu bo phat hien,
    dung duoc tu ky dau, khong nhin tuong lai. Nhom tinh tien rong hon nhom cham diem: P2 tinh moi hang tuoi ke ca
    thit vi nguoi quan ly can biet tong so tien; diem phat hien van dung nhom hang tuoi gia thap nhu bo phat hien."""
    w_end = w + pd.Timedelta(days=6)
    cost = G["dim_ingredient"].set_index("ingredient_id").standard_unit_cost
    a = G["mart_ingredient_avt"].copy()
    a = a[a.ingredient_id.map(cost) >= C.HIGH_VALUE_COST] if group == "high_value" else a[a.is_fresh]
    cover = a[(a.branch_id == b) & (a.period_start_excl < w_end) & (a.period_end >= w_end)]
    if cover.empty:
        return None
    pend = cover.period_end.min()
    p = a[a.period_end == pend].assign(theory_value=lambda x: x.theory_qty * x.ingredient_id.map(cost))
    by = p.groupby("branch_id").agg(value=("variance_value", "sum"), theory=("theory_value", "sum"))
    by["rate"] = by.value / by.theory.where(by.theory > 0)
    own, others = by.loc[b], by.drop(index=b).rate.dropna()
    normal = others.median() * own.theory if len(others) else np.nan
    mine = p[p.branch_id == b]
    top = mine[mine.variance_value > 0].sort_values("variance_value", ascending=False).head(3)
    return {"start": mine.period_start_excl.max() + pd.Timedelta(days=1), "end": pend, "value": own.value,
            "normal": normal, "excess": max(own.value - normal, 0.0) if pd.notna(normal) else np.nan, "top": top}


def _names(top):
    return ", ".join(f"{r.ingredient_name} vượt {pct(r.variance_pct, 0)}" for r in top.itertuples()) or "không rõ"


# ------------------------------------------------------------------ tung nguyen nhan
def _p1a(G, ctx, b, w):
    d = _wk(G, b)
    r = Rec("P1a", C.CAUSE_NAMES["P1a"], "Kế toán công nợ sàn", "trong kỳ đối soát kế tiếp")
    week_total, claim_total, first = 0.0, 0.0, w
    for p, name in PLATFORMS.items():
        gap = d[f"{p}_commission_gap"].get(w)
        if pd.isna(gap) or gap <= C.COMMISSION_TOLERANCE:
            continue
        streak = []
        for ws, gp in d[f"{p}_commission_gap"].loc[:w][::-1].items():   # chuoi tuan lech lien tiep den tuan nay
            if pd.notna(gp) and gp > C.COMMISSION_TOLERANCE:
                streak.append(ws)
            else:
                break
        total = d.loc[streak, f"{p}_commission_overcharge"].sum()
        week_total += d.at[w, f"{p}_commission_overcharge"]
        claim_total += total
        first = min(first, min(streak))
        r.verify.append(f"Đối chiếu báo cáo đối soát {name} với phụ lục hợp đồng: hợp đồng {pct(d.at[w, f'{p}_contract_rate'])}, "
                        f"sàn đang áp {pct(d.at[w, f'{p}_effective_rate'])} trên doanh thu món "
                        f"{money(d.at[w, f'{p}_settled_gross'])} của tuần.")
        r.act.append(f"Gửi {name} yêu cầu điều chỉnh và hoàn {money(total)} hoa hồng thu thừa của {len(streak)} tuần "
                     f"tính từ tuần {min(streak):%d/%m}, đính kèm bảng đối soát từng tuần.")
        r.watch.append(f"Tỷ lệ hoa hồng hiệu dụng của {name} về lại {pct(d.at[w, f'{p}_contract_rate'])} ở kỳ kế tiếp; "
                       "khoản hoàn xuất hiện ở dòng điều chỉnh của báo cáo sàn.")
    r.impact = [("Hoa hồng thu thừa trong tuần", week_total, "vnd", "Hoa hồng sàn thu trừ hoa hồng theo hợp đồng."),
                (f"Lũy kế từ tuần {first:%d/%m}", claim_total, "vnd", "Cộng các tuần lệch liên tiếp tới tuần đang xem.")]
    r.verify.append("Kiểm tra sàn có thông báo đổi biểu phí hay chương trình tính thêm phí trong kỳ không.")
    r.act.append("Từ kỳ sau, đối chiếu tỷ lệ hoa hồng mỗi tuần trước khi xác nhận công nợ với sàn.")
    return r


def _p1b(G, ctx, b, w):
    r = Rec("P1b", C.CAUSE_NAMES["P1b"], "Quản lý chi nhánh, kế toán doanh thu", "trong 2 ngày")
    ms = ctx["mkt_all"]
    ms = ms[(ms.branch_id == b) & (ms.week_start == w)].sort_values("mkt_z", ascending=False)
    if ms.empty:
        return r
    flagged = ms[ms.mkt_z >= C.Z_WATCH]
    ms = flagged if len(flagged) else ms.head(1)     # moi san co tin hieu, it nhat san noi bat nhat
    missing = excess = value = 0.0
    notes, names = [], []
    for m in ms.itertuples():
        name = PLATFORMS[m.platform]
        ex = max(m.missing - m.settled * m.normal_miss_rate, 0.0)
        ticket = m.settled_gross / m.settled if m.settled else np.nan
        missing, excess, value = missing + m.missing, excess + ex, value + (ex * ticket if pd.notna(ticket) else 0.0)
        names.append(name)
        notes.append(f"{name}: sàn báo {m.settled} đơn, thiếu {m.missing}, thường thiếu {pct(m.normal_miss_rate)}, "
                     f"giá trị đơn bình quân {money(ticket)}")
        r.watch.append(f"Độ phủ POS đơn {name} về lại khoảng {pct(1 - m.normal_miss_rate, 0)} trong 1–2 tuần.")
    on = " và ".join(names)
    r.impact = [(f"Đơn {on} không có trên POS", missing, "don", "; ".join(notes) + "."),
                ("Vượt mức thiếu thường ngày", excess, "don", "Số đơn thiếu trừ phần thiếu thường gặp do lệch giờ chốt sổ."),
                ("Giá trị bán chưa vào sổ, ước tính", value, "vnd", "Số đơn vượt nhân với giá trị đơn bình quân trên từng sàn tuần đó.")]
    r.verify = [f"Lấy danh sách mã đơn {on} hoàn thành trong tuần, đối chiếu với hóa đơn POS cùng nguồn theo ngày và ca "
                "để biết đơn thiếu rơi vào ca, máy nào.",
                "Kiểm tra máy tính bảng nhận đơn sàn và thao tác nhập đơn sàn vào POS ở các ca đó."]
    if len(names) > 1:
        r.verify.append("Cả hai sàn cùng thiếu thường do quy trình hoặc người ở quầy, ít khi do lỗi kết nối của một sàn.")
    r.act = ["Nếu do quy trình: yêu cầu mọi đơn sàn phải có hóa đơn POS trước khi giao cho tài xế.",
             "Nếu tiền sàn đã chuyển về nhưng không có doanh thu tương ứng trên POS: kế toán ghi nhận bổ sung và báo "
             "quản lý vùng xem xét trách nhiệm."]
    r.watch.append("Hao hụt kho ở kỳ kiểm kê tới: đơn bán không vào POS cũng làm kho trông như thất thoát.")
    return r


def _p2(G, ctx, b, w):
    r = Rec("P2", C.CAUSE_NAMES["P2"], "Quản lý chi nhánh, bếp trưởng", "trong tuần")
    k = _inventory(G, ctx, b, w, "fresh")
    if k is None:
        return r
    top = k["top"]
    r.impact = [(f"Hao hụt hàng tươi kỳ {k['start']:%d/%m}–{k['end']:%d/%m}", k["value"], "vnd",
                 "Mọi nguyên liệu tươi kể cả thịt: tiêu hao thực tế trừ định mức theo công thức, theo đơn giá chuẩn."),
                ("Mức thường", k["normal"], "vnd", "Trung vị tỷ lệ hao hụt trên định mức của các chi nhánh khác cùng kỳ, nhân với định mức của chi nhánh này."),
                ("Phần vượt mức thường", k["excess"], "vnd", "Số tiền ước tính có thể thu hẹp nếu xử lý được nguyên nhân.")]
    first = top.ingredient_name.iloc[0] if len(top) else "nguyên liệu vượt nhiều nhất"
    r.verify = [f"Xem sổ hủy hàng, hàng hết hạn trong kỳ; tập trung vào {_names(top)}.",
                "Kiểm tra nhiệt độ tủ mát, tủ đông và việc xuất kho theo nguyên tắc nhập trước xuất trước.",
                f"Cân thử định lượng thực tế các món dùng {first.lower()} so với công thức."]
    r.act = [f"Điều chỉnh lượng đặt {first.lower()} theo lượng bán thực tế, tăng số lần nhận hàng nếu nhà cung cấp cho phép.",
             "Nhắc lại quy trình bảo quản, dán nhãn ngày nhận hàng trên từng thùng."]
    r.watch = ["Hao hụt hàng tươi ở kỳ kiểm kê kế tiếp, sau 2 tuần, về gần trung vị các chi nhánh."]
    return r


def _p4(G, ctx, b, w):
    r = Rec("P4", C.CAUSE_NAMES["P4"], "Quản lý vùng, kiểm soát nội bộ", "trong 1 ngày")
    k = _inventory(G, ctx, b, w, "high_value")
    if k is None:
        return r
    top = k["top"]
    r.impact = [(f"Hao hụt nhóm giá trị cao kỳ {k['start']:%d/%m}–{k['end']:%d/%m}", k["value"], "vnd",
                 "Nguyên liệu đơn giá chuẩn từ 80.000 đ: tiêu hao thực tế trừ định mức theo công thức."),
                ("Mức thường", k["normal"], "vnd", "Trung vị tỷ lệ hao hụt trên định mức của các chi nhánh khác cùng kỳ, nhân với định mức của chi nhánh này."),
                ("Phần vượt mức thường", k["excess"], "vnd", "Số tiền ước tính có thể thu hẹp nếu xử lý được nguyên nhân.")]
    r.verify = [f"Kiểm kê đột xuất nhóm giá trị cao trong ngày, không báo trước; tập trung vào {_names(top)}.",
                "Đối chiếu phiếu nhập kho với hóa đơn, phiếu giao của nhà cung cấp để loại trừ nhận thiếu hàng.",
                "Xem camera khu kho vào giờ nhận hàng và giờ đóng cửa."]
    m = _row(ctx["mkt"], b, w)
    if m is not None and m.mkt_z >= C.Z_WATCH:
        r.verify.insert(0, "Kiểm tra trước việc đơn sàn không vào POS: nguyên liệu đã dùng cho đơn bán nhưng không có "
                           "doanh số đối ứng cũng làm kho hụt.")
    r.act = ["Tách người nhận hàng và người ghi sổ kho; khóa tủ đông nhóm giá trị cao, giao chìa cho quản lý ca.",
             "Kiểm kê nhóm này hằng tuần cho tới khi hao hụt về mức thường."]
    r.watch = ["Hao hụt nhóm giá trị cao ở kỳ kiểm kê kế tiếp so với các chi nhánh khác."]
    return r


def _p3(G, ctx, b, w):
    r = Rec("P3", C.CAUSE_NAMES["P3"], "Quản lý chi nhánh, quản lý vùng", "trước tuần kế tiếp")
    cur, d = _kpi(G, b, w), _wk(G, b)
    ke = cur.loc["kitchen_evening"] if "kitchen_evening" in cur.index else None
    short = max(round(ke.expected_value - ke.value), 0) if ke is not None and pd.notna(ke.expected_value) else 0
    ls = G.get("fact_labor_shift")
    shift_cost = np.nan
    if ls is not None:
        past = ls[(ls.branch_id == b) & (ls.role == "Kitchen") & (ls.shift_name == "TOI")
                  & (ls.date_day < w) & (ls.date_day >= w - pd.Timedelta(weeks=8))]
        shift_cost = past.labor_cost.median() if len(past) else np.nan
    gap = cur.loc["net_sales"].gap_vs_expected if "net_sales" in cur.index else np.nan
    cancels = d.at[w, "app_store_cancels"] + d.at[w, "app_wait_cancels"] if w in d.index else np.nan
    lost_app = cancels * d.at[w, "aov_app"] if w in d.index else np.nan
    r.impact = [("Doanh thu so với kỳ vọng", gap, "vnd", "Đã trừ biến động chung của nhóm chi nhánh cùng hạng."),
                ("Đơn App bị hủy vì quá tải", lost_app, "vnd",
                 f"{0 if pd.isna(cancels) else int(cancels)} đơn cửa hàng tự hủy hoặc khách hủy vì chờ, nhân với AOV App."),
                (f"Chi phí thêm {short} ca bếp tối mỗi tuần", short * shift_cost if short else 0.0, "vnd",
                 "Theo chi phí trung vị một ca bếp tối của chi nhánh trong 8 tuần trước.")]
    if ke is not None:
        r.verify.append(f"So lịch phân ca với chấm công: tuần này có {ke.value:.0f} ca bếp tối, mức thường khoảng "
                        f"{ke.expected_value:.0f}.")
    r.verify.append("Tìm nguyên nhân thiếu người: nghỉ việc, nghỉ phép, chưa tuyển thay.")
    if short:
        r.act.append(f"Bổ sung khoảng {short} ca bếp tối mỗi tuần bằng nhân viên bán thời gian hoặc điều chuyển từ chi "
                     f"nhánh cùng hạng; "
                     f"chi phí khoảng {money(short * shift_cost)}/tuần.")
    r.act.append("Trong thời gian thiếu người, bật chế độ bận trên ứng dụng sàn vào cao điểm tối để tránh hủy đơn "
                 "và giảm điểm đánh giá.")
    r.watch = ["Thời gian chuẩn bị và tỷ lệ tự hủy đơn App trong tuần kế tiếp.",
               "Điểm đánh giá và số đơn sàn trong 2–3 tuần sau: ảnh hưởng lên thứ hạng sàn đến muộn."]
    return r


def _p5(G, ctx, b, w):
    r = Rec("P5", C.CAUSE_NAMES["P5"], "Quản lý chi nhánh; kiểm soát nội bộ nếu xác minh có sai phạm", "trong 2 ngày")
    c = _row(ctx["cash"], b, w)
    if c is None or c.staff_code is None:
        return r
    excess = max(c["count"] - c.receipts * c.expected_rate, 0.0)
    r.impact = [(f"Hóa đơn bị {c.kind} của {c.staff_code}", c["count"], "don",
                 f"Trên {c.receipts} hóa đơn của thu ngân này trong tuần."),
                ("Vượt mức của thu ngân khác", excess, "don", f"Thu ngân khác cùng chi nhánh: {pct(c.expected_rate)}."),
                (f"Giá trị các hóa đơn bị {c.kind}", c.amount, "vnd", "Tổng giá trị, chưa phải số tiền thất thoát.")]
    detail = ""
    if c.kind == "hủy":
        cw = G["mart_cashier_weekly"]
        x = cw[(cw.branch_id == b) & (cw.week_start == w) & (cw.staff_code == c.staff_code)]
        if len(x):
            detail = f" Có {int(x.quick_voids.iloc[0])} hóa đơn hủy trong 10 phút sau khi in, {int(x.cash_voids.iloc[0])} hóa đơn tiền mặt."
    r.verify = [f"Rà từng hóa đơn bị {c.kind} của {c.staff_code} trong tuần, ưu tiên hóa đơn tiền mặt.{detail}",
                "Đối chiếu với camera quầy và biên bản kiểm két cuối ca."]
    r.act = [f"Trong thời gian xác minh, yêu cầu quản lý ca duyệt mọi lệnh {c.kind} tại quầy.",
             "Không kết luận gian lận chỉ dựa trên thống kê; trao đổi với nhân viên sau khi có bằng chứng đối chiếu."]
    r.watch = [f"Tỷ lệ {c.kind} của {c.staff_code} so với các thu ngân khác trong 2–4 tuần."]
    return r


def _unknown(G, ctx, b, w):
    cur = _kpi(G, b, w)
    gap = cur.loc["net_sales"].gap_vs_expected if "net_sales" in cur.index else np.nan
    up = pd.notna(gap) and gap > 0
    r = Rec("?", "Chưa xác định nguyên nhân", "Quản lý vận hành", "theo dõi thêm 1 tuần")
    r.impact = [("Doanh thu so với kỳ vọng", gap, "vnd", "Đã trừ biến động chung của nhóm chi nhánh cùng hạng.")]
    r.verify = ["Xem cây KPI bên dưới: chênh lệch nằm ở kênh nào, do số đơn hay giá trị đơn.",
                "Kiểm tra dữ liệu của tuần ở trang Chất lượng dữ liệu: thiếu tệp nguồn cũng làm doanh thu lệch giả.",
                "Hỏi chi nhánh về sự kiện tại chỗ: sửa đường, đối thủ khai trương, mất điện, khuyến mãi riêng."]
    r.act = (["Tìm hiểu nguyên nhân tăng như sự kiện, khuyến mãi, kênh mới để áp dụng cho chi nhánh khác."] if up else
             ["Chưa đủ căn cứ để hành động; không quy trách nhiệm khi chưa rõ nguyên nhân."])
    r.watch = ["Nếu chênh lệch kéo dài từ 2 tuần, chuyển quản lý vùng xem xét."]
    return r
