"""
Kham pha du lieu (EDA) tren TAP PHAT TRIEN: in cac so lieu dung o muc 4.4 (du lieu tho, tang Bronze va buoc
kiem tra cua Silver) va muc 4.7 (du lieu da lam sach, tang Gold) cua bao cao. Chi doc kho, khong doc ground_truth,
khong dung tap kiem tra.

  .venv/Scripts/python tools/kham_pha_du_lieu.py
"""
from pathlib import Path

import duckdb

DB = Path(__file__).resolve().parents[1] / "data" / "calibration" / "warehouse" / "fastfat.duckdb"
END = "date '2024-09-08'"   # 182 ngay danh gia


def main():
    c = duckdb.connect(str(DB), read_only=True)
    q = lambda s: c.sql(s).fetchall()

    def show(title, rows):
        print(f"{title}: {rows}")

    print("== DU LIEU THO")
    show("POS: so hoa don theo phien ban (so truong)", q(
        "select len(json_keys(payload)), count(*) from bronze.pos_receipts group by 1"))
    show("POS: trung so hoa don", q(
        "select count(*) - count(distinct json_extract_string(payload, '$.receipt_no')) from bronze.pos_receipts"))
    show("POS: dinh dang ngay", q(
        "select regexp_matches(json_extract_string(payload, '$.txn_time'), '^\\d{4}-') iso, count(*) "
        "from bronze.pos_receipts group by 1"))
    show("POS: so cach ghi ten mon / so ma mon", q(
        "select count(distinct json_extract_string(li, '$.name_on_receipt')), count(distinct json_extract_string(li, '$.sku')) "
        "from (select unnest(json_extract(payload, '$.items[*]')) li from bronze.pos_receipts)"))
    for k in ("void_reason", "loyalty_member_phone_masked", "discount_code", "total_paid", "table_number"):
        show(f"POS: % trong '{k}'", q(
            f"select round(100 * avg(case when coalesce(json_type(payload, '$.{k}'), 'NULL') = 'NULL' then 1 else 0 end), 1) "
            "from bronze.pos_receipts"))
    for k in ("kitchen_ready_at_utc", "rating", "review_text", "cancel_reason"):
        show(f"App: % trong '{k}'", q(
            f"select round(100 * avg(case when coalesce(json_type(payload, '$.{k}'), 'NULL') = 'NULL' then 1 else 0 end), 1) "
            "from bronze.app_orders"))
    show("App: trang thai", q("select json_extract_string(payload, '$.order_status'), count(*) from bronze.app_orders group by 1"))
    show("San: so ten/ma cua hang, so dong", q(
        "select (select count(distinct merchant_store_name) from bronze.grab_settlement), "
        "(select count(distinct ma_cua_hang) from bronze.shopee_settlement), (select count(*) from bronze.grab_settlement)"))
    show("Kho: loai dong theo mau", q(
        "select template, row_kind, count(*) from silver_work.base_inventory__receipts group by 1, 2 order by 1, 2"))
    show("Kho: so cach viet ten / so nguyen lieu", q(
        "select count(distinct raw_name), count(distinct ingredient_id) from silver_work.checked_inventory__receipts"))
    show("Kho: ti so so luong / trung vi, dong binh thuong (min, max) va dong bi cach ly (min)", q(
        "select min(quantity / median_qty) filter (where dq_issue is null), max(quantity / median_qty) filter (where dq_issue is null), "
        "min(quantity / median_qty) filter (where dq_issue is not null), count(*) filter (where dq_issue is not null) "
        "from silver_work.checked_inventory__receipts where median_qty > 0"))
    show("Kiem ke: so dong, o trong", q(
        "select count(*), sum(case when nullif(trim(ton_thuc_te), '') is null then 1 else 0 end) from bronze.stock_counts"))
    show("Cham cong: luot, nhan vien", q("select count(*), count(distinct employee_code) from bronze.timekeeping_punches"))
    show("Cham cong: khoang cach toi luot cung loai truoc (phut): max nhom < 5, min nhom >= 5, so luot < 5", q(
        "with g as (select date_diff('second', lag(event_at) over (partition by staff_id, event_type order by event_at), "
        "event_at) / 60.0 m from silver_work.base_timekeeping__punches) "
        "select round(max(m) filter (where m < 5), 2), round(min(m) filter (where m >= 5)), count(*) filter (where m < 5) from g"))

    print("== DU LIEU DA LAM SACH (Gold)")
    show("Don/ngay theo hang: p10, trung vi, p90", q(
        f"select store_class, round(quantile_cont(orders, 0.1)), round(median(orders)), round(quantile_cont(orders, 0.9)) "
        f"from gold.mart_branch_daily where date_day <= {END} group by 1 order by 1"))
    show("Gia tri don hoan thanh: trung binh, trung vi, do lech", q(
        f"select round(avg(net_sales)), median(net_sales), round(skewness(net_sales), 2) "
        f"from gold.fact_order where is_completed and date_day <= {END}"))
    show("Do lech doanh thu tuan so voi muc nen: sd, min, max", q(
        "select round(stddev(dev), 3), round(min(dev), 3), round(max(dev), 3) "
        "from gold.mart_kpi_vs_peers_weekly where kpi = 'net_sales' and dev is not null"))
    show("Thu ngan x tuan (>= 30 hoa don): so dong, % tuan khong huy, trung vi hoa don, trung vi so huy", q(
        f"select count(*), round(100 * avg(case when voids = 0 then 1 else 0 end), 1), median(receipts), median(voids) "
        f"from gold.mart_cashier_weekly where week_start <= {END} and receipts >= 30"))
    show("Diem danh gia san: so gia tri khac nhau, min, max", q(
        f"select count(distinct store_rating), min(store_rating), max(store_rating) "
        f"from gold.fact_marketplace_settlement where week_start <= {END}"))
    show("Chenh lech hoa hong: so dong, so dong bang 0, so dong lech > 0,5 diem %", q(
        f"select count(*), count(*) filter (where commission_rate_gap = 0), count(*) filter (where abs(commission_rate_gap) > 0.005) "
        f"from gold.fact_marketplace_settlement where week_start <= {END}"))
    show("Hao hut / dinh muc theo nhom (tuoi?): trung vi, p10, p90 (%)", q(
        f"select is_fresh, round(100 * median(variance_pct), 1), round(100 * quantile_cont(variance_pct, 0.1), 1), "
        f"round(100 * quantile_cont(variance_pct, 0.9), 1) from gold.mart_ingredient_avt "
        f"where period_end <= {END} and theory_qty > 0 group by 1"))
    show("Ton luc kiem ke / tieu hao dinh muc moi ngay (ngay)", q(
        f"select is_fresh, round(median(opening_qty / (theory_qty / period_days)), 1) from gold.mart_ingredient_avt "
        f"where period_end <= {END} and theory_qty > 0 group by 1"))
    show("Bep ca toi -> thoi gian chuan bi App, % don App cua hang huy (hang, so bep, so ngay)", q(
        f"select store_class, kitchen_evening, count(*), round(avg(app_avg_prep_min), 1), "
        f"round(100.0 * sum(app_store_cancels) / sum(app_orders_placed), 1) from gold.mart_branch_daily "
        f"where date_day <= {END} group by 1, 2 having count(*) >= 5 order by 1, 2"))
    c.close()


if __name__ == "__main__":
    main()
