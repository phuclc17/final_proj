"""Tham so cua the gioi mo phong Fast&Fat. Moi con so "nghiep vu" nam o day de de giai thich trong bao cao."""
from datetime import date
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parent
ROOT = SIM_DIR.parent
REFERENCE_DIR = SIM_DIR / "reference"
SCENARIO_DIR = SIM_DIR / "scenarios"
DATA_DIR = ROOT / "data"

START_DATE = date(2024, 3, 11)  # thu Hai -> tuan doi soat Thu Hai..Chu Nhat
BACKFILL_DAYS = 182             # 26 tuan

# ---------- Nhu cau ----------
TIER_BASE_ORDERS = {"hot": 380, "medium": 170, "low": 60}  # tong don/ngay moi kenh, ngay thuong
CHANNELS = ["WALKIN", "GRABFOOD", "SHOPEEFOOD", "APP"]
MARKETPLACES = ["GRABFOOD", "SHOPEEFOOD"]
CHANNEL_MIX = {"WALKIN": 0.55, "GRABFOOD": 0.15, "SHOPEEFOOD": 0.10, "APP": 0.20}
WEEKDAY_FACTOR = [0.92, 0.90, 0.95, 0.98, 1.10, 1.25, 1.20]
DAILY_NOISE_SD = 0.075          # khop voi uoc luong tu du lieu that (gia dinh cu 0.08)
BRANCH_LEVEL_SD = 0.10

HOLIDAYS = {
    date(2024, 4, 18): "Gio To Hung Vuong",
    date(2024, 4, 30): "Ngay Giai phong mien Nam",
    date(2024, 5, 1): "Quoc te Lao dong",
    date(2024, 9, 2): "Quoc khanh",
    date(2024, 9, 3): "Quoc khanh (nghi bu)",
}
HOLIDAY_FACTOR = {"WALKIN": 1.35, "APP": 1.30, "GRABFOOD": 1.15, "SHOPEEFOOD": 1.15}
RAIN_FACTOR = {"WALKIN": 0.75, "APP": 1.20, "GRABFOOD": 1.25, "SHOPEEFOOD": 1.25}
WET_SEASON_MONTHS = range(5, 11)
RAIN_PROB = {"wet": 0.45, "dry": 0.08}

OPEN_HOURS = list(range(7, 22))
HOUR_WEIGHT = {h: (3.0 if (11 <= h <= 13 or 18 <= h <= 20) else 1.0) for h in OPEN_HOURS}
MORNING_HOURS = range(7, 14)
EVENING_HOURS = range(14, 22)

# Hieu chinh tu du lieu that "The Bread Basket" (OpenML 43422, CC0, 9.465 giao dich, 2016-2017)
# - xem simulator/calibrate_public.py va data/public_reference/calibration_report.json
ITEMS_PER_ORDER = ([1, 2, 3, 4], [0.42, 0.32, 0.16, 0.10])
QTY_PER_LINE = ([1, 2], [0.92, 0.08])
ITEM_ZIPF_EXPONENT = 1.06       # do tap trung mon ban chay (mon dau ~27% so phan, top 5 ~59%)
# Thu tu mon ban chay la GIA DINH cua tac gia (mon chu luc truoc); chi do doc cua phan phoi lay tu du lieu that
ITEM_POPULARITY_RANK = [1, 19, 14, 2, 25, 5, 7, 13, 4, 15, 22, 21, 26, 10, 27, 8, 9, 3, 24, 20, 16, 11, 6, 23,
                        12, 18, 17, 28]

# ---------- Nhan su & nang luc bep ----------
ATTENDANCE_BY_WEEKDAY = [0.70, 0.70, 0.72, 0.74, 0.82, 0.88, 0.88]
MIN_KITCHEN_BY_TIER = {"hot": 3, "medium": 2, "low": 1}  # quan ly goi nguoi lam bu neu ca thieu bep
UTIL_AT_MIN_COVERAGE = 0.95     # ngay dong nhat, ca chi co so bep toi thieu -> tai 95%
SHIFT_TIMES = {"morning": ((6, 45), (14, 0)), "evening": ((13, 45), (22, 0))}

