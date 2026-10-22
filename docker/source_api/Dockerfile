# API gia lap cua phan mem POS dam may va App (phia doanh nghiep, khong thuoc duong ong). Chi doc kho cua phan mem.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 TZ=Asia/Ho_Chi_Minh
RUN pip install --no-cache-dir fastapi==0.143.3 uvicorn==0.34.0
WORKDIR /opt/fastfat
EXPOSE 8600
CMD ["uvicorn", "source_api.app:app", "--host", "0.0.0.0", "--port", "8600"]
