# CHƯƠNG 5. THỰC NGHIỆM VÀ ĐÁNH GIÁ

Chương này trả lời ba câu hỏi nghiên cứu đã đặt ra ở mục 1.3. Mục 5.1 mô tả thiết lập thực nghiệm. Mục 5.2 đánh giá đường ống và chất lượng dữ liệu (RQ1). Mục 5.3 đánh giá năm bộ phát hiện (RQ2). Mục 5.4 đánh giá khả năng truy vết nguyên nhân (RQ3). Mục 5.5 phân tích độ nhạy theo ngưỡng và theo cách tính mức kỳ vọng, và so sánh với các phương án cơ sở. Mục 5.6 trình bày các phát hiện kinh doanh rút ra từ kho dữ liệu. Mục 5.7 thảo luận kết quả và các yếu tố ảnh hưởng đến tính hợp lệ; mục 5.8 tóm tắt chương.

## 5.1. Thiết lập thực nghiệm

### 5.1.1. Dữ liệu

Thực nghiệm sử dụng hai tập dữ liệu do bộ mô phỏng sinh ra, đã mô tả ở mục 3.3.7 và kiểm chứng ở Bảng 4.3, Bảng 4.4. Cả hai tập có cùng cấu trúc: 11 chi nhánh, 26 tuần từ 11/03/2024 đến 08/09/2024, bảy nhóm hệ thống nguồn. Chúng khác nhau về hạt giống ngẫu nhiên và về các kịch bản sự cố. Đường ống dữ liệu và các bộ phát hiện được chạy giống hệt nhau trên hai tập, mỗi tập có kho dữ liệu riêng. Bốn tuần đầu của mỗi tập chỉ dùng làm mức nền, nên mỗi tập có 22 tuần đánh giá được, từ tuần 08/04 đến tuần 02/09, tức 242 chi nhánh × tuần.

### 5.1.2. Quy trình đánh giá

Quy trình được thiết kế để kết quả trên tập kiểm tra phản ánh đúng năng lực của hệ thống khi gặp dữ liệu mới:

1. Phát triển phương pháp và chọn mọi tham số, gồm cửa sổ thời gian, ngưỡng và quy tắc gộp bằng chứng, chỉ trên tập phát triển.
2. Chọn ngưỡng điểm cảnh báo theo một quy tắc khai báo trước: quét ngưỡng từ 2,0 đến 5,0, lấy ngưỡng có F1 cao nhất trên tập phát triển, hòa thì lấy ngưỡng thấp hơn. Kết quả là 3,5.
3. Ghi cấu hình cuối cùng vào tệp `analytics/config.py` và lưu phiên bản mã nguồn ở commit `60d28bb` ngày 11/10/2026.
4. Chạy bộ phát hiện với cấu hình đó trên tập kiểm tra một lần duy nhất, không chỉnh sửa gì sau khi xem kết quả.
5. Chương trình `analytics/evaluate.py` đọc danh sách cảnh báo và đáp án, đối chiếu và tính các độ đo. Ngoài bộ mô phỏng, chỉ chương trình này và trang Bộ mô phỏng của ứng dụng được đọc đáp án; bộ phát hiện thì không.

Mọi phân tích lỗi thực hiện sau khi biết đáp án, như ở mục 5.3.3, chỉ để giải thích và không làm thay đổi kết quả đã báo cáo.

### 5.1.3. Quy tắc đối chiếu cảnh báo với sự cố

Đơn vị đánh giá là chi nhánh × tuần. Mỗi sự cố có một chi nhánh và một khoảng thời gian. Cửa sổ của sự cố gồm các tuần giao với khoảng từ ngày bắt đầu đến 14 ngày sau ngày kết thúc, vì một số hậu quả đến muộn: thứ hạng trên sàn giảm sau vài tuần, hao hụt chỉ lộ ra ở lần kiểm kê kế tiếp. Một cảnh báo là cảnh báo đúng nếu cùng chi nhánh và nằm trong cửa sổ của một sự cố; còn lại là báo động giả. Cách đánh giá theo khoảng thời gian này phù hợp với bất thường kéo dài, nơi một sự cố là một khoảng chứ không phải một điểm (Tatbul và cộng sự, 2018). Việc cảnh báo có chỉ đúng nguyên nhân hay không được đánh giá riêng bằng độ đo đúng nguyên nhân ở mục 5.1.4, để tách hai năng lực: phát hiện có vấn đề và chỉ ra đó là vấn đề gì.

### 5.1.4. Độ đo

Sáu độ đo được sử dụng.

- Số sự cố bắt được là số kịch bản có ít nhất một cảnh báo đúng.
- Số sự cố đúng nguyên nhân hạng 1 là số sự cố, trong các sự cố bắt được, mà cảnh báo đầu tiên có nguyên nhân hạng một trùng với nguyên nhân thật.
- Độ trễ phát hiện là số ngày từ khi sự cố bắt đầu đến ngày cuối của tuần có cảnh báo đúng đầu tiên. Vì hệ thống đánh giá theo tuần, độ trễ nhỏ nhất thường là 6 ngày.
- Precision là tỷ lệ chi nhánh × tuần có cảnh báo là cảnh báo đúng, theo công thức (2.11).
- Recall theo tuần là tỷ lệ chi nhánh × tuần đang có sự cố diễn ra mà được cảnh báo.
- F1 là trung bình điều hòa của precision và recall theo tuần.

Do mỗi tập chỉ có sáu kịch bản, các tỷ lệ theo sự cố có độ phân giải thô: mỗi kịch bản tương ứng khoảng 17 điểm phần trăm. Vì vậy kết quả được báo cáo chi tiết theo từng kịch bản, kèm từng báo động giả.

## 5.2. Đánh giá đường ống và chất lượng dữ liệu (RQ1)

### 5.2.1. Phát hiện và xử lý lỗi dữ liệu

Bảng 5.1 so sánh các lỗi dữ liệu mà tầng Silver phát hiện được trên hai tập. Tỷ lệ gần như giống nhau giữa hai tập, phù hợp với việc các lỗi được bộ mô phỏng sinh theo cùng xác suất. Quan trọng hơn, các quy tắc làm sạch được xây dựng trên tập phát triển hoạt động không cần sửa trên tập kiểm tra.

TABLE: Bảng 5.1. Lỗi dữ liệu được phát hiện và xử lý ở tầng Silver || Kết quả thực nghiệm của tác giả
WIDTHS: 4.6,3.2,3.2,3.6
| Loại lỗi | Tập phát triển (183 ngày) | Tập kiểm tra (182 ngày) | Cách xử lý |
| Lượt quẹt thẻ trùng | 1.290 (3,03%) | 1.285 (3,03%) | Cách ly |
| Ca thiếu lượt ra | 1.036 ca (4,89%) | 1.023 ca (4,85%) | Gắn cờ; Gold nội suy số giờ, có cờ |
| Nghi gõ gam vào cột kg | 62 dòng (0,38%) | 63 dòng (0,40%) | Cách ly |
| Dòng tổng cộng, chữ ký trong sổ kho | 2.486 | 2.474 | Tách thành dòng cấu trúc |
| Tên nguyên liệu khớp chính xác | 13.576 dòng (84,3%) | 13.336 dòng (84,5%) | Ánh xạ trực tiếp |
| Tên nguyên liệu qua bảng biến thể | 2.528 dòng (15,7%) | 2.453 dòng (15,5%) | Ánh xạ; khớp mờ không phải dùng, không dòng nào cách ly |
| Ô kiểm kê trống | 77 (2,4%) | 76 (2,4%) | Giữ giá trị thiếu, gắn cờ |
| Hóa đơn POS phiên bản cũ | 59.979 | 59.131 | Chuẩn hóa về lược đồ chung |
| Hóa đơn hủy / hoàn tiền | 1.896 / 2.278 | 1.669 / 2.050 | Giữ lại, gắn cờ, tính phút đến lúc hủy |
| Đơn App lưu giờ UTC | 97.207 | 85.931 | Đổi sang giờ Việt Nam rồi xác định ngày, ca |
| Số lượng dính đơn vị (sổ mẫu B) | 4.536 | 4.470 | Tách số và đơn vị, chuẩn hóa đơn vị |

