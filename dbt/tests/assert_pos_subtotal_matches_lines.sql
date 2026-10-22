-- Nhat quan noi bo: tam tinh cua hoa don phai bang tong thanh tien cac dong mon.
select r.receipt_no, r.subtotal_amount, sum(l.line_amount) as sum_lines
from {{ ref('stg_pos__receipts') }} r
join {{ ref('stg_pos__receipt_lines') }} l using (receipt_no)
group by 1, 2
having r.subtotal_amount != sum(l.line_amount)
