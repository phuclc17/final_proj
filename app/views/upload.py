"""Tai tep len: kenh tiep nhan tep do nguoi gui (ke toan, quan ly cua hang). Nhan dang nguon theo noi dung, kiem tra
hop dong du lieu, dua vao vung tiep nhan cua moi truong van hanh, bao Airflow -> pipeline tu chay; hien ket qua tung tep
tu luc tiep nhan toi khi nap Bronze va lam sach o Silver. Chi ghi vao moi truong van hanh, khong bao gio vao tap danh gia."""
import time
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

import airflow_client as af
import ui
from common import ROOT, db_path, vn
from pipeline import intake
from pipeline.contracts import SOURCES

PROFILE = "live"
SAMPLES = ROOT / "samples" / "tep_mau"
ui.LEVEL.update({"Đã nhận": ui.GREEN, "Thay bản cũ": ui.BLUE, "Trùng, bỏ qua": ui.GRAY, "Từ chối": ui.RED})


def label(status):
    return status[:1].upper() + status[1:]


ui.header("Tải tệp lên", "Kênh cho tệp do người gửi: báo cáo đối soát sàn, sổ nhập kho, phiếu kiểm kê, bản sửa. Hệ thống "
                         "nhận dạng tệp theo nội dung, kiểm tra theo hợp đồng dữ liệu, rồi đường ống tự xử lý.")


def query(sql):
    """Doc kho cua moi truong van hanh; None neu pipeline dang ghi."""
    try:
        with duckdb.connect(str(db_path(PROFILE)), read_only=True) as con:
            return con.sql(sql).df()
    except (duckdb.IOException, duckdb.CatalogException):
        return None


def submit(items):
    """items: [(ten, byte)]. Tiep nhan tung tep, bao Airflow neu co tep moi hoac ban sua."""
    res = [intake.intake(PROFILE, name, data, sender="tải lên") for name, data in items]
    st.session_state.upload_result = res
    if any(r["status"] in ("đã nhận", "thay bản cũ") for r in res):
        try:
            how = af.notify_new_files("tải lên: " + ", ".join(r["file"] for r in res)[:200])
            st.session_state.upload_note = ("Đã báo Airflow có tệp mới, đường ống khởi động trong vài giây."
                                            if how else "Đã báo Airflow có tệp mới.")
        except Exception:
            st.session_state.upload_note = ("Airflow chưa chạy. Tệp đã nằm trong vùng tiếp nhận và sẽ được nạp ở lượt chạy "
                                            "kế tiếp.")
    else:
        st.session_state.upload_note = "Không có tệp mới cần xử lý."
    st.rerun()


# ---------------------------------------------------------------- gui tep
c1, c2 = st.columns([3, 2])
with c1:
    files = st.file_uploader("Tệp JSON, CSV hoặc Excel", accept_multiple_files=True, type=["json", "csv", "xlsx", "xls"])
    if st.button("Gửi vào hệ thống", type="primary", disabled=not files):
        submit([(f.name, f.getvalue()) for f in files])
