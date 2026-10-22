"""Hop dong du lieu cua tung nguon: nhan dang tep theo NOI DUNG (cot, khoa JSON, dong tieu de phieu), suy ra he thong,
chi nhanh, ngay va vi tri chuan trong vung tiep nhan, kiem tra toi thieu truoc khi cho vao.

Dung chung cho:
  - kenh tai tep len (app/views/upload.py) va pipeline/intake.py: tep sai hop dong bi tu choi kem ly do,
  - buoc nap (pipeline/ingest.py): tep nam dung thu muc nhung sai hop dong khong vao Bronze, ghi ly do vao nhat ky,
  - trang Ket noi nguon: danh muc nguon, kenh thu thap, tan suat, cot bat buoc.
Ngoai thuc te, moi nguon den bang mot kenh khac nhau (API, tep xuat tu dong, tep do nguoi gui); hop dong la cho duy nhat
khai bao "mot tep hop le cua nguon X trong nhu the nao".
"""
import csv
import io
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "dbt" / "seeds" / "branch_code_map.csv"

# ---------------------------------------------------------------- danh muc nguon
# key, he thong, kenh ngoai thuc te, kenh trong he thong nay, tan suat, dinh dang, thu muc, bang bronze, cot/khoa bat buoc
SOURCES = [
    dict(key="pos", system="POS tại quầy", real="API của phần mềm POS đám mây; POS cài tại máy thì xuất tệp mỗi đêm",
         here="8 chi nhánh dùng POS đám mây: bộ kết nối kéo qua API; CN5, CN7, CN10 dùng POS cài tại máy: "
              "tệp xuất mỗi đêm", cadence="mỗi ngày, mỗi chi nhánh", fmt="JSON",
         folder="pos/<máy POS>/pos_export_<ngày>.json", bronze=["pos_receipts"],
         required=["receipt_no", "terminal_id", "txn_time", "items"]),
    dict(key="app", system="App đặt hàng riêng", real="API hoặc bản sao cơ sở dữ liệu của chính công ty",
         here="API, bộ kết nối kéo về mỗi lượt", cadence="mỗi ngày", fmt="JSON có lớp vỏ trang",
         folder="owned_app/orders_<ngày>.json", bronze=["app_orders"],
         required=["order_uuid", "created_at_utc", "branch_ref", "line_items", "order_status"]),
    dict(key="grab", system="GrabFood", real="Kế toán tải báo cáo đối soát từ cổng đối tác, hoặc nhận qua email",
         here="tệp đẩy vào vùng tiếp nhận, hoặc tải lên", cadence="mỗi tuần", fmt="CSV",
         folder="grabfood/GrabFood_Settlement_<đầu tuần>_<cuối tuần>.csv", bronze=["grab_settlement"],
         required=["Merchant Store Name", "Week", "Gross Sales", "Total Orders", "Total Commission", "Net Payout"]),
    dict(key="shopee", system="ShopeeFood", real="Kế toán tải báo cáo đối soát từ cổng đối tác, hoặc nhận qua email",
         here="tệp đẩy vào vùng tiếp nhận, hoặc tải lên", cadence="mỗi tuần", fmt="Excel",
         folder="shopeefood/ShopeeFood_DoiSoat_<đầu tuần>_<cuối tuần>.xlsx", bronze=["shopee_settlement"],
         required=["Mã cửa hàng", "Số đơn hoàn thành", "Doanh thu món (VNĐ)", "Phí dịch vụ (VNĐ)", "Thực nhận (VNĐ)"]),
    dict(key="receipt_a", system="Sổ nhập kho, mẫu A", real="Quản lý cửa hàng điền Excel, gửi email, Drive hoặc Zalo",
         here="tệp đẩy vào vùng tiếp nhận, hoặc tải lên", cadence="mỗi lần nhập hàng", fmt="Excel dạng phiếu",
         folder="warehouse_receipts/CNxx/NhapKho_CNxx_<ngày>.xlsx", bronze=["warehouse_receipts_form"],
         required=["Tên nguyên liệu", "ĐVT", "Số lượng", "Đơn giá"]),
    dict(key="receipt_b", system="Sổ nhập kho, mẫu B", real="Quản lý cửa hàng điền Excel, gửi email, Drive hoặc Zalo",
         here="tệp đẩy vào vùng tiếp nhận, hoặc tải lên", cadence="mỗi lần nhập hàng", fmt="Excel dạng bảng",
         folder="warehouse_receipts/CNxx/receipts_CNxx_<ngày>.xlsx", bronze=["warehouse_receipts_table"],
         required=["date", "item", "quantity", "unit_price", "supplier"]),
    dict(key="stock", system="Phiếu kiểm kê", real="Nhân viên đếm kho, điền Excel, gửi về trụ sở",
         here="tệp đẩy vào vùng tiếp nhận, hoặc tải lên", cadence="2 tuần một lần", fmt="Excel dạng phiếu",
         folder="stock_counts/CNxx/KiemKe_CNxx_<ngày>.xlsx", bronze=["stock_counts"],
         required=["Mã NL", "Tên nguyên liệu", "ĐVT", "Tồn thực tế"]),
    dict(key="timekeeping", system="Máy chấm công", real="Phần mềm đi kèm máy vân tay, khuôn mặt xuất CSV; HR đám mây có API",
         here="tệp đẩy vào vùng tiếp nhận, hoặc tải lên", cadence="mỗi ngày, mỗi chi nhánh", fmt="CSV",
         folder="timekeeping/BRxx/punch_BRxx_<ngày>.csv", bronze=["timekeeping_punches"],
         required=["employee_code", "branch_code", "event_type", "event_time"]),
    dict(key="weather", system="Thời tiết", real="API dịch vụ thời tiết công khai", here="tệp đẩy vào vùng tiếp nhận",
         cadence="mỗi ngày", fmt="JSON", folder="external/weather/weather_hcm_<ngày>.json", bronze=["weather_daily"],
         required=["date", "precipitation_mm", "condition"]),
    dict(key="master", system="Danh mục trụ sở", real="Xuất từ hệ thống quản trị hoặc Excel của trụ sở khi có thay đổi",
         here="tệp đẩy vào vùng tiếp nhận, hoặc tải lên", cadence="khi có thay đổi", fmt="CSV",
         folder="master_data/<danh mục>/<danh mục>_<ngày hiệu lực>.csv", bronze=["master_*"], required=[]),
]
BY_KEY = {s["key"]: s for s in SOURCES}
MASTER_HEADERS = {
    "app_catalog": ["product_ref", "product_name", "category_ref", "price_vnd"],
    "branches": ["branch_id", "branch_name", "district", "latitude", "longitude", "open_date", "store_class"],
    "combo_components": ["combo_item_id", "component_item_id", "quantity"],
    "ingredients": ["ingredient_id", "ingredient_code", "ingredient_name", "unit", "category", "shelf_life_days",
                    "standard_unit_cost"],
    "marketplace_contracts": ["branch_id", "platform", "commission_rate", "effective_from"],
    "menu_items": ["item_id", "item_name", "category", "price", "standard_cost"],
    "recipes": ["item_id", "ingredient_id", "qty_per_unit"],
    "staff": ["staff_id", "staff_name", "branch_id", "role", "hourly_wage", "hire_date"],
}


