"""Phan dung chung cua ung dung: nap du lieu Gold, chay bo phat hien, bo loc chung (tap du lieu, chi nhanh,
khoang thoi gian) luu trong session_state de moi trang dung chung."""
import os
import re
import sys
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics import actions  # noqa: E402
from analytics import config as C  # noqa: E402
from analytics import detect  # noqa: E402
from analytics.data import PROFILES, db_path, load_gold  # noqa: E402

ALL = "Toàn chuỗi"
# Ban xem truc tuyen: chi co ung dung va kho du lieu chi doc, khong co Airflow, Metabase, API nguon.
STATIC = os.environ.get("FASTFAT_STATIC") == "1"
# Ban trinh dien cong khai cho giang vien cham: an tai tep len, bat/tat lich chay; o SQL luon qua lop an toan.
DEMO = os.environ.get("FASTFAT_DEMO") == "1" or STATIC


@st.cache_data(show_spinner="Đang đọc kho dữ liệu và quét cảnh báo…")
def get_data(profile, mtime):
    G = load_gold(profile)
    if G is None:
        return None, None, None
    scores = detect.score_all(G)
    return G, scores, detect.alert_table(G, scores)


def load_current():
    profile = PROFILES[st.session_state.get("profile", list(PROFILES)[0])]
    path = db_path(profile)
    if not path.exists():
        st.error(f"Chưa có kho dữ liệu `{path}`.")
        st.stop()
    try:
        G, scores, alerts = get_data(profile, path.stat().st_mtime)
    except duckdb.IOException:
        st.warning("Pipeline đang ghi dữ liệu vào kho. Vui lòng tải lại trang sau ít giây.")
        st.stop()
    if G is None:
        st.error("Chưa có tầng Gold. Chạy: `python -m pipeline.run_dbt --profile <tập> build`")
        st.stop()
    return G, scores, alerts


@st.cache_data(show_spinner=False)
def get_action_context(profile, mtime):
    """Bang chung dung chung cho phan de xuat xu ly (kho, thu ngan, doi soat san), tinh mot lan cho moi phien ban kho."""
    G, _, _ = get_data(profile, mtime)
    return actions.prepare(G)


def action_context():
    profile = current_profile()
    return get_action_context(profile, db_path(profile).stat().st_mtime)


@st.cache_data(show_spinner=False)
def get_losses(profile, mtime, score_alert):
    """Uoc tinh thiet hai va nguoi phu trach cho moi dong canh bao, theo doi (de sap xep danh sach)."""
    G, scores, _ = get_data(profile, mtime)
    A = detect.alert_table(G, scores, score_alert=score_alert)
    return actions.loss_table(G, get_action_context(profile, mtime), A[A.level != "Bình thường"])


def losses(score_alert):
    profile = current_profile()
    return get_losses(profile, db_path(profile).stat().st_mtime, score_alert)


def show_recommendation(rec, heading=True):
    """Khoi de xuat xu ly: anh huong uoc tinh, nguoi phu trach, viec xac minh, xu ly, theo doi."""
    if heading:
        st.subheader("Đề xuất xử lý")
    st.markdown(f"Phụ trách: {rec.owner}. Thời hạn: {rec.deadline}.")
    if rec.impact:
        for col, (label, v, unit, note) in zip(st.columns(len(rec.impact)), rec.impact):
            val = money_short(v) if unit == "vnd" else ("—" if pd.isna(v) else f"{vn(v)} {'đơn' if unit == 'don' else 'ca'}")
            col.metric(label, val, border=True)
        notes = [f"{label}: {pretty(note)}" for label, _, _, note in rec.impact if note]
        if notes:
            st.caption(" ".join(n if n.endswith(".") else n + "." for n in notes))
    cols = st.columns(3)
    for col, title, items in zip(cols, ("Xác minh", "Xử lý", "Theo dõi sau xử lý"), (rec.verify, rec.act, rec.watch)):
        with col:
            st.markdown(f"**{title}**")
            st.markdown("\n".join(f"{i}. {x}" for i, x in enumerate(items, 1)) or "—")
    st.caption("Số tiền là ước tính từ dữ liệu trong kho để ưu tiên xử lý, không phải kết luận. Mọi nghi vấn cần được "
               "xác minh tại chi nhánh trước khi quy trách nhiệm.")


def current_profile():
    return PROFILES[st.session_state.get("profile", list(PROFILES)[0])]


@st.cache_data(ttl=30, show_spinner=False)
def query(profile, sql):
    """Truy van chi doc; None neu bang chua ton tai. Ket noi dong ngay de khong giu khoa tep."""
    path = db_path(profile)
    if not path.exists():
        return None
    try:
        with duckdb.connect(str(path), read_only=True) as con:
            return con.sql(sql).df()
    except duckdb.CatalogException:
        return None
    except duckdb.IOException:
        st.warning("Pipeline đang ghi dữ liệu vào kho. Vui lòng tải lại trang sau ít giây.")
        st.stop()


