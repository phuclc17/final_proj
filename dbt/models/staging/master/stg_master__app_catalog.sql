-- Danh muc mon cua ung dung rieng (ma san pham rieng, ten tieng Viet co dau), moi anh chup.
select
    product_ref,
    product_name,
    {{ normalize_name('product_name') }}        as product_name_norm,
    category_ref,
    cast(price_vnd as bigint)                   as price,
    {{ snapshot_date_from_file('_source_file') }} as snapshot_date
from {{ source('bronze', 'master_app_catalog') }}
