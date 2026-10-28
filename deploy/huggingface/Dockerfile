# Ban xem truc tuyen tren Hugging Face Spaces: ung dung Streamlit doc kho DuckDB o che do chi doc.
# Ma nguon lay tu GitHub, du lieu (kho cua ba moi truong, tep nguon, metadata dbt) lay tu dataset tren Hugging Face.
FROM python:3.12-slim

ARG REPO=https://github.com/phuclc17/fnb-ops-data-platform
ARG DATA_REPO=DATA_REPO_ID

ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 TZ=Asia/Ho_Chi_Minh FASTFAT_STATIC=1 HOME=/home/user
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 user
WORKDIR /home/user/app

RUN git clone --depth 1 "$REPO" . \
    && pip install --no-cache-dir -r docker/app/requirements-app.txt huggingface_hub==2.3.0 \
    && python deploy/huggingface/fetch_data.py "$DATA_REPO" \
    && chown -R user:user /home/user

USER user
EXPOSE 7860
CMD ["streamlit", "run", "app/main.py", "--server.port", "7860", "--server.address", "0.0.0.0", \
     "--server.headless", "true", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false", \
     "--browser.gatherUsageStats", "false"]
