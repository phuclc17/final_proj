-- Ty le hoa hong theo hop dong voi tung san, co ngay hieu luc. Dung de doi chieu bao cao doi soat (P1a).
select
    cast(branch_id as integer)          as branch_id,
    platform,
    cast(commission_rate as double)     as contract_commission_rate,
    cast(effective_from as date)        as effective_from
from {{ source('bronze', 'master_marketplace_contracts') }}
qualify {{ snapshot_date_from_file('_source_file') }} = max({{ snapshot_date_from_file('_source_file') }}) over ()
