# CHƯƠNG 4. HIỆN THỰC HỆ THỐNG

NGUON: Kết quả thực nghiệm

Chương này trình bày việc cài đặt các thành phần đã thiết kế ở Chương 3 và kết quả kiểm chứng từng thành phần theo thứ tự dòng dữ liệu: bộ mô phỏng, tầng thu thập và Bronze, Silver, Gold, bộ phát hiện, kho phục vụ, ứng dụng và điều phối. Các số liệu đều được đo trực tiếp trên hệ thống.

## 4.1. Môi trường và cấu trúc mã nguồn

TABLE: Bảng 4.1. Môi trường hiện thực || Cấu hình thực nghiệm
WIDTHS: 4,8
| Thành phần | Phiên bản, cấu hình |
| Máy tính | AMD Ryzen 5 5600H, RAM 16 GB, Windows 11 Home |
| Ngôn ngữ và xử lý dữ liệu | Python 3.12.4; pandas 3.0.6, NumPy 2.5.3, PyArrow 25.0.1, openpyxl 3.1.5 |
| Kho dữ liệu và biến đổi | DuckDB 1.5.6; dbt-core 1.12.5, dbt-duckdb 1.11.0 |
| Kho phục vụ và báo cáo | PostgreSQL 16.15; Metabase 0.58.36.1 |
| Ứng dụng | Streamlit 1.65.0 |
| Điều phối | Apache Airflow 2.10.5, Docker Compose (Docker 29.4) |
| API nguồn giả lập | FastAPI 0.143.3, Uvicorn 0.34.0 |

Mã nguồn được tổ chức theo đúng ranh giới kiến trúc: `simulator/` đóng vai các hệ thống nguồn, `source_api/` là API giả lập phía nguồn, `pipeline/` gồm thu thập, nạp, cửa chặn chất lượng và điều phối từng bước, `dbt/` gồm các mô hình Silver, Gold và kiểm thử, `analytics/` gồm bộ phát hiện, đề xuất xử lý và chương trình đánh giá, `app/` là ứng dụng, `airflow/` và `docker/` là cấu hình điều phối. Đáp án nằm trong thư mục `ground_truth/` của từng tập và chỉ được đọc bởi phần kiểm chứng, phần đánh giá và trang Bộ mô phỏng; `pipeline/`, `dbt/` và bộ phát hiện `analytics/detect.py` không đọc thư mục này.

## 4.2. Hiện thực bộ mô phỏng

### 4.2.1. Tổ chức chương trình và sinh dữ liệu tăng dần

Bộ mô phỏng gồm năm mô-đun Python. `config.py` tập trung toàn bộ tham số nghiệp vụ (Bảng 3.5) để mọi giả định truy vết được tại một nơi. `world.py` chứa lớp `World` giữ trạng thái của thế giới như tồn kho, điểm trên sàn, lịch sử mua của khách và bộ sinh số ngẫu nhiên; hàm `simulate_day()` lần lượt cho mỗi chi nhánh giao hàng, xếp ca, sinh nhu cầu, tính tải bếp và kết quả phục vụ từng đơn, cập nhật tồn kho và kiểm kê khi đến kỳ. `views.py` chuyển sự kiện thật thành bản ghi theo định dạng từng hệ thống và là nơi tạo các lỗi ở Bảng 3.6; `exporters.py` ghi tệp JSON, CSV và Excel; `run.py` điều khiển một lần chạy.

Sau mỗi lần chạy, toàn bộ đối tượng `World`, kể cả trạng thái bộ sinh số ngẫu nhiên, được lưu lại, nên sinh 182 ngày một lần cho kết quả giống hệt sinh 181 ngày rồi thêm một ngày. Nhờ vậy hệ thống vận hành như một doanh nghiệp đang hoạt động: mỗi ngày bộ mô phỏng thêm tệp của ngày mới và đường ống xử lý tăng dần. Hạt giống cố định là 2024 cho tập phát triển và 777 cho tập kiểm tra. Sinh một ngày của 11 chi nhánh mất khoảng một giây, toàn bộ 182 ngày khoảng 3,5 phút.

### 4.2.2. Dữ liệu nguồn được tạo ra

TABLE: Bảng 4.2. Khối lượng dữ liệu nguồn của tập phát triển (182 ngày, 11 chi nhánh)
WIDTHS: 4,2,2,5
| Hệ thống nguồn | Số tệp | Dung lượng | Số bản ghi |
| POS | 2.002 | 474,2 MB | 339.989 hóa đơn |
| Ứng dụng riêng | 182 | 106,9 MB | 96.779 đơn |
| GrabFood | 26 | < 0,1 MB | 286 dòng chi nhánh × tuần |
| ShopeeFood | 26 | 0,2 MB | 286 dòng chi nhánh × tuần |
| Sổ nhập kho | 1.699 | 9,6 MB | 18.424 dòng, cả dòng tổng cộng, chữ ký |
| Phiếu kiểm kê | 143 | 0,9 MB | 3.146 dòng |
| Máy chấm công | 2.002 | 2,6 MB | 42.375 lượt quẹt |
| Thời tiết | 182 | < 0,1 MB | 182 ngày |
| Danh mục trụ sở | 11 | < 0,1 MB | 8 ảnh chụp ban đầu và 3 ảnh chụp cập nhật |

Tập phát triển chứa 445.153 lượt nhu cầu, trong đó 435.279 đơn được phục vụ với tổng giá trị khoảng 38,67 tỷ đồng, AOV 88.844 đồng; gồm 227.182 đơn tại quầy, 93.664 đơn ứng dụng, 68.742 đơn GrabFood và 45.691 đơn ShopeeFood. Phần không được phục vụ gồm 1.149 lượt khách bỏ về, 2.096 đơn bị cửa hàng hủy và 4.797 đơn bị khách hủy. Tập kiểm tra có 384.918 đơn được phục vụ, khoảng 34,15 tỷ đồng. Hình 4.1 trích nguyên văn dữ liệu thô của một số nguồn, cho thấy mức độ không đồng nhất mà đường ống phải xử lý.

IMAGE: figures/h4_2_du_lieu_tho.png || Hình 4.1. Ví dụ dữ liệu thô của các hệ thống nguồn, trích nguyên văn từ tệp của tập phát triển || 13 || Trích từ tệp nguồn của tập phát triển

