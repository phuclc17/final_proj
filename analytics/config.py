"""Bo thong so giam sat chung. Cac nguong o day CHI duoc chon tren tap phat trien (calibration)."""

# ---------------------------------------------------------------- nguong
Z_WATCH = 2.0            # can theo doi
Z_ALERT = 3.0            # bat thuong
SCORE_ALERT = 3.5        # diem bang chung cua mot gia thuyet tu muc nay tro len -> phat canh bao
                         # chot 11/10/2026: nguong cho F1 cao nhat tren tap phat trien (quet 2,0-5,0; 3,5 -> F1 0,788),
                         # TRUOC khi chay tap kiem tra. Khong sua sau khi da xem ket qua tap kiem tra.
MIN_BASELINE_WEEKS = 4   # can it nhat 4 tuan lich su moi co muc nen dang tin
COMMISSION_TOLERANCE = 0.005  # lech hoa hong > 0,5 diem % so voi hop dong = sai hop dong (luat doi soat)
HIGH_VALUE_COST = 80_000      # nhom nguyen lieu gia tri cao: don gia dinh muc >= 80.000 d / don vi
MIN_CASHIER_RECEIPTS = 30     # thu ngan it hon so hoa don nay trong tuan thi khong danh gia
CASHIER_RATE_FLOOR = 0.005    # san ty le huy/hoan ky vong, tranh ky vong ~0

# ---------------------------------------------------------------- bo chi so giam sat
# direction: -1 = thap bat thuong la xau, +1 = cao bat thuong la xau, 0 = lech ca hai chieu deu dang chu y
INDICATORS = [
    # ket qua kinh doanh
    ("net_sales", "Doanh thu thuần", "Kết quả kinh doanh", 0),
    ("orders", "Số đơn hoàn thành", "Kết quả kinh doanh", 0),
    ("aov", "Giá trị đơn bình quân (AOV)", "Kết quả kinh doanh", 0),
    ("net_sales_walkin", "Doanh thu tại quầy", "Kết quả kinh doanh", 0),
    ("net_sales_app", "Doanh thu App", "Kết quả kinh doanh", 0),
    ("net_sales_grabfood", "Doanh thu Grab ghi trên POS", "Kết quả kinh doanh", 0),
    ("net_sales_shopeefood", "Doanh thu Shopee ghi trên POS", "Kết quả kinh doanh", 0),
    # van hanh va nhan su
    ("kitchen_evening", "Số ca bếp tối", "Vận hành và nhân sự", -1),
    ("shifts_evening", "Số ca tối có chấm công", "Vận hành và nhân sự", -1),
    ("orders_per_evening_shift", "Số đơn tối mỗi ca tối", "Vận hành và nhân sự", 1),
    ("app_avg_prep_min", "Thời gian chuẩn bị đơn App", "Vận hành và nhân sự", 1),
    ("grabfood_avg_prep_min", "Thời gian chuẩn bị Grab", "Vận hành và nhân sự", 1),
    ("app_store_cancel_rate", "Tỷ lệ cửa hàng tự hủy đơn App", "Vận hành và nhân sự", 1),
    ("app_wait_cancel_rate", "Tỷ lệ khách hủy vì chờ lâu", "Vận hành và nhân sự", 1),
    ("app_avg_rating", "Điểm đánh giá App", "Trải nghiệm khách hàng", -1),
    ("grabfood_rating", "Điểm đánh giá Grab", "Trải nghiệm khách hàng", -1),
    ("shopeefood_rating", "Điểm đánh giá Shopee", "Trải nghiệm khách hàng", -1),
    # doi soat san
    ("grabfood_pos_coverage", "Độ phủ POS đơn Grab", "Đối soát sàn", -1),
    ("shopeefood_pos_coverage", "Độ phủ POS đơn Shopee", "Đối soát sàn", -1),
    # quay thu ngan
    ("void_rate", "Tỷ lệ hủy hóa đơn tại quầy", "Quầy thu ngân", 1),
    ("refund_rate", "Tỷ lệ hoàn tiền tại quầy", "Quầy thu ngân", 1),
    ("discount_rate", "Tỷ lệ giảm giá trên doanh thu gộp", "Quầy thu ngân", 1),
    # chi phi
    ("cogs_pct", "COGS% định mức", "Chi phí", 1),
    ("labor_pct", "Labor% (lương giờ trực tiếp)", "Chi phí", 1),
]

# ---------------------------------------------------------------- gia thuyet nguyen nhan ("dau van tay")
# (ma, ten, cach gop bang chung, [(kpi, chieu bat thuong)])
FINGERPRINTS = {
    "P3": ("Thiếu nhân sự, bếp quá tải, mất đơn", "mean",
           [("kitchen_evening", -1), ("app_avg_prep_min", 1), ("grabfood_avg_prep_min", 1),
            ("app_store_cancel_rate", 1), ("app_wait_cancel_rate", 1)]),
    "P1b": ("Đơn sàn hoàn thành nhưng không được ghi vào POS", "max",
            [("grabfood_pos_coverage", -1), ("shopeefood_pos_coverage", -1)]),
    "P5": ("Gian lận tại quầy: hủy, hoàn, giảm giá bất thường", "max",
           [("void_rate", 1), ("refund_rate", 1), ("discount_rate", 1)]),
}
CAUSE_NAMES = {
    "P1a": "Sàn thu hoa hồng sai hợp đồng",
    "P1b": FINGERPRINTS["P1b"][0],
    "P2": "Hao hụt nguyên liệu vượt định mức",
    "P3": FINGERPRINTS["P3"][0],
    "P4": "Thất thoát nguyên liệu giá trị cao",
    "P5": FINGERPRINTS["P5"][0],
    "BT": "Biến động bình thường",
}

KPI_LABEL = {k: lbl for k, lbl, _, _ in INDICATORS}
KPI_LABEL.update({
    "orders_walkin": "Số đơn tại quầy", "aov_walkin": "AOV tại quầy", "orders_app": "Số đơn App", "aov_app": "AOV App",
    "orders_grabfood": "Số đơn Grab ghi trên POS", "aov_grabfood": "AOV Grab",
    "orders_shopeefood": "Số đơn Shopee ghi trên POS", "aov_shopeefood": "AOV Shopee",
    "shifts_morning": "Số ca sáng có chấm công", "labor_hours": "Tổng giờ công",
    "shopeefood_avg_prep_min": "Thời gian chuẩn bị Shopee",
    "grabfood_commission_gap": "Hoa hồng Grab lệch hợp đồng", "shopeefood_commission_gap": "Hoa hồng Shopee lệch hợp đồng",
})
RATE_KPIS = {"cogs_pct", "labor_pct", "void_rate", "refund_rate", "discount_rate", "app_store_cancel_rate",
             "app_wait_cancel_rate", "grabfood_commission_gap", "shopeefood_commission_gap",
             "grabfood_pos_coverage", "shopeefood_pos_coverage"}
CHANNELS = [("walkin", "Tại quầy"), ("app", "App"), ("grabfood", "GrabFood"), ("shopeefood", "ShopeeFood")]
