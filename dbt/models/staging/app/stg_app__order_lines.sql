-- Silver: moi dong la 1 mon trong 1 don ung dung, da anh xa ve ma mon chuan.
with orders as (
    select order_id, branch_id, business_date, order_status, items_json
    from {{ ref('base_app__orders') }}
    where dq_issue is null
),

lines as (
    select order_id, branch_id, business_date, order_status,
           unnest(json_extract(items_json, '$[*]')) as line
    from orders
)

select
    l.order_id,
    row_number() over (partition by l.order_id order by json_extract_string(l.line, '$.product_ref')) as line_no,
    json_extract_string(l.line, '$.product_ref')                       as product_ref,
    json_extract_string(l.line, '$.product_name')                      as product_name,
    p.item_id,
    try_cast(json_extract_string(l.line, '$.qty') as integer)          as qty,
    {{ parse_vnd("json_extract_string(l.line, '$.price_vnd')") }}      as unit_price,
    try_cast(json_extract_string(l.line, '$.qty') as integer) * {{ parse_vnd("json_extract_string(l.line, '$.price_vnd')") }} as line_amount,
    l.branch_id,
    l.business_date,
    l.order_status
from lines l
left join {{ ref('map_app_product_item') }} p on p.product_ref = json_extract_string(l.line, '$.product_ref')
