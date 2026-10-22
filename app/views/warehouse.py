"""Kho du lieu: xem bang cua ca ba tang (Bronze nguyen van, Silver da lam sach, Gold mo hinh hoa) va chay SQL chi doc."""
import duckdb
import streamlit as st

import ui
from common import current_profile, db_path, query, show_df
from dataviews import MAX_ROWS, filtered_table
from analytics import safe_sql

profile = current_profile()
path = db_path(profile)
ui.header("Kho dữ liệu", f"Kho DuckDB `{path.relative_to(path.parents[3]).as_posix()}`, mỗi tầng một schema. Mọi truy "
                         "vấn ở đây chỉ đọc.")
if not path.exists():
    st.caption("Chưa có kho dữ liệu cho môi trường này.")
    st.stop()

LAYERS = {
    "Bronze": ("bronze", "Nguyên văn tệp nguồn, mỗi dòng giữ nội dung gốc trong cột payload kèm siêu dữ liệu truy vết: "
                         "tệp nào, dòng thứ mấy, mã băm, lô nạp."),
    "Silver": ("silver", "Đã ép kiểu, chuẩn hóa định dạng và đơn vị, gắn mã chuẩn giữa các hệ thống; dòng lỗi nằm ở "
                         "bảng cách ly kèm lý do. Bảng trung gian nằm ở schema silver_work."),
    "Gold": ("gold", "Lược đồ hình sao: bảng chiều dim_, bảng sự kiện fact_, bảng chỉ số mart_ đã tính sẵn cho phân tích."),
    "Vận hành": ("ops", "Kết quả do pipeline hằng ngày ghi ra: nhật ký các lượt chạy, cảnh báo, điểm bằng chứng."),
}
layer = st.segmented_control("Tầng", list(LAYERS), default="Gold", label_visibility="collapsed") or "Gold"
schema, desc = LAYERS[layer]
st.caption(desc)

tables = query(profile, f"""select table_name as bang, estimated_size as so_dong, column_count as so_cot
                            from duckdb_tables() where schema_name = '{schema}' order by 1""")
if tables is None or tables.empty:
    st.caption(f"Schema {schema} chưa có bảng nào.")
    st.stop()
if layer == "Gold":
    tables.insert(0, "nhóm", tables.bang.str.split("_").str[0].map({"dim": "Chiều", "fact": "Sự kiện", "mart": "Chỉ số"}))

SAMPLES = {
    "Bronze: hai phiên bản phần mềm POS ghi khác nhau": """select json_extract_string(payload, '$.pos_software_version') as phien_ban_pos,
       count(*) as so_hoa_don,
       count(json_extract_string(payload, '$.total_paid'))  as co_cot_total_paid,
       count(json_extract_string(payload, '$.grand_total')) as co_cot_grand_total,
       min(json_extract_string(payload, '$.txn_time'))      as vi_du_thoi_gian
from bronze.pos_receipts group by 1""",
    "Silver: dòng bị cách ly theo lý do": """select source_table, dq_issue, count(*) as so_dong
from silver.silver_quarantine group by all order by 3 desc""",
    "Gold: doanh thu, COGS%, Labor% theo chi nhánh": """select b.branch_id, b.branch_name, b.store_class,
       sum(d.net_sales) as doanh_thu, sum(d.orders) as so_don,
       round(sum(d.net_sales) / sum(d.orders)) as aov,
       round(sum(d.cogs_standard) / sum(d.net_sales), 4) as cogs_pct,
       round(sum(d.labor_cost) / sum(d.net_sales), 4) as labor_pct
from gold.mart_branch_daily d join gold.dim_branch b using (branch_id)
group by all order by 1""",
    "Gold: lịch sử giá món (SCD loại 2)": """select item_id, item_name, price, standard_cost, valid_from, valid_to, is_current
from gold.dim_menu_item where item_id in (1, 25) order by item_id, valid_from""",
    "Gold: đối soát sàn, độ phủ POS và hoa hồng": """select branch_id, week_start, grabfood_settled_orders, orders_grabfood,
       round(grabfood_pos_coverage, 3) as do_phu_grab, round(grabfood_commission_gap, 4) as lech_hoa_hong_grab
from gold.mart_branch_weekly order by grabfood_pos_coverage nulls last limit 20""",
}

tab_table, tab_sql = st.tabs(["Xem bảng", "Truy vấn SQL"])
with tab_table:
    show_df(tables.rename(columns={"nhóm": "Nhóm", "bang": "Bảng", "so_dong": "Số dòng", "so_cot": "Số cột"}),
            width="stretch", hide_index=True, height=min(38 * (len(tables) + 1), 300))
    name = st.selectbox("Bảng", tables.bang.tolist(), key=f"tbl_{schema}")
    try:
        with duckdb.connect(str(path), read_only=True) as con:
            filtered_table(con, schema, name, f"wh_{schema}")
    except duckdb.IOException:
        st.warning("Pipeline đang ghi dữ liệu vào kho. Vui lòng tải lại trang sau ít giây.")
with tab_sql:
    pick = st.selectbox("Câu truy vấn mẫu", list(SAMPLES))
    sql = st.text_area("Câu lệnh SQL, chỉ đọc", SAMPLES[pick], height=200, key=f"sql_{pick}")
    if st.button("Chạy truy vấn", type="primary"):
        try:
            df, cut = safe_sql.run(path, sql, limit=MAX_ROWS)
            st.dataframe(df, width="stretch", hide_index=True)
            if cut:
                st.caption(f"Chỉ hiện {MAX_ROWS} dòng đầu.")
        except Exception as e:  # loi cu phap SQL hoac cau bi chan -> hien thong bao, khong dung trang
            st.error(str(e))
