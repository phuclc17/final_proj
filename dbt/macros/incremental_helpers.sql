{#
  Xu ly tang dan theo THOI DIEM NAP (_ingested_at), khong theo ngay nghiep vu:
  du lieu den tre (tep POS dong bo cham, bao cao san cua tuan truoc) van duoc xu ly o lan chay ke tiep.
  Dung kem unique_key='_source_file' + delete+insert: tep duoc gui lai ban sua -> thay toan bo dong cua tep do,
  khop voi co che nap lai o tang Bronze.
#}
{% macro only_new_bronze_rows(ts_col='_ingested_at') %}
{% if is_incremental() %}
    where {{ ts_col }} > (select coalesce(max({{ ts_col }}), timestamp '1900-01-01') from {{ this }})
{% endif %}
{% endmacro %}
