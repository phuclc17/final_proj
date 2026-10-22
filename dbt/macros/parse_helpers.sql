{# Tien VND co the la so (75000) hoac chuoi co dau cham ngan cach hang nghin ("125.000", POS v2.8) #}
{% macro parse_vnd(expr) -%}
    try_cast(replace(cast({{ expr }} as varchar), '.', '') as bigint)
{%- endmacro %}

{# Chuan hoa ten de so khop: bo dau tieng Viet (ke ca d/D), chu thuong, ky tu dac biet -> khoang trang.
   "Ly + ống hút + hộp đựng" -> "ly ong hut hop dung"; "Khoai Tây Chiên (S)" -> "khoai tay chien s" #}
{% macro normalize_name(expr) -%}
    trim(regexp_replace(lower(strip_accents(replace(replace({{ expr }}, 'Đ', 'D'), 'đ', 'd'))), '[^a-z0-9]+', ' ', 'g'))
{%- endmacro %}

{# Ngay chup danh muc lay tu ten tep: ".../menu_items_20240601.csv" -> 2024-06-01 #}
{% macro snapshot_date_from_file(expr) -%}
    cast(strptime(regexp_extract({{ expr }}, '(\d{8})\.csv$', 1), '%Y%m%d') as date)
{%- endmacro %}

{# Lay phan so o cuoi ma: "NV0093" -> 93, "SKU-001" -> 1, "BR02" -> 2 #}
{% macro trailing_int(expr) -%}
    try_cast(regexp_extract({{ expr }}, '(\d+)$', 1) as integer)
{%- endmacro %}
