"""Kiem thu cua chan chat luong dau vao tren mot kho DuckDB dung tay trong bo nho."""
import json
from datetime import date, datetime, timedelta

import duckdb
import pytest

from pipeline import quality_gate as qg

D0 = date(2024, 3, 1)


def build(days=20, pos_rows=100, skip_pos_last=0, last_pos_rows=None, new_field=False):
    """Kho gia lap: moi ngay 1 lo nap gom POS, App, cham cong, thoi tiet; bao cao san moi tuan."""
    con = duckdb.connect()
    con.execute("create schema bronze")
    con.execute("""create table bronze._ingest_log (batch_id varchar, bronze_table varchar, file_path varchar,
                   file_hash varchar, file_bytes bigint, row_count integer, status varchar, error varchar,
                   ingested_at timestamp)""")
    con.execute("create table bronze.pos_receipts (payload varchar, _batch_id varchar, _source_file varchar default 'pos/POS-01/f.json')")
    con.execute("create table bronze.app_orders (payload varchar, _batch_id varchar, _source_file varchar default 'owned_app/f.json')")
    con.execute("create table bronze.weather_daily (payload varchar, _batch_id varchar, _source_file varchar default 'external/weather/f.json')")
    logs = []
    for k in range(days):
        d = D0 + timedelta(days=k)
        batch, ts = f"b{k:03d}", datetime(2024, 3, 1) + timedelta(days=k + 1)
        last = k == days - 1
        if k < days - skip_pos_last:
            n = last_pos_rows if (last and last_pos_rows is not None) else pos_rows
            logs.append((batch, "pos_receipts", f"pos/POS-01/pos_export_{d:%Y-%m-%d}.json", "h", 1, n, "loaded", None, ts))
            fields = {"receipt_no": "x", "total_paid": 1, **({"loyalty_tier": "gold"} if new_field and last else {})}
            con.execute("insert into bronze.pos_receipts (payload, _batch_id) values (?, ?)", [json.dumps(fields), batch])
        for t, path in [("app_orders", f"owned_app/orders_{d:%Y%m%d}.json"),
                        ("timekeeping_punches", f"timekeeping/BR01/punch_BR01_{d:%Y%m%d}.csv"),
                        ("weather_daily", f"external/weather/weather_hcm_{d:%Y%m%d}.json")]:
            logs.append((batch, t, path, "h", 1, 50, "loaded", None, ts))
        con.execute("insert into bronze.app_orders (payload, _batch_id) values (?, ?)", [json.dumps({"order_uuid": "o"}), batch])
        con.execute("insert into bronze.weather_daily (payload, _batch_id) values (?, ?)", [json.dumps({"date": "d"}), batch])
        if d.weekday() == 6:
            for t in ("grab_settlement", "shopee_settlement"):
                logs.append((batch, t, f"{t}/S_{d - timedelta(days=6):%Y%m%d}_{d:%Y%m%d}.csv", "h", 1, 11, "loaded",
                             None, ts))
    logs.append(("b000", "stock_counts", f"stock_counts/CN01/KiemKe_CN01_{D0 + timedelta(days=days - 3):%Y%m%d}.xlsx",
                 "h", 1, 22, "loaded", None, datetime(2024, 3, 2)))
    con.executemany("insert into bronze._ingest_log values (?, ?, ?, ?, ?, ?, ?, ?, ?)", logs)
    return con


def levels(res, kind, source):
    return res[(res.check == kind) & (res.source == source)].level.tolist()


def test_du_lieu_binh_thuong_deu_dat():
    con = build()
    qg.run_checks(con)                       # lan dau khoi tao so dang ky cau truc
    res = qg.run_checks(con)
    assert (res.level == "đạt").all(), res[res.level != "đạt"]


def test_nguon_ngay_cham_4_ngay_thi_chan():
    res = qg.run_checks(build(skip_pos_last=4))
    assert levels(res, "độ mới", "pos_receipts") == ["chặn"]


def test_nguon_ngay_cham_2_ngay_thi_canh_bao():
    res = qg.run_checks(build(skip_pos_last=2))
    assert levels(res, "độ mới", "pos_receipts") == ["cảnh báo"]


def test_khoi_luong_tut_manh_thi_canh_bao():
    res = qg.run_checks(build(last_pos_rows=30))
    assert levels(res, "khối lượng", "pos_receipts") == ["cảnh báo"]


def test_ngay_khong_co_dong_nao_thi_chan():
    res = qg.run_checks(build(last_pos_rows=0))
    assert "chặn" in levels(res, "khối lượng", "pos_receipts")


def test_truong_moi_xuat_hien_thi_canh_bao():
    con = build(days=20)
    con.execute("create schema if not exists ops")
    con.execute("create table ops.schema_registry (bronze_table varchar, field varchar, first_seen timestamp)")
    con.execute("insert into ops.schema_registry values ('pos_receipts', 'receipt_no', now()), "
                "('pos_receipts', 'total_paid', now()), ('app_orders', 'order_uuid', now()), "
                "('weather_daily', 'date', now())")
    con.execute("insert into bronze.pos_receipts (payload, _batch_id) values (?, 'b019')",
                [json.dumps({"receipt_no": "x", "total_paid": 1, "loyalty_tier": "gold"})])
    res = qg.run_checks(con)
    msg = res[(res.check == "cấu trúc") & (res.source == "pos_receipts")].message.tolist()
    assert msg and "loyalty_tier" in msg[0]


