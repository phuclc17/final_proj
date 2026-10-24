# CHƯƠNG 5. THỰC NGHIỆM VÀ ĐÁNH GIÁ

NGUON: Kết quả thực nghiệm

Chương này trả lời ba câu hỏi nghiên cứu ở mục 1.3. Sau phần thiết lập thực nghiệm (mục 5.1), mục 5.2 đánh giá đường ống và chất lượng dữ liệu (RQ1), mục 5.3 đánh giá năm bộ phát hiện (RQ2), mục 5.4 đánh giá khả năng truy vết nguyên nhân (RQ3), mục 5.5 phân tích độ nhạy và so sánh với phương án cơ sở. Mục 5.6 trình bày các phát hiện kinh doanh rút ra từ kho dữ liệu, mục 5.7 thảo luận kết quả và tính hợp lệ.

## 5.1. Thiết lập thực nghiệm

### 5.1.1. Dữ liệu và quy trình đánh giá

Thực nghiệm dùng hai tập dữ liệu do bộ mô phỏng sinh ra (mục 3.3.4), đã kiểm chứng ở Bảng 4.3. Hai tập có cùng cấu trúc, 11 chi nhánh, 26 tuần từ 11/03/2024 đến 08/09/2024, nhưng khác hạt giống ngẫu nhiên và kịch bản sự cố. Đường ống và bộ phát hiện chạy giống hệt nhau trên hai tập, mỗi tập một kho riêng. Bốn tuần đầu chỉ dùng làm mức nền, nên mỗi tập có 22 tuần đánh giá được, tức 242 chi nhánh × tuần.

Quy trình được thiết kế để kết quả trên tập kiểm tra phản ánh đúng năng lực của hệ thống khi gặp dữ liệu mới. Mọi tham số, gồm cửa sổ thời gian, ngưỡng và quy tắc gộp bằng chứng, chỉ được chọn trên tập phát triển. Ngưỡng điểm cảnh báo được chọn theo quy tắc khai báo trước: quét từ 2,0 đến 5,0, lấy ngưỡng có F1 cao nhất trên tập phát triển, hòa thì lấy ngưỡng thấp hơn; kết quả là 3,5. Cấu hình cuối được ghi vào `analytics/config.py` và lưu ở commit `60d28bb` ngày 11/10/2026, rồi chạy trên tập kiểm tra đúng một lần, không chỉnh sửa gì sau khi xem kết quả. Chương trình `analytics/evaluate.py` đọc danh sách cảnh báo và đáp án để tính các độ đo; bộ phát hiện không đọc đáp án. Mọi phân tích lỗi thực hiện sau khi biết đáp án chỉ để giải thích và không làm thay đổi kết quả đã báo cáo.

### 5.1.2. Quy tắc đối chiếu và độ đo

Đơn vị đánh giá là chi nhánh × tuần. Cửa sổ của một sự cố gồm các tuần giao với khoảng từ ngày bắt đầu đến 14 ngày sau ngày kết thúc, vì một số hậu quả đến muộn, như thứ hạng sàn giảm sau vài tuần hay hao hụt chỉ lộ ra ở lần kiểm kê kế tiếp. Cảnh báo cùng chi nhánh và nằm trong cửa sổ là cảnh báo đúng, còn lại là báo động giả; cách đánh giá theo khoảng phù hợp với bất thường kéo dài (Tatbul et al., 2018). Việc chỉ đúng nguyên nhân được đánh giá riêng, để tách hai năng lực là phát hiện có vấn đề và chỉ ra đó là vấn đề gì.

Sáu độ đo được dùng: số sự cố bắt được, tức có ít nhất một cảnh báo đúng; số sự cố đúng nguyên nhân hạng một ở cảnh báo đầu tiên; độ trễ phát hiện, tính từ ngày bắt đầu đến ngày cuối của tuần có cảnh báo đúng đầu tiên, nhỏ nhất thường là 6 ngày vì hệ thống đánh giá theo tuần; precision theo công thức (2.11); recall theo tuần, tức tỷ lệ chi nhánh × tuần đang có sự cố mà được cảnh báo; và F1 theo công thức (2.12). Mỗi tập chỉ có sáu kịch bản nên mỗi kịch bản ứng với khoảng 17 điểm phần trăm; vì vậy kết quả được báo cáo chi tiết theo từng kịch bản và từng báo động giả.

## 5.2. Đánh giá đường ống và chất lượng dữ liệu (RQ1)

### 5.2.1. Phát hiện và xử lý lỗi dữ liệu

Bảng 5.1 so sánh các lỗi mà tầng Silver phát hiện trên hai tập. Tỷ lệ gần như giống nhau, phù hợp với việc bộ mô phỏng sinh lỗi theo cùng xác suất; quan trọng hơn, các quy tắc làm sạch xây dựng trên tập phát triển hoạt động không cần sửa trên tập kiểm tra.

TABLE: Bảng 5.1. Lỗi dữ liệu được phát hiện và xử lý ở tầng Silver
WIDTHS: 4.6,3.2,3.2,3.6
| Loại lỗi | Tập phát triển (183 ngày) | Tập kiểm tra (182 ngày) | Cách xử lý |
| Lượt quẹt thẻ trùng | 1.290 (3,03%) | 1.285 (3,03%) | Cách ly |
| Ca thiếu lượt ra | 1.036 ca (4,89%) | 1.023 ca (4,85%) | Gắn cờ; Gold nội suy số giờ, có cờ |
| Nghi gõ gam vào cột kg | 62 dòng (0,38%) | 63 dòng (0,40%) | Cách ly |
| Dòng tổng cộng, chữ ký trong sổ kho | 2.486 | 2.474 | Tách thành dòng cấu trúc |
| Tên nguyên liệu khớp chính xác | 13.576 dòng (84,3%) | 13.336 dòng (84,5%) | Ánh xạ trực tiếp |
| Tên nguyên liệu qua bảng biến thể | 2.528 dòng (15,7%) | 2.453 dòng (15,5%) | Ánh xạ; khớp mờ không phải dùng |
| Ô kiểm kê trống | 77 (2,4%) | 76 (2,4%) | Giữ giá trị thiếu, gắn cờ |
| Hóa đơn POS phiên bản cũ | 59.979 | 59.131 | Chuẩn hóa về lược đồ chung |
| Hóa đơn hủy / hoàn tiền | 1.896 / 2.278 | 1.669 / 2.050 | Giữ lại, gắn cờ, tính phút đến lúc hủy |
| Đơn App lưu giờ UTC | 97.207 | 85.931 | Đổi sang giờ Việt Nam rồi xác định ngày, ca |
| Số lượng dính đơn vị (sổ mẫu B) | 4.536 | 4.470 | Tách số và đơn vị, chuẩn hóa |