### 4.2.3. Kiểm chứng bộ mô phỏng

Trước khi dùng dữ liệu để xây dựng và đánh giá đường ống, cần kiểm chứng bộ mô phỏng tạo đúng các tác động đã thiết kế. Chương trình `validate.py`, được phép đọc đáp án vì chỉ phục vụ bộ mô phỏng, so giai đoạn sự cố với bốn tuần trước đó của cùng chi nhánh; với kịch bản thiếu nhân sự còn so với các chi nhánh cùng hạng để loại biến động chung (Bảng 4.3, Bảng 4.4).

TABLE: Bảng 4.3. Tác động đo được của các kịch bản sự cố trên hai tập
WIDTHS: 1.6,7.2,7.2
| Vấn đề | Tập phát triển | Tập kiểm tra |
| P1a | S1: hoa hồng GrabFood của CN4 bị tính 30% trong đúng ba tuần bắt đầu 13/5, 20/5, 27/5 | H1: hoa hồng ShopeeFood của CN10 bị tính 26% trong hai tuần bắt đầu 5/8, 12/8 |
| P1b | S2: tỷ lệ đơn sàn không có trên POS của CN6 tăng từ 2,6% lên 15,5%; giá trị mất dấu vết 8,52 triệu đ | H2: CN3 tăng từ 3,2% lên 16,4%; 18,70 triệu đ |
| P2 | S3: hao hụt vượt định mức mỗi ngày của CN7 tăng từ khoảng 119 lên 801 nghìn đ | H3: CN1 tăng từ khoảng 101 lên 533 nghìn đ |
| P3 | S4: bếp ca tối CN2 giảm từ 3,6 xuống 1,8 người; tải đỉnh 0,80 → 1,67; thời gian chuẩn bị 15,5 → 20,4 phút; khách bỏ về 1,2 → 16,9 lượt/ngày; đơn bị cửa hàng hủy 1,9 → 16,6/ngày; hệ số thứ hạng GrabFood 0,98 → 0,90 trong kỳ và 0,84 ba tuần sau. Doanh thu thấp hơn nhóm cùng hạng 16,9% trong kỳ, 6,7% ba tuần sau | H4: bếp ca tối CN8 giảm từ 4,6 xuống 3,0 người; tải đỉnh 0,66 → 0,99; thời gian chuẩn bị 13,0 → 16,0 phút; khách bỏ về 0,1 → 5,9 lượt/ngày; đơn bị cửa hàng hủy 1,3 → 4,0/ngày. Doanh thu chỉ thấp hơn nhóm cùng hạng 1,4% trong kỳ, 0,9% ba tuần sau |
| P4 | S5: nguyên liệu bị mất tại CN9 trong 14 ngày khoảng 0,83 triệu đ | H5: CN5, khoảng 0,18 triệu đ |
| P5 | S6: thu ngân NV0093 của CN8 hủy 60 hóa đơn tiền mặt sau khi thu tiền, 5,31 triệu đ | H6: NV0126 của CN10 hủy 29 hóa đơn, 2,62 triệu đ |

TABLE: Bảng 4.4. Các biến động bình thường đo được (ngày không có sự cố)
WIDTHS: 5,3,3
| Yếu tố | Tập phát triển | Tập kiểm tra |
| Doanh thu cuối tuần so với ngày thường | +25,0% | +25,4% |
| Doanh thu ngày lễ so với ngày thường | +22,7% | +21,2% |
| Số đơn tại quầy ngày mưa so với ngày khô | −25,9% | −25,5% |
| Số đơn giao hàng ngày mưa so với ngày khô | +22,4% | +21,1% |
| AOV trước và sau điều chỉnh giá 1/6 | 87.450 → 90.014 đ | 87.173 → 90.141 đ |

Cả mười hai kịch bản đều tạo tác động đúng chỗ, đúng thời điểm và đúng chiều. S4 tái hiện đủ chuỗi nhân quả: thời gian chuẩn bị tăng, khách bỏ về, cửa hàng hủy đơn, rồi thứ hạng sàn giảm và doanh thu còn thấp nhiều tuần sau khi sự cố kết thúc; H4 nhẹ hơn có tín hiệu vận hành rõ nhưng doanh thu gần như không đổi, đúng với thực tế là không phải lần thiếu người nào cũng gây mất doanh thu rõ rệt. Trong khi đó các yếu tố bình thường tạo biến động bằng hoặc lớn hơn tác động của sự cố: ngày lễ làm doanh thu tăng 21–23%, ngày mưa làm số đơn mỗi kênh đổi 21–26%. Vì vậy, như RQ3 đặt ra, phương pháp chỉ nhìn độ lớn biến động sẽ cảnh báo sai rất nhiều. Thiệt hại của thất thoát kho và gian lận chỉ 0,2 đến 5,3 triệu đồng, nhỏ so với doanh thu hàng trăm triệu mỗi tuần; mức này có chủ đích, vì ngoài thực tế các vấn đề này thường nhỏ lẻ, kéo dài và không lộ ra ở chỉ số tổng hợp.

## 4.3. Hiện thực tầng thu thập và Bronze

### 4.3.1. Kênh thu thập và hợp đồng dữ liệu

Danh mục nguồn và hợp đồng dữ liệu được khai báo một lần trong `pipeline/contracts.py`, dùng chung cho kênh tải lên, bước nạp và trang Kết nối nguồn (Bảng 4.5).

TABLE: Bảng 4.5. Kênh thu thập của từng nguồn || Đề xuất của nghiên cứu
WIDTHS: 2.4,5,4.6,2.2
| Nguồn | Ngoài thực tế thường đến bằng | Trong hệ thống này | Tần suất |
| POS tại quầy | API của POS đám mây; POS cài tại máy xuất tệp mỗi đêm | 8 chi nhánh dùng POS đám mây: kéo qua API; CN5, CN7, CN10 dùng POS cài tại máy: tệp JSON mỗi đêm | Hằng ngày |
| App đặt hàng riêng | API hoặc bản sao cơ sở dữ liệu của công ty | Kéo qua API | Hằng ngày |
| GrabFood, ShopeeFood | Kế toán tải báo cáo từ cổng đối tác hoặc nhận qua email | Tệp CSV, Excel vào vùng tiếp nhận hoặc tải lên | Hằng tuần |
| Sổ nhập kho, phiếu kiểm kê | Quản lý cửa hàng điền Excel, gửi qua email hoặc nhắn tin | Tệp Excel vào vùng tiếp nhận hoặc tải lên | Mỗi lần nhập; hai tuần |
| Máy chấm công | Phần mềm đi kèm máy vân tay xuất CSV | Tệp CSV vào vùng tiếp nhận | Hằng ngày |
| Thời tiết, danh mục trụ sở | API thời tiết; tệp xuất khi danh mục đổi | Tệp JSON, CSV vào vùng tiếp nhận | Hằng ngày; khi đổi |

