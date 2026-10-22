-- Silver: luot quet the hop le (da loai quet trung).
select
    _source_file || ':' || _row_number as punch_id,
    staff_id,
    branch_id,
    event_type,
    event_at,
    device_id,
    verification_method,
    _source_file,
    _row_number,
    _batch_id
from {{ ref('base_timekeeping__punches') }}
where dq_issue is null
