"""Bo ket noi API: keo tang dan theo moc, phan trang, thu lai, loi khong lam hong trang thai, ghi dung dinh dang tep."""
import json
import random

import pytest
from fastapi.testclient import TestClient

from pipeline import extract
from source_api import app as api


class Adapter:
    """Dua TestClient cua FastAPI vao bo ket noi thay cho HTTP that."""

    def __init__(self, fail_days=()):
        self.c, self.fail_days = TestClient(api.app), set(fail_days)

    def get(self, path, params, headers):
        if params.get("date") in self.fail_days:
            raise OSError("mat ket noi")
        r = self.c.get(path, params=params, headers=headers)
        return r.status_code, {k.lower(): v for k, v in r.headers.items()}, r.json()


def receipts(prefix, day, n):
    return [{"receipt_no": f"{prefix}-01-{day}-{k:05d}", "terminal_id": f"{prefix}-01", "txn_time": f"{day}T10:00:00",
             "items": [{"sku": "SKU-001", "qty": 1}], "ten": "Gà rán"} for k in range(n)]


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


@pytest.fixture
def world(tmp_path, monkeypatch):
    store, src = tmp_path / "store", tmp_path / "data" / "live" / "source_systems"
    monkeypatch.setattr(api, "STORE", store)
    monkeypatch.setattr(api, "FAIL_RATE", 0.0)
    monkeypatch.setattr(api, "MAX_RPS", 10_000)
    monkeypatch.setattr(extract, "ROOT", tmp_path)
    monkeypatch.setattr(extract, "PAGE_SIZE", 7)
    for day, n in (("2024-09-22", 5), ("2024-09-23", 12), ("2024-09-24", 9)):
        for prefix in ("POS-01", "POS-02"):
            write(store / "pos" / prefix / f"pos_export_{day}.json", receipts(prefix, day, n))
        write(store / "owned_app" / f"orders_{day.replace('-', '')}.json",
              {"page": 1, "total": n, "data": [{"order_uuid": f"{day}-{k}"} for k in range(n)]})
    # vung tiep nhan da co du lieu den 22/09 (truoc khi co bo ket noi)
    for prefix in ("POS-01", "POS-02", "POS-05"):
        write(src / "pos" / prefix / "pos_export_2024-09-22.json", receipts(prefix, "2024-09-22", 5))
    write(src / "owned_app" / "orders_20240922.json",
          {"page": 1, "total": 5, "data": [{"order_uuid": f"2024-09-22-{k}"} for k in range(5)]})
    return store, src


def client(**kw):
    return extract.Client(Adapter(**kw), token=api.TOKEN, sleep=lambda s: None)


def test_keo_tang_dan_tu_moc_va_ghi_dung_dinh_dang(world):
    store, src = world
    state = extract.run("live", client())
    assert state["pos"]["watermark"] == state["app"]["watermark"] == "2024-09-24"
    assert state["pos"]["days"] == ["2024-09-22", "2024-09-23", "2024-09-24"]       # lay lai ngay moc 22/09
    assert state["pos"]["files_unchanged"] == 2 and state["pos"]["files_written"] == 4
    for day in ("2024-09-23", "2024-09-24"):
        for prefix in ("POS-01", "POS-02"):     # tep vung tiep nhan giong het tep phan mem POS xuat ra
            rel = f"pos/{prefix}/pos_export_{day}.json"
            assert (src / rel).read_bytes() == (store / rel).read_bytes()
        got = json.loads((src / "owned_app" / f"orders_{day.replace('-', '')}.json").read_text(encoding="utf-8"))
        assert got["data"] == json.loads((store / "owned_app" / f"orders_{day.replace('-', '')}.json")
                                         .read_text(encoding="utf-8"))["data"]
        assert got["total"] == len(got["data"])
    assert state["pos"]["pages"] == 2 + 4 + 3        # 10, 24, 18 hoa don / 7 moi trang
    assert not list(src.rglob("*.part"))


