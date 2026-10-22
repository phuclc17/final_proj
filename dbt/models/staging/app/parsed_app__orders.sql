{{ config(schema='silver_work', materialized='incremental', unique_key='_source_file',
          incremental_strategy='delete+insert', on_schema_change='fail') }}
-- Giai ma JSON don ung dung thanh cot.
-- Phan ton thoi gian nhat cua Silver (giai ma JSON) -> chay TANG DAN: moi lan chi giai ma cac tep vua nap.
-- Kiem tra trung ma giua cac tep van lam o base_app__orders tren TOAN BO du lieu da giai ma (re, dang cot).
with src as (
    select payload, _source_file, _row_number, _batch_id, _ingested_at
    from {{ source('bronze', 'app_orders') }}
    {{ only_new_bronze_rows() }}
)

select
    json_extract_string(payload, '$.order_uuid')                                         as order_id,
    json_extract_string(payload, '$.branch_ref.code')                                    as app_branch_code,
    try_strptime(json_extract_string(payload, '$.created_at_utc'), '%Y-%m-%dT%H:%M:%SZ')        as created_at_utc,
    try_strptime(json_extract_string(payload, '$.kitchen_ready_at_utc'), '%Y-%m-%dT%H:%M:%SZ')  as ready_at_utc,
    json_extract_string(payload, '$.customer_id_hashed')                                 as customer_id,
    cast(json_extract(payload, '$.is_first_order_flag') as boolean)                      as is_first_order,
    json_extract_string(payload, '$.platform')                                           as device_platform,
    json_extract_string(payload, '$.order_status')                                       as order_status,
    json_extract_string(payload, '$.cancel_reason')                                      as cancel_reason,
    json_extract_string(payload, '$.payment_method')                                     as payment_method,
    json_extract_string(payload, '$.payment_status')                                     as payment_status,
    json_extract_string(payload, '$.delivery_type')                                      as delivery_type,
    {{ parse_vnd("json_extract_string(payload, '$.subtotal')") }}                        as subtotal_amount,
    {{ parse_vnd("json_extract_string(payload, '$.delivery_fee')") }}                    as delivery_fee,
    {{ parse_vnd("json_extract_string(payload, '$.packaging_fee')") }}                   as packaging_fee,
    {{ parse_vnd("json_extract_string(payload, '$.service_fee')") }}                     as service_fee,
    json_extract_string(payload, '$.promo_applied.code')                                 as promo_code,
    {{ parse_vnd("json_extract_string(payload, '$.promo_applied.value')") }}             as promo_value,
    {{ parse_vnd("json_extract_string(payload, '$.total_amount')") }}                    as total_amount,
    try_cast(json_extract_string(payload, '$.rating') as integer)                        as rating,
    json_extract_string(payload, '$.utm_source')                                         as utm_source,
    json_extract(payload, '$.line_items')                                                as items_json,
    json_array_length(json_extract(payload, '$.line_items'))                     as n_items_json,
    _source_file, _row_number, _batch_id, _ingested_at
from src