Lỗi kỹ thuật như quẹt trùng, gõ nhầm đơn vị được tách khỏi dữ liệu, còn tín hiệu nghiệp vụ như hóa đơn hủy, quên quẹt ra, ô kiểm kê trống được giữ lại kèm cờ, đúng nguyên tắc ở mục 2.4.2. Hạn chế cần ghi nhận là tầng khớp mờ tên nguyên liệu chưa được kiểm chứng, vì mọi biến thể tên do bộ mô phỏng tạo ra đều nằm trong bảng biến thể.

### 5.2.2. Đối soát giữa các tầng và hiệu năng

Đối soát Bronze–Silver ở Bảng 4.8 cho phần không giải thích được bằng 0 ở cả bảy nguồn trên cả hai tập. Doanh thu thuần ở Gold khớp tuyệt đối với tổng tính từ Silver theo từng chi nhánh × ngày, với 37.899.868.200 đồng ở tập phát triển và 33.302.131.300 đồng ở tập kiểm tra. Ở bước đưa sang kho phục vụ, số dòng của cả 22 bảng được so giữa DuckDB và PostgreSQL trước khi đổi lược đồ, và mọi lượt trong nhật ký đều khớp (Bảng 5.2).

TABLE: Bảng 5.2. Kết quả kiểm thử và kiểm tra chất lượng
WIDTHS: 6,2.6,2.6,2.6
| Nội dung | Tập phát triển | Tập kiểm tra | Môi trường vận hành |
| Kiểm thử dbt đạt | 158/158 | 158/158 | 158/158 |
| Bước dbt thành công (mô hình, hạt giống, kiểm thử) | 211/211 | 211/211 | 211/211 |
| Nguồn có chênh lệch số dòng không giải thích được | 0/7 | 0/7 | 0/7 |
| Mục cửa chặn chất lượng đạt mỗi lượt | — | — | 15/15 ở lượt dữ liệu bình thường |

TABLE: Bảng 5.3. Thời gian chạy của từng bước
WIDTHS: 4,4.4,4.4
| Bước | Dựng toàn bộ một tập (182 ngày, trên máy) | Một ngày mới (trong Docker, qua Airflow) |
| Sinh dữ liệu nguồn | khoảng 3,5 phút | khoảng 2 giây |
| Kéo qua API (POS đám mây, App) | — | 0,8 giây, 1.343 hóa đơn và 419 đơn |
| Kiểm tra tệp mới | — | 23,9 giây |
| Nạp Bronze | 80 giây, 6.273 tệp | 20,2 giây, 35 tệp |
| Cửa chặn chất lượng | — | 5,6 giây |
| dbt build (211 bước) | 15–25 giây | 17,4 giây |
| Bộ phát hiện | khoảng 1 giây | 2,0 giây |
| Đưa sang kho phục vụ | khoảng 38 giây, lần đầu | 8,9 giây |

Xử lý một ngày mới qua bảy bước mất khoảng 80 giây (Bảng 5.3), đáp ứng NFR7; phần chậm nhất là liệt kê và đọc tệp qua thư mục gắn vào Docker, đã phân tích ở mục 4.11.3.

### 5.2.3. Độ bền trước dữ liệu bất thường và sự cố nguồn

Để kiểm tra NFR8, chương trình `tools/thu_tinh_huong.py` dựng một “ngày xấu” trên môi trường vận hành: hệ thống nguồn ghi bảy ngày 23–29/09/2024, 11 tình huống dữ liệu bất thường được cài cùng lúc, rồi đường ống chạy hai lượt không có thao tác tay ở giữa, lượt đầu khi API của POS đám mây và App không phản hồi, lượt sau khi API hoạt động lại. Cả 11 tình huống cho đúng kết quả mong đợi đã ghi trước khi chạy và không tệp nào bị bỏ qua im lặng (Bảng 5.4).

TABLE: Bảng 5.4. Kết quả xử lý 11 tình huống dữ liệu bất thường cài cùng lúc (môi trường vận hành, 17/10/2026)
WIDTHS: 4.6,7.4
| Tình huống | Kết quả đo được |
| Tệp POS bị cắt ngang khi ghi (CN5, 23/09) | Không đọc được, không nạp, ghi lỗi; các tệp khác vẫn nạp; cửa chặn báo CN5 thiếu POS ngày 23/09 |
| Tệp POS rỗng (CN10, 23/09) | Nạp 0 dòng; cửa chặn coi như thiếu; bộ phát hiện để CN10 ở mức theo dõi, ghi chưa kết luận |
| Tệp chấm công thiếu cột `event_type` (CN4) | Sai hợp đồng, không nạp, lý do nêu đúng cột thiếu; cửa chặn báo thiếu chấm công CN4 |
| Tệp chấm công xuất bằng bảng mã UTF-16 (CN2) | Đọc được, nạp 24 dòng |
| Báo cáo GrabFood lưu thành Excel | Không nhận dạng, không nạp, kèm gợi ý gửi đúng tệp CSV gốc |
| Bảng lương gửi nhầm vào vùng tiếp nhận | Không nhận dạng, không nạp |
| Tệp POS CN7 ngày 23/09 chép thành tên ngày 30/09 | Sai hợp đồng vì tên không khớp nội dung, không nạp, tránh đếm hai lần |
| Tệp của máy POS-12 chưa khai báo | Bronze nạp 3 dòng; Silver cách ly 3 dòng vì không gắn được chi nhánh |
| Phiếu kiểm kê CN3 ngày 22/09 đếm lại | Nạp lại, thay toàn bộ bản cũ (22 dòng) |
| Phiếu nhập CN1 ngày 22/09 gửi muộn | Nạp 4 dòng; Silver và Gold tính lại kỳ đó |
| API POS đám mây trả thêm trường `loyalty_tier` | Kéo về, nạp bình thường; cửa chặn cảnh báo trường mới |