Hàm nhận dạng đọc nội dung tệp chứ không dựa vào tên: từ khóa JSON, dòng tiêu đề cột của CSV hay dòng tiêu đề phiếu của Excel cho biết nguồn, chi nhánh và ngày, từ đó ra vị trí chuẩn trong vùng tiếp nhận. CSV được đọc thử lần lượt với các bảng mã UTF-8, UTF-16, Windows-1258 và Windows-1252, vì phần mềm cũ hay xuất UTF-16. Kênh tải lên trong `pipeline/intake.py` cho bốn kết quả là đã nhận, thay bản cũ, trùng nên bỏ qua và từ chối kèm lý do; tệp được ghi ra tệp tạm rồi đổi tên trong một thao tác nên bước nạp không đọc phải tệp ghi dở, và sau khi nhận, ứng dụng báo Airflow để đường ống chạy ngay. Hình 4.2 là kết quả gửi chín tệp mẫu, gồm cả các trường hợp sai như báo cáo GrabFood lưu nhầm thành Excel, tệp chấm công thiếu cột, bảng lương gửi nhầm và tệp của một máy POS chưa khai báo.

IMAGE: figures/h4_tai_len.png || Hình 4.2. Trang Tải tệp lên sau khi gửi chín tệp mẫu (môi trường vận hành) || 12 || Ảnh chụp giao diện hệ thống

### 4.3.2. API nguồn và bộ kết nối

Để đường API được kiểm chứng như thực tế, phía nguồn có một dịch vụ FastAPI riêng (`source_api/app.py`). Ở môi trường vận hành, bộ mô phỏng ghi hóa đơn của tám chi nhánh POS đám mây và đơn App vào kho riêng của phần mềm nguồn, bên ngoài chỉ lấy được qua API. Dịch vụ có bốn điểm cuối cho danh sách ngày và danh sách bản ghi theo ngày của POS và App, phân trang tối đa 500 bản ghi kèm tổng số để đối chiếu, xác thực bằng mã Bearer; như API thật, dịch vụ giới hạn 20 lượt gọi mỗi giây, vượt thì trả mã 429, và trả lỗi tạm thời 503 với xác suất 8%. Hai tập đánh giá vẫn đi đường tệp để kết quả đã chốt không đổi.

Bộ kết nối `pipeline/extract.py` chỉ dùng thư viện HTTP chuẩn của Python. Mỗi lượt, nó lấy các ngày sau mốc và lấy lại ngày mốc theo trang 200 bản ghi rồi so tổng với số API báo; lỗi 503, 429 hoặc mất kết nối được thử lại tối đa sáu lần với thời gian chờ 0,5 đến 8 giây hoặc theo yêu cầu của API, còn mã 401, 403 dừng ngay. Dữ liệu được ghi vào vùng tiếp nhận đúng định dạng tệp của nguồn; tệp có nội dung không đổi thì không ghi lại, nên lấy lại ngày mốc không làm đường ống nạp lại. Mốc và thống kê từng lượt được lưu trong `landing/api_connector.json`.

TABLE: Bảng 4.6. Một lượt kéo bảy ngày kinh doanh 23–29/09/2024 qua API (môi trường vận hành, chạy trong Airflow)
WIDTHS: 3,1.4,1.8,1.4,1.6,1.6,1.4,1.8
| Hệ thống | Số ngày | Bản ghi | Trang | Lần gọi | Thử lại | Tệp ghi | Thời gian |
| POS đám mây (8 chi nhánh) | 7 | 10.365 | 55 | 62 | 6 | 56 | 7,2 giây |
| App đặt hàng | 7 | 3.880 | 24 | 26 | 1 | 7 | 1,2 giây |

Bảy lần thử lại ở Bảng 4.6 do lỗi 503 ngẫu nhiên và đều thành công ở lần sau. Để kiểm chứng đường API không làm thay đổi dữ liệu, 56 tệp POS trong vùng tiếp nhận được so với tệp gốc trong kho của phần mềm nguồn: cả 56 giống nhau đến từng byte. Lần chạy thật đầu tiên lộ ra một lỗi: mốc khởi tạo lấy ngày mới nhất trên mọi thư mục POS, trong khi ba chi nhánh POS cài tại máy đã có tệp tới 29/09, nên mốc nhảy qua sáu ngày 23–28/09 của POS đám mây. Lỗi được sửa bằng cách lấy ngày nhỏ nhất trong các ngày mới nhất của từng máy, kèm kiểm thử hồi quy; lượt lỗi đó vô tình trở thành một phép thử thiếu dữ liệu hàng loạt (mục 5.2.3).

### 4.3.3. Nạp tầng Bronze

Chương trình `pipeline/ingest.py` khai báo danh sách nguồn như một bảng cấu hình gồm bảng Bronze đích, mẫu đường dẫn và bộ đọc, nên thêm một nguồn chỉ cần thêm một dòng. Bốn bộ đọc được xây dựng cho JSON của POS, JSON có vỏ bọc API của App, CSV và Excel; bộ đọc Excel tự xác định dòng tiêu đề cột là dòng đầu tiên có từ ba ô có giá trị và giữ các dòng phía trên trong cột `_doc_line_k`. Mọi giá trị giữ dạng chuỗi; chỉ tên cột được chuyển sang dạng an toàn cho SQL, ví dụ “Doanh thu món (VNĐ)” thành `doanh_thu_mon_vnd`. Khi nguồn xuất hiện cột mới, chương trình tự thêm cột vào bảng Bronze thay vì báo lỗi. Trước khi đọc, mỗi tệp được kiểm tra theo hợp đồng của thư mục chứa nó, vì tệp có thể được thả thẳng vào vùng tiếp nhận: tệp sai hợp đồng có trạng thái `rejected`, kể cả tệp POS ngày 23/09 bị chép thành tên ngày 30/09; tệp ngoài mọi mẫu đường dẫn là `unrecognized`; tệp không đọc được là `failed`. Tệp POS rỗng là hợp lệ vì cửa hàng có thể nghỉ, nhưng cửa chặn chất lượng coi như chi nhánh đó thiếu dữ liệu.

