{# Kiem thu tu viet (khong can goi dbt_utils): to hop cot phai duy nhat. #}
{% test unique_combination(model, columns) %}
select {{ columns | join(', ') }}, count(*) as n
from {{ model }}
group by {{ columns | join(', ') }}
having count(*) > 1
{% endtest %}