@dataclass
class Result:
    source: str | None = None          # key trong SOURCES; None = khong nhan dang duoc
    target: str | None = None          # duong dan tuong doi chuan trong vung tiep nhan
    errors: list = field(default_factory=list)   # vi pham hop dong -> tu choi
    notes: list = field(default_factory=list)    # luu y, van nhan
    facts: dict = field(default_factory=dict)    # ngay, chi nhanh, so dong... de hien thi

    @property
    def ok(self):
        return self.source is not None and self.target is not None and not self.errors


# ---------------------------------------------------------------- tien ich
def branch_map(src=None):
    """Bang anh xa ma chi nhanh cua 6 he thong (seed dbt) + ten chi nhanh (danh muc moi nhat trong vung tiep nhan)."""
    m = pd.read_csv(SEED, dtype=str)
    names = {}
    if src is not None:
        files = sorted((Path(src) / "master_data" / "branches").glob("*.csv"))
        if files:
            b = pd.read_csv(files[-1], dtype=str)
            names = dict(zip(b.branch_name, b.branch_id.astype(int)))
    return m.assign(branch_id=m.branch_id.astype(int)), names


def parse_date(s):
    s = str(s).strip()
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d", "%d %b %Y"):
        try:
            return datetime.strptime(s[:len(datetime.now().strftime(fmt))] if "%b" not in fmt else s, fmt)
        except ValueError:
            continue
    try:
        return pd.Timestamp(s).to_pydatetime()
    except (ValueError, TypeError):
        return None


