# Ung dung Streamlit cua nen tang Fast&Fat (doc kho DuckDB gan tu thu muc du an).
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 TZ=Asia/Ho_Chi_Minh
COPY docker/app/requirements-app.txt /tmp/requirements-app.txt
RUN pip install --no-cache-dir -r /tmp/requirements-app.txt
WORKDIR /opt/fastfat
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