Các lỗi kỹ thuật như quẹt trùng, gõ nhầm đơn vị được tách khỏi dữ liệu, còn các tín hiệu nghiệp vụ như hóa đơn hủy, quên quẹt ra, ô kiểm kê trống được giữ lại kèm cờ, đúng nguyên tắc ở mục 2.4.2. Cần ghi nhận một hạn chế là tầng khớp mờ tên nguyên liệu chưa được kiểm chứng trên dữ liệu thật, vì mọi biến thể tên do bộ mô phỏng tạo ra đều nằm trong bảng biến thể.

### 5.2.2. Đối soát giữa các tầng

Đối soát số dòng giữa Bronze và Silver ở Bảng 4.9 cho phần không giải thích được bằng 0 ở cả bảy nguồn trên cả hai tập. Doanh thu thuần ở Gold khớp tuyệt đối với tổng tính từ Silver theo từng chi nhánh × ngày, với 37.899.868.200 đồng ở tập phát triển, kể cả ngày thêm khi kiểm chứng nạp tăng dần, và 33.302.131.300 đồng ở tập kiểm tra. Ở bước đưa sang kho phục vụ, số dòng của cả 22 bảng được so giữa DuckDB và PostgreSQL trước khi đổi lược đồ; mọi lượt chạy trong nhật ký đều khớp.

TABLE: Bảng 5.2. Kết quả kiểm thử và kiểm tra chất lượng || Kết quả thực nghiệm của tác giả
WIDTHS: 6,2.6,2.6,2.6
| Nội dung | Tập phát triển | Tập kiểm tra | Môi trường vận hành |
| Kiểm thử dbt đạt | 158/158 | 158/158 | 158/158 |
| Bước dbt thành công (mô hình, hạt giống, kiểm thử) | 211/211 | 211/211 | 211/211 |
| Nguồn có phần chênh lệch số dòng không giải thích được | 0/7 | 0/7 | 0/7 |
| Mục cửa chặn chất lượng đạt mỗi lượt | — | — | 15/15 ở các lượt dữ liệu bình thường; lượt có dữ liệu bất thường xem mục 5.2.4 |

### 5.2.3. Hiệu năng

TABLE: Bảng 5.3. Thời gian chạy của từng bước || Kết quả thực nghiệm của tác giả
WIDTHS: 4,4.4,4.4
| Bước | Dựng toàn bộ một tập (182 ngày, trên máy) | Một ngày mới (trong Docker, qua Airflow) |
| Sinh dữ liệu nguồn | khoảng 3,5 phút | khoảng 2 giây |
| Kéo qua API (POS đám mây, App) | — | 0,8 giây, 1.343 hóa đơn và 419 đơn |
| Kiểm tra tệp mới | — | 23,9 giây |
| Nạp Bronze | 80 giây, 6.273 tệp | 20,2 giây, 35 tệp |
| Cửa chặn chất lượng | — | 5,6 giây |
| dbt build (211 bước) | 15–25 giây | 17,4 giây |
| Bộ phát hiện | khoảng 1 giây | 2,0 giây |
| Đưa sang kho phục vụ | khoảng 38 giây (lần đầu) | 8,9 giây |

Thời gian xử lý một ngày mới khoảng 80 giây cho bảy bước, đáp ứng yêu cầu NFR7 là xử lý một ngày trong vài phút trên một máy tính cá nhân. Phần chậm do thư mục gắn vào Docker đã được phân tích ở mục 4.10.3.

### 5.2.4. Độ bền trước dữ liệu bất thường và sự cố nguồn

Để kiểm tra yêu cầu NFR8, chương trình `tools/thu_tinh_huong.py` dựng một "ngày xấu" trên môi trường vận hành: hệ thống nguồn ghi bảy ngày 23–29/09/2024, 11 tình huống dữ liệu bất thường được cài cùng lúc, rồi đường ống chạy hai lượt không có thao tác tay nào ở giữa, lượt đầu khi API của POS đám mây và App không phản hồi, lượt sau khi API hoạt động lại. Kết quả được đo từ nhật ký nạp, bảng cách ly, cửa chặn chất lượng và bộ phát hiện trong lần chạy ngày 17/10/2026; kết quả từng tình huống ở Bảng G.1 của Phụ lục G.

Cả 11 tình huống cho đúng kết quả mong đợi đã ghi trước khi chạy; không tệp nào bị bỏ qua im lặng. Với sự cố API, lượt thứ nhất kết thúc sau 105 giây: bộ kết nối thử sáu lần rồi ghi cảnh báo, các nguồn tệp vẫn được nạp (174 tệp), nhưng cửa chặn chất lượng dừng đường ống trước Silver vì hai mục ở mức chặn: dữ liệu App chậm 7 ngày, và mỗi ngày từ 8 đến 10 trong 11 chi nhánh thiếu POS. Tầng Gold và kho phục vụ giữ nguyên dữ liệu đến 22/09, nên không có cảnh báo hay báo cáo nào được tạo từ dữ liệu thiếu. Lượt thứ hai, khi API hoạt động lại, tự lấy đủ bảy ngày (10.365 hóa đơn, 3.880 đơn App, 7 lần thử lại do lỗi tạm thời của API), chạy hết đường ống trong 66 giây và đưa ra đúng hai cảnh báo của hai sự cố đã cài: CN1 hoa hồng sàn sai hợp đồng (điểm 6,0) và CN3 thiếu nhân sự (điểm 4,8). Cửa chặn của lượt này còn ba cảnh báo, đều đúng với các tình huống đã cài: chi nhánh thiếu tệp, tệp lỗi và trường mới.

Hai quy tắc không kết luận trên dữ liệu thiếu của bộ phát hiện (mục 3.7.3) được bổ sung sau khi đã chốt đánh giá ở mục 5.3, nên cần nói rõ nguồn gốc. Quy tắc thứ nhất, áp dụng theo từng chi nhánh, xuất phát từ thử nghiệm tệp xấu: một tệp POS rỗng từng làm bộ phát hiện báo P1b sai cho chi nhánh đó. Quy tắc thứ hai xuất phát từ một lỗi thật của bộ kết nối ở lần chạy đầu, đã nêu ở mục 4.3.2. Lỗi này làm tám chi nhánh thiếu POS sáu ngày, tạo ra một phép thử thiếu dữ liệu hàng loạt ngoài dự kiến. Kết quả của lượt đó:
- Phần đã đúng: tám chi nhánh thiếu dữ liệu được hạ đúng xuống mức theo dõi, cảnh báo CN1 hoa hồng sai hợp đồng vẫn giữ.
- Phần sai: ba chi nhánh đủ dữ liệu (CN5, CN7, CN10) bị cảnh báo "chưa xác định nguyên nhân", vì trung vị của nhóm cùng hạng sụt theo các chi nhánh thiếu dữ liệu.

