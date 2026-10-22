"""O SQL tren ban trinh dien cong khai: chi doc kho, khong doc/ghi tep ngoai, khong doi cau hinh."""
import duckdb
import pytest

from analytics import safe_sql


@pytest.fixture()
def kho(tmp_path):
    f = tmp_path / "kho.duckdb"
    with duckdb.connect(str(f)) as con:
        con.sql("create schema gold; create table gold.t as select range as x from range(500)")
    (tmp_path / "bi_mat.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    return f, tmp_path


def test_select_hop_le_co_gioi_han_dong(kho):
    f, _ = kho
    df, cut = safe_sql.run(f, "select x from gold.t order by x", limit=200)
    assert len(df) == 200 and cut
    df, cut = safe_sql.run(f, "with q as (select count(*) n from gold.t) select n from q;")
    assert df.n.iloc[0] == 500 and not cut


@pytest.mark.parametrize("sql", [
    "copy gold.t to 'x.csv'",
    "select 1; drop table gold.t",
    "attach 'khac.duckdb'",
    "install httpfs",
    "set enable_external_access = true",
    "select * from gold.t; select 2",
    "pragma database_list",
])
def test_cau_bi_chan_truoc_khi_chay(kho, sql):
    f, _ = kho
    with pytest.raises(ValueError):
        safe_sql.run(f, sql)


def test_khong_doc_duoc_tep_ngoai(kho):
    f, d = kho
    with pytest.raises(duckdb.Error):
        safe_sql.run(f, f"select * from read_csv('{(d / 'bi_mat.csv').as_posix()}')")
    with pytest.raises(duckdb.Error):
        safe_sql.run(f, f"select * from '{(d / 'bi_mat.csv').as_posix()}'")


def test_tu_khoa_trong_chuoi_khong_bi_chan(kho):
    f, _ = kho
    df, _ = safe_sql.run(f, "select 'copy, delete' as ghi_chu")
    assert df.ghi_chu.iloc[0] == "copy, delete"


def test_cac_cau_mau_cua_trang_kho_du_lieu_deu_qua_kiem_tra():
    import re
    from pathlib import Path
    src = (Path(__file__).resolve().parent.parent / "app" / "views" / "warehouse.py").read_text(encoding="utf-8")
    samples = [s for s in re.findall(r'"""(select.*?|with.*?)"""', src, re.S | re.I)]
    assert samples
    for s in samples:
        safe_sql.check_sql(s)
