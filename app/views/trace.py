"""Truy vet nguyen nhan cho 1 chi nhanh x 1 tuan: doanh thu so voi ky vong -> cay KPI theo kenh ->
tin hieu van hanh theo gia thuyet -> dien bien quanh tuan (do tre) -> diem bang chung cua bo phat hien."""
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import ui
from common import (C, action_context, actions, analysis_page, current_profile, detect, fmt_kpi, fmt_vnd, query,
                    pretty, selection, show_df, show_recommendation, vn, week_label, zflag)

G, scores, alerts = analysis_page()
side_branch, start, end = selection()
kv, wk = G["mart_kpi_vs_peers_weekly"], G["mart_branch_weekly"]
branches = G["dim_branch"].sort_values("branch_id").set_index("branch_id")

ui.header("Truy vết nguyên nhân")

# ---------------------------------------------------------------- chon chi nhanh, tuan
weeks = [w for w in detect.usable_weeks(G) if w + pd.Timedelta(days=6) >= start and w <= end]
if not weeks:
    st.caption(f"Khoảng thời gian đã chọn không có tuần nào đủ lịch sử để đánh giá. Cần ít nhất {C.MIN_BASELINE_WEEKS} "
               "tuần dữ liệu trước đó.")
    st.stop()
recent = alerts[(alerts.level == "Cảnh báo") & alerts.week_start.isin(weeks)]
if side_branch is not None:
    recent = recent[recent.branch_id == side_branch]
recent = recent.sort_values(["week_start", "score"], ascending=False)
if "trace_week" not in st.session_state and not recent.empty:
    # mac dinh mo canh bao gan nhat do bo phat hien tim ra trong khoang da chon (khong phai kich ban dung san)
    st.session_state.trace_branch = int(recent.branch_id.iloc[0])
    st.session_state.trace_week = pd.Timestamp(recent.week_start.iloc[0])
if side_branch is not None:
    b = side_branch
    st.session_state.trace_branch = b
else:
    ids = branches.index.tolist()
    b0 = st.session_state.get("trace_branch", ids[0])
    b = st.selectbox("Chi nhánh", ids, index=ids.index(b0) if b0 in ids else 0,
                     format_func=lambda x: f"CN{x} · {branches.branch_name[x]} · hạng {branches.store_class[x]}")
    st.session_state.trace_branch = b
w0 = st.session_state.get("trace_week")
week = st.selectbox("Tuần", weeks, index=weeks.index(w0) if w0 in weeks else len(weeks) - 1, format_func=week_label)
st.session_state.trace_week = week
week = pd.Timestamp(week)


def signed(x, d=1):
    return ("+" if x >= 0 else "") + vn(x, d)

week_end = week + pd.Timedelta(days=6)
tier = branches.store_class[b]
peers = [i for i in branches.index if branches.store_class[i] == tier and i != b]
st.caption(f"Nhóm so sánh hạng {tier}: " + ", ".join(f"CN{p}" for p in peers) + ". Mặc định mở cảnh báo gần nhất "
           "trong khoảng thời gian đã chọn.")

cur = kv[(kv.branch_id == b) & (kv.week_start == week)].set_index("kpi")
wrow = wk[(wk.branch_id == b) & (wk.week_start == week)]
if cur.empty or wrow.empty:
    st.caption("Không có dữ liệu cho chi nhánh và tuần này.")
    st.stop()
wrow = wrow.iloc[0]
sc = scores[(scores.branch_id == b) & (scores.week_start == week)].sort_values("score", ascending=False)

# ---------------------------------------------------------------- 1. ket luan nhanh
top = sc[sc.cause != "BT"].iloc[0]
level = alerts[(alerts.branch_id == b) & (alerts.week_start == week)].level
level = level.iloc[0] if len(level) else "Bình thường"
if top.score >= C.SCORE_ALERT:
    ui.note(f"{level} · {top.cause} {top.cause_name}", f"Điểm bằng chứng {vn(top.score, 1)}. {pretty(top.evidence)}", level)
