"""Kiem thu buoc 'check' cua pipeline: phat hien dung tep nguon moi / da doi, bo qua tep da nap."""
import json
import os
import time

import pytest

from pipeline import ingest, run_daily


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "ROOT", tmp_path)
    monkeypatch.setattr(run_daily, "ROOT", tmp_path)
    src = tmp_path / "data" / "t" / "source_systems"
    (src / "pos" / "POS-01").mkdir(parents=True)
    (src / "master_data").mkdir(parents=True)
    return src


def write_pos(src, day, n):
    p = src / "pos" / "POS-01" / f"pos_export_2024-03-{day:02d}.json"
    p.write_text(json.dumps([{"receipt_no": f"R{i}", "grand_total": "10.000"} for i in range(n)]), encoding="utf-8")
    return p


def test_chua_nap_gi_thi_moi_tep_deu_moi(workspace):
    write_pos(workspace, 11, 2)
    write_pos(workspace, 12, 2)
    found, _ = run_daily.new_files("t")
    assert found == {"pos": 2}


def test_da_nap_thi_khong_con_tep_moi_va_check_tra_ma_bo_qua(workspace):
    write_pos(workspace, 11, 2)
    ingest.run("t")
    assert run_daily.new_files("t")[0] == {}
    assert run_daily.step_check("t", None)[0] == run_daily.NO_NEW_FILES


def test_tep_moi_va_tep_bi_sua_deu_duoc_phat_hien(workspace):
    old = write_pos(workspace, 11, 2)
    ingest.run("t")
    write_pos(workspace, 12, 3)                      # ngay moi
    old.write_text(old.read_text(encoding="utf-8").replace("10.000", "12.000"), encoding="utf-8")  # sua tep cu
    future = time.time() + 5
    os.utime(old, (future, future))
    assert run_daily.new_files("t")[0] == {"pos": 2}


def test_check_bao_so_tep_moi_theo_he_thong(workspace, monkeypatch):
    monkeypatch.setattr(run_daily, "SETTLE_SECONDS", 0)
    write_pos(workspace, 11, 2)
    code, note = run_daily.step_check("t", None)
    assert code == 0 and note == "1 tep moi: pos 1"