@pytest.mark.parametrize("name,expected", [
    ("pos_export_2024-03-11.json", date(2024, 3, 11)),
    ("GrabFood_Settlement_20240311_20240317.csv", date(2024, 3, 17)),
    ("staff_20240311.csv", date(2024, 3, 11)),
    ("khong_co_ngay.csv", None),
])
def test_doc_ngay_tu_ten_tep(name, expected):
    got = qg.file_date(name)
    assert (got.date() if got else None) == expected


def test_chi_nhanh_thieu_tep_pos_ngay_moi_nhat_thi_canh_bao():
    con = build()
    # chi nhanh thu hai gui POS deu dan, rieng ngay moi nhat khong gui
    d_last = D0 + timedelta(days=19)
    rows = [(f"b{k:03d}", "pos_receipts", f"pos/POS-02/pos_export_{D0 + timedelta(days=k):%Y-%m-%d}.json", "h", 1, 80,
             "loaded", None, datetime(2024, 3, 2) + timedelta(days=k)) for k in range(19)]
    con.executemany("insert into bronze._ingest_log values (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    res = qg.run_checks(con)
    msg = res[res.check == "đầy đủ"]
    assert msg.level.tolist() == ["cảnh báo"] and "POS-02" in msg.message.iloc[0] and f"{d_last:%d/%m}" in msg.message.iloc[0]


@pytest.mark.parametrize("n_missing,level", [(1, "cảnh báo"), (4, "chặn")])
def test_thieu_hang_loat_thi_chan(n_missing, level):
    con = build()
    rows = [(f"b{k:03d}", "pos_receipts", f"pos/POS-{b:02d}/pos_export_{D0 + timedelta(days=k):%Y-%m-%d}.json", "h", 1, 80,
             "loaded", None, datetime(2024, 3, 2) + timedelta(days=k))
            for b in range(2, 10) for k in range(19 if b < 2 + n_missing else 20)]
    con.executemany("insert into bronze._ingest_log values (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    res = qg.run_checks(con)
    assert res[res.check == "đầy đủ"].level.tolist() == [level]
    assert ("Thiếu hàng loạt" in res[res.check == "đầy đủ"].message.iloc[0]) == (level == "chặn")


def test_tep_rong_coi_nhu_thieu():
    con = build()
    con.execute("update bronze._ingest_log set row_count = 0 where file_path like 'timekeeping/%' "
                "and file_path like '%20240320%'")
    res = qg.run_checks(con)
    assert res[res.check == "đầy đủ"].level.tolist() == ["cảnh báo"]


@pytest.mark.parametrize("status,kind", [("rejected", "sai hợp đồng"), ("unrecognized", "không nhận dạng"),
                                         ("failed", "tệp lỗi")])
def test_tep_sai_hop_dong_hoac_la_thi_canh_bao(status, kind):
    con = build()
    con.execute("insert into bronze._ingest_log values ('b019', null, 'grabfood/baocao.xlsx', 'h', 1, 0, ?, 'ly do', "
                "timestamp '2024-03-21 00:00:00')", [status])
    res = qg.run_checks(con)
    assert res[res.check == kind].level.tolist() == ["cảnh báo"]


def test_mot_tep_le_ngay_tuong_lai_khong_keo_ngay_tham_chieu():
    con = build()
    con.execute("insert into bronze._ingest_log values ('b019', 'pos_receipts', 'pos/POS-02/pos_export_2024-04-30.json',"
                " 'h', 1, 10, 'loaded', null, timestamp '2024-03-21 00:00:00')")
    res = qg.run_checks(con)
    assert levels(res, "độ mới", "pos_receipts") == ["đạt"]


def test_hai_phien_ban_dinh_dang_khac_lo_khong_bao_mat_truong():
    """POS may cu (v2.8, tep) va POS dam may (v3.2, API) ve o hai lo khac nhau: khong phai truong bien mat."""
    con = build()
    qg.run_checks(con)
    con.execute("insert into bronze.pos_receipts values (?, 'b020', 'pos/POS-05/f.json')",
                [json.dumps({"receipt_no": "x", "grand_total": 1})])
    con.execute("insert into bronze._ingest_log values ('b020', 'pos_receipts', 'pos/POS-05/pos_export_2024-03-21.json', "
                "'h', 1, 1, 'loaded', null, timestamp '2024-03-22 00:00:00')")
    qg.run_checks(con)
    con.execute("insert into bronze.pos_receipts values (?, 'b021', 'pos/POS-01/f.json')",
                [json.dumps({"receipt_no": "x", "total_paid": 1})])
    con.execute("insert into bronze._ingest_log values ('b021', 'pos_receipts', 'pos/POS-01/pos_export_2024-03-21.json', "
                "'h', 1, 1, 'loaded', null, timestamp '2024-03-22 01:00:00')")
    res = qg.run_checks(con)
    assert not res[(res.check == "cấu trúc") & res.message.str.contains("không còn")].shape[0]


def test_cung_thu_muc_mat_truong_thi_canh_bao():
    con = build()
    con.execute("insert into bronze.pos_receipts values (?, 'b020', 'pos/POS-01/f.json')",
                [json.dumps({"receipt_no": "x"})])
    con.execute("insert into bronze._ingest_log values ('b020', 'pos_receipts', 'pos/POS-01/pos_export_2024-03-21.json', "
                "'h', 1, 1, 'loaded', null, timestamp '2024-03-22 00:00:00')")
    qg.run_checks(con)
    res = qg.run_checks(con)
    msg = res[(res.check == "cấu trúc") & (res.source == "pos_receipts")].message.tolist()
    assert msg and "total_paid" in msg[0]
