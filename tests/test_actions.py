"""Kiem thu phan de xuat xu ly: dinh dang tien, quy tac chon con so uoc tinh thiet hai de sap xep canh bao."""
import ast
from pathlib import Path

import numpy as np

from analytics import actions
from analytics.actions import Rec


def test_tien_kieu_viet_nam():
    assert actions.money(850000) == "850.000 đ"
    assert actions.money(1_250_000) == "1,25 triệu đ"
    assert actions.money(12_345_670) == "12,35 triệu đ"
    assert actions.money(np.nan) == "—"


def test_p1a_lay_hoa_hong_thu_thua_luy_ke_khong_lay_mot_tuan():
    r = Rec("P1a", "", "", "", impact=[("tuần", 200_000, "vnd", ""), ("lũy kế", 700_000, "vnd", "")])
    assert actions.estimated_loss(r) == 700_000


def test_doanh_thu_cao_hon_ky_vong_khong_tinh_la_thiet_hai():
    tang = Rec("?", "", "", "", impact=[("doanh thu so với kỳ vọng", 5_000_000, "vnd", "")])
    giam = Rec("P3", "", "", "", impact=[("doanh thu so với kỳ vọng", -46_000_000, "vnd", ""),
                                        ("đơn App bị hủy", 7_000_000, "vnd", ""), ("chi phí thêm ca", 3_000_000, "vnd", "")])
    assert actions.estimated_loss(tang) == 0.0
    assert actions.estimated_loss(giam) == 46_000_000


def test_thieu_so_lieu_thi_uoc_tinh_bang_0_khong_loi():
    assert actions.estimated_loss(Rec("P2", "", "", "", impact=[])) == 0.0
    assert actions.estimated_loss(Rec("P4", "", "", "", impact=[("a", 1, "vnd", ""), ("b", 2, "vnd", ""),
                                                                   ("c", np.nan, "vnd", "")])) == 0.0


def test_de_xuat_khong_doc_dap_an_cua_bo_mo_phong():
    """Mo-dun de xuat chi duoc doc Gold va bang chung bo phat hien: khong mo tep, khong import simulator."""
    tree = ast.parse(Path(actions.__file__).read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    imports = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
    mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert "open" not in names
    assert not any("simulator" in m for m in imports | mods)
    strings = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert not any("ground_truth" in s for s in strings[1:])   # bo qua docstring dau tep (chi nhac de noi la khong doc)
