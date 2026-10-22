# Kết quả đánh giá bộ phát hiện (ghi nhận ngày 11/10/2026)

Nguồn số liệu: `python -m analytics.evaluate --profile <tập>`; các bảng CSV cùng thư mục. Bộ phát hiện chỉ đọc tầng Gold; chỉ script đánh giá đọc đáp án.

## Quy trình

1. Phát triển phương pháp và quét ngưỡng điểm 2,0–5,0 trên tập phát triển (calibration).
2. Quy tắc chọn ngưỡng khai báo trước: F1 theo chi nhánh × tuần cao nhất, hòa thì lấy ngưỡng thấp hơn → **3,5**.
3. Chốt ngưỡng trong `analytics/config.py`, commit `60d28bb`, rồi chạy tập kiểm tra (holdout) **một lần**. Không chỉnh gì sau đó.

Định nghĩa: cửa sổ sự cố = các tuần giao với [bắt đầu, kết thúc + 14 ngày]. Cảnh báo trong cửa sổ cùng chi nhánh là cảnh báo đúng; còn lại là báo động giả. Recall theo tuần = tỷ lệ tuần sự cố đang diễn ra có cảnh báo. Độ trễ = ngày cuối tuần cảnh báo đầu tiên − ngày bắt đầu sự cố. Mỗi tập có 22 tuần đánh giá được × 11 chi nhánh (4 tuần đầu dùng làm mức nền).

## Tập phát triển (ngưỡng 3,5)

| Phương pháp | Sự cố bắt được | Đúng nguyên nhân hạng 1 | Trễ trung vị | Số cảnh báo | Báo động giả | Precision | Recall tuần | F1 |
|---|---|---|---|---|---|---|---|---|
| Đề xuất | 5/6 | 5/5 | 6 ngày | 18 | 5 | 0,72 | 0,87 | 0,79 |
| Chỉ theo dõi doanh thu, \|z\| ≥ 3 | 0/6 | — | — | 2 | 2 | 0 | 0 | 0 |
| Isolation Forest, cùng số cảnh báo | 3/6 | — | 6 ngày | 18 | 14 | 0,22 | 0,27 | 0,24 |

Bỏ sót: S5 thất thoát kho CN9 (điểm 2,8).

## Tập kiểm tra (chạy một lần, ngưỡng 3,5)

| Phương pháp | Sự cố bắt được | Đúng nguyên nhân hạng 1 | Trễ trung vị | Số cảnh báo | Báo động giả | Precision | Recall tuần | F1 |
|---|---|---|---|---|---|---|---|---|
| Đề xuất | 4/6 | 3/4 | 6 ngày | 14 | 7 | 0,50 | 0,54 | 0,52 |
| Chỉ theo dõi doanh thu, \|z\| ≥ 3 | 1/6 | — | 27 ngày | 5 | 4 | 0,20 | 0,08 | 0,11 |
| Isolation Forest, cùng số cảnh báo | 2/6 | — | 16,5 ngày | 14 | 12 | 0,14 | 0,15 | 0,15 |

Theo sự cố: H1 hoa hồng sàn CN10, H2 đơn sàn không vào POS CN3, H3 hao hụt CN1 đều bắt được sau 6 ngày, đúng nguyên nhân. H6 gian lận thu ngân CN10 chỉ được cảnh báo ở tuần thứ tư dưới dạng "doanh thu lệch, chưa xác định nguyên nhân" (trễ 27 ngày). Bỏ sót H4 thiếu nhân sự CN8 và H5 thất thoát kho CN5.

Báo động giả: 4 tuần doanh thu lệch không khớp nguyên nhân ở các chi nhánh hạng C (CN4, CN5, CN11 – nhóm cùng hạng chỉ có 3 chi nhánh nên mức kỳ vọng nhiễu), 2 tuần P2 ở CN6 tháng 5, 1 tuần P5 ở CN2.

## Phân tích lỗi (thực hiện sau khi biết đáp án, chỉ để giải thích, không thay đổi kết quả trên)

