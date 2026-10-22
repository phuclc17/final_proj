"""Bo phat hien: quet bo chi so giam sat va cham diem gia thuyet nguyen nhan cho MOI chi nhanh x tuan.
Chi dung thong tin co tai thoi diem danh gia (lich su qua khu, cac chi nhanh khac cung ky) - khong nhin tuong lai.

    from analytics.data import load_gold
    from analytics import detect
    G = load_gold("calibration")
    scores = detect.score_all(G)           # 1 dong / chi nhanh / tuan / gia thuyet
    alerts = detect.alert_table(G, scores)  # 1 dong / chi nhanh / tuan
"""
import math
from statistics import NormalDist

import numpy as np
import pandas as pd

from . import config as C


# ------------------------------------------------------------------ tien ich
def evidence(z, direction):
    """Muc vuot theo dung chieu bat thuong, cat trong [0, 6]."""
    return np.nan if pd.isna(z) else float(np.clip(direction * z, 0, 6))


def poisson_sf(k, lam):
    """P(X >= k) voi X ~ Poisson(lam)."""
    if k <= 0:
        return 1.0
    term, cdf = math.exp(-lam), 0.0
    for i in range(k):
        cdf += term
        term *= lam / (i + 1)
    return max(1.0 - cdf, 1e-300)


def p_to_z(p):
    """Doi xac suat duoi tren sang z (tinh tu phia p nho de khong mat do chinh xac khi p rat nho)."""
    return -NormalDist().inv_cdf(max(p, 1e-300)) if p < 0.5 else 0.0


def usable_weeks(G):
    kv = G["mart_kpi_vs_peers_weekly"]
    return sorted(kv[kv.baseline_n >= C.MIN_BASELINE_WEEKS].week_start.unique())


def z_wide(G):
    """Bang rong: (chi nhanh, tuan) x KPI -> z."""
    kv = G["mart_kpi_vs_peers_weekly"]
    kv = kv[kv.baseline_n >= C.MIN_BASELINE_WEEKS]
    return kv.pivot_table(index=["branch_id", "week_start"], columns="kpi", values="z")


# ------------------------------------------------------------------ bo chi so giam sat
def scan_indicators(G, z_alert=C.Z_ALERT):
    """Cac chi so vuot nguong (theo dung chieu bat thuong) - 'bo thong so quan sat chung'."""
    kv = G["mart_kpi_vs_peers_weekly"]
    meta = pd.DataFrame(C.INDICATORS, columns=["kpi", "label", "group", "direction"])
    d = kv[kv.baseline_n >= C.MIN_BASELINE_WEEKS].merge(meta, on="kpi")
    signed = np.where(d.direction == 0, d.z.abs(), d.z * d.direction)
    d = d.assign(severity=signed)
    return d[d.severity >= z_alert].sort_values("severity", ascending=False)


