"""Kiem thu tang Bronze tren mot thu muc du lieu tam (khong dung du lieu that cua du an)."""
import csv
import io
import json

import duckdb
import pytest

from pipeline import ingest


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "ROOT", tmp_path)
    src = tmp_path / "data" / "t" / "source_systems"
    (src / "pos" / "POS-01").mkdir(parents=True)
    (src / "master_data").mkdir(parents=True)
    (src / "grabfood").mkdir(parents=True)
    return src


def write_pos(src, day, receipts):
    """Hoa don POS toi thieu nhung dung hop dong du lieu (pipeline/contracts.py)."""
    path = src / "pos" / "POS-01" / f"pos_export_2024-03-{day:02d}.json"
    path.write_text(json.dumps([{"receipt_no": r, "terminal_id": "POS-01-01", "txn_time": f"{day:02d}/03/2024 08:00:00",
                                 "items": [], "grand_total": "10.000"} for r in receipts]), encoding="utf-8")
    return path


GRAB = ["Merchant Store Name", "Week", "Report Generated Date", "Gross Sales", "Total Orders", "Total Commission",
        "Net Payout"]


def write_grab(src, name, header, rows):
    with open(src / "grabfood" / name, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def db(tmp_path):
    return duckdb.connect(str(tmp_path / "data" / "t" / "warehouse" / "fastfat.duckdb"), read_only=True)


def test_nap_lai_khong_tao_trung(workspace, tmp_path):
    write_pos(workspace, 11, ["A1", "A2", "A3"])
    ingest.run("t")
    ingest.run("t")
    with db(tmp_path) as con:
        assert con.sql("select count(*) from bronze.pos_receipts").fetchone()[0] == 3
        assert con.sql("select count(*) from bronze._ingest_log").fetchone()[0] == 1


def test_them_tep_moi_chi_nap_tep_moi(workspace, tmp_path):
    write_pos(workspace, 11, ["A1", "A2"])
    ingest.run("t")
    write_pos(workspace, 12, ["B1"])
    ingest.run("t")
    with db(tmp_path) as con:
        assert con.sql("select count(*) from bronze.pos_receipts").fetchone()[0] == 3
        assert con.sql("select count(distinct batch_id) from bronze._ingest_log").fetchone()[0] == 2


def test_tep_sua_thay_toan_bo_ban_cu(workspace, tmp_path):
    write_pos(workspace, 11, ["A1", "A2", "A3"])
    ingest.run("t")
    write_pos(workspace, 11, ["A1", "A2"])          # he thong nguon gui lai ban sua, it dong hon
    ingest.run("t")
    with db(tmp_path) as con:
        assert con.sql("select count(*) from bronze.pos_receipts").fetchone()[0] == 2
        assert con.sql("select status from bronze._ingest_log order by ingested_at desc limit 1").fetchone()[0] == "reloaded"


def test_chi_doc_lai_tep_doi_kich_thuoc_hoac_thoi_diem_sua(workspace, tmp_path, monkeypatch):
    import os
    import time
    path = write_pos(workspace, 11, ["A1", "A2"])
    ingest.run("t")
    hashed = []
    real = ingest.file_md5
    monkeypatch.setattr(ingest, "file_md5", lambda p: hashed.append(p.name) or real(p))
    ingest.run("t")
    assert hashed == []                               # khong doi: khong doc lai tep
    write_pos(workspace, 11, ["B1", "B2"])           # sua noi dung, cung kich thuoc
    os.utime(path, (time.time() + 5, time.time() + 5))
    ingest.run("t")
    assert hashed == [path.name]
    with db(tmp_path) as con:
        assert sorted(r[0] for r in con.sql("select json_extract_string(payload, '$.receipt_no') "
                                            "from bronze.pos_receipts").fetchall()) == ["B1", "B2"]


def test_tep_hong_khong_lam_hong_ca_lo_va_khong_xoa_ban_cu(workspace, tmp_path):
    good = write_pos(workspace, 11, ["A1", "A2"])
    ingest.run("t")
    good.write_text("{hong", encoding="utf-8")       # ban gui lai bi hong
    write_pos(workspace, 12, ["B1"])
    ingest.run("t")
    with db(tmp_path) as con:
        files = dict(con.sql("select _source_file, count(*) from bronze.pos_receipts group by 1").fetchall())
        assert files == {"pos/POS-01/pos_export_2024-03-11.json": 2, "pos/POS-01/pos_export_2024-03-12.json": 1}
        assert con.sql("select count(*) from bronze._ingest_log where status = 'failed'").fetchone()[0] == 1


def test_nguon_them_cot_thi_tu_them_cot(workspace, tmp_path):
    store = "Fast&Fat - District 3 (#1)"
    write_grab(workspace, "GrabFood_Settlement_20240311_20240317.csv", GRAB,
               [[store, "11/03/2024 - 17/03/2024", "19 Mar 2024", "100", "1", "25", "75"]])
    ingest.run("t")
    write_grab(workspace, "GrabFood_Settlement_20240318_20240324.csv", GRAB + ["Ads Spend"],
               [[store, "18/03/2024 - 24/03/2024", "26 Mar 2024", "200", "2", "50", "145", "5"]])
    ingest.run("t")
    with db(tmp_path) as con:
        cols = [r[0] for r in con.sql("describe bronze.grab_settlement").fetchall()]
        assert "ads_spend" in cols
        assert con.sql("select count(*) from bronze.grab_settlement").fetchone()[0] == 2


def test_gia_tri_goc_duoc_giu_nguyen(workspace, tmp_path):
    write_pos(workspace, 11, ["A1"])
    ingest.run("t")
    with db(tmp_path) as con:
        payload = json.loads(con.sql("select payload from bronze.pos_receipts").fetchone()[0])
        assert payload["grand_total"] == "10.000"   # Bronze khong ep kieu, khong lam sach


def test_tep_khong_thuoc_nguon_nao_duoc_ghi_nhan_khong_bo_qua(workspace, tmp_path):
    write_pos(workspace, 11, ["A1"])
    (workspace / "grabfood" / "baocao_tuan.xlsx").write_bytes(b"khong phai excel")
    (workspace / "ghi_chu.txt").write_text("tep la", encoding="utf-8")
    ingest.run("t")
    ingest.run("t")                                   # chay lai: khong ghi nhat ky lap lai
    with db(tmp_path) as con:
        st = dict(con.sql("select file_path, status from bronze._ingest_log").fetchall())
        assert st["grabfood/baocao_tuan.xlsx"] == "unrecognized" and st["ghi_chu.txt"] == "unrecognized"
        assert con.sql("select count(*) from bronze._ingest_log where status = 'unrecognized'").fetchone()[0] == 2


def test_tep_dung_thu_muc_sai_hop_dong_khong_duoc_nap(workspace, tmp_path):
    write_pos(workspace, 11, ["A1"])
    write_grab(workspace, "GrabFood_Settlement_20240311_20240317.csv", ["cot_a", "cot_b"], [["1", "2"]])
    ingest.run("t")
    with db(tmp_path) as con:
        row = con.sql("select status, error from bronze._ingest_log where file_path like 'grabfood/%'").fetchone()
        assert row[0] == "rejected" and "GrabFood" in row[1]
        tables = [r[0] for r in con.sql("select table_name from duckdb_tables() where schema_name='bronze'").fetchall()]
        assert "grab_settlement" not in tables


def test_csv_utf16_tha_thang_vao_van_nap_duoc(workspace, tmp_path):
    rows = [["Fast&Fat - District 3 (#1)", "11/03/2024 - 17/03/2024", "19 Mar 2024", "100", "1", "25", "75"]]
    buf = io.StringIO()
    csv.writer(buf).writerows([GRAB] + rows)
    (workspace / "grabfood" / "GrabFood_Settlement_20240311_20240317.csv").write_bytes(buf.getvalue().encode("utf-16"))
    ingest.run("t")
    with db(tmp_path) as con:
        assert con.sql("select merchant_store_name from bronze.grab_settlement").fetchone()[0] == rows[0][0]


def test_tep_pos_rong_hop_le_nap_0_dong(workspace, tmp_path):
    write_pos(workspace, 11, ["A1"])
    (workspace / "pos" / "POS-01" / "pos_export_2024-03-12.json").write_text("[]", encoding="utf-8")
    ingest.run("t")
    with db(tmp_path) as con:
        assert con.sql("select status, row_count from bronze._ingest_log where file_path like '%03-12%'").fetchone() \
            == ("loaded", 0)


def test_ten_tep_khong_khop_noi_dung_bi_tu_choi(workspace, tmp_path):
    """Chep tep ngay 11 thanh ten ngay 20: nap vao se ghi sai ngay va dem hai lan doanh thu."""
    good = write_pos(workspace, 11, ["A1", "A2"])
    (workspace / "pos" / "POS-01" / "pos_export_2024-03-20.json").write_bytes(good.read_bytes())
    ingest.run("t")
    with db(tmp_path) as con:
        st = dict(con.sql("select file_path, status from bronze._ingest_log").fetchall())
        assert st["pos/POS-01/pos_export_2024-03-20.json"] == "rejected"
        assert con.sql("select count(*) from bronze.pos_receipts").fetchone()[0] == 2
