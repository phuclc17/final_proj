# Airflow (dieu phoi) + mot moi truong Python rieng cho pipeline Fast&Fat (/opt/fastfat-venv).
FROM apache/airflow:2.10.5-python3.12

USER root
RUN python -m venv /opt/fastfat-venv && chown -R airflow: /opt/fastfat-venv
USER airflow

COPY docker/airflow/requirements-pipeline.txt /tmp/requirements-pipeline.txt
RUN /opt/fastfat-venv/bin/pip install --no-cache-dir -r /tmp/requirements-pipeline.txt
