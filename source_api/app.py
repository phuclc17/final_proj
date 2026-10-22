"""API gia lap cua cac phan mem nguon co API: POS dam may (chi nhanh dung POS ban moi) va App dat hang rieng.

Day la "phia doanh nghiep", khong thuoc duong ong: phan mem POS, App ghi giao dich vao kho cua chinh no; API chi doc kho
do va tra ve theo trang, giong API that cua nha cung cap phan mem:
  - xac thuc bang ma Bearer,
  - lay theo ngay kinh doanh, phan trang (page, page_size), tra kem tong so ban ghi de ben goi doi chieu,
  - gioi han tan suat goi (429 kem Retry-After), thinh thoang loi tam thoi (503) - ben goi phai tu thu lai.
Kho phia sau: thu muc data/live/_he_thong_nguon/ (bo mo phong dong vai phan mem ghi vao day).

    uvicorn source_api.app:app --port 8600      # tai lieu API tu sinh: http://localhost:8600/docs
"""
import json
import os
import random
import threading
import time
from collections import deque
from datetime import date
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query

STORE = Path(os.environ.get("SOURCE_STORE", Path(__file__).resolve().parent.parent / "data" / "live" / "_he_thong_nguon"))
TOKEN = os.environ.get("SOURCE_API_TOKEN", "fastfat-demo-token")
FAIL_RATE = float(os.environ.get("SOURCE_API_FAIL_RATE", "0.08"))
MAX_RPS = int(os.environ.get("SOURCE_API_MAX_RPS", "20"))

app = FastAPI(title="API hệ thống nguồn Fast&Fat (giả lập)", version="1.0",
              description="POS đám mây và App đặt hàng riêng. Lấy giao dịch theo ngày kinh doanh, phân trang. "
                          "Cần tiêu đề Authorization: Bearer <mã>. Có giới hạn tần suất và lỗi tạm thời như API thật.")
_calls, _lock = deque(), threading.Lock()


def guard(authorization):
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(401, "Sai hoặc thiếu mã xác thực")
    now = time.time()
    with _lock:
        while _calls and now - _calls[0] > 1:
            _calls.popleft()
        if len(_calls) >= MAX_RPS:
            raise HTTPException(429, "Gọi quá nhiều, thử lại sau", headers={"Retry-After": "1"})
        _calls.append(now)
    if random.random() < FAIL_RATE:
        raise HTTPException(503, "Hệ thống tạm thời quá tải, thử lại sau")


@lru_cache(maxsize=64)
def _read(path, mtime):
    return json.load(open(path, encoding="utf-8"))


def read(path):
    return _read(str(path), path.stat().st_mtime)


def pos_files(day):
    return sorted(STORE.glob(f"pos/*/pos_export_{day}.json"))


def app_file(day):
    return STORE / "owned_app" / f"orders_{day.replace('-', '')}.json"


def page_of(records, page, size, day):
    total = len(records)
    pages = max(1, -(-total // size))
    if page > pages:
        raise HTTPException(404, f"Không có trang {page}; tổng {pages} trang")
    return {"business_date": day, "page": page, "page_size": size, "total": total, "total_pages": pages,
            "data": records[(page - 1) * size: page * size]}


def check_day(day):
    try:
        date.fromisoformat(day)
    except ValueError:
        raise HTTPException(422, "Ngày phải có dạng YYYY-MM-DD")


@app.get("/health")
def health():
    return {"status": "ok", "store": str(STORE)}


@app.get("/pos/v1/business-dates", summary="Các ngày kinh doanh đã có giao dịch")
def pos_dates(authorization: str = Header(None)):
    guard(authorization)
    days = sorted({p.stem.replace("pos_export_", "") for p in STORE.glob("pos/*/pos_export_*.json")})
    return {"dates": days}


@app.get("/pos/v1/receipts", summary="Hóa đơn của mọi chi nhánh dùng POS đám mây trong một ngày, theo trang")
def pos_receipts(date_: str = Query(..., alias="date"), page: int = Query(1, ge=1),
                 page_size: int = Query(200, ge=1, le=500), authorization: str = Header(None)):
    guard(authorization)
    check_day(date_)
    recs = [r for f in pos_files(date_) for r in read(f)]
    return page_of(recs, page, page_size, date_)


@app.get("/app/v1/business-dates", summary="Các ngày kinh doanh đã có đơn App")
def app_dates(authorization: str = Header(None)):
    guard(authorization)
    days = sorted(f"{p.stem[7:11]}-{p.stem[11:13]}-{p.stem[13:15]}" for p in STORE.glob("owned_app/orders_*.json"))
    return {"dates": days}


@app.get("/app/v1/orders", summary="Đơn App của mọi chi nhánh trong một ngày, theo trang")
def app_orders(date_: str = Query(..., alias="date"), page: int = Query(1, ge=1),
               page_size: int = Query(200, ge=1, le=500), authorization: str = Header(None)):
    guard(authorization)
    check_day(date_)
    f = app_file(date_)
    recs = read(f)["data"] if f.exists() else []
    return page_of(recs, page, page_size, date_)