def sidebar_filters(G):
    """Bo loc chung: chi nhanh + khoang ngay, gioi han theo du lieu thuc co.
    Gia tri luu o khoa rieng (branch_value, period_value) chu khong gan vao widget: Streamlit xoa trang thai widget khi
    sang trang khong co widget do, nen gan truc tiep se mat bo loc moi lan di qua trang Du lieu."""
    b = G["dim_branch"].sort_values("branch_id")
    options = [ALL] + b.branch_id.tolist()
    names = dict(zip(b.branch_id, b.branch_name))
    classes = dict(zip(b.branch_id, b.store_class))
    cur_b = st.session_state.get("branch_value", ALL)
    st.session_state.branch_value = st.sidebar.selectbox(
        "Chi nhánh", options, index=options.index(cur_b) if cur_b in options else 0,
        format_func=lambda x: x if x == ALL else f"CN{x} · {names[x]} · hạng {classes[x]}")
    dmin, dmax = G["dim_date"].date_day.min().date(), G["dim_date"].date_day.max().date()
    cur = st.session_state.get("period_value")
    if not (isinstance(cur, (list, tuple)) and len(cur) == 2 and dmin <= cur[0] <= cur[1] <= dmax):
        cur = (dmin, dmax)
    val = st.sidebar.date_input("Khoảng thời gian", value=cur, min_value=dmin, max_value=dmax, format="DD/MM/YYYY")
    if isinstance(val, (list, tuple)) and len(val) == 2:
        st.session_state.period_value = tuple(val)
    st.sidebar.caption(f"Dữ liệu hiện có: {dmin:%d/%m/%Y} – {dmax:%d/%m/%Y}")


def analysis_page():
    """Goi o dau moi trang phan tich: nap du lieu va dung bo loc o thanh ben."""
    G, scores, alerts = load_current()
    sidebar_filters(G)
    return G, scores, alerts


def selection():
    """(chi nhanh hoac None, ngay bat dau, ngay ket thuc)."""
    branch = st.session_state.get("branch_value", ALL)
    start, end = st.session_state.get("period_value", (None, None))
    return (None if branch == ALL else branch), pd.Timestamp(start), pd.Timestamp(end)


def in_period(df, col, start, end):
    return df[(df[col] >= start) & (df[col] <= end)]


def weeks_in_period(df, start, end):
    """Tuan (thu Hai) co giao voi khoang ngay da chon."""
    return df[(df.week_start + pd.Timedelta(days=6) >= start) & (df.week_start <= end)]


def vn(x, d=0):
    """So kieu Viet Nam: dau cham hang nghin, dau phay thap phan."""
    if x is None or pd.isna(x):
        return "—"
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def vn_frame(df, decimals=None):
    """Bang tong hop cho st.dataframe theo kieu so Viet Nam: cot so thanh chuoi '1.234,5' can phai.
    decimals: {cot: so chu so thap phan}; mac dinh 0 voi so nguyen, 2 voi so thuc. Tra (bang, column_config)."""
    decimals, out, cfg = decimals or {}, df.copy(), {}
    for c in out.columns:
        col = out[c]
        if not pd.api.types.is_numeric_dtype(col) or pd.api.types.is_bool_dtype(col):
            continue
        whole = pd.api.types.is_integer_dtype(col) or bool(((col.dropna() % 1) == 0).all())
        d = decimals.get(c, 0 if whole else 2)
        out[c] = col.map(lambda x: vn(x, d))
        cfg[c] = st.column_config.TextColumn(c, alignment="right")
    return out, cfg


def show_df(df, decimals=None, **kw):
    """st.dataframe cho bang tong hop, so theo kieu Viet Nam (vn_frame)."""
    out, cfg = vn_frame(df, decimals)
    st.dataframe(out, column_config={**cfg, **kw.pop("column_config", {})}, **kw)


def fmt_vnd(x):
    return "—" if x is None or pd.isna(x) else vn(x) + " đ"


def money_short(x):
    """Tien rut gon cho o chi so: 37,90 ty d / 125,4 trieu d."""
    if x is None or pd.isna(x):
        return "—"
    if abs(x) >= 1e9:
        return vn(x / 1e9, 2) + " tỷ đ"
    if abs(x) >= 1e6:
        return vn(x / 1e6, 1) + " triệu đ"
    return fmt_vnd(x)


def fmt_kpi(kpi, v):
    if pd.isna(v):
        return "—"
    if kpi in C.RATE_KPIS:
        return vn(v * 100, 2) + "%"
    if kpi.startswith(("net_sales", "aov")):
        return fmt_vnd(v)
    return vn(v, 1)


PLATFORM = {"grabfood": "GrabFood", "shopeefood": "ShopeeFood", "walkin": "tại quầy", "app": "App"}


def pretty(text):
    """Dinh dang lai chuoi bang chung cua bo phat hien khi hien thi (khong doi du lieu goc): ten san viet hoa, dau
    phay thap phan, bo ngoac."""
    if not isinstance(text, str):
        return text
    s = re.sub(r"\b(grabfood|shopeefood)\b", lambda m: PLATFORM[m.group(1)], text)
    s = re.sub(r"(?<=\d)\.(?=\d)", ",", s)
    s = re.sub(r"\s*\(([^()]*)\)", r", \1", s)
    return s


def zflag(z):
    """Muc lech theo nguong giam sat, dang chu (khong dung bieu tuong)."""
    if pd.isna(z):
        return ""
    return "bất thường" if abs(z) >= C.Z_ALERT else ("theo dõi" if abs(z) >= C.Z_WATCH else "")


def week_label(d):
    d = pd.Timestamp(d)
    return f"{d:%d/%m} – {d + pd.Timedelta(days=6):%d/%m/%Y}"
