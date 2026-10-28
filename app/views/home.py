"""Trang chu: luong du lieu tu nguon den nguoi quan ly, moi khoi la so lieu song cua moi truong dang chon."""
import pandas as pd
import streamlit as st

import airflow_client as af
import dbt_meta
import ui
from common import STATIC, C, current_profile, load_current, query, vn

profile = current_profile()
orders = query(profile, "select count(*) as n, min(date_day) as d0, max(date_day) as d1 from gold.fact_order")
period = (f"{pd.Timestamp(orders.d0.iloc[0]):%d/%m/%Y} – {pd.Timestamp(orders.d1.iloc[0]):%d/%m/%Y}"
          if orders is not None and len(orders) else "—")
ui.header("Sơ đồ hệ thống", f"Chuỗi giả định Fast&Fat · 11 chi nhánh · 4 kênh bán · dữ liệu {period} · môi trường "
                            f"{st.session_state.get('profile', '')}")

# ---------------------------------------------------------------- so lieu song cua tung tang
src = query(profile, """select split_part(file_path, '/', 1) as he_thong, count(*) as tep, sum(row_count) as dong
                        from bronze._ingest_log where status in ('loaded', 'reloaded') group by 1""")
silver = query(profile, """select coalesce(sum(estimated_size), 0) as dong, count(*) as bang from duckdb_tables()
                           where schema_name = 'silver' and table_name like 'stg_%'""")
quarantine = query(profile, "select count(*) as n from silver.silver_quarantine")
gold = query(profile, """select count(*) filter (where table_name like 'dim_%') as dim,
                                count(*) filter (where table_name like 'fact_%') as fact,
                                count(*) filter (where table_name like 'mart_%') as mart
                         from duckdb_tables() where schema_name = 'gold'""")
runs = query(profile, "select run_id, max(finished_at) as t, bool_and(status in ('ok', 'warn')) as ok "
                      "from ops.pipeline_runs group by 1 order by 2 desc limit 1")
pub = query("live", "select finished_at from ops.pipeline_runs where step = 'publish' and status = 'ok' "
                    "order by finished_at desc limit 1")
m, rr = dbt_meta.manifest(profile), dbt_meta.run_results(profile)
tests = dbt_meta.test_results(m, rr) if m else pd.DataFrame()
_, _, alerts = load_current()

n_files = int(src.tep.sum()) if src is not None else 0
n_bronze = int(src.dong.sum()) if src is not None else 0
n_silver, n_silver_tables = (int(silver.dong.iloc[0]), int(silver.bang.iloc[0])) if silver is not None else (0, 0)
n_q = int(quarantine.n.iloc[0]) if quarantine is not None else 0
dim, fact, mart = (int(gold.dim.iloc[0]), int(gold.fact.iloc[0]), int(gold.mart.iloc[0])) if gold is not None else (0, 0, 0)
n_pass, n_tests = (int((tests["Trạng thái"] == "pass").sum()), len(tests)) if len(tests) else (0, 0)
n_alert = int((alerts.level == "Cảnh báo").sum())
n_alert_branches = alerts[alerts.level == "Cảnh báo"].branch_id.nunique()
n_days = (pd.Timestamp(orders.d1.iloc[0]) - pd.Timestamp(orders.d0.iloc[0])).days + 1 if orders is not None else 0
status = None if STATIC else af.status(limit=1)
last_run = (f"Lượt gần nhất {pd.Timestamp(runs.t.iloc[0]):%d/%m %H:%M}, {'thành công' if runs.ok.iloc[0] else 'lỗi'}"
            if runs is not None and len(runs) else "Chưa có lượt chạy tự động trên môi trường này")
pub_t = f"{pd.Timestamp(pub.finished_at.iloc[0]):%d/%m %H:%M}" if pub is not None and len(pub) else "—"


def short(x):
    """So lon rut gon: 504,6 nghìn / 1,37 triệu."""
    if x >= 1e6:
        return vn(x / 1e6, 2) + " triệu"
    if x >= 1e4:
        return vn(x / 1e3, 1) + " nghìn"
    return vn(x)


st.subheader("Luồng dữ liệu")
ui.cards([
    ("Nguồn", f"{vn(n_files)} tệp", f"7 hệ thống, {vn(n_days)} ngày kinh doanh; qua API, tệp tự động và tệp tải lên", "01"),
    ("Bronze", f"{short(n_bronze)} dòng", "17 bảng nguyên văn, nạp tăng dần theo mã băm tệp", "02"),
    ("Silver", f"{short(n_silver)} dòng", f"{n_silver_tables} bảng chuẩn hóa, cách ly {vn(n_q)} dòng lỗi kèm lý do", "03"),
    ("Gold", f"{short(int(orders.n.iloc[0])) if orders is not None else '—'} đơn",
     f"{dim} bảng chiều, {fact} bảng sự kiện, {mart} bảng chỉ số", "04"),
], cols=4)
ui.cards([
    ("Bộ phát hiện", f"{n_alert} tuần cảnh báo", f"{n_alert_branches} chi nhánh; {len(C.INDICATORS)} chỉ số giám sát", "05"),
    ("Kho phục vụ", "PostgreSQL", f"Bản sao Gold cho Metabase; lần đưa gần nhất {pub_t}", "06"),
    ("Điều phối", "Airflow" if status or STATIC else "Airflow chưa bật", last_run, "07"),
    ("Kiểm thử dữ liệu", f"{n_pass}/{n_tests} đạt" if n_tests else "—", "Khóa, toàn vẹn tham chiếu, đối soát giữa các tầng",
     "08"),
], cols=4)
