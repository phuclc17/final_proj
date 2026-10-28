"""Bo mo phong: dong vai cac he thong nguon cua doanh nghiep. Trang nay cho thay du lieu duoc sinh ra the nao:
mot ngay "that" cua the gioi mo phong, moi he thong nguon ghi lai phan no thay (kem loi rieng), kich ban su co
duoc dua vao, va cac tham so cua mo hinh.

Trang DOC DAP AN (ground_truth/) - cong cu trinh bay, kiem chung bo mo phong. Pipeline va bo phat hien KHONG doc dap an;
moi so lieu "he thong ghi nhan" tren trang nay lay tu kho du lieu va tep nguon, dung nhu pipeline nhin thay."""
import glob
import html
import json
import os

import altair as alt
import pandas as pd
import streamlit as st

import ui
from common import ROOT, current_profile, query, vn
from dataviews import load_file
from simulator import config as SC

profile = current_profile()
SRC = ROOT / "data" / profile / "source_systems"
GT = ROOT / "data" / profile / "ground_truth"
CAUSE = {"P1a": "Hoa hồng sàn sai hợp đồng", "P1b": "Đơn sàn không vào POS", "P2": "Hao hụt nguyên liệu",
         "P3": "Thiếu nhân sự bếp ca tối", "P4": "Thất thoát kho", "P5": "Gian lận tại quầy"}
CLASS = SC.STORE_CLASS_BY_TIER
# mo ta kich ban co dau de trinh bay (tep cau hinh cua bo mo phong viet khong dau); khoa = ma kich ban
STORY_VI = {
    "S1": "GrabFood tính hoa hồng 30% thay vì 25% theo hợp đồng, trong 3 tuần",
    "S2": "Nhân viên bỏ qua, không nhập 20% đơn sàn vào POS (bình thường 3%)",
    "S3": "Vi phạm nhập trước xuất trước, nguyên liệu tươi hỏng nhiều: hao hụt gấp 1,15–1,30 lần",
    "S4": "Quản lý điều 55% nhân viên ca tối sang ca sáng: tối quá tải, sáng thừa người",
    "S5": "Mất cắp nguyên liệu giá trị cao trước kỳ kiểm kê 30/6",
    "S6": "Một thu ngân hủy hóa đơn tiền mặt sau khi đã thu tiền (12% đơn tiền mặt của người này)",
    "H1": "ShopeeFood tính hoa hồng 26% thay vì 22%, trong 2 tuần",
    "H2": "Nhân viên bỏ qua, không nhập 15% đơn sàn vào POS",
    "H3": "Hao hụt nguyên liệu tươi gấp 1,12–1,25 lần",
    "H4": "Điều 45% nhân viên ca tối sang ca sáng",
    "H5": "Mất cắp nguyên liệu trước kỳ kiểm kê 25/8",
    "H6": "Thu ngân hủy hóa đơn tiền mặt sau khi đã thu tiền (10% đơn tiền mặt của người này)",
    "L1": "Minh họa môi trường vận hành: điều 55% nhân viên ca tối CN3 sang ca sáng trong 2 tuần",
    "L2": "Minh họa môi trường vận hành: ShopeeFood tính hoa hồng CN1 cao hơn hợp đồng trong 2 tuần",
}
CODE_OF_TYPE = {"commission_overcharge": "P1a", "marketplace_not_entered": "P1b", "fresh_waste": "P2",
                "evening_understaffing": "P3", "stock_theft": "P4", "cashier_void_fraud": "P5"}

ui.header("Bộ mô phỏng", "Mỗi ngày kinh doanh được sinh một lần như sự kiện thật, rồi từng hệ thống xuất ra phần nó thấy, "
                         "theo định dạng và kèm lỗi riêng. Trang này đặt sự thật cạnh những gì các hệ thống ghi lại.")
ui.note("Trang kiểm chứng, có đọc đáp án", "Đường ống dữ liệu và bộ phát hiện không đọc đáp án. Phần hệ thống ghi nhận "
        "dưới đây lấy từ tệp nguồn và kho dữ liệu, đúng như đường ống nhìn thấy.", "chờ")