# ------------------------------------------------------------------ bang chung tu kho (P2, P4)
def inventory_z(G):
    """z hao hut theo nhom nguyen lieu cho moi chi nhanh x ky kiem ke.
    - Hao hut chia cho luong ban THUONG NGAY cua chinh chi nhanh (trung vi cac ky truoc), khong chia cho luong
      ban ky nay: ky ban it thi phan hao hut co dinh (hang het han) chiem ty le lon hon, de hieu nham la that thoat.
    - So cat ngang voi cac chi nhanh khac CUNG KY (co ngay tai thoi diem kiem ke, khong nhin tuong lai).
      Khong dung muc nen rieng cua chi nhanh: chi ~12 ky / nua nam, vai ky dau nhieu do sai so dem keo lech nen.
    - Do dao dong = MAD cat ngang trong ky, san 0,5 diem %.
    Chon tren tap phat trien: 2 su co kho deu z > 3, ngoai su co con 1 ky vuot 3 (hang tuoi)."""
    avt = G["mart_ingredient_avt"].copy()
    cost = G["dim_ingredient"].set_index("ingredient_id").standard_unit_cost
    hv = set(cost[cost >= C.HIGH_VALUE_COST].index)
    avt["group"] = np.where(avt.ingredient_id.isin(hv), "high_value", np.where(avt.is_fresh, "fresh_low", "dry"))
    # quy ve moi ngay theo ky cua TUNG nguyen lieu (nguyen lieu bo trong 1 lan dem co ky dai gap doi)
    days = avt.period_days.clip(lower=1)
    avt["var_per_day"] = avt.variance_value / days
    avt["theory_per_day"] = avt.theory_qty * avt.ingredient_id.map(cost) / days
    g = (avt.groupby(["branch_id", "period_end", "group"], as_index=False)
         .agg(var_per_day=("var_per_day", "sum"), theory_per_day=("theory_per_day", "sum"),
              var_value=("variance_value", "sum"), period_start_excl=("period_start_excl", "max")))
    g = g.sort_values("period_end")
    typical = (g.groupby(["branch_id", "group"]).theory_per_day
               .transform(lambda s: s.shift(1).expanding(min_periods=1).median()))
    g["var_pct"] = g.var_per_day / typical.fillna(g.theory_per_day)
    by = g.groupby(["period_end", "group"]).var_pct
    g["peer_median"] = by.transform("median")
    mad = by.transform(lambda s: (s - s.median()).abs().median() * 1.4826)
    g["z"] = (g.var_pct - g.peer_median) / mad.clip(lower=0.005)
    return g


def inventory_for_weeks(G, inv):
    """Gan moi tuan voi ky kiem ke bao phu ngay cuoi tuan (Chu nhat)."""
    weeks = pd.DataFrame({"week_start": usable_weeks(G)})
    weeks["week_end"] = weeks.week_start + pd.Timedelta(days=6)
    # ky = (lan dem lien truoc, lan dem nay]; nguyen lieu bo trong 1 lan dem co ky dai hon -> lay ky ngan nhat
    per = inv.groupby(["branch_id", "period_end"], as_index=False).period_start_excl.max()
    m = weeks.merge(per, how="cross")
    m = m[(m.period_start_excl < m.week_end) & (m.period_end >= m.week_end)]
    piv = inv.pivot_table(index=["branch_id", "period_end"], columns="group", values="z").reset_index()
    return m.merge(piv, on=["branch_id", "period_end"], how="left")


# ------------------------------------------------------------------ bang chung doi soat san (P1b)
def marketplace_gap_z(G):
    """San noi bat nhat moi chi nhanh x tuan (dung de cham diem P1b)."""
    d = marketplace_gap_all(G)
    return d.sort_values("mkt_z", ascending=False).groupby(["branch_id", "week_start"]).head(1)


def marketplace_gap_all(G):
    """So don san bao hoan thanh nhung khong co tren POS, kiem dinh Poisson so voi ty le thieu thuong ngay
    cua chinh chi nhanh (trung vi cac tuan truoc); hieu chinh Bonferroni cho 2 san. Moi san mot dong."""
    wk = G["mart_branch_weekly"].sort_values("week_start")
    rows = []
    for p in ("grabfood", "shopeefood"):
        d = wk[["branch_id", "week_start", f"{p}_settled_orders", f"orders_{p}", f"{p}_settled_gross"]].copy()
        d.columns = ["branch_id", "week_start", "settled", "pos", "settled_gross"]
        d = d.dropna(subset=["settled", "pos"])
        d["missing"] = (d.settled - d.pos).clip(lower=0)
        d["rate"] = d.missing / d.settled.where(d.settled > 0)
        d["p0"] = d.groupby("branch_id").rate.transform(lambda s: s.shift(1).expanding(min_periods=4).median())
        d["p0"] = d.p0.fillna(d.groupby("week_start").rate.transform("median")).clip(lower=0.01)
        for r in d.itertuples():
            p_adj = min(1.0, poisson_sf(int(r.missing), r.settled * r.p0) * 2)
            z = p_to_z(p_adj)
            rows.append((r.branch_id, r.week_start, p, z,
                         f"{p}: sàn báo {int(r.settled)} đơn, POS ghi {int(r.pos)}, thiếu {int(r.missing)} "
                         f"(thường thiếu {r.p0:.1%})", int(r.settled), int(r.missing), r.p0, r.settled_gross))
    # cac cot sau mkt_note chi de phan khuyen nghi uoc tinh anh huong, khong tham gia cham diem
    return pd.DataFrame(rows, columns=["branch_id", "week_start", "platform", "mkt_z", "mkt_note",
                                       "settled", "missing", "normal_miss_rate", "settled_gross"])


