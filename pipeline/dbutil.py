"""
Mo kho DuckDB cho duong ong. Tep DuckDB chi cho mot tien trinh ghi, va khong cho ghi khi tien trinh khac
dang mo doc (ung dung Streamlit doc kho moi vai giay khi nguoi dung theo doi trang Tai tep len, Van hanh
hang ngay). Neu bao loi ngay, mot luot duong ong co the that bai chi vi co nguoi dang xem trang; vi vay
khi gap loi khoa tep thi cho va thu lai, het thoi gian cho moi bao loi.
"""
import time

import duckdb

WAIT_SECONDS = 120
# Linux (Docker): "Could not set lock on file"; Windows: "being used by another process"
LOCKED = ("lock", "being used by another process")


def connect(path, read_only=False, wait=WAIT_SECONDS, step=0.5):
    t0 = time.time()
    while True:
        try:
            return duckdb.connect(str(path), read_only=read_only)
        except duckdb.IOException as e:
            if not any(m in str(e).lower() for m in LOCKED) or time.time() - t0 >= wait:
                raise
            time.sleep(step)


def wait_writable(path, wait=WAIT_SECONDS):
    """Cho toi khi mo duoc kho de ghi (dung truoc khi giao kho cho dbt, chuong trinh tu mo ket noi rieng)."""
    if path.exists():
        connect(path, wait=wait).close()
