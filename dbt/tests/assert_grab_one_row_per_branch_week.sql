-- Moi chi nhanh chi co 1 dong doi soat GrabFood moi tuan; tuan dai dung 7 ngay.
select branch_id, week_start, count(*) as n_rows, max(week_end - week_start) as days_span
from {{ ref('stg_grab__settlement') }}
group by 1, 2
having count(*) != 1 or max(week_end - week_start) != 6