# ------------------------------------------------------------------ bang chung tu thu ngan (P5)
def cashier_z(G):
    """Thu ngan noi bat nhat moi chi nhanh x tuan: duoi Poisson cua so hoa don huy/hoan so voi ty le cua cac
    thu ngan khac, hieu chinh Bonferroni theo so phep thu trong tuan, doi ra z."""
    cw = G["mart_cashier_weekly"]
    cw = cw[cw.receipts >= C.MIN_CASHIER_RECEIPTS]
    rows = []
    for (b, w), grp in cw.groupby(["branch_id", "week_start"]):
        m, best = 3 * len(grp), (0.0, "", None, None, 0, 0, 0.0, 0.0)
        for r in grp.itertuples():
            for cnt, p_other, what, amount in ((r.voids, r.others_void_rate, "hủy", r.void_amount),
                                               (r.refunds, r.others_refund_rate, "hoàn", r.refund_amount),
                                               (r.discounted, r.others_discount_rate, "giảm giá", r.discount_amount)):
                p0 = max(p_other if pd.notna(p_other) else 0.0, C.CASHIER_RATE_FLOOR)
                p_adj = min(1.0, poisson_sf(int(cnt), r.receipts * p0) * m)
                z = p_to_z(p_adj)
                if z > best[0]:
                    best = (z, f"{r.staff_code}: {cnt}/{r.receipts} hóa đơn bị {what} ({cnt / r.receipts:.1%}), "
                               f"thu ngân khác {p_other:.1%}", r.staff_code, what, int(cnt), int(r.receipts), p0, amount)
        rows.append((b, w, *best))
    # cac cot sau cashier_note chi de phan khuyen nghi, khong tham gia cham diem
    return pd.DataFrame(rows, columns=["branch_id", "week_start", "cashier_z", "cashier_note", "staff_code", "kind",
                                       "count", "receipts", "expected_rate", "amount"])


