# TÀI LIỆU THAM KHẢO

TODO: rà lại từng tài liệu theo APA 7; thêm tài liệu cho mục 1.1, 2.1, 2.8.

REF: Agresti, A. (2013). *Categorical data analysis* (3rd ed.). Wiley.

REF: Apache Software Foundation. (n.d.). *Apache Airflow documentation*. https://airflow.apache.org/docs/

REF: Armbrust, M., Ghodsi, A., Xin, R., & Zaharia, M. (2021). Lakehouse: A new generation of open platforms that unify data warehousing and advanced analytics. In *Proceedings of the 11th Conference on Innovative Data Systems Research (CIDR 2021)*.

REF: Batini, C., & Scannapieco, M. (2016). *Data and information quality: Dimensions, principles and techniques*. Springer.

REF: Chandola, V., Banerjee, A., & Kumar, V. (2009). Anomaly detection: A survey. *ACM Computing Surveys, 41*(3), Article 15.

REF: Christen, P. (2012). *Data matching: Concepts and techniques for record linkage, entity resolution, and duplicate detection*. Springer.

REF: Databricks. (n.d.). *What is a medallion architecture?* https://www.databricks.com/glossary/medallion-architecture

REF: dbt Labs. (n.d.). *dbt documentation*. https://docs.getdbt.com/

REF: Docker Inc. (n.d.). *Docker Compose documentation*. https://docs.docker.com/compose/

REF: Dopson, L. R., & Hayes, D. K. (2019). *Food and beverage cost control* (7th ed.). Wiley.

REF: Dunn, O. J. (1961). Multiple comparisons among means. *Journal of the American Statistical Association, 56*(293), 52–64.

REF: FastAPI. (n.d.). *FastAPI documentation*. https://fastapi.tiangolo.com/

REF: Fellegi, I. P., & Sunter, A. B. (1969). A theory for record linkage. *Journal of the American Statistical Association, 64*(328), 1183–1210.

REF: Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. *MIS Quarterly, 28*(1), 75–105.

REF: Iglewicz, B., & Hoaglin, D. C. (1993). *How to detect and handle outliers*. ASQC Quality Press.

REF: Inmon, W. H. (2005). *Building the data warehouse* (4th ed.). Wiley.

REF: Kasavana, M. L., & Smith, D. I. (1982). *Menu engineering: A practical guide to menu analysis*. Hospitality Publications.

REF: Kimball, R., & Caserta, J. (2004). *The data warehouse ETL toolkit*. Wiley.

REF: Kimball, R., & Ross, M. (2013). *The data warehouse toolkit: The definitive guide to dimensional modeling* (3rd ed.). Wiley.

REF: Kleinrock, L. (1975). *Queueing systems, Volume 1: Theory*. Wiley.

REF: Law, A. M. (2015). *Simulation modeling and analysis* (5th ed.). McGraw-Hill Education.

REF: Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation forest. In *2008 Eighth IEEE International Conference on Data Mining* (pp. 413–422). IEEE.

REF: Metabase. (n.d.). *Metabase documentation*. https://www.metabase.com/docs/

REF: Object Management Group. (2017). *OMG Unified Modeling Language (OMG UML), Version 2.5.1*. https://www.omg.org/spec/UML/2.5.1/

REF: OpenML. (2022). *The-Bread-Basket* (Dataset ID 43422) [Data set]. Giấy phép CC0. https://www.openml.org/d/43422 (truy cập ngày 10/10/2026)

REF: Patki, N., Wedge, R., & Veeramachaneni, K. (2016). The synthetic data vault. In *2016 IEEE International Conference on Data Science and Advanced Analytics (DSAA)* (pp. 399–410). IEEE.

REF: PostgreSQL Global Development Group. (n.d.). *PostgreSQL documentation*. https://www.postgresql.org/docs/

REF: Raasveldt, M., & Mühleisen, H. (2019). DuckDB: An embeddable analytical database. In *Proceedings of the 2019 International Conference on Management of Data (SIGMOD ’19)* (pp. 1981–1984). ACM.

REF: Reis, J., & Housley, M. (2022). *Fundamentals of data engineering*. O’Reilly Media.

REF: Rousseeuw, P. J., & Croux, C. (1993). Alternatives to the median absolute deviation. *Journal of the American Statistical Association, 88*(424), 1273–1283.

REF: Streamlit. (n.d.). *Streamlit documentation*. https://docs.streamlit.io/

REF: Vanschoren, J., van Rijn, J. N., Bischl, B., & Torgo, L. (2013). OpenML: Networked science in machine learning. *SIGKDD Explorations, 15*(2), 49–60.

REF: Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. *Journal of Management Information Systems, 12*(4), 5–33.

# PHỤ LỤC

## Phụ lục A. Đặc tả dữ liệu của các hệ thống nguồn

### A.1. Hóa đơn POS

Mỗi tệp `pos/<mã máy POS>/pos_export_<ngày>.json` là một mảng hóa đơn của một chi nhánh trong một ngày. Phiên bản phần mềm 3.2.1 có 43 trường; phiên bản 2.8.0 (CN5, CN7, CN10) có 39 trường.

