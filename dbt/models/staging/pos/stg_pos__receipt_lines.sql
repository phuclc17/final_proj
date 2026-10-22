-- Silver: moi dong la 1 mon trong 1 hoa don POS (tach mang items).
-- item_id lay tu ma SKU ("SKU-014" -> 14) vi ten mon tren hoa don co nhieu bien the ("KT Chien Lon", "Khoai Tay (L)").
with receipts as (
    select receipt_no, branch_id, business_date, channel, is_void, is_refund, items_json
    from {{ ref('base_pos__receipts') }}
    where dq_issue is null
),

lines as (
    select
        receipt_no, branch_id, business_date, channel, is_void, is_refund,
        unnest(json_extract(items_json, '$[*]')) as line
    from receipts
)

select
    receipt_no,
    try_cast(json_extract_string(line, '$.line_id') as integer)            as line_no,
    {{ trailing_int("json_extract_string(line, '$.sku')") }}               as item_id,
    json_extract_string(line, '$.name_on_receipt')                         as name_on_receipt,
    try_cast(json_extract_string(line, '$.qty') as integer)                as qty,
    {{ parse_vnd("json_extract_string(line, '$.unit_price')") }}           as unit_price,
    {{ parse_vnd("json_extract_string(line, '$.line_discount_amount')") }} as line_discount_amount,
    try_cast(json_extract_string(line, '$.qty') as integer) * {{ parse_vnd("json_extract_string(line, '$.unit_price')") }}
        - {{ parse_vnd("json_extract_string(line, '$.line_discount_amount')") }} as line_amount,
    cast(json_extract(line, '$.void_item_flag') as boolean)                as is_item_void,
    branch_id,
    business_date,
    channel,
    is_void   as receipt_is_void,
    is_refund as receipt_is_refund
from lines