Sau khi thêm quy tắc thứ hai và mức chặn của cửa chặn chất lượng, cùng dữ liệu đó chỉ còn cảnh báo CN1. Cả hai quy tắc chỉ có tác dụng khi dữ liệu thiếu. Trên hai tập đánh giá, không chi nhánh × tuần nào chịu tác động của chúng, và mã băm của bảng điểm và bảng cảnh báo trùng khớp trước và sau khi bổ sung quy tắc thứ hai. Vì vậy mọi kết quả ở mục 5.3 không thay đổi.

Thử nghiệm có hai giới hạn. Thứ nhất, các tình huống do tác giả thiết kế dựa trên các lỗi thường gặp, chưa bao quát hết lỗi của hệ thống thật. Thứ hai, API là dịch vụ giả lập. Xác thực, phân trang, giới hạn tần suất và lỗi tạm thời được mô phỏng theo cách các API bán hàng thường làm, nhưng API thật của từng nhà cung cấp có thể khác, chẳng hạn xác thực OAuth, lấy theo thời điểm cập nhật thay vì theo ngày, hoặc thông báo đẩy.

## 5.3. Đánh giá các bộ phát hiện (RQ2)

### 5.3.1. Kết quả tổng hợp

TABLE: Bảng 5.4. Kết quả của phương pháp đề xuất trên hai tập (ngưỡng điểm 3,5) || Kết quả thực nghiệm của tác giả
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

Trên tập kiểm tra, hệ thống bắt được bốn trên sáu sự cố; ba sự cố được chỉ đúng nguyên nhân ngay ở cảnh báo đầu tiên, sau đúng một tuần. F1 giảm từ 0,79 xuống 0,52 khi chuyển sang tập kiểm tra. Khoảng cách này cho thấy phương pháp có phần khớp với tập phát triển, và đó là lý do phải tách tập kiểm tra: nếu chỉ báo cáo trên tập phát triển, kết quả sẽ lạc quan hơn thực tế đáng kể.

Hình 5.1 đặt từng cảnh báo cạnh vùng thời gian của các sự cố. Ở cả hai tập, cảnh báo đúng tập trung trong vùng sự cố đang diễn ra; báo động giả nằm rải rác ở các chi nhánh hạng C và ở CN10, CN6; hai sự cố bị bỏ sót trên tập kiểm tra là H4 và H5, thể hiện bằng hai dải không có điểm nào.

IMAGE: figures/c5_ban_do.png || Hình 5.1. Cảnh báo của bộ phát hiện đặt cạnh thời gian các sự cố, theo chi nhánh × tuần (ngưỡng điểm 3,5) || 16 || Kết quả thực nghiệm của tác giả

### 5.3.2. Kết quả theo từng bộ phát hiện

TABLE: Bảng 5.5. Kết quả theo từng loại sự cố || Kết quả thực nghiệm của tác giả
WIDTHS: 3.2,2.2,1.9,1.4,2.2,1.9,1.4
| Bộ phát hiện | Phát triển: sự cố | Phát triển: cảnh báo đúng / tổng | Phát triển: trễ (ngày) | Kiểm tra: sự cố | Kiểm tra: cảnh báo đúng / tổng | Kiểm tra: trễ (ngày) |
| P1a. Hoa hồng sai hợp đồng | S1 bắt được | 3/3 | 6 | H1 bắt được | 2/2 | 6 |
| P1b. Đơn sàn không vào POS | S2 bắt được | 2/3 | 6 | H2 bắt được | 2/2 | 6 |
| P2. Hao hụt vượt định mức | S3 bắt được | 2/4 | 4 | H3 bắt được | 2/4 | 6 |
| P3. Thiếu nhân sự | S4 bắt được | 2/2 | 6 | H4 bỏ sót | 0/0 | — |
| P4. Thất thoát kho | S5 bỏ sót | 0/0 | — | H5 bỏ sót | 0/0 | — |
| P5. Gian lận tại quầy | S6 bắt được | 4/4 | 6 | H6 bắt được, sai nhãn | 0/1 | 27 |
| Chưa xác định nguyên nhân | — | 0/2 | — | — | 1/5 | — |

Cột "cảnh báo đúng / tổng" tính theo nguyên nhân mà hệ thống gán cho cảnh báo. Hai bộ phát hiện đối soát sàn P1a và P1b hoạt động ổn định nhất: bắt cả bốn sự cố sau một tuần, không có báo động giả trên tập kiểm tra. Điều này phù hợp với bản chất bài toán, vì đối soát dựa trên các con số so được trực tiếp giữa hai nguồn như tỷ lệ hợp đồng, số đơn sàn báo so với số đơn trên POS, nên ít phụ thuộc vào mô hình kỳ vọng. P2 bắt cả hai sự cố hao hụt nhưng cũng sinh báo động giả ở cả hai tập, tại CN10 trên tập phát triển và CN6 trên tập kiểm tra. P3, P4 và P5 là các bài toán khó hơn, được phân tích ở mục 5.3.3.

Hình 5.2 cho thấy vì sao bốn bộ phát hiện bắt được sự cố trên tập phát triển: ở mỗi bộ, tín hiệu của chi nhánh hoặc thu ngân có sự cố tách hẳn khỏi dải của các đối tượng còn lại đúng trong thời gian sự cố. Tín hiệu hao hụt ở hình (c) lộ ra ở lần kiểm kê ngay sau sự cố, đúng như thiết kế đánh giá theo kỳ kiểm kê.

IMAGE: figures/c5_tin_hieu.png || Hình 5.2. Tín hiệu của bốn bộ phát hiện quanh sự cố trên tập phát triển || 16 || Kết quả thực nghiệm của tác giả

### 5.3.3. Phân tích lỗi

Phần này thực hiện sau khi biết đáp án, chỉ để giải thích kết quả.

TABLE: Bảng 5.6. Các sự cố bị bỏ sót hoặc gán sai nguyên nhân || Kết quả thực nghiệm của tác giả
WIDTHS: 2.6,2,1.4,8
| Sự cố | Điểm cao nhất của nguyên nhân đúng | Hạng | Giải thích |
| S5 thất thoát kho CN9 | 2,8 | 1 | Ở mức theo dõi, dưới ngưỡng 3,5. Tồn kho mỗi nguyên liệu chỉ đủ 2–4 ngày, nên mất 1,5% lượng tồn mỗi ngày chỉ làm hao hụt nhóm giá trị cao tăng 1–2 điểm % |
| H4 thiếu nhân sự CN8 | 2,82 | 1 | Số ca bếp tối giảm rõ (z = −5,6) nhưng sự cố chỉ 10 ngày, hậu quả vừa phải; điểm P3 là trung bình của năm tín hiệu nên bị các tín hiệu yếu kéo xuống |
| H5 thất thoát kho CN5 | gần 0 | — | Không có tín hiệu: chi nhánh nhỏ, mất 1,2% lượng tồn mỗi ngày, kiểm kê hai tuần một lần |
| H6 gian lận thu ngân CN10 | 3,44 | 1 | Thiếu ngưỡng 0,06. Mức gian lận nhẹ hơn S6 (5–8 so với 14–20 hóa đơn mỗi tuần). Hệ thống chỉ cảnh báo ở tuần thứ tư, khi doanh thu lệch kỳ vọng đủ lớn, với nhãn "chưa xác định nguyên nhân" |

