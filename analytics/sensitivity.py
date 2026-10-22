"""Phan tich do nhay theo CACH TINH MUC KY VONG - CHI chay tren tap phat trien (calibration).

Tap kiem tra da duoc danh gia mot lan voi cau hinh chot (commit 60d28bb); chuong trinh nay tu choi chay tren holdout.
Moi phuong an chi thay cach tinh bang mart_kpi_vs_peers_weekly (muc ky vong, z cua bo chi so giam sat); cac bang
chung khac (doi soat san, kho, thu ngan) giu nguyen, nguong diem giu 3,5. Ket qua chi de giai thich lua chon thiet ke,
khong dung de chon lai phuong phap.

    python -m analytics.sensitivity            # ghi docs/results/calibration_do_nhay_phuong_phap.csv
"""
import argparse

import numpy as np
import pandas as pd

from . import config as C
from . import detect
from . import evaluate as E
from .data import load_gold

PROFILE = "calibration"
VARIANTS = [
    # (ten, nhom so sanh, so tuan muc nen, cach uoc luong, co san do dao dong)
    ("Đề xuất: nhóm cùng hạng, trung vị và MAD 8 tuần, có sàn", "tier", 8, "robust", True),
    ("Nhóm so sánh toàn chuỗi", "chain", 8, "robust", True),
    ("Không so nhóm, chỉ lịch sử của chính chi nhánh", "none", 8, "robust", True),
    ("Cửa sổ mức nền 4 tuần", "tier", 4, "robust", True),
    ("Cửa sổ mức nền 12 tuần", "tier", 12, "robust", True),
    ("Trung bình và độ lệch chuẩn thay trung vị và MAD", "tier", 8, "classic", True),
    ("Bỏ sàn độ dao động", "tier", 8, "robust", False),
]


def _loo_median(values):
    """Trung vi cua cac phan tu KHAC tung phan tu (bo chinh no), bo qua gia tri thieu."""
    v = values.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        rest = np.delete(v, i)
        rest = rest[~np.isnan(rest)]
        if len(rest):
            out[i] = np.median(rest)
    return pd.Series(out, index=values.index)


def _mad(x):
    x = x[~np.isnan(x)]
    return np.median(np.abs(x - np.median(x))) if len(x) else np.nan


def expected_table(long, peer="tier", window=8, estimator="robust", floor=True):
    """Tai hien mart_kpi_vs_peers_weekly (dbt) voi cac lua chon thay doi duoc."""
    d = long.sort_values(["branch_id", "kpi", "week_start"]).copy()
    level = d.kpi_kind == "level"
    if peer == "none":
        d["peer_median"] = np.where(level, 1.0, 0.0)
    else:
        keys = ["week_start", "kpi"] + (["store_class"] if peer == "tier" else [])
        d["peer_median"] = d.groupby(keys, group_keys=False).value.apply(_loo_median)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = d.value.where(d.value != 0) / d.peer_median.where(d.peer_median != 0)
        d["rel"] = np.where(level, np.log(ratio), d.value - d.peer_median)
    g = d.groupby(["branch_id", "kpi"]).rel
    prev = g.shift(1)
    roll = prev.groupby([d.branch_id, d.kpi]).rolling(window, min_periods=1)
    if estimator == "robust":
        d["baseline_rel"] = roll.median().reset_index(level=[0, 1], drop=True)
        d["noise_own"] = 1.4826 * roll.apply(_mad, raw=True).reset_index(level=[0, 1], drop=True)
    else:
        d["baseline_rel"] = roll.mean().reset_index(level=[0, 1], drop=True)
        d["noise_own"] = roll.std().reset_index(level=[0, 1], drop=True)
    d["baseline_n"] = roll.count().reset_index(level=[0, 1], drop=True)
    d["noise_floor"] = d.groupby(["kpi", "week_start"]).noise_own.transform("median")
    rating = np.where(d.kpi.str.endswith("_rating"), 0.05, 0.0)
    d["noise_sd"] = np.fmax(np.fmax(d.noise_own, d.noise_floor if floor else np.nan), rating)
    d["dev"] = d.rel - d.baseline_rel
    d["z"] = d.dev / np.fmax(d.noise_sd, 1e-6)
    d["expected_value"] = np.where(level, d.peer_median * np.exp(d.baseline_rel), d.peer_median + d.baseline_rel)
    d["gap_vs_expected"] = d.value - d.expected_value
    return d


