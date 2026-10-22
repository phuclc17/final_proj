{{ config(schema='silver_work', materialized='incremental', unique_key='_source_file',
          incremental_strategy='delete+insert', on_schema_change='fail') }}
-- Giai ma JSON hoa don POS (2 phien ban phan mem) thanh cot.
-- Phan ton thoi gian nhat cua Silver (giai ma JSON) -> chay TANG DAN: moi lan chi giai ma cac tep vua nap.
-- Kiem tra trung ma giua cac tep van lam o base_pos__receipts tren TOAN BO du lieu da giai ma (re, dang cot).
with src as (
    select payload, _source_file, _row_number, _batch_id, _ingested_at
    from {{ source('bronze', 'pos_receipts') }}
    {{ only_new_bronze_rows() }}
)

select
    json_extract_string(payload, '$.receipt_no')                                    as receipt_no,
    json_extract_string(payload, '$.terminal_id')                                   as terminal_id,
    regexp_extract(json_extract_string(payload, '$.terminal_id'), '^(POS-\d+)', 1)  as pos_terminal_prefix,
    json_extract_string(payload, '$.pos_software_version')                          as pos_version,
    coalesce(
        try_strptime(json_extract_string(payload, '$.txn_time'), '%d/%m/%Y %H:%M:%S'),
        try_strptime(json_extract_string(payload, '$.txn_time'), '%Y-%m-%dT%H:%M:%S')
    )                                                                               as txn_at,
    case json_extract_string(payload, '$.order_source')
        when 'POS' then 'WALKIN' else json_extract_string(payload, '$.order_source')
    end                                                                             as channel,
    json_extract_string(payload, '$.order_type')                                    as order_type,
    {{ trailing_int("json_extract_string(payload, '$.cashier_code')") }}            as cashier_staff_id,
    json_extract_string(payload, '$.payment_method')                                as payment_method,
    {{ parse_vnd("json_extract_string(payload, '$.subtotal_amount')") }}            as subtotal_amount,
    json_extract_string(payload, '$.discount_code')                                 as discount_code,
    {{ parse_vnd("json_extract_string(payload, '$.discount_amount')") }}            as discount_amount,
    {{ parse_vnd("json_extract_string(payload, '$.rounding_adjustment')") }}        as rounding_adjustment,
    {{ parse_vnd("coalesce(json_extract_string(payload, '$.total_paid'), json_extract_string(payload, '$.grand_total'))") }} as total_paid,
    cast(json_extract(payload, '$.void_flag') as boolean)                           as is_void,
    json_extract_string(payload, '$.void_reason')                                   as void_reason,
    {{ trailing_int("json_extract_string(payload, '$.void_by')") }}                 as void_by_staff_id,
    try_strptime(json_extract_string(payload, '$.void_timestamp'), '%d/%m/%Y %H:%M:%S') as void_at,
    cast(json_extract(payload, '$.refund_flag') as boolean)                         as is_refund,
    {{ parse_vnd("json_extract_string(payload, '$.refund_amount')") }}              as refund_amount,
    {{ trailing_int("json_extract_string(payload, '$.refund_by')") }}               as refund_by_staff_id,
    cast(json_extract(payload, '$.printed_flag') as boolean)                        as is_printed,
    try_cast(json_extract_string(payload, '$.reprint_count') as integer)            as reprint_count,
    json_extract_string(payload, '$.sync_status')                                   as sync_status,
    json_extract(payload, '$.items')                                                as items_json,
    json_array_length(json_extract(payload, '$.items'))                     as n_items_json,
    _source_file, _row_number, _batch_id, _ingested_at
from src