def mode_date(values):
    ds = [d.date() for d in (parse_date(v) for v in values) if d is not None]
    return max(set(ds), key=ds.count) if ds else None


def read_text(data):
    """CSV co the den voi nhieu kieu ma hoa (Excel tren Windows hay luu UTF-8 co BOM hoac UTF-16)."""
    for enc in ("utf-8-sig", "utf-16", "cp1258", "cp1252"):
        try:
            text = data.decode(enc)
            if "\x00" not in text:
                return text, enc
        except UnicodeDecodeError:
            continue
    return None, None


def excel_grid(data):
    df = pd.read_excel(io.BytesIO(data), header=None, dtype=str).fillna("")
    return [[str(v).strip() for v in row] for row in df.values.tolist()]


def week_of(text):
    m = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})", str(text))
    if not m:
        return None, None
    a, b = datetime.strptime(m[1], "%d/%m/%Y"), datetime.strptime(m[2], "%d/%m/%Y")
    return a, b


def doc_value(grid, label):
    for row in grid[:8]:
        for v in row:
            if v.startswith(label):
                return v.split(":", 1)[1].strip() if ":" in v else ""
    return None


# ---------------------------------------------------------------- nhan dang
def identify(name, data, src=None):
    """Nhan dang mot tep (ten goc + noi dung byte). Khong ghi gi xuong dia."""
    ext = Path(name).suffix.lower()
    bmap, names = branch_map(src)
    r = Result()
    try:
        if ext == ".json":
            return _json(name, data, bmap, r)
        if ext == ".csv":
            return _csv(name, data, bmap, r)
        if ext in (".xlsx", ".xlsm"):
            return _excel(name, data, bmap, names, r)
        if ext == ".xls":
            r.errors.append("Excel đời cũ (.xls) không được hỗ trợ; lưu lại dưới dạng .xlsx.")
            return r
    except Exception as e:  # tep hong, khong doc duoc
        r.errors.append(f"Không đọc được tệp: {type(e).__name__}: {str(e)[:160]}")
        return r
    r.errors.append(f"Định dạng {ext or 'không có phần mở rộng'} không thuộc nguồn nào (JSON, CSV, Excel).")
    return r