TABLE: Bảng A.1. Các nhóm trường của hóa đơn POS
WIDTHS: 3,7,4
| Nhóm | Trường | Khác biệt ở phiên bản 2.8.0 |
| Định danh, thời gian | `receipt_no`, `terminal_id`, `cashier_code`, `txn_time`, `shift_id`, `order_source`, `order_type`, `table_number`, `guest_count` | `txn_time` dạng `2024-04-12T07:00:53` thay vì `12/04/2024 07:00:53` |
| Dòng món | `items[]`: `line_id`, `sku`, `name_on_receipt`, `category_code`, `qty`, `unit_price`, `line_discount_amount`, `line_tax_amount`, `modifier_list`, `void_item_flag` | — |
| Tiền và phụ phí | `subtotal_amount`, `tax_rate`, `tax_amount`, `service_charge_amount`, `tip_amount`, `rounding_adjustment`, `total_paid` | Tiền là chuỗi `"125.000"`; `total_paid` được gọi là `grand_total` |
| Khuyến mãi, thành viên | `discount_code`, `discount_type`, `discount_amount`, `coupon_id`, `loyalty_member_phone_masked`, `loyalty_points_earned`, `loyalty_points_redeemed` | Không có `loyalty_points_redeemed` |
| Thanh toán | `payment_method`, `payment_reference_no`, `card_last4` | — |
| Hủy, hoàn tiền | `void_flag`, `void_reason`, `void_by`, `void_timestamp`, `refund_flag`, `refund_amount`, `refund_by` | Không có `void_timestamp`, `refund_by` |
| Hệ thống | `pos_software_version`, `pos_device_id`, `sync_status`, `sync_timestamp`, `printed_flag`, `reprint_count`, `currency`, `notes`, `branch_manager_on_duty` | Không có `sync_timestamp` |

### A.2. Đơn hàng ứng dụng riêng

Mỗi tệp `owned_app/orders_<ngày>.json` là kết quả xuất từ API, gồm phần vỏ (`export_generated_at`, `page`, `page_size`, `total`) và mảng `data` các đơn hàng. Mỗi đơn có 30 trường: định danh và thời gian (`order_uuid`, `created_at_utc`, `updated_at_utc`, `kitchen_ready_at_utc`), chi nhánh (`branch_ref.code`, `branch_ref.display_name`), khách hàng (`customer_id_hashed`, `is_first_order_flag`, `customer_tier_display`), thiết bị (`platform`, `app_version`, `device_os_version`), dòng món (`line_items[]` với `product_ref`, `product_name`, `category_ref`, `qty`, `price_vnd`, `modifiers`), tiền (`subtotal`, `delivery_fee`, `packaging_fee`, `service_fee`, `promo_applied`, `total_amount`), thanh toán và trạng thái (`payment_method`, `payment_status`, `order_status`, `cancel_reason`), giao hàng (`delivery_type`, `delivery_ward`), tiếp thị (`utm_source`, `utm_campaign`, `session_id`) và phản hồi (`rating`, `review_text`, `notes_from_customer`). Mọi thời điểm theo giờ UTC.

### A.3. Báo cáo đối soát sàn

TABLE: Bảng A.2. Cột của báo cáo đối soát GrabFood (CSV) và ShopeeFood (Excel)
WIDTHS: 5,5,4
| GrabFood | ShopeeFood | Ý nghĩa |
| Merchant Store Name | Mã cửa hàng | Định danh cửa hàng trên sàn |
| Week | (dòng “Kỳ đối soát” phía trên bảng) | Kỳ báo cáo |
| Report Generated Date | — | Ngày tạo báo cáo |
| Gross Sales | Doanh thu món (VNĐ) | Doanh thu món của đơn hoàn thành |
| Total Orders | Số đơn hoàn thành | Số đơn hoàn thành |
| Cancelled Orders | Số đơn hủy | Số đơn bị hủy |
| Total Commission | Phí dịch vụ (VNĐ) | Phí hoa hồng (không ghi tỷ lệ) |
| Promotion Cost Borne by Merchant | Khuyến mãi do quán tài trợ (VNĐ) | Phần khuyến mãi cửa hàng chịu |
| Ads Spend | Phí quảng cáo (VNĐ) | Chi phí quảng cáo trên sàn |
| Adjustment Amount | Điều chỉnh (VNĐ) | Các khoản điều chỉnh |
| Net Payout | Thực nhận (VNĐ) | Tiền cửa hàng thực nhận |
| Average Prep Time (min) | Thời gian chuẩn bị TB (phút) | Thời gian chuẩn bị trung bình |
| Store Rating | Đánh giá | Điểm đánh giá cửa hàng |

### A.4. Sổ nhập kho, phiếu kiểm kê, chấm công

- **Sổ nhập kho mẫu A** (8 chi nhánh): tệp `NhapKho_CNxx_<ngày>.xlsx`; ba dòng tiêu đề (“PHIẾU NHẬP KHO”, “Chi nhánh: …”, “Ngày nhập: dd/mm/yyyy”); bảng gồm STT, Tên nguyên liệu, ĐVT, Số lượng, Đơn giá, Thành tiền, Hạn sử dụng, Nhà cung cấp; dòng “Tổng cộng” và dòng “Người lập phiếu” ở cuối.
- **Sổ nhập kho mẫu B** (CN3, CN6, CN9): tệp `receipts_CNxx_<ngày>.xlsx`; một bảng gồm date (yyyy-mm-dd), item (tên không dấu), quantity (số lượng dính đơn vị, ví dụ `53.6kg`), unit_price, supplier.
- **Phiếu kiểm kê**: tệp `KiemKe_CNxx_<ngày>.xlsx`; bốn dòng tiêu đề (tên phiếu, chi nhánh, ngày kiểm kê, người kiểm); bảng gồm STT, Mã NL, Tên nguyên liệu, ĐVT, Tồn thực tế, Ghi chú.
- **Chấm công**: tệp `punch_BRxx_<ngày>.csv`; các cột `employee_code`, `branch_code`, `event_type` (CHECK_IN, CHECK_OUT), `event_time`, `device_id`, `verification_method`.

## Phụ lục B. Từ điển dữ liệu tầng Gold