def test_moc_dau_khong_bi_may_pos_xuat_tep_keo_len(world):
    _, src = world
    for day in ("2024-09-23", "2024-09-24"):     # POS cai tai may da xuat tep truoc khi bo ket noi chay lan dau
        write(src / "pos" / "POS-05" / f"pos_export_{day}.json", receipts("POS-05", day, 3))
    state = extract.run("live", client())
    assert state["pos"]["days"] == ["2024-09-22", "2024-09-23", "2024-09-24"]
    assert (src / "pos" / "POS-01" / "pos_export_2024-09-23.json").exists()


def test_lay_lai_tu_ngay(world):
    _, src = world
    extract.run("live", client())
    (src / "pos" / "POS-02" / "pos_export_2024-09-23.json").unlink()      # mat tep da qua moc
    state = extract.run("live", client(), since="2024-09-23")
    assert state["pos"]["days"][0] == "2024-09-22" and state["app"]["days"][0] == "2024-09-22"
    assert state["pos"]["files_written"] == 1 and state["app"]["files_written"] == 0
    assert (src / "pos" / "POS-02" / "pos_export_2024-09-23.json").exists()


def test_chay_lai_khong_ghi_gi_moi(world):
    extract.run("live", client())
    state = extract.run("live", client())
    assert state["pos"]["status"] == "không có ngày mới"
    assert state["pos"]["files_written"] == state["app"]["files_written"] == 0


def test_ngay_moc_duoc_bo_sung_khi_den_tre(world):
    store, src = world
    extract.run("live", client())
    late = receipts("POS-01", "2024-09-24", 10)      # may POS mat mang, dong bo tre them 1 hoa don
    write(store / "pos" / "POS-01" / "pos_export_2024-09-24.json", late)
    state = extract.run("live", client())
    assert state["pos"]["files_written"] == 1
    assert json.loads((src / "pos" / "POS-01" / "pos_export_2024-09-24.json").read_text(encoding="utf-8")) == late


def test_loi_tam_thoi_duoc_thu_lai(world, monkeypatch):
    monkeypatch.setattr(api, "FAIL_RATE", 0.4)
    random.seed(7)
    state = extract.run("live", client())
    assert state["pos"]["ok"] and state["app"]["ok"]
    assert state["pos"]["retries"] + state["app"]["retries"] > 0
    assert state["pos"]["watermark"] == "2024-09-24"


def test_429_cho_theo_retry_after():
    calls, slept = [], []

    class Http:
        def get(self, path, params, headers):
            calls.append(path)
            return (429, {"retry-after": "3"}, {"detail": "nhieu"}) if len(calls) == 1 else (200, {}, {"ok": 1})

    c = extract.Client(Http(), sleep=slept.append)
    assert c.get("/x") == {"ok": 1} and slept == [3.0] and c.retries == 1


def test_sai_ma_xac_thuc_dung_ngay(world):
    _, src = world
    c = extract.Client(Adapter(), token="sai", sleep=lambda s: None)
    state = extract.run("live", c)
    assert not state["pos"]["ok"] and "xác thực" in state["pos"]["status"]
    assert c.calls == 1                      # khong thu lai khi sai ma
    assert state["pos"]["watermark"] == "2024-09-22"
    assert not (src / "pos" / "POS-01" / "pos_export_2024-09-23.json").exists()


def test_loi_giua_chung_lan_sau_lam_tiep(world):
    _, src = world
    state = extract.run("live", client(fail_days={"2024-09-24"}))
    assert not state["pos"]["ok"] and state["pos"]["watermark"] == "2024-09-23"   # moc dung o ngay da ghi xong
    assert not (src / "pos" / "POS-01" / "pos_export_2024-09-24.json").exists()
    state = extract.run("live", client())
    assert state["pos"]["ok"] and state["pos"]["watermark"] == "2024-09-24"
    assert (src / "pos" / "POS-01" / "pos_export_2024-09-24.json").exists()


def test_api_sap_khong_nem_loi(world, monkeypatch):
    class Down:
        def get(self, *a):
            raise OSError("connection refused")

    state = extract.run("live", extract.Client(Down(), sleep=lambda s: None))
    assert not state["pos"]["ok"] and not state["app"]["ok"]
    assert "không phản hồi" in state["pos"]["status"]
    assert state["pos"]["retries"] == extract.MAX_ATTEMPTS - 1
