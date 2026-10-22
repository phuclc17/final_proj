"""Trung tam canh bao: bo phat hien quet MOI chi nhanh x tuan theo bo chi so giam sat chung;
canh bao tu phat sinh tu du lieu, nguoi dung chon mot dong de truy vet."""
import altair as alt
import pandas as pd
import streamlit as st

import ui
from common import (C, analysis_page, detect, fmt_vnd, losses, money_short, pretty, selection, week_label,
                    weeks_in_period)

G, scores, alerts = analysis_page()
branch, start, end = selection()

ui.header("Trung tâm cảnh báo", "Mọi chi nhánh, mọi tuần được so với mức kỳ vọng theo cùng một bộ chỉ số giám sát, rồi "
                                "chấm điểm bằng chứng cho từng nguyên nhân.")

c1, c2, c3 = st.columns([2, 3, 2])
score_alert = c1.slider("Ngưỡng điểm phát cảnh báo", 2.0, 5.0, float(C.SCORE_ALERT), 0.5)
levels = c2.multiselect("Hiển thị mức", ["Cảnh báo", "Theo dõi", "Bình thường"], default=["Cảnh báo", "Theo dõi"])
order = c3.radio("Sắp xếp danh sách", ["Ước tính thiệt hại", "Điểm bằng chứng"], horizontal=True)
A = detect.alert_table(G, scores, score_alert=score_alert)
A = weeks_in_period(A, start, end)

# ---------------------------------------------------------------- ban do nhiet
heat = A.copy()
heat["chi_nhánh"] = "CN" + heat.branch_id.astype(str) + " · " + heat.store_class
heat["mức"] = heat.level
heat["nghi_vấn"] = heat.cause + " · " + heat.cause_name
if branch is not None:
    heat = heat[heat.branch_id == branch]
st.altair_chart(alt.Chart(heat).mark_rect(stroke="white").encode(
    x=alt.X("yearmonthdate(week_start):O", title="Tuần", axis=alt.Axis(format="%d/%m", labelAngle=-60)),
    y=alt.Y("chi_nhánh:N", title=None, sort=alt.SortField("branch_id")),
    color=alt.Color("mức:N", title=None, scale=alt.Scale(domain=["Cảnh báo", "Theo dõi", "Bình thường"],
                                             range=[ui.RED, "#E8A33D", "#EEF0F3"])),
    tooltip=["chi_nhánh", alt.Tooltip("week_start:T", format="%d/%m/%Y"), "mức", "nghi_vấn",
             alt.Tooltip("score:Q", format=".1f", title="điểm")]),
    width="stretch")

# ---------------------------------------------------------------- danh sach canh bao
L = A[A.level.isin(levels)]
if branch is not None:
    L = L[L.branch_id == branch]
L = L.merge(losses(score_alert), on=["branch_id", "week_start"], how="left")
L = L.sort_values(["level", "est_loss" if order == "Ước tính thiệt hại" else "score"],
                  ascending=[True, False]).reset_index(drop=True)
st.subheader(f"{(L.level == 'Cảnh báo').sum()} cảnh báo, {(L.level == 'Theo dõi').sum()} mục cần theo dõi")
view = pd.DataFrame({
    "Tuần": L.week_start.map(week_label), "Chi nhánh": "CN" + L.branch_id.astype(str) + " · " + L.branch_name,
    "Mức": L.level, "Nghi vấn": L.cause + " · " + L.cause_name, "Điểm": L.score.round(1),
    "Ước tính thiệt hại": L.est_loss.map(money_short), "Phụ trách": L.owner.fillna(""),
    "Doanh thu so kỳ vọng": L.gap_vs_expected.map(fmt_vnd),
    "Nghi vấn thứ hai": L.cause_2.fillna("") + " " + L.score_2.round(1).astype(str),
    "Số chỉ số vượt ngưỡng": L.n_breaches, "Bằng chứng chính": L.evidence.map(pretty),
})
ev = st.dataframe(view, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", key="alert_pick",
                  column_config={"Điểm": st.column_config.NumberColumn(format="%.1f")})
