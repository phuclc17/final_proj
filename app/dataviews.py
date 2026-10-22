"""Ham dung chung cho cac trang du lieu: doc tep nguon dang bang, ho so cot, xem bang trong kho co bo loc."""
import json
import os
import re

import duckdb
import pandas as pd
import streamlit as st

EXTS = (".csv", ".json", ".parquet", ".xlsx")
MAX_ROWS = 5000
DATE_COLS = ["date_day", "business_date", "work_date", "week_start", "receipt_date", "count_date", "period_end",
             "report_generated_date", "snapshot_date", "weather_date", "holiday_date", "finished_at", "ingested_at"]


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
    """(bang, ban ghi JSON, thong tin lop vo). Giu nguyen gia tri tho: CSV/Excel doc dang chuoi, khong tu doan kieu."""
    if path.endswith(".csv"):
        return pd.read_csv(path, dtype=str, keep_default_na=False), None, None
    if path.endswith(".parquet"):
        return pd.read_parquet(path), None, None
    if path.endswith(".xlsx"):
        df = pd.read_excel(path, header=None, dtype=str).fillna("")
        df.columns = [f"cot_{i + 1}" for i in range(df.shape[1])]
        return df, None, None
    raw = json.load(open(path, encoding="utf-8"))
    if isinstance(raw, dict):
        # tep xuat qua API thuong boc ban ghi trong 1 lop vo, vd {page, total, data: [...]} -> bung mang ban ghi
        lists = [k for k, v in raw.items() if isinstance(v, list) and v and isinstance(v[0], dict)]
        if len(lists) == 1:
            return None, raw[lists[0]], {k: v for k, v in raw.items() if k != lists[0]}
        return None, [raw], None
    return None, raw, None


def column_profile(df):
    rows = []
    for c in df.columns:
        s = df[c]
        empty = s.isna() | s.astype(str).str.strip().isin(["", "None", "nan"])
        non_empty = s[~empty]
        rows.append({"Cột": c, "Kiểu": str(s.dtype), "% rỗng": round(empty.mean() * 100, 1),
                     "Số giá trị khác nhau": s.astype(str).nunique(),
                     "Ví dụ": str(non_empty.iloc[0])[:80] if len(non_empty) else ""})
    return pd.DataFrame(rows)


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
            where.append("branch_id = ?")
            params.append(b)
    dcol = next((c for c in DATE_COLS if c in cols), None)
    if dcol:
        lo, hi = con.sql(f'select min(cast({dcol} as date)), max(cast({dcol} as date)) from {schema}."{name}"').fetchone()
        if lo and hi:
            rng = c2.date_input(f"Khoảng thời gian theo cột {dcol}", (lo, hi), min_value=lo, max_value=hi,
                                format="DD/MM/YYYY", key=f"{key}_d_{name}")
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                where.append(f"cast({dcol} as date) between ? and ?")
                params += list(rng)
    sql_where = (" where " + " and ".join(where)) if where else ""
    n = con.execute(f'select count(*) from {schema}."{name}"{sql_where}', params).fetchone()[0]
    order = f" order by {dcol}" if dcol else ""
    df = con.execute(f'select * from {schema}."{name}"{sql_where}{order} limit {MAX_ROWS}', params).df()
    st.caption(f"{n:,} dòng thỏa bộ lọc".replace(",", ".")
               + (f", hiển thị {MAX_ROWS:,} dòng đầu".replace(",", ".") if n > MAX_ROWS else ""))
    st.dataframe(df, width="stretch", hide_index=True)


def readonly(path):
    return duckdb.connect(str(path), read_only=True)


def dir_signature(root):
    """Thoi diem sua moi nhat cua thu muc goc va hai cap thu muc con (~100 thu muc): tep moi den lam doi thu muc chua no."""
    sig = os.path.getmtime(root) if os.path.isdir(root) else 0
    for system in os.scandir(root) if os.path.isdir(root) else []:
        if system.is_dir():
            sig = max(sig, system.stat().st_mtime)
            sig = max([sig] + [d.stat().st_mtime for d in os.scandir(system.path) if d.is_dir()])
    return sig


@st.cache_data(max_entries=8)
def walk_sources(root, sig):
    """Ban do tep nguon theo he thong: so tep, dung luong, dinh dang, tep moi nhat. Duyet ~6.700 tep qua thu muc
    gan vao Docker mat ~10 giay, nen giu ket qua theo dir_signature: chi duyet lai khi co tep moi."""
    rows = []
    if not os.path.isdir(root):
        return pd.DataFrame()
    for system in sorted(os.listdir(root)):
        base = os.path.join(root, system)
        if not os.path.isdir(base):
            continue
        n = size = 0
        exts, newest = set(), ""
        for r, _, fs in os.walk(base):
            for f in fs:
                if f.endswith(EXTS):
                    n += 1
                    size += os.path.getsize(os.path.join(r, f))
                    exts.add(f.rsplit(".", 1)[-1].upper())
                    newest = max(newest, f)
        rows.append({"Thư mục": system, "Số tệp": n, "Dung lượng, MB": size / 1e6,
                     "Định dạng": ", ".join(sorted(exts)), "Tệp mới nhất theo tên": newest})
    return pd.DataFrame(rows)
