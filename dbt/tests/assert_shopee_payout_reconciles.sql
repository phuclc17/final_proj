-- Doi soat noi bo bao cao ShopeeFood: thuc nhan = doanh thu mon - phi dich vu - quang cao - khuyen mai quan chiu + dieu chinh.
select branch_id, week_start, gross_sales, commission, ads_spend, merchant_promo, adjustment, net_payout
from {{ ref('stg_shopee__settlement') }}
where net_payout != gross_sales - commission - ads_spend - merchant_promo + adjustment
   or week_end - week_start != 6
