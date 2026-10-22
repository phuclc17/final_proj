"""Chat luong du lieu: cua chan dau vao, kiem thu dbt, doi soat - cach ly, do moi cua nguon.
(Dieu phoi Airflow o trang Van hanh hang ngay.)"""
import pandas as pd
import streamlit as st

import dbt_meta
import ui
from common import current_profile, query, show_df

profile = current_profile()
ui.header("Chất lượng dữ liệu", "Đọc từ các bảng kiểm soát của kho và metadata của dbt.")

tab_gate, tab_test, tab_rec, tab_fresh = st.tabs(
    ["Kiểm tra đầu vào", "Kiểm thử dữ liệu", "Đối soát và cách ly", "Độ mới nguồn"])

# ---------------------------------------------------------------- cua chan dau vao
with tab_gate:
    st.caption("Chạy sau khi nạp Bronze, trước dbt. Một mục ở mức chặn làm đường ống dừng lại trước Silver.")
    gate = query(profile, "select * from ops.dq_checks order by checked_at desc")
    if gate is None or gate.empty:
        st.caption("Môi trường này chưa chạy kiểm tra đầu vào.")
    else:
        last = gate[gate.checked_at == gate.checked_at.max()]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lần kiểm tra gần nhất", f"{last.checked_at.iloc[0]:%d/%m %H:%M}", border=True)
        for col, lv in zip((c2, c3, c4), ("đạt", "cảnh báo", "chặn")):
            col.metric(lv.capitalize(), int((last.level == lv).sum()), border=True)
        show_df(pd.DataFrame({
            "Kiểm tra": last["check"], "Nguồn": last.source, "Mức": last.level.str.capitalize(),
            "Giá trị": last.value, "Ngưỡng": last.threshold, "Chi tiết": last.message,
        }), hide_index=True, width="stretch")
        hist = gate.groupby("checked_at")["level"].apply(lambda s: (s != "đạt").sum()).rename("Số mục không đạt")
        with st.expander(f"Lịch sử {len(hist)} lần kiểm tra"):
            st.dataframe(hist.sort_index(ascending=False).reset_index(), hide_index=True, width="stretch")

# ---------------------------------------------------------------- kiem thu dbt
with tab_test:
    m, rr = dbt_meta.manifest(profile), dbt_meta.run_results(profile)
    tests = dbt_meta.test_results(m, rr) if m else pd.DataFrame()
    if tests.empty:
        st.caption("Chưa có kết quả kiểm thử dbt cho môi trường này.")
    else:
        failed = tests[tests["Trạng thái"] != "pass"]
        when = pd.Timestamp(rr["metadata"]["generated_at"]).tz_convert("Asia/Ho_Chi_Minh")
        c1, c2, c3 = st.columns(3)
        c1.metric("Kiểm thử đạt", f"{len(tests) - len(failed)}/{len(tests)}", border=True)
        c2.metric("Lần chạy", f"{when:%d/%m/%Y %H:%M}", border=True)
        c3.metric("Bảng được kiểm thử", tests["Bảng"].nunique(), border=True)
        if not failed.empty:
            ui.note(f"{len(failed)} kiểm thử không đạt", "Xem danh sách đầy đủ ở cuối thẻ.", "Cảnh báo")
        kind = {"not_null": ("Không rỗng", "Dựng sẵn của dbt"), "unique": ("Duy nhất", "Dựng sẵn của dbt"),
                "relationships": ("Toàn vẹn tham chiếu", "Dựng sẵn của dbt"),
                "accepted_values": ("Giá trị hợp lệ", "Dựng sẵn của dbt"),
                "unique_combination": ("Duy nhất theo tổ hợp cột", "Kiểm thử tổng quát viết bằng macro"),
                "singular": ("Luật nghiệp vụ", "Câu SQL trong dbt/tests")}
        tests["Nhóm"] = tests["Loại"].map(lambda k: kind.get(k, (k, ""))[0])
        tests["Cách hiện thực"] = tests["Loại"].map(lambda k: kind.get(k, (k, ""))[1])
        c1, c2 = st.columns(2)
        groups = tests.groupby(["Loại", "Nhóm", "Cách hiện thực"]).size().rename("Số kiểm thử").reset_index()
        groups = groups.sort_values("Loại", key=lambda c: c.map(list(kind).index))
        c1.dataframe(groups.drop(columns="Loại"), hide_index=True, width="stretch")
        c2.dataframe(tests[tests["Loại"] == "singular"][["Kiểm thử", "Trạng thái", "Giây"]], hide_index=True,
                     width="stretch")
        st.caption("Luật nghiệp vụ là các câu SQL trả về dòng vi phạm, đạt khi kết quả rỗng: số dòng Bronze bằng Silver "
                   "cộng cách ly cộng dòng cấu trúc, tạm tính POS bằng tổng dòng món, tiền thực nhận của sàn khớp công "
                   "thức, doanh thu Gold khớp Silver theo chi nhánh và ngày, lịch sử SCD không chồng lấn.")
        with st.expander("Toàn bộ kiểm thử"):
            st.dataframe(tests, hide_index=True, width="stretch")