| Sự cố | Điểm nguyên nhân đúng (cao nhất trong cửa sổ) | Hạng | Giải thích |
|---|---|---|---|
| H6 gian lận thu ngân | 3,44 | 1 | Thiếu ngưỡng 3,5 chỉ 0,06; với ngưỡng 3,0 đã bắt được ở tuần đầu. Mức gian lận nhẹ hơn S6 (5–8 so với 14–20 hóa đơn mỗi tuần). |
| H4 thiếu nhân sự | 2,82 | 1 | Ca bếp tối giảm rõ (z = −5,6) nhưng sự cố chỉ 10 ngày nên hậu quả vừa phải; điểm P3 là trung bình 5 tín hiệu nên bị kéo xuống. Ở mức "theo dõi". |
| H5 thất thoát kho | ~0 | – | Không có tín hiệu: mất 1,2%/ngày lượng tồn ở chi nhánh nhỏ, kiểm kê 2 tuần/lần. |

Ở cả 5 sự cố có tín hiệu, nguyên nhân đúng đều được xếp hạng 1. Điểm yếu chính là ngưỡng phát cảnh báo và độ nhạy với sự cố nhẹ, ngắn; khả năng chỉ đúng nguyên nhân khi đã có tín hiệu là tốt. Khoảng cách F1 giữa hai tập (0,79 → 0,52) cho thấy phương pháp có phần khớp với tập phát triển, đúng lý do phải tách tập kiểm tra.

## Hướng cải thiện (ghi vào Chương 6, chưa áp dụng)

- Gộp bằng chứng P3 theo trung bình có trọng số hoặc theo tín hiệu gốc (số ca bếp) thay vì trung bình đều.
- Cộng dồn bằng chứng thu ngân qua nhiều tuần (gian lận kéo dài thì tích lũy), thay vì đánh giá từng tuần riêng.
- Kiểm kê nguyên liệu giá trị cao dày hơn (hằng tuần) để phát hiện thất thoát.
- Nhóm so sánh hạng C quá nhỏ (3 chi nhánh): dùng mô hình kỳ vọng có thêm biến quy mô thay vì trung vị nhóm.

## Độ nhạy theo cách tính mức kỳ vọng (17/10/2026, CHỈ tập phát triển)

Nguồn: `python -m analytics.sensitivity` → `calibration_do_nhay_phuong_phap.csv`, `calibration_minh_hoa_luat_vs_z.csv`. Chương trình tính lại bảng `mart_kpi_vs_peers_weekly` bằng Python (khớp tuyệt đối bảng dbt, 8.954 dòng), mỗi lần thay một lựa chọn, giữ ngưỡng 3,5. Từ chối chạy trên tập kiểm tra. Không đổi cấu hình đã chốt.

| Phương án | Sự cố | Cảnh báo | Báo động giả | Trong đó do lệch doanh thu/nhân sự | Precision | Recall tuần | F1 |
|---|---|---|---|---|---|---|---|
| Đề xuất (nhóm cùng hạng, trung vị/MAD 8 tuần, có sàn) | 5/6 | 18 | 5 | 2 | 0,72 | 0,87 | 0,79 |
| So toàn chuỗi | 5/6 | 20 | 7 | 4 | 0,65 | 0,87 | 0,74 |
| Không so nhóm, chỉ lịch sử | 5/6 | 20 | 7 | 4 | 0,65 | 0,87 | 0,74 |
| Cửa sổ 4 tuần | 5/6 | 27 | 15 | 12 | 0,44 | 0,80 | 0,57 |
| Cửa sổ 12 tuần | 5/6 | 17 | 4 | 1 | 0,76 | 0,87 | 0,81 |
| Trung bình + độ lệch chuẩn | 5/6 | 17 | 5 | 2 | 0,71 | 0,80 | 0,75 |
| Bỏ sàn độ dao động | 5/6 | 26 | 13 | 10 | 0,50 | 0,87 | 0,63 |

- Sàn độ dao động và cửa sổ đủ dài quan trọng nhất; cửa sổ 4 tuần và trung bình/độ lệch chuẩn đều làm mất tuần thứ hai của S4 (tuần sự cố đầu nhiễm vào mức nền).
- Không so nhóm: CN1 tuần lễ 29/4 bị cảnh báo P3 (gán nhầm), tuần lễ 2/9 bị cảnh báo "chưa xác định".
- Cửa sổ 12 tuần tốt hơn nhẹ (bớt 1 báo động giả). Ghi trung thực vào báo cáo; KHÔNG đổi cấu hình (tập kiểm tra chỉ có giá trị với cấu hình chốt trước), ghi vào hướng phát triển.
- Minh họa P1a: nếu sàn tính thừa 5 điểm % kéo dài 17 tuần (CN4 từ 13/5), luật bắt 17/17 tuần, điểm z ≥ 3 chỉ 4 tuần đầu (tuần 5: z = 0,67; từ tuần 6: z = 0).