Với sự cố API, lượt thứ nhất kết thúc sau 105 giây: bộ kết nối thử sáu lần rồi ghi cảnh báo, 174 tệp của các nguồn tệp vẫn được nạp, nhưng cửa chặn chất lượng dừng đường ống trước Silver vì dữ liệu App chậm 7 ngày và mỗi ngày có 8 đến 10 trong 11 chi nhánh thiếu POS. Gold và kho phục vụ giữ nguyên dữ liệu đến 22/09, nên không có cảnh báo hay báo cáo nào từ dữ liệu thiếu. Lượt thứ hai tự lấy đủ bảy ngày, chạy hết đường ống trong 66 giây và đưa ra đúng hai cảnh báo của hai sự cố đã cài.

Hai quy tắc không kết luận trên dữ liệu thiếu (mục 3.7.3) được bổ sung sau khi đã chốt đánh giá, xuất phát từ thử nghiệm tệp xấu và từ lỗi thật của bộ kết nối nêu ở mục 4.3.2: khi tám chi nhánh thiếu POS sáu ngày, ba chi nhánh đủ dữ liệu từng bị cảnh báo “chưa xác định nguyên nhân” vì trung vị nhóm cùng hạng sụt theo các chi nhánh thiếu. Trên hai tập đánh giá, không chi nhánh × tuần nào chịu tác động của hai quy tắc và mã băm của bảng điểm, bảng cảnh báo trùng khớp trước và sau khi bổ sung, nên kết quả ở mục 5.3 không thay đổi. Giới hạn của thử nghiệm là các tình huống dựa trên lỗi thường gặp, và API là dịch vụ giả lập.

## 5.3. Đánh giá các bộ phát hiện (RQ2)

### 5.3.1. Kết quả tổng hợp

TABLE: Bảng 5.5. Kết quả của phương pháp đề xuất trên hai tập (ngưỡng điểm 3,5)
WIDTHS: 5,3,3
| Độ đo | Tập phát triển | Tập kiểm tra |
| Sự cố bắt được | 5/6 | 4/6 |
| Đúng nguyên nhân hạng 1 | 5/5 | 3/4 |
| Độ trễ trung vị | 6 ngày | 6 ngày |
| Số cảnh báo (chi nhánh × tuần) | 18 | 14 |
| Cảnh báo đúng / báo động giả | 13 / 5 | 7 / 7 |
| Precision | 0,72 | 0,50 |
| Recall theo tuần | 0,87 | 0,54 |
| F1 | 0,79 | 0,52 |
| Báo động giả trên số tuần bình thường | 2,3% | 3,2% |

Trên tập kiểm tra, hệ thống bắt được bốn trên sáu sự cố; ba sự cố được chỉ đúng nguyên nhân ngay ở cảnh báo đầu tiên, sau đúng một tuần (Bảng 5.5). F1 giảm từ 0,79 xuống 0,52 khi chuyển sang tập kiểm tra, cho thấy phương pháp có phần khớp với tập phát triển; đó là lý do phải tách tập kiểm tra, vì nếu chỉ báo cáo trên tập phát triển, kết quả sẽ lạc quan hơn thực tế đáng kể. Hình 5.1 đặt từng cảnh báo cạnh thời gian các sự cố: cảnh báo đúng tập trung trong vùng sự cố, báo động giả rải rác ở các chi nhánh hạng C và ở CN10, CN6, còn H4 và H5 bị bỏ sót.

IMAGE: figures/c5_ban_do.png || Hình 5.1. Cảnh báo của bộ phát hiện đặt cạnh thời gian các sự cố, theo chi nhánh × tuần (ngưỡng điểm 3,5) || 14

### 5.3.2. Kết quả theo từng bộ phát hiện

TABLE: Bảng 5.6. Kết quả theo từng loại sự cố
WIDTHS: 3.2,2.2,1.9,1.4,2.2,1.9,1.4
| Bộ phát hiện | Phát triển: sự cố | Phát triển: cảnh báo đúng / tổng | Phát triển: trễ (ngày) | Kiểm tra: sự cố | Kiểm tra: cảnh báo đúng / tổng | Kiểm tra: trễ (ngày) |
| P1a. Hoa hồng sai hợp đồng | S1 bắt được | 3/3 | 6 | H1 bắt được | 2/2 | 6 |
| P1b. Đơn sàn không vào POS | S2 bắt được | 2/3 | 6 | H2 bắt được | 2/2 | 6 |
| P2. Hao hụt vượt định mức | S3 bắt được | 2/4 | 4 | H3 bắt được | 2/4 | 6 |
| P3. Thiếu nhân sự | S4 bắt được | 2/2 | 6 | H4 bỏ sót | 0/0 | — |
| P4. Thất thoát kho | S5 bỏ sót | 0/0 | — | H5 bỏ sót | 0/0 | — |
| P5. Gian lận tại quầy | S6 bắt được | 4/4 | 6 | H6 bắt được, sai nhãn | 0/1 | 27 |
| Chưa xác định nguyên nhân | — | 0/2 | — | — | 1/5 | — |

Cột “cảnh báo đúng / tổng” tính theo nguyên nhân mà hệ thống gán. Hai bộ phát hiện đối soát sàn P1a, P1b ổn định nhất: bắt cả bốn sự cố sau một tuần, không có báo động giả trên tập kiểm tra, phù hợp với bản chất bài toán vì đối soát dựa trên con số so được trực tiếp giữa hai nguồn nên ít phụ thuộc mô hình kỳ vọng. P2 bắt cả hai sự cố hao hụt nhưng có báo động giả ở cả hai tập. Hình 5.2 cho thấy vì sao bốn bộ phát hiện bắt được sự cố trên tập phát triển: tín hiệu của chi nhánh hoặc thu ngân có sự cố tách hẳn khỏi dải của các đối tượng khác đúng trong thời gian sự cố, còn tín hiệu hao hụt lộ ra ở lần kiểm kê ngay sau sự cố.

IMAGE: figures/c5_tin_hieu.png || Hình 5.2. Tín hiệu của bốn bộ phát hiện quanh sự cố trên tập phát triển || 15

### 5.3.3. Phân tích lỗi

Phần này thực hiện sau khi biết đáp án, chỉ để giải thích kết quả (Bảng 5.7, Hình 5.3).