Ở cả năm sự cố có tín hiệu trên tập kiểm tra (H1, H2, H3, H4, H6), nguyên nhân đúng đều được xếp hạng một trong cửa sổ sự cố, kể cả hai trường hợp chưa vượt ngưỡng. Điểm yếu chính vì vậy nằm ở ngưỡng phát cảnh báo và độ nhạy với sự cố nhẹ, ngắn, chứ không nằm ở khả năng chỉ đúng nguyên nhân khi đã có tín hiệu. Thất thoát kho (P4) là loại khó nhất: với kiểm kê hai tuần một lần và tồn kho chỉ vài ngày, lượng mất nhỏ chìm trong sai số đếm. Đây là giới hạn của dữ liệu đầu vào, không chỉ của phương pháp.

Bảy báo động giả trên tập kiểm tra gồm ba nhóm. Bốn tuần ở các chi nhánh hạng C (CN4, CN5, CN11) có doanh thu lệch kỳ vọng mà không nguyên nhân nào đủ điểm; nhóm cùng hạng chỉ có ba chi nhánh nên trung vị nhóm dao động mạnh. Hai tuần P2 ở CN6 trong tháng 5 có hao hụt hàng tươi cao hơn các chi nhánh khác cùng kỳ. Một tuần P5 ở CN2, tuần 02/09, có một thu ngân hủy hóa đơn nhiều hơn đồng nghiệp. Ở tập phát triển, năm báo động giả gồm hai tuần doanh thu lệch không rõ nguyên nhân, hai tuần P2 và một tuần P1b ở CN10. Các báo động giả này đều có thiệt hại ước tính nhỏ: báo động P2 ở CN10 chỉ 66 nghìn đồng và ở CN6 chỉ 29 nghìn đồng, so với 6,83 triệu đồng của sự cố hao hụt thật ở CN7. Khi danh sách được sắp theo thiệt hại, báo động giả nằm cuối danh sách, nên chi phí xử lý chúng thấp.

## 5.4. Đánh giá khả năng truy vết nguyên nhân (RQ3)

### 5.4.1. Ví dụ truy vết: thiếu nhân sự ở CN2

Sự cố S4 của tập phát triển làm CN2 thiếu nhân viên bếp ca tối từ 06/05 đến 19/05. Bảng 5.7 trình bày cây KPI và các tín hiệu vận hành của CN2 trong tuần đầu sự cố, đúng như trang Truy vết ở Hình 4.6 hiển thị.

TABLE: Bảng 5.7. Truy vết CN2, tuần 06/05–12/05/2024 (tập phát triển) || Kết quả thực nghiệm của tác giả
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

Cây KPI cho thấy chênh lệch nằm chủ yếu ở số đơn, không ở giá trị đơn, và nặng nhất ở kênh App, kênh mà cửa hàng tự hủy đơn khi quá tải. Các tín hiệu vận hành cùng chỉ về một hướng: số ca bếp tối giảm một nửa, thời gian chuẩn bị tăng gần 50%, cửa hàng tự hủy đơn App tăng gấp năm. Bộ phát hiện xếp P3 ở hạng một với điểm 4,3. Nếu chỉ nhìn doanh thu thì tuần này chưa đủ để cảnh báo, vì z = −2,8 còn dưới ngưỡng 3; chính các tín hiệu vận hành đã đẩy tuần này lên mức cảnh báo.

Hậu quả kéo dài sau sự cố cũng được ghi nhận. Ở tuần 20/05, khi nhân sự đã trở lại bình thường với 26 ca bếp tối và thời gian chuẩn bị 13,3 phút, doanh thu GrabFood của CN2 vẫn thấp hơn kỳ vọng 22,1% với số đơn thấp hơn 18,8% và điểm đánh giá 4,3 so với 4,5. Hệ thống xếp tuần này ở mức theo dõi. Đây đúng là chuỗi nhân quả trễ qua thứ hạng sàn đã mô tả ở mục 3.3.4: tín hiệu nhân sự đã hết nhưng doanh thu sàn vẫn chịu ảnh hưởng, như Hình 5.3 cho thấy.

IMAGE: figures/c5_truy_vet_cn2.png || Hình 5.3. Doanh thu thuần và số ca bếp tối của CN2 so với mức kỳ vọng; vùng tô là thời gian sự cố S4 || 16 || Kết quả thực nghiệm của tác giả

### 5.4.2. Khả năng chỉ đúng nguyên nhân

Trên tập phát triển, cả năm sự cố bắt được đều được chỉ đúng nguyên nhân ngay ở cảnh báo đầu tiên. Trên tập kiểm tra, ba trên bốn sự cố bắt được có nguyên nhân đúng; sự cố còn lại là H6, được cảnh báo với nhãn "chưa xác định nguyên nhân" chứ không bị gán nhầm sang một nguyên nhân khác. Trong toàn bộ 32 cảnh báo của hai tập, không có cảnh báo nào nằm trong cửa sổ một sự cố mà lại chỉ sai sang một nguyên nhân vận hành khác.

### 5.4.3. Phân biệt với biến động bình thường

Bảng 5.8 xét các tuần có biến động chung lớn trên toàn chuỗi: tuần có ngày lễ, tuần điều chỉnh giá và tuần mưa nhiều nhất.

TABLE: Bảng 5.8. Cảnh báo trong các tuần có biến động bình thường lớn || Kết quả thực nghiệm của tác giả
WIDTHS: 4.8,3.2,2.3,4.4
| Tuần (tập) | Biến động chung | Doanh thu chuỗi so với tuần trước | Cảnh báo trong tuần |
| 29/04 (phát triển), lễ 30/4–1/5 | Hai ngày lễ | +10,0% | 0 |
| 02/09 (phát triển), lễ 2/9 | Hai ngày lễ | +7,6% | 0 |
| 15/04 (phát triển), Giỗ Tổ | Một ngày lễ | +7,0% | 2, đều thuộc kho (CN7 sự cố thật; CN10 báo động giả P2) |
| 03/06 (phát triển), sau điều chỉnh giá 1/6, 6 ngày mưa | AOV +3,3%, mưa nhiều nhất | +2,7% | 0 |
| 29/04 (kiểm tra), lễ 30/4–1/5 | Hai ngày lễ | +7,9% | 1, sự cố thật H2 |
| 02/09 (kiểm tra), lễ 2/9 | Hai ngày lễ | +5,5% | 1, báo động giả P5 ở một thu ngân |

Trong các tuần này, không cảnh báo nào được gán cho biến động doanh thu chung; các cảnh báo xuất hiện đều đến từ bằng chứng riêng của chi nhánh về kho, thu ngân hoặc đối soát sàn. Lý do là mức kỳ vọng được tính theo nhóm chi nhánh cùng hạng trong cùng tuần, nên tác động của lễ, mưa và điều chỉnh giá lên cả nhóm tự triệt tiêu. Để so sánh, doanh thu ngày lễ cao hơn ngày thường khoảng 21–23% theo Bảng 4.5, lớn hơn tác động doanh thu của phần lớn các sự cố.

Điểm yếu của cách tính kỳ vọng theo nhóm cùng hạng lộ ra ở hạng C: nhóm chỉ có ba chi nhánh, mỗi chi nhánh so với trung vị của hai chi nhánh còn lại, nên một biến động riêng của một chi nhánh trong nhóm cũng làm lệch kỳ vọng của các chi nhánh khác. Bốn trong bảy báo động giả trên tập kiểm tra rơi vào hạng C.

## 5.5. Phân tích độ nhạy và so sánh với phương án cơ sở

### 5.5.1. Độ nhạy theo ngưỡng điểm cảnh báo