Lần nạp đầu của tập phát triển xử lý 6.273 tệp thành 17 bảng Bronze với khoảng 502 nghìn dòng trong 80 giây, không có tệp lỗi; số dòng mỗi bảng bằng đúng số bản ghi ở Bảng 4.2. Chạy lại ngay khi không có tệp mới mất 5 giây và không tạo dòng nào. Khi bộ mô phỏng thêm ngày 09/9/2024, chương trình chỉ nạp đúng 35 tệp, 2.561 dòng của ngày đó trong 5 giây, tức chi phí hằng ngày tỷ lệ với lượng dữ liệu mới chứ không với kích thước lịch sử (NFR2). Bronze giữ nguyên mọi khác biệt của dữ liệu gốc. Hình 4.3 là một truy vấn trên trang Kho dữ liệu: 281.695 hóa đơn phiên bản 3.2.1 ghi tổng tiền ở cột `total_paid` và thời gian dạng ngày/tháng/năm, còn 59.979 hóa đơn phiên bản 2.8.0 ghi ở `grand_total` với thời gian dạng ISO; tổng hai nhóm đúng bằng 341.674 hóa đơn POS.

IMAGE: figures/ph_kho_sql.png || Hình 4.3. Truy vấn trên tầng Bronze: hai phiên bản phần mềm POS ghi tổng tiền và thời gian theo hai cách (tập phát triển) || 13 || Ảnh chụp giao diện hệ thống

## 4.4. Hiện thực tầng Silver

### 4.4.1. Tổ chức dự án dbt

Tầng Silver và Gold nằm trong một dự án dbt ở thư mục `dbt/`, chạy bằng `pipeline/run_dbt.py`; chương trình này chọn tệp kho của tập cần chạy và tách thư mục kết quả của từng tập, nên các tập được dựng độc lập bằng cùng mã nguồn. Dự án gồm 50 mô hình, 3 bảng hạt giống và 158 kiểm thử, tổng 211 bước trong một lần `dbt build`, chia theo ba lược đồ. `silver_work` chứa 10 mô hình trung gian và 3 bảng hạt giống (ánh xạ mã chi nhánh, biến thể tên nguyên liệu, ngày lễ 2024); mô hình trung gian gồm `parsed_` giải mã JSON theo chế độ tăng dần, `base_` ép kiểu và gắn mã lỗi, `checked_` áp quy tắc cần so với lịch sử, `map_` giải quyết định danh. `silver` chứa 20 bảng `stg_` đã sạch, bảng cách ly và bảng đối soát. `gold` chứa 13 bảng chiều, sự kiện và 5 bảng chỉ số. Mỗi nguồn đi qua cùng một khuôn: `base_` gắn cột `dq_issue` cho dòng vi phạm, `stg_` chỉ lấy dòng có `dq_issue` rỗng, bảng cách ly lấy phần còn lại, nên không dòng nào bị xóa im lặng.

### 4.4.2. Xử lý lỗi dữ liệu và giải quyết định danh

Các quy tắc ở Bảng 3.9 được hiện thực theo hai hướng: lỗi kỹ thuật bị tách khỏi dữ liệu, còn tín hiệu nghiệp vụ được giữ kèm cờ. Hai phiên bản POS được nhận diện theo từng hóa đơn rồi đưa về lược đồ chung; chẳng hạn hóa đơn bản 2.8 của CN7 ngày 12/4 ghi “2024-04-12T07:10:59” và chuỗi “89.000” ở `grand_total`, còn hóa đơn bản 3.2 của CN8 ghi “12/04/2024 07:11:22” và số 90000 ở `total_paid`. Hóa đơn hủy và hoàn được giữ lại, kèm số phút từ lúc thanh toán đến lúc hủy, vì đây là đầu vào của bộ phát hiện gian lận. Đơn App được đổi từ UTC sang giờ Việt Nam trước khi xác định ngày và ca; nếu không, mọi đơn ca tối sẽ rơi vào ca sáng. Ở sổ kho, số lượng lớn hơn 20 lần trung vị cùng nguyên liệu bị cách ly với mã `nghi_go_gam_vao_cot_kg`, ví dụ cà chua 2.300 kg khi trung vị là 2,2 kg. Ở chấm công, lượt quẹt cùng loại lặp lại trong 5 phút bị cách ly với mã `quet_trung`, ca thiếu lượt ra được gắn cờ mà không tự gán số giờ, ô kiểm kê trống giữ giá trị thiếu kèm cờ thay vì thay bằng 0. Số dòng chịu tác động của từng quy tắc trên hai tập được trình bày ở Bảng 5.1.

Về định danh, mã chi nhánh của sáu hệ thống được ánh xạ bằng bảng hạt giống `branch_code_map` lập từ khảo sát Bronze; mã `NV0012` của POS được chuẩn hóa về mã số của trụ sở bằng quy tắc; 28 món trên App đều khớp với danh mục trụ sở qua tên đã bỏ dấu. Tên nguyên liệu trong sổ kho đi qua ba tầng: khớp chính xác sau chuẩn hóa xử lý 38 cách viết, 84,3% số dòng; bảng biến thể 29 cách viết do người hiểu nghiệp vụ lập, chẳng hạn “gà tươi” và “thịt gà” đều là Thịt gà tươi, xử lý 35 cách viết, 15,7%; tầng khớp mờ Jaro–Winkler ngưỡng 0,9 chưa phải dùng lần nào. Thứ tự này có chủ đích: khớp mờ dễ nhầm giữa nguyên liệu tên gần nhau nên chỉ là lưới an toàn cuối cùng, và tên dưới ngưỡng được cách ly để người bổ sung vào bảng biến thể.

### 4.4.3. Bảo toàn số dòng

