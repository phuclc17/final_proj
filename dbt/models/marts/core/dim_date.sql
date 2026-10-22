-- Gold: chieu thoi gian, 1 dong / ngay trong khoang du lieu POS (tu mo rong khi them ngay moi).
-- Gan le (seed lich nghi le cong khai) va thoi tiet (Silver) de cay KPI tach bien dong binh thuong.
with bounds as (
    select min(business_date) as d0, max(business_date) as d1
    from {{ ref('stg_pos__receipts') }}
),

days as (
    select cast(unnest(generate_series(d0, d1, interval 1 day)) as date) as date_day
    from bounds
)

select
    d.date_day,
    cast(strftime(d.date_day, '%Y%m%d') as integer)     as date_key,
    cast(date_trunc('week', d.date_day) as date)        as week_start,      -- thu Hai
    weekofyear(d.date_day)                              as iso_week,
    month(d.date_day)                                   as month_no,
    isodow(d.date_day)                                  as iso_dow,         -- 1 = thu Hai
    strftime(d.date_day, '%a')                          as dow_name,
    isodow(d.date_day) >= 6                             as is_weekend,
    h.holiday_name,
    h.holiday_date is not null                          as is_holiday,
    w.weather_condition,
    w.precipitation_mm,
    w.temp_max_c,
    coalesce(w.is_rain, false)                          as is_rain
from days d
left join {{ ref('vn_public_holidays_2024') }} h on h.holiday_date = d.date_day
left join {{ ref('stg_weather__daily') }} w on w.weather_date = d.date_day
