"""
Bieu do so lieu cho bao cao (Chuong 5), ve bang matplotlib tu kho Gold va docs/results, nen tai lap duoc.
Ban do canh bao dung dung ham cua analytics/evaluate.py (doc dap an CHI de cham diem, nhu evaluate) va tu
kiem tra so canh bao khop ket qua da chot trong docs/results; lech thi dung lai, khong ve.

  .venv/Scripts/python docs/report/figures/charts.py            # ve tat ca
  .venv/Scripts/python docs/report/figures/charts.py c5_ban_do   # ve 1 hinh
"""
import sys
from pathlib import Path

import duckdb
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from analytics import config as C, detect, evaluate  # noqa: E402
from analytics.data import load_gold  # noqa: E402

RES = ROOT / "docs" / "results"
NAVY, TEAL, STEEL, SAND, RED, GRAY, LIGHT = "#1F3A5F", "#2F7F86", "#5B8DB8", "#C08A2E", "#B4232A", "#9AA5B1", "#D9DEE4"
TIER = {"A": NAVY, "B": TEAL, "C": SAND}
W_IN = 16 / 2.54                      # rong dung bang khung hinh trong bao cao (16 cm) -> co chu in dung nhu khai bao

plt.rcParams.update({
    "font.family": "Times New Roman", "font.size": 10, "axes.titlesize": 10.5, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.fontsize": 9, "legend.frameon": False, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#52606D", "axes.grid": True, "grid.color": "#E5E7EB", "grid.linewidth": 0.6,
    "axes.axisbelow": True, "figure.dpi": 100, "savefig.dpi": 300,
})