Bảng `silver_row_reconciliation` đối soát từng nguồn theo đẳng thức Bronze = Silver + cách ly + dòng cấu trúc, và kiểm thử `assert_silver_rows_conserved` thất bại nếu phần không giải thích được khác 0 (Bảng 4.7). Báo cáo GrabFood có 286 dòng ở cả hai tầng và được kiểm tra bằng hai kiểm thử riêng: mỗi chi nhánh × tuần đúng một dòng, và tiền thực nhận bằng doanh thu món trừ hoa hồng, quảng cáo, khuyến mãi cộng điều chỉnh.

TABLE: Bảng 4.7. Đối soát số dòng giữa Bronze và Silver (tập phát triển, 183 ngày)
WIDTHS: 3.4,1.9,1.9,1.8,1.8,2
| Nguồn | Bronze | Silver | Cách ly | Dòng cấu trúc | Không giải thích được |
| POS | 341.674 | 341.674 | 0 | 0 | 0 |
| Ứng dụng | 97.207 | 97.207 | 0 | 0 | 0 |
| ShopeeFood | 286 | 286 | 0 | 0 | 0 |
| Sổ nhập kho (hai mẫu) | 18.652 | 16.104 | 62 | 2.486 | 0 |
| Phiếu kiểm kê | 3.146 | 3.146 | 0 | 0 | 0 |
| Chấm công | 42.594 | 41.304 | 1.290 | 0 | 0 |
| Thời tiết | 183 | 183 | 0 | 0 | 0 |

## 4.5. Hiện thực tầng Gold

### 4.5.1. Bảng chiều, bảng sự kiện và bảng chỉ số

TABLE: Bảng 4.8. Các bảng chiều và sự kiện của tầng Gold (tập phát triển, 183 ngày)
WIDTHS: 4.2,1.8,7
| Bảng | Số dòng | Ghi chú hiện thực |
| `fact_order` | 438.881 | Hợp nhất 341.674 hóa đơn POS và 97.207 đơn App; trạng thái chuẩn hóa về COMPLETED, VOIDED, REFUNDED, CANCELLED_BY_STORE, CANCELLED_BY_CUSTOMER; doanh thu thuần chỉ tính COMPLETED |
| `fact_order_line` | 851.601 | Gắn phiên bản món có hiệu lực tại ngày bán để lấy giá vốn định mức |
| `fact_labor_shift` | 21.170 | 1.036 ca thiếu lượt ra được nội suy số giờ bằng trung vị cùng ca, vai trò, cờ `is_hours_imputed` |
| `fact_marketplace_settlement` | 572 | Hai sàn × 11 chi nhánh × 26 tuần; tỷ lệ hợp đồng, chênh lệch, tiền thu thừa |
| `fact_inventory_receipt` | 16.104 | Dòng nhập kho hợp lệ, đơn vị chuẩn |
| `fact_stock_count` | 3.146 | Tồn đếm được, cờ ô trống |
| `dim_date`, `dim_branch` | 183; 11 | Ngày lễ từ bảng hạt giống, mưa; hạng, quận và mã chi nhánh ở mọi hệ thống |
| `dim_menu_item` | 34 | SCD kiểu 2: 28 món, 6 món có hai phiên bản do điều chỉnh giá 01/06 |
| `dim_employee` | 146 | SCD kiểu 2: 145 nhân viên, 1 người lên quản lý ca từ 01/07 |
| `dim_ingredient`, `dim_channel`, `dim_customer` | 22; 4; 4.089 | Nguyên liệu, kênh, khách hàng App |

Với chiều SCD kiểu 2, các ảnh chụp danh mục liên tiếp có cùng giá và giá vốn được gộp thành một phiên bản; khi giá đổi, phiên bản cũ đóng ở ngày liền trước ảnh chụp mới và phiên bản mới mở từ ngày đó. Ví dụ món Gà giòn miếng đơn có hai phiên bản: 35.000 đồng đến 31/05/2024 và 37.000 đồng từ 01/06/2024, nên giá vốn của một dòng món bán ngày 30/5 và ngày 2/6 được tính theo hai bảng giá khác nhau.

Năm bảng chỉ số ở mục 3.7.1 cũng viết bằng SQL trong dbt nên được kiểm thử và có phả hệ như mọi bảng Gold. `mart_branch_daily` có 52 cột cho mỗi chi nhánh × ngày; `mart_branch_weekly` nối với báo cáo sàn để tính độ phủ POS và chênh lệch hoa hồng; `mart_ingredient_avt` tính hao hụt theo kỳ kiểm kê, combo được tách thành món thành phần trước khi nhân công thức; `mart_cashier_weekly` tính tỷ lệ hủy, hoàn, giảm giá của từng thu ngân và của các thu ngân còn lại. `mart_kpi_vs_peers_weekly` hiện thực công thức (3.6), (3.7) ở dạng dài, mỗi dòng là một chi nhánh × tuần × chỉ số với giá trị, trung vị nhóm, mức nền, độ dao động, z và mức kỳ vọng, gồm 10.582 dòng ở tập phát triển; trung vị và MAD cửa sổ tám tuần được tính bằng hàm cửa sổ của DuckDB.

Vì mọi biến đổi được khai báo trong dbt, phả hệ của từng bảng được sinh từ siêu dữ liệu của dự án. Hình 4.4 là phả hệ của `fact_order`: bảng được dựng từ hai bảng Bronze của POS và App qua các bước giải mã, gắn mã chi nhánh và làm sạch, lấy phiên bản nhân viên từ `dim_employee`, và là nguồn của các bảng chỉ số. Khi một con số ở Gold cần giải thích, phả hệ cho biết phải kiểm tra những bảng nào phía trước.

IMAGE: figures/h4_pha_he.png || Hình 4.4. Phả hệ dữ liệu của bảng fact_order, sinh từ siêu dữ liệu dbt || 9.5 || Ảnh chụp giao diện hệ thống

### 4.5.2. Kiểm thử

Dự án dbt có 158 kiểm thử theo các nhóm ở Bảng 3.12: 83 `not_null`, 36 `unique`, 18 `relationships` và 9 `accepted_values` khai báo trong tệp cấu hình mô hình; năm kiểm thử tổng quát `unique_combination` cho khóa ghép của năm bảng chỉ số; và bảy luật nghiệp vụ dạng câu SQL gồm bảo toàn số dòng, tạm tính POS bằng tổng dòng món, thực nhận của hai sàn khớp công thức, một dòng GrabFood mỗi chi nhánh × tuần, SCD không chồng lấn và doanh thu Gold bằng Silver. Cả 158 kiểm thử đạt trên ba tập dữ liệu; chẳng hạn `assert_gold_net_sales_reconciles` cho thấy tổng doanh thu thuần 37.899.868.200 đồng của tập phát triển khớp tuyệt đối giữa Silver và Gold theo từng chi nhánh × ngày. Một lần `dbt build` đầy đủ mất 15 đến 25 giây, phần lớn ở hai mô hình giải mã JSON khi phải giải mã lại từ đầu.

