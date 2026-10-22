"""Danh gia bo phat hien bang dap an cua bo mo phong.
Day la noi DUY NHAT trong lop phan tich duoc doc ground_truth/ - va chi de CHAM DIEM, khong de phat hien.

    python -m analytics.evaluate --profile calibration --sweep     # tap phat trien: chon nguong
    python -m analytics.evaluate --profile holdout                  # tap kiem tra: chay MOT lan voi nguong da chot

Don vi danh gia:
  - Su co: bat duoc khong (co canh bao trong cua so su co), tre bao nhieu ngay, nguyen nhan hang 1 co dung khong.
  - Chi nhanh x tuan: canh bao dung (nam trong cua so cua mot su co cung chi nhanh) / sai -> precision;
    tuan co su co dang dien ra duoc canh bao -> recall.
Cua so su co = cac tuan giao voi [bat dau, ket thuc + 14 ngay]: hau qua co the den sau (thu hang tren san giam
sau vai tuan, hao hut chi lo ra o lan kiem ke ke tiep).
"""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C
from . import detect
from .data import ROOT, load_gold

CAUSE_OF_TYPE = {
    "commission_overcharge": "P1a", "marketplace_not_entered": "P1b", "fresh_waste": "P2",
    "evening_understaffing": "P3", "stock_theft": "P4", "cashier_void_fraud": "P5",
}
GRACE_DAYS = 14
OUT_DIR = ROOT / "docs" / "results"


# ------------------------------------------------------------------ dap an
def load_incidents(profile):
    s = json.load(open(ROOT / "data" / profile / "ground_truth" / "scenarios.json", encoding="utf-8"))["scenarios"]
    inc = pd.DataFrame([{"id": x["id"], "cause": CAUSE_OF_TYPE[x["type"]], "branch_id": int(x["branch_id"]),
                         "start": pd.Timestamp(x["start"]), "end": pd.Timestamp(x["end"])} for x in s])
    return inc


def label_weeks(weeks, inc):
    """Moi (chi nhanh, tuan) danh gia duoc -> su co dang dien ra (active) / trong cua so hau qua (window)."""
    rows = []
    for r in inc.itertuples():
        for w in weeks:
            w_end = w + pd.Timedelta(days=6)
            active = (w_end >= r.start) and (w <= r.end)
            window = (w_end >= r.start) and (w <= r.end + pd.Timedelta(days=GRACE_DAYS))
            if window:
                rows.append((r.branch_id, w, r.id, r.cause, active))
    return pd.DataFrame(rows, columns=["branch_id", "week_start", "incident", "true_cause", "active"])


# ------------------------------------------------------------------ cac phuong an phat hien
def method_ours(G, scores, score_alert):
    a = detect.alert_table(G, scores, score_alert=score_alert)
    a = a[a.level == "Cảnh báo"][["branch_id", "week_start", "cause"]]
    return a.rename(columns={"cause": "pred_cause"})


def method_revenue_only(G, z_alert=C.Z_ALERT):
    kv = G["mart_kpi_vs_peers_weekly"]
    d = kv[(kv.kpi == "net_sales") & (kv.baseline_n >= C.MIN_BASELINE_WEEKS) & (kv.z.abs() >= z_alert)]
    return d[["branch_id", "week_start"]].assign(pred_cause="?")


def method_isolation_forest(G, n_alerts, seed=0):
    """Phat hien bat thuong khong giam sat tren vector z cua bo chi so giam sat; dat so canh bao bang dung so canh
    bao cua phuong phap de xuat de so sanh cong bang (cung 'ngan sach' canh bao)."""
    from sklearn.ensemble import IsolationForest
    X = detect.z_wide(G)[[k for k, *_ in C.INDICATORS if k in detect.z_wide(G).columns]].fillna(0.0).clip(-10, 10)
    model = IsolationForest(n_estimators=300, random_state=seed).fit(X)
    s = pd.Series(-model.score_samples(X), index=X.index).sort_values(ascending=False)
    top = s.head(max(n_alerts, 1)).index
    return pd.DataFrame(list(top), columns=["branch_id", "week_start"]).assign(pred_cause="?")


