-- Doi soat noi bo cua bao cao Grab: thuc nhan = doanh thu mon - hoa hong - quang cao - khuyen mai quan chiu + dieu chinh.
-- Neu cong thuc khong khop, bao cao nguon co van de (hoac ep kieu sai).
select branch_id, week_start, gross_sales, commission, ads_spend, merchant_promo, adjustment, net_payout
from {{ ref('stg_grab__settlement') }}
where net_payout != gross_sales - commission - ads_spend - merchant_promo + adjustment
