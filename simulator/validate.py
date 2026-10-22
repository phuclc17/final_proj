"""
Kiem chung bo mo phong (CHI dung cho bo mo phong, duoc phep doc ground truth):
moi kich ban co tac dong dung cho, dung muc; chuoi nhan qua nhan su -> doanh thu co chay; bien dong binh thuong co mat.
  python -m simulator.validate --profile calibration
"""
import argparse
import json
from datetime import date, timedelta

import pandas as pd

from . import config as C


def _window(t, b, start, end):
    m = (t.branch_id == b) & (t.date >= start) & (t.date <= end)
    return t[m]


def _baseline(t, b, start, days=28):
    return _window(t, b, start - timedelta(days=days), start - timedelta(days=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="calibration")
    args = ap.parse_args()
    gt = C.DATA_DIR / args.profile / "ground_truth"
    t = pd.read_csv(gt / "daily_branch_truth.csv", parse_dates=["date"])
    t["date"] = t.date.dt.date
    scen = json.load(open(gt / "scenarios.json", encoding="utf-8"))["scenarios"]
    comm = pd.read_csv(gt / "commission_truth.csv")

    print(f"=== {args.profile}: {t.date.min()} -> {t.date.max()}, {t.branch_id.nunique()} chi nhanh, "
          f"{int(t.orders_served.sum()):,} don phuc vu ===\n")
    for s in scen:
        b, start, end = s["branch_id"], date.fromisoformat(s["start"]), date.fromisoformat(s["end"])
        w, base = _window(t, b, start, end), _baseline(t, b, start)
        print(f"[{s['id']} | {s['pain_point']} | CN{b}] {s['story']}")
        if s["type"] == "commission_overcharge":
            c = comm[(comm.branch_id == b) & (comm.platform == s["platform"])]
            hit = c[c.commission_rate_applied != C.COMMISSION_CONTRACT[s["platform"]]]
            print(f"   tuan bi tinh sai: {hit.week_start.tolist()} (ty le {hit.commission_rate_applied.unique().tolist()})")
        elif s["type"] == "marketplace_not_entered":
            rate = w.mkt_not_entered.sum() / (w.served_grabfood.sum() + w.served_shopeefood.sum())
            rate0 = base.mkt_not_entered.sum() / (base.served_grabfood.sum() + base.served_shopeefood.sum())
            print(f"   ty le don san khong vao POS: {rate0:.1%} -> {rate:.1%}; gia tri mat dau vet {w.mkt_not_entered_value.sum():,.0f} VND")
        elif s["type"] == "fresh_waste":
            print(f"   hao hut vuot dinh muc/ngay: {base.waste_excess_value.mean():,.0f} -> {w.waste_excess_value.mean():,.0f} VND")
        elif s["type"] == "evening_understaffing":
            after = _window(t, b, end + timedelta(days=1), end + timedelta(days=21))
            print(f"   bep ca toi: {base.kitchen_evening.mean():.1f} -> {w.kitchen_evening.mean():.1f} nguoi; "
                  f"tai dinh {base.peak_util.mean():.2f} -> {w.peak_util.mean():.2f}; "
                  f"prep {base.avg_prep_min.mean():.1f} -> {w.avg_prep_min.mean():.1f} phut")
            print(f"   khach bo di/ngay {base.walkin_balked.mean():.1f} -> {w.walkin_balked.mean():.1f}; "
                  f"cua hang huy/ngay {base.store_cancelled.mean():.1f} -> {w.store_cancelled.mean():.1f}")
            print(f"   he so xep hang Grab: {base.mkt_mult_grab.mean():.2f} -> trong {w.mkt_mult_grab.mean():.2f} "
                  f"-> 3 tuan sau {after.mkt_mult_grab.mean():.2f}")
            for name, part in (("trong ky", w), ("3 tuan sau", after)):
                peers = t[(t.branch_id != b) & t.branch_id.isin(_same_tier(b)) & t.date.isin(part.date)]
                peers_base = t[(t.branch_id != b) & t.branch_id.isin(_same_tier(b)) & t.date.isin(base.date)]
                own = part.served_value.mean() / base.served_value.mean() - 1
                peer = peers.served_value.mean() / peers_base.served_value.mean() - 1
                print(f"   doanh thu {name}: CN{b} {own:+.1%} vs chi nhanh cung hang {peer:+.1%} "
                      f"-> chenh {own - peer:+.1%}")
        elif s["type"] == "stock_theft":
            print(f"   gia tri mat cap: {w.theft_value.sum():,.0f} VND trong {len(w)} ngay")
        elif s["type"] == "cashier_void_fraud":
            print(f"   thu ngan {s.get('resolved_pos_code')}: {int(w.fraud_void_count.sum())} hoa don huy gian lan, "
                  f"{w.fraud_void_value.sum():,.0f} VND")
        print()

    print("=== Bien dong binh thuong (khong phai su co) ===")
    t["wd"] = pd.to_datetime(t.date).dt.weekday
    norm = t[t.scenario_ids.isna()]
    wk = norm[norm.wd < 5]
    print(f"   cuoi tuan vs ngay thuong: {norm[norm.wd >= 5].served_value.mean() / wk.served_value.mean() - 1:+.1%}")
    print(f"   ngay le vs ngay thuong:   {norm[norm.holiday == 1].served_value.mean() / wk[wk.holiday == 0].served_value.mean() - 1:+.1%}")
    rain, dry = wk[(wk.rain == 1) & (wk.holiday == 0)], wk[(wk.rain == 0) & (wk.holiday == 0)]
    print(f"   ngay mua: don tai quay {rain.served_walkin.mean() / dry.served_walkin.mean() - 1:+.1%}, "
          f"don giao {((rain.served_grabfood + rain.served_shopeefood + rain.served_app).mean() / (dry.served_grabfood + dry.served_shopeefood + dry.served_app).mean()) - 1:+.1%}")
    before, after = norm[norm.date < date(2024, 6, 1)], norm[norm.date >= date(2024, 6, 1)]
    print(f"   AOV truoc/sau doi gia 1/6: {before.served_value.sum() / before.orders_served.sum():,.0f} -> "
          f"{after.served_value.sum() / after.orders_served.sum():,.0f} VND")


def _same_tier(b):
    names = json.load(open(C.REFERENCE_DIR / "system_names.json", encoding="utf-8"))
    tier = {m["internal_branch_id"]: m["tier"] for m in names}
    return [k for k, v in tier.items() if v == tier[b]]


if __name__ == "__main__":
    main()