# ------------------------------------------------------------------ cham diem
def evaluate(pred, labels, inc, weeks, n_branches):
    pred = pred.merge(labels, on=["branch_id", "week_start"], how="left")
    tp = pred.incident.notna()
    n_alert = len(pred.drop_duplicates(["branch_id", "week_start"]))
    n_tp = pred[tp].drop_duplicates(["branch_id", "week_start"]).shape[0]
    active = labels[labels.active].drop_duplicates(["branch_id", "week_start"])
    hit = active.merge(pred[["branch_id", "week_start"]].drop_duplicates(), on=["branch_id", "week_start"])
    precision = n_tp / n_alert if n_alert else np.nan
    recall_w = len(hit) / len(active) if len(active) else np.nan
    f1 = 2 * precision * recall_w / (precision + recall_w) if precision and recall_w else 0.0
    normal_weeks = len(weeks) * n_branches - labels.drop_duplicates(["branch_id", "week_start"]).shape[0]

    per = []
    for r in inc.itertuples():
        win = labels[labels.incident == r.id]
        evaluable = len(win) > 0
        p = pred[pred.incident == r.id].sort_values("week_start")
        first = p.iloc[0] if len(p) else None
        per.append({
            "Sự cố": r.id, "Nguyên nhân thật": r.cause, "Chi nhánh": f"CN{r.branch_id}",
            "Thời gian": f"{r.start:%d/%m}–{r.end:%d/%m}", "Số tuần đánh giá được": len(win),
            "Bắt được": "không đánh giá được" if not evaluable else ("có" if first is not None else "không"),
            "Trễ (ngày)": int((first.week_start + pd.Timedelta(days=6) - r.start).days) if first is not None else None,
            "Nguyên nhân hạng 1 lần đầu": first.pred_cause if first is not None else None,
            "Đúng nguyên nhân": (first.pred_cause == r.cause) if first is not None and first.pred_cause != "?" else None,
            "Số tuần cảnh báo": len(p),
        })
    per = pd.DataFrame(per)
    det = per[per["Bắt được"] == "có"]
    summary = {
        "su_co_bat_duoc": f"{len(det)}/{(per['Bắt được'] != 'không đánh giá được').sum()}",
        "top1_dung": f"{int(det['Đúng nguyên nhân'].fillna(False).sum())}/{len(det)}" if det["Đúng nguyên nhân"].notna().any() else "—",
        "tre_trung_vi_ngay": float(det["Trễ (ngày)"].median()) if len(det) else None,
        "so_canh_bao": n_alert, "canh_bao_dung": n_tp, "bao_dong_gia": n_alert - n_tp,
        "precision": round(precision, 3) if pd.notna(precision) else None,
        "recall_tuan": round(recall_w, 3) if pd.notna(recall_w) else None, "f1": round(f1, 3),
        "ty_le_bao_dong_gia_tren_tuan_binh_thuong": round((n_alert - n_tp) / normal_weeks, 4),
    }
    fp = pred[~tp][["branch_id", "week_start", "pred_cause"]].sort_values(["branch_id", "week_start"])
    return summary, per, fp


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True, choices=["calibration", "holdout"])
    ap.add_argument("--sweep", action="store_true", help="quet do nhay theo nguong (chi nen dung tren tap phat trien)")
    args = ap.parse_args()

    G = load_gold(args.profile)
    scores = detect.score_all(G)
    weeks = detect.usable_weeks(G)
    weeks = [w for w in weeks if (G["mart_branch_weekly"].query("week_start == @w").n_days == 7).all()]
    inc = load_incidents(args.profile)
    labels = label_weeks(weeks, inc)
    nb = G["dim_branch"].shape[0]

    ours = method_ours(G, scores, C.SCORE_ALERT)
    ours = ours[ours.week_start.isin(weeks)]
    results = {"Đề xuất: bộ chỉ số + dấu vân tay": evaluate(ours, labels, inc, weeks, nb)}
    rev = method_revenue_only(G)
    results["Đối chứng 1: chỉ theo dõi doanh thu |z| ≥ 3"] = evaluate(rev[rev.week_start.isin(weeks)], labels, inc, weeks, nb)
    iso = method_isolation_forest(G, len(ours))
    results["Đối chứng 2: Isolation Forest, cùng số cảnh báo"] = evaluate(iso[iso.week_start.isin(weeks)], labels, inc, weeks, nb)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    comp = pd.DataFrame({k: v[0] for k, v in results.items()}).T
    print(f"\n=== {args.profile}: {len(weeks)} tuần × {nb} chi nhánh, commit {git_commit()}, "
          f"ngưỡng điểm {C.SCORE_ALERT}, z {C.Z_ALERT}")
    print(comp.to_string())
    per = results["Đề xuất: bộ chỉ số + dấu vân tay"][1]
    print("\n" + per.to_string(index=False))
    fp = results["Đề xuất: bộ chỉ số + dấu vân tay"][2]
    print("\nBáo động giả của phương pháp đề xuất:\n" + (fp.to_string(index=False) if len(fp) else "không có"))
    comp.to_csv(OUT_DIR / f"{args.profile}_so_sanh.csv", encoding="utf-8-sig")
    per.to_csv(OUT_DIR / f"{args.profile}_theo_su_co.csv", index=False, encoding="utf-8-sig")
    fp.to_csv(OUT_DIR / f"{args.profile}_bao_dong_gia.csv", index=False, encoding="utf-8-sig")

    if args.sweep:
        rows = []
        for t in np.arange(2.0, 5.01, 0.5):
            p = method_ours(G, scores, float(t))
            s, *_ = evaluate(p[p.week_start.isin(weeks)], labels, inc, weeks, nb)
            rows.append({"nguong_diem": t, **s})
        sw = pd.DataFrame(rows)
        print("\nĐộ nhạy theo ngưỡng điểm:\n" + sw.to_string(index=False))
        sw.to_csv(OUT_DIR / f"{args.profile}_do_nhay.csv", index=False, encoding="utf-8-sig")
    meta = {"profile": args.profile, "commit": git_commit(), "score_alert": C.SCORE_ALERT, "z_alert": C.Z_ALERT,
            "grace_days": GRACE_DAYS, "weeks": len(weeks), "run_at": pd.Timestamp.now().isoformat(timespec="seconds")}
    (OUT_DIR / f"{args.profile}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