Ngưỡng điểm điều chỉnh sự đánh đổi giữa bỏ sót và báo động giả, như Hình 5.4. Ở ngưỡng 2,0 hệ thống bắt cả sáu sự cố nhưng có 26 báo động giả; ở ngưỡng 2,5 vẫn bắt đủ sáu sự cố với 15 báo động giả, bằng số cảnh báo đúng. Ngưỡng 3,5 cho F1 cao nhất là 0,79, với precision 0,72, recall theo tuần 0,87 và 5 báo động giả, nên được chốt; từ 4,0 trở lên recall giảm nhanh vì bắt thêm ít sự cố hơn. Ở mọi ngưỡng, khi đã bắt được, nguyên nhân hạng một đều đúng. Trên thực tế, ngưỡng này nên do người quản lý chọn theo khả năng xử lý cảnh báo của bộ phận mình; vì vậy ứng dụng cho phép thay đổi ngưỡng trên trang Trung tâm cảnh báo, còn kết quả chính thức luôn được báo cáo ở ngưỡng đã chốt.

IMAGE: figures/c5_nguong.png || Hình 5.4. Precision, recall theo tuần và F1 trên tập phát triển theo ngưỡng điểm cảnh báo; hai dòng phía trên là số sự cố bắt được và số báo động giả || 16 || Kết quả thực nghiệm của tác giả

### 5.5.2. So sánh với phương án cơ sở

Hai phương án cơ sở được chạy trên cùng dữ liệu Gold. Phương án thứ nhất chỉ theo dõi doanh thu: cảnh báo khi |z| doanh thu thuần từ 3, tức cách làm phổ biến khi chỉ có báo cáo doanh thu. Phương án thứ hai là Isolation Forest (Liu và cộng sự, 2008), cài đặt bằng thư viện scikit-learn (Pedregosa và cộng sự, 2011), một phương pháp phát hiện bất thường không giám sát, chạy trên vector z của cả 24 chỉ số giám sát và được phép đưa ra đúng số cảnh báo như phương pháp đề xuất, để so sánh công bằng.

TABLE: Bảng 5.9. So sánh với các phương án cơ sở || Kết quả thực nghiệm của tác giả
WIDTHS: 4.4,1.6,1.6,1.6,1.6,1.6,1.6
| Phương pháp | Phát triển: sự cố | Phát triển: precision | Phát triển: F1 | Kiểm tra: sự cố | Kiểm tra: precision | Kiểm tra: F1 |
| Đề xuất: bộ chỉ số giám sát và dấu vân tay nguyên nhân | 5/6 | 0,72 | 0,79 | 4/6 | 0,50 | 0,52 |
| Chỉ theo dõi doanh thu, lệch từ 3 đơn vị z | 0/6 | 0 | 0 | 1/6 | 0,20 | 0,11 |
| Isolation Forest, cùng số cảnh báo | 3/6 | 0,22 | 0,24 | 2/6 | 0,14 | 0,15 |

Theo dõi doanh thu gần như không phát hiện được sự cố nào. Lý do là phần lớn sự cố không làm doanh thu lệch đủ xa: hoa hồng sai hợp đồng và hao hụt làm tăng chi phí chứ không làm giảm doanh thu; gian lận tại quầy chỉ vài triệu đồng mỗi tuần; ngay cả sự cố thiếu nhân sự S4 cũng chỉ làm doanh thu lệch z = −2,8. Đây là bằng chứng định lượng cho nhận định ở mục 1.1: nhìn con số tổng hợp không đủ để phát hiện sự cố vận hành. Isolation Forest dùng đúng các chỉ số như phương pháp đề xuất nhưng chỉ tìm điểm "lạ" chung chung, không biết chiều nào là xấu và chỉ số nào đi cùng nhau, nên phần lớn cảnh báo rơi vào các tuần lạ mà vô hại; phương pháp này cũng không cho biết nguyên nhân. Phương pháp đề xuất vượt cả hai phương án cơ sở trên cả hai tập.

### 5.5.3. Độ nhạy theo cách tính mức kỳ vọng

Mục này kiểm tra từng lựa chọn trong cách tính mức kỳ vọng ở mục 3.7.2. Mỗi lần chỉ thay một lựa chọn, giữ nguyên mọi phần khác và ngưỡng điểm 3,5, rồi chấm lại trên tập phát triển. Chương trình `analytics/sensitivity.py` tính lại bảng mức kỳ vọng bằng Python; trước khi thay đổi bất cứ gì, bản tính lại được đối chiếu với bảng do dbt sinh ra và khớp tuyệt đối trên 8.954 dòng. Tập kiểm tra không được dùng, vì nó đã được đánh giá một lần với cấu hình đã chốt.

TABLE: Bảng 5.10. Độ nhạy theo cách tính mức kỳ vọng (tập phát triển, ngưỡng điểm 3,5) || Kết quả thực nghiệm của tác giả
WIDTHS: 4.4,1.3,1.3,1.4,1.8,2.3,1.5,1.1
| Phương án | Sự cố bắt được | Số cảnh báo | Báo động giả | Trong đó do lệch doanh thu, nhân sự | Precision | Recall tuần | F1 |
| Đề xuất: nhóm cùng hạng, trung vị và MAD 8 tuần, có sàn độ dao động | 5/6 | 18 | 5 | 2 | 0,72 | 0,87 | 0,79 |
| So với toàn chuỗi thay vì nhóm cùng hạng | 5/6 | 20 | 7 | 4 | 0,65 | 0,87 | 0,74 |
| Không so nhóm, chỉ lịch sử của chính chi nhánh | 5/6 | 20 | 7 | 4 | 0,65 | 0,87 | 0,74 |
| Cửa sổ mức nền 4 tuần | 5/6 | 27 | 15 | 12 | 0,44 | 0,80 | 0,57 |
| Cửa sổ mức nền 12 tuần | 5/6 | 17 | 4 | 1 | 0,76 | 0,87 | 0,81 |
| Trung bình và độ lệch chuẩn thay trung vị và MAD | 5/6 | 17 | 5 | 2 | 0,71 | 0,80 | 0,75 |
| Bỏ sàn độ dao động | 5/6 | 26 | 13 | 10 | 0,50 | 0,87 | 0,63 |

Cột "trong đó do lệch doanh thu, nhân sự" đếm các báo động giả có nguyên nhân "chưa xác định" hoặc P3, tức loại chịu ảnh hưởng của mức kỳ vọng. Ba báo động giả còn lại của mọi phương án, gồm hai tuần P2 và một tuần P1b ở CN10, đến từ bằng chứng kho và đối soát, không phụ thuộc vào cách tính này. Bốn nhận xét rút ra:

