{# Dung dung ten schema khai bao (silver, gold) thay vi mac dinh cua dbt la "main_silver" #}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}{{ target.schema }}{%- else -%}{{ custom_schema_name | trim }}{%- endif -%}
{%- endmacro %}
