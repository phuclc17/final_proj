-- Silver: moi dong la 1 nguyen lieu trong 1 phieu nhap kho, da hop nhat 2 mau, dung don vi danh muc.
select
    _source_file || ':' || _row_number         as receipt_line_id,
    branch_id,
    receipt_date,
    ingredient_id,
    raw_name,
    match_method                                as ingredient_match_method,
    quantity,
    unit,
    unit_price,
    round(quantity * unit_price)                as line_amount,
    expiry_date,
    supplier,
    template,
    _source_file,
    _row_number,
    _batch_id
from {{ ref('checked_inventory__receipts') }}
where dq_issue is null
