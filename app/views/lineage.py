"""Mo hinh va pha he du lieu: danh muc mo hinh dbt, pha he tu Bronze den Gold, so do hinh sao tu sinh."""
import pandas as pd
import streamlit as st

import dbt_meta
import ui
from common import current_profile

profile = current_profile()
ui.header("Mô hình và phả hệ", "Sinh từ metadata của dbt sau mỗi lần build, nên luôn khớp với mã đang chạy.")
m = dbt_meta.manifest(profile)
if m is None:
    st.error("Chưa có metadata dbt cho tập này. Chạy: `python -m pipeline.run_dbt --profile <tập> build`")
    st.stop()
t = dbt_meta.nodes_table(m)

c = st.columns(4)
for col, layer in zip(c, dbt_meta.LAYER_ORDER):
    col.metric(layer, f"{(t.Tầng == layer).sum()} bảng")

tab_lineage, tab_star, tab_catalog = st.tabs(["Phả hệ dữ liệu", "Lược đồ hình sao", "Danh mục mô hình"])

with tab_lineage:
    names = t.sort_values(["Tầng", "Tên"]).set_index("uid")
    order = [u for layer in dbt_meta.LAYER_ORDER for u in names[names.Tầng == layer].index]
    default = "model.fastfat.fact_order" if "model.fastfat.fact_order" in order else None
    focus = st.selectbox("Xem phả hệ của một bảng", [None] + order, index=order.index(default) + 1 if default else 0,
                         format_func=lambda u: "Toàn bộ" if u is None else f"{names.Tầng[u]} · {names.Tên[u]}")
    st.graphviz_chart(dbt_meta.lineage_dot(m, focus), width="stretch")
    if focus:
        n = names.loc[focus]
        st.caption(f"Phả hệ của {n.Tên}. Mũi tên đi từ bảng nguồn tới bảng dùng nó.")

with tab_star:
    dot, rel = dbt_meta.star_dot(m)
    st.graphviz_chart(dot, width="stretch")
    st.caption("Sinh từ các kiểm thử quan hệ của dbt: mỗi đường nối là một khóa ngoại đã được kiểm tra trên dữ liệu.")
    st.dataframe(pd.DataFrame(rel, columns=["Bảng sự kiện", "Bảng được tham chiếu", "Khóa"]),
                 hide_index=True, width="stretch")
    grain = {
        "fact_order": "1 đơn hàng (POS + App)", "fact_order_line": "1 dòng món trên đơn",
        "fact_labor_shift": "1 nhân viên × 1 ngày × 1 ca", "fact_marketplace_settlement": "1 sàn × 1 chi nhánh × 1 tuần",
        "fact_inventory_receipt": "1 dòng phiếu nhập kho", "fact_stock_count": "1 chi nhánh × 1 nguyên liệu × 1 lần kiểm kê",
    }
    st.markdown("**Hạt dữ liệu của các bảng sự kiện**")
    st.dataframe(pd.DataFrame(list(grain.items()), columns=["Bảng sự kiện", "Một dòng là"]), hide_index=True,
                 width="stretch")
    st.markdown("**Chiều thay đổi chậm loại 2:** `dim_menu_item` lưu lịch sử giá và giá vốn, `dim_employee` lưu lịch sử "
                "vai trò và lương; bảng sự kiện gắn đúng phiên bản có hiệu lực tại ngày phát sinh.")

with tab_catalog:
    layer = st.multiselect("Tầng", dbt_meta.LAYER_ORDER, default=dbt_meta.LAYER_ORDER)
    show = t[t.Tầng.isin(layer)].drop(columns=["uid", "Phụ thuộc"])
    show["Tầng"] = pd.Categorical(show["Tầng"], dbt_meta.LAYER_ORDER, ordered=True)
    st.dataframe(show.sort_values(["Tầng", "Tên"]), hide_index=True, width="stretch")