Kiểm thử dbt kiểm tra dữ liệu nhưng không kiểm tra được mã Python của đường ống. Phần này có 89 kiểm thử pytest chạy trên dữ liệu nhỏ dựng riêng trong thư mục tạm: 12 cho bước nạp, như nạp lại không tạo dòng trùng hay tệp hỏng không làm hỏng cả lô; 10 cho hợp đồng dữ liệu; 10 cho bộ kết nối API, như thử lại khi lỗi tạm thời, lấy bổ sung hóa đơn đến trễ và làm tiếp đúng chỗ sau gián đoạn; 20 cho cửa chặn chất lượng; 4 cho bước kiểm tra tệp mới; cùng các kiểm thử cho phép thống kê của bộ phát hiện, đề xuất xử lý và ô truy vấn SQL chỉ đọc. Cả 89 kiểm thử đều đạt.

## 4.6. Hiện thực các bộ phát hiện và đề xuất xử lý

Các bộ phát hiện nằm trong `analytics/` và chỉ đọc tầng Gold. `config.py` khai báo bộ chỉ số giám sát, các ngưỡng và “dấu vân tay” của từng nguyên nhân, tức danh sách chỉ số cùng chiều bất thường đặc trưng cho nguyên nhân đó. `detect.py` có ba hàm chính: `scan_indicators` liệt kê chỉ số vượt ngưỡng, `score_all` chấm điểm mọi giả thuyết cho mọi chi nhánh × tuần, `alert_table` chọn giả thuyết mạnh nhất và xếp mức. Chương trình chỉ dùng thông tin có tại thời điểm đánh giá, không nhìn dữ liệu tương lai; quét 242 chi nhánh × tuần của một tập mất khoảng một giây. Các tham số và lý do chọn được trình bày ở Bảng 4.9.

TABLE: Bảng 4.9. Tham số của bộ phát hiện và lý do chọn (chỉ trên tập phát triển)
WIDTHS: 3.4,3,7
| Tham số | Giá trị | Lý do |
| Mức nền | Trung vị 8 tuần trước | Bản đầu dùng trung bình 4 tuần; tuần 27/5 ở CN2, sau sự cố thiếu nhân sự, bị báo sai vì các tuần sự cố kéo mức nền xuống. Độ nhạy được đo ở mục 5.5.3 |
| Độ dao động | 1,4826 × MAD 8 tuần, sàn bằng trung vị các chi nhánh; điểm đánh giá sàn 0,05 | Độ lệch chuẩn của 8 mẫu quá nhỏ ở vài chi nhánh gây báo sai; điểm đánh giá làm tròn 0,1 nên MAD có thể bằng 0 |
| Lịch sử tối thiểu | 4 tuần | Bốn tuần đầu của mỗi tập chỉ dùng làm mức nền |
| Dung sai hoa hồng (P1a) | 0,5 điểm % | Lớn hơn nhiều sai số làm tròn trên báo cáo sàn |
| Nhóm giá trị cao (P4) | Giá chuẩn từ 80.000 đ/đơn vị | Tôm, thịt bò, phô mai, thịt gà: dễ bị lấy cắp, giá trị lớn |
| Thu ngân (P5) | Từ 30 hóa đơn/tuần; tỷ lệ kỳ vọng tối thiểu 0,5% | Tránh kết luận từ mẫu nhỏ; so với thu ngân khác cùng tuần vì khi gian lận kéo dài, lịch sử bị nhiễm làm điểm giảm dần |
| Ngưỡng z | Theo dõi 2, bất thường 3 | Quy ước thông dụng, không tinh chỉnh |
| Ngưỡng điểm cảnh báo | 3,5 | F1 cao nhất khi quét 2,0–5,0 trên tập phát triển (mục 5.5.1), chốt trước khi chạy tập kiểm tra |

Một số quy tắc gộp bằng chứng được bổ sung khi phân tích cảnh báo sai trên tập phát triển. Ví dụ ở S2, nguyên liệu vẫn được dùng cho các đơn không vào sổ nên hao hụt hàng giá trị cao cũng tăng (z = 8,3), làm P4 hòa điểm với P1b; quy tắc giảm một nửa điểm P4 khi P1b đủ bằng chứng xuất phát từ quan sát này. Mọi quy tắc như vậy đều được chốt trước khi chạy tập kiểm tra.

Tệp `actions.py` lập đề xuất xử lý gồm việc xác minh, việc cần làm, việc theo dõi, người phụ trách, thời hạn và thiệt hại ước tính tính từ Gold. Với P1a đó là hoa hồng thu thừa lũy kế để kế toán đòi lại; P1b là số đơn thiếu trên POS vượt mức thường nhân giá trị đơn sàn bình quân; P2 và P4 là hao hụt vượt mức thường, với mức thường lấy theo tỷ lệ hao hụt trên định mức của các chi nhánh khác cùng kỳ; P3 là doanh thu thấp hơn kỳ vọng, đơn App bị hủy và chi phí bù ca bếp tối; P5 là giá trị hóa đơn bị hủy, hoàn, giảm giá của thu ngân nghi vấn, kèm ghi chú đây là giá trị liên quan chứ không phải số tiền đã xác định thất thoát, và không được kết luận gian lận chỉ từ thống kê. Con số này giúp xếp thứ tự xử lý: trên tập phát triển, cảnh báo hao hụt đúng ở CN7 ước tính vượt mức thường 6,83 triệu đồng, còn cảnh báo sai ở CN10 chỉ 66 nghìn đồng.

## 4.7. Kho phục vụ và báo cáo kinh doanh

