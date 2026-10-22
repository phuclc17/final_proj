# ĐẶC TẢ BỘ MÔ PHỎNG DỮ LIỆU NGUỒN (tư liệu cho mục 3.3 báo cáo)

> Bộ mô phỏng **không thuộc phần DE**. Nó đóng vai "doanh nghiệp và các hệ thống của doanh nghiệp", sinh ra file gốc giống như một chuỗi F&B thật nhận được hằng ngày. Pipeline DE chỉ được đọc `data/<profile>/source_systems/`, **không bao giờ** đọc `ground_truth/` hay code của bộ mô phỏng.

## 1. Nguyên lý: một thế giới, nhiều góc nhìn

Bộ mô phỏng cũ sinh từng nguồn **độc lập** (file đối soát sàn tự random, không liên quan đơn POS), nên "tích hợp đa nguồn" chỉ là hình thức. Bộ mới làm theo 2 bước:

1. **Sinh sự kiện thật một lần** (`simulator/world.py`): khách đặt đơn qua kênh nào, giờ nào, món gì; ai đi làm ca nào; bếp tải bao nhiêu; nguyên liệu dùng, hỏng, mất bao nhiêu; giao hàng; kiểm kê.
2. **Mỗi hệ thống nguồn xuất phần nó nhìn thấy** (`simulator/views.py`, `exporters.py`), theo định dạng và quy ước riêng, kèm lỗi riêng:

| Hệ thống nguồn | Thấy gì | Định dạng file | "Độ bẩn" cố ý |
|---|---|---|---|
| POS tại quầy | Đơn tại quầy (mọi trạng thái) + đơn sàn **do nhân viên nhập tay** | JSON/chi nhánh/ngày, 43 trường | 3 chi nhánh dùng POS v2.8: ngày ISO thay vì dd/mm/yyyy, tiền dạng chuỗi `"125.000"`, cột `grand_total` thay `total_paid`, thiếu 4 trường; tên món nhiều biến thể; ~3% đơn sàn không được nhập |
| App riêng | Đơn app (mọi trạng thái), khách hàng | JSON dump API/ngày, 30 trường | Giờ UTC; mã chi nhánh riêng (`FNF-Q3-01`); mã món riêng (`PID-xxxxxx`), tên tiếng Việt có dấu |
| GrabFood | Tổng hợp tuần từ **đúng các đơn Grab thật** | CSV tuần, tiếng Anh | Tên cửa hàng tự do (`Fast&Fat - District 3 (#1)`); ngày `19 Mar 2024`; chỉ có số tiền hoa hồng, không có tỷ lệ |
| ShopeeFood | Tổng hợp tuần từ đúng các đơn Shopee thật | **Excel** tuần, tiếng Việt, có dòng tiêu đề | Mã cửa hàng khác (`FASTFAT_DISTRICT3_01`); header tiếng Việt |
| Sổ nhập kho | Mỗi lần giao hàng | **Excel** do quản lý tự ghi, 2 mẫu khác nhau | Mẫu A: tiêu đề, tên nguyên liệu tiếng Việt có dấu, ĐVT "quả/lít", dòng "Tổng cộng"; mẫu B (CN3, 6, 9): tiếng Anh không dấu, số lượng dính đơn vị `"12.5kg"`; ~5% tên viết tắt/biến thể; ~0,5% gõ gram vào cột kg |
| Phiếu kiểm kê | Tồn thực tế 2 tuần/lần | **Excel**, tiếng Việt | Sai số đếm tay ±2%; ~2% dòng bỏ trống "chưa đếm" |
| Máy chấm công | Lượt quẹt | CSV/chi nhánh/ngày | Mã nhân viên dạng số (POS dùng `NV0012`); ~6% quẹt trùng; ~5% quên quẹt ra |
| HQ (master data) | Danh mục chi nhánh, món, giá, nguyên liệu, công thức, nhân viên, hợp đồng sàn | CSV snapshot khi có thay đổi | Giá đổi 1/6/2024; 1 nhân viên được thăng chức 1/7/2024 → nguồn gốc SCD2 |
| Thời tiết (bên ngoài) | Mưa/nắng theo ngày | JSON/ngày | — |

## 2. Mô hình nhu cầu (biến động bình thường)

`kỳ vọng số đơn = mức theo hạng chi nhánh × hệ số chi nhánh × hệ số thứ × nhiễu ngày × hệ số kênh × (lễ) × (mưa) × (xếp hạng trên sàn)`

- Hạng chi nhánh: A (hot) 380, B (medium) 170, C (low) 60 đơn/ngày.
- Thứ: T2 0.92 … T7 1.25, CN 1.20. Lễ (18/4, 30/4, 1/5, 2–3/9): tại quầy ×1.35, giao ×1.15.
- Mưa (mùa mưa 45% số ngày): tại quầy ×0.75, giao hàng ×1.20–1.25.
- Phân bổ theo giờ 7h–22h, cao điểm 11–13h và 18–20h (trọng số ×3).
- **Hiệu chỉnh từ dữ liệu thật công khai** (The Bread Basket, OpenML 43422, CC0, 9.465 giao dịch): số món mỗi đơn 42/32/16/10%, số lượng/dòng 92/8%, độ tập trung món bán chạy Zipf 1,06, nhiễu ngày 0,075 (giả định cũ 0,08 được xác nhận). Hệ số thứ và khung giờ KHÔNG chuyển giao (tiệm bánh đóng cửa chiều). Chạy lại: `python -m simulator.calibrate_public`.

