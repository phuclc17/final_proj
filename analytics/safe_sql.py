"""Chay SQL do nguoi dung (hoac tro ly) viet tren kho DuckDB mot cach an toan, dung chung cho trang Kho du lieu va tro ly.

Hai lop bao ve:
  1. check_sql: chi mot cau SELECT/WITH, chan tu khoa ghi/doc tep (COPY, ATTACH, INSTALL, LOAD, PRAGMA, SET...).
  2. Ket noi DuckDB chi doc, tat truy cap ngoai (read_csv('/etc/passwd'), http...), khoa cau hinh de cau SQL khong
     bat lai duoc; them gioi han so dong va thoi gian.
"""
import re
import threading

import duckdb

FORBIDDEN = re.compile(r"\b(attach|detach|copy|export|import|install|load|pragma|create|insert|update|delete|drop|alter|"
                       r"call|set|reset|checkpoint|vacuum|grant|truncate)\b", re.I)


def check_sql(sql):
    """Chi chap nhan mot cau SELECT/WITH. Lop bao ve thu hai la ket noi DuckDB chi doc, tat truy cap tep ngoai."""
    s = sql.strip().rstrip(";").strip()
    if ";" in s:
        raise ValueError("Chỉ được chạy một câu lệnh.")
    if not re.match(r"^(select|with)\b", s, re.I):
        raise ValueError("Chỉ cho phép câu SELECT hoặc WITH ... SELECT.")
    bad = FORBIDDEN.search(re.sub(r"'[^']*'", "''", s))   # bo qua tu khoa nam trong chuoi ky tu
    if bad:
        raise ValueError(f"Không cho phép từ khóa {bad.group(1).upper()}.")
    return s


def connect(db_file):
    return duckdb.connect(str(db_file), read_only=True,
                          config={"enable_external_access": False, "lock_configuration": True})


def run(db_file, sql, limit=200, timeout=15):
    """Tra ve (DataFrame toi da `limit` dong, co bi cat bot hay khong). Loi cu phap/chan -> ValueError, duckdb.Error."""
    s = check_sql(sql)
    with connect(db_file) as con:
        timer = threading.Timer(timeout, con.interrupt)
        timer.start()
        try:
            df = con.sql(f"select * from ({s}) as q limit {int(limit) + 1}").df()
        finally:
            timer.cancel()
    return df.head(limit), len(df) > limit