- Sàn độ dao động và độ dài cửa sổ là hai lựa chọn ảnh hưởng lớn nhất. Bỏ sàn làm báo động giả tăng từ 5 lên 13, vì có những chi nhánh mà tám tuần trước tình cờ rất đều, làm z bị thổi phồng. Cửa sổ 4 tuần làm báo động giả tăng lên 15, đồng thời sự cố S4 chỉ còn được cảnh báo một tuần: tuần sự cố đầu tiên đã chiếm một phần tư mức nền của tuần thứ hai.
- Trung bình và độ lệch chuẩn cho cùng số báo động giả nhưng bỏ sót tuần thứ hai của S4, vì tuần sự cố đầu tiên làm độ lệch chuẩn phình ra. Đây đúng là lý do chọn trung vị và MAD đã nêu ở mục 3.7.2.
- So với toàn chuỗi, hoặc không so nhóm, đều thêm hai báo động giả. Khi chỉ dùng lịch sử của chính chi nhánh, hai trong bốn báo động giả liên quan rơi vào các tuần lễ 29/4 và 2/9 ở CN1, và tuần 29/4 còn bị gán nhầm là thiếu nhân sự. So với nhóm cùng hạng loại bỏ được đúng loại lỗi này. Mức chênh trên dữ liệu này không lớn, F1 là 0,79 so với 0,74, vì phần lớn sự cố được phát hiện bằng bằng chứng riêng về đối soát, kho hay thu ngân chứ không qua độ lệch doanh thu.
- Cửa sổ 12 tuần cho kết quả tốt hơn nhẹ cửa sổ 8 tuần đang dùng: ít hơn một báo động giả, F1 0,81. Khi phát triển, cửa sổ 8 tuần được chọn khi so với 4 tuần; cửa sổ dài hơn chưa được thử trước khi chốt. Khóa luận không đổi cấu hình, vì kết quả trên tập kiểm tra chỉ có giá trị với cấu hình đã chốt trước khi xem nó. Chênh lệch chỉ là một cảnh báo trên chính tập đã dùng để phát triển, và cửa sổ dài phản ứng chậm hơn với các thay đổi bền vững như đổi cơ cấu kênh hay khai trương chi nhánh mới. Thử cửa sổ dài hơn trên một tập kiểm tra mới được ghi vào hướng phát triển.

Cuối cùng, lập luận ở mục 3.7.3 về việc dùng luật thay vì điểm z cho P1a cũng được kiểm tra. Chuỗi chênh lệch hoa hồng GrabFood của CN4 được sửa theo giả định rằng sàn tính thừa 5 điểm % từ tuần 13/5 đến hết kỳ, tức 17 tuần, thay vì ba tuần. Luật đối soát cảnh báo cả 17 tuần. Điểm z tính theo đúng cách hiện tại chỉ vượt 3 ở bốn tuần đầu; ở tuần thứ năm z còn 0,67, và từ tuần thứ sáu bằng 0, vì mức nền trung vị tám tuần đã gồm phần lớn các tuần bị tính sai. Như vậy, với phương pháp thống kê dựa trên lịch sử, một sai lệch kéo dài dần trở thành "bình thường"; với bài toán tuân thủ hợp đồng, luật so trực tiếp với tỷ lệ cam kết mới là công cụ đúng, như Hình 5.5 minh họa.

IMAGE: figures/c5_luat_z.png || Hình 5.5. Điểm bằng chứng P1a theo luật đối soát và theo điểm z khi sai lệch hoa hồng kéo dài 17 tuần (giả định trên dữ liệu CN4) || 16 || Kết quả thực nghiệm của tác giả

## 5.6. Các phát hiện kinh doanh

Các số liệu trong mục này được tính hoàn toàn từ kho dữ liệu 182 ngày của tập phát triển, không lấy từ đáp án của bộ mô phỏng. Vì dữ liệu là mô phỏng, các phát hiện minh họa loại câu hỏi mà nền tảng trả lời được, không phải kết luận về một doanh nghiệp thật.

### 5.6.1. Cơ cấu chi phí theo hạng chi nhánh

IMAGE: figures/c5_nhan_cong.png || Hình 5.6. Labor% và số đơn mỗi giờ công của từng chi nhánh × tuần, theo hạng chi nhánh (tập phát triển) || 16 || Kết quả thực nghiệm của tác giả

Doanh thu bình quân mỗi chi nhánh mỗi tuần là 261,2 triệu đồng ở ba chi nhánh hạng A, 113,1 triệu ở năm chi nhánh hạng B và 33,8 triệu ở ba chi nhánh hạng C. COGS% định mức như nhau ở cả ba hạng, đều 31,0%, nhưng Labor% của hạng C là 29,1%, cao gấp khoảng 3,4 lần mức 8,6% của hạng A; hạng B ở giữa với 12,4%. Đây là phát hiện về cấu trúc chứ không phải sự cố. Một chi nhánh phải có số người tối thiểu cho mỗi ca dù lượng đơn ít, nên năng suất ở hạng C chỉ 1,04 đơn mỗi giờ công so với 3,44 ở hạng A, kéo theo tỷ lệ chi phí nhân công chênh lệch lớn; Hình 5.6 cho thấy ba hạng tạo thành ba cụm tách biệt trên cùng một đường cong. Hệ quả cho việc giám sát là không thể dùng một ngưỡng Labor% chung cho mọi chi nhánh; so sánh phải theo nhóm cùng hạng, như cách hệ thống đang làm. Cần lưu ý Labor% ở đây chỉ gồm lương giờ trực tiếp theo chấm công, chưa gồm lương cố định của quản lý và bảo hiểm, nên thấp hơn mức thường được nêu trong thực tiễn. COGS% định mức giống nhau giữa các chi nhánh vì cùng công thức và cùng cơ cấu món; khác biệt về giá vốn thực tế chỉ lộ ra qua hao hụt so với định mức mà P2 và P4 theo dõi.

### 5.6.2. Hiệu quả theo kênh sau phí sàn

Tại quầy chiếm 52% doanh thu thuần, ứng dụng riêng 22%, GrabFood 16%, ShopeeFood 10%. Theo báo cáo đối soát, tổng phí mà sàn giữ lại, gồm hoa hồng, quảng cáo và khuyến mãi do cửa hàng tài trợ, bằng 27,7% doanh thu món trên GrabFood và 24,7% trên ShopeeFood. Cộng với giá vốn định mức khoảng 31%, mỗi 100 đồng bán qua GrabFood chỉ còn khoảng 41 đồng trước chi phí nhân công và mặt bằng, so với khoảng 69 đồng khi bán tại quầy. Kênh sàn mang lại lượng đơn bổ sung nhưng có biên đóng góp thấp hơn rõ rệt; điều này giải thích vì sao một sai lệch nhỏ của tỷ lệ hoa hồng như P1a đáng được kiểm soát hằng tuần.

### 5.6.3. Ma trận thực đơn

Áp dụng phương pháp menu engineering (Kasavana & Smith, 1982), mỗi món được xếp theo hai trục. Trục thứ nhất là mức phổ biến, so tỷ trọng số lượng bán với 70% mức bình quân 1/28; trục thứ hai là lãi gộp mỗi phần, so với bình quân có trọng số là 29.357 đồng.

IMAGE: figures/c5_thuc_don.png || Hình 5.7. Ma trận thực đơn: tỷ trọng số lượng bán và lãi gộp mỗi phần của 28 món (tập phát triển) || 16 || Kết quả thực nghiệm của tác giả

Nhóm ngôi sao, tức món phổ biến và lãi cao, có 5 món, chiếm 23,2% số lượng và 35,6% lãi gộp, tiêu biểu là gà giòn combo 2 miếng và burger gà giòn phô mai. Nhóm ngựa kéo, phổ biến nhưng lãi thấp, có 5 món, chiếm 51,2% số lượng nhưng chỉ 33,3% lãi gộp; nhóm này gồm gà giòn miếng đơn với 23,3% số lượng, Pepsi lon, khoai tây chiên L. Nhóm câu đố, ít bán nhưng lãi cao, có 9 món với 13,3% số lượng và 25,5% lãi gộp, nổi bật là combo gia đình 4 người lãi 182.920 đồng mỗi phần. Nhóm chó, ít bán và lãi thấp, có 9 món với 12,4% số lượng và 5,7% lãi gộp, như trà sữa trân châu, nước suối, súp ngô và các món salad.