TABLE: Bảng 5.7. Các sự cố bị bỏ sót hoặc gán sai nguyên nhân
WIDTHS: 2.6,2,1.4,8
| Sự cố | Điểm cao nhất của nguyên nhân đúng | Hạng | Giải thích |
| S5 thất thoát kho CN9 | 2,8 | 1 | Ở mức theo dõi, dưới ngưỡng 3,5. Tồn kho mỗi nguyên liệu chỉ đủ 2–4 ngày, nên mất 1,5% lượng tồn mỗi ngày chỉ làm hao hụt nhóm giá trị cao tăng 1–2 điểm % |
| H4 thiếu nhân sự CN8 | 2,82 | 1 | Số ca bếp tối giảm rõ (z = −5,6) nhưng sự cố chỉ 10 ngày, hậu quả vừa phải; điểm P3 là trung bình năm tín hiệu nên bị các tín hiệu yếu kéo xuống |
| H5 thất thoát kho CN5 | gần 0 | — | Không có tín hiệu: chi nhánh nhỏ, mất 1,2% lượng tồn mỗi ngày, kiểm kê hai tuần một lần |
| H6 gian lận thu ngân CN10 | 3,44 | 1 | Thiếu ngưỡng 0,06. Gian lận nhẹ hơn S6 (5–8 so với 14–20 hóa đơn mỗi tuần); chỉ được cảnh báo ở tuần thứ tư khi doanh thu lệch đủ lớn, với nhãn chưa xác định |

IMAGE: figures/c5_diem_su_co.png || Hình 5.3. Điểm cao nhất của nguyên nhân đúng trong cửa sổ từng sự cố, so với ngưỡng cảnh báo và mức theo dõi || 15

Ở cả năm sự cố có tín hiệu trên tập kiểm tra, nguyên nhân đúng đều xếp hạng một trong cửa sổ sự cố, kể cả hai trường hợp chưa vượt ngưỡng. Mười một trên mười hai sự cố có điểm từ mức theo dõi trở lên; ba sự cố S5, H4, H6 nằm giữa mức theo dõi và ngưỡng, tức một ngưỡng thấp hơn sẽ bắt được nhưng phải trả giá bằng nhiều báo động giả hơn (mục 5.5.1). Điểm yếu chính vì vậy nằm ở ngưỡng và độ nhạy với sự cố nhẹ, ngắn, không nằm ở khả năng chỉ đúng nguyên nhân khi đã có tín hiệu. Thất thoát kho là loại khó nhất: với kiểm kê hai tuần một lần và tồn kho chỉ vài ngày, lượng mất nhỏ chìm trong sai số đếm; đây là giới hạn của dữ liệu đầu vào, không chỉ của phương pháp.

Bảy báo động giả trên tập kiểm tra gồm bốn tuần ở chi nhánh hạng C có doanh thu lệch kỳ vọng mà không nguyên nhân nào đủ điểm, vì nhóm chỉ có ba chi nhánh nên trung vị dao động mạnh; hai tuần P2 ở CN6 có hao hụt hàng tươi cao hơn các chi nhánh cùng kỳ; và một tuần P5 ở CN2 có một thu ngân hủy hóa đơn nhiều hơn đồng nghiệp. Năm báo động giả trên tập phát triển gồm hai tuần doanh thu lệch không rõ nguyên nhân, hai tuần P2 và một tuần P1b ở CN10. Các báo động giả này có thiệt hại ước tính nhỏ, như P2 ở CN10 chỉ 66 nghìn đồng và ở CN6 chỉ 29 nghìn đồng so với 6,83 triệu đồng của sự cố hao hụt thật ở CN7, nên khi danh sách sắp theo thiệt hại, chúng nằm cuối và chi phí xử lý thấp.

## 5.4. Đánh giá khả năng truy vết nguyên nhân (RQ3)

### 5.4.1. Ví dụ truy vết: thiếu nhân sự ở CN2

Sự cố S4 làm CN2 thiếu nhân viên bếp ca tối từ 06/05 đến 19/05. Bảng 5.8 trình bày cây KPI và tín hiệu vận hành của CN2 trong tuần đầu sự cố, đúng như trang Truy vết ở Hình 4.10 hiển thị.

TABLE: Bảng 5.8. Truy vết CN2, tuần 06/05–12/05/2024 (tập phát triển)
WIDTHS: 5.6,2.6,2.6,2,1.4
| Nút của cây KPI hoặc tín hiệu | Thực tế | Kỳ vọng | Chênh lệch | z |
| Doanh thu thuần | 233,4 triệu đ | 281,7 triệu đ | −17,2% | −2,8 |
| · Tại quầy | 112,6 triệu đ | 131,8 triệu đ | −14,6% | −1,6 |
| · App | 50,6 triệu đ | 67,5 triệu đ | −25,0% | −3,0 |
| · GrabFood (ghi trên POS) | 41,6 triệu đ | 46,5 triệu đ | −10,5% | −0,9 |
| · ShopeeFood (ghi trên POS) | 28,5 triệu đ | 31,6 triệu đ | −9,7% | −0,7 |
| Số đơn App | 611 | 742 | −17,7% | −2,0 |
| Số ca bếp tối | 11 | 22,7 | −51,6% | −7,1 |
| Thời gian chuẩn bị đơn App | 20,9 phút | 14,2 phút | +47,1% | +2,9 |
| Tỷ lệ cửa hàng tự hủy đơn App | 6,2% | 1,1% | +5,1 điểm % | +8,0 |
| Tỷ lệ khách hủy vì chờ lâu | 3,3% | 0,5% | +2,8 điểm % | +3,5 |
| Điểm đánh giá GrabFood | 4,3 | 4,5 | −0,2 | −4,0 |

Cây KPI cho thấy chênh lệch nằm chủ yếu ở số đơn chứ không ở giá trị đơn, và nặng nhất ở kênh App, kênh mà cửa hàng tự hủy đơn khi quá tải. Các tín hiệu vận hành cùng chỉ một hướng: số ca bếp tối giảm một nửa, thời gian chuẩn bị tăng gần 50%, cửa hàng tự hủy đơn App tăng gấp năm; bộ phát hiện xếp P3 hạng một với điểm 4,3. Chỉ nhìn doanh thu thì tuần này chưa đủ để cảnh báo, vì z = −2,8 còn dưới 3; chính các tín hiệu vận hành đã đẩy tuần này lên mức cảnh báo. Hậu quả kéo dài cũng được ghi nhận: ở tuần 20/05, khi nhân sự đã trở lại với 26 ca bếp tối và thời gian chuẩn bị 13,3 phút, doanh thu GrabFood của CN2 vẫn thấp hơn kỳ vọng 22,1% với điểm đánh giá 4,3 so với 4,5, và hệ thống xếp tuần này ở mức theo dõi. Đây đúng là chuỗi nhân quả trễ qua thứ hạng sàn ở mục 3.3.2, như Hình 5.4 cho thấy.