Chương trình `pipeline/publish.py` đưa 22 bảng gồm toàn bộ Gold và bốn bảng vận hành từ DuckDB sang PostgreSQL qua phần mở rộng postgres của DuckDB; kiểu số nguyên 128 bit được đổi sang `BIGINT`. Sau khi nạp vào lược đồ tạm, chương trình so số dòng từng bảng với DuckDB, chỉ khi khớp hết mới đổi lược đồ trong một giao dịch, cấp quyền cho vai trò chỉ đọc `bi_reader`, tạo chỉ mục cho các cột hay lọc và ghi nhật ký. Mỗi lượt của môi trường vận hành đưa khoảng 1,5 triệu dòng trong 9 đến 15 giây.

Metabase được dựng hoàn toàn bằng mã trong `bi/metabase_setup.py` qua giao diện lập trình: kết nối ba cơ sở dữ liệu bằng tài khoản chỉ đọc, đặt định dạng số kiểu Việt Nam, tạo 15 câu hỏi SQL và một dashboard cho mỗi tập kèm bộ lọc khoảng ngày và chi nhánh, rồi tạo liên kết để nhúng; chạy lại cho cùng kết quả. Trang Tổng quan của ứng dụng (Hình 4.5) nhúng dashboard của tập đang chọn và truyền bộ lọc ở thanh bên qua địa chỉ, nên người dùng không phải chọn lại ở hai nơi.

IMAGE: figures/h4_3_tong_quan.png || Hình 4.5. Trang Tổng quan: dashboard Metabase trên kho phục vụ, nhúng vào ứng dụng (tập phát triển, toàn chuỗi) || 13 || Ảnh chụp giao diện hệ thống

## 4.8. Ứng dụng

### 4.8.1. Tổ chức ứng dụng

Ứng dụng Streamlit (`app/main.py`) có 14 trang xếp theo dòng dữ liệu như mục 3.8.1, mỗi trang một tệp trong `app/views/`. Ứng dụng chỉ mở DuckDB ở chế độ đọc, đóng ngay sau mỗi lần đọc để không giữ khóa tệp, và tự đọc lại khi đường ống vừa ghi dữ liệu mới. Trang chủ Sơ đồ hệ thống (Hình 4.6) tóm tắt các tầng, mỗi thẻ hiện số liệu hiện tại như số tệp nguồn, số dòng Bronze, số dòng bị cách ly và số đơn ở Gold.

IMAGE: figures/h4_so_do.png || Hình 4.6. Trang chủ Sơ đồ hệ thống với số liệu của từng tầng (tập phát triển) || 15 || Ảnh chụp giao diện hệ thống

### 4.8.2. Các trang phân tích vận hành

Trang Trung tâm cảnh báo (Hình 4.7) hiển thị bản đồ nhiệt mức cảnh báo theo chi nhánh × tuần và danh sách cảnh báo với nguyên nhân, điểm, bằng chứng, thiệt hại ước tính và người phụ trách, sắp theo thiệt hại; người dùng có thể thay ngưỡng điểm để xem đánh đổi giữa bỏ sót và báo động giả, và chọn một dòng để mở trang Truy vết của đúng chi nhánh, tuần đó.

IMAGE: figures/h4_4_canh_bao.png || Hình 4.7. Trang Trung tâm cảnh báo (tập phát triển) || 12.5 || Ảnh chụp giao diện hệ thống

Trang Truy vết nguyên nhân mở đầu bằng kết luận và đề xuất xử lý (Hình 4.8), tiếp theo là doanh thu thực tế so với kỳ vọng qua các tuần, cây KPI theo kênh, số đơn và AOV, tín hiệu của từng giả thuyết và các yếu tố bình thường của tuần. Cuối trang là mục bằng chứng gốc, hiện thực FR8 và NFR3: trang liệt kê các bản ghi làm căn cứ cùng tên tệp và số dòng gốc mà Bronze đã lưu, và một nút mở thẳng tệp gốc ở trang Tệp nguồn với dòng đó được lọc sẵn. Ví dụ từ cảnh báo gian lận ở CN8 tuần 01/07/2024, người dùng đi tới hóa đơn POS-08-03-20240701-00065 do thu ngân NV0093 thu tiền mặt lúc 14:13 và hủy 14,8 phút sau, nằm trong tệp `pos/POS-08/pos_export_2024-07-01.json`.

IMAGE: figures/h4_5_truy_vet.png || Hình 4.8. Phần kết luận và đề xuất xử lý của trang Truy vết nguyên nhân: CN2, tuần 06/05/2024 (tập phát triển) || 12.5 || Ảnh chụp giao diện hệ thống

### 4.8.3. Các trang dữ liệu và kiểm chứng

Trang Vận hành hằng ngày (Hình 4.9) cho phép đưa dữ liệu của một hoặc bảy ngày kinh doanh mới vào môi trường vận hành bằng cách kích hoạt DAG nguồn, rồi theo dõi từng bước: số bản ghi kéo qua API, tệp mới, số dòng nạp, cửa chặn chất lượng, kiểm thử dbt, cảnh báo mới và lượt đưa sang kho phục vụ; bước gặp sự cố nhưng không chặn các bước sau, như API không phản hồi, hiện ở mức cảnh báo, tách khỏi mức lỗi. Trang Chất lượng dữ liệu tổng hợp kết quả cửa chặn, kiểm thử dbt, đối soát số dòng, bảng cách ly và độ mới từng nguồn; trang Mô hình và phả hệ vẽ phả hệ và lược đồ hình sao từ siêu dữ liệu dbt nên luôn khớp với mã nguồn.

IMAGE: figures/h4_6_van_hanh.png || Hình 4.9. Trang Vận hành hằng ngày sau khi đưa vào bảy ngày kinh doanh mới (môi trường vận hành) || 13 || Ảnh chụp giao diện hệ thống

Trang Bộ mô phỏng (Hình 4.10), thuộc nhóm Kiểm chứng, đặt con số sự thật của một ngày cạnh những gì từng hệ thống ghi lại, lấy từ kho đúng như đường ống nhìn thấy. Ở ngày 11/05/2024 của CN2, giữa kịch bản thiếu nhân sự, 216 đơn tại quầy khớp với số hóa đơn POS còn hiệu lực và 92 đơn App khớp với App, nhưng 38 khách bỏ về không được hệ thống nào ghi nhận, và 5 đơn sàn không được nhập POS lộ ra đúng bằng phần thiếu ở hai dòng GrabFood, ShopeeFood. Trang này đọc đáp án nên chỉ dùng để trình bày và kiểm chứng. Ngoài ra, ứng dụng có một trang trợ lý phân tích thử nghiệm dùng mô hình ngôn ngữ lớn gọi các hàm truy vấn có sẵn; phần này chưa được đánh giá nên không thuộc kết quả của khóa luận.

