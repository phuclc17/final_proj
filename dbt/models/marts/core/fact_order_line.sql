-- Gold: bang su kien DONG MON, 1 dong / mon tren don (POS + App).
-- Gan phien ban mon (SCD2) theo ngay ban -> gia von dinh muc dung theo thoi diem (doi gia 01/06).
-- cogs_standard = gia von dinh muc cua phan mon da ban (chi dong co doanh thu).
with pos as (
    select
        'POS:' || receipt_no                                     as order_key,
        line_no,
        item_id,
        qty,
        unit_price,
        line_discount_amount,
        line_amount,
        is_item_void,
        branch_id,
        business_date                                            as date_day,
        channel,
        case when receipt_is_void then 'VOIDED'
             when receipt_is_refund then 'REFUNDED'
             else 'COMPLETED' end                                as order_status
    from {{ ref('stg_pos__receipt_lines') }}
),

app as (
    select
        'APP:' || order_id,
        cast(line_no as integer),
        item_id,
        qty,
        unit_price,
        cast(0 as bigint),
        line_amount,
        false,
        branch_id,
        business_date,
        'APP',
        case order_status when 'DELIVERED' then 'COMPLETED' else order_status end
    from {{ ref('stg_app__order_lines') }}
),

lines as (
    select * from pos
    union all
    select * from app
)

select
    l.order_key || '#' || l.line_no                                         as order_line_key,
    l.order_key,
    l.line_no,
    l.branch_id,
    l.date_day,
    l.channel,
    l.item_id,
    mi.menu_item_sk,
    mi.category,
    mi.is_combo,
    l.qty,
    l.unit_price,
    l.line_discount_amount,
    l.line_amount,
    l.is_item_void,
    l.order_status,
    l.order_status = 'COMPLETED' and not l.is_item_void                    as is_revenue_line,
    l.order_status in ('COMPLETED', 'REFUNDED') and not l.is_item_void     as is_prepared,
    mi.standard_cost                                                        as standard_unit_cost,
    case when l.order_status = 'COMPLETED' and not l.is_item_void
         then l.qty * mi.standard_cost else 0 end                           as cogs_standard
from lines l
left join {{ ref('dim_menu_item') }} mi
    on mi.item_id = l.item_id
   and l.date_day between mi.valid_from and mi.valid_to