# ------------------------------------------------------------------ cham diem gia thuyet
def score_all(G):
    Z = z_wide(G)
    wk = G["mart_branch_weekly"].set_index(["branch_id", "week_start"])
    inv = inventory_for_weeks(G, inventory_z(G)).set_index(["branch_id", "week_start"])
    cash = cashier_z(G).set_index(["branch_id", "week_start"])
    mkt = marketplace_gap_z(G).set_index(["branch_id", "week_start"])
    out = []
    for key, zrow in Z.iterrows():
        def z(k):
            return zrow.get(k, np.nan)

        res = {}
        for code, (_, agg, sig) in C.FINGERPRINTS.items():
            evs = [e for e in (evidence(z(k), s) for k, s in sig) if pd.notna(e)]
            sc = (np.mean(evs) if agg == "mean" else max(evs)) if evs else 0.0
            notes = [f"{C.KPI_LABEL.get(k, k)} z={z(k):+.1f}" for k, s in sig if pd.notna(z(k)) and s * z(k) >= C.Z_WATCH]
            res[code] = [sc, notes]
        # P5: gian lan gan voi nguoi thuc hien -> diem lay tu kiem dinh tung thu ngan; ty le cap chi nhanh
        # (nhieu o chi nhanh nho) chi la bang chung phu.
        cz, cnote = cash.loc[key, ["cashier_z", "cashier_note"]] if key in cash.index else (0.0, "")
        res["P5"][0] = evidence(cz, 1)
        if cz >= C.Z_WATCH:
            res["P5"][1].insert(0, cnote)
        # P1b: kiem dinh so don thieu tren POS (on dinh hon ty le o chi nhanh it don san)
        mz, mnote = mkt.loc[key, ["mkt_z", "mkt_note"]] if key in mkt.index else (0.0, "")
        res["P1b"][0] = evidence(mz, 1)
        if mz >= C.Z_WATCH:
            res["P1b"][1].insert(0, mnote)

        w = wk.loc[key] if key in wk.index else None
        bad = {}
        if w is not None:
            for p in ("grabfood", "shopeefood"):
                g = w.get(f"{p}_commission_gap")
                if pd.notna(g) and g > C.COMMISSION_TOLERANCE:
                    bad[p] = (g, w.get(f"{p}_commission_overcharge"))
        res["P1a"] = [6.0 if bad else 0.0,
                      [f"{p} lệch {g * 100:+.1f} điểm %, thu thừa {v:,.0f} đ" for p, (g, v) in bad.items()]]

        zf = inv.loc[key, "fresh_low"] if key in inv.index else np.nan
        zh = inv.loc[key, "high_value"] if key in inv.index else np.nan
        res["P2"] = [evidence(zf, 1) if pd.notna(zf) else 0.0,
                     [f"hàng tươi giá thấp z={zf:+.1f}, giá trị cao z={zh:+.1f}"] if pd.notna(zf) else []]
        p4 = evidence(zh, 1) if pd.notna(zh) else 0.0
        if pd.notna(zf) and zf >= C.Z_WATCH:
            p4 *= 0.5   # hang tuoi re cung vuot -> giong hao hut hon la that thoat
        if res["P1b"][0] >= C.SCORE_ALERT:
            p4 *= 0.5   # don ban khong vao POS -> nguyen lieu bi dung ma khong co doanh so doi ung
        res["P4"] = [p4, [f"giá trị cao z={zh:+.1f}, hàng tươi giá thấp z={zf:+.1f}"] if pd.notna(zh) else []]

        zn = z("net_sales")
        res["BT"] = [float(np.clip(C.Z_ALERT - abs(zn), 0, C.Z_ALERT)) if pd.notna(zn) else 0.0,
                     [f"doanh thu lệch kỳ vọng z={zn:+.1f}"] if pd.notna(zn) else []]
        for code, (sc, notes) in res.items():
            out.append((*key, code, C.CAUSE_NAMES[code], round(float(sc), 2), "; ".join(notes)))
    return pd.DataFrame(out, columns=["branch_id", "week_start", "cause", "cause_name", "score", "evidence"])


