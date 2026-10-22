"""Ket noi nguon: lop dau tien cua nen tang. Moi nguon den bang mot kenh (API, tep tu dong, tep do nguoi gui) vao vung
tiep nhan; trang nay cho biet nguon nao dang ket noi the nao, nhan du lieu toi dau, co cham hay co tep loi khong."""
import json
import os

import pandas as pd
import streamlit as st

import ui
from common import DEMO, ROOT, current_profile, query, vn
from pipeline.contracts import SOURCES
from pipeline.quality_gate import CADENCE, file_date

profile = current_profile()
ui.header("Kết nối nguồn", "Mỗi hệ thống đưa dữ liệu vào vùng tiếp nhận bằng kênh mà nó hỗ trợ. Từ vùng tiếp nhận, mọi "
                           "nguồn đi chung một đường ống.")

ui.cards([
    ("Kéo qua API", "2 nguồn", "POS đám mây của 8 chi nhánh và App đặt hàng. Bộ kết nối lấy tăng dần theo mốc ngày, "
                               "theo trang, tự thử lại khi API lỗi."),
    ("Tệp tự động", "4 nguồn", "POS cài tại máy của CN5, CN7, CN10, máy chấm công, thời tiết và danh mục trụ sở xuất "
                               "tệp theo lịch."),
    ("Tệp do người gửi", "4 nguồn", "Báo cáo đối soát GrabFood, ShopeeFood, sổ nhập kho và phiếu kiểm kê, gửi qua trang "
                                    "Tải tệp lên và được kiểm tra trước khi nhận."),
], cols=3)

log = query(profile, "select bronze_table, file_path, row_count, status, error, ingested_at from bronze._ingest_log")
if log is None or log.empty:
    st.caption("Môi trường này chưa nạp tệp nào.")
    st.stop()
log["ngay"] = log.file_path.map(file_date)
ok = log[log.status.isin(["loaded", "reloaded"])]
ref = ok[ok.bronze_table.isin(["pos_receipts", "app_orders", "timekeeping_punches"])].ngay.max()
last_in = pd.Timestamp(log.ingested_at.max()) + pd.Timedelta(hours=7)

rows = []
for s in SOURCES:
    tables = [t for t in log.bronze_table.dropna().unique() if t in s["bronze"] or (s["bronze"] == ["master_*"]
                                                                                    and t.startswith("master_"))]
    t = ok[ok.bronze_table.isin(tables)]
    bad = log[log.bronze_table.isin(tables) & log.status.isin(["failed", "rejected"])]
    newest = t.ngay.max()
    warn = CADENCE.get(tables[0], (None, None))[0] if tables else None
    lag = (ref - newest).days if pd.notna(newest) and pd.notna(ref) else None
    fresh = ("không theo lịch" if lag is None or warn is None else "đúng hạn" if lag <= warn else f"chậm {lag} ngày")
    rows.append({"Nguồn": s["system"], "Ngoài thực tế": s["real"], "Trong hệ thống này": s["here"],
                 "Tần suất": s["cadence"], "Định dạng": s["fmt"], "Tệp đã nạp": vn(len(t)),
                 "Dữ liệu đến": f"{newest:%d/%m/%Y}" if pd.notna(newest) else "—", "Độ mới": fresh,
                 "Tệp lỗi": vn(len(bad))})
st.subheader("Các nguồn")
tbl = pd.DataFrame(rows)
st.dataframe(tbl[["Nguồn", "Tần suất", "Định dạng", "Tệp đã nạp", "Dữ liệu đến", "Độ mới", "Tệp lỗi"]],
             hide_index=True, width="stretch")
st.caption(f"Dữ liệu hằng ngày mới nhất: {ref:%d/%m/%Y}. Lần nạp gần nhất: {last_in:%d/%m/%Y %H:%M}. Báo cáo sàn đến "
           "theo tuần và phiếu kiểm kê hai tuần một lần, nên chậm vài ngày là bình thường.")
with st.expander("Kênh của từng nguồn ngoài thực tế và trong hệ thống này"):
    ui.table(tbl[["Nguồn", "Ngoài thực tế", "Trong hệ thống này"]])

# ---------------------------------------------------------------- bo ket noi API
state = ROOT / "data" / profile / "landing" / "api_connector.json"
if profile == "live":
    st.subheader("Bộ kết nối API")
    api_docs = os.environ.get("SOURCE_API_PUBLIC_URL", "http://localhost:8600") + "/docs"
    if not state.exists():
        st.caption("Bộ kết nối chưa chạy lần nào. Ở lần đầu, mốc là ngày mới nhất đã có trong vùng tiếp nhận.")
    else:
        s = json.loads(state.read_text(encoding="utf-8"))
        st.dataframe(pd.DataFrame([{
            "Hệ thống": v.get("label", k),
            "Mốc": pd.to_datetime(v["watermark"]).strftime("%d/%m/%Y") if v.get("watermark") else "—",
            "Lần kéo gần nhất": v.get("last_run"), "Ngày vừa lấy": ", ".join(d[8:10] + "/" + d[5:7] for d in v.get("days", [])),
            "Bản ghi": vn(v.get("records") or 0), "Trang": v.get("pages"), "Lần gọi": v.get("calls"),
            "Thử lại": v.get("retries"), "Kết quả": v.get("status")} for k, v in s.items()]),
            hide_index=True, width="stretch")
    st.caption("Mỗi lượt, bộ kết nối lấy các ngày sau mốc và lấy lại chính ngày mốc để nhận hóa đơn đồng bộ trễ, đối chiếu "
               "số bản ghi với tổng do API báo rồi mới dời mốc. Khi API không phản hồi, các nguồn tệp vẫn được xử lý.")
    if not DEMO:   # API nguon thuoc phia doanh nghiep, khong mo ra ngoai o ban trinh dien
        st.markdown(f"[Tài liệu API nguồn]({api_docs})")

# ---------------------------------------------------------------- van de can xu ly
st.subheader("Tệp cần xử lý")
latest = log.sort_values("ingested_at").groupby("file_path").tail(1)
issues = latest[latest.status.isin(["failed", "rejected", "unrecognized"])].sort_values("ingested_at", ascending=False)
if issues.empty:
    st.caption("Không có tệp nào bị lỗi, bị từ chối hay không nhận dạng được.")
else:
    label = {"failed": "Không đọc được", "rejected": "Sai hợp đồng dữ liệu", "unrecognized": "Không thuộc nguồn nào"}
    st.dataframe(pd.DataFrame({"Tệp": issues.file_path, "Tình trạng": issues.status.map(label), "Lý do": issues.error,
                               "Phát hiện lúc": (issues.ingested_at + pd.Timedelta(hours=7)).dt.strftime("%d/%m %H:%M")}),
                 hide_index=True, width="stretch")
    st.caption("Các tệp này không được nạp. Sửa rồi gửi lại qua trang Tải tệp lên; bản đang dùng được giữ nguyên tới khi "
               "có bản hợp lệ.")