Món bán chạy nhất, gà giòn miếng đơn, chiếm gần một phần tư số lượng nhưng lãi mỗi phần thấp hơn bình quân. Theo lý thuyết menu engineering, hành động gợi ý là đẩy khách từ miếng đơn sang các combo thuộc nhóm ngôi sao bằng gợi ý bán kèm tại quầy và trên ứng dụng; quảng bá nhóm câu đố như combo gia đình; xem xét rút gọn nhóm chó. Phân tích này dùng giá vốn định mức, chưa tính hao hụt thực tế theo món.

### 5.6.4. Ảnh hưởng của mưa và của điều chỉnh giá

Không tính ngày lễ, dữ liệu có 59 ngày mưa và 118 ngày khô. So với ngày khô, vào ngày mưa mỗi chi nhánh trung bình có ít hơn 27% đơn tại quầy, nhiều hơn 19% đơn App và 21% đơn sàn; tỷ trọng đơn giao hàng tăng từ 43,6% lên 56,0%, còn doanh thu mỗi chi nhánh mỗi ngày giảm 5,3%. Vì đơn sàn chịu phí khoảng một phần tư, ngày mưa làm biên lợi nhuận giảm nhiều hơn doanh thu. Hai gợi ý vận hành: dịch chuyển nhân sự từ quầy sang khu đóng gói vào ngày dự báo mưa, và ưu tiên kéo khách sang ứng dụng riêng vốn không mất phí sàn.

Sau điều chỉnh giá sáu món ngày 01/06, AOV hai tuần sau tăng 3,4% so với hai tuần trước (86.708 lên 89.670 đồng) và COGS% định mức giảm từ 31,6% xuống 30,6%. Số đơn mỗi ngày không giảm, nhưng điều này chỉ phản ánh giả định của bộ mô phỏng, vốn chưa mô hình hóa độ co giãn của cầu theo giá như đã nêu ở mục 3.3.9, chứ không phải bằng chứng về phản ứng của khách hàng.

### 5.6.5. Thiệt hại ước tính của các sự cố được phát hiện

TABLE: Bảng 5.11. Thiệt hại ước tính từ kho dữ liệu cho các sự cố được phát hiện (tập phát triển) || Kết quả thực nghiệm của tác giả
WIDTHS: 3.4,4.6,2.6,4
| Sự cố | Cách ước tính (mục 4.7) | Ước tính | Đối chiếu sau với tác động đo bởi bộ mô phỏng (Bảng 4.3) |
| S1 hoa hồng GrabFood CN4 | Hoa hồng thu thừa lũy kế 3 tuần | 0,72 triệu đ | Khớp: sàn tính 30% thay vì 25% |
| S2 đơn sàn không vào POS CN6 | Đơn thiếu vượt mức thường × giá trị đơn sàn, 2 tuần | 7,12 triệu đ | 8,52 triệu đ |
| S3 hao hụt CN7 | Hao hụt vượt mức thường của kỳ kiểm kê | 6,83 triệu đ | khoảng 7,5 triệu đ (682 nghìn đ/ngày × 11 ngày) |
| S4 thiếu nhân sự CN2 | Doanh thu thấp hơn kỳ vọng, 2 tuần | 94,6 triệu đ | Doanh thu thấp hơn nhóm cùng hạng 16,9% trong kỳ |
| S6 gian lận thu ngân CN8 | Giá trị hóa đơn bị hủy, hoàn, giảm giá của thu ngân bị nghi vấn, 4 tuần | 5,74 triệu đ (giá trị liên quan) | 5,31 triệu đ hóa đơn bị hủy sau khi thu tiền |

Các ước tính được tính hoàn toàn từ kho dữ liệu, không đọc đáp án; cột cuối chỉ dùng để kiểm tra độ hợp lý sau khi đã tính. Ước tính cùng bậc độ lớn với tác động thật, đủ để xếp thứ tự ưu tiên xử lý. Thiếu nhân sự là sự cố đắt nhất, gấp hơn mười lần các sự cố còn lại, dù về mặt dữ liệu nó chỉ là vài ca làm việc bị thiếu. Ngược lại, gian lận tại quầy và thất thoát kho nhỏ về tiền nhưng là vấn đề về kiểm soát nội bộ, nên vẫn cần được xử lý dù không đứng đầu danh sách.

## 5.7. Thảo luận

### 5.7.1. Trả lời các câu hỏi nghiên cứu

Với RQ1, câu hỏi về tích hợp dữ liệu, câu trả lời là có. Đường ống tích hợp được bảy nhóm hệ thống nguồn với ba định dạng tệp, hai phiên bản lược đồ POS, sáu hệ mã chi nhánh và các tên nguyên liệu tự do vào một lược đồ hình sao. Kết quả được kiểm chứng bằng ba lớp: 158/158 kiểm thử dbt đạt trên cả ba tập; đối soát số dòng Bronze–Silver không có phần chênh lệch không giải thích được ở cả bảy nguồn; doanh thu thuần Gold khớp tuyệt đối với Silver. Các quy tắc làm sạch xây dựng trên tập phát triển hoạt động không cần sửa trên tập kiểm tra, như Bảng 5.1 cho thấy. Đường ống chạy tăng dần, lũy đẳng và xử lý một ngày mới trong khoảng 80 giây. Giới hạn của kết quả này là các lỗi dữ liệu do bộ mô phỏng sinh ra, nên chưa bao phủ hết các dạng lỗi của dữ liệu thật.

Với RQ2, câu hỏi về phát hiện sự cố, trên tập kiểm tra chưa từng dùng để chọn ngưỡng, hệ thống bắt được bốn trên sáu sự cố với precision 0,50, recall theo tuần 0,54 và F1 0,52, độ trễ trung vị 6 ngày; trên tập phát triển là 5/6 và F1 0,79. Kết quả vượt rõ hai phương án cơ sở: chỉ theo dõi doanh thu bắt được 0/6 và 1/6 sự cố, Isolation Forest bắt được 3/6 và 2/6. Mức độ chính xác khác nhau theo loại sự cố. Đối soát sàn P1a, P1b đáng tin cậy nhất; hao hụt P2 bắt được nhưng có báo động giả; thiếu nhân sự nhẹ ở H4 và gian lận nhẹ ở H6 nằm sát dưới ngưỡng; thất thoát kho P4 không phát hiện được với nhịp kiểm kê hai tuần.

Với RQ3, câu hỏi về truy vết nguyên nhân, câu trả lời là phần lớn có thể. Khi một sự cố đã có tín hiệu, nguyên nhân đúng luôn được xếp hạng một, ở cả 5/5 sự cố có tín hiệu trên tập kiểm tra, và không cảnh báo nào trong cửa sổ sự cố bị chỉ sang một nguyên nhân vận hành sai. Ví dụ CN2 cho thấy cây KPI chỉ đúng kênh và thành phần bị ảnh hưởng, các tín hiệu nhân sự xác nhận nguyên nhân, kể cả tác động trễ qua thứ hạng sàn. Mức kỳ vọng theo nhóm cùng hạng loại được biến động của ngày lễ, mưa, điều chỉnh giá: không tuần nào trong các tuần này bị gán nguyên nhân do biến động chung, trong khi bỏ so nhóm thì tuần lễ bắt đầu bị cảnh báo và có tuần bị gán nhầm là thiếu nhân sự, như mục 5.5.3 đã cho thấy. Giới hạn chính là nhóm hạng C quá nhỏ, gây bốn trên bảy báo động giả trên tập kiểm tra.