Tên cột và kiểu dữ liệu lấy trực tiếp từ kho dữ liệu của tập phát triển. Các khóa có hậu tố `_sk` là khóa thay thế của phiên bản trong bảng chiều thay đổi chậm.

TABLE: Bảng B.1. Bảng fact_order: một đơn hàng ở một kênh (hóa đơn POS hoặc đơn App) (438.881 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `order_key` | chuỗi | Khóa đơn hàng, duy nhất trên mọi hệ thống |
| `source_system` | chuỗi | Hệ thống gốc: POS hoặc APP |
| `source_order_id` | chuỗi | Số hóa đơn POS hoặc mã đơn App ở hệ thống gốc |
| `branch_id` | số nguyên | Mã chi nhánh theo trụ sở (1–11) |
| `date_day` | ngày | Ngày phát sinh theo giờ Việt Nam |
| `date_key` | số nguyên | Khóa ngày dạng số yyyymmdd |
| `ordered_at_local` | ngày giờ | Thời điểm đặt hoặc thanh toán, giờ Việt Nam |
| `order_hour` | số nguyên | Giờ trong ngày của đơn |
| `shift_name` | chuỗi | Ca làm việc: sáng hoặc tối |
| `channel` | chuỗi | Kênh: WALKIN, APP, GRABFOOD, SHOPEEFOOD |
| `order_type` | chuỗi | Hình thức: ăn tại chỗ, mang đi, giao hàng |
| `cashier_staff_id` | số nguyên | Mã nhân viên thu ngân (đơn POS) |
| `cashier_employee_sk` | chuỗi | Khóa phiên bản nhân viên thu ngân tại ngày bán |
| `customer_id` | chuỗi | Mã khách hàng đã băm (chỉ đơn App) |
| `is_first_order` | đúng/sai | Đơn đầu tiên của khách trên ứng dụng |
| `order_status` | chuỗi | Trạng thái chuẩn hóa: COMPLETED, VOIDED, REFUNDED, CANCELLED_BY_STORE, CANCELLED_BY_CUSTOMER |
| `cancel_reason` | chuỗi | Lý do hủy theo hệ thống gốc |
| `is_completed` | đúng/sai | Đơn hoàn thành, được tính doanh thu |
| `is_prepared` | đúng/sai | Bếp đã làm món (kể cả đơn bị hủy, hoàn sau khi làm), dùng để tính tiêu hao định mức |
| `payment_method` | chuỗi | Phương thức thanh toán |
| `gross_sales` | số nguyên | Tiền món trước giảm giá |
| `discount_amount` | số nguyên | Tiền giảm giá |
| `promo_code` | chuỗi | Mã khuyến mãi |
| `net_sales` | số nguyên | Doanh thu thuần: tiền món sau giảm giá, chỉ đơn hoàn thành |
| `refund_amount` | số nguyên | Tiền hoàn cho khách |
| `delivery_fee` | số nguyên | Phí giao hàng khách trả (đơn App) |
| `minutes_to_void` | số thực | Số phút từ lúc thanh toán đến lúc hủy hóa đơn |
| `prep_minutes` | số thực | Thời gian chuẩn bị đơn, phút (đơn App) |
| `rating` | số nguyên | Điểm đánh giá của khách cho đơn (đơn App) |
| `n_lines` | số nguyên | Số dòng món trong đơn |

TABLE: Bảng B.2. Bảng fact_order_line: một dòng món trong một đơn (851.601 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `order_line_key` | chuỗi | Khóa dòng món |
| `order_key` | chuỗi | Khóa đơn hàng, duy nhất trên mọi hệ thống |
| `line_no` | số nguyên | Số thứ tự dòng trong đơn |
| `branch_id` | số nguyên | Mã chi nhánh theo trụ sở (1–11) |
| `date_day` | ngày | Ngày phát sinh theo giờ Việt Nam |
| `channel` | chuỗi | Kênh: WALKIN, APP, GRABFOOD, SHOPEEFOOD |
| `item_id` | số nguyên | Mã món theo trụ sở |
| `menu_item_sk` | chuỗi | Khóa phiên bản món có hiệu lực tại ngày bán |
| `category` | chuỗi | Nhóm món: Main, Side, Drink, Combo |
| `is_combo` | đúng/sai | Món combo, được tách thành món thành phần khi tính tiêu hao |
| `qty` | số nguyên | Số lượng |
| `unit_price` | số nguyên | Đơn giá |
| `line_discount_amount` | số nguyên | Giảm giá phân bổ cho dòng |
| `line_amount` | số nguyên | Thành tiền của dòng |
| `is_item_void` | đúng/sai | Món bị hủy riêng trong đơn |
| `order_status` | chuỗi | Trạng thái chuẩn hóa: COMPLETED, VOIDED, REFUNDED, CANCELLED_BY_STORE, CANCELLED_BY_CUSTOMER |
| `is_revenue_line` | đúng/sai | Dòng được tính doanh thu |
| `is_prepared` | đúng/sai | Bếp đã làm món (kể cả đơn bị hủy, hoàn sau khi làm), dùng để tính tiêu hao định mức |
| `standard_unit_cost` | số nguyên | Giá vốn chuẩn mỗi đơn vị |
| `cogs_standard` | số nguyên | Giá vốn định mức của dòng theo phiên bản món tại ngày bán |

TABLE: Bảng B.3. Bảng fact_marketplace_settlement: một chi nhánh × một sàn × một tuần đối soát (572 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `settlement_key` | chuỗi | Khóa dòng đối soát |
| `channel` | chuỗi | Kênh: WALKIN, APP, GRABFOOD, SHOPEEFOOD |
| `branch_id` | số nguyên | Mã chi nhánh theo trụ sở (1–11) |
| `week_start` | ngày | Ngày đầu tuần (thứ Hai) |
| `week_end` | ngày | Ngày cuối tuần (Chủ nhật) |
| `report_generated_date` | ngày | Ngày sàn tạo báo cáo |
| `gross_sales` | số nguyên | Doanh thu món theo báo cáo sàn |
| `orders_completed` | số nguyên | Số đơn hoàn thành theo báo cáo sàn |
| `orders_cancelled` | số nguyên | Số đơn bị hủy theo báo cáo sàn |
| `commission` | số nguyên | Phí hoa hồng sàn thu |
| `ads_spend` | số nguyên | Chi phí quảng cáo trên sàn |
| `merchant_promo` | số nguyên | Khuyến mãi do cửa hàng tài trợ |
| `adjustment` | số nguyên | Khoản điều chỉnh |
| `net_payout` | số nguyên | Tiền cửa hàng thực nhận |
| `avg_prep_min` | số thực | Thời gian chuẩn bị trung bình theo sàn, phút |
| `store_rating` | số thực | Điểm đánh giá cửa hàng trên sàn |
| `effective_commission_rate` | số thực | Tỷ lệ hoa hồng hiệu dụng = hoa hồng / doanh thu món |
| `contract_commission_rate` | số thực | Tỷ lệ hoa hồng trong hợp đồng có hiệu lực |
| `commission_rate_gap` | số thực | Tỷ lệ hiệu dụng trừ tỷ lệ hợp đồng |
| `commission_overcharge` | số thực | Hoa hồng thu thừa = chênh lệch tỷ lệ × doanh thu món |

TABLE: Bảng B.4. Bảng fact_inventory_receipt: một dòng phiếu nhập kho hợp lệ (16.104 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `receipt_line_id` | chuỗi | Khóa dòng phiếu nhập |
| `branch_id` | số nguyên | Mã chi nhánh theo trụ sở (1–11) |
| `date_day` | ngày | Ngày nhập |
| `ingredient_id` | số nguyên | Mã nguyên liệu theo trụ sở |
| `ingredient_match_method` | chuỗi | Cách nhận diện tên nguyên liệu: khớp chính xác, bảng biến thể, khớp mờ |
| `quantity` | số thực | Số lượng theo đơn vị chuẩn |
| `unit` | chuỗi | Đơn vị chuẩn |
| `unit_price` | số nguyên | Đơn giá nhập |
| `line_amount` | số thực | Thành tiền nhập |
| `expiry_date` | ngày | Hạn sử dụng |
| `supplier` | chuỗi | Nhà cung cấp |

TABLE: Bảng B.5. Bảng fact_stock_count: một chi nhánh × một nguyên liệu × một lần kiểm kê (3.146 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `count_key` | chuỗi | Khóa dòng kiểm kê |
| `branch_id` | số nguyên | Mã chi nhánh theo trụ sở (1–11) |
| `date_day` | ngày | Ngày kiểm kê |
| `ingredient_id` | số nguyên | Mã nguyên liệu theo trụ sở |
| `counted_qty` | số thực | Số lượng tồn đếm được (trống nếu không đếm) |
| `is_not_counted` | đúng/sai | Ô kiểm kê để trống |
| `counted_by` | chuỗi | Người kiểm kê |
| `standard_unit_cost` | số nguyên | Giá vốn chuẩn mỗi đơn vị |
| `counted_value` | số thực | Giá trị tồn đếm được theo giá chuẩn |

TABLE: Bảng B.6. Bảng fact_labor_shift: một nhân viên × một ca làm việc (21.170 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `shift_key` | chuỗi | Khóa ca làm việc |
| `staff_id` | số nguyên | Mã nhân viên theo trụ sở |
| `employee_sk` | chuỗi | Khóa phiên bản nhân viên có hiệu lực tại ngày làm |
| `branch_id` | số nguyên | Mã chi nhánh theo trụ sở (1–11) |
| `date_day` | ngày | Ngày làm việc |
| `shift_name` | chuỗi | Ca làm việc: sáng hoặc tối |
| `role` | chuỗi | Vai trò: thu ngân, bếp, phục vụ, quản lý ca |
| `check_in_at` | ngày giờ | Giờ vào |
| `check_out_at` | ngày giờ | Giờ ra (trống nếu quên quẹt) |
| `is_missing_checkout` | đúng/sai | Thiếu lượt ra |
| `hours_worked` | số thực | Số giờ theo chấm công |
| `is_hours_imputed` | đúng/sai | Số giờ được nội suy do thiếu lượt ra |
| `hours_paid` | số thực | Số giờ dùng để tính lương (đã nội suy nếu thiếu) |
| `hourly_wage` | số nguyên | Lương giờ theo phiên bản nhân viên |
| `labor_cost` | số thực | Chi phí nhân công của ca |

TABLE: Bảng B.7. Bảng dim_date: một ngày (183 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `date_day` | ngày | Ngày phát sinh theo giờ Việt Nam |
| `date_key` | số nguyên | Khóa ngày dạng số yyyymmdd |
| `week_start` | ngày | Ngày đầu tuần (thứ Hai) |
| `iso_week` | số nguyên | Số tuần ISO |
| `month_no` | số nguyên | Tháng |
| `iso_dow` | số nguyên | Thứ trong tuần (1 = thứ Hai) |
| `dow_name` | chuỗi | Tên thứ |
| `is_weekend` | đúng/sai | Cuối tuần |
| `holiday_name` | chuỗi | Tên ngày lễ |
| `is_holiday` | đúng/sai | Ngày lễ |
| `weather_condition` | chuỗi | Tình trạng thời tiết |
| `precipitation_mm` | số thực | Lượng mưa, mm |
| `temp_max_c` | số thực | Nhiệt độ cao nhất, °C |
| `is_rain` | đúng/sai | Ngày có mưa |

TABLE: Bảng B.8. Bảng dim_branch: một chi nhánh (11 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `branch_id` | số nguyên | Mã chi nhánh theo trụ sở (1–11) |
| `branch_name` | chuỗi | Tên chi nhánh |
| `district` | chuỗi | Quận |
| `store_class` | chuỗi | Hạng chi nhánh: A lớn, B vừa, C nhỏ |
| `latitude` | số thực | Vĩ độ |
| `longitude` | số thực | Kinh độ |
| `open_date` | ngày | Ngày khai trương |
| `pos_terminal_prefix` | chuỗi | Tiền tố mã máy POS |
| `app_branch_code` | chuỗi | Mã chi nhánh trên ứng dụng |
| `grab_store_name` | chuỗi | Tên cửa hàng trên GrabFood |
| `shopee_store_code` | chuỗi | Mã cửa hàng trên ShopeeFood |
| `timekeeping_branch_code` | chuỗi | Mã chi nhánh trên máy chấm công |

TABLE: Bảng B.9. Bảng dim_channel: một kênh bán (4 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `channel` | chuỗi | Kênh: WALKIN, APP, GRABFOOD, SHOPEEFOOD |
| `channel_name` | chuỗi | Tên kênh |
| `channel_group` | chuỗi | Nhóm kênh: tại cửa hàng, giao hàng |
| `source_systems` | chuỗi | Hệ thống nguồn ghi nhận kênh |
| `has_commission` | đúng/sai | Kênh chịu hoa hồng sàn |

TABLE: Bảng B.10. Bảng dim_menu_item: một phiên bản của một món (SCD loại 2) (34 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `menu_item_sk` | chuỗi | Khóa phiên bản món có hiệu lực tại ngày bán |
| `item_id` | số nguyên | Mã món theo trụ sở |
| `item_name` | chuỗi | Tên món |
| `category` | chuỗi | Nhóm món: Main, Side, Drink, Combo |
| `is_combo` | đúng/sai | Món combo, được tách thành món thành phần khi tính tiêu hao |
| `price` | số nguyên | Giá bán của phiên bản |
| `standard_cost` | số nguyên | Giá vốn định mức mỗi phần |
| `standard_cost_pct` | số thực | Giá vốn định mức / giá bán |
| `valid_from` | ngày | Ngày bắt đầu hiệu lực của phiên bản |
| `valid_to` | ngày | Ngày kết thúc hiệu lực (9999-12-31 nếu còn hiệu lực) |
| `is_current` | đúng/sai | Phiên bản hiện hành |
| `first_seen_snapshot` | ngày | Ảnh chụp danh mục đầu tiên có phiên bản này |

TABLE: Bảng B.11. Bảng dim_employee: một phiên bản của một nhân viên (SCD loại 2) (146 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `employee_sk` | chuỗi | Khóa phiên bản nhân viên có hiệu lực tại ngày làm |
| `staff_id` | số nguyên | Mã nhân viên theo trụ sở |
| `staff_code` | chuỗi | Mã nhân viên dạng NV0xxx (như trên POS) |
| `staff_name` | chuỗi | Tên nhân viên |
| `branch_id` | số nguyên | Chi nhánh làm việc của phiên bản |
| `role` | chuỗi | Vai trò: thu ngân, bếp, phục vụ, quản lý ca |
| `hourly_wage` | số nguyên | Lương giờ theo phiên bản nhân viên |
| `hire_date` | ngày | Ngày vào làm |
| `valid_from` | ngày | Ngày bắt đầu hiệu lực của phiên bản |
| `valid_to` | ngày | Ngày kết thúc hiệu lực (9999-12-31 nếu còn hiệu lực) |
| `is_current` | đúng/sai | Phiên bản hiện hành |

TABLE: Bảng B.12. Bảng dim_ingredient: một nguyên liệu (22 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `ingredient_id` | số nguyên | Mã nguyên liệu theo trụ sở |
| `ingredient_code` | chuỗi | Mã nguyên liệu trên phiếu kiểm kê (NLxx) |
| `ingredient_name` | chuỗi | Tên chuẩn của nguyên liệu |
| `unit` | chuỗi | Đơn vị chuẩn |
| `ingredient_category` | chuỗi | Nhóm nguyên liệu |
| `is_fresh` | đúng/sai | Hàng tươi |
| `shelf_life_days` | số nguyên | Hạn dùng, ngày |
| `standard_unit_cost` | số nguyên | Giá vốn chuẩn mỗi đơn vị |

TABLE: Bảng B.13. Bảng dim_customer: một khách hàng của ứng dụng (4.089 dòng ở tập phát triển)
WIDTHS: 4.4,2,8.6
| Cột | Kiểu | Ý nghĩa |
| `customer_id` | chuỗi | Mã khách hàng đã băm (chỉ đơn App) |
| `first_order_date` | ngày | Ngày đặt đơn đầu tiên |
| `first_branch_id` | số nguyên | Chi nhánh của đơn đầu tiên |
| `acquisition_source` | chuỗi | Nguồn thu hút khách (UTM) |
| `first_device_platform` | chuỗi | Nền tảng thiết bị ở đơn đầu tiên |

## Phụ lục C. Danh sách quy tắc chất lượng và kiểm thử dữ liệu

### C.1. Quy tắc cách ly ở tầng Silver

Mỗi dòng vi phạm được gắn mã lỗi ở cột `dq_issue` và chuyển vào bảng `silver.silver_quarantine`. Một dòng chỉ nhận mã của quy tắc đầu tiên mà nó vi phạm.

TABLE: Bảng C.1. Các quy tắc cách ly
WIDTHS: 2.6,5.4,6
| Nguồn | Mã lỗi | Điều kiện |
| POS | `thieu_so_hoa_don, trung_so_hoa_don` | Thiếu hoặc trùng số hóa đơn |
| POS | `thoi_gian_khong_doc_duoc, tong_tien_khong_doc_duoc` | Không đọc được thời gian, tổng tiền ở cả hai định dạng |
| POS | `tong_tien_am, hoa_don_khong_co_mon` | Tổng tiền âm; hóa đơn không có dòng món |
| POS, App, chấm công, kho | `khong_anh_xa_duoc_chi_nhanh` | Mã chi nhánh không có trong bảng ánh xạ |
| App | `thieu_ma_don, trung_ma_don, don_khong_co_mon` | Thiếu, trùng mã đơn; đơn không có món |
| Chấm công | `thieu_ma_nhan_vien, loai_su_kien_khong_hop_le` | Thiếu mã nhân viên; loại sự kiện khác vào, ra |
| Chấm công | `quet_trung` | Lượt quẹt cùng loại của cùng nhân viên lặp lại trong vòng 5 phút |
| Sổ nhập kho | `chi_nhanh_tieu_de_khac_thu_muc` | Chi nhánh trên tiêu đề phiếu khác thư mục chứa tệp |
| Sổ nhập kho | `khong_nhan_dien_duoc_nguyen_lieu` | Tên nguyên liệu không khớp ở cả ba tầng ánh xạ |
| Sổ nhập kho | `so_luong_khong_hop_le, don_vi_khong_khop_danh_muc` | Số lượng trống hoặc không dương; đơn vị khác danh mục |
| Sổ nhập kho | `nghi_go_gam_vao_cot_kg` | Số lượng tính bằng kg lớn hơn 20 lần trung vị của cùng nguyên liệu |
| Phiếu kiểm kê | `ngay_kiem_ke_khong_doc_duoc, ma_nguyen_lieu_khong_ton_tai, don_vi_khong_khop_danh_muc` | Không đọc được ngày; mã nguyên liệu không có trong danh mục; đơn vị khác danh mục |

### C.2. Kiểm thử dbt

Bảng C.2 liệt kê theo từng mô hình các kiểm thử dựng sẵn của dbt và kiểm thử tổng quát khóa ghép, viết bằng macro `test_unique_combination`. Bảng C.3 liệt kê các kiểm thử luật nghiệp vụ trong thư mục `dbt/tests/`; mỗi kiểm thử là một câu SQL trả về các dòng vi phạm và đạt khi kết quả rỗng.

TABLE: Bảng C.2. Kiểm thử dựng sẵn và kiểm thử tổng quát theo mô hình
WIDTHS: 5.4,1.5,1.5,1.9,1.7,1.7,1.3
| Mô hình | Không rỗng | Duy nhất | Toàn vẹn tham chiếu | Miền giá trị | Khóa ghép | Tổng |
| `stg_app__order_lines` | 2 |  |  |  |  | 2 |
| `stg_app__orders` | 3 | 1 | 1 | 1 |  | 6 |
| `stg_grab__settlement` | 9 |  | 1 |  |  | 10 |
| `stg_inventory__receipt_lines` | 5 | 1 | 2 |  |  | 8 |
| `stg_marketplace__settlement` | 2 | 1 |  |  |  | 3 |
| `stg_master__branches` | 2 | 2 |  |  |  | 4 |
| `stg_master__ingredients` | 2 | 3 |  |  |  | 5 |
| `stg_master__marketplace_contracts` |  |  |  | 1 |  | 1 |
| `stg_master__menu_items` | 2 |  |  |  |  | 2 |
| `stg_master__recipes` |  |  | 1 |  |  | 1 |
| `stg_master__staff` | 1 |  |  |  |  | 1 |
| `stg_pos__receipt_lines` | 3 |  | 1 |  |  | 4 |
| `stg_pos__receipts` | 4 | 1 | 1 | 2 |  | 8 |
| `stg_shopee__settlement` | 5 |  | 1 |  |  | 6 |
| `stg_stock__counts` | 1 | 1 | 1 |  |  | 3 |
| `stg_timekeeping__punches` | 2 | 1 |  | 1 |  | 4 |
| `stg_timekeeping__shifts` | 1 | 1 |  | 1 |  | 3 |
| `stg_weather__daily` | 1 | 1 |  |  |  | 2 |
| `branch_code_map` | 6 | 6 |  |  |  | 12 |
| `dim_branch` | 2 | 1 |  | 1 |  | 4 |
| `dim_channel` | 1 | 1 |  |  |  | 2 |
| `dim_customer` | 1 | 1 |  |  |  | 2 |
| `dim_date` | 1 | 1 |  |  |  | 2 |
| `dim_employee` | 2 | 1 |  |  |  | 3 |
| `dim_ingredient` | 1 | 1 |  |  |  | 2 |
| `dim_menu_item` | 2 | 1 |  |  |  | 3 |
| `fact_inventory_receipt` | 2 | 1 | 1 |  |  | 4 |
| `fact_labor_shift` | 3 | 1 | 1 |  |  | 5 |
| `fact_marketplace_settlement` | 3 | 1 |  |  |  | 4 |
| `fact_order` | 4 | 1 | 5 | 1 |  | 11 |
| `fact_order_line` | 3 | 1 | 2 |  |  | 6 |
| `fact_stock_count` | 1 | 1 |  |  |  | 2 |
| `ingredient_name_variants` | 2 | 1 |  |  |  | 3 |
| `map_app_product_item` | 2 | 1 |  |  |  | 3 |
| `map_ingredient_name` | 1 | 1 |  | 1 |  | 3 |
| `mart_branch_daily` |  |  |  |  | 1 | 1 |
| `mart_branch_weekly` |  |  |  |  | 1 | 1 |
| `mart_cashier_weekly` |  |  |  |  | 1 | 1 |
| `mart_ingredient_avt` |  |  |  |  | 1 | 1 |
| `mart_kpi_vs_peers_weekly` |  |  |  |  | 1 | 1 |
| `vn_public_holidays_2024` | 1 | 1 |  |  |  | 2 |
| Tổng | 83 | 36 | 18 | 9 | 5 | 151 |

TABLE: Bảng C.3. Kiểm thử luật nghiệp vụ dạng câu SQL (7 kiểm thử)
WIDTHS: 6,8
| Kiểm thử | Nội dung |
| `assert_gold_net_sales_reconciles` | Doanh thu thuần Gold bằng tổng tính từ Silver theo chi nhánh × ngày |
| `assert_grab_one_row_per_branch_week` | Báo cáo GrabFood có đúng một dòng cho mỗi chi nhánh × tuần |
| `assert_grab_payout_reconciles` | Tiền thực nhận GrabFood = doanh thu món − hoa hồng − quảng cáo − khuyến mãi + điều chỉnh |
| `assert_pos_subtotal_matches_lines` | Tạm tính mỗi hóa đơn POS bằng tổng thành tiền các dòng món |
| `assert_scd2_no_overlap` | Các phiên bản của cùng món, cùng nhân viên không chồng lấn thời gian |
| `assert_shopee_payout_reconciles` | Như trên, cho ShopeeFood |
| `assert_silver_rows_conserved` | Số dòng Bronze = Silver + cách ly + dòng cấu trúc cho mọi nguồn |

## Phụ lục D. Cấu hình kịch bản sự cố

Các tệp cấu hình kịch bản nằm trong thư mục `simulator/scenarios/`: `calibration.json` (tập phát triển), `holdout.json` (tập kiểm tra) và `live.json` (hai sự cố minh họa của môi trường vận hành, không dùng để đánh giá). Ví dụ một kịch bản trong tập phát triển:

CODE
{"id": "S4", "pain_point": "P3", "type": "evening_understaffing", "branch_id": 2,
 "start": "2024-05-06", "end": "2024-05-19", "move_share": 0.55,
 "story": "Quan ly dieu 55% nhan vien ca toi sang ca sang: toi qua tai, sang thua nguoi"}
ENDCODE

Các kịch bản của cả hai tập được tóm tắt ở Bảng 3.12. Tập phát triển dùng hạt giống ngẫu nhiên 2024, tập kiểm tra dùng hạt giống 777.

## Phụ lục E. Hướng dẫn cài đặt và chạy

Hình E.1 cho thấy mã nguồn và dữ liệu của dự án được tổ chức theo ranh giới kiến trúc: bộ mô phỏng đóng vai các hệ thống nguồn và tách biệt với đường ống; các mũi tên liền là luồng dữ liệu chính, mũi tên đứt là đường đọc đáp án chỉ dùng khi đánh giá.

IMAGE: figures/h4_1_ma_nguon.png || Hình E.1. Tổ chức mã nguồn và dữ liệu của dự án || 16

Yêu cầu: Python 3.12, khoảng 2 GB dung lượng trống cho hai tập dữ liệu.

CODE
# 1. Tạo môi trường và cài thư viện
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

# 2. Sinh dữ liệu nguồn (khoảng 3,5 phút mỗi tập)
.venv\Scripts\python -m simulator.run --profile calibration --days 182 --reset
.venv\Scripts\python -m simulator.run --profile holdout --days 182 --reset

# 3. Kiểm chứng bộ mô phỏng
.venv\Scripts\python -m simulator.validate --profile calibration

# 4. Nạp tầng Bronze
.venv\Scripts\python -m pipeline.ingest --profile calibration

# 5. Mô phỏng một ngày vận hành mới và nạp tăng dần
.venv\Scripts\python -m simulator.run --profile calibration --days 1
.venv\Scripts\python -m pipeline.ingest --profile calibration
ENDCODE

CODE
# 6. Dựng Silver, Gold và chạy kiểm thử (211 bước)
.venv\Scripts\python -m pipeline.run_dbt --profile calibration build

# 7. Đánh giá bộ phát hiện (đọc đáp án, chỉ để chấm điểm)
.venv\Scripts\python -m analytics.evaluate --profile calibration --sweep
.venv\Scripts\python -m analytics.evaluate --profile holdout

# 8. Bật toàn bộ hệ thống: Airflow :8080, PostgreSQL :5433, Metabase :3000, ứng dụng :8501, API nguồn :8600
docker compose up -d --build

# 9. Đưa Gold sang kho phục vụ và dựng dashboard Metabase (một lần cho mỗi tập)
.venv\Scripts\python -m pipeline.publish --profile calibration
.venv\Scripts\python -m pipeline.publish --profile holdout
.venv\Scripts\python bi\metabase_setup.py

# 10. Môi trường vận hành: tạo một lần, sau đó Airflow tự chạy khi có dữ liệu mới
.venv\Scripts\python -m pipeline.run_daily --init-live
.venv\Scripts\python -m pipeline.run_daily --profile live --step simulate --days 1
.venv\Scripts\python -m pipeline.run_daily --profile live
#     API nguồn (POS đám mây, App) chạy trong Docker ở cổng 8600, tài liệu tại http://localhost:8600/docs
#     kéo qua API riêng, hoặc lấy lại từ một ngày:
.venv\Scripts\python -m pipeline.extract --profile live --since 2024-09-23
#     thử 11 tình huống dữ liệu bất thường và API nguồn sập (tự khôi phục môi trường sau khi thử)
.venv\Scripts\python tools\thu_tinh_huong.py

# 11. Kiểm tra toàn bộ trước khi trình diễn
.venv\Scripts\python tools\kiem_tra_truoc_demo.py
ENDCODE

## Phụ lục F. Trích đoạn mã nguồn

### F.1. Chuỗi nhân quả phục vụ trong bộ mô phỏng (trích `simulator/world.py`)

CODE
for hi, h in enumerate(C.OPEN_HOURS):
    n_h = int(sum(hourly[ch][hi] for ch in C.CHANNELS))
    kitchen = kitchen_h[h]
    util = n_h / (self.capacity[b] * kitchen) if kitchen > 0 else 5.0
    rho = min(util, C.UTIL_CAP)
    prep_mean = C.PREP_BASE + C.PREP_SCALE / (1 - rho) ** C.PREP_POWER
    balk = min(C.BALK_MAX, C.BALK_SLOPE * max(0.0, util - C.BALK_START))
    p_store_cancel = C.STORE_CANCEL_BASE + C.STORE_CANCEL_SLOPE * max(0.0, util - C.STORE_CANCEL_START)
ENDCODE

### F.2. Nạp tăng dần và lũy đẳng (trích `pipeline/ingest.py`)

CODE
for path in files:
    rel = path.relative_to(src).as_posix()
    if unchanged(path, rel):          # cùng kích thước, không sửa sau lần nạp trước -> không cần băm lại
        skipped += 1
        continue
    h = file_md5(path)
    if loaded.get(rel) == h:          # đã nạp với cùng nội dung -> bỏ qua
        skipped += 1
        continue
    status = "reloaded" if rel in loaded else "loaded"
    if status == "reloaded" and table_exists(con, table):
        con.execute(f"delete from bronze.{table} where _source_file = ?", [rel])
ENDCODE

### F.3. Mức kỳ vọng theo nhóm cùng hạng (trích mô hình dbt `mart_kpi_vs_peers_weekly.sql`)

CODE
stats as (
    select
        *,
        median(rel) over w8                                           as baseline_rel,
        count(rel) over w8                                            as baseline_n,
        1.4826 * mad(rel) over w8                                     as noise_own
    from rel
    window
        w8 as (partition by branch_id, kpi order by week_start rows between 8 preceding and 1 preceding)
),
noise as (
    select *, median(noise_own) over (partition by kpi, week_start) as noise_floor
    from stats
)
-- z = (rel - baseline_rel) / greatest(noise_own, noise_floor)
ENDCODE

### F.4. Kiểm định từng thu ngân cho P5 (trích `analytics/detect.py`)

CODE
for (b, w), grp in cw.groupby(["branch_id", "week_start"]):
    m = 3 * len(grp)                              # số phép thử trong tuần: Bonferroni
    for r in grp.itertuples():
        for cnt, p_other, what in ((r.voids, r.others_void_rate, "hủy"),
                                   (r.refunds, r.others_refund_rate, "hoàn"),
                                   (r.discounted, r.others_discount_rate, "giảm giá")):
            p0 = max(p_other, C.CASHIER_RATE_FLOOR)
            p_adj = min(1.0, poisson_sf(int(cnt), r.receipts * p0) * m)
            z = p_to_z(p_adj)                     # đổi xác suất đuôi ra z, rồi cắt [0, 6]
ENDCODE

## Phụ lục G. Kết quả thử nghiệm dữ liệu bất thường

Kết quả của lần chạy `tools/thu_tinh_huong.py` ngày 17/10/2026 trên môi trường vận hành (mục 5.2.4): 11 tình huống được cài cùng lúc, đường ống chạy hai lượt, lượt đầu khi API của POS đám mây và App không phản hồi, lượt sau khi API hoạt động lại.

TABLE: Bảng G.1. Kết quả xử lý 11 tình huống dữ liệu bất thường cài cùng lúc
WIDTHS: 4.6,7.4
| Tình huống | Kết quả đo được |
| Tệp POS bị cắt ngang khi ghi (CN5, 23/09) | Không đọc được, không nạp, ghi lỗi; các tệp khác vẫn nạp; cửa chặn báo CN5 thiếu POS ngày 23/09 |
| Tệp POS rỗng (CN10, 23/09) | Nạp 0 dòng; cửa chặn coi như thiếu; bộ phát hiện chỉ để CN10 ở mức theo dõi, ghi "thiếu dữ liệu nguồn, chưa kết luận" |
| Tệp chấm công thiếu cột `event_type` (CN4) | Sai hợp đồng, không nạp, lý do nêu đúng cột thiếu; cửa chặn báo thiếu chấm công CN4 |
| Tệp chấm công xuất bằng bảng mã UTF-16 (CN2) | Đọc được, nạp 24 dòng |
| Báo cáo GrabFood lưu thành Excel thả vào thư mục GrabFood | Không nhận dạng, không nạp, kèm gợi ý gửi đúng tệp CSV gốc |
| Bảng lương gửi nhầm vào vùng tiếp nhận | Không nhận dạng, không nạp |
| Tệp POS CN7 ngày 23/09 chép thành tên ngày 30/09 | Sai hợp đồng vì tên không khớp nội dung, không nạp, tránh đếm hai lần |
| Tệp của máy POS-12 chưa khai báo | Bronze nạp 3 dòng; Silver cách ly 3 dòng vì không gắn được chi nhánh |
| Phiếu kiểm kê CN3 ngày 22/09 đếm lại | Nạp lại, thay toàn bộ bản cũ (22 dòng) |
| Phiếu nhập CN1 ngày 22/09 gửi muộn | Nạp 4 dòng; Silver và Gold tính lại kỳ đó |
| API POS đám mây trả thêm trường `loyalty_tier` | Kéo về, nạp bình thường; cửa chặn cảnh báo trường mới |