def run(G, kv, weeks, labels, inc, nb):
    G2 = dict(G)
    G2["mart_kpi_vs_peers_weekly"] = kv
    scores = detect.score_all(G2)
    pred = E.method_ours(G2, scores, C.SCORE_ALERT)
    s, per, fp = E.evaluate(pred[pred.week_start.isin(weeks)], labels, inc, weeks, nb)
    best = (0.0, None)
    for t in np.arange(2.0, 5.01, 0.5):
        p = E.method_ours(G2, scores, float(t))
        st, *_ = E.evaluate(p[p.week_start.isin(weeks)], labels, inc, weeks, nb)
        if st["f1"] > best[0]:
            best = (st["f1"], float(t))
    s["f1_tot_nhat_khi_quet_nguong"], s["nguong_tot_nhat"] = best
    s["bao_dong_gia_chua_xac_dinh"] = int((fp.pred_cause == "?").sum())
    return s


def commission_illustration(G):
    """Minh hoa gia dinh: neu san tinh sai 5 diem % keo dai tu 13/5 den het ky, luat doi soat va diem z bat duoc
    bao nhieu tuan. Chi doi chuoi chenh lech hoa hong cua CN4 tren GrabFood, dung dung cach tinh z hien tai."""
    kv = G["mart_kpi_vs_peers_weekly"]
    long = kv[kv.kpi == "grabfood_commission_gap"][["branch_id", "store_class", "week_start", "kpi", "kpi_kind", "value"]].copy()
    hit = (long.branch_id == 4) & (long.week_start >= "2024-05-13")
    long.loc[hit, "value"] = 0.05
    t = expected_table(long)
    t = t[(t.branch_id == 4) & (t.week_start >= "2024-05-13")]
    rule = int((t.value > C.COMMISSION_TOLERANCE).sum())
    z_hit = int((t.z >= C.Z_ALERT).sum())
    return len(t), rule, z_hit, t[["week_start", "value", "baseline_rel", "z"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default=PROFILE)
    args = ap.parse_args()
    if args.profile != PROFILE:
        raise SystemExit("Chỉ chạy trên tập phát triển: tập kiểm tra đã được đánh giá một lần với cấu hình đã chốt.")

    G = load_gold(PROFILE)
    kv = G["mart_kpi_vs_peers_weekly"]
    long = kv[["branch_id", "store_class", "week_start", "kpi", "kpi_kind", "value"]]
    weeks = detect.usable_weeks(G)
    weeks = [w for w in weeks if (G["mart_branch_weekly"].query("week_start == @w").n_days == 7).all()]
    inc = E.load_incidents(PROFILE)
    labels = E.label_weeks(weeks, inc)
    nb = G["dim_branch"].shape[0]

    # 1. tai hien dung bang dbt truoc khi thay doi bat cu gi
    mine = expected_table(long).set_index(["branch_id", "week_start", "kpi"])
    ref = kv.set_index(["branch_id", "week_start", "kpi"])
    both = ref[ref.baseline_n >= C.MIN_BASELINE_WEEKS][["z"]].join(mine[["z"]], rsuffix="_py").dropna()
    diff = (both.z - both.z_py).abs()
    print(f"Tái hiện mart dbt: {len(both)} dòng, sai khác z lớn nhất {diff.max():.2e}")
    if diff.max() > 1e-6:
        raise SystemExit("Không tái hiện được bảng dbt, dừng.")

    rows = []
    for name, peer, window, est, floor in VARIANTS:
        t = expected_table(long, peer, window, est, floor)
        s = run(G, t, weeks, labels, inc, nb)
        rows.append({"phuong_an": name, **s})
        print(f"{name}: {s['su_co_bat_duoc']} sự cố, {s['so_canh_bao']} cảnh báo, báo động giả {s['bao_dong_gia']}, "
              f"F1 {s['f1']} (tốt nhất {s['f1_tot_nhat_khi_quet_nguong']} ở ngưỡng {s['nguong_tot_nhat']})")
    out = pd.DataFrame(rows)
    out.to_csv(E.OUT_DIR / f"{PROFILE}_do_nhay_phuong_phap.csv", index=False, encoding="utf-8-sig")

    n, rule, z_hit, detail = commission_illustration(G)
    print(f"\nMinh họa P1a, sai lệch 5 điểm % kéo dài {n} tuần: luật bắt {rule} tuần, điểm z ≥ 3 bắt {z_hit} tuần")
    print(detail.to_string(index=False))
    detail.to_csv(E.OUT_DIR / f"{PROFILE}_minh_hoa_luat_vs_z.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