### 5.7.2. So sánh với các nghiên cứu liên quan

Kết quả của khóa luận không so sánh trực tiếp được bằng con số với các nghiên cứu ở Bảng 2.5, vì dữ liệu, loại sự cố và cách đánh giá khác nhau. Tuy vậy, có thể so sánh về cách tiếp cận và về các xu hướng quan sát được.

Malashin và cộng sự (2024) dùng Isolation Forest và bộ mã hóa tự động trên dữ liệu hóa đơn nhà hàng và phát hiện được 25 trên 100 trường hợp bất thường đã biết. Trong khóa luận, phương án cơ sở Isolation Forest chạy trên toàn bộ 24 chỉ số giám sát cũng chỉ phát hiện được 2 trên 6 sự cố ở tập kiểm tra. Hai kết quả cùng cho thấy phương pháp không giám sát tổng quát chỉ ra được chỗ bất thường nhưng khó chỉ ra nguyên nhân. Cách khóa luận gắn mỗi nguyên nhân với một dấu vân tay chỉ số trên nhiều nguồn cho phép vừa phát hiện vừa gán nguyên nhân, đổi lại chỉ nhận ra được những nguyên nhân đã được định nghĩa trước; các trường hợp còn lại được ghi là chưa xác định.

So với Begen và cộng sự (2023), những người dùng mô hình phân loại có giám sát trên nhật ký POS để phát hiện gian lận tại quầy, bộ phát hiện P5 của khóa luận không cần dữ liệu gắn nhãn mà dựa trên kiểm định Poisson so với các thu ngân khác cùng chi nhánh. Ưu điểm là áp dụng được ngay cho doanh nghiệp chưa có lịch sử gian lận được xác minh; hạn chế là gian lận ở mức nhẹ như sự cố H6 không đạt ngưỡng của P5 và chỉ được cảnh báo ở tuần thứ tư dưới nhãn chưa xác định. Khi doanh nghiệp tích lũy được các trường hợp đã xác minh, hai cách có thể bổ trợ nhau.

Các phương pháp định vị nguyên nhân như Adtributor (Bhagwan và cộng sự, 2014) hay HotSpot (Sun và cộng sự, 2018) tìm chiều và giá trị gây ra biến động trên một chỉ số. Cây KPI của khóa luận làm việc tương tự ở bước đầu, khi tách doanh thu theo kênh, số đơn và giá trị đơn, nhưng đi thêm một bước là đối chiếu với dữ liệu nhân sự, kho và đối soát để chỉ ra nguyên nhân vận hành. Ví dụ CN2 ở mục 5.4.1 cho thấy bước đối chiếu này là cần thiết: phân rã doanh thu chỉ cho biết số đơn, nhất là đơn App, giảm; còn dữ liệu chấm công mới cho biết vì sao, và riêng doanh thu tuần đó còn chưa đủ để cảnh báo.

Cuối cùng, việc không phát hiện được thất thoát kho với nhịp kiểm kê hai tuần phù hợp với các nghiên cứu về sai lệch tồn kho: sai lệch phổ biến, tần suất kiểm kê là yếu tố làm giảm sai lệch (DeHoratius & Raman, 2008), và thất thoát nhỏ chỉ lộ ra khi đã tích lũy (Kang & Gershwin, 2005). Kết quả này vì vậy không chỉ là giới hạn của bộ phát hiện mà còn là giới hạn của dữ liệu kiểm kê thưa, và là căn cứ cho đề xuất kiểm kê dày hơn ở mục 6.2.

### 5.7.3. Các yếu tố ảnh hưởng đến tính hợp lệ của kết quả

Về tính hợp lệ nội tại, ngưỡng và tham số của các bộ phát hiện được chọn trên tập phát triển, nên kết quả trên tập này có xu hướng lạc quan; khoảng cách F1 từ 0,79 xuống 0,52 xác nhận điều đó. Việc báo cáo kết quả trên tập kiểm tra độc lập, với hạt giống, chi nhánh, thời điểm và mức độ sự cố khác, giảm thiểu rủi ro này. Tuy vậy, hai tập vẫn được sinh bởi cùng một bộ mô phỏng với cùng các giả định hành vi, nên tập kiểm tra kiểm tra được khả năng khái quát sang sự cố mới chứ chưa kiểm tra được khả năng khái quát sang một doanh nghiệp khác có quy luật vận hành khác. Ngoài ra, tác giả vừa thiết kế bộ mô phỏng vừa thiết kế bộ phát hiện, nên có nguy cơ vô thức thiết kế phương pháp phù hợp với cách dữ liệu được sinh ra.

Về tính hợp lệ cấu trúc, các kịch bản sự cố được thiết kế đơn giản hơn thực tế: mỗi kịch bản có một nguyên nhân chính, cường độ ổn định trong khoảng thời gian xác định, và các sự cố hầu như không chồng lấn nhau. Ngoài thực tế, nhiều vấn đề có thể xảy ra đồng thời và tăng dần, khiến việc phát hiện và truy vết khó hơn.

Về tính hợp lệ bên ngoài, dữ liệu là dữ liệu mô phỏng của một chuỗi giả định. Một số quy luật hành vi mua hàng như số món mỗi đơn, độ tập trung món bán chạy và độ dao động theo ngày đã được hiệu chỉnh từ dữ liệu giao dịch thật công khai ở mục 3.3.8, nhưng dữ liệu đó đến từ một tiệm bánh ở Vương quốc Anh, khác cả về loại hình lẫn bối cảnh. Các tham số vận hành còn lại là giả định hợp lý chưa được kiểm chứng bằng dữ liệu thật, như đã nêu ở mục 3.3.9. Kết quả định lượng vì vậy chưa thể khẳng định cho một doanh nghiệp cụ thể. Điều khóa luận chứng minh được là tính khả thi và tính đúng đắn của phương pháp trong điều kiện có kiểm soát, cùng một đường ống dữ liệu có thể áp dụng cho dữ liệu thật mà không phải thay đổi kiến trúc.

Về tính hợp lệ thống kê, mỗi tập chỉ có sáu kịch bản, nên các tỷ lệ phát hiện chỉ mang tính chỉ báo; chênh lệch một sự cố làm recall theo sự cố thay đổi khoảng 17 điểm phần trăm. Khóa luận khắc phục một phần bằng cách báo cáo chi tiết từng kịch bản và phân tích từng báo động giả.

## 5.8. Tiểu kết chương

Kết quả thực nghiệm trả lời được cả ba câu hỏi nghiên cứu, với những giới hạn đã nêu rõ. Về dữ liệu, đường ống tích hợp đủ bảy nhóm nguồn, bảo toàn số dòng và tổng tiền giữa các tầng, và chịu được các tình huống dữ liệu bất thường mà không đưa ra kết luận sai. Về phát hiện, trên tập kiểm tra độc lập hệ thống bắt được bốn trên sáu sự cố với F1 0,52, thấp hơn mức 0,79 trên tập phát triển nhưng vượt rõ cả hai phương án cơ sở. Về truy vết, khi sự cố đã để lại tín hiệu, nguyên nhân đúng luôn đứng hạng một, và các biến động bình thường như ngày lễ, mưa, điều chỉnh giá không bị gán nhầm thành sự cố. Điểm yếu tập trung ở các sự cố nhẹ, ngắn, ở thất thoát kho khi kiểm kê thưa và ở nhóm chi nhánh hạng C quá nhỏ. Chương 6 tổng kết các kết quả này theo mục tiêu đề tài và đề xuất hướng phát triển.