def _json(name, data, bmap, r):
    doc = json.loads(data.decode("utf-8-sig"))
    if isinstance(doc, list) and doc and isinstance(doc[0], dict) and "receipt_no" in doc[0]:
        r.source = "pos"
        miss = sorted({k for k in BY_KEY["pos"]["required"] for rec in doc if k not in rec})
        if miss:
            r.errors.append("Hóa đơn thiếu trường bắt buộc: " + ", ".join(miss))
        if not any("total_paid" in x or "grand_total" in x for x in doc):
            r.errors.append("Hóa đơn không có trường tổng tiền (total_paid hoặc grand_total).")
        prefixes = {str(x.get("terminal_id", ""))[:6] for x in doc}
        unknown = prefixes - set(bmap.pos_terminal_prefix)
        if unknown:
            r.errors.append("Mã máy POS không thuộc chi nhánh nào: " + ", ".join(sorted(unknown)))
        if len(prefixes) > 1:
            r.errors.append("Một tệp POS chỉ được chứa hóa đơn của một chi nhánh.")
        d = mode_date(x.get("txn_time") for x in doc)
        if d is None:
            r.errors.append("Không đọc được ngày giao dịch (txn_time).")
        if not r.errors:
            p = prefixes.pop()
            r.target = f"pos/{p}/pos_export_{d:%Y-%m-%d}.json"
            r.facts = {"ngày": d, "chi nhánh": int(bmap.set_index("pos_terminal_prefix").branch_id[p]), "số dòng": len(doc)}
        return r
    if isinstance(doc, dict) and isinstance(doc.get("data"), list) and doc["data"] and "order_uuid" in doc["data"][0]:
        r.source = "app"
        rows = doc["data"]
        miss = sorted({k for k in BY_KEY["app"]["required"] for rec in rows if k not in rec})
        if miss:
            r.errors.append("Đơn App thiếu trường bắt buộc: " + ", ".join(miss))
        codes = {(x.get("branch_ref") or {}).get("code") for x in rows}
        unknown = codes - set(bmap.app_branch_code)
        if unknown:
            r.notes.append("Có mã chi nhánh lạ, các đơn này sẽ bị cách ly ở tầng Silver: " + ", ".join(map(str, unknown)))
        local = [(parse_date(x.get("created_at_utc")) or datetime.min) + timedelta(hours=7) for x in rows]
        d = mode_date(t.isoformat() for t in local if t.year > 1)
        if d is None:
            r.errors.append("Không đọc được thời điểm đặt đơn (created_at_utc).")
        if not r.errors:
            r.target = f"owned_app/orders_{d:%Y%m%d}.json"
            r.facts = {"ngày": d, "số dòng": len(rows)}
        return r
    if isinstance(doc, dict) and {"date", "precipitation_mm", "condition"} <= set(doc):
        r.source = "weather"
        d = parse_date(doc["date"])
        if d is None:
            r.errors.append("Không đọc được ngày.")
        else:
            r.target = f"external/weather/weather_hcm_{d:%Y%m%d}.json"
            r.facts = {"ngày": d.date(), "số dòng": 1}
        return r
    r.errors.append("Tệp JSON không khớp hợp đồng của POS, App hay thời tiết.")
    return r


def _csv(name, data, bmap, r):
    text, enc = read_text(data)
    if text is None:
        r.errors.append("Không xác định được bảng mã ký tự của tệp CSV.")
        return r
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        r.errors.append("Tệp CSV rỗng.")
        return r
    head = [h.strip() for h in rows[0]]
    body = [x for x in rows[1:] if any(c.strip() for c in x)]
    if enc not in ("utf-8-sig",):
        r.notes.append(f"Tệp lưu theo bảng mã {enc}; sẽ được chuyển về UTF-8 khi đưa vào vùng tiếp nhận.")
    if set(BY_KEY["grab"]["required"]) <= set(head) or "Merchant Store Name" in head:
        r.source = "grab"
        miss = [c for c in BY_KEY["grab"]["required"] if c not in head]
        if miss:
            r.errors.append("Báo cáo GrabFood thiếu cột: " + ", ".join(miss))
            return r
        weeks = {x[head.index("Week")] for x in body}
        a, b = week_of(next(iter(weeks), ""))
        if len(weeks) != 1 or a is None:
            r.errors.append("Một báo cáo GrabFood phải đúng một kỳ tuần, dạng dd/mm/yyyy - dd/mm/yyyy.")
            return r
        unknown = {x[head.index("Merchant Store Name")] for x in body} - set(bmap.grab_store_name)
        if unknown:
            r.notes.append("Cửa hàng không có trong bảng ánh xạ, dòng này sẽ bị cách ly: " + ", ".join(sorted(unknown)))
        r.target = f"grabfood/GrabFood_Settlement_{a:%Y%m%d}_{b:%Y%m%d}.csv"
        r.facts = {"ngày": a.date(), "số dòng": len(body)}
        return r
    if set(BY_KEY["timekeeping"]["required"]) <= set(head) or "employee_code" in head:
        r.source = "timekeeping"
        miss = [c for c in BY_KEY["timekeeping"]["required"] if c not in head]
        if miss:
            r.errors.append("Tệp chấm công thiếu cột: " + ", ".join(miss))
            return r
        codes = {x[head.index("branch_code")] for x in body}
        if len(codes) != 1:
            r.errors.append("Một tệp chấm công chỉ được chứa một chi nhánh.")
            return r
        code = codes.pop()
        if code not in set(bmap.timekeeping_branch_code):
            r.errors.append(f"Mã chi nhánh máy chấm công không có trong bảng ánh xạ: {code}")
            return r
        d = mode_date(x[head.index("event_time")] for x in body)
        if d is None:
            r.errors.append("Không đọc được thời điểm quẹt thẻ (event_time).")
            return r
        r.target = f"timekeeping/{code}/punch_{code}_{d:%Y%m%d}.csv"
        r.facts = {"ngày": d, "chi nhánh": int(bmap.set_index("timekeeping_branch_code").branch_id[code]),
                   "số dòng": len(body)}
        return r
    for entity, cols in MASTER_HEADERS.items():
        if head == cols:
            r.source = "master"
            m = re.search(r"(20\d{6})", name)
            if not m:
                r.errors.append("Danh mục cần ngày hiệu lực trong tên tệp, dạng YYYYMMDD.")
                return r
            r.target = f"master_data/{entity}/{entity}_{m[1]}.csv"
            r.facts = {"ngày": datetime.strptime(m[1], "%Y%m%d").date(), "số dòng": len(body), "danh mục": entity}
            return r
    r.errors.append("Tiêu đề cột không khớp hợp đồng của nguồn CSV nào (GrabFood, chấm công, danh mục): "
                    + ", ".join(head[:6]))
    return r