elif level != "Bình thường":
    ui.note(f"{level} · Chưa xác định nguyên nhân", f"Doanh thu lệch kỳ vọng nhưng chưa giả thuyết nào đủ bằng chứng. "
            f"Nghi vấn cao nhất: {top.cause} {top.cause_name}, điểm {vn(top.score, 1)}.", level)
else:
    ui.note("Bình thường", "Không giả thuyết sự cố nào đủ bằng chứng trong tuần này.", level)

# ---------------------------------------------------------------- de xuat xu ly
# nguyen nhan du bang chung -> viec cu the cho nguyen nhan do; chi lech doanh thu -> viec kiem tra chung
ctx = action_context()
cause = top.cause if top.score >= C.SCORE_ALERT else ("?" if level != "Bình thường" else None)
if cause is not None:
    show_recommendation(actions.recommend(G, ctx, b, week, cause))
    runner_up = sc[(sc.cause != "BT") & (sc.cause != top.cause)].head(1)
    if cause != "?" and len(runner_up) and runner_up.score.iloc[0] >= C.SCORE_ALERT:
        r2 = runner_up.iloc[0]
        with st.expander(f"Nghi vấn thứ hai cũng đủ bằng chứng: {r2.cause} · {r2.cause_name}, điểm {vn(r2.score, 1)}"):
            show_recommendation(actions.recommend(G, ctx, b, week, r2.cause), heading=False)