IMAGE: figures/c5_truy_vet_cn2.png || Hình 5.4. Doanh thu thuần và số ca bếp tối của CN2 so với mức kỳ vọng; vùng tô là thời gian sự cố S4 || 15

### 5.4.2. Chỉ đúng nguyên nhân và phân biệt với biến động bình thường

Trên tập phát triển, cả năm sự cố bắt được đều được chỉ đúng nguyên nhân ngay ở cảnh báo đầu tiên; trên tập kiểm tra, ba trên bốn, còn H6 được cảnh báo với nhãn “chưa xác định nguyên nhân” chứ không bị gán nhầm sang nguyên nhân khác. Trong toàn bộ 32 cảnh báo của hai tập, không cảnh báo nào nằm trong cửa sổ một sự cố mà lại chỉ sai sang một nguyên nhân vận hành khác. Bảng 5.9 xét các tuần có biến động chung lớn trên toàn chuỗi.

TABLE: Bảng 5.9. Cảnh báo trong các tuần có biến động bình thường lớn
WIDTHS: 4.8,3.2,2.3,4.4
| Tuần (tập) | Biến động chung | Doanh thu chuỗi so với tuần trước | Cảnh báo trong tuần |
| 29/04 (phát triển), lễ 30/4–1/5 | Hai ngày lễ | +10,0% | 0 |
| 02/09 (phát triển), lễ 2/9 | Hai ngày lễ | +7,6% | 0 |
| 15/04 (phát triển), Giỗ Tổ | Một ngày lễ | +7,0% | 2, đều thuộc kho (CN7 sự cố thật; CN10 báo động giả P2) |
| 03/06 (phát triển), sau điều chỉnh giá, 6 ngày mưa | AOV +3,3%, mưa nhiều nhất | +2,7% | 0 |
| 29/04 (kiểm tra), lễ 30/4–1/5 | Hai ngày lễ | +7,9% | 1, sự cố thật H2 |
| 02/09 (kiểm tra), lễ 2/9 | Hai ngày lễ | +5,5% | 1, báo động giả P5 ở một thu ngân |

Không cảnh báo nào trong các tuần này được gán cho biến động doanh thu chung; các cảnh báo xuất hiện đều đến từ bằng chứng riêng của chi nhánh về kho, thu ngân hoặc đối soát sàn. Lý do là mức kỳ vọng tính theo nhóm cùng hạng trong cùng tuần nên tác động của lễ, mưa và điều chỉnh giá lên cả nhóm tự triệt tiêu, trong khi doanh thu ngày lễ cao hơn ngày thường 21–23% (Bảng 4.4), lớn hơn tác động doanh thu của phần lớn sự cố. Điểm yếu lộ ra ở hạng C: nhóm chỉ có ba chi nhánh, mỗi chi nhánh so với trung vị của hai chi nhánh còn lại, nên biến động riêng của một chi nhánh làm lệch kỳ vọng của các chi nhánh khác; bốn trên bảy báo động giả trên tập kiểm tra rơi vào hạng C.

## 5.5. Phân tích độ nhạy và so sánh với phương án cơ sở

### 5.5.1. Độ nhạy theo ngưỡng điểm cảnh báo

Ngưỡng điểm điều chỉnh đánh đổi giữa bỏ sót và báo động giả (Hình 5.5). Ở ngưỡng 2,0 hệ thống bắt cả sáu sự cố nhưng có 26 báo động giả; ở 2,5 vẫn bắt đủ sáu với 15 báo động giả, bằng số cảnh báo đúng. Ngưỡng 3,5 cho F1 cao nhất 0,79 với 5 báo động giả nên được chốt; từ 4,0 trở lên recall giảm nhanh. Ở mọi ngưỡng, sự cố đã bắt được đều có nguyên nhân hạng một đúng. Trên thực tế, ngưỡng nên do người quản lý chọn theo khả năng xử lý cảnh báo của bộ phận mình, nên ứng dụng cho thay đổi ngưỡng trên trang Trung tâm cảnh báo, còn kết quả chính thức luôn báo cáo ở ngưỡng đã chốt.

IMAGE: figures/c5_nguong.png || Hình 5.5. Precision, recall theo tuần và F1 trên tập phát triển theo ngưỡng điểm cảnh báo; hai dòng phía trên là số sự cố bắt được và số báo động giả || 15

### 5.5.2. So sánh với phương án cơ sở

Hai phương án cơ sở chạy trên cùng dữ liệu Gold. Phương án thứ nhất chỉ theo dõi doanh thu, cảnh báo khi |z| doanh thu thuần từ 3, tức cách làm phổ biến khi chỉ có báo cáo doanh thu. Phương án thứ hai là Isolation Forest (Liu et al., 2008) cài bằng scikit-learn (Pedregosa et al., 2011), phát hiện bất thường không giám sát trên vector z của cả 24 chỉ số, được đưa ra đúng số cảnh báo như phương pháp đề xuất để so sánh công bằng (Bảng 5.10, Hình 5.6).

TABLE: Bảng 5.10. So sánh với các phương án cơ sở
WIDTHS: 4.6,2.2,1.9,1.7,1.9,1.4
| Phương pháp | Tập | Sự cố bắt được | Precision | Recall theo tuần | F1 |
| Đề xuất: bộ chỉ số giám sát và dấu vân tay nguyên nhân | Phát triển | 5/6 | 0,72 | 0,87 | 0,79 |
|  | Kiểm tra | 4/6 | 0,50 | 0,54 | 0,52 |
| Chỉ theo dõi doanh thu, lệch từ 3 đơn vị z | Phát triển | 0/6 | 0,00 | 0,00 | 0,00 |
|  | Kiểm tra | 1/6 | 0,20 | 0,08 | 0,11 |
| Isolation Forest, cùng số cảnh báo | Phát triển | 3/6 | 0,22 | 0,27 | 0,24 |
|  | Kiểm tra | 2/6 | 0,14 | 0,15 | 0,15 |

IMAGE: figures/c5_so_sanh.png || Hình 5.6. Precision, recall theo tuần và F1 của phương pháp đề xuất và hai phương án cơ sở || 15