def _excel(name, data, bmap, names, r):
    grid = excel_grid(data)
    flat = " ".join(" ".join(row) for row in grid[:8])
    if "ShopeeFood" in flat or any("Mã cửa hàng" in row for row in grid[:8]):
        r.source = "shopee"
        hi = next((i for i, row in enumerate(grid[:10]) if "Mã cửa hàng" in row), None)
        head = grid[hi] if hi is not None else []
        miss = [c for c in BY_KEY["shopee"]["required"] if c not in head]
        if miss:
            r.errors.append("Báo cáo ShopeeFood thiếu cột: " + ", ".join(miss))
            return r
        a, b = week_of(doc_value(grid, "Kỳ đối soát") or "")
        if a is None:
            r.errors.append("Không tìm thấy dòng 'Kỳ đối soát: dd/mm/yyyy - dd/mm/yyyy'.")
            return r
        body = [x for x in grid[hi + 1:] if x[0]]
        unknown = {x[0] for x in body} - set(bmap.shopee_store_code)
        if unknown:
            r.notes.append("Mã cửa hàng không có trong bảng ánh xạ, dòng này sẽ bị cách ly: " + ", ".join(sorted(unknown)))
        r.target = f"shopeefood/ShopeeFood_DoiSoat_{a:%Y%m%d}_{b:%Y%m%d}.xlsx"
        r.facts = {"ngày": a.date(), "số dòng": len(body)}
        return r
    if "PHIẾU NHẬP KHO" in flat or "PHIẾU KIỂM KÊ" in flat:
        stock = "PHIẾU KIỂM KÊ" in flat
        r.source = "stock" if stock else "receipt_a"
        hi = next((i for i, row in enumerate(grid[:12]) if "Tên nguyên liệu" in row), None)
        head = grid[hi] if hi is not None else []
        miss = [c for c in BY_KEY[r.source]["required"] if c not in head]
        if miss:
            r.errors.append("Phiếu thiếu cột: " + ", ".join(miss))
            return r
        bname = doc_value(grid, "Chi nhánh")
        d = parse_date(doc_value(grid, "Ngày kiểm kê" if stock else "Ngày nhập") or "")
        if bname not in names:
            r.errors.append(f"Tên chi nhánh trên phiếu không có trong danh mục: {bname or '(trống)'}")
        if d is None:
            r.errors.append("Không đọc được ngày trên phiếu.")
        if r.errors:
            return r
        b = names[bname]
        folder = bmap.set_index("branch_id").warehouse_folder[b]
        kind = "stock_counts" if stock else "warehouse_receipts"
        stem = "KiemKe" if stock else "NhapKho"
        r.target = f"{kind}/{folder}/{stem}_{folder}_{d:%Y%m%d}.xlsx"
        rows = [x for x in grid[hi + 1:] if x[0].isdigit()]
        r.facts = {"ngày": d.date(), "chi nhánh": b, "số dòng": len(rows)}
        return r
    if grid and [c.lower() for c in grid[0][:5]] == BY_KEY["receipt_b"]["required"]:
        r.source = "receipt_b"
        m = re.search(r"CN(\d{2})", name.upper())
        if not m:
            r.errors.append("Mẫu sổ B không ghi chi nhánh trong tệp: tên tệp phải có mã chi nhánh dạng CNxx.")
            return r
        folder = f"CN{m[1]}"
        if folder not in set(bmap.warehouse_folder):
            r.errors.append(f"Mã chi nhánh {folder} không có trong bảng ánh xạ.")
            return r
        d = mode_date(x[0] for x in grid[1:] if x[0])
        if d is None:
            r.errors.append("Không đọc được ngày nhập (cột date).")
            return r
        r.target = f"warehouse_receipts/{folder}/receipts_{folder}_{d:%Y%m%d}.xlsx"
        r.facts = {"ngày": d, "chi nhánh": int(bmap.set_index("warehouse_folder").branch_id[folder]),
                   "số dòng": len([x for x in grid[1:] if x[0]])}
        return r
    if any("Merchant Store Name" in row for row in grid[:3]):
        r.errors.append("Giống báo cáo GrabFood nhưng GrabFood gửi CSV; hãy tải lên đúng tệp CSV gốc từ cổng đối tác.")
        return r
    r.errors.append("Tệp Excel không khớp hợp đồng của báo cáo ShopeeFood, sổ nhập kho hay phiếu kiểm kê.")
    return r


