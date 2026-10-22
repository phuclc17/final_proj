"""Kiem thu cac ham thong ke cua bo phat hien."""
import math

import numpy as np
import pytest

from analytics import detect


def test_poisson_sf_khop_cong_thuc():
    lam = 2.0
    exact = 1 - sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(5))
    assert detect.poisson_sf(5, lam) == pytest.approx(exact)
    assert detect.poisson_sf(0, lam) == 1.0


def test_p_to_z_dung_va_khong_tran_so():
    assert detect.p_to_z(0.5) == 0.0
    assert detect.p_to_z(0.0013499) == pytest.approx(3.0, abs=1e-3)
    assert detect.p_to_z(1e-300) > 30          # p rat nho khong duoc lam tron thanh 1 - p = 1


def test_bang_chung_cat_trong_0_6_va_theo_chieu():
    assert detect.evidence(-8, -1) == 6.0
    assert detect.evidence(2.5, -1) == 0.0
    assert detect.evidence(2.5, 1) == 2.5
    assert np.isnan(detect.evidence(np.nan, 1))


def test_nhieu_thu_ngan_cung_luc_can_hieu_chinh_so_sanh_boi():
    """5 lan hoan tren 130 hoa don khi ky vong ~1,4: xet rieng thi vuot nguong theo doi (z ~2,2),
    nhung khi thu 10 phep so sanh cung luc (10 thu ngan x hoan) thi la chuyen ngau nhien binh thuong."""
    p = detect.poisson_sf(5, 130 * 0.0105)
    assert detect.p_to_z(p) > 2.0                 # rieng le: trong co ve dang ngo
    assert detect.p_to_z(min(1.0, p * 10)) < 2.0  # sau Bonferroni cho 10 phep thu: khong con dang ngo
