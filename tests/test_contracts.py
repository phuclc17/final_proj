"""Kiem thu hop dong du lieu va kenh tiep nhan tep tren thu muc tam, du lieu tu tao (khong dung du lieu that).
Moi kiem thu la mot tinh huong hay gap ngoai thuc te khi tep den tu nhieu kenh."""
import csv
import io
import json

import pandas as pd
import pytest

from pipeline import contracts, intake

GRAB = ["Merchant Store Name", "Week", "Report Generated Date", "Gross Sales", "Total Orders", "Cancelled Orders",
        "Total Commission", "Ads Spend", "Promotion Cost Borne by Merchant", "Adjustment Amount",
        "Average Prep Time (min)", "Store Rating", "Net Payout"]
TK = ["employee_code", "branch_code", "event_type", "event_time", "device_id", "verification_method"]


def pos_bytes(prefix="POS-01", day="11/03/2024", n=2):
    return json.dumps([{"receipt_no": f"{prefix}-01-x-{i}", "terminal_id": f"{prefix}-01", "txn_time": f"{day} 08:0{i}:00",
                        "items": [], "total_paid": 1000} for i in range(n)]).encode()


def csv_bytes(header, rows, enc="utf-8"):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode(enc)


def grab_bytes(store="Fast&Fat - District 3 (#1)"):
    return csv_bytes(GRAB, [[store, "11/03/2024 - 17/03/2024", "19 Mar 2024", "100", "1", "0", "25", "0", "0", "0",
                             "15", "4.5", "75"]])


def tk_bytes(code="BR01", enc="utf-8", drop=None):
    rows = [["9", code, "CHECK_IN", "2024-03-11 06:41:44", "DEV-TK-01", "face"],
            ["9", code, "CHECK_OUT", "2024-03-11 14:05:00", "DEV-TK-01", "face"]]
    head = TK
    if drop:
        k = TK.index(drop)
        head = TK[:k] + TK[k + 1:]
        rows = [r[:k] + r[k + 1:] for r in rows]
    return csv_bytes(head, rows, enc)


@pytest.fixture
def live(tmp_path, monkeypatch):
    monkeypatch.setattr(intake, "ROOT", tmp_path)
    src = tmp_path / "data" / "live" / "source_systems"
    (src / "master_data" / "branches").mkdir(parents=True)
    pd.DataFrame({"branch_id": [1], "branch_name": ["Fast&Fat 250 Ly Chinh Thang"], "district": ["Q3"],
                  "latitude": [0], "longitude": [0], "open_date": ["2020-01-01"], "store_class": ["B"]}) \
        .to_csv(src / "master_data" / "branches" / "branches_20240311.csv", index=False)
    return src


# ---------------------------------------------------------------- nhan dang theo noi dung
def test_nhan_dang_theo_noi_dung_khong_theo_ten_tep():
    r = contracts.identify("baocao_ten_bat_ky.csv", grab_bytes())
    assert r.ok and r.target == "grabfood/GrabFood_Settlement_20240311_20240317.csv"
    r = contracts.identify("abc.json", pos_bytes())
    assert r.ok and r.target == "pos/POS-01/pos_export_2024-03-11.json"


def test_thieu_cot_bat_buoc_bi_tu_choi():
    r = contracts.identify("tk.csv", tk_bytes(drop="event_type"))
    assert not r.ok and "event_type" in r.errors[0]


def test_may_pos_chua_khai_bao_bi_tu_choi():
    r = contracts.identify("pos.json", pos_bytes(prefix="POS-12"))
    assert not r.ok and any("POS-12" in e for e in r.errors)


def test_tep_la_khong_nhan_dang_duoc():
    r = contracts.identify("ghi_chu.csv", csv_bytes(["a", "b"], [["1", "2"]]))
    assert r.source is None and not r.ok


def test_bao_cao_grab_luu_nham_excel_co_goi_y(tmp_path):
    f = tmp_path / "grab.xlsx"
    pd.read_csv(io.BytesIO(grab_bytes()), dtype=str).to_excel(f, index=False)
    r = contracts.identify(f.name, f.read_bytes())
    assert not r.ok and "CSV" in r.errors[0]


def test_bang_ma_utf16_van_doc_duoc():
    r = contracts.identify("tk.csv", tk_bytes(enc="utf-16"))
    assert r.ok and r.target == "timekeeping/BR01/punch_BR01_20240311.csv" and r.notes


# ---------------------------------------------------------------- kenh tiep nhan
def test_tiep_nhan_moi_trung_va_ban_sua(live):
    a = intake.intake("live", "x.json", pos_bytes(n=2))
    assert a["status"] == "đã nhận" and (live / a["target"]).exists()
    assert intake.intake("live", "y.json", pos_bytes(n=2))["status"] == "trùng, bỏ qua"
    assert intake.intake("live", "z.json", pos_bytes(n=3))["status"] == "thay bản cũ"
    assert len(json.loads((live / a["target"]).read_text())) == 3


def test_trung_noi_dung_khac_vi_tri_bi_tu_choi(live):
    """Tep da co, nguoi gui chep lai va doi ten thanh ngay khac nhung noi dung giu nguyen -> nap them se dem hai lan."""
    intake.intake("live", "tk.csv", tk_bytes())
    dup = live / "timekeeping" / "BR01" / "punch_BR01_20240312.csv"
    dup.write_bytes((live / "timekeeping" / "BR01" / "punch_BR01_20240311.csv").read_bytes())
    (live / "timekeeping" / "BR01" / "punch_BR01_20240311.csv").unlink()
    r = intake.intake("live", "tk_lai.csv", tk_bytes())
    assert r["status"] == "từ chối" and "giống hệt" in r["reason"]


def test_csv_utf16_duoc_chuyen_ve_utf8(live):
    r = intake.intake("live", "tk.csv", tk_bytes(enc="utf-16"))
    assert r["status"] == "đã nhận"
    (live / r["target"]).read_text(encoding="utf-8")   # khong loi giai ma


def test_tep_bi_tu_choi_duoc_luu_va_ghi_nhat_ky(live):
    r = intake.intake("live", "bang_luong.csv", csv_bytes(["a"], [["1"]]))
    assert r["status"] == "từ chối"
    landing = live.parent / "landing"
    assert any(landing.joinpath("_rejected").iterdir())
    assert intake.history("live")[0]["file"] == "bang_luong.csv"