picked = ev.selection.rows if ev and ev.selection else []
if picked:
    r = L.iloc[picked[0]]
    if st.button(f"Truy vết CN{r.branch_id}, tuần {week_label(r.week_start)}", type="primary"):
        st.session_state.trace_branch = int(r.branch_id)
        st.session_state.trace_week = pd.Timestamp(r.week_start)
        st.switch_page("views/trace.py")
else:
    st.caption("Chọn một dòng để truy vết và xem đề xuất xử lý.")
with st.expander("Cách ước tính thiệt hại"):
    ui.table(pd.DataFrame({"Nguyên nhân": ["P1a hoa hồng sàn sai hợp đồng", "P1b đơn sàn không vào POS",
                                           "P2, P4 hao hụt, thất thoát kho", "P3 thiếu nhân sự, nguyên nhân chưa xác định",
                                           "P5 gian lận tại quầy"],
                           "Ước tính": ["Hoa hồng thu thừa cộng dồn các tuần lệch", "Giá trị bán chưa vào sổ",
                                        "Hao hụt vượt mức thường của các chi nhánh khác cùng kỳ",
                                        "Doanh thu thấp hơn kỳ vọng",
                                        "Giá trị hóa đơn bị hủy, hoàn, giảm giá của thu ngân bị nghi vấn"]}))

# ---------------------------------------------------------------- bo chi so giam sat
with st.expander("Bộ chỉ số giám sát và ngưỡng"):
    st.dataframe(pd.DataFrame([{
        "Nhóm": g, "Chỉ số": lbl,
        "Bất thường khi": {0: "lệch cả hai chiều", 1: "cao hơn kỳ vọng", -1: "thấp hơn kỳ vọng"}[d],
        "Ngưỡng": f"|z| ≥ {C.Z_ALERT:g}, theo dõi từ {C.Z_WATCH:g}"} for _, lbl, g, d in C.INDICATORS]),
        hide_index=True, width="stretch")
    st.markdown(
        f"- Hoa hồng sàn: luật đối soát, lệch so với hợp đồng quá {C.COMMISSION_TOLERANCE * 100:g} điểm % là sai hợp đồng.\n"
        "- Đơn sàn không vào POS: kiểm định Poisson số đơn sàn báo hoàn thành mà POS không ghi, so với tỷ lệ thiếu "
        "thường ngày của chính chi nhánh.\n"
        f"- Thu ngân: kiểm định từng người có từ {C.MIN_CASHIER_RECEIPTS} hóa đơn một tuần, so với các thu ngân khác "
        "cùng chi nhánh, có hiệu chỉnh vì thử nhiều người cùng lúc.\n"
        "- Kho: hao hụt so với định mức theo kỳ kiểm kê, so với các chi nhánh khác cùng kỳ; tách hàng tươi giá thấp "
        f"và nguyên liệu giá trị cao, giá chuẩn từ {C.HIGH_VALUE_COST:,.0f} đồng một đơn vị.\n"
        f"- Mức nền cần ít nhất {C.MIN_BASELINE_WEEKS} tuần lịch sử, nên các tuần đầu tiên của dữ liệu chưa được đánh giá.")
    br = detect.scan_indicators(G)
    br = weeks_in_period(br, start, end)
    if branch is not None:
        br = br[br.branch_id == branch]
    st.caption(f"Trong khoảng đã chọn có {len(br)} lượt chỉ số vượt ngưỡng.")
    if not br.empty:
        st.dataframe(pd.DataFrame({
            "Tuần": br.week_start.map(week_label), "Chi nhánh": "CN" + br.branch_id.astype(str),
            "Nhóm": br.group, "Chỉ số": br.label, "z": br.z.round(1)}).head(300), hide_index=True, width="stretch")