# ---------- Chuoi nhan qua dich vu ----------
# prep_time = PREP_BASE + PREP_SCALE / (1 - util)^PREP_POWER  (kieu hang doi, bao hoa o UTIL_CAP)
PREP_BASE, PREP_SCALE, PREP_POWER, UTIL_CAP = 4.0, 6.0, 0.6, 0.97
BALK_START, BALK_SLOPE, BALK_MAX = 0.90, 0.60, 0.40           # khach tai quay bo di khi qua tai
STORE_CANCEL_BASE, STORE_CANCEL_START, STORE_CANCEL_SLOPE = 0.006, 0.85, 0.30
CUST_CANCEL_BASE, CUST_CANCEL_PREP_START, CUST_CANCEL_SLOPE = 0.015, 18.0, 0.004
RATING_BASE, RATING_PREP_START, RATING_PREP_SLOPE, RATING_SD, RATING_SHARE = 4.7, 15.0, 0.05, 0.7, 0.35
RATING_EMA, RATING_CANCEL_PENALTY = 0.4, 2.0
RANKING_REF_RATING, RANKING_SLOPE, RANKING_MIN, RANKING_MAX = 4.5, 0.8, 0.55, 1.08

# ---------- Doi soat san ----------
COMMISSION_CONTRACT = {"GRABFOOD": 0.25, "SHOPEEFOOD": 0.22}
MKT_PROMO_SHARE, MKT_PROMO_RANGE, MKT_PROMO_MERCHANT_SHARE = 0.25, (10000, 20000), 0.5
ADS_BRANCHES = {2, 3, 8, 6}     # chi nhanh co mua quang cao tren san
ADS_RATE = 0.01

# ---------- Gia & danh muc thay doi (nguon goc cua SCD2) ----------
PRICE_CHANGES = {date(2024, 6, 1): {1: 37000, 2: 72000, 4: 55000, 10: 62000, 25: 95000, 26: 85000}}
STAFF_CHANGES = [{"date": date(2024, 7, 1), "staff_id": 3, "role": "ShiftManager", "hourly_wage": 30000}]

# ---------- Kho ----------
FRESH_DELIVERY_WEEKDAYS = {0, 1, 2, 3, 4, 5}
DRY_DELIVERY_WEEKDAYS = {0, 3}
COVER_DAYS = {"fresh": 2.2, "fresh_saturday": 3.0, "dry": 6.0}
REORDER_DAYS = {"fresh": 1.6, "dry": 3.5}
INITIAL_STOCK_DAYS = {"fresh": 3.0, "dry": 8.0}
WASTE_FACTOR = {"fresh": (1.02, 1.05), "dry": (1.00, 1.02)}
SUPPLIER_PRICE_NOISE = 0.03
SUPPLIERS = {"fresh": ["Cty TNHH Thuc Pham Sach", "Nha cung cap XYZ"], "dry": ["Cty ABC", "Nha phan phoi Minh Long"]}
COUNT_EVERY_DAYS = 14           # kiem ke 2 tuan/lan vao Chu Nhat
COUNT_NOISE_SD = 0.02

# ---------- Loi nhap lieu / loi he thong cua tung nguon ----------
POS_MISS_MARKETPLACE = 0.03     # nhan vien quen nhap don san vao POS
NORMAL_VOID_RATE = 0.008
REFUND_RATE = 0.01
STAFF_MEAL_RATE = 0.004
COMBO_DISCOUNT_RATE = 0.35
LOYALTY_RATE = 0.12
TK_DUP_RATE, TK_MISSING_OUT_RATE = 0.06, 0.05
RECEIPT_NAME_VARIANT_RATE = 0.05
RECEIPT_KG_TYPO_RATE = 0.005    # nhap so luong theo gram nhung de don vi kg
COUNT_BLANK_RATE = 0.02

# ---------- Dinh dang theo tung he thong ----------
OLD_POS_BRANCHES = {5, 7, 10}           # POS v2.8: dinh dang ngay/tien khac, doi ten cot tong tien
# tap live: POS dam may (chi nhanh khong dung POS cu) va App luu giao dich trong kho cua chinh phan mem, ben ngoai chi
# lay duoc qua API (source_api/); POS cai tai may van xuat tep moi dem vao vung tiep nhan nhu cac tap danh gia
API_STORE_DIR = "_he_thong_nguon"
RECEIPT_TEMPLATE_B_BRANCHES = {3, 6, 9}  # so nhap kho kieu "tieng Anh", so luong dinh don vi
TERMINALS_BY_TIER = {"hot": 3, "medium": 2, "low": 1}
STORE_CLASS_BY_TIER = {"hot": "A", "medium": "B", "low": "C"}

N_CUSTOMERS = 4200