# ---------------------------------------------------------------- dung cho buoc nap
INGEST_KEY = {"pos_receipts": "pos", "app_orders": "app", "grab_settlement": "grab", "shopee_settlement": "shopee",
              "warehouse_receipts_form": "receipt_a", "warehouse_receipts_table": "receipt_b", "stock_counts": "stock",
              "timekeeping_punches": "timekeeping", "weather_daily": "weather"}


def check_for_ingest(table, path, src):
    """Tep nam dung thu muc cua mot nguon: co dung hop dong cua nguon do khong. Tra ve danh sach loi (rong = hop le).
    Chi xet loi lam tep vo nghia (sai nguon, thieu cot); loi tung dong de tang Silver cach ly."""
    key = INGEST_KEY.get(table)
    if key is None:          # danh muc tru so: chi can doc duoc
        return []
    data = Path(path).read_bytes()
    if key == "pos" and data.strip() == b"[]":
        return []            # ngay khong co hoa don nao (nghi, mat dien): hop le, cua chan chat luong bao thieu
    r = identify(Path(path).name, data, src)
    if r.source is None and any(e.startswith("Không đọc được tệp") for e in r.errors):
        return []            # tep hong: de bo doc bao loi doc (status 'failed'), khong tinh la sai hop dong
    if r.source != key:
        found = BY_KEY[r.source]["system"] if r.source else "không nhận dạng được"
        return [f"Nằm trong thư mục của {BY_KEY[key]['system']} nhưng nội dung là: {found}. " + "; ".join(r.errors)]
    errs = [e for e in r.errors if "thiếu" in e or "Không đọc được" in e or "không khớp" in e]
    rel = Path(path).relative_to(src).as_posix()
    if r.ok and r.target != rel:   # ten tep noi mot dang, noi dung mot neo (vd chep tep cu doi ten ngay)
        errs.append(f"Tên hoặc vị trí tệp không khớp nội dung: nội dung thuộc {r.target}. Nạp sẽ ghi sai ngày, "
                    "sai chi nhánh hoặc đếm hai lần.")
    return errs