# ---------------------------------------------------------------- 2. doanh thu so voi ky vong
st.header(f"CN{b} · {branches.branch_name[b]} · tuần {week_label(week)}")
ns = cur.loc["net_sales"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Doanh thu thuần thực tế", fmt_vnd(ns.value), border=True)
c2.metric("Mức kỳ vọng", fmt_vnd(ns.expected_value), border=True)
c3.metric("Chênh lệch", fmt_vnd(ns.gap_vs_expected), delta=f"{vn((np.exp(ns.dev) - 1) * 100, 1)}%", border=True)
c4.metric("Độ lệch chuẩn hóa z", signed(ns.z), border=True,
          help="Chênh lệch so với kỳ vọng chia cho độ dao động tự nhiên 8 tuần trước. Từ 3 trở lên là bất thường.")
hist = kv[(kv.branch_id == b) & (kv.kpi == "net_sales") & (kv.baseline_n >= C.MIN_BASELINE_WEEKS)]
hist = hist[["week_start", "value", "expected_value"]].melt("week_start", var_name="loại", value_name="VND")
hist["triệu"] = hist.VND / 1e6
hist["loại"] = hist["loại"].map({"value": "Thực tế", "expected_value": "Kỳ vọng"})
line = alt.Chart(hist).mark_line(point=True).encode(
    x=alt.X("week_start:T", title=None, axis=alt.Axis(format="%d/%m")),
    y=alt.Y("triệu:Q", scale=alt.Scale(zero=False), title="Doanh thu thuần mỗi tuần, triệu đồng"),
    color=alt.Color("loại:N", title=None, scale=alt.Scale(domain=["Thực tế", "Kỳ vọng"], range=["#1F3A5F", "#9CA3AF"])),
    tooltip=[alt.Tooltip("week_start:T", format="%d/%m/%Y"), "loại", alt.Tooltip("VND:Q", format=",.0f")])
band = alt.Chart(pd.DataFrame({"s": [week], "e": [week_end]})).mark_rect(opacity=0.08, color=ui.RED) \
    .encode(x="s:T", x2="e:T")
st.altair_chart(band + line, width="stretch")
st.caption("Kỳ vọng bằng trung vị các chi nhánh cùng hạng trong tuần đó nhân với độ chênh thường ngày của chi nhánh so "
           "với nhóm, lấy trung vị 8 tuần trước. Biến động chung của cả nhóm như lễ, mưa, mùa vụ đã được trừ ra.")

# ---------------------------------------------------------------- 3. cay KPI
st.subheader("Cây KPI: chênh lệch nằm ở kênh nào, do số đơn hay giá trị đơn")
rows = []
for ch, name in C.CHANNELS:
    s, o, a = (cur.loc[k] if k in cur.index else None for k in (f"net_sales_{ch}", f"orders_{ch}", f"aov_{ch}"))
    if s is None:
        continue
    rows.append({"Kênh": name, "Doanh thu thực tế": s.value, "Kỳ vọng": s.expected_value, "Chênh lệch": s.gap_vs_expected,
                 "Doanh thu so kỳ vọng": np.exp(s.dev) - 1 if pd.notna(s.dev) else np.nan,
                 "Số đơn so kỳ vọng": np.exp(o.dev) - 1 if o is not None and pd.notna(o.dev) else np.nan,
                 "AOV so kỳ vọng": np.exp(a.dev) - 1 if a is not None and pd.notna(a.dev) else np.nan, "z": s.z})
tree = pd.DataFrame(rows)
show = tree.copy()
for c in ("Doanh thu thực tế", "Kỳ vọng", "Chênh lệch"):
    show[c] = show[c].map(fmt_vnd)
for c in ("Doanh thu so kỳ vọng", "Số đơn so kỳ vọng", "AOV so kỳ vọng"):
    show[c] = show[c].map(lambda v: "—" if pd.isna(v) else signed(v * 100) + "%")
show["z"] = tree.z.map(lambda z: signed(z) if pd.notna(z) else "—")
show["Đánh giá"] = tree.z.map(zflag)
st.dataframe(show, hide_index=True, width="stretch")
st.altair_chart(alt.Chart(tree.assign(trieu=tree["Chênh lệch"] / 1e6)).mark_bar().encode(
    y=alt.Y("Kênh:N", sort=None, title=None), x=alt.X("trieu:Q", title="Chênh lệch so với kỳ vọng, triệu đồng"),
    color=alt.condition("datum.trieu < 0", alt.value(ui.RED), alt.value("#4F7F5F")),
    tooltip=["Kênh", alt.Tooltip("Chênh lệch:Q", format=",.0f")]).properties(height=170), width="stretch")
st.caption("Doanh thu kênh = số đơn × AOV. Kênh sàn ở đây là phần cửa hàng ghi trên POS.")

# ---------------------------------------------------------------- 4. tin hieu theo gia thuyet
st.subheader("Tín hiệu vận hành cùng tuần, theo từng giả thuyết")


def kpi_table(kpis):
    out = []
    for k in kpis:
        if k not in cur.index:
            continue
        r = cur.loc[k]
        out.append({"Chỉ số": C.KPI_LABEL.get(k, k), "Thực tế": fmt_kpi(k, r.value),
                    "Kỳ vọng": fmt_kpi(k, r.expected_value), "Nhóm cùng hạng": fmt_kpi(k, r.peer_median),
                    "z": signed(r.z) if pd.notna(r.z) and abs(r.z) < 1e3 else "—",
                    "Đánh giá": zflag(r.z) if pd.notna(r.z) and abs(r.z) < 1e3 else ""})
    st.dataframe(pd.DataFrame(out), hide_index=True, width="stretch")


tabs = st.tabs(["P3 Nhân sự và bếp", "P1a Hoa hồng sàn", "P1b Đơn sàn vào POS", "P5 Thu ngân", "P2 và P4 Kho",
                "Yếu tố bình thường"])
with tabs[0]:
    kpi_table(["kitchen_evening", "shifts_evening", "shifts_morning", "orders_per_evening_shift", "app_avg_prep_min",
               "grabfood_avg_prep_min", "shopeefood_avg_prep_min", "app_store_cancel_rate", "app_wait_cancel_rate",
               "app_avg_rating", "grabfood_rating", "shopeefood_rating", "labor_pct"])
    st.caption("Chuỗi nhân quả: thiếu ca bếp làm đơn chuẩn bị lâu, cửa hàng tự hủy và khách hủy vì chờ, điểm đánh giá "
               "giảm, rồi vài tuần sau sàn giảm thứ hạng hiển thị và số đơn sàn giảm.")
with tabs[1]:
    rows = []
    for p, name in (("grabfood", "GrabFood"), ("shopeefood", "ShopeeFood")):
        gap = wrow.get(f"{p}_commission_gap")
        rows.append({"Sàn": name, "Hợp đồng": fmt_kpi("cogs_pct", wrow.get(f"{p}_contract_rate")),
                     "Hiệu dụng trên báo cáo": fmt_kpi("cogs_pct", wrow.get(f"{p}_effective_rate")),
                     "Lệch": "—" if pd.isna(gap) else f"{gap * 100:+.2f} điểm %",
                     "Thu thừa trong tuần": fmt_vnd(wrow.get(f"{p}_commission_overcharge")),
                     "Đánh giá": "—" if pd.isna(gap) else ("Sai hợp đồng" if gap > C.COMMISSION_TOLERANCE
                                                           else "Đúng hợp đồng")})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption("Bài toán tuân thủ hợp đồng nên dùng luật đối soát, không dùng thống kê. Hoa hồng thu thừa làm giảm "
               "tiền sàn chuyển về, không làm giảm doanh thu bán hàng.")
with tabs[2]:
    st.dataframe(pd.DataFrame([
        {"Sàn": n, "Sàn báo hoàn thành": wrow.get(f"{p}_settled_orders"), "Cửa hàng ghi trên POS": wrow.get(f"orders_{p}"),
         "Độ phủ": fmt_kpi("grabfood_pos_coverage", wrow.get(f"{p}_pos_coverage"))}
        for p, n in (("grabfood", "GrabFood"), ("shopeefood", "ShopeeFood"))]), hide_index=True, width="stretch")
    st.caption("Độ phủ thấp thì doanh thu trên POS giảm dù khách vẫn đặt: có đơn đã bán mà không vào sổ, "
               "không phải mất khách.")
with tabs[3]:
    kpi_table(["void_rate", "refund_rate", "discount_rate", "aov_walkin", "orders_walkin"])
    cw = G["mart_cashier_weekly"]
    cw = cw[(cw.branch_id == b) & (cw.week_start == week) & (cw.receipts >= C.MIN_CASHIER_RECEIPTS)].copy()
    if not cw.empty:
        cw = cw.assign(excess=cw.void_rate - cw.others_void_rate).sort_values("excess", ascending=False)
        st.dataframe(pd.DataFrame({
            "Thu ngân": cw.staff_code, "Hóa đơn": cw.receipts, "Hủy": cw.voids, "Hủy trong 10 phút": cw.quick_voids,
            "Tỷ lệ hủy": cw.void_rate.map("{:.1%}".format), "Thu ngân khác": cw.others_void_rate.map("{:.1%}".format),
            "Hoàn tiền": cw.refunds, "Có giảm giá": cw.discounted, "Giá trị bị hủy": cw.void_amount.map(fmt_vnd),
        }), hide_index=True, width="stretch")
    st.caption("Gian lận kiểu thu tiền rồi hủy hóa đơn tập trung ở một người: so từng thu ngân với các thu ngân khác "
               "cùng chi nhánh, cùng tuần.")
with tabs[4]:
    inv = detect.inventory_z(G)
    inv = inv[(inv.branch_id == b) & (inv.period_start_excl < week_end) & (inv.period_end >= week_end)]
    if inv.empty:
        st.caption("Không có kỳ kiểm kê bao phủ tuần này.")
    else:
        pend = inv.period_end.iloc[0]
        label = {"fresh_low": "Hàng tươi giá thấp", "high_value": "Giá trị cao", "dry": "Hàng khô, đóng gói"}
        st.caption(f"Kỳ kiểm kê kết thúc ngày {pend:%d/%m/%Y}. Tiêu hao thực tế bằng tồn đầu cộng nhập trừ tồn cuối; "
                   "định mức bằng số món đã làm nhân công thức.")
        st.dataframe(pd.DataFrame({
            "Nhóm nguyên liệu": inv.group.map(label), "Hao hụt vượt định mức": inv.var_value.map(fmt_vnd),
            "Tỷ lệ so lượng bán thường ngày": inv.var_pct.map("{:+.1%}".format),
            "Trung vị các chi nhánh cùng kỳ": inv.peer_median.map("{:+.1%}".format),
            "z": inv.z.map(signed), "Đánh giá": inv.z.map(zflag)}), hide_index=True, width="stretch")
        a = G["mart_ingredient_avt"]
        top_i = a[(a.branch_id == b) & (a.period_end == pend)].sort_values("variance_value", ascending=False).head(8)
        st.dataframe(pd.DataFrame({
            "Nguyên liệu": top_i.ingredient_name, "Đơn vị": top_i.unit, "Định mức": top_i.theory_qty.round(1),
            "Thực tế": top_i.actual_qty.round(1), "Vượt": top_i.variance_pct.map("{:+.1%}".format),
            "Giá trị vượt": top_i.variance_value.map(fmt_vnd)}), hide_index=True, width="stretch")
        st.caption("Cả hàng tươi giá thấp lẫn thịt cùng vượt thì nghiêng về hao hụt, hư hỏng (P2). Chỉ nhóm giá trị cao "
                   "vượt còn hàng tươi giá thấp bình thường thì nghiêng về thất thoát (P4). Kiểm kê 2 tuần một lần.")
with tabs[5]:
    dd = G["dim_date"]
    dw = dd[dd.week_start == week]
    peer_ns = kv[(kv.branch_id == b) & (kv.kpi == "net_sales")].set_index("week_start").peer_median.sort_index()
    prev = peer_ns[peer_ns.index < week].tail(8)
    peer_chg = peer_ns.get(week, np.nan) / prev.median() - 1 if len(prev) else np.nan
    mi = G["dim_menu_item"]
    price = mi[(mi.valid_from >= week - pd.Timedelta(days=14)) & (mi.valid_from <= week_end)]
    st.dataframe(pd.DataFrame([
        {"Yếu tố": "Ngày lễ trong tuần", "Giá trị": ", ".join(dw.holiday_name.dropna().unique()) or "không"},
        {"Yếu tố": "Số ngày mưa", "Giá trị": f"{int(dw.is_rain.sum())}/7, lượng mưa {dw.precipitation_mm.sum():.0f} mm"},
        {"Yếu tố": f"Doanh thu nhóm cùng hạng {tier} so với 8 tuần trước",
         "Giá trị": "—" if pd.isna(peer_chg) else f"{peer_chg * 100:+.1f}%"},
        {"Yếu tố": "Đổi giá menu trong hoặc ngay trước tuần", "Giá trị": f"{len(price)} món" if len(price) else "không"},
    ]), hide_index=True, width="stretch")
    st.caption("Các yếu tố này tác động lên cả nhóm nên đã được trừ ra khi so với chi nhánh cùng hạng.")

# ---------------------------------------------------------------- 5. dien bien quanh tuan
st.subheader("Diễn biến tín hiệu quanh tuần được chọn")
sig = ["net_sales", "orders_walkin", "orders_app", "orders_grabfood", "orders_shopeefood", "kitchen_evening",
       "app_avg_prep_min", "app_store_cancel_rate", "grabfood_rating", "shopeefood_rating",
       "grabfood_pos_coverage", "shopeefood_pos_coverage", "void_rate", "refund_rate"]
tl = kv[(kv.branch_id == b) & kv.kpi.isin(sig) & (kv.baseline_n >= C.MIN_BASELINE_WEEKS)
        & (kv.week_start >= week - pd.Timedelta(weeks=4)) & (kv.week_start <= week + pd.Timedelta(weeks=4))].copy()
tl["Chỉ số"] = tl.kpi.map(C.KPI_LABEL)
tl["z_clip"] = tl.z.clip(-6, 6)
order = [C.KPI_LABEL[k] for k in sig]
heat = alt.Chart(tl).mark_rect().encode(
    x=alt.X("yearmonthdate(week_start):O", title=None, axis=alt.Axis(format="%d/%m", labelAngle=0)),
    y=alt.Y("Chỉ số:N", sort=order, title=None, axis=alt.Axis(labelLimit=320)),
    color=alt.Color("z_clip:Q", title="z", scale=alt.Scale(scheme="redblue", domain=[-6, 6])),
    tooltip=["Chỉ số", alt.Tooltip("week_start:T", format="%d/%m/%Y"), alt.Tooltip("z:Q", format="+.1f")])
txt = alt.Chart(tl).mark_text(fontSize=10).encode(
    x=alt.X("yearmonthdate(week_start):O"), y=alt.Y("Chỉ số:N", sort=order), text=alt.Text("z_clip:Q", format=".0f"),
    color=alt.condition("abs(datum.z_clip) >= 3", alt.value("white"), alt.value("black")))
st.altair_chart(heat + txt, width="stretch")
st.caption("Mỗi ô là z của chỉ số trong tuần đó: đỏ thấp hơn kỳ vọng, xanh cao hơn. Nguyên nhân thường đi trước hậu quả, "
           "ví dụ thiếu bếp tuần t thì điểm đánh giá và đơn sàn giảm ở các tuần t+1 đến t+3.")

# ---------------------------------------------------------------- 6. diem bang chung
st.subheader("Điểm bằng chứng của từng giả thuyết")
cS, cT = st.columns([2, 3])
with cS:
    st.altair_chart(alt.Chart(sc).mark_bar().encode(
        y=alt.Y("cause:N", sort="-x", title=None), x=alt.X("score:Q", scale=alt.Scale(domain=[0, 6]), title="Điểm"),
        color=alt.condition(f"datum.score >= {C.SCORE_ALERT}", alt.value(ui.RED), alt.value("#9CA3AF")),
        tooltip=["cause_name", alt.Tooltip("score:Q", format=".1f")]), width="stretch")
with cT:
    st.dataframe(pd.DataFrame({"Mã": sc.cause, "Giả thuyết": sc.cause_name, "Điểm": sc.score.round(1),
                               "Bằng chứng chính": sc.evidence.map(pretty)}), hide_index=True, width="stretch")
st.caption(f"Điểm là mức vượt của các chỉ số đặc trưng theo đúng chiều của từng giả thuyết, tối đa 6; từ "
           f"{C.SCORE_ALERT:g} trở lên thì phát cảnh báo. Kết luận cuối cùng vẫn cần quản lý xác minh.")

# ---------------------------------------------------------------- 7. bang chung goc
st.subheader("Bằng chứng gốc trong tệp nguồn")
ev = cause if cause and cause != "?" else (top.cause if top.score >= C.Z_WATCH else None)
profile = current_profile()
d0, d1 = f"{week:%Y-%m-%d}", f"{week_end:%Y-%m-%d}"
evidence = None
if ev == "P5":
    cz = ctx["cash"]
    row = cz[(cz.branch_id == b) & (cz.week_start == week)]
    code = row.staff_code.iloc[0] if len(row) and isinstance(row.staff_code.iloc[0], str) else None
    if code:
        sid = int(code[2:])
        evidence = query(profile, f"""
            select receipt_no as "Số hóa đơn", strftime(txn_at, '%d/%m %H:%M') as "Thời điểm", total_paid as "Tổng tiền",
                   case when is_void then 'hủy' when is_refund then 'hoàn tiền' else 'giảm giá' end as "Loại",
                   coalesce(void_reason, discount_code, '') as "Lý do, mã giảm",
                   coalesce(cast(round(minutes_to_void, 1) as varchar), '') as "Phút từ lúc thu tới lúc hủy",
                   payment_method as "Thanh toán",
                   _source_file as "Tệp gốc", _row_number as "Dòng"
            from silver.stg_pos__receipts
            where branch_id = {b} and business_date between '{d0}' and '{d1}'
              and (cashier_staff_id = {sid} or void_by_staff_id = {sid} or refund_by_staff_id = {sid})
              and (is_void or is_refund or discount_amount > 0)
            order by txn_at""")
        st.caption(f"Các hóa đơn bị hủy, hoàn tiền hoặc giảm giá do thu ngân {code} thực hiện trong tuần. Mẫu điển hình "
                   "của gian lận: hóa đơn tiền mặt bị hủy vài phút sau khi thu tiền. Thống kê chỉ là nghi vấn, cần đối "
                   "chiếu camera và két tiền trước khi kết luận.")
elif ev in ("P1a", "P1b"):
    evidence = query(profile, f"""
        select s.platform as "Sàn", s.gross_sales as "Doanh thu món", s.orders_completed as "Đơn sàn báo hoàn thành",
               s.commission as "Hoa hồng sàn thu", round(100.0 * s.commission / nullif(s.gross_sales, 0), 2) as "Tỷ lệ hiệu dụng, %",
               round(100.0 * f.contract_commission_rate, 2) as "Tỷ lệ hợp đồng, %", s._source_file as "Tệp gốc",
               s._row_number as "Dòng"
        from silver.stg_marketplace__settlement s
        join gold.fact_marketplace_settlement f using (settlement_key)
        where s.branch_id = {b} and s.week_start = '{d0}'""")
    pos = query(profile, f"""
        select strftime(business_date, '%d/%m') as ngay, channel, count(*) n from silver.stg_pos__receipts
        where branch_id = {b} and business_date between '{d0}' and '{d1}' and channel in ('GRABFOOD', 'SHOPEEFOOD')
        group by all order by 1""")
    if ev == "P1b" and pos is not None and len(pos):
        st.caption("Đơn sàn bị bỏ sót thì không có bản ghi nào trên POS để chỉ ra; bằng chứng là số tổng sàn báo trong tệp "
                   "đối soát lớn hơn số đơn sàn mà POS ghi theo từng ngày dưới đây.")
        show_df(pos.pivot(index="ngay", columns="channel", values="n").reset_index().rename(
            columns={"ngay": "Ngày", "GRABFOOD": "Đơn GrabFood trên POS", "SHOPEEFOOD": "Đơn ShopeeFood trên POS"}),
            hide_index=True, width="stretch")
    else:
        st.caption("Dòng báo cáo đối soát của tuần, nguyên văn số liệu sàn gửi; tỷ lệ hoa hồng hiệu dụng tự tính, so với "
                   "hợp đồng có hiệu lực.")
elif ev == "P3":
    k = query(profile, f"""
        with d as (select date_day, isodow(date_day) dow, kitchen_evening, app_store_cancels, app_avg_prep_min
                   from gold.mart_branch_daily where branch_id = {b})
        select strftime(x.date_day, '%d/%m') as "Ngày", x.kitchen_evening as "Ca bếp tối có chấm công",
               (select median(y.kitchen_evening) from d y where y.dow = x.dow
                  and y.date_day between x.date_day - interval 56 day and x.date_day - interval 1 day) as "Thường ngày cùng thứ",
               round(x.app_avg_prep_min, 1) as "Chuẩn bị đơn App, phút", x.app_store_cancels as "Đơn App bị cửa hàng hủy"
        from d x where x.date_day between '{d0}' and '{d1}' order by x.date_day""")
    if k is not None:
        show_df(k, decimals={"Thường ngày cùng thứ": 1, "Chuẩn bị đơn App, phút": 1}, hide_index=True, width="stretch")
    evidence = query(profile, f"""
        select order_id as "Mã đơn App", strftime(created_at_local, '%d/%m %H:%M') as "Giờ đặt",
               cancel_reason as "Lý do hủy", total_amount as "Giá trị", _source_file as "Tệp gốc", _row_number as "Dòng"
        from silver.stg_app__orders
        where branch_id = {b} and business_date between '{d0}' and '{d1}' and is_store_cancelled
        order by created_at_local""")
    st.caption("Ca bếp tối mỗi ngày đếm từ máy chấm công, so với mức thường cùng thứ trong 8 tuần trước, và từng đơn App "
               "bị cửa hàng tự hủy trong tuần.")
elif ev in ("P2", "P4"):
    a2 = G["mart_ingredient_avt"]
    per = a2[(a2.branch_id == b) & (a2.period_start_excl < week_end) & (a2.period_end >= week_end)]
    if len(per):
        topi = per.sort_values("variance_value", ascending=False).iloc[0]
        i, p0, p1 = int(topi.ingredient_id), pd.Timestamp(topi.period_start_excl), pd.Timestamp(topi.period_end)
        cnt = query(profile, f"""
            select strftime(count_date, '%d/%m/%Y') as "Ngày kiểm kê", counted_qty as "Tồn đếm được", counted_by as "Người đếm",
                   _source_file as "Tệp gốc", _row_number as "Dòng"
            from silver.stg_stock__counts where branch_id = {b} and cast(ingredient_id as integer) = {i}
              and count_date in ('{p0:%Y-%m-%d}', '{p1:%Y-%m-%d}') order by count_date""")
        if cnt is not None:
            show_df(cnt, decimals={"Tồn đếm được": 1}, hide_index=True, width="stretch")
        evidence = query(profile, f"""
            select strftime(receipt_date, '%d/%m') as "Ngày nhập", raw_name as "Tên trên phiếu", quantity as "Số lượng",
                   unit as "Đơn vị", unit_price as "Đơn giá", supplier as "Nhà cung cấp", _source_file as "Tệp gốc",
                   _row_number as "Dòng"
            from silver.stg_inventory__receipt_lines where branch_id = {b} and cast(ingredient_id as integer) = {i}
              and receipt_date > '{p0:%Y-%m-%d}' and receipt_date <= '{p1:%Y-%m-%d}' order by receipt_date""")
        st.caption(f"Nguyên liệu vượt định mức nhiều nhất trong kỳ kiểm kê: {topi.ingredient_name}. Hai phiếu kiểm kê ở "
                   "trên và các phiếu nhập dưới đây là toàn bộ dữ liệu gốc dùng để tính tiêu hao thực tế.")
else:
    st.caption("Tuần này không có giả thuyết nguyên nhân nào đủ bằng chứng, nên không có bản ghi gốc cụ thể để chỉ ra.")
if evidence is not None and len(evidence):
    show_df(evidence, hide_index=True, width="stretch")
    files = evidence["Tệp gốc"].dropna().unique().tolist()
    c1, c2 = st.columns([4, 1.4])
    f = c1.selectbox("Mở tệp gốc", files, label_visibility="collapsed")
    if c2.button("Mở tệp gốc", width="stretch"):
        rowkey = evidence[evidence["Tệp gốc"] == f].iloc[0]
        # chuoi de loc dung dong trong tep goc: khoa nguyen van ma he thong nguon ghi
        if "Số hóa đơn" in rowkey:
            key = rowkey["Số hóa đơn"]
        elif "Mã đơn App" in rowkey:
            key = rowkey["Mã đơn App"]
        elif "Tên trên phiếu" in rowkey:
            key = rowkey["Tên trên phiếu"]
        elif "Sàn" in evidence:
            key = branches.grab_store_name[b] if "grab" in f.lower() else branches.shopee_store_code[b]
        else:
            key = ""
        st.session_state.src_goto = (profile, f, str(key))
        st.switch_page("views/sources.py")
    st.caption("Mỗi bản ghi trong kho giữ tên tệp và số dòng gốc từ tầng Bronze, nên con số trên trang này truy ngược "
               "được tới đúng dòng mà hệ thống nguồn đã xuất.")
