-- Silver: thoi tiet TP.HCM theo ngay (nguon ben ngoai).
select
    cast(json_extract_string(payload, '$.date') as date)                 as weather_date,
    try_cast(json_extract_string(payload, '$.precipitation_mm') as double) as precipitation_mm,
    json_extract_string(payload, '$.condition')                          as weather_condition,
    try_cast(json_extract_string(payload, '$.temp_max_c') as double)     as temp_max_c,
    coalesce(try_cast(json_extract_string(payload, '$.precipitation_mm') as double), 0) > 0
        or json_extract_string(payload, '$.condition') = 'Rain'          as is_rain
from {{ source('bronze', 'weather_daily') }}
