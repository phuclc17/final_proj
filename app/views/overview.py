"""Tong quan: dashboard kinh doanh dung bang Metabase (cong cu BI) tren kho phuc vu PostgreSQL, nhung vao ung dung.
Dung dung tap du lieu va bo loc chi nhanh, khoang thoi gian o thanh ben: moi tap mot dashboard, bo loc truyen qua URL.
Bao cao chuan (doanh thu, kenh, chi phi, nhan su, thuc don) dung cong cu BI; ung dung chi tu viet phan can logic rieng
(canh bao, truy vet, de xuat xu ly, van hanh du lieu)."""
import json
import os
from urllib.parse import urlencode

import requests
import streamlit as st

import ui
import overview_native
from common import DEMO, ROOT, STATIC, analysis_page, current_profile, selection

G, scores, alerts = analysis_page()
branch, start, end = selection()
names = G["dim_branch"].set_index("branch_id")
title = "Toàn chuỗi" if branch is None else f"CN{branch} · {names.branch_name[branch]}"
if STATIC:   # ban xem truc tuyen khong co Metabase: ve cung cac chi so tu Gold
    overview_native.render(G, alerts, branch, start, end, title)
    st.stop()
ui.header(f"Tổng quan · {title}")

links_file = ROOT / "bi" / "metabase_links.json"
links = json.loads(links_file.read_text(encoding="utf-8")).get(current_profile()) if links_file.exists() else None
public_base = os.environ.get("METABASE_PUBLIC_URL", "").rstrip("/")
if links and public_base:   # tren may chu: duong dan do metabase_setup ghi la noi bo, trinh duyet cua nguoi xem can dia chi cong khai
    links = {k: public_base + v[v.index("/", v.index("//") + 2):] for k, v in links.items()}
if not links:
    st.caption("Chưa dựng dashboard cho môi trường này. Chạy `python -m pipeline.publish` rồi "
               "`python bi/metabase_setup.py`.")
    st.stop()
try:
    ok = requests.get(os.environ.get("METABASE_URL", "http://localhost:3000").rstrip("/") + "/api/health",
                      timeout=3).json().get("status") == "ok"
except (requests.RequestException, ValueError):
    ok = False
if not ok:
    st.caption("Metabase chưa chạy. Bật bằng `docker compose up -d metabase`.")
    st.stop()

params = {"khoang_ngay": f"{start:%Y-%m-%d}~{end:%Y-%m-%d}"}
if branch is not None:
    params["chi_nhanh"] = names.branch_name[branch]
query = urlencode(params)
a, b = st.columns([5, 1.3], vertical_alignment="center")
a.caption(f"{start:%d/%m/%Y} – {end:%d/%m/%Y}. Dashboard Metabase trên kho phục vụ PostgreSQL. COGS% là giá vốn theo định "
          "mức công thức; Labor% chỉ gồm lương giờ trực tiếp theo chấm công. Nên so chi nhánh trong cùng hạng.")
# ban trinh dien: nguoi xem khong co tai khoan Metabase -> mo ban cong khai (chi xem) thay vi trang quan tri
b.link_button("Mở trong Metabase", f"{links['public' if DEMO else 'dashboard']}?{query}", width="stretch")
st.iframe(f"{links['public']}?{query}#bordered=false&titled=false&hide_parameters=khoang_ngay,chi_nhanh", height=1880)
