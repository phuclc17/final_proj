"""Nen tang du lieu van hanh Fast&Fat - mot ung dung duy nhat cho ca phan du lieu (DE) va phan phan tich (DA).
Chay: .venv/Scripts/streamlit run app/main.py --server.port 8504   (hoac docker compose up -d -> cong 8501)"""
import streamlit as st

import ui
from common import DEMO, PROFILES
from analytics import assistant

st.set_page_config(page_title="Fast&Fat · Dữ liệu vận hành", layout="wide")
ui.setup()

home = st.Page("views/home.py", title="Sơ đồ hệ thống", default=True)
source = [
    st.Page("views/connectors.py", title="Kết nối nguồn"),
    st.Page("views/sources.py", title="Tệp nguồn"),
]
if not DEMO:   # ban trinh dien cong khai khong nhan tep tu ngoai
    source.insert(1, st.Page("views/upload.py", title="Tải tệp lên"))
data = [
    st.Page("views/daily_ops.py", title="Vận hành hằng ngày"),
    st.Page("views/warehouse.py", title="Kho dữ liệu"),
    st.Page("views/lineage.py", title="Mô hình và phả hệ"),
    st.Page("views/data_ops.py", title="Chất lượng dữ liệu"),
]
analysis = [
    st.Page("views/overview.py", title="Tổng quan"),
    st.Page("views/alerts.py", title="Trung tâm cảnh báo"),
    st.Page("views/trace.py", title="Truy vết nguyên nhân"),
]
# tro ly la phan mo rong: chi hien khi da cau hinh mo hinh ngon ngu, tranh mot trang cut khi chua co khoa
if assistant.configured():
    analysis.append(st.Page("views/assistant.py", title="Trợ lý phân tích"))
# khu kiem chung: phuong phap nghien cuu (bo mo phong dong vai doanh nghiep, danh gia bang dap an), tach khoi san pham
evaluation = [
    st.Page("views/simulator.py", title="Bộ mô phỏng"),
    st.Page("views/evaluation.py", title="Đánh giá bộ phát hiện"),
]
nav = st.navigation({"": [home], "Nguồn dữ liệu": source, "Dữ liệu": data, "Phân tích vận hành": analysis,
                     "Kiểm chứng": evaluation}, expanded=True)

user_changed = st.session_state.pop("profile_changed", False)   # nguoi dung vua tu doi o chon moi truong
if "profile_next" in st.session_state:   # trang khac yeu cau doi tap (vd bam Truy vet tu trang Van hanh hang ngay)
    st.session_state.profile = st.session_state.pop("profile_next")
elif not user_changed and st.session_state.get("profile_keep") not in (None, st.session_state.get("profile")):
    # st.switch_page xoa gia tri cua widget va tra ve moi truong mac dinh: giu moi truong dang xem khi chuyen trang
    # bang nut (Truy vet tu Trung tam canh bao, Mo tep goc tu Truy vet)
    st.session_state.profile = st.session_state.profile_keep
st.sidebar.selectbox("Môi trường dữ liệu", list(PROFILES), key="profile",
                     on_change=lambda: st.session_state.update(profile_changed=True))
st.session_state.profile_keep = st.session_state.profile
if DEMO:
    st.sidebar.caption("Bản trình diễn trên dữ liệu mô phỏng của một chuỗi giả định. Dữ liệu môi trường vận hành "
                       "được đưa về điểm ban đầu mỗi đêm.")
nav.run()