if not (GT / "daily_branch_truth.csv").exists():
    st.caption("Môi trường này chưa có dữ liệu của bộ mô phỏng.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_truth(prof, mtime):
    g = ROOT / "data" / prof / "ground_truth"
    t = pd.read_csv(g / "daily_branch_truth.csv", parse_dates=["date"])
    scen = pd.DataFrame(json.load(open(g / "scenarios.json", encoding="utf-8"))["scenarios"])
    scen["start"], scen["end"] = pd.to_datetime(scen.start), pd.to_datetime(scen.end)
    scen["code"] = scen.type.map(CODE_OF_TYPE).fillna(scen.pain_point)   # dap an ghi P1 chung cho ca P1a, P1b
    scen["story"] = scen.id.map(STORY_VI).fillna(scen.story)
    com = pd.read_csv(g / "commission_truth.csv", parse_dates=["week_start"])
    return t, scen, com


truth, scen, com_truth = load_truth(profile, os.path.getmtime(GT / "daily_branch_truth.csv"))
branches = query(profile, """select branch_id, branch_name, store_class, pos_terminal_prefix, app_branch_code,
                                    timekeeping_branch_code, grab_store_name, shopee_store_code
                             from gold.dim_branch order by branch_id""")
if branches is None:
    st.caption("Kho dữ liệu của môi trường này chưa được dựng.")
    st.stop()
B = branches.set_index("branch_id")
dmin, dmax = truth.date.min(), truth.date.max()


def blabel(b):
    return f"CN{b} · {B.branch_name[b]} · hạng {B.store_class[b]}"


def default_day():
    """Mac dinh mo mot ngay dang ke: ngay ban nhat (tai bep cao nhat) cua kich ban thieu nhan su, neu co.
    Tap van hanh thu: kich ban cua chinh tap nay (ma L...), khong co thi ngay moi nhat."""
    cand = scen[scen.id.str.startswith("L")] if profile == "live" else scen
    p3 = cand[(cand.code == "P3") & (cand.start <= dmax)]
    if len(p3):
        s = p3.iloc[0]
        w = truth[(truth.branch_id == s.branch_id) & truth.date.between(s.start, min(s.end, dmax))]
        w = w[w.kitchen_evening >= 1] if (w.kitchen_evening >= 1).any() else w   # tranh ngay cuc doan, de giai thich
        if len(w):
            r = w.loc[w.orders_served.idxmax()]
            return int(r.branch_id), r.date
    return 1, dmax


TABLE_CSS = """<style>
.st-tb {width:100%; border-collapse:collapse; font-size:14px; margin:2px 0 6px 0;}
.st-tb th {text-align:left; background:#F9FAFB; color:#4B5563; font-weight:500; padding:8px 10px;
           border-bottom:1px solid #E5E7EB;}
.st-tb td {padding:8px 10px; border-bottom:1px solid #F1F2F4; vertical-align:top; color:#111827; line-height:1.45;}
.st-tb td.ok {color:#067647; font-weight:500;} .st-tb td.bad {color:#B42318; font-weight:500;}
.st-tb td.hid {color:#B54708; font-weight:500;} .st-tb td.num {white-space:nowrap;}
</style>"""


def html_table(df, tones=None, num=()):
    """Bang HTML tu xuong dong (bang du lieu cua Streamlit cat chu dai). tones: lop CSS cho cot cuoi tung dong."""
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    body = []
    for i, row in enumerate(df.itertuples(index=False)):
        cells = []
        for j, v in enumerate(row):
            cls = (tones[i] if tones and j == len(row) - 1 else "") or ("num" if df.columns[j] in num else "")
            cells.append(f"<td class='{cls}'>{html.escape(str(v))}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    st.markdown(TABLE_CSS + f"<table class='st-tb'><tr>{head}</tr>{''.join(body)}</table>", unsafe_allow_html=True)


# chuyen tu trang khac (vd Van hanh hang ngay) toi mot chi nhanh, ngay cu the
goto = st.session_state.pop("sim_goto", None)
kb, kd = f"sim_b_{profile}", f"sim_d_{profile}"
if goto and goto[0] == profile:
    st.session_state[kb], st.session_state[kd] = int(goto[1]), pd.Timestamp(goto[2]).date()
if kb not in st.session_state:
    b0, d0 = default_day()
    st.session_state[kb], st.session_state[kd] = b0, d0.date()

tab_day, tab_scen, tab_model = st.tabs(["Một ngày, bảy góc nhìn", "Kịch bản sự cố", "Nguyên lý và tham số"])

# ==================================================================== 1. mot ngay, bay goc nhin
def day_view():
    c1, c2 = st.columns([2, 1])
    b = c1.selectbox("Chi nhánh", B.index.tolist(), key=kb, format_func=blabel)
    d = pd.Timestamp(c2.date_input("Ngày", key=kd, min_value=dmin.date(), max_value=dmax.date(), format="DD/MM/YYYY"))
    tr = truth[(truth.branch_id == b) & (truth.date == d)]
    if tr.empty:
        st.caption("Không có dữ liệu mô phỏng cho ngày này.")
        return
    tr = tr.iloc[0]
    ws = d - pd.Timedelta(days=d.weekday())
    active = scen[(scen.branch_id == b) & (scen.start <= d) & (scen.end >= d)]
    tags = []
    if tr.holiday:
        tags.append("ngày lễ")
    if tr.rain:
        tags.append("trời mưa")
    tags.append(["thứ Hai", "thứ Ba", "thứ Tư", "thứ Năm", "thứ Sáu", "thứ Bảy", "Chủ nhật"][d.weekday()])
    st.markdown(f"#### {blabel(b)} · {d:%d/%m/%Y} · {', '.join(tags)}")
    for s in active.itertuples():
        ui.note(f"Kịch bản sự cố {s.id} · {CAUSE.get(s.code, s.code)}", f"{s.start:%d/%m} – {s.end:%d/%m}. {s.story}.",
                "Cảnh báo")

    st.subheader("1. Sự thật của ngày, do bộ mô phỏng sinh ra")
    m = st.columns(3) + st.columns(3)
    m[0].metric("Khách muốn đặt", vn(tr.orders_demand), border=True)
    m[1].metric("Đơn được phục vụ", vn(tr.orders_served), border=True)
    m[2].metric("Khách tại quầy bỏ về", vn(tr.walkin_balked), border=True)
    m[3].metric("Đơn bị hủy", vn(tr.store_cancelled + tr.customer_cancelled), border=True)
    m[4].metric("Tải bếp giờ cao điểm", vn(tr.peak_util * 100) + "%", border=True)
    m[5].metric("Thời gian chuẩn bị bình quân", vn(tr.avg_prep_min, 1) + " phút", border=True)
    st.caption(f"Khách muốn đặt là số đơn khách định đặt ở mọi kênh. Đơn bị hủy gồm {vn(tr.store_cancelled)} do cửa hàng và "
               f"{vn(tr.customer_cancelled)} do khách. Tải bếp là số đơn trong giờ chia năng lực của số nhân viên bếp có "
               "mặt; trên 90% bếp bắt đầu quá tải.")

    # -------------------------------------------------- he thong ghi nhan
    day = query(profile, f"select * from gold.mart_branch_daily where branch_id = {b} and date_day = '{d:%Y-%m-%d}'")
    wk = query(profile, f"select * from gold.mart_branch_weekly where branch_id = {b} and week_start = '{ws:%Y-%m-%d}'")
    st.subheader("2. Mỗi hệ thống ghi lại được gì")
    if day is None or day.empty:
        st.caption("Ngày này chưa được đường ống nạp vào kho. Tệp có thể vừa được xuất và chưa xử lý xong.")
    else:
        r = day.iloc[0]
        w = wk.iloc[0] if wk is not None and len(wk) else None
        miss_pos = int(tr.served_grabfood - r.orders_grabfood + tr.served_shopeefood - r.orders_shopeefood)
        valid = int(r.pos_receipts_walkin - r.voids)   # hoa don con hieu luc (bo hoa don bi huy)
        refund = query(profile, f"select count(*) n from gold.fact_order where branch_id = {b} and channel = 'APP' "
                                f"and date_day = '{d:%Y-%m-%d}' and order_status = 'REFUNDED'")
        app_ref = int(refund.n.iloc[0]) if refund is not None else 0
        app_note = ("khớp" if tr.served_app == r.orders_app else
                    f"khớp, tính cả {vn(app_ref)} đơn đã giao rồi hoàn tiền" if tr.served_app == r.orders_app + app_ref
                    else "lệch")
        gap = int(tr.served_walkin - valid)
        walk_note = ("khớp" if gap == 0 else
                     f"thiếu {vn(gap)}: hóa đơn bị thu ngân hủy sau khi đã thu tiền" if gap == tr.fraud_void_count
                     else "lệch")

        def same(a, x):
            return "khớp" if round(float(a), 1) == round(float(x), 1) else ""

        rows = [
            ("Khách muốn đặt", vn(tr.orders_demand), "không hệ thống nào thấy trọn", "—",
             "Nhu cầu chỉ lộ ra một phần, qua đơn được phục vụ và đơn bị hủy"),
            ("Đơn tại quầy được phục vụ", vn(tr.served_walkin),
             f"{vn(valid)} hóa đơn còn hiệu lực trên {vn(r.pos_receipts_walkin)}, {vn(r.voids)} bị hủy", "POS",
             walk_note),
            ("Khách tại quầy bỏ về vì chờ lâu", vn(tr.walkin_balked), "không ghi nhận", "—",
             "Mất doanh thu mà không hệ thống nào thấy; chỉ suy ra được qua tín hiệu nhân sự, thời gian chờ"),
            ("Đơn App giao thành công", vn(tr.served_app),
             f"{vn(r.orders_app)} đơn hoàn thành" + (f", {vn(app_ref)} hoàn tiền" if app_ref else ""), "App", app_note),
            ("Đơn GrabFood được phục vụ", vn(tr.served_grabfood), f"{vn(r.orders_grabfood)} đơn trên POS",
             "POS, nhân viên nhập tay", same(tr.served_grabfood, r.orders_grabfood)
             or f"thiếu {vn(tr.served_grabfood - r.orders_grabfood)}: đơn sàn không được nhập POS"),
            ("Đơn ShopeeFood được phục vụ", vn(tr.served_shopeefood), f"{vn(r.orders_shopeefood)} đơn trên POS",
             "POS, nhân viên nhập tay", same(tr.served_shopeefood, r.orders_shopeefood)
             or f"thiếu {vn(tr.served_shopeefood - r.orders_shopeefood)}: đơn sàn không được nhập POS"),
            ("Đơn bị cửa hàng hủy", vn(tr.store_cancelled), f"{vn(r.app_store_cancels)} đơn App",
             "App; sàn chỉ báo tổng cả tuần", "đơn hủy trên sàn chỉ có trong báo cáo đối soát tuần"),
            ("Thời gian chuẩn bị bình quân", vn(tr.avg_prep_min, 1) + " phút", vn(r.app_avg_prep_min, 1) + " phút",
             "App", "chỉ App ghi thời điểm bếp xong món"),
            ("Nhân viên bếp ca tối", vn(tr.kitchen_evening, 1) + " người, bình quân theo giờ",
             f"{vn(r.kitchen_evening)} ca có chấm công", "Máy chấm công", "chấm công đếm ca, không đếm người theo giờ"),
            ("Doanh thu", vn(tr.served_value) + " đ", vn(r.net_sales) + " đ doanh thu thuần", "POS + App, sau làm sạch",
             "kho tính sau giảm giá; thiếu phần đơn sàn không vào POS, hóa đơn bị hủy"),
            ("Hóa đơn thu ngân hủy gian lận", vn(tr.fraud_void_count), f"{vn(r.voids)} hóa đơn hủy với mọi lý do", "POS",
             "POS không phân biệt hủy hợp lệ và gian lận; phải thống kê theo từng thu ngân"),
            ("Hao hụt vượt mức thường", vn(tr.waste_excess_value) + " đ", "chưa thấy trong ngày", "Kiểm kê 2 tuần/lần",
             "chỉ lộ ra khi đặt nhập kho, lượng bán, tồn kiểm kê cạnh nhau"),
            ("Nguyên liệu bị lấy mất", vn(tr.theft_value) + " đ", "chưa thấy trong ngày", "Kiểm kê 2 tuần/lần", ""),
            ("Trời mưa", "có" if tr.rain else "không", ("có" if r.is_rain else "không") + f", {vn(r.precipitation_mm, 1)} mm",
             "Dịch vụ thời tiết", same(tr.rain, r.is_rain)),
        ]
        if w is not None:
            rows.append(("Đơn GrabFood cả tuần", "—", f"sàn báo {vn(w.grabfood_settled_orders)}, POS ghi {vn(w.orders_grabfood)}",
                         "Báo cáo đối soát tuần GrabFood", "đối chiếu hai nguồn này là cách phát hiện đơn không vào POS"))
        tbl = pd.DataFrame(rows, columns=["Đại lượng", "Sự thật", "Hệ thống ghi nhận", "Ghi nhận ở đâu",
                                          "Nhận xét"])
        tones = ["ok" if str(x).startswith("khớp") else "bad" if str(x).startswith(("thiếu", "lệch"))
                 else "hid" if "không" in str(y) or "chưa" in str(y) else ""
                 for x, y in zip(tbl["Nhận xét"], tbl["Hệ thống ghi nhận"])]
        html_table(tbl, tones, num=("Sự thật",))
        note = (f"Hôm nay có {vn(tr.mkt_not_entered)} đơn sàn nhân viên quên nhập POS, khớp với phần thiếu ở hai dòng GrabFood, "
                f"ShopeeFood." if tr.mkt_not_entered and miss_pos == tr.mkt_not_entered else "")
        st.caption("Các con số khớp nhau vì mọi hệ thống được sinh từ cùng một tập sự kiện; chỗ lệch đến từ lỗi vận hành "
                   "hoặc giới hạn của từng hệ thống, đúng như ngoài thực tế. " + note)

    # -------------------------------------------------- tep nguon cua ngay
    st.subheader("3. Tệp gốc mà các hệ thống xuất cho ngày này")
    P, T = B.pos_terminal_prefix[b], B.timekeeping_branch_code[b]
    found = {
        "POS": f"pos/{P}/pos_export_{d:%Y-%m-%d}.json",
        "App": f"owned_app/orders_{d:%Y%m%d}.json",
        "Máy chấm công": f"timekeeping/{T}/punch_{T}_{d:%Y%m%d}.csv",
        "Sổ nhập kho": next(iter(glob.glob(str(SRC / "warehouse_receipts" / f"CN{b:02d}" / f"*_{d:%Y%m%d}.xlsx"))), None),
        "Phiếu kiểm kê": next(iter(glob.glob(str(SRC / "stock_counts" / f"CN{b:02d}" / f"*_{d:%Y%m%d}.xlsx"))), None),
        "Báo cáo tuần GrabFood": next(iter(glob.glob(str(SRC / "grabfood" / f"*_{ws:%Y%m%d}_*.csv"))), None),
        "Báo cáo tuần ShopeeFood": next(iter(glob.glob(str(SRC / "shopeefood" / f"*_{ws:%Y%m%d}_*.xlsx"))), None),
        "Thời tiết": f"external/weather/weather_hcm_{d:%Y%m%d}.json",
    }
    rel = {k: (os.path.relpath(v, SRC).replace("\\", "/") if v and os.path.isabs(v) else v) for k, v in found.items()}
    paths = [v for v in rel.values() if v]
    log = query(profile, "select file_path, row_count, ingested_at from bronze._ingest_log where status in ('loaded', 'reloaded') "
                         "and file_path in (" + ",".join(f"'{p}'" for p in paths) + ")") if paths else None
    log = log.set_index("file_path") if log is not None else pd.DataFrame()
    frows = []
    for k, p in rel.items():
        if not p or not (SRC / p).exists():
            frows.append((k, "không có tệp trong ngày này", "", "", ""))
            continue
        inlog = p in log.index
        frows.append((k, p, f"{(SRC / p).stat().st_size / 1024:,.1f} KB".replace(",", "X").replace(".", ",").replace("X", "."),
                      vn(log.row_count[p]) if inlog else "", f"{pd.Timestamp(log.ingested_at[p]):%d/%m %H:%M}" if inlog else "chưa nạp"))
    st.dataframe(pd.DataFrame(frows, columns=["Hệ thống", "Tệp", "Kích thước", "Dòng nạp vào Bronze", "Nạp lúc"]),
                 hide_index=True, width="stretch")

    st.markdown("**Xem nguyên văn**")
    vt = st.tabs(["POS", "App", "Chấm công", "Sổ nhập kho", "Báo cáo sàn", "Thời tiết"])
    with vt[0]:
        if (SRC / rel["POS"]).exists():
            _, rec, _ = load_file(str(SRC / rel["POS"]))
            st.caption(f"{vn(len(rec))} hóa đơn trong tệp; dưới đây là hóa đơn đầu tiên, đúng như máy POS xuất ra.")
            st.json(rec[0], expanded=1)
    with vt[1]:
        if (SRC / rel["App"]).exists():
            _, rec, meta = load_file(str(SRC / rel["App"]))
            mine = [o for o in rec if (o.get("branch_ref") or {}).get("code") == B.app_branch_code[b]]
            st.caption(f"Tệp App chứa {vn(len(rec))} đơn của mọi chi nhánh, {vn(len(mine))} đơn của chi nhánh này. "
                       "Thời gian lưu theo giờ UTC, chậm hơn giờ Việt Nam 7 tiếng.")
            if mine:
                st.json(mine[0], expanded=1)
    with vt[2]:
        if (SRC / rel["Máy chấm công"]).exists():
            df, _, _ = load_file(str(SRC / rel["Máy chấm công"]))
            st.caption("Mỗi dòng là một lượt quẹt thẻ. Có thể thấy lượt quẹt bị máy ghi trùng, hai lượt vào cách nhau vài "
                       "chục giây, và nhân viên quên quẹt ra.")
            st.dataframe(df, hide_index=True, width="stretch")
    with vt[3]:
        p = rel["Sổ nhập kho"]
        if p:
            df, _, _ = load_file(str(SRC / p))
            st.caption("Ô Excel nguyên trạng, gồm cả dòng tiêu đề phiếu, dòng Tổng cộng và chữ ký." if "NhapKho" in p else
                       "Mẫu sổ thứ hai: tên không dấu, số lượng dính đơn vị.")
            st.dataframe(df, hide_index=True, width="stretch")
        else:
            st.caption("Chi nhánh không nhập kho ngày này.")
    with vt[4]:
        for k in ("Báo cáo tuần GrabFood", "Báo cáo tuần ShopeeFood"):
            p = rel[k]
            if p:
                df, _, _ = load_file(str(SRC / p))
                st.caption(f"{k}: một tệp cho cả chuỗi, chỉ có số tổng theo cửa hàng, không ghi tỷ lệ hoa hồng.")
                st.dataframe(df.head(14), hide_index=True, width="stretch")
            else:
                st.caption(f"{k}: sàn chưa gửi báo cáo cho tuần này. Báo cáo đến sau khi tuần kết thúc.")
    with vt[5]:
        if (SRC / rel["Thời tiết"]).exists():
            _, rec, _ = load_file(str(SRC / rel["Thời tiết"]))
            st.json(rec[0] if rec else {}, expanded=True)

    # -------------------------------------------------- loi du lieu trong tep cua ngay
    st.subheader("4. Lỗi dữ liệu nằm trong tệp của ngày này và cách tầng Silver xử lý")
    tk, wh, pos = rel["Máy chấm công"], rel["Sổ nhập kho"], rel["POS"]
    q = lambda sql: query(profile, sql)  # noqa: E731
    dup = q(f"select count(*) n from silver.silver_quarantine where _source_file = '{tk}' and dq_issue = 'quet_trung'")
    miss = q(f"select count(*) n from silver.stg_timekeeping__shifts where branch_id = {b} "
             f"and work_date = '{d:%Y-%m-%d}' and is_missing_checkout")
    ver = q(f"select pos_version v, count(*) n from silver.stg_pos__receipts where _source_file = '{pos}' group by 1")
    err = [("Lượt quẹt thẻ bị máy ghi trùng", "Máy chấm công", vn(dup.n.iloc[0]) if dup is not None else "—",
            "cách ly, không tính giờ hai lần", ""),
           ("Quên quẹt thẻ khi ra ca", "Máy chấm công", vn(miss.n.iloc[0]) if miss is not None else "—",
            "giữ ca, gắn cờ thiếu lượt ra; Gold nội suy số giờ có cờ", "")]
    if ver is not None and len(ver):
        v = ver.iloc[0]
        old = str(v["v"]).startswith("v2")
        err.append(("POS phiên bản cũ: ngày ISO, tiền dạng chuỗi \"89.000\", cột grand_total" if old else
                    "POS phiên bản mới: ngày dd/mm/yyyy, cột total_paid", "POS", vn(v["n"]),
                    "nhận diện phiên bản, chuẩn hóa về một lược đồ", v["v"]))
    if wh:
        wq = q(f"select dq_issue, count(*) n, any_value(raw_name) ten, any_value(raw_qty) sl, any_value(median_qty) tv "
               f"from silver_work.checked_inventory__receipts where _source_file = '{wh}' and dq_issue is not null group by 1")
        var = q(f"select l.raw_name, i.ingredient_name from silver.stg_inventory__receipt_lines l "
                f"join gold.dim_ingredient i on i.ingredient_id = cast(l.ingredient_id as integer) "
                f"where l._source_file = '{wh}' and l.ingredient_match_method = 'bang_bien_the'")
        n_silver = q(f"select count(*) n from silver.stg_inventory__receipt_lines where _source_file = '{wh}'")
        n_bronze = int(log.row_count[wh]) if wh in log.index else None
        n_q = int(wq.n.sum()) if wq is not None and len(wq) else 0
        if n_bronze is not None and n_silver is not None:
            err.append(("Dòng Tổng cộng, chữ ký, tiêu đề lẫn trong bảng", "Sổ nhập kho",
                        vn(n_bronze - int(n_silver.n.iloc[0]) - n_q), "tách thành dòng cấu trúc, không đưa vào dữ liệu", ""))
        if var is not None and len(var):
            ex = "; ".join(f"“{a}” thành {c}" for a, c in var.drop_duplicates().head(3).itertuples(index=False))
            err.append(("Tên nguyên liệu viết khác danh mục", "Sổ nhập kho", vn(len(var)),
                        "ánh xạ qua bảng biến thể tên", ex))
        if wq is not None:
            for x in wq.itertuples():
                if x.dq_issue == "nghi_go_gam_vao_cot_kg":
                    err.append(("Gõ số gam vào cột kg", "Sổ nhập kho", vn(x.n), "cách ly kèm lý do",
                                f"“{x.ten}” {x.sl} kg, trung vị {vn(x.tv, 1)} kg"))
        if os.path.basename(wh).startswith("receipts_"):
            err.append(("Số lượng dính đơn vị trong một ô", "Sổ nhập kho mẫu B", vn(n_bronze) if n_bronze else "—",
                        "tách số và đơn vị", "ví dụ \"90.9kg\""))
    err.append(("Thời gian App lưu theo giờ UTC", "App", "mọi đơn", "đổi sang giờ Việt Nam trước khi xác định ngày, ca",
                "01:41Z là 08:41 giờ Việt Nam"))
    html_table(pd.DataFrame(err, columns=["Lỗi", "Hệ thống", "Số dòng trong tệp ngày này", "Tầng Silver xử lý",
                                          "Ví dụ"]))
    st.caption("Lỗi được bộ mô phỏng cài vào theo xác suất cố định cho từng hệ thống, xem thẻ Nguyên lý và tham số. Đường "
               "ống không biết trước dòng nào lỗi mà tự phát hiện bằng quy tắc ở tầng Silver.")

with tab_day:
    day_view()

# ==================================================================== 2. kich ban su co
with tab_scen:
    st.caption("Mỗi tập dữ liệu có các kịch bản sự cố được đưa vào thế giới mô phỏng, có đáp án biết trước để chấm điểm "
               "bộ phát hiện. Tập phát triển dùng để xây dựng phương pháp, tập kiểm tra chỉ dùng một lần để đánh giá.")
    if scen.empty:
        st.caption("Môi trường này không có kịch bản sự cố.")
    else:
        sc = scen.assign(label=scen.apply(lambda s: f"{s.id} · CN{s.branch_id} · {s.code} {CAUSE.get(s.code, '')}",
                                          axis=1), end1=scen.end + pd.Timedelta(days=1))
        span = pd.DataFrame({"start": [dmin], "end1": [dmax + pd.Timedelta(days=1)]})
        gantt = (alt.Chart(span).mark_rect(color="#f4f6f8").encode(x="start:T", x2="end1:T")
                 + alt.Chart(sc).mark_bar(height=16, cornerRadius=3).encode(
                     x=alt.X("start:T", title=None, axis=alt.Axis(format="%d/%m", labelAngle=0)), x2="end1:T",
                     y=alt.Y("label:N", title=None, sort=sc.sort_values("start").label.tolist(),
                             axis=alt.Axis(labelLimit=320)),
                     color=alt.Color("code:N", title="Vấn đề", legend=None),
                     tooltip=["id", "code", alt.Tooltip("start:T", format="%d/%m/%Y"),
                              alt.Tooltip("end:T", format="%d/%m/%Y"), "story"]))
        st.altair_chart(gantt.properties(height=34 * len(sc) + 30), width="stretch")
        pick = st.selectbox("Xem tác động của kịch bản", sc.sort_values("start").label.tolist())
        s = sc[sc.label == pick].iloc[0]
        st.markdown(f"**{s.id}: {s.story}**")
        bt = truth[truth.branch_id == s.branch_id]
        tier = B.store_class[s.branch_id]
        peers = [i for i in B.index if B.store_class[i] == tier and i != s.branch_id]
        METRICS = {"P1a": [], "P1b": [("mkt_not_entered", "Đơn sàn không được nhập POS")],
                   "P2": [("waste_excess_value", "Hao hụt vượt mức thường, đ")],
                   "P3": [("kitchen_evening", "Nhân viên bếp ca tối"), ("peak_util", "Tải bếp giờ cao điểm"),
                          ("avg_prep_min", "Thời gian chuẩn bị, phút"), ("store_cancelled", "Đơn bị cửa hàng hủy"),
                          ("walkin_balked", "Khách bỏ về")],
                   "P4": [("theft_value", "Nguyên liệu bị lấy mất, đ")],
                   "P5": [("fraud_void_count", "Hóa đơn bị hủy gian lận"), ("fraud_void_value", "Giá trị hóa đơn gian lận, đ")]}
        before = bt[bt.date.between(s.start - pd.Timedelta(days=28), s.start - pd.Timedelta(days=1))]
        during = bt[bt.date.between(s.start, s.end)]
        def fmt(c, v):
            return vn(v * 100, 0) + "%" if c == "peak_util" else vn(v, 0 if c.endswith("value") else 1)
        imp = [(lbl, fmt(c, before[c].mean()), fmt(c, during[c].mean())) for c, lbl in METRICS.get(s.code, [])]
        if s.code == "P1a":
            ct = com_truth[(com_truth.branch_id == s.branch_id)]
            rate_in = ct[ct.week_start.between(s.start - pd.Timedelta(days=6), s.end)]
            plat = rate_in.loc[rate_in.commission_rate_applied.idxmax(), "platform"] if len(rate_in) else ""
            imp.append((f"Tỷ lệ hoa hồng {plat} thực thu", vn(SC.COMMISSION_CONTRACT.get(plat, 0) * 100, 0) + "% (hợp đồng)",
                        vn(rate_in[rate_in.platform == plat].commission_rate_applied.max() * 100, 0) + "%"))
        wsum = (truth.assign(week=truth.date - pd.to_timedelta(truth.date.dt.weekday, unit="D"))
                .groupby(["week", "branch_id"]).served_value.sum().unstack())
        ratio = (wsum[s.branch_id] / wsum[peers].mean(axis=1) - 1)
        imp.append(("Doanh thu so với chi nhánh cùng hạng (theo tuần)",
                    vn(ratio[(ratio.index >= s.start - pd.Timedelta(days=28)) & (ratio.index < s.start)].mean() * 100, 1) + "%",
                    vn(ratio[(ratio.index >= s.start - pd.Timedelta(days=6)) & (ratio.index <= s.end)].mean() * 100, 1) + "%"))
        html_table(pd.DataFrame(imp, columns=["Đại lượng (bình quân mỗi ngày)", "4 tuần trước sự cố", "Trong sự cố"]))
        lo, hi = s.start - pd.Timedelta(days=35), min(s.end + pd.Timedelta(days=35), dmax)
        band = alt.Chart(pd.DataFrame({"s": [s.start], "e": [s.end + pd.Timedelta(days=1)]})).mark_rect(
            opacity=0.15, color="#d62728").encode(x="s:T", x2="e:T")
        rw = ratio.rename("ty_le").reset_index()
        rw = rw[rw.week.between(lo, hi)]
        st.markdown(f"**CN{s.branch_id}: doanh thu thực so với trung bình chi nhánh cùng hạng {tier}, theo tuần**")
        st.altair_chart(band + alt.Chart(rw).mark_line(point=True).encode(
            x=alt.X("week:T", title=None, axis=alt.Axis(format="%d/%m")),
            y=alt.Y("ty_le:Q", title="Doanh thu so với cùng hạng", axis=alt.Axis(format="%")),
            tooltip=[alt.Tooltip("week:T", format="%d/%m/%Y"), alt.Tooltip("ty_le:Q", format="+.1%")]).properties(
            height=200), width="stretch")
        for c, lbl in METRICS.get(s.code, [])[:3]:
            win = bt[bt.date.between(lo, hi)]
            st.markdown(f"**{lbl} · CN{s.branch_id}, theo ngày**")
            st.altair_chart(band + alt.Chart(win).mark_bar(color="#3b6fb6").encode(
                x=alt.X("date:T", title=None, axis=alt.Axis(format="%d/%m")), y=alt.Y(f"{c}:Q", title=None),
                tooltip=[alt.Tooltip("date:T", format="%d/%m/%Y"), alt.Tooltip(f"{c}:Q", format=",.2f")]).properties(
                height=170), width="stretch")
        st.caption("Vùng tô là thời gian kịch bản diễn ra. Đây là sự thật của thế giới mô phỏng; bộ phát hiện phải tự tìm "
                   "ra sự cố từ dữ liệu các hệ thống ghi lại.")

# ==================================================================== 3. nguyen ly va tham so
with tab_model:
    st.markdown("**Một thế giới, nhiều góc nhìn.** Mỗi ngày, bộ mô phỏng sinh nhu cầu theo giờ và kênh, xếp ca nhân viên, "
                "tính tải bếp, quyết định từng đơn được phục vụ, bị hủy hay khách bỏ về, trừ tồn kho theo công thức món. "
                "Sau đó mỗi hệ thống nguồn chỉ xuất phần nó thấy. Vì cùng một tập sự kiện, các nguồn nhất quán với nhau "
                "như ngoài thực tế, và một sự cố gây ra dấu vết ở nhiều nguồn cùng lúc.")
    fig = ROOT / "docs" / "images" / "chuoi_nhan_qua.png"
    if fig.exists():
        st.image(str(fig), caption="Chuỗi nhân quả vận hành trong bộ mô phỏng", width=640)

    st.subheader("Nhu cầu và biến động bình thường")
    a, bcol = st.columns(2)
    dem = pd.DataFrame([(f"Hạng {CLASS[k]}", v) for k, v in SC.TIER_BASE_ORDERS.items()], columns=["Hạng", "Đơn mỗi ngày"])
    a.altair_chart(alt.Chart(dem).mark_bar(color="#3b6fb6").encode(
        x=alt.X("Hạng:N", title=None, axis=alt.Axis(labelAngle=0)), y="Đơn mỗi ngày:Q",
        tooltip=["Hạng", "Đơn mỗi ngày"]).properties(
        height=220, title="Nhu cầu cơ sở mỗi chi nhánh, ngày thường"), width="stretch")
    CH = {"WALKIN": "Tại quầy", "APP": "App", "GRABFOOD": "GrabFood", "SHOPEEFOOD": "ShopeeFood"}
    fac = pd.DataFrame([(CH[c], "Ngày lễ", SC.HOLIDAY_FACTOR[c] - 1) for c in CH] +
                       [(CH[c], "Ngày mưa", SC.RAIN_FACTOR[c] - 1) for c in CH], columns=["Kênh", "Yếu tố", "Thay đổi"])
    bcol.altair_chart(alt.Chart(fac).mark_bar().encode(
        x=alt.X("Kênh:N", title=None, axis=alt.Axis(labelAngle=0)), xOffset="Yếu tố:N",
        y=alt.Y("Thay đổi:Q", axis=alt.Axis(format="%"), title=None),
        color=alt.Color("Yếu tố:N", scale=alt.Scale(range=["#e0b100", "#3b6fb6"]),
                        legend=alt.Legend(orient="top", title=None)),
        tooltip=["Kênh", "Yếu tố", alt.Tooltip("Thay đổi:Q", format="+.0%")]).properties(
        height=220, title="Ngày lễ, ngày mưa làm đổi nhu cầu từng kênh"), width="stretch")
    days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
    rep = json.load(open(ROOT / "data" / "public_reference" / "calibration_report.json", encoding="utf-8"))["bread_basket"]
    wf = pd.DataFrame([(dd, "Bộ mô phỏng (giả định)", v) for dd, v in zip(days, SC.WEEKDAY_FACTOR)] +
                      [(dd, "Tiệm bánh thật The Bread Basket", v) for dd, v in zip(days, rep["weekday_factor_mon_to_sun"])],
                      columns=["Thứ", "Nguồn", "Hệ số"])
    a, bcol = st.columns(2)
    a.altair_chart(alt.Chart(wf).mark_line(point=True).encode(
        x=alt.X("Thứ:N", sort=days, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Hệ số:Q", scale=alt.Scale(zero=False)),
        color=alt.Color("Nguồn:N", scale=alt.Scale(range=["#c8102e", "#9aa5b1"]),
                        legend=alt.Legend(orient="top", columns=1, labelLimit=320, title=None)),
        tooltip=["Thứ", "Nguồn", "Hệ số"]).properties(height=240, title="Hệ số theo thứ trong tuần"), width="stretch")
    ipo = pd.DataFrame([(str(k), "Bộ mô phỏng", v) for k, v in zip(*SC.ITEMS_PER_ORDER)] +
                       [(k, "Tiệm bánh thật The Bread Basket", v) for k, v in rep["items_per_order_dist"].items()],
                       columns=["Số món", "Nguồn", "Tỷ lệ đơn"])
    bcol.altair_chart(alt.Chart(ipo).mark_bar().encode(
        x=alt.X("Số món:N", title="Số món mỗi đơn", axis=alt.Axis(labelAngle=0)), xOffset="Nguồn:N",
        y=alt.Y("Tỷ lệ đơn:Q", axis=alt.Axis(format="%")),
        color=alt.Color("Nguồn:N", scale=alt.Scale(range=["#c8102e", "#9aa5b1"]),
                        legend=alt.Legend(orient="top", columns=1, labelLimit=320, title=None)),
        tooltip=["Số món", "Nguồn", alt.Tooltip("Tỷ lệ đơn:Q", format=".0%")]).properties(
        height=240, title="Số món mỗi đơn: hiệu chỉnh từ giao dịch thật"), width="stretch")
    st.caption("Phân phối số món mỗi đơn, số lượng mỗi dòng, độ tập trung món bán chạy và độ dao động theo ngày được ước "
               "lượng từ 9.465 giao dịch thật của tiệm bánh The Bread Basket, bộ OpenML 43422, giấy phép CC0. Hệ số theo "
               "thứ và khung giờ không chuyển giao vì tiệm bánh khác mô hình đồ ăn nhanh, nên vẫn là giả định của tác giả.")

    st.subheader("Chuỗi nhân quả dịch vụ")
    html_table(pd.DataFrame([
        ("Tải bếp", "số đơn trong giờ / (năng lực mỗi nhân viên × số nhân viên bếp có mặt)", "thiếu người bếp làm tải tăng"),
        ("Thời gian chuẩn bị", f"{SC.PREP_BASE:g} + {SC.PREP_SCALE:g} / (1 − tải)^{SC.PREP_POWER:g} phút",
         "tăng rất nhanh khi tải gần 100%, như hàng đợi"),
        ("Khách tại quầy bỏ về", f"khi tải vượt {SC.BALK_START:.0%}, tỷ lệ tăng {SC.BALK_SLOPE:g} theo phần vượt, tối đa {SC.BALK_MAX:.0%}",
         "mất doanh thu không ai ghi nhận"),
        ("Cửa hàng tự hủy đơn giao", f"{SC.STORE_CANCEL_BASE:.1%} cơ sở, tăng khi tải vượt {SC.STORE_CANCEL_START:.0%}",
         "App ghi được, sàn chỉ báo tổng tuần"),
        ("Điểm đánh giá trên sàn", f"giảm {SC.RATING_PREP_SLOPE:g} điểm mỗi phút chờ trên {SC.RATING_PREP_START:g} phút, "
         f"trừ thêm theo tỷ lệ hủy", "trung bình trượt theo tuần"),
        ("Thứ hạng hiển thị trên sàn", f"1 + {SC.RANKING_SLOPE:g} × (điểm − {SC.RANKING_REF_RATING:g}), trong "
         f"[{SC.RANKING_MIN:g}; {SC.RANKING_MAX:g}]", "tuần sau ít người thấy quán hơn: doanh thu sàn giảm trễ"),
    ], columns=["Bước", "Quy luật", "Hệ quả"]))

    st.subheader("Lỗi dữ liệu được cài vào từng hệ thống")
    html_table(pd.DataFrame([
        ("POS", f"chi nhánh {', '.join(f'CN{x}' for x in sorted(SC.OLD_POS_BRANCHES))} dùng phần mềm bản cũ",
         "khác định dạng ngày, tiền dạng chuỗi, đổi tên cột tổng tiền"),
        ("POS", f"{SC.POS_MISS_MARKETPLACE:.0%} đơn sàn nhân viên quên nhập", "doanh thu sàn trên POS thiếu so với báo cáo sàn"),
        ("App", "mọi thời điểm lưu theo giờ UTC", "sai ngày, sai ca nếu không đổi giờ"),
        ("Máy chấm công", f"{SC.TK_DUP_RATE:.0%} ca bị ghi trùng lượt vào; {SC.TK_MISSING_OUT_RATE:.0%} ca quên quẹt ra",
         "giờ công tính sai nếu không xử lý"),
        ("Sổ nhập kho", f"chi nhánh {', '.join(f'CN{x}' for x in sorted(SC.RECEIPT_TEMPLATE_B_BRANCHES))} dùng mẫu sổ khác",
         "hai lược đồ cho cùng một nghiệp vụ, số lượng dính đơn vị"),
        ("Sổ nhập kho", f"{SC.RECEIPT_NAME_VARIANT_RATE:.0%} dòng ghi tên tắt, tên tự đặt; {SC.RECEIPT_KG_TYPO_RATE:.1%} dòng "
         "gõ số gam vào cột kg", "không khớp danh mục; số lượng lớn gấp nghìn lần"),
        ("Phiếu kiểm kê", f"{SC.COUNT_BLANK_RATE:.0%} ô bỏ trống; sai số đếm {SC.COUNT_NOISE_SD:.0%}",
         "thiếu số liệu; chênh lệch nhỏ không phải thất thoát"),
        ("Báo cáo sàn", "chỉ có số tổng theo tuần, không ghi tỷ lệ hoa hồng, tên cửa hàng theo cách của sàn",
         "phải tự tính tỷ lệ và tự ánh xạ chi nhánh"),
    ], columns=["Hệ thống", "Lỗi được cài", "Hệ quả nếu không làm sạch"]))
    st.caption("Mọi tham số nằm trong tệp simulator/config.py. Tập dữ liệu sinh lại được y hệt nhờ hạt giống ngẫu nhiên "
               "cố định; mỗi ngày mới được sinh tiếp từ trạng thái đã lưu.")
