-- Gold mart: TIEU HAO THUC TE so voi DINH MUC (Actual vs Theoretical, AvT)
-- theo CHI NHANH x NGUYEN LIEU x KY KIEM KE (giua 2 lan dem lien tiep co so lieu).
--   thuc te (actual)    = ton dau ky (lan dem truoc) + nhap trong ky - ton cuoi ky (lan dem nay)
--   dinh muc (theory)   = so mon bep da lam (don hoan thanh + don hoan tien) x cong thuc;
--                         combo duoc tach thanh mon thanh phan truoc khi nhan cong thuc
--   variance            = actual - theory  (> 0: hut nhieu hon dinh muc -> hao hut / that thoat)
-- Gia dinh: kiem ke cuoi ngay dem -> ky = (ngay dem truoc, ngay dem nay].
-- Lan dem bo trong (is_not_counted) bi bo qua, ky noi dai den lan dem co so lieu ke tiep.
with prepared as (
    select branch_id, date_day, item_id, sum(qty) as qty
    from {{ ref('fact_order_line') }}
    where is_prepared
    group by all
),

exploded as (
    select p.branch_id, p.date_day, coalesce(cc.component_item_id, p.item_id) as item_id,
           p.qty * coalesce(cc.quantity, 1) as qty
    from prepared p
    left join {{ ref('stg_master__combo_components') }} cc on cc.combo_item_id = p.item_id
),

theory_daily as (
    select e.branch_id, e.date_day, r.ingredient_id, sum(e.qty * r.qty_per_unit) as theory_qty
    from exploded e
    join {{ ref('stg_master__recipes') }} r using (item_id)
    group by all
),

counts as (
    select
        branch_id,
        ingredient_id,
        date_day                                                                  as count_date,
        counted_qty                                                               as closing_qty,
        lag(date_day) over (partition by branch_id, ingredient_id order by date_day) as prev_count_date,
        lag(counted_qty) over (partition by branch_id, ingredient_id order by date_day) as opening_qty
    from {{ ref('fact_stock_count') }}
    where not is_not_counted and counted_qty is not null
),

periods as (
    select * from counts where prev_count_date is not null
),

receipts as (
    select p.branch_id, p.ingredient_id, p.count_date, sum(r.quantity) as received_qty
    from periods p
    join {{ ref('fact_inventory_receipt') }} r
      on r.branch_id = p.branch_id
     and r.ingredient_id = p.ingredient_id
     and r.date_day > p.prev_count_date and r.date_day <= p.count_date
    group by all
),

theory as (
    select p.branch_id, p.ingredient_id, p.count_date, sum(t.theory_qty) as theory_qty
    from periods p
    join theory_daily t
      on t.branch_id = p.branch_id
     and t.ingredient_id = p.ingredient_id
     and t.date_day > p.prev_count_date and t.date_day <= p.count_date
    group by all
)

select
    p.branch_id,
    b.store_class,
    p.ingredient_id,
    i.ingredient_name,
    i.is_fresh,
    i.unit,
    p.prev_count_date                                                        as period_start_excl,
    p.count_date                                                             as period_end,
    datediff('day', p.prev_count_date, p.count_date)                         as period_days,
    p.opening_qty,
    coalesce(r.received_qty, 0)                                              as received_qty,
    p.closing_qty,
    p.opening_qty + coalesce(r.received_qty, 0) - p.closing_qty              as actual_qty,
    coalesce(t.theory_qty, 0)                                                as theory_qty,
    p.opening_qty + coalesce(r.received_qty, 0) - p.closing_qty
        - coalesce(t.theory_qty, 0)                                          as variance_qty,
    (p.opening_qty + coalesce(r.received_qty, 0) - p.closing_qty)
        / nullif(t.theory_qty, 0) - 1                                        as variance_pct,
    round((p.opening_qty + coalesce(r.received_qty, 0) - p.closing_qty
        - coalesce(t.theory_qty, 0)) * i.standard_unit_cost)                 as variance_value
from periods p
left join receipts r using (branch_id, ingredient_id, count_date)
left join theory t using (branch_id, ingredient_id, count_date)
left join {{ ref('dim_ingredient') }} i using (ingredient_id)
left join {{ ref('dim_branch') }} b using (branch_id)