# ---------------------------------------------------------------- doi soat va cach ly
with tab_rec:
    rec = query(profile, "select * from silver.silver_row_reconciliation order by 1")
    if rec is not None:
        ok = (rec.unexplained_rows == 0).all()
        if ok:
            st.caption("Mọi dòng Bronze đều có mặt ở Silver, ở bảng cách ly, hoặc là dòng cấu trúc như dòng Tổng cộng.")
        else:
            ui.note("Có dòng Bronze chưa được giải thích ở Silver", "Cần kiểm tra các nguồn có cột cuối khác 0.", "Cảnh báo")
        show_df(rec.rename(columns={"source_table": "Nguồn", "bronze_rows": "Dòng Bronze", "silver_rows": "Dòng Silver",
                                         "quarantined_rows": "Dòng cách ly", "structural_rows": "Dòng cấu trúc",
                                         "unexplained_rows": "Không giải thích được", "pct_quarantined": "% cách ly"}),
                     hide_index=True, width="stretch")
    q = query(profile, "select source_table, dq_issue, count(*) as n from silver.silver_quarantine group by all order by 3 desc")
    if q is not None and not q.empty:
        st.subheader("Dòng bị cách ly theo lý do")
        show_df(q.rename(columns={"source_table": "Nguồn", "dq_issue": "Lý do", "n": "Số dòng"}),
                     hide_index=True, width="stretch")
        st.caption("Dòng lỗi không bị xóa hay tự sửa mà được giữ nguyên kèm lý do để người phụ trách nguồn xử lý.")

# ---------------------------------------------------------------- do moi nguon
with tab_fresh:
    fresh = query(profile, """select bronze_table, count(*) as so_tep, sum(row_count) as so_dong,
                                     sum(case when status = 'failed' then 1 else 0 end) as tep_loi,
                                     max(ingested_at) as lan_nap_cuoi
                              from bronze._ingest_log group by 1 order by 1""")
    latest = query(profile, """
        select 'POS' as he_thong, max(business_date) as ngay from silver.stg_pos__receipts
        union all select 'App', max(business_date) from silver.stg_app__orders
        union all select 'Chấm công', max(work_date) from silver.stg_timekeeping__shifts
        union all select 'Nhập kho', max(receipt_date) from silver.stg_inventory__receipt_lines
        union all select 'Kiểm kê', max(count_date) from silver.stg_stock__counts
        union all select 'Đối soát sàn', max(week_end) from silver.stg_marketplace__settlement""")
    if latest is not None:
        cols = st.columns(len(latest))
        for col, r in zip(cols, latest.itertuples()):
            col.metric(r.he_thong, f"{pd.Timestamp(r.ngay):%d/%m/%Y}" if pd.notna(r.ngay) else "—", border=True)
        st.caption("Ngày dữ liệu mới nhất của từng hệ thống. Đối soát sàn theo tuần và kiểm kê hai tuần một lần nên luôn "
                   "chậm hơn các nguồn theo ngày.")
    if fresh is not None:
        show_df(fresh.rename(columns={"bronze_table": "Bảng Bronze", "so_tep": "Số tệp", "so_dong": "Số dòng",
                                           "tep_loi": "Tệp lỗi", "lan_nap_cuoi": "Lần nạp cuối"}),
                     hide_index=True, width="stretch")
