"""Nguon du lieu: tep tho do cac he thong nguon xuat ra, xem duoc dang bang va ho so cot truoc khi lam sach."""
import os

import pandas as pd
import streamlit as st

import ui
from common import ROOT, current_profile, show_df, vn
from dataviews import (EXTS, MAX_ROWS, column_profile, dir_signature, load_file, natural_key, stringify_nested,
                       walk_sources)

profile = current_profile()
ui.header("Tệp nguồn", "Nội dung vùng tiếp nhận ở dạng nguyên trạng, trước mọi bước xử lý. Mỗi hệ thống có định dạng "
                       "và kiểu mã riêng.")

SYSTEM = {
    "pos": ("Máy POS tại quầy", "Mỗi máy 1 tệp mỗi ngày", "bronze.pos_receipts"),
    "owned_app": ("App đặt hàng riêng", "1 tệp trang API mỗi ngày", "bronze.app_orders"),
    "grabfood": ("GrabFood", "Báo cáo đối soát mỗi tuần", "bronze.grab_settlement"),
    "shopeefood": ("ShopeeFood", "Báo cáo đối soát mỗi tuần", "bronze.shopee_settlement"),
    "warehouse_receipts": ("Sổ nhập kho", "Mỗi lần nhập, 2 mẫu khác nhau", "bronze.warehouse_receipts_form, _table"),
    "stock_counts": ("Phiếu kiểm kê", "2 tuần 1 lần", "bronze.stock_counts"),
    "timekeeping": ("Máy chấm công", "Mỗi chi nhánh 1 tệp mỗi ngày", "bronze.timekeeping_punches"),
    "master_data": ("Danh mục trụ sở", "Ảnh chụp khi có thay đổi", "bronze.master_*"),
    "external": ("Thời tiết, nguồn ngoài", "Mỗi ngày", "bronze.weather_daily"),
}
roots = {"Tập dữ liệu đang chọn": str(ROOT / "data" / profile / "source_systems"),
         "Dữ liệu giao dịch thật công khai The Bread Basket": str(ROOT / "data" / "public_reference")}
# mo dung tep tu trang khac (vd bang chung goc o trang Truy vet): dat san cac o chon thu muc, loc dong.
# Chi xoa yeu cau sau khi cac o chon da ve xong: khi chuyen trang, trinh duyet co the chay lai trang truoc khi lan
# chay dau ve xong, neu xoa ngay tu dau thi lan chay sau mo tep mac dinh.
goto = st.session_state.get("src_goto")
if goto and goto[0] == profile:
    st.session_state.src_root = list(roots)[0]
    cur = roots[list(roots)[0]]
    for part in goto[1].split("/"):
        st.session_state[f"src_{cur}"] = part
        cur = os.path.join(cur, part)
    st.session_state.src_filter = goto[2]
which = st.radio("Thư mục", list(roots), horizontal=True, label_visibility="collapsed", key="src_root")
root = roots[which]

if which.startswith("Tập"):
    m = walk_sources(root, dir_signature(root))
    if not m.empty:
        m.insert(1, "Hệ thống", m["Thư mục"].map(lambda k: SYSTEM.get(k, ("",))[0]))
        m["Tần suất"] = m["Thư mục"].map(lambda k: SYSTEM.get(k, ("", ""))[1])
        m["Nạp vào bảng"] = m["Thư mục"].map(lambda k: SYSTEM.get(k, ("", "", ""))[2])
        with st.expander(f"Bản đồ nguồn: {vn(m['Số tệp'].sum())} tệp, {vn(m['Dung lượng, MB'].sum())} MB",
                         expanded=True):
            mb = m["Dung lượng, MB"]
            m["Dung lượng, MB"] = mb.map(lambda x: "< 0,1" if 0 < x < 0.1 else vn(x, 1))
            show_df(m, hide_index=True, width="stretch",
                    column_config={"Dung lượng, MB": st.column_config.TextColumn("Dung lượng, MB", alignment="right")})

# ---------------------------------------------------------------- chon tep
current, level = root, 0
cols = st.columns(4)
while os.path.isdir(current):
    entries = [e for e in os.listdir(current) if not e.startswith((".", "__"))]
    entries = [e for e in entries if e.endswith(EXTS) or os.path.isdir(os.path.join(current, e))]
    if not entries:
        st.caption("Thư mục này không có tệp dữ liệu.")
        st.stop()
    label = "Hệ thống" if level == 0 and which.startswith("Tập") else ("Tệp" if not any(
        os.path.isdir(os.path.join(current, e)) for e in entries) else "Thư mục")
    ordered = sorted(entries, key=natural_key)
    if level == 0 and "pos" in ordered:  # mo san nguon chinh (POS) thay vi thu muc dau tien theo ten
        ordered.insert(0, ordered.pop(ordered.index("pos")))
    choice = cols[min(level, 3)].selectbox(label, ordered, key=f"src_{current}",
                                           format_func=lambda e: f"{e} · {SYSTEM[e][0]}" if e in SYSTEM else e)
    current, level = os.path.join(current, choice), level + 1

path = current
st.session_state.pop("src_goto", None)
st.subheader(os.path.basename(path))
st.caption(f"`{os.path.relpath(path, ROOT)}` · {os.path.getsize(path) / 1024:.1f} KB")
df, records, meta = load_file(path)
if meta:
    st.caption("Lớp vỏ của tệp: " + ", ".join(f"{k} = {v}" for k, v in meta.items()))
if records is not None:
    nested = [k for k, v in records[0].items() if isinstance(v, list) and v and isinstance(v[0], dict)]
    views = ["Mỗi dòng một bản ghi"] + [f"Tách danh sách con: {c}" for c in nested]
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
c1.metric("Số dòng", f"{len(df):,}".replace(",", "."))
c2.metric("Số cột", len(df.columns))
tab_data, tab_profile = st.tabs(["Dữ liệu", "Hồ sơ cột"])
with tab_data:
    keyword = st.text_input("Lọc dòng chứa chuỗi", key="src_filter")
    shown = df
    if keyword:
        shown = df[df.astype(str).apply(lambda s: s.str.contains(keyword, case=False, regex=False)).any(axis=1)]
    if len(shown) > MAX_ROWS:
        st.caption(f"Hiển thị {vn(MAX_ROWS)} dòng đầu trên {vn(len(shown))} dòng.")
    st.dataframe(shown.head(MAX_ROWS), width="stretch", hide_index=True)
with tab_profile:
    st.caption("Tỷ lệ rỗng và số giá trị khác nhau của từng cột là căn cứ để viết quy tắc làm sạch ở tầng Silver.")
    st.dataframe(column_profile(df), width="stretch", hide_index=True)
