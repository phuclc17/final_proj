# Thử nghiệm "ngày xấu": nhiều tình huống dữ liệu bất thường cùng lúc

Chạy bằng `python tools/thu_tinh_huong.py` lúc 17/10/2026 04:43, trên môi trường vận hành (khôi phục về điểm demo trước và sau khi thử). Hệ thống nguồn ghi 7 ngày 23–29/09/2024: POS cài tại máy (CN5, CN7, CN10), chấm công, kho, sàn xuất tệp vào vùng tiếp nhận; POS đám mây (8 chi nhánh) và App ghi vào kho của phần mềm, chỉ lấy được qua API. Sau đó các tình huống dưới đây được cài vào. Đường ống chạy hai lượt, không có thao tác tay nào ở giữa.

## API nguồn sập rồi hoạt động lại

Lượt 1, API không phản hồi: mã thoát 1, 105 giây, Gold vẫn đến ngày 22/09/2024. Các bước: extract warn (POS đám mây: lỗi: API không phản hồi được sau 6 lần thử (lần cuối mạng: không kết nối được); check ok (179 tep moi: grab 1, khongnhandang 2, pos 23, shopee 1, stock 1, timekeeping 77, warehouse); ingest ok (Tong: 174 file moi, 4411 dong moi, 3 file loi, 2 file khong nhan dang); quality failed (4 cảnh báo, 2 chặn, 9 đạt)

Cửa chặn chất lượng lượt 1: [chặn] độ mới app_orders: Dữ liệu mới nhất 22/09/2024, chậm 7 ngày so với 29/09/2024.; [cảnh báo] khối lượng pos_receipts: Ngày 29/09/2024: 329 dòng. trung vị 14 ngày trước 1.604.; [chặn] đầy đủ pos, chấm công: Thiếu hàng loạt: 23/09 thiếu POS của 10/11 chi nhánh; 24/09 thiếu POS của 8/11 chi nhánh; 25/09 thiếu POS của 8/11 chi nhánh; 26/09 thiếu POS của 8/11 chi nhánh; [cảnh báo] tệp lỗi bronze: Tệp không đọc được: pos/POS-05/pos_export_2024-09-23.json (JSONDecodeError('Unterminated string starting at: line 1 column 4994 (char 4993)')); [cảnh báo] sai hợp đồng bronze: Tệp sai hợp đồng dữ liệu, không nạp: pos/POS-07/pos_export_2024-09-30.json (Tên hoặc vị trí tệp không khớp nội dung: nội dung thuộc pos/POS-07/pos_export_2024-0; [cảnh báo] không nhận dạng bronze: Tệp không thuộc nguồn nào, không nạp: bang_luong_thang_9.xlsx (Không thuộc nguồn nào. Tệp Excel không khớp hợp đồng của báo cáo ShopeeFood, sổ nhập kho hay phiế

Lượt 2, API hoạt động lại: mã thoát 0, 66 giây. Các bước: extract ok (POS đám mây: 7 ngày mới, 56 tệp ghi (10365 bản ghi, 55 trang, thử lại 4); App đặt hàng: 7 ); check ok (63 tep moi: app 7, pos 56); ingest ok (Tong: 63 file moi, 14245 dong moi, 1 file loi); quality ok (12 đạt, 3 cảnh báo); dbt ok (Done. PASS=211 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=211); detect ok (tuan 23/09/2024: 2 canh bao; CN1 P1a 6.0; CN3 P3 4.8); publish ok (Da dua 22 bang, 1.499.991 dong sang Postgres, doi soat so dong khop, 9 giay)

Bộ kết nối lượt 2: POS đám mây: 7 ngày mới, 56 tệp ghi, 10365 bản ghi, 55 trang, 60 lần gọi, 4 lần thử lại do API lỗi tạm thời; App đặt hàng: 7 ngày mới, 7 tệp ghi, 3880 bản ghi, 24 trang, 28 lần gọi, 3 lần thử lại do API lỗi tạm thời

## Từng tình huống

| Tình huống | Cách đưa vào | Mong đợi | Kết quả đo được | Ghi chú hệ thống |
|---|---|---|---|---|
| Tệp POS bị hỏng (ghi dở, cắt ngang) | tệp POS CN5 ngày 23/09 bị cắt | không nạp, ghi lỗi đọc; các tệp khác vẫn nạp; cảnh báo thiếu POS của CN5 | không đọc được, không nạp | JSONDecodeError('Unterminated string starting at: line 1 column 4994 (char 4993)') |
| Tệp POS rỗng | tệp POS CN10 ngày 23/09 không có hóa đơn nào | nạp 0 dòng; cửa chặn coi như thiếu tệp, cảnh báo; không kết luận sự cố cho CN10 | nạp, 0 dòng |  |
| Tệp chấm công thiếu cột bắt buộc | tệp chấm công CN4 mất cột event_type | không nạp, ghi sai hợp đồng; cảnh báo thiếu chấm công CN4 | sai hợp đồng, không nạp | Tệp chấm công thiếu cột: event_type |
| Tệp CSV bảng mã UTF-16 | tệp chấm công CN2 xuất từ phần mềm cũ | đọc được, nạp bình thường | nạp, 24 dòng |  |
| Báo cáo sàn lưu nhầm định dạng | báo cáo GrabFood tuần 38 lưu thành .xlsx, thả vào thư mục GrabFood | không nạp, ghi 'không nhận dạng' kèm gợi ý gửi tệp CSV | không nhận dạng, không nạp | Không thuộc nguồn nào. Giống báo cáo GrabFood nhưng GrabFood gửi CSV; hãy tải lên đúng tệp CSV gốc từ cổng đối tác. |
| Tệp lạ không thuộc nguồn nào | bảng lương thả vào vùng tiếp nhận | không nạp, ghi 'không nhận dạng' | không nhận dạng, không nạp | Không thuộc nguồn nào. Tệp Excel không khớp hợp đồng của báo cáo ShopeeFood, sổ nhập kho hay phiếu kiểm kê. |
| Tệp trùng nội dung, đặt tên khác | tệp POS CN7 ngày 23/09 chép thành tên ngày 30/09 | không nạp: tên tệp ghi ngày 30/09 nhưng nội dung là ngày 23/09 | sai hợp đồng, không nạp | Tên hoặc vị trí tệp không khớp nội dung: nội dung thuộc pos/POS-07/pos_export_2024-09-23.json. Nạp sẽ ghi sai ngày, sai chi nhánh hoặc đếm hai lần. |
| Máy POS chưa khai báo trong bảng ánh xạ | tệp POS của máy POS-12 | Bronze nạp; Silver cách ly vì không gắn được chi nhánh | nạp, 3 dòng; Silver cách ly 3 dòng khong_anh_xa_duoc_chi_nhanh |  |
| Bản sửa gửi lại | phiếu kiểm kê CN03 ngày 22/09 đếm lại | nạp lại, thay toàn bộ bản cũ | nạp lại thay bản cũ, 22 dòng |  |
| Tệp đến muộn cho ngày cũ | phiếu nhập CN01 ngày 22/09 gửi sau khi ngày đó đã xử lý | nạp bình thường, Silver và Gold tính lại kỳ đó | nạp, 4 dòng |  |
| Nguồn đổi cấu trúc, thêm trường mới | API POS đám mây trả thêm trường loyalty_tier (CN1 ngày 23/09) | kéo về, nạp bình thường; cửa chặn cảnh báo trường mới | nạp, 168 dòng |  |

## Cửa chặn chất lượng ghi nhận

| Kiểm tra | Nguồn | Mức | Nội dung |
|---|---|---|---|
| đầy đủ | pos, chấm công | cảnh báo | 23/09 POS-05 thiếu tệp POS; 23/09 POS-10 thiếu tệp POS; 23/09 BR04 thiếu tệp chấm công. Doanh thu, giờ công của chi nhánh ngày đó sẽ thấp giả tạo cho tới khi tệp được gửi bổ sung; bộ phát hiện không kết luận sự cố dựa tr |
| tệp lỗi | bronze | cảnh báo | Tệp không đọc được: pos/POS-05/pos_export_2024-09-23.json (JSONDecodeError('Unterminated string starting at: line 1 column 4994 (char 4993)')) |
| cấu trúc | pos_receipts | cảnh báo | Trường mới xuất hiện: loyalty_tier |

## Bộ phát hiện, tuần 23–29/09

| Chi nhánh | Mức | Nguyên nhân | Điểm |
|---|---|---|---|
| CN10 | Theo dõi | P1b Đơn sàn hoàn thành nhưng không được ghi vào POS (thiếu dữ liệu nguồn trong tuần, chưa kết luận) | 6.0 |
| CN1 | Cảnh báo | P1a Sàn thu hoa hồng sai hợp đồng | 6.0 |
| CN3 | Cảnh báo | P3 Thiếu nhân sự, bếp quá tải, mất đơn | 4.8 |