Theo dõi doanh thu gần như không phát hiện được sự cố nào, vì phần lớn sự cố không làm doanh thu lệch đủ xa: hoa hồng sai và hao hụt làm tăng chi phí chứ không giảm doanh thu, gian lận chỉ vài triệu đồng mỗi tuần, và ngay cả S4 cũng chỉ làm doanh thu lệch z = −2,8. Đây là bằng chứng định lượng cho nhận định ở mục 1.1 rằng nhìn con số tổng hợp không đủ để phát hiện sự cố vận hành. Isolation Forest dùng đúng các chỉ số như phương pháp đề xuất nhưng chỉ tìm điểm “lạ” chung chung, không biết chiều nào là xấu và chỉ số nào đi cùng nhau, nên phần lớn cảnh báo rơi vào các tuần lạ mà vô hại, và cũng không cho biết nguyên nhân.

### 5.5.3. Độ nhạy theo cách tính mức kỳ vọng

Mục này kiểm tra từng lựa chọn của cách tính mức kỳ vọng ở mục 3.7.2: mỗi lần chỉ thay một lựa chọn, giữ nguyên phần khác và ngưỡng 3,5, rồi chấm lại trên tập phát triển. Chương trình `analytics/sensitivity.py` tính lại bảng mức kỳ vọng bằng Python và trước khi thay đổi gì đã được đối chiếu khớp tuyệt đối với bảng do dbt sinh ra trên 8.954 dòng. Tập kiểm tra không được dùng vì đã được đánh giá một lần với cấu hình đã chốt.

IMAGE: figures/c5_do_nhay.png || Hình 5.7. F1 và số báo động giả theo cách tính mức kỳ vọng (tập phát triển, ngưỡng điểm 3,5) || 15

Hình 5.7 cho thấy mọi phương án đều bắt 5/6 sự cố, nhưng khác nhau ở số báo động giả; phần màu đỏ là báo động giả do lệch doanh thu hoặc nhân sự, tức loại chịu ảnh hưởng của mức kỳ vọng, còn ba báo động giả về kho và đối soát ở CN10 thì giống nhau ở mọi phương án. Sàn độ dao động và độ dài cửa sổ ảnh hưởng lớn nhất: bỏ sàn làm báo động giả tăng từ 5 lên 13 và F1 giảm còn 0,63, vì có chi nhánh mà tám tuần trước tình cờ rất đều làm z bị thổi phồng; cửa sổ 4 tuần làm báo động giả tăng lên 15, F1 0,57, đồng thời S4 chỉ còn được cảnh báo một tuần vì tuần sự cố đầu đã chiếm một phần tư mức nền của tuần sau. Trung bình và độ lệch chuẩn cho cùng số báo động giả nhưng bỏ sót tuần thứ hai của S4 (F1 0,75), vì tuần sự cố đầu làm độ lệch chuẩn phình ra, đúng lý do chọn trung vị và MAD. So với toàn chuỗi, hoặc chỉ dùng lịch sử của chính chi nhánh, đều thêm hai báo động giả (F1 0,74), trong đó các tuần lễ 29/4 và 2/9 ở CN1 bị cảnh báo và tuần 29/4 còn bị gán nhầm là thiếu nhân sự; so với nhóm cùng hạng loại được đúng loại lỗi này.

Cửa sổ 12 tuần cho kết quả tốt hơn nhẹ cửa sổ 8 tuần đang dùng, ít hơn một báo động giả và F1 0,81. Khi phát triển, cửa sổ 8 tuần được chọn khi so với 4 tuần, cửa sổ dài hơn chưa được thử trước khi chốt. Khóa luận không đổi cấu hình, vì kết quả trên tập kiểm tra chỉ có giá trị với cấu hình đã chốt trước khi xem nó; chênh lệch chỉ là một cảnh báo trên chính tập phát triển, và cửa sổ dài phản ứng chậm hơn với các thay đổi bền vững như đổi cơ cấu kênh. Thử cửa sổ dài hơn trên một tập kiểm tra mới được ghi vào hướng phát triển.

Cuối cùng, lập luận dùng luật thay vì điểm z cho P1a (mục 3.7.3) cũng được kiểm tra bằng cách sửa chuỗi chênh lệch hoa hồng GrabFood của CN4 theo giả định sàn tính thừa 5 điểm % từ tuần 13/5 đến hết kỳ, tức 17 tuần. Luật đối soát cảnh báo cả 17 tuần, còn điểm z chỉ vượt 3 ở bốn tuần đầu và bằng 0 từ tuần thứ sáu, vì mức nền trung vị tám tuần đã gồm phần lớn các tuần bị tính sai (Hình 5.8). Với phương pháp dựa trên lịch sử, một sai lệch kéo dài dần trở thành “bình thường”; với bài toán tuân thủ hợp đồng, luật so trực tiếp với tỷ lệ cam kết mới là công cụ đúng.

IMAGE: figures/c5_luat_z.png || Hình 5.8. Điểm bằng chứng P1a theo luật đối soát và theo điểm z khi sai lệch hoa hồng kéo dài 17 tuần (giả định trên dữ liệu CN4) || 15

## 5.6. Các phát hiện kinh doanh

Các số liệu trong mục này được tính hoàn toàn từ kho dữ liệu 182 ngày của tập phát triển, không lấy từ đáp án. Vì dữ liệu là mô phỏng, các phát hiện minh họa loại câu hỏi mà nền tảng trả lời được, không phải kết luận về một doanh nghiệp thật.

### 5.6.1. Cơ cấu chi phí theo hạng chi nhánh

Doanh thu bình quân mỗi chi nhánh mỗi tuần là 261,2 triệu đồng ở hạng A, 113,1 triệu ở hạng B và 33,8 triệu ở hạng C. COGS% định mức như nhau ở cả ba hạng, đều 31,0%, nhưng Labor% của hạng C là 29,1%, gấp khoảng 3,4 lần mức 8,6% của hạng A; hạng B ở giữa với 12,4%. Đây là phát hiện về cấu trúc chứ không phải sự cố: chi nhánh phải có số người tối thiểu cho mỗi ca dù ít đơn, nên năng suất ở hạng C chỉ 1,04 đơn mỗi giờ công so với 3,44 ở hạng A; Hình 5.9 cho thấy ba hạng tạo thành ba cụm tách biệt trên cùng một đường cong. Hệ quả cho việc giám sát là không thể dùng một ngưỡng Labor% chung cho mọi chi nhánh mà phải so theo nhóm cùng hạng. Labor% ở đây chỉ gồm lương giờ trực tiếp theo chấm công, chưa gồm lương cố định của quản lý và bảo hiểm, nên thấp hơn mức thường gặp trong thực tiễn.

IMAGE: figures/c5_nhan_cong.png || Hình 5.9. Labor% và số đơn mỗi giờ công của từng chi nhánh × tuần, theo hạng chi nhánh (tập phát triển) || 15

