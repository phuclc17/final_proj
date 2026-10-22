-- Gold: chieu mon an, SCD loai 2. Moi lan anh chup danh muc co gia/gia von/ten khac lan truoc
-- -> mo phien ban moi. Phien ban dau tien hieu luc tu 1900-01-01 de don truoc ngay chup van tra duoc.
with snaps as (
    select
        item_id, item_name, category, price, standard_cost, snapshot_date,
        md5(concat_ws('|', item_name, category, price, standard_cost)) as row_hash
    from {{ ref('stg_master__menu_items') }}
),

changes as (
    select *, lag(row_hash) over (partition by item_id order by snapshot_date) as prev_hash
    from snaps
),

versions as (
    select * from changes where prev_hash is null or prev_hash <> row_hash
)

select
    md5(item_id || '|' || snapshot_date)                                        as menu_item_sk,
    item_id,
    item_name,
    category,
    category = 'Combo'                                                          as is_combo,
    price,
    standard_cost,
    round(standard_cost / price, 4)                                             as standard_cost_pct,
    case when row_number() over w = 1 then date '1900-01-01' else snapshot_date end as valid_from,
    coalesce(cast(lead(snapshot_date) over w - interval 1 day as date), date '9999-12-31') as valid_to,
    lead(snapshot_date) over w is null                                          as is_current,
    snapshot_date                                                               as first_seen_snapshot
from versions
window w as (partition by item_id order by snapshot_date)
