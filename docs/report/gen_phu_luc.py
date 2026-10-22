"""Sinh Phu luc B (tu dien du lieu tang Gold) va Phu luc C (quy tac cach ly, kiem thu) cho bao cao.
Ten cot, kieu lay tu kho DuckDB cua tap phat trien; kiem thu lay tu manifest dbt; y nghia cot viet tay o MEANING.
Ket qua thay the hai muc "Phu luc B", "Phu luc C" trong 07_tailieu_phuluc.md (giu nguyen phan con lai).

    .venv/Scripts/python docs/report/gen_phu_luc.py
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DB = ROOT / "data" / "calibration" / "warehouse" / "fastfat.duckdb"
MANIFEST = ROOT / "dbt" / "target_calibration" / "manifest.json"

TABLES = [
    ("fact_order", "Một đơn hàng ở một kênh (hóa đơn POS hoặc đơn App)"),
    ("fact_order_line", "Một dòng món trong một đơn"),
    ("fact_marketplace_settlement", "Một chi nhánh × một sàn × một tuần đối soát"),
    ("fact_inventory_receipt", "Một dòng phiếu nhập kho hợp lệ"),
    ("fact_stock_count", "Một chi nhánh × một nguyên liệu × một lần kiểm kê"),
    ("fact_labor_shift", "Một nhân viên × một ca làm việc"),
    ("dim_date", "Một ngày"),
    ("dim_branch", "Một chi nhánh"),
    ("dim_channel", "Một kênh bán"),
    ("dim_menu_item", "Một phiên bản của một món (SCD loại 2)"),
    ("dim_employee", "Một phiên bản của một nhân viên (SCD loại 2)"),
    ("dim_ingredient", "Một nguyên liệu"),
    ("dim_customer", "Một khách hàng của ứng dụng"),
]

# y nghia dung chung cho cot cung ten o nhieu bang; (bang, cot) de ghi de khi khac nghia
MEANING = {
    "branch_id": "Mã chi nhánh theo trụ sở (1–11)",
    "date_day": "Ngày phát sinh theo giờ Việt Nam",
    "date_key": "Khóa ngày dạng số yyyymmdd",
    "channel": "Kênh: WALKIN, APP, GRABFOOD, SHOPEEFOOD",
    "order_key": "Khóa đơn hàng, duy nhất trên mọi hệ thống",
    "source_system": "Hệ thống gốc: POS hoặc APP",
    "source_order_id": "Số hóa đơn POS hoặc mã đơn App ở hệ thống gốc",
    "ordered_at_local": "Thời điểm đặt hoặc thanh toán, giờ Việt Nam",
    "order_hour": "Giờ trong ngày của đơn",
    "shift_name": "Ca làm việc: sáng hoặc tối",
    "order_type": "Hình thức: ăn tại chỗ, mang đi, giao hàng",
    "cashier_staff_id": "Mã nhân viên thu ngân (đơn POS)",
    "cashier_employee_sk": "Khóa phiên bản nhân viên thu ngân tại ngày bán",
    "customer_id": "Mã khách hàng đã băm (chỉ đơn App)",
    "is_first_order": "Đơn đầu tiên của khách trên ứng dụng",
    "order_status": "Trạng thái chuẩn hóa: COMPLETED, VOIDED, REFUNDED, CANCELLED_BY_STORE, CANCELLED_BY_CUSTOMER",
    "cancel_reason": "Lý do hủy theo hệ thống gốc",
    "is_completed": "Đơn hoàn thành, được tính doanh thu",
    "is_prepared": "Bếp đã làm món (kể cả đơn bị hủy, hoàn sau khi làm), dùng để tính tiêu hao định mức",
    "payment_method": "Phương thức thanh toán",
    "gross_sales": "Tiền món trước giảm giá",
    "discount_amount": "Tiền giảm giá",
    "promo_code": "Mã khuyến mãi",
    "net_sales": "Doanh thu thuần: tiền món sau giảm giá, chỉ đơn hoàn thành",
    "refund_amount": "Tiền hoàn cho khách",
    "delivery_fee": "Phí giao hàng khách trả (đơn App)",
    "minutes_to_void": "Số phút từ lúc thanh toán đến lúc hủy hóa đơn",
    "prep_minutes": "Thời gian chuẩn bị đơn, phút (đơn App)",
    "rating": "Điểm đánh giá của khách cho đơn (đơn App)",
    "n_lines": "Số dòng món trong đơn",
    "order_line_key": "Khóa dòng món",
    "line_no": "Số thứ tự dòng trong đơn",
    "item_id": "Mã món theo trụ sở",
    "menu_item_sk": "Khóa phiên bản món có hiệu lực tại ngày bán",
    "category": "Nhóm món: Main, Side, Drink, Combo",
    "is_combo": "Món combo, được tách thành món thành phần khi tính tiêu hao",
    "qty": "Số lượng",
    "unit_price": "Đơn giá",
    "line_discount_amount": "Giảm giá phân bổ cho dòng",
    "line_amount": "Thành tiền của dòng",
    "is_item_void": "Món bị hủy riêng trong đơn",
    "is_revenue_line": "Dòng được tính doanh thu",
    "standard_unit_cost": "Giá vốn chuẩn mỗi đơn vị",
    "cogs_standard": "Giá vốn định mức của dòng theo phiên bản món tại ngày bán",
    "settlement_key": "Khóa dòng đối soát",
    "week_start": "Ngày đầu tuần (thứ Hai)",
    "week_end": "Ngày cuối tuần (Chủ nhật)",
    "report_generated_date": "Ngày sàn tạo báo cáo",
    "orders_completed": "Số đơn hoàn thành theo báo cáo sàn",
    "orders_cancelled": "Số đơn bị hủy theo báo cáo sàn",
    "commission": "Phí hoa hồng sàn thu",
    "ads_spend": "Chi phí quảng cáo trên sàn",
    "merchant_promo": "Khuyến mãi do cửa hàng tài trợ",
    "adjustment": "Khoản điều chỉnh",
    "net_payout": "Tiền cửa hàng thực nhận",
    "avg_prep_min": "Thời gian chuẩn bị trung bình theo sàn, phút",
    "store_rating": "Điểm đánh giá cửa hàng trên sàn",
    "effective_commission_rate": "Tỷ lệ hoa hồng hiệu dụng = hoa hồng / doanh thu món",
    "contract_commission_rate": "Tỷ lệ hoa hồng trong hợp đồng có hiệu lực",
    "commission_rate_gap": "Tỷ lệ hiệu dụng trừ tỷ lệ hợp đồng",
    "commission_overcharge": "Hoa hồng thu thừa = chênh lệch tỷ lệ × doanh thu món",
    "receipt_line_id": "Khóa dòng phiếu nhập",
    "ingredient_id": "Mã nguyên liệu theo trụ sở",
    "ingredient_match_method": "Cách nhận diện tên nguyên liệu: khớp chính xác, bảng biến thể, khớp mờ",
    "quantity": "Số lượng theo đơn vị chuẩn",
    "unit": "Đơn vị chuẩn",
    "expiry_date": "Hạn sử dụng",
    "supplier": "Nhà cung cấp",
    "count_key": "Khóa dòng kiểm kê",
    "counted_qty": "Số lượng tồn đếm được (trống nếu không đếm)",
    "is_not_counted": "Ô kiểm kê để trống",
    "counted_by": "Người kiểm kê",
    "counted_value": "Giá trị tồn đếm được theo giá chuẩn",
    "shift_key": "Khóa ca làm việc",
    "staff_id": "Mã nhân viên theo trụ sở",
    "employee_sk": "Khóa phiên bản nhân viên có hiệu lực tại ngày làm",
    "role": "Vai trò: thu ngân, bếp, phục vụ, quản lý ca",
    "check_in_at": "Giờ vào",
    "check_out_at": "Giờ ra (trống nếu quên quẹt)",
    "is_missing_checkout": "Thiếu lượt ra",
    "hours_worked": "Số giờ theo chấm công",
    "is_hours_imputed": "Số giờ được nội suy do thiếu lượt ra",
    "hours_paid": "Số giờ dùng để tính lương (đã nội suy nếu thiếu)",
    "hourly_wage": "Lương giờ theo phiên bản nhân viên",
    "labor_cost": "Chi phí nhân công của ca",
    "iso_week": "Số tuần ISO",
    "month_no": "Tháng",
    "iso_dow": "Thứ trong tuần (1 = thứ Hai)",
    "dow_name": "Tên thứ",
    "is_weekend": "Cuối tuần",
    "holiday_name": "Tên ngày lễ",
    "is_holiday": "Ngày lễ",
    "weather_condition": "Tình trạng thời tiết",
    "precipitation_mm": "Lượng mưa, mm",
    "temp_max_c": "Nhiệt độ cao nhất, °C",
    "is_rain": "Ngày có mưa",
    "branch_name": "Tên chi nhánh",
    "district": "Quận",
    "store_class": "Hạng chi nhánh: A lớn, B vừa, C nhỏ",
    "latitude": "Vĩ độ",
    "longitude": "Kinh độ",
    "open_date": "Ngày khai trương",
    "pos_terminal_prefix": "Tiền tố mã máy POS",
    "app_branch_code": "Mã chi nhánh trên ứng dụng",
    "grab_store_name": "Tên cửa hàng trên GrabFood",
    "shopee_store_code": "Mã cửa hàng trên ShopeeFood",
    "timekeeping_branch_code": "Mã chi nhánh trên máy chấm công",
    "channel_name": "Tên kênh",
    "channel_group": "Nhóm kênh: tại cửa hàng, giao hàng",
    "source_systems": "Hệ thống nguồn ghi nhận kênh",
    "has_commission": "Kênh chịu hoa hồng sàn",
    "item_name": "Tên món",
    "price": "Giá bán của phiên bản",
    "standard_cost": "Giá vốn định mức mỗi phần",
    "standard_cost_pct": "Giá vốn định mức / giá bán",
    "valid_from": "Ngày bắt đầu hiệu lực của phiên bản",
    "valid_to": "Ngày kết thúc hiệu lực (9999-12-31 nếu còn hiệu lực)",
    "is_current": "Phiên bản hiện hành",
    "first_seen_snapshot": "Ảnh chụp danh mục đầu tiên có phiên bản này",
    "staff_code": "Mã nhân viên dạng NV0xxx (như trên POS)",
    "staff_name": "Tên nhân viên",
    "hire_date": "Ngày vào làm",
    "ingredient_code": "Mã nguyên liệu trên phiếu kiểm kê (NLxx)",
    "ingredient_name": "Tên chuẩn của nguyên liệu",
    "ingredient_category": "Nhóm nguyên liệu",
    "is_fresh": "Hàng tươi",
    "shelf_life_days": "Hạn dùng, ngày",
    "first_order_date": "Ngày đặt đơn đầu tiên",
    "first_branch_id": "Chi nhánh của đơn đầu tiên",
    "acquisition_source": "Nguồn thu hút khách (UTM)",
    "first_device_platform": "Nền tảng thiết bị ở đơn đầu tiên",
    ("fact_inventory_receipt", "unit_price"): "Đơn giá nhập",
    ("fact_inventory_receipt", "line_amount"): "Thành tiền nhập",
    ("fact_marketplace_settlement", "gross_sales"): "Doanh thu món theo báo cáo sàn",
    ("dim_employee", "branch_id"): "Chi nhánh làm việc của phiên bản",
    ("fact_stock_count", "date_day"): "Ngày kiểm kê",
    ("fact_inventory_receipt", "date_day"): "Ngày nhập",
    ("fact_labor_shift", "date_day"): "Ngày làm việc",
}
TYPES = {"VARCHAR": "chuỗi", "INTEGER": "số nguyên", "BIGINT": "số nguyên", "UBIGINT": "số nguyên",
         "HUGEINT": "số nguyên", "DOUBLE": "số thực", "DATE": "ngày", "TIMESTAMP": "ngày giờ", "BOOLEAN": "đúng/sai"}

QUARANTINE = [
    ("POS", "thieu_so_hoa_don, trung_so_hoa_don", "Thiếu hoặc trùng số hóa đơn"),
    ("POS", "thoi_gian_khong_doc_duoc, tong_tien_khong_doc_duoc", "Không đọc được thời gian, tổng tiền ở cả hai định dạng"),
    ("POS", "tong_tien_am, hoa_don_khong_co_mon", "Tổng tiền âm; hóa đơn không có dòng món"),
    ("POS, App, chấm công, kho", "khong_anh_xa_duoc_chi_nhanh", "Mã chi nhánh không có trong bảng ánh xạ"),
    ("App", "thieu_ma_don, trung_ma_don, don_khong_co_mon", "Thiếu, trùng mã đơn; đơn không có món"),
    ("Chấm công", "thieu_ma_nhan_vien, loai_su_kien_khong_hop_le", "Thiếu mã nhân viên; loại sự kiện khác vào, ra"),
    ("Chấm công", "quet_trung", "Lượt quẹt cùng loại của cùng nhân viên lặp lại trong vòng 5 phút"),
    ("Sổ nhập kho", "chi_nhanh_tieu_de_khac_thu_muc", "Chi nhánh trên tiêu đề phiếu khác thư mục chứa tệp"),
    ("Sổ nhập kho", "khong_nhan_dien_duoc_nguyen_lieu", "Tên nguyên liệu không khớp ở cả ba tầng ánh xạ"),
    ("Sổ nhập kho", "so_luong_khong_hop_le, don_vi_khong_khop_danh_muc", "Số lượng trống hoặc không dương; đơn vị khác danh mục"),
    ("Sổ nhập kho", "nghi_go_gam_vao_cot_kg", "Số lượng tính bằng kg lớn hơn 20 lần trung vị của cùng nguyên liệu"),
    ("Phiếu kiểm kê", "ngay_kiem_ke_khong_doc_duoc, ma_nguyen_lieu_khong_ton_tai, don_vi_khong_khop_danh_muc",
     "Không đọc được ngày; mã nguyên liệu không có trong danh mục; đơn vị khác danh mục"),
]
TEST_NAMES = {"not_null": "Không rỗng", "unique": "Duy nhất", "relationships": "Toàn vẹn tham chiếu",
              "accepted_values": "Miền giá trị", "unique_combination": "Khóa ghép duy nhất"}


def esc(s):
    return s.replace("|", "/")


def main():
    out = ["## Phụ lục B. Từ điển dữ liệu tầng Gold", "",
           "Tên cột và kiểu dữ liệu lấy trực tiếp từ kho dữ liệu của tập phát triển. Các khóa có hậu tố `_sk` là khóa "
           "thay thế của phiên bản trong bảng chiều thay đổi chậm.", ""]
    con = duckdb.connect(str(DB), read_only=True)
    for i, (t, grain) in enumerate(TABLES, 1):
        cols = con.execute(f"describe gold.{t}").fetchall()
        n = con.execute(f"select count(*) from gold.{t}").fetchone()[0]
        out += [f"TABLE: Bảng B.{i}. Bảng {t}: {grain[0].lower() + grain[1:]} ({n:,} dòng ở tập phát triển)".replace(",", "."),
                "WIDTHS: 4.4,2,8.6", "| Cột | Kiểu | Ý nghĩa |"]
        for c, typ, *_ in cols:
            meaning = MEANING.get((t, c)) or MEANING.get(c)
            if meaning is None:
                raise SystemExit(f"thieu y nghia cot {t}.{c}")
            out.append(f"| `{c}` | {TYPES.get(typ, typ.lower())} | {esc(meaning)} |")
        out.append("")
    con.close()

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out += ["## Phụ lục C. Danh sách quy tắc chất lượng và kiểm thử dữ liệu", "",
            "### C.1. Quy tắc cách ly ở tầng Silver", "",
            "Mỗi dòng vi phạm được gắn mã lỗi ở cột `dq_issue` và chuyển vào bảng `silver.silver_quarantine`. "
            "Một dòng chỉ nhận mã của quy tắc đầu tiên mà nó vi phạm.", "",
            "TABLE: Bảng C.1. Các quy tắc cách ly", "WIDTHS: 2.6,5.4,6", "| Nguồn | Mã lỗi | Điều kiện |"]
    out += [f"| {a} | `{b}` | {c} |" for a, b, c in QUARANTINE]
    out += ["", "### C.2. Kiểm thử dbt", "",
            "Bảng C.2 liệt kê theo từng mô hình các kiểm thử dựng sẵn của dbt và kiểm thử tổng quát khóa ghép, viết bằng "
            "macro `test_unique_combination`. Bảng C.3 liệt kê các kiểm thử luật nghiệp vụ trong thư mục `dbt/tests/`; "
            "mỗi kiểm thử là một câu SQL trả về các dòng vi phạm và đạt khi kết quả rỗng.", ""]
    tests = [n for n in m["nodes"].values() if n["resource_type"] == "test"]
    by_model = defaultdict(Counter)
    singular = []
    for n in tests:
        meta = n.get("test_metadata") or {}
        if meta:
            model = (n.get("attached_node") or "").split(".")[-1] or "?"
            by_model[model][meta["name"]] += 1
        else:
            singular.append(n["name"])
    out += ["TABLE: Bảng C.2. Kiểm thử dựng sẵn và kiểm thử tổng quát theo mô hình", "WIDTHS: 5.4,1.5,1.5,1.9,1.7,1.7,1.3",
            "| Mô hình | Không rỗng | Duy nhất | Toàn vẹn tham chiếu | Miền giá trị | Khóa ghép | Tổng |"]
    order = ["not_null", "unique", "relationships", "accepted_values", "unique_combination"]
    tot = Counter()
    for model in sorted(by_model, key=lambda x: (not x.startswith(("stg_", "silver")), x)):
        c = by_model[model]
        tot.update(c)
        out.append(f"| `{model}` | " + " | ".join(str(c.get(k, 0) or "") for k in order) + f" | {sum(c.values())} |")
    out.append("| Tổng | " + " | ".join(str(tot.get(k, 0)) for k in order) + f" | {sum(tot.values())} |")
    desc = {
        "assert_silver_rows_conserved": "Số dòng Bronze = Silver + cách ly + dòng cấu trúc cho mọi nguồn",
        "assert_pos_subtotal_matches_lines": "Tạm tính mỗi hóa đơn POS bằng tổng thành tiền các dòng món",
        "assert_grab_one_row_per_branch_week": "Báo cáo GrabFood có đúng một dòng cho mỗi chi nhánh × tuần",
        "assert_grab_payout_reconciles": "Tiền thực nhận GrabFood = doanh thu món − hoa hồng − quảng cáo − khuyến mãi + điều chỉnh",
        "assert_shopee_payout_reconciles": "Như trên, cho ShopeeFood",
        "assert_scd2_no_overlap": "Các phiên bản của cùng món, cùng nhân viên không chồng lấn thời gian",
        "assert_gold_net_sales_reconciles": "Doanh thu thuần Gold bằng tổng tính từ Silver theo chi nhánh × ngày",
    }
    out += ["", f"TABLE: Bảng C.3. Kiểm thử luật nghiệp vụ dạng câu SQL ({len(singular)} kiểm thử)", "WIDTHS: 6,8",
            "| Kiểm thử | Nội dung |"]
    for s in sorted(singular):
        out.append(f"| `{s}` | {desc.get(s, '')} |")
    out.append("")
    target = HERE / "07_tailieu_phuluc.md"
    text = target.read_text(encoding="utf-8")
    a, b = text.index("## Phụ lục B."), text.index("## Phụ lục D.")
    target.write_text(text[:a] + "\n".join(out) + "\n" + text[b:], encoding="utf-8")
    print(f"da cap nhat Phu luc B, C: {len(TABLES)} bang Gold, {len(tests)} kiem thu")


if __name__ == "__main__":
    main()