with c2:
    samples = sorted(p for p in SAMPLES.glob("0*")) if SAMPLES.exists() else []
    pick = st.multiselect("Tệp mẫu", [p.name for p in samples], placeholder="Mỗi tệp mẫu là một tình huống thường gặp")
    b1, b2 = st.columns(2)
    if b1.button("Gửi tệp mẫu đã chọn", disabled=not pick):
        submit([(n, (SAMPLES / n).read_bytes()) for n in pick])
    if b2.button(f"Gửi cả {len(samples)} tệp mẫu", disabled=not samples):
        submit([(p_.name, p_.read_bytes()) for p_ in samples])
    if (SAMPLES / "DOC_TRUOC.txt").exists():
        with st.expander("Mỗi tệp mẫu là tình huống gì"):
            st.text((SAMPLES / "DOC_TRUOC.txt").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- ket qua lan gui vua roi
res = st.session_state.get("upload_result")
if res:
    st.subheader("Kết quả tiếp nhận")
    ui.table(pd.DataFrame([{   # bang tinh, chu tu xuong dong: ly do tu choi phai doc duoc tron ven
        "Tệp gửi": r["file"], "Nhận dạng là": r["source"] or "Không nhận dạng được",
        "Kết quả": ui.status(label(r["status"])), "Vị trí trong vùng tiếp nhận": r["target"] or "—",
        "Lý do": " ".join(x for x in [r["reason"] or ""] + r["notes"] if x) or "—"} for r in res]),
        widths=[19, 11, 11, 24, 35])
    st.caption(st.session_state.get("upload_note", ""))


# ---------------------------------------------------------------- theo doi xu ly
def just_sent(minutes=15):
    """Co tep vua duoc nhan trong vai phut qua: duong ong co the chua kip khoi dong, van phai tu cap nhat."""
    now = pd.Timestamp.now()
    return any(h["status"] in ("đã nhận", "thay bản cũ") and now - pd.Timestamp(h["time"]) < pd.Timedelta(minutes=minutes)
               for h in intake.history(PROFILE, 20))


@st.fragment(run_every=4 if af.busy() or just_sent() else None)
def processing():
    st.subheader("Tệp đã gửi gần đây")
    hist = intake.history(PROFILE, 40)
    if not hist:
        st.caption("Chưa có tệp nào được gửi qua kênh này.")
        return
    targets = [h["target"] for h in hist if h["target"]]
    log = query("select file_path, status, row_count, error, ingested_at from bronze._ingest_log where file_path in ("
                + ",".join(f"'{t}'" for t in targets) + ") qualify row_number() over (partition by file_path "
                "order by ingested_at desc) = 1") if targets else pd.DataFrame()
    quar = query("select _source_file, count(*) n from silver.silver_quarantine where _source_file in ("
                 + ",".join(f"'{t}'" for t in targets) + ") group by 1") if targets else pd.DataFrame()
    busy = log is None
    log = log.set_index("file_path") if log is not None and len(log) else pd.DataFrame()
    quar = dict(zip(quar._source_file, quar.n)) if quar is not None and len(quar) else {}
    rows = []
    for h in hist:
        t, sent = h["target"], pd.Timestamp(h["time"])
        if h["status"] == "từ chối":
            stage = "Không vào vùng tiếp nhận"
        elif t in log.index and pd.Timestamp(log.ingested_at[t]) >= sent - pd.Timedelta(hours=7, minutes=1):
            st_ = log.status[t]
            stage = (f"Đã nạp Bronze, {vn(log.row_count[t])} dòng" + (f", cách ly {vn(quar[t])} dòng ở Silver" if t in quar
                                                                       else "")) if st_ in ("loaded", "reloaded") \
                else f"Bước nạp không nhận: {log.error[t]}"
        elif h["status"] == "trùng, bỏ qua":
            stage = "Đã có sẵn, không cần nạp"
        else:
            stage = "Kho đang được ghi" if busy else "Chờ đường ống nạp"
        rows.append({"Lúc gửi": f"{sent:%d/%m %H:%M}", "Tệp gửi": h["file"], "Nguồn": h["source"] or "—",
                     "Tiếp nhận": label(h["status"]), "Xử lý": stage})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    st.caption("Tệp bị từ chối được lưu riêng để người gửi sửa và gửi lại. Từng bước của đường ống xem ở trang Vận hành "
               "hằng ngày.")


processing()

# ---------------------------------------------------------------- hop dong du lieu
with st.expander("Hợp đồng dữ liệu của từng nguồn"):
    st.dataframe(pd.DataFrame([{"Nguồn": s["system"], "Định dạng": s["fmt"], "Vị trí chuẩn": s["folder"],
                                "Cột, trường bắt buộc": ", ".join(s["required"]) or "theo từng danh mục"}
                               for s in SOURCES]), hide_index=True, width="stretch")
    st.caption("Chi nhánh, ngày và vị trí chuẩn được suy ra từ nội dung tệp, nên tên tệp không quan trọng. Riêng sổ nhập "
               "kho mẫu B không ghi chi nhánh trong tệp, tên tệp phải có mã chi nhánh dạng CNxx.")