### 5.6.2. Hiệu quả theo kênh, ảnh hưởng của mưa và điều chỉnh giá

Tại quầy chiếm 52% doanh thu thuần, ứng dụng riêng 22%, GrabFood 16%, ShopeeFood 10%. Theo báo cáo đối soát, tổng phí sàn giữ lại, gồm hoa hồng, quảng cáo và khuyến mãi do cửa hàng tài trợ, bằng 27,7% doanh thu món trên GrabFood và 24,7% trên ShopeeFood. Cộng với giá vốn định mức khoảng 31%, mỗi 100 đồng bán qua GrabFood chỉ còn khoảng 41 đồng trước chi phí nhân công và mặt bằng, so với khoảng 69 đồng tại quầy; điều này giải thích vì sao một sai lệch nhỏ của tỷ lệ hoa hồng như P1a đáng được kiểm soát hằng tuần.

Không tính ngày lễ, so với 118 ngày khô, vào 59 ngày mưa mỗi chi nhánh có ít hơn 27% đơn tại quầy, nhiều hơn 19% đơn App và 21% đơn sàn; tỷ trọng đơn giao hàng tăng từ 43,6% lên 56,0%, còn doanh thu mỗi ngày giảm 5,3%. Vì đơn sàn chịu phí khoảng một phần tư, ngày mưa làm biên lợi nhuận giảm nhiều hơn doanh thu, gợi ý dịch chuyển nhân sự từ quầy sang khu đóng gói vào ngày dự báo mưa và ưu tiên kéo khách sang ứng dụng riêng. Sau điều chỉnh giá sáu món ngày 01/06, AOV hai tuần sau tăng 3,4% và COGS% định mức giảm từ 31,6% xuống 30,6%; số đơn không giảm, nhưng điều này chỉ phản ánh giả định của bộ mô phỏng vốn chưa mô hình hóa độ co giãn của cầu theo giá (mục 3.3.5).

### 5.6.3. Ma trận thực đơn

Theo phương pháp menu engineering (Kasavana & Smith, 1982), mỗi món được xếp theo mức phổ biến, so tỷ trọng số lượng bán với 70% mức bình quân 1/28, và lãi gộp mỗi phần, so với bình quân có trọng số 29.357 đồng (Hình 5.10). Nhóm ngôi sao có 5 món, chiếm 23,2% số lượng và 35,6% lãi gộp, tiêu biểu là gà giòn combo 2 miếng và burger gà giòn phô mai. Nhóm ngựa kéo có 5 món, chiếm 51,2% số lượng nhưng chỉ 33,3% lãi gộp, gồm gà giòn miếng đơn với 23,3% số lượng. Nhóm câu đố có 9 món với 13,3% số lượng và 25,5% lãi gộp, nổi bật là combo gia đình 4 người lãi 182.920 đồng mỗi phần. Nhóm chó có 9 món với 12,4% số lượng và 5,7% lãi gộp, như trà sữa, nước suối, súp ngô và salad. Hành động gợi ý là đẩy khách từ miếng đơn sang các combo nhóm ngôi sao bằng gợi ý bán kèm, quảng bá nhóm câu đố và xem xét rút gọn nhóm chó; phân tích này dùng giá vốn định mức, chưa tính hao hụt thực tế theo món.

IMAGE: figures/c5_thuc_don.png || Hình 5.10. Ma trận thực đơn: tỷ trọng số lượng bán và lãi gộp mỗi phần của 28 món (tập phát triển) || 15

### 5.6.4. Thiệt hại ước tính của các sự cố được phát hiện

TABLE: Bảng 5.11. Thiệt hại ước tính từ kho dữ liệu cho các sự cố được phát hiện (tập phát triển)
WIDTHS: 3.4,4.6,2.6,4
| Sự cố | Cách ước tính (mục 4.8) | Ước tính | Đối chiếu sau với tác động đo bởi bộ mô phỏng (Bảng 4.3) |
| S1 hoa hồng GrabFood CN4 | Hoa hồng thu thừa lũy kế 3 tuần | 0,72 triệu đ | Khớp: sàn tính 30% thay vì 25% |
| S2 đơn sàn không vào POS CN6 | Đơn thiếu vượt mức thường × giá trị đơn sàn, 2 tuần | 7,12 triệu đ | 8,52 triệu đ |
| S3 hao hụt CN7 | Hao hụt vượt mức thường của kỳ kiểm kê | 6,83 triệu đ | khoảng 7,5 triệu đ (682 nghìn đ/ngày × 11 ngày) |
| S4 thiếu nhân sự CN2 | Doanh thu thấp hơn kỳ vọng, 2 tuần | 94,6 triệu đ | Doanh thu thấp hơn nhóm cùng hạng 16,9% trong kỳ |
| S6 gian lận thu ngân CN8 | Giá trị hóa đơn bị hủy, hoàn, giảm giá của thu ngân nghi vấn, 4 tuần | 5,74 triệu đ (giá trị liên quan) | 5,31 triệu đ hóa đơn bị hủy sau khi thu tiền |

Các ước tính được tính hoàn toàn từ kho dữ liệu; cột cuối chỉ dùng để kiểm tra độ hợp lý sau khi đã tính. Ước tính cùng bậc độ lớn với tác động thật, đủ để xếp thứ tự ưu tiên. Thiếu nhân sự là sự cố đắt nhất, gấp hơn mười lần các sự cố còn lại, dù về dữ liệu nó chỉ là vài ca làm việc bị thiếu; ngược lại, gian lận và thất thoát kho nhỏ về tiền nhưng là vấn đề kiểm soát nội bộ nên vẫn cần được xử lý.

## 5.7. Thảo luận

### 5.7.1. Trả lời các câu hỏi nghiên cứu

Với RQ1, câu trả lời là có. Đường ống tích hợp được bảy nhóm hệ thống nguồn với ba định dạng tệp, hai phiên bản lược đồ POS, sáu hệ mã chi nhánh và tên nguyên liệu tự do vào một lược đồ hình sao, kiểm chứng bằng ba lớp: 158/158 kiểm thử dbt đạt trên cả ba tập, đối soát số dòng không có chênh lệch không giải thích được, doanh thu thuần Gold khớp tuyệt đối với Silver. Đường ống chạy tăng dần, lũy đẳng, xử lý một ngày mới trong khoảng 80 giây và chịu được 11 tình huống dữ liệu bất thường. Giới hạn là các lỗi do bộ mô phỏng sinh ra, chưa bao phủ hết lỗi của dữ liệu thật.