Các biến động này **không phải sự cố**: cây KPI phải phân biệt được chúng với biến động do sự cố.

## 3. Chuỗi nhân quả vận hành (điểm mới quan trọng nhất)

```
Nhân sự đi làm theo ca (vắng ngẫu nhiên; quản lý gọi người làm bù để đủ số bếp tối thiểu)
  → Tải bếp mỗi giờ: util = số đơn / (năng lực × số người bếp)
  → Thời gian chuẩn bị = 4 + 6 / (1 − util)^0.6        (kiểu hàng đợi)
  → util > 0.90: khách tại quầy bỏ đi (mất doanh thu, không để lại dấu vết)
  → util > 0.85: cửa hàng hủy đơn app/sàn ("STORE_TOO_BUSY")
  → chờ lâu: khách hủy đơn; rating đơn giảm
  → rating tuần (trung bình trượt) → hệ số xếp hạng trên sàn tuần sau → số đơn sàn tuần sau
```

Hệ quả: thiếu người không chỉ làm tăng chỉ số "đơn/giờ công", mà còn **làm mất doanh thu ngay trong kỳ và kéo dài vài tuần sau** qua thứ hạng trên sàn. Đây là căn cứ để đề tài "truy vết nguyên nhân biến động doanh thu" có dữ liệu chứng minh.

## 4. Kho

- Giao hàng buổi sáng: hàng tươi T2–T7 (thứ Bảy giao đủ cho cả Chủ nhật), hàng khô T2 và T5. Lượng đặt = tiêu hao trung bình 7 ngày × số ngày cần đủ − tồn hiện tại.
- Tiêu hao thật = tiêu hao lý thuyết (công thức × món đã làm) × hệ số hao hụt (tươi 1.02–1.05, khô 1.00–1.02).
- Đơn bị hủy trước khi làm thì không tiêu hao; khách hủy khi đang chờ thì tiêu hao 50%; **đơn sàn không nhập POS và hóa đơn bị hủy gian lận vẫn tiêu hao** → để lại dấu vết chéo ở kho.
- Kiểm kê 2 tuần/lần vào Chủ nhật.

## 5. Kịch bản (pain point)

Hai bộ độc lập, khác seed, khác chi nhánh, khác thời điểm, khác mức độ:

| Pain point | Tập phát triển (dùng để phát triển, chọn ngưỡng) | Tập kiểm tra (chỉ dùng đánh giá cuối) |
|---|---|---|
| P1a Sàn tính sai hoa hồng | S1: CN4 Grab 13/5–2/6, 30% thay vì 25% | H1: CN10 Shopee 5/8–18/8, 26% thay vì 22% |
| P1b Đơn sàn không nhập POS | S2: CN6 15/7–28/7, 20% | H2: CN3 22/4–5/5, 15% |
| P2 Hao hụt nguyên liệu tươi | S3: CN7 10/4–20/4, ×1.15–1.30 | H3: CN1 3/6–14/6, ×1.12–1.25 |
| P3 Thiếu người ca tối → mất doanh thu | S4: CN2 6/5–19/5, dời 55% ca tối | H4: CN8 22/7–31/7, dời 45% |
| P4 Mất cắp kho | S5: CN9 17/6–30/6, 1.5%/ngày thịt/tôm/phô mai | H5: CN5 12/8–25/8, 1.2%/ngày |
| P5 Thu ngân hủy hóa đơn gian lận | S6: CN8 1/7–28/7, 12% đơn tiền mặt của 1 người | H6: CN11 1/4–21/4, 10% |

Tập kiểm tra cố ý **khó hơn**: mức độ nhẹ hơn, rơi vào chi nhánh nhỏ (ít dữ liệu), sàn khác.

## 6. Cách chạy

```
python -m simulator.run --profile calibration --days 182 --reset   # backfill 26 tuần
python -m simulator.run --profile calibration --days 1             # thêm 1 ngày mới (dùng cho lịch chạy hằng ngày)
python -m simulator.validate --profile calibration                 # kiểm chứng tác động của kịch bản
```

Trạng thái thế giới (tồn kho, rating, khách hàng, bộ sinh số ngẫu nhiên) được lưu sau mỗi lần chạy, nên sinh tăng dần từng ngày cho kết quả **giống hệt** sinh một lần, và tái lập được hoàn toàn nhờ seed cố định.

## 7. Giới hạn (ghi trung thực trong báo cáo)

- Tham số hành vi (hệ số lễ, mưa, độ dốc hủy đơn theo tải…) là giả định hợp lý, chưa hiệu chỉnh bằng dữ liệu thật.
- Lương giờ, quy mô nhân sự lấy từ `staff.csv` nên tỷ lệ chi phí nhân công khác nhau nhiều giữa các hạng chi nhánh (hạng C cao về cấu trúc).
- Chưa mô phỏng: hết hàng làm hủy đơn, biến động giá nhà cung cấp, lịch phân ca kế hoạch, dữ liệu két tiền.
