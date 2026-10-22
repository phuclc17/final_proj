{{ config(schema='silver_work') }}
-- Giai quyet dinh danh nguyen lieu cho ten go tay trong so nhap kho, theo 3 tang:
--   1. khop chinh xac voi ten danh muc sau khi chuan hoa (bo dau, chu thuong, bo ky tu dac biet)
--   2. tra bang bien the do ky su du lieu lap (seed ingredient_name_variants)
--   3. khop mo: do tuong dong Jaro-Winkler cao nhat >= 0.90 voi ten danh muc hoac ten bien the
-- Ten khong qua duoc tang nao -> ingredient_id rong -> dong du lieu bi cach ly.
with names as (
    select distinct {{ normalize_name('raw_name') }} as name_norm
    from {{ ref('base_inventory__receipts') }}
    where row_kind = 'data' and raw_name is not null
),

master as (
    select ingredient_id, ingredient_name_norm as name_norm from {{ ref('stg_master__ingredients') }}
),

variants as (
    select name_norm, ingredient_id from {{ ref('ingredient_name_variants') }}
),

exact as (
    select n.name_norm, m.ingredient_id, 'khop_chinh_xac' as match_method, 1.0 as similarity
    from names n join master m using (name_norm)
),

by_variant as (
    select n.name_norm, v.ingredient_id, 'bang_bien_the' as match_method, 1.0 as similarity
    from names n join variants v using (name_norm)
    where n.name_norm not in (select name_norm from exact)
),

candidates as (
    select * from master
    union all
    select * from variants
),

fuzzy as (
    select
        n.name_norm,
        arg_max(c.ingredient_id, jaro_winkler_similarity(n.name_norm, c.name_norm)) as ingredient_id,
        'khop_mo'                                                                  as match_method,
        max(jaro_winkler_similarity(n.name_norm, c.name_norm))                     as similarity
    from names n
    cross join candidates c
    where n.name_norm not in (select name_norm from exact union all select name_norm from by_variant)
    group by n.name_norm
)

select * from exact
union all
select * from by_variant
union all
select name_norm,
       case when similarity >= 0.90 then ingredient_id end              as ingredient_id,
       case when similarity >= 0.90 then match_method else 'khong_nhan_dien_duoc' end as match_method,
       similarity
from fuzzy
