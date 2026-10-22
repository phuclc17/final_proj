"""
Cong cu xem du lieu cua du an (khong thuoc san pham cuoi):
  - Du lieu nguon: xem file goc cua cac he thong nguon dang bang (JSON/CSV/Excel)
  - Kho du lieu: xem cac bang Bronze / Silver / Gold trong DuckDB, chay SQL
  - Kiem chung bo mo phong: tac dong cua tung kich ban (doc DAP AN - chi dung de kiem chung bo mo phong)
Chay tu thu muc goc du an: streamlit run tools/data_viewer.py --server.port 8503
"""
import json
import os
import re

import altair as alt
import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Xem dữ liệu Fast&Fat", layout="wide")

EXTS = (".csv", ".json", ".parquet", ".xlsx")
MAX_ROWS = 5000
PROFILES = {"Tập phát triển": "calibration", "Tập kiểm tra": "holdout"}


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def stringify_nested(df):
    out = df.copy()
    for c in out.columns:
        if out[c].map(lambda v: isinstance(v, (list, dict))).any():
            out[c] = out[c].map(lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
    return out


@st.cache_data
def load_file(path):
    if path.endswith(".csv"):
        # doc nguyen van dang chuoi de thay dung du lieu tho, khong de pandas tu ep kieu
        return pd.read_csv(path, dtype=str, keep_default_na=False), None, None
    if path.endswith(".parquet"):
        return pd.read_parquet(path), None, None
    if path.endswith(".xlsx"):
        # giu nguyen luoi o nhu nguoi dung thay trong Excel (ca dong tieu de), khong tu doan header
        df = pd.read_excel(path, header=None, dtype=str).fillna("")
        df.columns = [f"cot_{i + 1}" for i in range(df.shape[1])]
        return df, None, None
    raw = json.load(open(path, encoding="utf-8"))
    if isinstance(raw, dict):
        # file xuat qua API thuong boc ban ghi trong 1 "vo" (vd {page, total, data: [...]}) -> bung mang ban ghi
        lists = [k for k, v in raw.items() if isinstance(v, list) and v and isinstance(v[0], dict)]
        if len(lists) == 1:
            meta = {k: v for k, v in raw.items() if k != lists[0]}
            return None, raw[lists[0]], meta
        return None, [raw], None
    return None, raw, None


def profile(df):
    rows = []
    for c in df.columns:
        s = df[c]
        empty = s.isna() | (s.astype(str).str.strip().isin(["", "None", "nan"]))
        non_empty = s[~empty]
        rows.append({
            "Cột": c,
            "Kiểu": str(s.dtype),
            "% rỗng": round(empty.mean() * 100, 1),
            "Số giá trị khác nhau": s.astype(str).nunique(),
            "Ví dụ": str(non_empty.iloc[0])[:80] if len(non_empty) else "",
        })
    return pd.DataFrame(rows)


# ====================================================================== File nguon
def page_files():
    roots = {k: f"data/{v}/source_systems" for k, v in PROFILES.items()}
    roots["Dữ liệu công khai The Bread Basket"] = "data/public_reference"
    roots = {k: v for k, v in roots.items() if os.path.isdir(v)}
    root = roots[st.sidebar.selectbox("Thư mục gốc", list(roots))]

    current, level = root, 0
    while os.path.isdir(current):
        entries = [e for e in os.listdir(current) if not e.startswith((".", "__"))]
        entries = [e for e in entries if e.endswith(EXTS) or os.path.isdir(os.path.join(current, e))]
        if not entries:
            st.warning(f"Không có file dữ liệu trong `{current}`")
            st.stop()
        choice = st.sidebar.selectbox(f"Cấp {level + 1}", sorted(entries, key=natural_key), key=f"lvl_{current}")
        current, level = os.path.join(current, choice), level + 1

    path = current
    st.title(os.path.basename(path))
    st.caption(f"`{path}` · {os.path.getsize(path) / 1024:.1f} KB")
    df, records, meta = load_file(path)
    if meta:
        st.caption("Thông tin lớp vỏ của file: " + ", ".join(f"{k} = {v}" for k, v in meta.items()))
    if records is not None:
        nested_cols = [k for k, v in records[0].items() if isinstance(v, list) and v and isinstance(v[0], dict)]
        views = ["Mỗi dòng một bản ghi"] + [f"Tách danh sách con: {c}" for c in nested_cols]
        view = st.radio("Cách xem JSON", views, horizontal=True)
        if view == views[0]:
            df = pd.json_normalize(records, max_level=1)
        else:
            col = view.split(": ", 1)[1]
            id_col = next(iter(records[0].keys()))
            df = pd.json_normalize(records, record_path=col, meta=[id_col], errors="ignore")
            df = df[[id_col] + [c for c in df.columns if c != id_col]]
    df = stringify_nested(df)

    c1, c2 = st.columns(2)
    c1.metric("Số dòng", f"{len(df):,}")
    c2.metric("Số cột", len(df.columns))
    tab_data, tab_profile = st.tabs(["Dữ liệu", "Hồ sơ cột"])
    with tab_data:
        keyword = st.text_input("Lọc dòng chứa chuỗi")
        shown = df
        if keyword:
            mask = df.astype(str).apply(lambda s: s.str.contains(keyword, case=False, regex=False)).any(axis=1)
            shown = df[mask]
        if len(shown) > MAX_ROWS:
            st.info(f"Chỉ hiển thị {MAX_ROWS:,}/{len(shown):,} dòng đầu")
        st.dataframe(shown.head(MAX_ROWS), width="stretch", hide_index=True)
    with tab_profile:
        st.dataframe(profile(df), width="stretch", hide_index=True)


# ====================================================================== Kho du lieu (Bronze)
DEFAULT_SQL = """-- Hai phien ban phan mem POS ghi du lieu khac nhau: dung cot nao, dinh dang ngay nao
select json_extract_string(payload, '$.pos_software_version') as phien_ban_pos,
       count(*)                                            as so_hoa_don,
       count(json_extract_string(payload, '$.total_paid'))  as co_cot_total_paid,
       count(json_extract_string(payload, '$.grand_total')) as co_cot_grand_total,
       min(json_extract_string(payload, '$.txn_time'))      as vi_du_thoi_gian
from bronze.pos_receipts
group by 1"""


DATE_COLS = ["date_day", "business_date", "work_date", "week_start", "receipt_date", "count_date", "period_end",
             "report_generated_date", "snapshot_date", "weather_date", "holiday_date"]


def filtered_table(con, schema, name, key):
    """Xem 1 bang co loc theo chi nhanh va khoang ngay (neu bang co cac cot do), gioi han theo du lieu thuc co."""
    cols = con.execute("select column_name from information_schema.columns where table_schema = ? and table_name = ?",
                       [schema, name]).df().column_name.tolist()
    where, params = [], []
    c1, c2 = st.columns([1, 2])
    if "branch_id" in cols:
        ids = [r[0] for r in con.sql(f'select distinct branch_id from {schema}."{name}" '
                                     'where branch_id is not null order by 1').fetchall()]
        b = c1.selectbox("Chi nhánh", ["Tất cả"] + ids, key=f"{key}_b",
                         format_func=lambda x: x if x == "Tất cả" else f"CN{x}")
        if b != "Tất cả":
            where.append("branch_id = ?"); params.append(b)
    dcol = next((c for c in DATE_COLS if c in cols), None)
    if dcol:
        lo, hi = con.sql(f'select min(cast({dcol} as date)), max(cast({dcol} as date)) from {schema}."{name}"').fetchone()
        if lo and hi:
            rng = c2.date_input(f"Khoảng thời gian theo cột {dcol}", (lo, hi), min_value=lo, max_value=hi,
                                format="DD/MM/YYYY", key=f"{key}_d_{name}")
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                where.append(f"cast({dcol} as date) between ? and ?"); params += list(rng)
    sql_where = (" where " + " and ".join(where)) if where else ""
    n = con.execute(f'select count(*) from {schema}."{name}"{sql_where}', params).fetchone()[0]
    order = f" order by {dcol}" if dcol else ""
    df = con.execute(f'select * from {schema}."{name}"{sql_where}{order} limit {MAX_ROWS}', params).df()
    st.caption(f"{n:,} dòng thỏa bộ lọc" + (f", hiển thị {MAX_ROWS:,} dòng đầu" if n > MAX_ROWS else ""))
    st.dataframe(df, width="stretch", hide_index=True)


def page_silver(con):
    tables = con.sql("select table_name as bang, estimated_size as so_dong, column_count as so_cot "
                     "from duckdb_tables() where schema_name = 'silver' order by 1").df()
    if tables.empty:
        st.warning("Chưa có tầng Silver. Chạy: `python -m pipeline.run_dbt --profile <tập> build`")
        return
    st.caption("Silver: dữ liệu đã ép kiểu, chuẩn hóa định dạng và đơn vị, gắn mã chuẩn (chi nhánh, món, nguyên liệu, "
               "nhân viên); dòng lỗi được đưa sang bảng cách ly kèm lý do, không bị xóa âm thầm.")
    has = set(tables.bang)
    tab_rec, tab_table = st.tabs(["Đối soát Bronze → Silver và cách ly", "Xem bảng"])
    with tab_rec:
        if "silver_row_reconciliation" in has:
            st.subheader("Đối soát số dòng: cột unexplained_rows phải bằng 0")
            st.dataframe(con.sql("select * from silver.silver_row_reconciliation").df(), width="stretch", hide_index=True)
        if "silver_quarantine" in has:
            st.subheader("Bảng cách ly theo lý do")
            st.dataframe(con.sql("select source_table, dq_issue, count(*) as so_dong from silver.silver_quarantine "
                                 "group by all order by 1, 3 desc").df(), width="stretch", hide_index=True)
            st.subheader("Ví dụ dòng bị cách ly")
            st.dataframe(con.sql("select * from silver.silver_quarantine limit 50").df(), width="stretch", hide_index=True)
    with tab_table:
        name = st.selectbox("Bảng Silver", tables.bang.tolist())
        filtered_table(con, "silver", name, "silver")


GOLD_SQL = """-- Doanh thu, so don, COGS%, Labor% theo chi nhanh (ca ky)
select b.branch_id, b.branch_name, b.store_class,
       sum(d.net_sales) as doanh_thu, sum(d.orders) as so_don,
       round(sum(d.net_sales) / sum(d.orders)) as aov,
       round(sum(d.cogs_standard) / sum(d.net_sales), 4) as cogs_pct,
       round(sum(d.labor_cost) / sum(d.net_sales), 4) as labor_pct
from gold.mart_branch_daily d
join gold.dim_branch b using (branch_id)
group by all order by 1"""


def page_gold(con):
    tables = con.sql("select table_name as bang, estimated_size as so_dong, column_count as so_cot "
                     "from duckdb_tables() where schema_name = 'gold' order by 1").df()
    if tables.empty:
        st.warning("Chưa có tầng Gold. Chạy: `python -m pipeline.run_dbt --profile <tập> build`")
        return
    st.caption("Gold: lược đồ hình sao gồm bảng chiều `dim_*` (món ăn, nhân viên có lịch sử SCD2), bảng sự kiện `fact_*` "
               "gộp nhiều hệ thống nguồn, và bảng phân tích `mart_*` đã tính sẵn KPI cho truy vết.")
    tables["nhóm"] = tables.bang.str.split("_").str[0].map({"dim": "Chiều", "fact": "Sự kiện", "mart": "Phân tích"})
    st.dataframe(tables[["nhóm", "bang", "so_dong", "so_cot"]], width="stretch", hide_index=True)
    tab_table, tab_sql = st.tabs(["Xem bảng", "Truy vấn SQL"])
    with tab_table:
        name = st.selectbox("Bảng Gold", tables.bang.tolist())
        filtered_table(con, "gold", name, "gold")
    with tab_sql:
        sql = st.text_area("Câu lệnh SQL, chỉ đọc", GOLD_SQL, height=220)
        if st.button("Chạy truy vấn", type="primary", key="gold_sql"):
            try:
                st.dataframe(con.sql(sql).df().head(MAX_ROWS), width="stretch", hide_index=True)
            except Exception as e:
                st.error(str(e))


def page_warehouse():
    prof = PROFILES[st.sidebar.selectbox("Tập dữ liệu", list(PROFILES))]
    layer = st.sidebar.radio("Tầng", ["Bronze", "Silver", "Gold"], horizontal=True)
    db = f"data/{prof}/warehouse/fastfat.duckdb"
    st.title(f"Tầng {layer}")
    if not os.path.exists(db):
        st.warning(f"Chưa có kho dữ liệu `{db}`. Chạy: `python -m pipeline.ingest --profile {prof}`")
        st.stop()
    con = duckdb.connect(db, read_only=True)
    if layer in ("Silver", "Gold"):
        try:
            (page_silver if layer == "Silver" else page_gold)(con)
        finally:
            con.close()
        return
    st.caption("Bronze giữ nguyên giá trị gốc của file nguồn, chỉ thêm siêu dữ liệu truy vết "
               "(_source_file, _file_hash, _row_number, _batch_id, _ingested_at). Việc làm sạch thuộc tầng Silver.")
    try:
        tables = con.sql("select table_name as bang, estimated_size as so_dong, column_count as so_cot "
                         "from duckdb_tables() where schema_name = 'bronze' order by 1").df()
        log = con.sql("""select bronze_table as bang_bronze, count(*) as so_tep, sum(row_count) as so_dong,
                                sum(case when status = 'failed' then 1 else 0 end) as tep_loi,
                                count(distinct batch_id) as so_lo_nap, max(ingested_at) as lan_nap_cuoi
                         from bronze._ingest_log group by 1 order by 1""").df()
        data_tables = tables[tables.bang != "_ingest_log"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Bảng Bronze", len(data_tables))
        c2.metric("Tổng số dòng", f"{int(data_tables.so_dong.sum()):,}")
        c3.metric("Tệp đã nạp", f"{int(log.so_tep.sum()):,}")
        c4.metric("Tệp lỗi", int(log.tep_loi.sum()))

        tab_log, tab_table, tab_sql = st.tabs(["Nhật ký nạp", "Xem bảng", "Truy vấn SQL"])
        with tab_log:
            st.dataframe(log, width="stretch", hide_index=True)
        with tab_table:
            name = st.selectbox("Bảng", data_tables.bang.tolist())
            df = con.sql(f'select * from bronze."{name}" limit 1000').df()
            st.caption(f"1.000 dòng đầu / {int(data_tables.set_index('bang').so_dong[name]):,} dòng")
            st.dataframe(df, width="stretch", hide_index=True)
        with tab_sql:
            sql = st.text_area("Câu lệnh SQL, chỉ đọc", DEFAULT_SQL, height=180)
            if st.button("Chạy truy vấn", type="primary"):
                try:
                    st.dataframe(con.sql(sql).df().head(MAX_ROWS), width="stretch", hide_index=True)
                except Exception as e:
                    st.error(str(e))
    finally:
        con.close()


# ====================================================================== Kiem chung bo mo phong
TRUTH_METRICS = {
    "served_value": "Doanh thu thực phục vụ, VND", "orders_served": "Số đơn được phục vụ",
    "orders_demand": "Nhu cầu, số đơn khách muốn đặt", "walkin_balked": "Khách tại quầy bỏ về",
    "store_cancelled": "Đơn bị cửa hàng hủy", "customer_cancelled": "Đơn bị khách hủy",
    "avg_prep_min": "Thời gian chuẩn bị bình quân, phút", "peak_util": "Mức tải bếp giờ cao điểm",
    "kitchen_evening": "Nhân viên bếp ca tối", "kitchen_morning": "Nhân viên bếp ca sáng",
    "mkt_mult_grab": "Hệ số thứ hạng hiển thị trên Grab", "mkt_mult_shopee": "Hệ số thứ hạng hiển thị trên Shopee",
    "waste_excess_value": "Hao hụt vượt mức thường, VND", "theft_value": "Nguyên liệu bị mất, VND",
    "fraud_void_count": "Hóa đơn bị hủy gian lận", "mkt_not_entered": "Đơn sàn không được nhập POS",
}


@st.cache_data
def load_truth(prof):
    gt = f"data/{prof}/ground_truth"
    t = pd.read_csv(f"{gt}/daily_branch_truth.csv", parse_dates=["date"])
    scen = pd.DataFrame(json.load(open(f"{gt}/scenarios.json", encoding="utf-8"))["scenarios"])
    scen["start"], scen["end"] = pd.to_datetime(scen.start), pd.to_datetime(scen.end)
    to_class = {"hot": "A", "medium": "B", "low": "C"}   # cung ky hieu hang voi danh muc chi nhanh
    tiers = {m["internal_branch_id"]: to_class.get(m["tier"], m["tier"])
             for m in json.load(open("simulator/reference/system_names.json", encoding="utf-8"))}
    return t, scen, tiers


def page_validation():
    prof = PROFILES[st.sidebar.selectbox("Tập dữ liệu", list(PROFILES))]
    st.title("Kiểm chứng bộ mô phỏng")
    st.info("Công cụ cho người phát triển: trang này đọc **đáp án** của bộ mô phỏng, tức các sự kiện thật của thế giới "
            "mô phỏng, để kiểm tra dữ liệu nguồn được tạo đúng. Ứng dụng phân tích và đường ống dữ liệu **không** đọc đáp án.")
    t, scen, tiers = load_truth(prof)
    b = st.sidebar.selectbox("Chi nhánh", sorted(t.branch_id.unique()), format_func=lambda x: f"CN{x} · hạng {tiers[x]}")
    lo, hi = t.date.min().date(), t.date.max().date()
    rng = st.sidebar.date_input("Khoảng thời gian", (lo, hi), min_value=lo, max_value=hi, format="DD/MM/YYYY")
    start, end = (pd.Timestamp(rng[0]), pd.Timestamp(rng[1])) if isinstance(rng, (list, tuple)) and len(rng) == 2         else (pd.Timestamp(lo), pd.Timestamp(hi))
    peers = [k for k, v in tiers.items() if v == tiers[b] and k != b]
    sc = scen[(scen.branch_id == b) & (scen.end >= start) & (scen.start <= end)]

    def with_bands(chart):
        if sc.empty:
            return chart
        bands = alt.Chart(sc.assign(end1=sc.end + pd.Timedelta(days=1))).mark_rect(opacity=0.15, color="#d62728")             .encode(x="start:T", x2="end1:T", tooltip=["id", "story"])
        return bands + chart

    t = t[(t.date >= start) & (t.date <= end)].assign(week=lambda d: d.date - pd.to_timedelta(d.date.dt.weekday, unit="D"))
    weekly = t.groupby(["week", "branch_id"]).served_value.sum().unstack()
    ratio = (weekly[b] / weekly[peers].mean(axis=1)).rename("ty_le").reset_index()
    st.subheader(f"Doanh thu thực phục vụ của CN{b} so với trung bình các chi nhánh cùng hạng {tiers[b]}, theo tuần")
    st.altair_chart(with_bands(alt.Chart(ratio).mark_line(point=True).encode(
        x=alt.X("week:T", title=None), y=alt.Y("ty_le:Q", title="Tỷ lệ", scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("week:T", format="%d/%m/%Y"), alt.Tooltip("ty_le:Q", format=".3f")])), width="stretch")

    pick = st.multiselect("Chỉ số theo ngày", list(TRUTH_METRICS), default=["kitchen_evening", "store_cancelled", "avg_prep_min"],
                          format_func=TRUTH_METRICS.get)
    window = t[t.branch_id == b]
    for col in pick:
        st.subheader(f"{TRUTH_METRICS[col]} · CN{b}")
        st.altair_chart(with_bands(alt.Chart(window).mark_bar().encode(
            x=alt.X("date:T", title=None), y=alt.Y(f"{col}:Q", title=None),
            tooltip=[alt.Tooltip("date:T", format="%d/%m/%Y"), alt.Tooltip(f"{col}:Q", format=",.2f")])).properties(height=200),
            width="stretch")
    if sc.empty:
        st.caption("Không có kịch bản sự cố nào của chi nhánh này trong khoảng đã chọn.")
    else:
        st.caption("Vùng đỏ: thời gian có kịch bản sự cố được đưa vào thế giới mô phỏng.")
    with st.expander("Danh sách kịch bản sự cố của tập dữ liệu này"):
        st.dataframe(scen[["id", "pain_point", "branch_id", "start", "end", "story"]]
                     .rename(columns={"id": "Kịch bản", "pain_point": "Vấn đề", "branch_id": "Chi nhánh",
                                      "start": "Từ", "end": "Đến", "story": "Mô tả"}), width="stretch", hide_index=True)


# ====================================================================== dieu huong
st.sidebar.title("Xem dữ liệu Fast&Fat")
PAGES = {"Dữ liệu nguồn": page_files, "Kho dữ liệu": page_warehouse, "Kiểm chứng mô phỏng": page_validation}
PAGES[st.sidebar.radio("Chế độ", list(PAGES))]()