def alert_table(G, scores, score_alert=C.SCORE_ALERT, z_alert=C.Z_ALERT):
    """1 dong / chi nhanh / tuan: gia thuyet manh nhat, chenh lech doanh thu, so chi so vuot nguong, muc canh bao."""
    inc = scores[scores.cause != "BT"].sort_values("score", ascending=False)
    top = inc.groupby(["branch_id", "week_start"]).head(1).set_index(["branch_id", "week_start"])
    second = inc.groupby(["branch_id", "week_start"]).nth(1).set_index(["branch_id", "week_start"])
    kv = G["mart_kpi_vs_peers_weekly"]
    ns = kv[kv.kpi == "net_sales"].set_index(["branch_id", "week_start"])[["value", "expected_value", "gap_vs_expected", "z"]]
    n_breach = scan_indicators(G, z_alert).groupby(["branch_id", "week_start"]).size().rename("n_breaches")
    a = (top[["cause", "cause_name", "score", "evidence"]]
         .join(second[["cause", "score"]].rename(columns={"cause": "cause_2", "score": "score_2"}))
         .join(ns).join(n_breach).reset_index())
    a["n_breaches"] = a.n_breaches.fillna(0).astype(int)
    a["level"] = np.select(
        [(a.score >= score_alert) | (a.z.abs() >= z_alert), (a.score >= C.Z_WATCH) | (a.z.abs() >= C.Z_WATCH)],
        ["Cảnh báo", "Theo dõi"], "Bình thường")
    # canh bao chi vi doanh thu lech ma khong gia thuyet nao du bang chung -> ghi ro "chua xac dinh", khong gan bua
    unknown = a.score < score_alert
    a.loc[unknown, "cause"] = "?"
    a.loc[unknown, "cause_name"] = "Chưa xác định nguyên nhân"
    # du lieu nguon chua du trong tuan (tep thieu, tep rong, tep bi tu choi) lam chi so lech gia tao: thieu POS mot ngay
    # thi doanh thu thap, don san "bien mat" khoi POS (giong P1b), luong ban thap lam hao hut so dinh muc cao (giong P2,
    # P4); thieu cham cong thi so ca bep thap (giong P3). Gia thuyet dua tren nguon bi thieu -> khong ket luan, ha muc
    # theo doi kem ghi chu; khi tep duoc gui bo sung, luot chay sau tu danh gia lai.
    d = G["mart_branch_daily"]
    days = (d.assign(pos=d.pos_receipts_walkin.fillna(0) > 0, tk=d.shifts.fillna(0) > 0)
            .groupby(["branch_id", "week_start"])[["pos", "tk"]].sum().reset_index())
    m = a[["branch_id", "week_start"]].merge(days, how="left", on=["branch_id", "week_start"]).fillna(0)
    pos_gap, tk_gap = m.pos.to_numpy() < 7, m.tk.to_numpy() < 7
    needs = {"?": pos_gap, "P1b": pos_gap, "P2": pos_gap, "P4": pos_gap, "P3": tk_gap}
    gap = np.zeros(len(a), dtype=bool)
    for code, g in needs.items():
        gap |= (a.cause.to_numpy() == code) & g
    a.loc[gap, "cause_name"] = a.loc[gap, "cause_name"] + " (thiếu dữ liệu nguồn trong tuần, chưa kết luận)"
    a.loc[gap & (a.level == "Cảnh báo"), "level"] = "Theo dõi"
    # nhieu chi nhanh cung thieu (API nguon sap, mat mang dien rong): trung vi nhom cung hang bi keo lech, chi nhanh du
    # du lieu cung trong nhu bat thuong -> gia thuyet dua tren so sanh voi chi nhanh khac khong ket luan trong tuan do.
    # "Thieu" o day tinh so voi chi nhanh day du nhat cung tuan (tuan dau, tuan cuoi khong tron 7 ngay khong bi tinh)
    full = days.groupby("week_start")[["pos", "tk"]].transform("max")
    days["short"] = (days.pos < full.pos) | (days.tk < full.tk)
    broken = days.groupby("week_start").short.mean() >= 1 / 3
    peer = (a.week_start.map(broken).fillna(False).to_numpy().astype(bool) & ~gap
            & np.isin(a.cause.to_numpy(), ["?", "P2", "P3", "P4"]))
    a.loc[peer, "cause_name"] = (a.loc[peer, "cause_name"]
                                 + " (nhiều chi nhánh thiếu dữ liệu nguồn trong tuần, so sánh giữa chi nhánh chưa tin cậy)")
    a.loc[peer & (a.level == "Cảnh báo"), "level"] = "Theo dõi"
    b = G["dim_branch"].set_index("branch_id")
    a["branch_name"] = a.branch_id.map(b.branch_name)
    a["store_class"] = a.branch_id.map(b.store_class)
    return a.sort_values(["week_start", "score"], ascending=[False, False])
