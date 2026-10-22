"""
Hieu chinh tham so mo phong bang du lieu cong khai THAT (khong phai du lieu cua Fast&Fat).
Chi rut ra QUY LUAT THONG KE co the chuyen giao (so mon/don, so luong/dong, he so ngay trong tuan,
do tap trung cua mon ban chay, do dao dong ngay), roi so voi gia tri dang gia dinh trong config.py.
  python -m simulator.calibrate_public
"""
import csv
import io
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C

REF_DIR = C.DATA_DIR / "public_reference"
OUT = REF_DIR / "calibration_report.json"


def load_bread_basket():
    path = REF_DIR / "bread_basket" / "The-Bread-Basket.arff"
    text = path.read_text(encoding="utf-8")
    data_part = text[re.search(r"^@DATA\s*$", text, re.M | re.I).end():]
    # ARFF: chuoi trong dau nhay don, dau nhay ben trong duoc thoat bang \' (vd: 'Children\'s Kitchen Pouches')
    reader = csv.reader(io.StringIO(data_part), quotechar="'", escapechar="\\", skipinitialspace=True)
    rows = [r[:3] for r in reader if r]
    df = pd.DataFrame(rows, columns=["transaction", "item", "date_time"])
    df["date_time"] = pd.to_datetime(df["date_time"], format="%d-%m-%Y %H:%M")
    return df


def fit_bread_basket(df):
    lines = df.groupby(["transaction", "item"]).size().rename("qty").reset_index()
    tx = lines.groupby("transaction").agg(n_items=("item", "nunique"))
    tx = tx.join(df.groupby("transaction")["date_time"].first())
    tx["date"] = tx.date_time.dt.normalize()

    items_dist = tx.n_items.clip(upper=4).value_counts(normalize=True).sort_index()
    qty_dist = lines.qty.clip(upper=2).value_counts(normalize=True).sort_index()

    daily = tx.groupby("date").size()
    daily = daily[daily > 0]
    wd = daily.groupby(daily.index.weekday).mean()
    weekday_factor = (wd / wd.mean()).round(3)
    # do dao dong ngay "them" ngoai nhieu Poisson: loai he so thu, loai xu huong (trung vi truot 28 ngay),
    # uoc luong vung (1.4826 x MAD), roi tru phuong sai Poisson ~ 1/trung binh (log-scale)
    adj = daily / daily.index.weekday.map(wd / wd.mean())
    level = adj.rolling(28, center=True, min_periods=14).median()
    resid = np.log(adj / level).dropna()
    robust_sd = 1.4826 * float(np.median(np.abs(resid - resid.median())))
    extra_var = max(robust_sd ** 2 - 1.0 / float(daily.mean()), 0.0)
    daily_noise_sd = float(np.sqrt(extra_var))
    naive_sd = float(np.log(daily / daily.index.weekday.map(wd)).std())

    freq = lines.groupby("item").qty.sum().sort_values(ascending=False)
    share = freq / freq.sum()
    top = freq.head(20)
    ranks = np.arange(1, len(top) + 1)
    zipf_s = float(-np.polyfit(np.log(ranks), np.log(top.values), 1)[0])

    hourly = tx.date_time.dt.hour.value_counts(normalize=True).sort_index()
    return {
        "source": "The Bread Basket (Edinburgh bakery), OpenML ID 43422, CC0",
        "period": [str(tx.date_time.min().date()), str(tx.date_time.max().date())],
        "n_transactions": int(len(tx)),
        "n_days": int(daily.size),
        "items_per_order_dist": {int(k): round(float(v), 3) for k, v in items_dist.items()},
        "qty_per_line_dist": {int(k): round(float(v), 3) for k, v in qty_dist.items()},
        "weekday_factor_mon_to_sun": [float(weekday_factor.get(i, np.nan)) for i in range(7)],
        "daily_noise_sd_log": round(daily_noise_sd, 3),
        "daily_noise_sd_log_naive": round(naive_sd, 3),
        "daily_noise_robust_sd_before_poisson": round(robust_sd, 3),
        "mean_transactions_per_day": round(float(daily.mean()), 1),
        "item_top1_share": round(float(share.iloc[0]), 3),
        "item_top5_share": round(float(share.head(5).sum()), 3),
        "item_zipf_exponent_top20": round(zipf_s, 3),
        "hourly_share": {int(k): round(float(v), 3) for k, v in hourly.items()},
    }


def current_assumptions():
    k, p = C.ITEMS_PER_ORDER
    q, qp = C.QTY_PER_LINE
    w = np.array(C.WEEKDAY_FACTOR)
    return {
        "items_per_order_dist": dict(zip(k, p)),
        "qty_per_line_dist": dict(zip(q, qp)),
        "weekday_factor_mon_to_sun": [round(float(x), 3) for x in w / w.mean()],
        "daily_noise_sd_log": C.DAILY_NOISE_SD,
    }


def main():
    bb = fit_bread_basket(load_bread_basket())
    report = {"bread_basket": bb, "current_simulator_assumptions": current_assumptions()}
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