def vn(x, d=0):
    """So kieu Viet Nam: dau cham ngan cach nghin, dau phay thap phan."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def vn_axis(ax, axis="y", d=0, pct=False):
    f = (lambda v, _: vn(v * 100, d) + "%") if pct else (lambda v, _: vn(v, d))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(matplotlib.ticker.FuncFormatter(f))


def date_axis(ax, every=2):
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=every))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))


def shade(ax, start, end, label=None):
    ax.axvspan(pd.Timestamp(start), pd.Timestamp(end) + pd.Timedelta(days=1), color="#F4D9B0", alpha=0.7, lw=0, label=label)


def save(fig, name):
    fig.savefig(HERE / f"{name}.png", bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
    print("da ve", name)


def gold(profile, sql):
    con = duckdb.connect(str(ROOT / "data" / profile / "warehouse" / "fastfat.duckdb"), read_only=True)
    try:
        return con.sql(sql).df()
    finally:
        con.close()


# ---------------------------------------------------------------- 1. ban do canh bao va su co
def alert_map(profile):
    G = load_gold(profile)
    scores = detect.score_all(G)
    weeks = [w for w in detect.usable_weeks(G) if (G["mart_branch_weekly"].query("week_start == @w").n_days == 7).all()]
    alerts = evaluate.method_ours(G, scores, C.SCORE_ALERT)
    alerts = alerts[alerts.week_start.isin(weeks)]
    official = pd.read_csv(RES / f"{profile}_so_sanh.csv", encoding="utf-8-sig", index_col=0).iloc[0]
    assert len(alerts) == int(official.so_canh_bao), f"{profile}: {len(alerts)} canh bao, ket qua chot {official.so_canh_bao}"
    inc = evaluate.load_incidents(profile)
    labels = evaluate.label_weeks(weeks, inc)
    tiers = G["dim_branch"].set_index("branch_id").store_class
    return weeks, alerts, inc, labels, tiers


def c5_ban_do():
    fig, axes = plt.subplots(2, 1, figsize=(W_IN, 5.9), gridspec_kw={"hspace": 0.3})
    for ax, (profile, title) in zip(axes, [("calibration", "(a) Tập phát triển"), ("holdout", "(b) Tập kiểm tra")]):
        weeks, alerts, inc, labels, tiers = alert_map(profile)
        col = {w: i for i, w in enumerate(weeks)}
        ax.set_xlim(-0.5, len(weeks) - 0.5)
        ax.set_ylim(11.5, 0.5)
        ax.grid(False)
        for b in range(1, 12):
            for i in range(len(weeks)):
                ax.add_patch(plt.Rectangle((i - 0.5, b - 0.5), 1, 1, fc="#F3F4F6", ec="white", lw=1.2))
        for r in labels.itertuples():
            ax.add_patch(plt.Rectangle((col[r.week_start] - 0.5, r.branch_id - 0.5), 1, 1,
                                       fc="#EFC58C" if r.active else "#F8E6CC", ec="white", lw=1.2))
        ids = inc[inc.id.isin(labels.incident)].groupby("branch_id").id.agg(", ".join)
        for b, t in ids.items():
            ax.text(len(weeks) - 0.3, b, t, ha="left", va="center", fontsize=8.5, color="#7A4A0C")
        lab = labels.set_index(["branch_id", "week_start"])
        for a in alerts.itertuples():
            x, y = col[a.week_start], a.branch_id
            if (a.branch_id, a.week_start) in lab.index:
                true = lab.loc[(a.branch_id, a.week_start), "true_cause"]
                true = true.iloc[0] if isinstance(true, pd.Series) else true
                if a.pred_cause == true:
                    ax.plot(x, y, "o", ms=7.5, color=NAVY)
                else:
                    ax.plot(x, y, "o", ms=7.5, mfc="white", mec=NAVY, mew=1.6)
            else:
                ax.plot(x, y, "x", ms=7.5, color=RED, mew=2)
        ax.set_yticks(range(1, 12), [f"CN{b} · {tiers[b]}" for b in range(1, 12)])
        ax.set_xticks(range(0, len(weeks), 2), [weeks[i].strftime("%d/%m") for i in range(0, len(weeks), 2)])
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(title, pad=4)
    handles = [Patch(fc="#EFC58C", label="sự cố đang diễn ra"), Patch(fc="#F8E6CC", label="14 ngày sau sự cố"),
               Line2D([], [], ls="", marker="o", ms=7, color=NAVY, label="cảnh báo đúng nguyên nhân"),
               Line2D([], [], ls="", marker="o", ms=7, mfc="white", mec=NAVY, mew=1.5, label="cảnh báo đúng chỗ, khác nhãn"),
               Line2D([], [], ls="", marker="x", ms=7, color=RED, mew=2, label="báo động giả")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0), handlelength=1.4, columnspacing=1.2)
    save(fig, "c5_ban_do")


# ---------------------------------------------------------------- 2. tin hieu cua tung bo phat hien
def c5_tin_hieu():
    inc = evaluate.load_incidents("calibration").set_index("id")
    wk = gold("calibration", "select * from gold.mart_branch_weekly order by week_start")
    wk["week_start"] = pd.to_datetime(wk.week_start)
    G = load_gold("calibration")
    inv = detect.inventory_z(G)
    inv = inv[inv.group == "fresh_low"].copy()
    inv["period_end"] = pd.to_datetime(inv.period_end)
    cw = gold("calibration", "select * from gold.mart_cashier_weekly where branch_id = 8 order by week_start")
    cw["week_start"] = pd.to_datetime(cw.week_start)

    fig, axes = plt.subplots(2, 2, figsize=(W_IN, 4.7), gridspec_kw={"hspace": 0.5, "wspace": 0.32})

    def peers(ax, df, col, b, color, scale=1):
        for other, d in df[df.branch_id != b].groupby("branch_id"):
            ax.plot(d.week_start, d[col] * scale, color=LIGHT, lw=0.9)
        d = df[df.branch_id == b]
        ax.plot(d.week_start, d[col] * scale, color=color, lw=1.8)

    ax = axes[0, 0]
    r = inc.loc["S1"]
    shade(ax, r.start, r.end)
    peers(ax, wk, "grabfood_commission_gap", 4, NAVY, 100)
    ax.axhline(C.COMMISSION_TOLERANCE * 100, color=RED, ls="--", lw=1)
    ax.text(pd.Timestamp("2024-06-20"), C.COMMISSION_TOLERANCE * 100 + 0.3, "dung sai 0,5 điểm %", color=RED, fontsize=8.5)
    ax.set_title("(a) P1a · CN4: hoa hồng GrabFood")
    ax.set_ylabel("chênh lệch, điểm %")
    vn_axis(ax, d=0)

    ax = axes[0, 1]
    r = inc.loc["S2"]
    shade(ax, r.start, r.end)
    peers(ax, wk, "shopeefood_pos_coverage", 6, NAVY)
    d = wk[wk.branch_id == 6]
    ax.plot(d.week_start, d.grabfood_pos_coverage, color=TEAL, lw=1.8)
    ax.set_title("(b) P1b · CN6: độ phủ POS đơn sàn")
    ax.set_ylabel("độ phủ POS")
    ax.legend([Line2D([], [], color=NAVY, lw=1.8), Line2D([], [], color=TEAL, lw=1.8)], ["ShopeeFood", "GrabFood"],
              loc="lower left", fontsize=8.5)
    vn_axis(ax, d=0, pct=True)

    ax = axes[1, 0]
    r = inc.loc["S3"]
    shade(ax, r.start, r.end)
    for b, d in inv.groupby("branch_id"):
        if b != 7:
            ax.plot(d.period_end, d.var_pct * 100, color=LIGHT, lw=0.9, marker="o", ms=2)
    d = inv[inv.branch_id == 7]
    ax.plot(d.period_end, d.var_pct * 100, color=NAVY, lw=1.8, marker="o", ms=3.5)
    ax.set_title("(c) P2 · CN7: hao hụt hàng tươi")
    ax.set_ylabel("% tiêu hao định mức")
    vn_axis(ax, d=0)

    ax = axes[1, 1]
    r = inc.loc["S6"]
    shade(ax, r.start, r.end)
    for code, d in cw.groupby("staff_code"):
        if code != "NV0093" and d.receipts.sum() > 300:
            ax.plot(d.week_start, d.void_rate * 100, color=LIGHT, lw=0.9)
    d = cw[cw.staff_code == "NV0093"]
    ax.plot(d.week_start, d.void_rate * 100, color=NAVY, lw=1.8)
    ax.set_title("(d) P5 · CN8: hủy hóa đơn theo thu ngân")
    ax.set_ylabel("% hóa đơn bị hủy")
    vn_axis(ax, d=0)

    for ax in axes.flat:
        date_axis(ax, every=4)
        ax.set_xlim(pd.Timestamp("2024-03-11"), pd.Timestamp("2024-09-09"))
    handles = [Line2D([], [], color=NAVY, lw=1.8, label="chi nhánh hoặc thu ngân có sự cố"),
               Line2D([], [], color=LIGHT, lw=1.5, label="các chi nhánh, thu ngân khác"),
               Patch(fc="#F4D9B0", label="thời gian sự cố")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.05))
    save(fig, "c5_tin_hieu")


# ---------------------------------------------------------------- 3. truy vet CN2
def c5_truy_vet_cn2():
    r = evaluate.load_incidents("calibration").set_index("id").loc["S4"]
    k = gold("calibration", """select week_start, kpi, value, expected_value from gold.mart_kpi_vs_peers_weekly
                               where branch_id = 2 and kpi in ('net_sales', 'kitchen_evening') order by week_start""")
    k["week_start"] = pd.to_datetime(k.week_start)
    fig, axes = plt.subplots(2, 1, figsize=(W_IN, 3.7), sharex=True, gridspec_kw={"hspace": 0.38, "height_ratios": [1.3, 1]})
    for ax, (kpi, title, scale, unit) in zip(axes, [
            ("net_sales", "(a) Doanh thu thuần mỗi tuần", 1e-6, "triệu đồng"),
            ("kitchen_evening", "(b) Số ca bếp tối mỗi tuần", 1, "ca")]):
        d = k[k.kpi == kpi]
        shade(ax, r.start, r.end)
        ax.plot(d.week_start, d.expected_value * scale, color=GRAY, lw=1.6, ls="--", label="kỳ vọng")
        ax.plot(d.week_start, d.value * scale, color=NAVY, lw=1.8, marker="o", ms=3, label="thực tế")
        ax.set_title(title)
        ax.set_ylabel(unit)
        vn_axis(ax)
    axes[0].legend(loc="lower right", ncol=2)
    date_axis(axes[1], every=2)
    save(fig, "c5_truy_vet_cn2")


# ---------------------------------------------------------------- 4. do nhay theo nguong
def c5_nguong():
    d = pd.read_csv(RES / "calibration_do_nhay.csv", encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(W_IN, 2.5))
    for col, color, name, m in [("precision", STEEL, "Precision", "s"), ("recall_tuan", TEAL, "Recall theo tuần", "^"),
                                ("f1", NAVY, "F1", "o")]:
        ax.plot(d.nguong_diem, d[col], color=color, lw=1.8, marker=m, ms=5, label=name)
    ax.axvline(C.SCORE_ALERT, color=RED, ls="--", lw=1)
    ax.text(C.SCORE_ALERT + 0.05, 0.04, "ngưỡng chốt 3,5", color=RED, fontsize=9)
    tr = matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes)
    for x, s, fp in zip(d.nguong_diem, d.su_co_bat_duoc, d.bao_dong_gia):
        ax.text(x, 1.13, f"{s}", ha="center", fontsize=9, color=NAVY, transform=tr)
        ax.text(x, 1.04, f"{fp}", ha="center", fontsize=9, color=RED, transform=tr)
    ax.text(1.8, 1.13, "sự cố bắt được", ha="right", fontsize=9, color=NAVY, transform=tr)
    ax.text(1.8, 1.04, "báo động giả", ha="right", fontsize=9, color=RED, transform=tr)
    ax.set_ylim(0, 1.02)
    ax.set_xlim(1.85, 5.15)
    ax.set_xticks(d.nguong_diem, [vn(x, 1) for x in d.nguong_diem])
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    vn_axis(ax, d=1)
    ax.set_xlabel("ngưỡng điểm cảnh báo")
    ax.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.24))
    save(fig, "c5_nguong")


# ---------------------------------------------------------------- 5. luat so voi z (P1a keo dai)
def c5_luat_z():
    d = pd.read_csv(RES / "calibration_minh_hoa_luat_vs_z.csv", encoding="utf-8-sig", parse_dates=["week_start"])
    rule = np.where(d.value > C.COMMISSION_TOLERANCE, 6.0, 0.0)
    zsc = d.z.clip(0, 6)
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(W_IN, 2.5))
    ax.bar(x - 0.2, rule, 0.38, color=NAVY, label="luật đối soát hợp đồng")
    ax.bar(x + 0.2, zsc, 0.38, color=SAND, label="điểm z so với lịch sử 8 tuần")
    ax.axhline(C.SCORE_ALERT, color=RED, ls="--", lw=1, label="ngưỡng cảnh báo 3,5")
    ax.set_xticks(x, [w.strftime("%d/%m") for w in d.week_start], rotation=45, ha="right", rotation_mode="anchor", fontsize=8.5)
    ax.set_ylabel("điểm bằng chứng")
    ax.set_ylim(0, 7.2)
    ax.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.17))
    ax.grid(axis="x", visible=False)
    save(fig, "c5_luat_z")


# ---------------------------------------------------------------- 6. ma tran thuc don
def menu_matrix():
    m = gold("calibration", """
        select l.item_id, any_value(i.item_name) as item_name, sum(l.qty) as qty,
               sum(l.line_amount - l.cogs_standard) as margin
        from gold.fact_order_line l join gold.dim_menu_item i using (menu_item_sk)
        where l.is_revenue_line and l.date_day <= date '2024-09-08'
        group by l.item_id""")
    m["share"] = m.qty / m.qty.sum()
    m["unit_margin"] = m.margin / m.qty
    avg = m.margin.sum() / m.qty.sum()
    pop = 0.7 / len(m)
    m["group"] = np.select([(m.share >= pop) & (m.unit_margin >= avg), (m.share >= pop), (m.unit_margin >= avg)],
                           ["Ngôi sao", "Ngựa kéo", "Câu đố"], "Chó")
    return m, avg, pop


OFFSET = {"Ga Gion Mieng Don": ((-6, 7), "right"), "Nuoc Suoi": ((7, -4), "left"),
          "Combo Gia Dinh 4 Nguoi": ((7, -3), "left")}
NAMES = {"Ga Gion Mieng Don": "Gà giòn miếng đơn", "Combo Gia Dinh 4 Nguoi": "Combo gia đình 4 người",
         "Pepsi Lon": "Pepsi lon", "Ga Gion Combo 2 Mieng": "Gà giòn combo 2 miếng",
         "Ga Gion Combo 4 Mieng": "Gà giòn combo 4 miếng", "Nuoc Suoi": "Nước suối"}


def c5_thuc_don():
    m, avg, pop = menu_matrix()
    print(m.groupby("group").agg(n=("item_id", "size"), qty=("share", "sum")).assign(
        margin=m.groupby("group").margin.sum() / m.margin.sum()), "\nlai gop binh quan", round(avg))
    fig, ax = plt.subplots(figsize=(W_IN, 3.3))
    color = {"Ngôi sao": NAVY, "Ngựa kéo": TEAL, "Câu đố": SAND, "Chó": GRAY}
    for g, d in m.groupby("group"):
        ax.scatter(d.share * 100, d.unit_margin / 1000, s=34, color=color[g], label=f"{g} ({len(d)} món)", zorder=3)
    ax.axvline(pop * 100, color="#52606D", lw=0.9, ls="--")
    ax.axhline(avg / 1000, color="#52606D", lw=0.9, ls="--")
    for r in m.itertuples():
        if r.item_name in NAMES:
            off, ha = OFFSET.get(r.item_name, ((5, 3), "left"))
            ax.annotate(NAMES[r.item_name], (r.share * 100, r.unit_margin / 1000), xytext=off, ha=ha,
                        textcoords="offset points", fontsize=8.5, color="#3E4C59")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: vn(v, 1 if v < 1 else 0) + "%"))
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xticks([0.3, 1, 3, 10, 25])
    ax.set_xlabel("tỷ trọng số lượng bán (thang log); đường đứng: 70% mức bình quân 1/28")
    ax.set_ylabel("lãi gộp mỗi phần, nghìn đồng")
    ax.set_xlim(0.28, 32)
    ax.set_ylim(0, 195)
    ax.text(0.3, avg / 1000 + 3, f"bình quân {vn(avg / 1000, 1)}", fontsize=8.5, color="#52606D")
    ax.legend(loc="upper center", ncol=4, bbox_to_anchor=(0.5, -0.17), fontsize=9)
    save(fig, "c5_thuc_don")


# ---------------------------------------------------------------- 7. Labor% theo hang chi nhanh
def c5_nhan_cong():
    d = gold("calibration", """select branch_id, store_class, week_start, labor_pct, orders_per_labor_hour
                               from gold.mart_branch_weekly where n_days = 7""")
    fig, ax = plt.subplots(figsize=(W_IN, 2.5))
    for t, g in d.groupby("store_class"):
        ax.scatter(g.orders_per_labor_hour, g.labor_pct * 100, s=12, alpha=0.75, color=TIER[t], label=f"hạng {t}", lw=0)
    ax.set_xlabel("số đơn mỗi giờ công")
    ax.set_ylabel("Labor%")
    vn_axis(ax, "x", d=1)
    vn_axis(ax, d=0)
    ax.legend(loc="upper right", markerscale=1.8)
    save(fig, "c5_nhan_cong")


# ---------------------------------------------------------------- 8. so voi hai phuong an co so
def c5_so_sanh():
    methods = [("Đề xuất", NAVY), ("Chỉ theo dõi doanh thu", GRAY), ("Isolation Forest", SAND)]
    metrics = [("precision", "Precision"), ("recall_tuan", "Recall theo tuần"), ("f1", "F1")]
    fig, axes = plt.subplots(1, 2, figsize=(W_IN, 2.5), sharey=True, gridspec_kw={"wspace": 0.08})
    for ax, (profile, title) in zip(axes, [("calibration", "(a) Tập phát triển"), ("holdout", "(b) Tập kiểm tra")]):
        d = pd.read_csv(RES / f"{profile}_so_sanh.csv", encoding="utf-8-sig", index_col=0)
        x = np.arange(len(metrics))
        for k, (name, color) in enumerate(methods):
            vals = [d.iloc[k][m] for m, _ in metrics]
            bars = ax.bar(x + (k - 1) * 0.26, vals, 0.24, color=color, label=name)
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.02, vn(v, 2), ha="center", fontsize=7.5)
        ax.set_xticks(x, [n for _, n in metrics])
        ax.set_ylim(0, 1.05)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        vn_axis(ax, d=1)
        ax.grid(axis="x", visible=False)
        ax.set_title(title, pad=4)
    axes[0].legend(loc="upper center", ncol=3, bbox_to_anchor=(1.04, -0.13))
    save(fig, "c5_so_sanh")


# ---------------------------------------------------------------- 9. do nhay theo cach tinh muc ky vong
def c5_do_nhay():
    d = pd.read_csv(RES / "calibration_do_nhay_phuong_phap.csv", encoding="utf-8-sig")
    names = ["Đề xuất", "So với toàn chuỗi", "Chỉ lịch sử của chi nhánh", "Cửa sổ 4 tuần", "Cửa sổ 12 tuần",
             "Trung bình và độ lệch chuẩn", "Bỏ sàn độ dao động"]
    assert len(d) == len(names)
    # ba bao dong gia do bang chung kho va doi soat giong nhau o moi phuong an (muc 5.5.3)
    fixed = 3
    assert (d.bao_dong_gia >= fixed).all()
    y = np.arange(len(d))[::-1]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W_IN, 2.7), sharey=True, gridspec_kw={"wspace": 0.06})
    colors = [NAVY if i == 0 else STEEL for i in range(len(d))]
    a1.barh(y, d.f1, color=colors, height=0.6)
    for yy, v in zip(y, d.f1):
        a1.text(v + 0.012, yy, vn(v, 2), va="center", fontsize=8,
                bbox=dict(fc="white", ec="none", pad=0.6))
    a1.axvline(d.f1.iloc[0], color=NAVY, ls=":", lw=1, zorder=1)
    a1.set_xlim(0, 1)
    vn_axis(a1, "x", d=1)
    a1.set_yticks(y, names)
    a1.set_title("(a) F1", pad=4)
    a2.barh(y, d.bao_dong_gia - fixed, color=RED, height=0.6, label="do lệch doanh thu, nhân sự")
    a2.barh(y, [fixed] * len(d), left=d.bao_dong_gia - fixed, color=LIGHT, height=0.6, label="do bằng chứng kho, đối soát")
    for yy, v in zip(y, d.bao_dong_gia):
        a2.text(v + 0.2, yy, str(v), va="center", fontsize=8)
    a2.set_xlim(0, 17)
    a2.set_title("(b) Số báo động giả", pad=4)
    for ax in (a1, a2):
        ax.grid(axis="y", visible=False)
        ax.tick_params(axis="y", length=0)
    a2.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.2, -0.1))
    save(fig, "c5_do_nhay")


# ---------------------------------------------------------------- 10. diem cua nguyen nhan dung o tung su co
def c5_diem_su_co():
    rows = []
    for profile in ("calibration", "holdout"):
        G = load_gold(profile)
        scores = detect.score_all(G)
        weeks = set(detect.usable_weeks(G))
        done = pd.read_csv(RES / f"{profile}_theo_su_co.csv", encoding="utf-8-sig").set_index("Sự cố")
        for r in evaluate.load_incidents(profile).itertuples():
            last = r.end + pd.Timedelta(days=evaluate.GRACE_DAYS)
            s = scores[(scores.branch_id == r.branch_id) & (scores.cause == r.cause) & scores.week_start.isin(weeks)
                       & (scores.week_start <= last) & (scores.week_start + pd.Timedelta(days=6) >= r.start)]
            rows.append((r.id, r.cause, s.score.max() if len(s) else 0.0, done.loc[r.id, "Bắt được"] == "có",
                         str(done.loc[r.id, "Đúng nguyên nhân"]) == "True"))
    d = pd.DataFrame(rows, columns=["id", "cause", "score", "caught", "right"]).set_index("id")
    # tu kiem: khop cac diem da bao cao o Bang 5.6
    for k, v in {"S5": 2.8, "H4": 2.82, "H6": 3.44}.items():
        assert abs(d.loc[k, "score"] - v) < 0.01, (k, d.loc[k, "score"])
    x = np.r_[np.arange(6), np.arange(7, 13)]
    color = [NAVY if c and r else (SAND if c else GRAY) for c, r in zip(d.caught, d.right)]
    fig, ax = plt.subplots(figsize=(W_IN, 2.4))
    ax.bar(x, d.score, 0.62, color=color)
    for xx, v in zip(x, d.score):
        ax.text(xx, v + 0.12, vn(v, 2), ha="center", fontsize=8, bbox=dict(fc="white", ec="none", pad=0.5))
    ax.axhline(C.SCORE_ALERT, color=RED, ls="--", lw=1)
    ax.axhline(2.0, color=GRAY, ls=":", lw=1)
    ax.set_xticks(x, [f"{i}\n{c}" for i, c in zip(d.index, d.cause)])
    ax.set_ylim(0, 6.6)
    ax.set_ylabel("điểm bằng chứng")
    ax.grid(axis="x", visible=False)
    tr = matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes)
    ax.text(2.5, 1.02, "tập phát triển", ha="center", fontsize=9, transform=tr)
    ax.text(9.5, 1.02, "tập kiểm tra", ha="center", fontsize=9, transform=tr)
    handles = [Patch(fc=NAVY, label="bắt được, đúng nguyên nhân"), Patch(fc=SAND, label="bắt được, nhãn chưa xác định"),
               Patch(fc=GRAY, label="bỏ sót"), Line2D([], [], color=RED, ls="--", lw=1, label="ngưỡng cảnh báo 3,5"),
               Line2D([], [], color=GRAY, ls=":", lw=1, label="mức theo dõi 2")]
    ax.legend(handles=handles, loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.27))
    save(fig, "c5_diem_su_co")


ALL = {f.__name__: f for f in (c5_ban_do, c5_tin_hieu, c5_truy_vet_cn2, c5_nguong, c5_luat_z, c5_thuc_don, c5_nhan_cong,
                               c5_so_sanh, c5_do_nhay, c5_diem_su_co)}

if __name__ == "__main__":
    for name in sys.argv[1:] or ALL:
        ALL[name]()