Với RQ2, trên tập kiểm tra chưa từng dùng để chọn ngưỡng, hệ thống bắt được bốn trên sáu sự cố với precision 0,50, recall theo tuần 0,54, F1 0,52 và độ trễ trung vị 6 ngày, vượt rõ hai phương án cơ sở là chỉ theo dõi doanh thu (1/6, F1 0,11) và Isolation Forest (2/6, F1 0,15). Mức độ chính xác khác nhau theo loại sự cố: đối soát sàn đáng tin cậy nhất; hao hụt bắt được nhưng có báo động giả; thiếu nhân sự nhẹ và gian lận nhẹ nằm sát dưới ngưỡng; thất thoát kho không phát hiện được với nhịp kiểm kê hai tuần.

Với RQ3, câu trả lời là phần lớn có thể. Khi sự cố đã có tín hiệu, nguyên nhân đúng luôn xếp hạng một, ở cả 5/5 sự cố có tín hiệu trên tập kiểm tra, và không cảnh báo nào trong cửa sổ sự cố bị chỉ sang nguyên nhân sai. Mức kỳ vọng theo nhóm cùng hạng loại được biến động của ngày lễ, mưa, điều chỉnh giá; bỏ so nhóm thì tuần lễ bị cảnh báo và có tuần bị gán nhầm là thiếu nhân sự. Giới hạn chính là nhóm hạng C quá nhỏ, gây bốn trên bảy báo động giả trên tập kiểm tra.

### 5.7.2. So sánh với các nghiên cứu liên quan

Kết quả không so sánh trực tiếp bằng con số được với các nghiên cứu ở Bảng 2.4 vì dữ liệu, loại sự cố và cách đánh giá khác nhau, nhưng so được về cách tiếp cận. Malashin et al. (2024) dùng Isolation Forest và bộ mã hóa tự động trên hóa đơn nhà hàng và phát hiện 25 trên 100 bất thường đã biết; trong khóa luận, Isolation Forest trên 24 chỉ số cũng chỉ phát hiện 2 trên 6 sự cố ở tập kiểm tra. Hai kết quả cùng cho thấy phương pháp không giám sát tổng quát chỉ ra chỗ bất thường nhưng khó chỉ ra nguyên nhân; gắn mỗi nguyên nhân với một dấu vân tay chỉ số trên nhiều nguồn cho phép vừa phát hiện vừa gán nguyên nhân, đổi lại chỉ nhận ra những nguyên nhân đã định nghĩa trước. So với Begen et al. (2023) dùng mô hình phân loại có giám sát trên nhật ký POS, P5 không cần dữ liệu gắn nhãn nên áp dụng được ngay cho doanh nghiệp chưa có lịch sử gian lận được xác minh, nhưng bỏ lỡ gian lận nhẹ như H6; khi đã tích lũy được trường hợp xác minh, hai cách có thể bổ trợ nhau.

Các phương pháp định vị nguyên nhân như Adtributor (Bhagwan et al., 2014) hay HotSpot (Sun et al., 2018) tìm chiều và giá trị gây biến động trên một chỉ số. Cây KPI làm việc tương tự ở bước đầu, nhưng đi thêm một bước là đối chiếu với dữ liệu nhân sự, kho và đối soát; ví dụ CN2 cho thấy bước này là cần thiết, vì phân rã doanh thu chỉ cho biết đơn App giảm, còn dữ liệu chấm công mới cho biết vì sao. Cuối cùng, việc không phát hiện được thất thoát kho với kiểm kê hai tuần phù hợp với nghiên cứu về sai lệch tồn kho: tần suất kiểm kê là yếu tố làm giảm sai lệch (DeHoratius & Raman, 2008), và thất thoát nhỏ chỉ lộ ra khi đã tích lũy (Kang & Gershwin, 2005).

### 5.7.3. Các yếu tố ảnh hưởng đến tính hợp lệ

Về tính hợp lệ nội tại, tham số được chọn trên tập phát triển nên kết quả trên tập này lạc quan, như khoảng cách F1 từ 0,79 xuống 0,52 xác nhận; tập kiểm tra độc lập với hạt giống, chi nhánh, thời điểm và mức độ sự cố khác giảm rủi ro này. Tuy vậy hai tập được sinh bởi cùng một bộ mô phỏng, nên tập kiểm tra kiểm tra được khả năng khái quát sang sự cố mới chứ chưa sang một doanh nghiệp khác; bộ mô phỏng và bộ phát hiện lại được xây dựng trong cùng một nghiên cứu, nên có nguy cơ vô thức thiết kế phương pháp hợp với cách dữ liệu được sinh. Về tính hợp lệ cấu trúc, mỗi kịch bản có một nguyên nhân chính, cường độ ổn định và hầu như không chồng lấn, trong khi ngoài thực tế nhiều vấn đề có thể xảy ra đồng thời và tăng dần. Về tính hợp lệ bên ngoài, dữ liệu mô phỏng một chuỗi giả định; một số quy luật mua hàng đã được hiệu chỉnh từ dữ liệu thật của một tiệm bánh ở Vương quốc Anh, còn các tham số vận hành khác là giả định (mục 3.3.5), nên kết quả định lượng chưa thể khẳng định cho một doanh nghiệp cụ thể. Điều khóa luận chứng minh được là tính khả thi và đúng đắn của phương pháp trong điều kiện có kiểm soát, cùng một đường ống áp dụng được cho dữ liệu thật mà không phải đổi kiến trúc. Về tính hợp lệ thống kê, sáu kịch bản mỗi tập chỉ cho tỷ lệ mang tính chỉ báo, nên kết quả được báo cáo chi tiết từng kịch bản và từng báo động giả.

## 5.8. Tiểu kết chương

Kết quả thực nghiệm trả lời được cả ba câu hỏi nghiên cứu như tóm tắt ở mục 5.7.1: đường ống tích hợp đủ bảy nguồn mà không thất lạc dữ liệu, bộ phát hiện vượt rõ hai phương án cơ sở trên tập kiểm tra độc lập, và nguyên nhân đúng luôn đứng hạng một khi sự cố đã để lại tín hiệu. Điểm yếu tập trung ở sự cố nhẹ, ngắn, ở thất thoát kho khi kiểm kê thưa và ở nhóm hạng C quá nhỏ. Chương 6 tổng kết theo mục tiêu đề tài và đề xuất hướng phát triển.
