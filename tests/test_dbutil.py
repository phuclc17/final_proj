"""Mo kho de ghi khi tien trinh khac dang giu khoa: phai cho roi ghi duoc, khong that bai ngay."""
import subprocess
import sys
import time

import duckdb
import pytest

from pipeline import dbutil

HOLD = """
import duckdb, sys, time
con = duckdb.connect(sys.argv[1], read_only=True)
print("giu", flush=True)
time.sleep(float(sys.argv[2]))
con.close()
"""


def hold_lock(path, seconds):
    """Mot tien trinh khac mo kho o che do doc (nhu ung dung Streamlit) trong `seconds` giay."""
    p = subprocess.Popen([sys.executable, "-c", HOLD, str(path), str(seconds)], stdout=subprocess.PIPE, text=True)
    assert p.stdout.readline().strip() == "giu"
    return p


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "kho.duckdb"
    with duckdb.connect(str(path)) as con:
        con.execute("create table t (x int)")
    return path


def test_cho_toi_khi_tien_trinh_khac_tha_khoa_roi_ghi_duoc(db):
    p = hold_lock(db, 2)
    t0 = time.time()
    with dbutil.connect(db, wait=30) as con:
        con.execute("insert into t values (1)")
    assert time.time() - t0 >= 1          # da phai cho, khong ghi chen khi kho dang bi giu
    p.wait()
    with duckdb.connect(str(db), read_only=True) as con:
        assert con.sql("select count(*) from t").fetchone()[0] == 1


def test_het_thoi_gian_cho_thi_bao_loi(db):
    p = hold_lock(db, 5)
    with pytest.raises(duckdb.IOException):
        dbutil.connect(db, wait=1)
    p.wait()


def test_loi_khong_phai_khoa_tep_thi_bao_ngay(tmp_path):
    not_db = tmp_path / "khong_phai_kho.duckdb"
    not_db.write_text("day khong phai tep DuckDB")
    t0 = time.time()
    with pytest.raises(duckdb.Error):
        dbutil.connect(not_db, wait=30)
    assert time.time() - t0 < 5
