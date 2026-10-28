"""Tong quan ve bang Streamlit truc tiep tu Gold, dung o ban xem truc tuyen (khong co Metabase).
Cung cac chi so voi dashboard Metabase: doanh thu, so don, AOV, COGS%, Labor%, huy don App, kenh, chi nhanh."""
import altair as alt
import pandas as pd
import streamlit as st

import ui
from common import C, fmt_vnd, in_period, money_short, vn

SUMS = ["net_sales", "orders", "cogs_standard", "labor_cost", "app_orders_placed", "app_store_cancels",
        "app_customer_cancels"]
PCT = {"COGS%", "Labor%", "Hủy đơn App"}


def totals(d):
    s = d[SUMS].sum()
    return {
        "Doanh thu": s.net_sales, "Số đơn": s.orders,
        "AOV": s.net_sales / s.orders if s.orders else None,
        "COGS%": s.cogs_standard / s.net_sales if s.net_sales else None,
        "Labor%": s.labor_cost / s.net_sales if s.net_sales else None,
        "Hủy đơn App": (s.app_store_cancels + s.app_customer_cancels) / s.app_orders_placed
        if s.app_orders_placed else None,
    }


def render(G, alerts, branch, start, end, title):
    names = G["dim_branch"].set_index("branch_id")
    daily = G["mart_branch_daily"]
    if branch is not None:
        daily = daily[daily.branch_id == branch]
    cur = in_period(daily, "date_day", start, end)
    span = end - start + pd.Timedelta(days=1)
    prev = in_period(daily, "date_day", start - span, start - pd.Timedelta(days=1))

    ui.header(f"Tổng quan · {title}", f"{start:%d/%m/%Y} – {end:%d/%m/%Y}, so với {span.days} ngày liền trước. "
                                      "COGS% là giá vốn theo định mức công thức; Labor% chỉ gồm lương giờ trực tiếp "
                                      "theo chấm công.")
    if cur.empty:
        st.caption("Không có dữ liệu trong khoảng thời gian này.")
        st.stop()

    tc, tp = totals(cur), (totals(prev) if not prev.empty else {})
    for col, (k, v) in zip(st.columns(6), tc.items()):
        pv = tp.get(k)
        if k in PCT:
            shown = "—" if v is None else vn(v * 100, 1) + "%"
            delta = f"{vn((v - pv) * 100, 1)} điểm %" if v is not None and pv else None
        else:
            shown = money_short(v) if k != "Số đơn" else vn(v)
            delta = f"{vn((v / pv - 1) * 100, 1)}%" if v is not None and pv else None
        col.metric(k, shown, delta, delta_color="inverse" if k in PCT else "normal", border=True)

    st.subheader("Doanh thu theo kênh và tuần")
    cols = [f"net_sales_{c}" for c, _ in C.CHANNELS]
    days_per_week = cur.groupby("week_start").date_day.nunique()
    full = days_per_week[days_per_week == 7].index
    ch = cur[cur.week_start.isin(full)].groupby("week_start")[cols].sum().reset_index()
    ch = ch.melt("week_start", var_name="kênh", value_name="VND")
    ch["kênh"] = ch["kênh"].map({f"net_sales_{c}": n for c, n in C.CHANNELS})
    ch["triệu đồng"] = ch.VND / 1e6
    st.altair_chart(alt.Chart(ch).mark_bar().encode(
        x=alt.X("week_start:T", title=None, axis=alt.Axis(format="%d/%m")),
        y=alt.Y("triệu đồng:Q", stack=True, title="Doanh thu thuần, triệu đồng"),
        color=alt.Color("kênh:N", sort=[n for _, n in C.CHANNELS], legend=alt.Legend(orient="top", title=None)),
        tooltip=[alt.Tooltip("week_start:T", format="%d/%m/%Y", title="tuần"), "kênh",
                 alt.Tooltip("VND:Q", format=",.0f", title="doanh thu")]).properties(height=300), width="stretch")
    mix = cur[cols].sum()
    st.caption("Cơ cấu kênh trong kỳ: " + " · ".join(f"{n} {vn(mix[f'net_sales_{c}'] / mix.sum() * 100, 1)}%"
                                                    for c, n in C.CHANNELS))

    if branch is None:
        st.subheader("So sánh chi nhánh")
        t = cur.groupby("branch_id").agg(
            net_sales=("net_sales", "sum"), orders=("orders", "sum"), cogs=("cogs_standard", "sum"),
            labor=("labor_cost", "sum"), placed=("app_orders_placed", "sum"),
            cancels=("app_store_cancels", "sum")).reset_index()
        al = alerts[(alerts.level == "Cảnh báo") & (alerts.week_start + pd.Timedelta(days=6) >= start)
                    & (alerts.week_start <= end)].groupby("branch_id").size()
        st.dataframe(pd.DataFrame({
            "Chi nhánh": "CN" + t.branch_id.astype(str) + " · " + t.branch_id.map(names.branch_name),
            "Hạng": t.branch_id.map(names.store_class),
            "Doanh thu thuần": t.net_sales.map(fmt_vnd), "Số đơn": t.orders.map(vn),
            "AOV": (t.net_sales / t.orders).map(fmt_vnd),
            "COGS%": (t.cogs / t.net_sales * 100).map(lambda x: vn(x, 1) + "%"),
            "Labor%": (t.labor / t.net_sales * 100).map(lambda x: vn(x, 1) + "%"),
            "Cửa hàng tự hủy đơn App": (t.cancels / t.placed * 100).map(lambda x: vn(x, 1) + "%"),
            "Số tuần có cảnh báo": t.branch_id.map(al).fillna(0).astype(int),
        }), hide_index=True, width="stretch", height=38 * (len(t) + 1) + 4)
        st.caption("Nên so trong cùng hạng: chi nhánh hạng C có Labor% cao vì vẫn cần đủ người tối thiểu cho mỗi ca.")
    else:
        st.subheader("Nhân sự và vận hành theo tuần")
        w = cur.groupby("week_start").agg(shifts_evening=("shifts_evening", "sum"),
                                          orders_evening=("orders_evening", "sum"),
                                          prep=("app_prep_sum", "sum"), prep_n=("app_prep_n", "sum"),
                                          days=("date_day", "nunique")).reset_index()
        w = w[w.days == 7]
        w["Số đơn tối mỗi ca tối"] = w.orders_evening / w.shifts_evening
        w["Thời gian chuẩn bị đơn App, phút"] = w.prep / w.prep_n
        m = w.melt("week_start", ["Số đơn tối mỗi ca tối", "Thời gian chuẩn bị đơn App, phút"], var_name="chỉ số")
        st.altair_chart(alt.Chart(m).mark_line(point=True).encode(
            x=alt.X("week_start:T", title=None, axis=alt.Axis(format="%d/%m")), y=alt.Y("value:Q", title=None),
            color=alt.Color("chỉ số:N", legend=alt.Legend(orient="top", title=None)),
            tooltip=[alt.Tooltip("week_start:T", format="%d/%m/%Y"), "chỉ số", alt.Tooltip("value:Q", format=".1f")])
            .properties(height=260), width="stretch")
    st.caption("Trên bản chạy đầy đủ, trang này là dashboard Metabase đọc kho phục vụ PostgreSQL với cùng các chỉ số.")