IMAGE: figures/h4_7_mo_phong.png || Hình 4.10. Trang Bộ mô phỏng: sự thật của một ngày đặt cạnh những gì các hệ thống nguồn ghi lại (CN2, 11/05/2024, tập phát triển) || 12.5 || Ảnh chụp giao diện hệ thống

## 4.9. Điều phối và vận hành tăng dần

### 4.9.1. Đóng gói và triển khai

Tệp `docker-compose.yml` dựng năm dịch vụ là Airflow, PostgreSQL, Metabase, ứng dụng và API giả lập phía nguồn; toàn bộ hệ thống bật bằng một lệnh `docker compose up -d`. Hình 4.11 là sơ đồ triển khai: mọi thành phần chạy trong container trên cùng một máy, giao tiếp qua mạng nội bộ của Docker; kho DuckDB nằm trong thư mục dự án, gắn vào container airflow để ghi và vào container app để đọc. Cấu hình cho máy chủ trong `deploy/` thêm một container Caddy đứng trước để cấp HTTPS và chuyển tiếp tới ba giao diện web; các cổng khác, kể cả PostgreSQL và API giả lập, không mở ra ngoài.

IMAGE: figures/h4_trien_khai.png || Hình 4.11. Sơ đồ triển khai của nền tảng trên Docker Compose || 13 || Đề xuất của nghiên cứu

### 4.9.2. Hai DAG và cơ chế kích hoạt theo dữ liệu

Tệp `airflow/dags/fastfat_pipeline.py` khai báo hai DAG như Hình 3.7. Bước ghi dữ liệu của DAG nguồn khai báo đầu ra là một Dataset, và trang Tải tệp lên cũng báo cập nhật Dataset này; DAG đường ống dùng lịch `DatasetOrTimeSchedule` nên chạy khi Dataset cập nhật hoặc vào đầu mỗi giờ. Bước `extract` gọi bộ kết nối API, và nếu API không phản hồi thì kết thúc ở trạng thái cảnh báo để các bước sau vẫn xử lý nguồn tệp. Bước `check` so các tệp với nhật ký nạp theo đường dẫn, kích thước và thời điểm sửa; không có tệp mới thì thoát với mã 99 và Airflow đánh dấu các bước sau là bỏ qua thay vì lỗi; tệp vừa được ghi trong 5 giây thì chờ thêm vì nguồn có thể còn đang ghi. Mỗi bước gọi `pipeline/run_daily.py --step <tên bước>`, nên cùng chương trình chạy được cả ngoài Airflow. Một lượt từng thất bại vì đúng lúc ghi nhật ký, ứng dụng đang mở kho để đọc; từ đó mọi chỗ đường ống mở kho đều chờ và thử lại tối đa 120 giây khi gặp lỗi khóa tệp.

### 4.9.3. Một lượt chạy với dữ liệu ngày mới

Môi trường vận hành, tức tập `live`, là bản sao của tập phát triển dùng riêng cho vận hành hằng ngày để hai tập đánh giá không bị thay đổi. Để minh họa luồng từ dữ liệu mới đến cảnh báo, môi trường này có hai sự cố từ ngày 23/09/2024 chỉ phục vụ trình diễn: thiếu nhân sự ca tối ở CN3 và ShopeeFood tính hoa hồng 27% ở CN1. Bảng 4.10 là nhật ký một lượt thật trong Docker: người dùng bấm gửi bảy ngày kinh doanh 23–29/09/2024 ở trang Vận hành hằng ngày, rồi Airflow tự kích hoạt đường ống mà không cần thao tác nào khác.

TABLE: Bảng 4.10. Một lượt đường ống kích hoạt theo dữ liệu mới (môi trường vận hành, bảy ngày, nhật ký `ops.pipeline_runs`)
WIDTHS: 2,1.6,8
| Bước | Thời gian | Kết quả ghi nhận |
| extract | 8,6 giây | POS đám mây: 7 ngày, 10.365 hóa đơn, 55 trang, 6 lần thử lại; App: 7 ngày, 3.880 đơn, 24 trang, 1 lần thử lại |
| check | 22,5 giây | 236 tệp mới: 77 POS, 7 App, 77 chấm công, 66 nhập kho, 7 thời tiết, 1 GrabFood, 1 ShopeeFood |
| ingest | 33,8 giây | 236 tệp, 18.798 dòng mới, 0 tệp lỗi |
| quality | 3,4 giây | 15/15 mục đạt |
| dbt | 21,0 giây | 211/211 bước đạt |
| detect | 2,5 giây | Tuần 23/09/2024: 2 cảnh báo, CN1 P1a điểm 6,0; CN3 P3 điểm 4,8 |
| publish | 8,6 giây | 22 bảng, 1.500.446 dòng sang PostgreSQL, đối soát số dòng khớp |

Từ lúc bấm nút đến khi dữ liệu lên kho phục vụ mất 146 giây; các lượt khác đo được từ 152 đến 199 giây. Phần lớn thời gian là liệt kê và đọc tệp qua thư mục gắn từ Windows vào Docker; để giảm phần này, bước nạp chỉ băm lại tệp có kích thước hoặc thời điểm sửa khác lần trước, nhờ đó nạp một ngày trong Docker giảm từ 74 xuống 20 giây. Hai cảnh báo trùng đúng hai sự cố đã cài, với số liệu y hệt khi POS đám mây và App còn đi đường tệp; riêng CN1 bị thu thừa 528.250 đồng.

## 4.10. Tiểu kết chương

Các thành phần thiết kế ở Chương 3 đều đã được hiện thực và chạy được trên một máy tính cá nhân. Bộ mô phỏng tạo đúng tác động của mười hai kịch bản; tầng thu thập nhận dữ liệu qua ba kênh và từ chối tệp sai hợp đồng; từ Bronze tới Gold không dòng nào bị loại im lặng, 158 kiểm thử dbt và 89 kiểm thử mã nguồn đều đạt; một lượt bảy ngày đi từ dữ liệu nguồn đến cảnh báo trên kho phục vụ mà không cần thao tác tay. Chương 5 đánh giá định lượng các kết quả này.
