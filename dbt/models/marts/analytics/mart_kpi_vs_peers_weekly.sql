-- Gold mart: moi KPI cua CHI NHANH x TUAN dat canh MUC KY VONG -> dau vao cay KPI truy vet.
-- Muc ky vong lay tu 2 nguon, de loai bien dong chung (le, mua, mua vu, doi gia) ra khoi tin hieu:
--   1) nhom chi nhanh cung hang (store_class), loai chinh chi nhanh do  -> peer_median
--   2) do lech thuong ngay cua chinh chi nhanh so voi nhom: TRUNG VI 8 tuan truoc -> baseline
--      (trung vi de 1-2 tuan bat thuong gan day khong keo lech muc nen)
--   rel      = log(gia tri / peer_median) voi KPI muc (doanh thu, so don...);
--              gia tri - peer_median          voi KPI ty le (ty le huy, hoa hong, do phu POS...)
--   dev      = rel - baseline  (> 0: cao hon binh thuong cua chinh no)
--   noise_sd = do dao dong tu nhien cua rel: 1,4826 x MAD 8 tuan truoc (ben vung, tuan bat thuong khong
--              thoi phong), san duoi = trung vi noise cua cac chi nhanh cung KPI cung tuan (8 mau qua it,
--              co luc uoc luong qua nho -> z ao)
--   expected = gia tri ky vong neu tuan nay "binh thuong nhu moi khi" -> gap = gia tri - expected
-- KHONG dat nguong o day; nguong la viec cua lop phat hien (chinh tren tap hieu chinh).
{% set level_kpis = [
    'net_sales', 'orders', 'aov',
    'net_sales_walkin', 'orders_walkin', 'aov_walkin',
    'net_sales_app', 'orders_app', 'aov_app',
    'net_sales_grabfood', 'orders_grabfood', 'aov_grabfood',
    'net_sales_shopeefood', 'orders_shopeefood', 'aov_shopeefood',
    'shifts_morning', 'shifts_evening', 'kitchen_evening', 'labor_hours',
    'orders_per_evening_shift', 'app_avg_prep_min',
    'grabfood_avg_prep_min', 'shopeefood_avg_prep_min'
] %}
{% set rate_kpis = [
    'cogs_pct', 'labor_pct', 'void_rate', 'refund_rate', 'discount_rate',
    'app_store_cancel_rate', 'app_wait_cancel_rate', 'app_avg_rating',
    'grabfood_rating', 'shopeefood_rating',
    'grabfood_commission_gap', 'shopeefood_commission_gap',
    'grabfood_pos_coverage', 'shopeefood_pos_coverage'
] %}

with wk as (
    select * from {{ ref('mart_branch_weekly') }} where n_days = 7
),

long as (
    {% for k in level_kpis + rate_kpis %}
    select branch_id, store_class, week_start, '{{ k }}' as kpi,
           '{{ "level" if k in level_kpis else "rate" }}' as kpi_kind,
           cast({{ k }} as double) as value
    from wk
    {% if not loop.last %}union all{% endif %}
    {% endfor %}
),

peer as (
    -- trung vi cua CAC chi nhanh khac cung hang, cung tuan, cung KPI
    select a.branch_id, a.week_start, a.kpi, median(b.value) as peer_median, count(b.value) as n_peers
    from long a
    join long b
      on b.store_class = a.store_class and b.week_start = a.week_start and b.kpi = a.kpi
     and b.branch_id <> a.branch_id
    group by all
),

rel as (
    select
        l.*,
        p.peer_median,
        p.n_peers,
        case when l.kpi_kind = 'level'
             then ln(nullif(l.value, 0) / nullif(p.peer_median, 0))
             else l.value - p.peer_median end                        as rel
    from long l
    left join peer p using (branch_id, week_start, kpi)
),

stats as (
    select
        *,
        median(rel) over w8                                           as baseline_rel,
        count(rel) over w8                                            as baseline_n,
        1.4826 * mad(rel) over w8                                     as noise_own
    from rel
    window
        w8 as (partition by branch_id, kpi order by week_start rows between 8 preceding and 1 preceding)
),

noise as (
    select
        *,
        median(noise_own) over (partition by kpi, week_start)        as noise_floor
    from stats
),

final as (
    -- diem danh gia san chi bao 1 chu so thap phan: nhieu khong the nho hon nua buoc lam tron (0,05)
    select *, greatest(noise_own, noise_floor, case when kpi like '%_rating' then 0.05 else 0 end) as noise_sd
    from noise
)

select
    branch_id,
    store_class,
    week_start,
    kpi,
    kpi_kind,
    value,
    peer_median,
    n_peers,
    rel,
    baseline_rel,
    baseline_n,
    noise_own,
    noise_floor,
    noise_sd,
    rel - baseline_rel                                                as dev,
    (rel - baseline_rel) / nullif(greatest(noise_sd, 1e-6), 0)        as z,
    case when kpi_kind = 'level' then peer_median * exp(baseline_rel)
         else peer_median + baseline_rel end                          as expected_value,
    value - case when kpi_kind = 'level' then peer_median * exp(baseline_rel)
                 else peer_median + baseline_rel end                  as gap_vs_expected
from final
