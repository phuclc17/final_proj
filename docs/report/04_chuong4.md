# CHƯƠNG 4. HIỆN THỰC HỆ THỐNG

Chương này trình bày việc cài đặt các thành phần đã thiết kế ở Chương 3 và kết quả kiểm chứng từng thành phần, theo đúng thứ tự dòng dữ liệu: bộ mô phỏng, tầng thu thập và Bronze, Silver, Gold, lớp chỉ số, bộ phát hiện, kho phục vụ, ứng dụng và điều phối. Các số liệu trong chương đều được đo trực tiếp trên hệ thống và có thể tái lập bằng các lệnh ở Phụ lục E.

## 4.1. Môi trường và cấu trúc mã nguồn

TABLE: Bảng 4.1. Môi trường hiện thực
WIDTHS: 4,8
| Thành phần | Phiên bản, cấu hình |
| Máy tính | AMD Ryzen 5 5600H, RAM 16 GB, Windows 11 Home |
| Ngôn ngữ | Python 3.12.4 (môi trường ảo riêng của dự án) |
| Xử lý dữ liệu | pandas 3.0.6, NumPy 2.5.3, PyArrow 25.0.1, openpyxl 3.1.5 |
| Kho dữ liệu | DuckDB 1.5.6 |
| Biến đổi dữ liệu | dbt-core 1.12.5, dbt-duckdb 1.11.0 |
| Ứng dụng | Streamlit 1.65.0 |
| Kho phục vụ | PostgreSQL 16.15 |
| Báo cáo kinh doanh | Metabase 0.58.36.1 |
| Điều phối | Apache Airflow 2.10.5, Docker Compose (Docker 29.4) |
| API nguồn giả lập | FastAPI 0.143.3, Uvicorn 0.34.0 |

Mã nguồn được tổ chức theo đúng ranh giới kiến trúc; sơ đồ đầy đủ ở Hình E.1 của Phụ lục E. Bộ mô phỏng, vốn đóng vai các hệ thống nguồn, tách biệt hoàn toàn với đường ống dữ liệu. Đáp án nằm trong thư mục `ground_truth/` của từng tập dữ liệu và chỉ được đọc bởi phần kiểm chứng, phần đánh giá và trang Bộ mô phỏng của ứng dụng. Đường ống trong `pipeline/`, `dbt/` và bộ phát hiện trong `analytics/detect.py` không đọc thư mục này.


## 4.2. Hiện thực bộ mô phỏng

### 4.2.1. Tổ chức chương trình

Bộ mô phỏng được viết bằng Python, gồm năm mô-đun chính. Mô-đun `config.py` tập trung toàn bộ tham số nghiệp vụ (Bảng 3.10 và mục 3.3.4), nhờ đó mọi giả định đều có thể truy vết và điều chỉnh tại một nơi. Mô-đun `world.py` chứa lớp `World` lưu trạng thái của thế giới: tồn kho từng nguyên liệu ở từng chi nhánh, lịch sử tiêu hao bảy ngày, điểm đánh giá và hệ số thứ hạng trên sàn, lịch sử mua của khách hàng ứng dụng, bộ sinh số ngẫu nhiên. Hàm `simulate_day()` của lớp này thực hiện tuần tự cho mỗi chi nhánh: giao hàng buổi sáng, xếp ca và sinh lượt quẹt thẻ, sinh nhu cầu theo kênh và giờ, tính tải bếp và sinh từng đơn hàng với kết quả phục vụ, tính tiêu hao và cập nhật tồn kho, kiểm kê khi đến kỳ, cộng dồn số liệu đối soát tuần. Mô-đun `views.py` chuyển các sự kiện thật thành bản ghi theo định dạng của từng hệ thống nguồn, và là nơi tạo ra các lỗi dữ liệu ở Bảng 3.11. Mô-đun `exporters.py` ghi tệp JSON, CSV và Excel; thư viện openpyxl được dùng để tạo cả các phiếu có dòng tiêu đề, ô gộp và định dạng số. Mô-đun `run.py` điều khiển một lần chạy: nạp trạng thái đã lưu, sinh số ngày yêu cầu, ghi tệp và lưu lại trạng thái. Các kịch bản sự cố được khai báo trong tệp JSON riêng của từng tập ở thư mục `simulator/scenarios/`.

### 4.2.2. Sinh dữ liệu tăng dần và khả năng tái lập

Sau mỗi lần chạy, toàn bộ đối tượng `World`, kể cả trạng thái của bộ sinh số ngẫu nhiên, được lưu lại. Lần chạy sau tiếp tục từ đúng trạng thái đó. Vì vậy sinh 182 ngày một lần cho kết quả giống hệt sinh 181 ngày rồi thêm một ngày. Nhờ tính chất này, hệ thống vận hành như một doanh nghiệp đang hoạt động: mỗi ngày bộ mô phỏng thêm tệp của ngày mới vào thư mục nguồn và đường ống xử lý tăng dần. Mỗi tập kịch bản có hạt giống ngẫu nhiên cố định, là 2024 với tập phát triển và 777 với tập kiểm tra, nên toàn bộ dữ liệu tái lập được từ mã nguồn. Thời gian sinh khoảng một giây cho một ngày dữ liệu của 11 chi nhánh; sinh toàn bộ 182 ngày mất khoảng 3,5 phút.

Trước khi sinh dữ liệu chính thức, các phân phối số món mỗi đơn, số lượng mỗi dòng món, độ tập trung món bán chạy và độ dao động theo ngày được hiệu chỉnh từ bộ dữ liệu giao dịch thật The Bread Basket bằng chương trình `simulator/calibrate_public.py` theo mục 3.3.8. Kết quả hiệu chỉnh được lưu trong tệp `data/public_reference/calibration_report.json` cùng dữ liệu gốc đã tải về, để có thể kiểm tra và tái lập.

### 4.2.3. Dữ liệu nguồn được tạo ra

TABLE: Bảng 4.2. Khối lượng dữ liệu nguồn của tập phát triển (182 ngày, 11 chi nhánh)
WIDTHS: 4,2,2,5
| Hệ thống nguồn | Số tệp | Dung lượng | Số bản ghi |
| POS | 2.002 | 474,2 MB | 339.989 hóa đơn |
| Ứng dụng riêng | 182 | 106,9 MB | 96.779 đơn |
| GrabFood | 26 | < 0,1 MB | 286 dòng chi nhánh × tuần |
| ShopeeFood | 26 | 0,2 MB | 286 dòng chi nhánh × tuần |
| Sổ nhập kho | 1.699 | 9,6 MB | 18.424 dòng (cả dòng tổng cộng, chữ ký) |
| Phiếu kiểm kê | 143 | 0,9 MB | 3.146 dòng |
| Máy chấm công | 2.002 | 2,6 MB | 42.375 lượt quẹt |
| Thời tiết | 182 | < 0,1 MB | 182 ngày |
| Danh mục trụ sở | 11 | < 0,1 MB | 8 ảnh chụp ban đầu và 3 ảnh chụp cập nhật (giá món ở trụ sở và ứng dụng, thông tin nhân viên) |

Về nghiệp vụ, tập phát triển chứa 445.153 lượt nhu cầu đặt món, trong đó 435.279 đơn được phục vụ với tổng giá trị khoảng 38,67 tỷ đồng và giá trị trung bình 88.844 đồng mỗi đơn. Trong số đơn được phục vụ, 227.182 đơn tại quầy, 93.664 đơn qua ứng dụng riêng, 68.742 đơn GrabFood và 45.691 đơn ShopeeFood. Phần nhu cầu không được phục vụ gồm 1.149 lượt khách tại quầy bỏ về, 2.096 đơn bị cửa hàng hủy và 4.797 đơn bị khách hủy. Tập kiểm tra có 384.918 đơn được phục vụ, khoảng 34,15 tỷ đồng.

IMAGE: figures/h4_2_du_lieu_tho.png || Hình 4.1. Ví dụ dữ liệu thô của các hệ thống nguồn, trích nguyên văn từ tệp của tập phát triển || 16

### 4.2.4. Kiểm chứng bộ mô phỏng

Trước khi dùng dữ liệu để xây dựng và đánh giá đường ống, cần kiểm chứng rằng bộ mô phỏng tạo ra đúng các tác động đã thiết kế. Chương trình `validate.py` được phép đọc đáp án vì chỉ phục vụ bộ mô phỏng; chương trình đo tác động của từng kịch bản bằng cách so sánh giai đoạn sự cố với bốn tuần trước đó của cùng chi nhánh. Với kịch bản thiếu nhân sự, chương trình còn so sánh với các chi nhánh cùng hạng để loại bỏ biến động chung. Ngoài chương trình này, trang Bộ mô phỏng của ứng dụng cho xem trực quan từng ngày, đặt sự thật của thế giới mô phỏng cạnh những gì từng hệ thống nguồn ghi lại; trang này được trình bày ở mục 4.9.3.

TABLE: Bảng 4.3. Kết quả kiểm chứng kịch bản trên tập phát triển
WIDTHS: 2,10
| Kịch bản | Tác động đo được |
| S1 (P1a) | Hoa hồng GrabFood của CN4 bị tính 30% trong đúng ba tuần bắt đầu 13/5, 20/5, 27/5 |
| S2 (P1b) | Tỷ lệ đơn sàn không có trong POS của CN6 tăng từ 2,6% lên 15,5%; giá trị đơn mất dấu vết 8,52 triệu đồng |
| S3 (P2) | Giá trị hao hụt vượt định mức mỗi ngày của CN7 tăng từ khoảng 119 nghìn lên 801 nghìn đồng |
| S4 (P3) | Nhân viên bếp ca tối của CN2 giảm từ 3,6 xuống 1,8 người; tải bếp đỉnh tăng từ 0,80 lên 1,67; thời gian chuẩn bị trung bình tăng từ 15,5 lên 20,4 phút; khách bỏ về tăng từ 1,2 lên 16,9 lượt/ngày; đơn bị cửa hàng hủy tăng từ 1,9 lên 16,6 đơn/ngày; hệ số thứ hạng GrabFood giảm từ 0,98 xuống 0,90 trong kỳ và 0,84 trong ba tuần sau. Doanh thu của CN2 thấp hơn mức thay đổi của chi nhánh cùng hạng 16,9% trong kỳ và 6,7% trong ba tuần sau kỳ |
| S5 (P4) | Giá trị nguyên liệu bị mất tại CN9 trong 14 ngày khoảng 0,83 triệu đồng |
| S6 (P5) | Thu ngân NV0093 của CN8 hủy 60 hóa đơn tiền mặt sau khi thu tiền, tổng 5,31 triệu đồng |

TABLE: Bảng 4.4. Kết quả kiểm chứng kịch bản trên tập kiểm tra
WIDTHS: 2,10
| Kịch bản | Tác động đo được |
| H1 (P1a) | Hoa hồng ShopeeFood của CN10 bị tính 26% trong hai tuần bắt đầu 5/8, 12/8 |
| H2 (P1b) | Tỷ lệ đơn sàn không có trong POS của CN3 tăng từ 3,2% lên 16,4%; giá trị mất dấu vết 18,70 triệu đồng |
| H3 (P2) | Hao hụt vượt định mức mỗi ngày của CN1 tăng từ khoảng 101 nghìn lên 533 nghìn đồng |
| H4 (P3) | Nhân viên bếp ca tối của CN8 giảm từ 4,6 xuống 3,0 người; tải bếp đỉnh tăng từ 0,66 lên 0,99; thời gian chuẩn bị tăng từ 13,0 lên 16,0 phút; khách bỏ về tăng từ 0,1 lên 5,9 lượt/ngày; đơn bị cửa hàng hủy tăng từ 1,3 lên 4,0 đơn/ngày. Doanh thu chỉ thấp hơn chi nhánh cùng hạng 1,4% trong kỳ và 0,9% trong ba tuần sau |
| H5 (P4) | Giá trị nguyên liệu bị mất tại CN5 trong 14 ngày khoảng 0,18 triệu đồng |
| H6 (P5) | Thu ngân NV0126 của CN10 hủy 29 hóa đơn tiền mặt sau khi thu tiền, tổng 2,62 triệu đồng |

TABLE: Bảng 4.5. Các biến động bình thường đo được (ngày không có sự cố)
WIDTHS: 5,3,3
| Yếu tố | Tập phát triển | Tập kiểm tra |
| Doanh thu cuối tuần so với ngày thường | +25,0% | +25,4% |
| Doanh thu ngày lễ so với ngày thường | +22,7% | +21,2% |
| Số đơn tại quầy ngày mưa so với ngày khô | −25,9% | −25,5% |
| Số đơn giao hàng ngày mưa so với ngày khô | +22,4% | +21,1% |
| Giá trị trung bình mỗi đơn trước và sau điều chỉnh giá 1/6 | 87.450 → 90.014 đồng | 87.173 → 90.141 đồng |

Cả mười hai kịch bản đều tạo ra tác động đúng chỗ, đúng thời điểm và đúng chiều. Kịch bản thiếu nhân sự tái hiện đủ chuỗi nhân quả đã thiết kế: thời gian chuẩn bị tăng, khách bỏ về và cửa hàng hủy đơn, sau đó thứ hạng trên sàn giảm và doanh thu tiếp tục thấp nhiều tuần sau khi sự cố kết thúc. Kịch bản H4 nhẹ hơn tạo ra tín hiệu vận hành rõ nhưng doanh thu gần như không đổi so với chi nhánh cùng hạng, đúng với thực tế là không phải lần thiếu người nào cũng gây mất doanh thu rõ rệt. Trong khi đó, các yếu tố bình thường tạo ra biến động doanh thu bằng hoặc lớn hơn tác động của sự cố. Ngày lễ làm doanh thu tăng khoảng 21–23%, ngày mưa làm số đơn mỗi kênh thay đổi khoảng 21–26%. Vì vậy, như câu hỏi RQ3 đặt ra, phương pháp nào chỉ nhìn độ lớn biến động sẽ cảnh báo sai rất nhiều.

Thiệt hại của các kịch bản thất thoát kho và gian lận tại quầy chỉ từ khoảng 0,2 đến 5,3 triệu đồng, nhỏ so với doanh thu hàng trăm triệu đồng mỗi tuần. Mức này được chọn có chủ đích, vì ngoài thực tế thất thoát và gian lận thường nhỏ lẻ, kéo dài và không thể phát hiện bằng chỉ số tổng hợp.

## 4.3. Hiện thực tầng thu thập và Bronze

### 4.3.1. Kênh thu thập và hợp đồng dữ liệu

Danh mục nguồn và hợp đồng dữ liệu được khai báo một lần trong `pipeline/contracts.py` và dùng chung cho kênh tải lên, bước nạp và trang Kết nối nguồn. Mỗi nguồn có hệ thống, kênh ngoài thực tế, kênh trong hệ thống này, tần suất, định dạng, vị trí chuẩn và các cột hoặc khóa bắt buộc. Bảng 4.6 tóm tắt cách từng nguồn đến.

TABLE: Bảng 4.6. Kênh thu thập của từng nguồn
WIDTHS: 2.4,5,4.6,2.2
| Nguồn | Ngoài thực tế thường đến bằng | Trong hệ thống này | Tần suất |
| POS tại quầy | API của phần mềm POS đám mây; POS cài tại máy xuất tệp mỗi đêm | 8 chi nhánh dùng POS đám mây: bộ kết nối kéo qua API; CN5, CN7, CN10 dùng POS cài tại máy: tệp JSON xuất mỗi đêm | Hằng ngày |
| App đặt hàng riêng | API hoặc bản sao cơ sở dữ liệu của chính công ty | Bộ kết nối kéo qua API | Hằng ngày |
| GrabFood, ShopeeFood | Kế toán tải báo cáo đối soát từ cổng đối tác hoặc nhận qua email | Tệp CSV, Excel đẩy vào vùng tiếp nhận hoặc tải lên | Hằng tuần |
| Sổ nhập kho (hai mẫu), phiếu kiểm kê | Quản lý cửa hàng điền Excel, gửi email, Drive hoặc Zalo | Tệp Excel đẩy vào vùng tiếp nhận hoặc tải lên | Mỗi lần nhập; hai tuần một lần |
| Máy chấm công | Phần mềm đi kèm máy vân tay, khuôn mặt xuất CSV | Tệp CSV đẩy vào vùng tiếp nhận | Hằng ngày |
| Thời tiết, danh mục trụ sở | API dịch vụ thời tiết; tệp xuất khi danh mục thay đổi | Tệp JSON, CSV đẩy vào vùng tiếp nhận | Hằng ngày; khi thay đổi |

Hàm nhận dạng đọc nội dung tệp chứ không dựa vào tên. Từ khóa JSON, dòng tiêu đề cột của CSV hay dòng tiêu đề phiếu của Excel, hàm suy ra nguồn, chi nhánh và ngày dữ liệu, từ đó ra vị trí chuẩn trong vùng tiếp nhận. Tệp CSV được đọc thử lần lượt với các bảng mã UTF-8, UTF-16, Windows-1258 và Windows-1252, vì phần mềm cũ hay xuất UTF-16. Tệp bị từ chối khi thiếu cột bắt buộc, khi một tệp POS chứa hóa đơn của nhiều chi nhánh, hoặc khi giống một nguồn nhưng sai định dạng.

Kênh tải lên trong `pipeline/intake.py` cho bốn kết quả: đã nhận, thay bản cũ, trùng nên bỏ qua, và từ chối kèm lý do. Tệp được ghi ra tệp tạm rồi đổi tên trong một thao tác, nên bước nạp không bao giờ đọc phải tệp ghi dở; mọi lần gửi được ghi vào nhật ký tiếp nhận. Sau khi nhận, ứng dụng báo Airflow cập nhật Dataset nguồn để đường ống chạy ngay. Hình 4.2 là kết quả gửi chín tệp mẫu trong `samples/tep_mau/`, gồm cả các trường hợp sai: báo cáo GrabFood lưu nhầm thành Excel, tệp chấm công thiếu cột, bảng lương gửi nhầm, tệp của một máy POS chưa khai báo.

IMAGE: figures/h4_tai_len.png || Hình 4.2. Trang Tải tệp lên sau khi gửi chín tệp mẫu (môi trường vận hành) || 16

Trang Kết nối nguồn (Hình 4.3) cho người vận hành thấy mỗi nguồn đã đến tới ngày nào, có chậm so với nhịp của nó không, trạng thái của bộ kết nối API và các tệp đang bị từ chối hoặc không nhận dạng cần người xử lý.

IMAGE: figures/h4_ket_noi.png || Hình 4.3. Trang Kết nối nguồn sau một lượt kéo bảy ngày qua API (môi trường vận hành) || 16

### 4.3.2. API nguồn và bộ kết nối

Để đường API được kiểm chứng như ngoài thực tế, phía nguồn có một dịch vụ API riêng viết bằng FastAPI trong `source_api/app.py`, chạy trong Docker ở cổng 8600. Với môi trường vận hành, bộ mô phỏng ghi hóa đơn POS của tám chi nhánh dùng POS đám mây và đơn App vào kho riêng của phần mềm nguồn thay vì vùng tiếp nhận; bên ngoài chỉ lấy được dữ liệu này qua API. Dịch vụ có bốn điểm cuối: danh sách ngày kinh doanh và danh sách bản ghi theo ngày, cho POS và App. Danh sách bản ghi được phân trang, tối đa 500 bản ghi mỗi trang, kèm tổng số bản ghi để bên gọi đối chiếu. Mọi lời gọi cần mã xác thực dạng Bearer. Như API thật, dịch vụ giới hạn 20 lượt gọi mỗi giây, vượt thì trả mã 429 kèm thời gian chờ, và trả lỗi tạm thời 503 với xác suất 8%. Hai tập đánh giá vẫn đi đường tệp như trước để kết quả đã chốt không đổi.

Bộ kết nối `pipeline/extract.py` dùng thư viện HTTP chuẩn của Python, không thêm phụ thuộc vào môi trường của Airflow. Mỗi lượt, với từng hệ thống, nó hỏi danh sách ngày, lấy các ngày sau mốc và lấy lại ngày mốc, mỗi ngày lấy đủ các trang 200 bản ghi rồi so tổng với số API báo. Khi gặp lỗi 503, 429 hoặc mất kết nối, một lời gọi được thực hiện tối đa sáu lần, giữa các lần chờ 0,5; 1; 2; 4; 8 giây hoặc theo thời gian chờ API yêu cầu; mã 401, 403 dừng ngay. Dữ liệu được ghi vào vùng tiếp nhận đúng định dạng tệp của nguồn: hóa đơn POS chia theo máy POS dựa vào mã máy trong hóa đơn, đơn App bọc trong lớp vỏ ghi thời điểm kéo. Tệp có nội dung không đổi so với bản đang có thì không ghi lại, nên lấy lại ngày mốc không làm đường ống nạp lại. Mốc được dời sau từng ngày và lưu trong `landing/api_connector.json` cùng thống kê của lượt gồm số trang, số bản ghi, số lần gọi, số lần thử lại và kết quả. Lần đầu kết nối, mốc lấy bằng ngày cuối cùng mà mọi máy POS đều đã có dữ liệu trong vùng tiếp nhận.

TABLE: Bảng 4.7. Một lượt kéo bảy ngày kinh doanh 23–29/09/2024 qua API (môi trường vận hành, chạy trong Airflow)
WIDTHS: 3,1.4,1.8,1.4,1.6,1.6,1.4,1.8
| Hệ thống | Số ngày | Bản ghi | Trang | Lần gọi | Thử lại | Tệp ghi | Thời gian |
| POS đám mây (8 chi nhánh) | 7 | 10.365 | 55 | 62 | 6 | 56 | 7,2 giây |
| App đặt hàng | 7 | 3.880 | 24 | 26 | 1 | 7 | 1,2 giây |

Bảy lần thử lại trong Bảng 4.7 là do lỗi 503 ngẫu nhiên của API và đều thành công ở lần sau. Vì lỗi là ngẫu nhiên, số lần gọi và thử lại thay đổi giữa các lượt, còn số ngày, bản ghi, trang và tệp ghi giống nhau ở mọi lượt. Để kiểm chứng đường API không làm thay đổi dữ liệu, 56 tệp POS trong vùng tiếp nhận được so với tệp gốc trong kho của phần mềm: cả 56 giống nhau đến từng byte; bảy tệp App có cùng mảng đơn hàng. Vì vậy dữ liệu từ Bronze trở đi giống hệt khi đi đường tệp, và lượt trình diễn cho đúng kết quả như trước khi có API (mục 4.10.3).

Lần chạy thật đầu tiên lộ ra một lỗi của bộ kết nối: mốc khởi tạo lấy ngày mới nhất trên mọi thư mục POS, trong khi ba chi nhánh POS cài tại máy đã có tệp tới 29/09, nên mốc nhảy qua sáu ngày 23–28/09 của POS đám mây. Lỗi được sửa bằng cách lấy ngày nhỏ nhất trong các ngày mới nhất của từng máy, kèm một kiểm thử hồi quy; lượt chạy lỗi đó vô tình trở thành một phép thử thiếu dữ liệu hàng loạt (mục 5.2.4). Bộ kết nối có 10 kiểm thử tự động, bao gồm phân trang, dữ liệu đến trễ của ngày mốc, thử lại khi lỗi tạm thời, giới hạn tần suất, sai mã xác thực và làm tiếp đúng chỗ sau lỗi giữa chừng.

### 4.3.3. Chương trình nạp dữ liệu

Tầng Bronze được hiện thực trong chương trình `pipeline/ingest.py`. Danh sách nguồn được khai báo như một bảng cấu hình gồm tên bảng Bronze đích, mẫu đường dẫn tệp và bộ đọc; thêm một nguồn mới chỉ cần thêm một dòng cấu hình. Bốn bộ đọc được xây dựng: JSON dạng danh sách cho POS, JSON có vỏ bọc API cho App với phần vỏ lưu ở cột `_envelope`, CSV và Excel. Mọi giá trị được giữ nguyên dạng chuỗi hoặc JSON nguyên văn; chỉ tên cột được chuyển sang dạng an toàn cho SQL, ví dụ “Doanh thu món (VNĐ)” thành `doanh_thu_mon_vnd`. Bộ đọc Excel tự xác định dòng tiêu đề cột là dòng đầu tiên có từ ba ô có giá trị; các dòng phía trên như tên phiếu, chi nhánh, ngày, người lập được giữ trong các cột `_doc_line_k`. Khi nguồn xuất hiện thêm cột mới, chương trình tự thêm cột vào bảng Bronze thay vì báo lỗi, để đường ống chịu được việc phần mềm nguồn được nâng cấp.

Trước khi đọc, mỗi tệp được kiểm tra theo hợp đồng của nguồn tương ứng với thư mục chứa nó, vì tệp có thể được thả thẳng vào vùng tiếp nhận mà không qua trang tải lên. Tệp sai hợp đồng có trạng thái `rejected`, kể cả tệp có tên không khớp nội dung như tệp POS ngày 23/09 bị chép thành tên ngày 30/09; tệp ngoài mọi mẫu đường dẫn có trạng thái `unrecognized`; tệp không đọc được có trạng thái `failed`. Tệp POS rỗng là hợp lệ vì cửa hàng có thể nghỉ hoặc mất điện, nhưng cửa chặn chất lượng coi như chi nhánh đó thiếu dữ liệu.

### 4.3.4. Kết quả nạp

Lần nạp đầu tiên của tập phát triển xử lý 6.273 tệp thành 17 bảng Bronze với khoảng 502 nghìn dòng, không có tệp lỗi. Số dòng mỗi bảng bằng đúng số bản ghi của nguồn tương ứng ở Bảng 4.2; riêng sổ nhập kho được nạp vào hai bảng theo hai mẫu, gồm 13.951 dòng mẫu A dạng phiếu và 4.473 dòng mẫu B dạng bảng, còn danh mục trụ sở được nạp vào 8 bảng `master_*` với 537 dòng. Bronze giữ nguyên mọi khác biệt của dữ liệu gốc, như hai định dạng thời gian và tiền của hai phiên bản POS, dòng “Tổng cộng” trong sổ kho mẫu A, giờ UTC của App; việc xử lý thuộc về tầng Silver ở mục 4.4.2.

### 4.3.5. Kiểm chứng tính lũy đẳng và nạp tăng dần

TABLE: Bảng 4.8. Kết quả kiểm chứng tính lũy đẳng và nạp tăng dần
WIDTHS: 5,3,3,3
| Lần chạy | Tệp mới | Dòng mới | Thời gian |
| Nạp lần đầu (182 ngày) | 6.273 | ≈ 502.000 | 80 giây |
| Chạy lại ngay, không có tệp mới | 0 | 0 | 5 giây, chỉ tính và so mã băm |
| Sau khi bộ mô phỏng thêm một ngày mới | 35 | 2.561 | 5 giây |

Chạy lại chương trình nạp khi không có dữ liệu mới không tạo ra dòng trùng nào. Khi bộ mô phỏng thêm ngày 09/9/2024, chương trình chỉ nạp đúng 35 tệp của ngày đó, gồm 11 tệp POS, 1 tệp ứng dụng, 11 tệp chấm công, 11 phiếu nhập kho và 1 tệp thời tiết, trong 5 giây so với 80 giây khi nạp toàn bộ. Kết quả này đáp ứng yêu cầu NFR2 và cho thấy chi phí xử lý hằng ngày tỷ lệ với lượng dữ liệu mới, không tăng theo kích thước lịch sử.

## 4.4. Hiện thực tầng Silver

### 4.4.1. Tổ chức dự án dbt

Tầng Silver và Gold được hiện thực trong một dự án dbt ở thư mục `dbt/`, chạy bằng chương trình `pipeline/run_dbt.py`. Chương trình này chọn tệp kho DuckDB của tập dữ liệu cần chạy và tách riêng thư mục kết quả, nhật ký của từng tập, nhờ đó tập phát triển và tập kiểm tra được dựng độc lập bằng cùng một mã nguồn. Dự án gồm 50 mô hình, 3 bảng hạt giống và 158 kiểm thử, tổng cộng 211 bước trong một lần `dbt build`. Các mô hình được chia theo ba lược đồ:

- `silver_work` chứa 10 mô hình trung gian và 3 bảng hạt giống: ánh xạ mã chi nhánh của sáu hệ thống, biến thể tên nguyên liệu và ngày lễ năm 2024. Mô hình trung gian có bốn loại: `parsed_` giải mã JSON của POS và App, chạy theo chế độ tăng dần để mỗi ngày chỉ giải mã bản ghi mới; `base_` đọc Bronze, ép kiểu và gắn mã lỗi chất lượng; `checked_` áp các quy tắc cần so với lịch sử như số lượng bất thường trong sổ kho; `map_` giải quyết định danh.
- `silver` chứa 20 bảng `stg_` đã sạch theo từng nguồn, bảng cách ly `silver_quarantine` và bảng đối soát `silver_row_reconciliation`.
- `gold` chứa 13 bảng chiều và sự kiện cùng 5 bảng chỉ số, trình bày ở mục 4.5 và 4.6.

Mỗi nguồn đi qua cùng một khuôn: `base_` gắn cột `dq_issue` cho dòng vi phạm, bảng `stg_` chỉ lấy dòng có `dq_issue` rỗng, bảng cách ly lấy phần còn lại. Không dòng nào bị xóa im lặng. Số liệu ở mục 4.4 và 4.5 được đo trên kho của tập phát triển, gồm 182 ngày chính và ngày 09/09/2024 được thêm khi kiểm chứng nạp tăng dần ở mục 4.3.5.

### 4.4.2. Xử lý các lỗi dữ liệu

Các quy tắc ở Bảng 3.14 được hiện thực đúng theo hai hướng: lỗi kỹ thuật bị tách khỏi dữ liệu, còn tín hiệu nghiệp vụ được giữ lại kèm cờ. Hai phiên bản POS được nhận diện theo từng hóa đơn rồi đưa về một lược đồ chung. Chẳng hạn, hóa đơn đầu tiên ngày 12/4 của CN7, dùng bản 2.8, ghi thời gian “2024-04-12T07:10:59” và tổng tiền là chuỗi “89.000” ở cột `grand_total`, còn hóa đơn của CN8, dùng bản 3.2, ghi “12/04/2024 07:11:22” và số 90000 ở cột `total_paid`. Hóa đơn hủy và hoàn tiền được giữ lại, gắn cờ và tính số phút từ lúc thanh toán đến lúc hủy, vì đây là dữ liệu đầu vào của bộ phát hiện gian lận. Đơn App lưu giờ UTC được đổi sang giờ Việt Nam trước khi xác định ngày và ca; nếu không đổi, mọi đơn ca tối sẽ rơi vào ca sáng. Ở sổ nhập kho, số lượng lớn hơn 20 lần trung vị của cùng nguyên liệu bị cách ly với mã `nghi_go_gam_vao_cot_kg`, ví dụ cà chua 2.300 kg trong khi trung vị là 2,2 kg. Ở chấm công, lượt quẹt cùng loại lặp lại trong vòng 5 phút bị cách ly với mã `quet_trung`; ca thiếu lượt ra được gắn cờ `is_missing_checkout` mà không tự gán số giờ ở Silver; ô kiểm kê trống giữ giá trị thiếu kèm cờ `is_not_counted`, không thay bằng 0. Số dòng chịu tác động của từng quy tắc trên cả hai tập được trình bày ở Bảng 5.1.

### 4.4.3. Giải quyết định danh

Mã chi nhánh của sáu hệ thống được ánh xạ bằng bảng hạt giống `branch_code_map`, lập từ khảo sát dữ liệu Bronze. Mã nhân viên dạng `NV0012` của POS được chuẩn hóa về mã số của trụ sở bằng quy tắc. Món trên App được ánh xạ về danh mục trụ sở bằng tên sau khi bỏ dấu và chuẩn hóa khoảng trắng; toàn bộ 28 món trên App được khớp.

Tên nguyên liệu trong sổ nhập kho đi qua ba tầng. Tầng một khớp chính xác sau chuẩn hóa: 38 cách viết, 13.576 dòng (84,3%). Tầng hai tra bảng biến thể gồm 29 cách viết do người hiểu nghiệp vụ lập, chẳng hạn "gà tươi" và "thịt gà" đều là Thịt gà tươi, "aquafina" là Nước suối; tầng này xử lý 35 cách viết trong dữ liệu, 2.528 dòng (15,7%). Tầng ba là khớp mờ Jaro–Winkler với ngưỡng 0,9, chỉ áp dụng cho tên không khớp ở hai tầng trên; trong dữ liệu hiện có, tầng này chưa phải dùng tới lần nào. Thứ tự này có chủ đích: khớp mờ dễ nhầm giữa các nguyên liệu tên gần nhau, nên chỉ là lưới an toàn cuối cùng, và tên dưới ngưỡng được đưa vào cách ly để người xem xét bổ sung vào bảng biến thể.

### 4.4.4. Bảo toàn số dòng

Bảng `silver_row_reconciliation` đối soát từng nguồn theo đẳng thức: số dòng Bronze bằng số dòng Silver cộng số dòng cách ly cộng số dòng cấu trúc. Kiểm thử `assert_silver_rows_conserved` thất bại nếu phần không giải thích được khác 0.

TABLE: Bảng 4.9. Đối soát số dòng giữa Bronze và Silver (tập phát triển, 183 ngày)
WIDTHS: 3.4,1.9,1.9,1.8,1.8,2
| Nguồn | Bronze | Silver | Cách ly | Dòng cấu trúc | Không giải thích được |
| POS | 341.674 | 341.674 | 0 | 0 | 0 |
| Ứng dụng | 97.207 | 97.207 | 0 | 0 | 0 |
| ShopeeFood | 286 | 286 | 0 | 0 | 0 |
| Sổ nhập kho (hai mẫu) | 18.652 | 16.104 | 62 | 2.486 | 0 |
| Phiếu kiểm kê | 3.146 | 3.146 | 0 | 0 | 0 |
| Chấm công | 42.594 | 41.304 | 1.290 | 0 | 0 |
| Thời tiết | 183 | 183 | 0 | 0 | 0 |

Báo cáo GrabFood có 286 dòng ở cả hai tầng, chưa có trong bảng đối soát chung mà được kiểm tra bằng hai kiểm thử riêng: mỗi chi nhánh × tuần đúng một dòng, và tiền thực nhận bằng doanh thu món trừ hoa hồng, quảng cáo, khuyến mãi cộng điều chỉnh. Ngoài số dòng, kiểm thử `assert_pos_subtotal_matches_lines` kiểm tra tạm tính của mỗi hóa đơn bằng tổng các dòng món sau khi tách.

## 4.5. Hiện thực tầng Gold

### 4.5.1. Bảng chiều và bảng sự kiện

TABLE: Bảng 4.10. Các bảng chiều và sự kiện của tầng Gold (tập phát triển, 183 ngày)
WIDTHS: 4.2,1.8,7
| Bảng | Số dòng | Ghi chú hiện thực |
| `fact_order` | 438.881 | Hợp nhất 341.674 hóa đơn POS và 97.207 đơn App; trạng thái chuẩn hóa về COMPLETED, VOIDED, REFUNDED, CANCELLED_BY_STORE, CANCELLED_BY_CUSTOMER; doanh thu thuần chỉ tính đơn COMPLETED |
| `fact_order_line` | 851.601 | Gắn phiên bản món có hiệu lực tại ngày bán để lấy giá vốn định mức |
| `fact_labor_shift` | 21.170 | 1.036 ca thiếu lượt ra được nội suy số giờ bằng trung vị cùng ca và vai trò, cờ `is_hours_imputed` |
| `fact_marketplace_settlement` | 572 | Hai sàn × 11 chi nhánh × 26 tuần; tỷ lệ hợp đồng, chênh lệch và tiền thu thừa |
| `fact_inventory_receipt` | 16.104 | Dòng nhập kho hợp lệ, đơn vị chuẩn |
| `fact_stock_count` | 3.146 | Tồn đếm được, cờ ô trống |
| `dim_date` | 183 | Thứ, cuối tuần, ngày lễ (từ bảng hạt giống), mưa và lượng mưa |
| `dim_branch` | 11 | Hạng, quận, tọa độ và mã chi nhánh ở mọi hệ thống nguồn |
| `dim_menu_item` | 34 | SCD loại 2: 28 món, 6 món có hai phiên bản do điều chỉnh giá 01/06 |
| `dim_employee` | 146 | SCD loại 2: 145 nhân viên, 1 người lên quản lý ca từ 01/07 |
| `dim_ingredient`, `dim_channel`, `dim_customer` | 22; 4; 4.089 | Nguyên liệu (nhóm tươi, giá chuẩn); kênh; khách hàng App |

Các bảng chiều thay đổi chậm được dựng từ chuỗi ảnh chụp danh mục mà trụ sở xuất định kỳ. Với mỗi món, các ảnh chụp liên tiếp có cùng giá và giá vốn được gộp thành một phiên bản; khi giá đổi, phiên bản cũ được đóng ở ngày liền trước ảnh chụp mới (`valid_to`) và phiên bản mới mở từ ngày đó (`valid_from`). Ví dụ món Gà giòn miếng đơn có hai phiên bản: 35.000 đồng đến 31/05/2024 và 37.000 đồng từ 01/06/2024. Kiểm thử `assert_scd2_no_overlap` bảo đảm các phiên bản của cùng một món hay một nhân viên không chồng lấn thời gian. Nhờ vậy giá vốn định mức của một dòng món bán ngày 30/5 và ngày 2/6 được tính theo đúng hai bảng giá khác nhau.

### 4.5.2. Kiểm thử dữ liệu

Dự án dbt có 158 kiểm thử theo các nhóm thiết kế ở Bảng 3.18. Phần lớn là kiểm thử dựng sẵn của dbt, khai báo trong tệp cấu hình của từng mô hình: 83 kiểm thử `not_null`, 36 `unique`, 18 `relationships` và 9 `accepted_values`. Năm bảng chỉ số dùng kiểm thử tổng quát `unique_combination` cho khóa ghép, viết một lần bằng macro trong thư mục `macros/`. Bảy kiểm thử còn lại là luật nghiệp vụ dạng câu SQL trong thư mục `tests/`: bảo toàn số dòng Bronze–Silver, tạm tính POS bằng tổng dòng món, tiền thực nhận của hai sàn khớp công thức, mỗi chi nhánh × tuần một dòng GrabFood, lịch sử SCD không chồng lấn và doanh thu thuần Gold bằng Silver. Danh sách đầy đủ ở Phụ lục C.2. Cả 158 kiểm thử đạt trên ba tập dữ liệu. Chẳng hạn, kiểm thử `assert_gold_net_sales_reconciles` so doanh thu thuần ở Gold với tổng tính trực tiếp từ Silver cho từng chi nhánh × ngày; trên tập phát triển, tổng 37.899.868.200 đồng khớp tuyệt đối giữa hai tầng. Một lần `dbt build` đầy đủ 211 bước mất từ 15 đến 25 giây trên máy phát triển, trong đó hai mô hình giải mã JSON chiếm phần lớn khi phải giải mã lại từ đầu.

Kiểm thử dbt kiểm tra dữ liệu sau khi dựng, nhưng không kiểm tra được phần mã Python của đường ống. Phần này có 89 kiểm thử tự động viết bằng pytest, chạy trên dữ liệu nhỏ dựng riêng trong thư mục tạm, không đụng tới kho thật. Bước nạp có 12 kiểm thử, trong đó có nạp lại không tạo dòng trùng, tệp sửa thay toàn bộ bản cũ, tệp hỏng không làm hỏng cả lô; hợp đồng dữ liệu có 10; bộ kết nối API có 10, gồm thử lại khi lỗi tạm thời, dừng ngay khi sai mã xác thực, lấy bổ sung hóa đơn đến trễ của ngày mốc và làm tiếp đúng chỗ sau một lượt bị gián đoạn; cửa chặn chất lượng có 20; bước kiểm tra tệp mới có 4. Phía phân tích có 4 kiểm thử cho các phép thống kê của bộ phát hiện, như đuôi phân phối Poisson và hiệu chỉnh Bonferroni, 5 kiểm thử cho phần đề xuất xử lý và 11 kiểm thử cho ô truy vấn SQL chỉ đọc. Phần còn lại kiểm tra cơ chế chờ khi kho đang bị khóa và trợ lý phân tích. Cả 89 kiểm thử đều đạt.

## 4.6. Hiện thực lớp chỉ số và cây KPI

Năm bảng chỉ số ở mục 3.7.1 được viết bằng SQL trong dbt, nên được kiểm thử và có lineage như mọi bảng Gold khác. `mart_branch_daily` có 52 cột cho mỗi chi nhánh × ngày, gồm doanh thu và số đơn từng kênh, số đơn theo ca, hóa đơn hủy, hoàn, đơn App bị hủy, thời gian chuẩn bị, giá vốn định mức, số ca theo vai trò, giờ công và chi phí nhân công. `mart_branch_weekly` cộng lên theo tuần và nối với báo cáo sàn để tính độ phủ POS và chênh lệch hoa hồng. `mart_ingredient_avt` tính hao hụt theo kỳ kiểm kê của từng nguyên liệu; món combo được tách thành món thành phần trước khi nhân công thức. `mart_cashier_weekly` tính số hóa đơn, số hủy, hoàn, giảm giá của từng thu ngân và tỷ lệ của các thu ngân còn lại cùng chi nhánh.

Bảng `mart_kpi_vs_peers_weekly` hiện thực công thức (3.7) và (3.8) ở dạng dài: mỗi dòng là một chi nhánh × tuần × chỉ số với giá trị, trung vị nhóm cùng hạng, mức nền, độ dao động, z, mức kỳ vọng và chênh lệch so với kỳ vọng. Tập phát triển có 10.582 dòng như vậy. Trung vị và MAD trong cửa sổ tám tuần được tính bằng hàm cửa sổ của DuckDB, không cần mã Python. Trang Truy vết của ứng dụng đọc bảng này để vẽ cây KPI; ví dụ truy vết chi tiết được trình bày ở mục 5.4.1.

## 4.7. Hiện thực các bộ phát hiện và đề xuất xử lý

Các bộ phát hiện nằm trong thư mục `analytics/` và chỉ đọc tầng Gold. Tệp `config.py` khai báo bộ chỉ số giám sát, các ngưỡng và "dấu vân tay" của từng nguyên nhân, tức danh sách chỉ số cùng chiều bất thường đặc trưng cho nguyên nhân đó. Tệp `detect.py` có ba hàm chính: `scan_indicators` liệt kê các chỉ số vượt ngưỡng, `score_all` chấm điểm mọi giả thuyết cho mọi chi nhánh × tuần, `alert_table` chọn giả thuyết mạnh nhất và xếp mức. Chương trình chỉ dùng thông tin có tại thời điểm đánh giá: mức nền lấy từ các tuần trước, so sánh cắt ngang lấy các chi nhánh khác cùng kỳ, không nhìn dữ liệu tương lai. Quét toàn bộ 242 chi nhánh × tuần của một tập mất khoảng một giây.

TABLE: Bảng 4.11. Tham số của bộ phát hiện và lý do chọn (chỉ trên tập phát triển)
WIDTHS: 3.4,3,7
| Tham số | Giá trị | Lý do |
| Mức nền | Trung vị 8 tuần trước | Bản đầu dùng trung bình 4 tuần; tuần 27/5 ở CN2, sau sự cố thiếu nhân sự, bị báo sai vì các tuần sự cố đã kéo mức nền xuống. Độ nhạy của lựa chọn này được đo ở mục 5.5.3 |
| Độ dao động | 1,4826 × MAD 8 tuần, sàn bằng trung vị các chi nhánh; điểm đánh giá sàn 0,05 | Độ lệch chuẩn của 8 mẫu quá nhỏ ở vài chi nhánh gây báo sai (ShopeeFood CN8); điểm đánh giá làm tròn 0,1 nên MAD có thể bằng 0 |
| Lịch sử tối thiểu | 4 tuần | Bốn tuần đầu của mỗi tập chỉ dùng làm mức nền |
| Dung sai hoa hồng (P1a) | 0,5 điểm % | Lớn hơn nhiều sai số làm tròn trên báo cáo sàn |
| Nhóm giá trị cao (P4) | Giá chuẩn từ 80.000 đ/đơn vị | Gồm tôm, thịt bò, phô mai, thịt gà: hàng dễ bị lấy cắp, giá trị lớn |
| Thu ngân (P5) | Từ 30 hóa đơn/tuần; tỷ lệ kỳ vọng tối thiểu 0,5% | Tránh kết luận từ mẫu quá nhỏ và kỳ vọng gần 0. So với thu ngân khác cùng tuần thay vì lịch sử của chi nhánh: khi gian lận kéo dài, lịch sử bị nhiễm làm điểm giảm dần |
| Ngưỡng z | Theo dõi 2, bất thường 3 | Quy ước thông dụng, không tinh chỉnh |
| Ngưỡng điểm cảnh báo | 3,5 | F1 cao nhất khi quét 2,0–5,0 trên tập phát triển (mục 5.5), chốt trước khi chạy tập kiểm tra |

Một số quy tắc gộp bằng chứng được bổ sung khi phân tích các cảnh báo sai trên tập phát triển. Ví dụ, ở sự cố đơn sàn không vào POS (S2), nguyên liệu vẫn được dùng cho các đơn không có trong sổ nên hao hụt hàng giá trị cao cũng tăng (z = 8,3), làm P4 hòa điểm với P1b. Quy tắc giảm một nửa điểm P4 khi P1b đủ bằng chứng xuất phát từ quan sát này. Mọi quy tắc như vậy đều được chốt trước khi chạy tập kiểm tra.

Tệp `actions.py` tạo đề xuất xử lý cho một cảnh báo. Mỗi nguyên nhân có mẫu riêng gồm việc cần xác minh, việc cần làm, việc theo dõi, người phụ trách, thời hạn và các con số ảnh hưởng tính từ Gold:

- P1a: hoa hồng thu thừa lũy kế qua chuỗi tuần lệch, để kế toán đòi lại từ sàn.
- P1b: số đơn thiếu trên POS vượt mức thiếu thường ngày, nhân giá trị đơn sàn bình quân, cho mọi sàn có dấu hiệu.
- P2, P4: phần hao hụt vượt mức thường, với mức thường bằng tỷ lệ hao hụt trên định mức của các chi nhánh khác cùng kỳ, nhân định mức của chi nhánh.
- P3: doanh thu thấp hơn kỳ vọng, số đơn App bị hủy, chi phí bù ca bếp tối về mức thường.
- P5: giá trị hóa đơn bị hủy, hoàn, giảm giá của thu ngân bị nghi vấn, kèm ghi chú rằng đây là giá trị liên quan, không phải số tiền đã xác định bị thất thoát, và không được kết luận gian lận chỉ từ thống kê.

Con số ảnh hưởng giúp người quản lý xếp thứ tự xử lý. Trên tập phát triển, cảnh báo hao hụt đúng ở CN7 ước tính vượt mức thường 6,83 triệu đồng, còn cảnh báo hao hụt sai ở CN10 chỉ 66 nghìn đồng, nên dù cả hai cùng là cảnh báo, người quản lý sẽ xử lý CN7 trước.

## 4.8. Kho phục vụ và báo cáo kinh doanh

Chương trình `pipeline/publish.py` đưa 22 bảng từ DuckDB sang PostgreSQL 16 qua phần mở rộng postgres của DuckDB, gồm toàn bộ Gold và bốn bảng vận hành về cảnh báo, điểm cảnh báo, lượt chạy và kết quả cửa chặn. Kiểu số nguyên 128 bit của DuckDB được đổi sang `BIGINT` vì PostgreSQL không có kiểu tương ứng. Sau khi nạp vào lược đồ tạm `gold__new`, `ops__new`, chương trình so số dòng từng bảng với DuckDB; chỉ khi khớp hết mới đổi lược đồ trong một giao dịch, cấp quyền cho vai trò chỉ đọc `bi_reader`, tạo chỉ mục cho các cột hay được lọc như ngày, chi nhánh, tuần và ghi nhật ký vào `public.publish_log`. Với môi trường vận hành, mỗi lượt đưa khoảng 1,45 đến 1,5 triệu dòng trong 9 đến 15 giây.

Metabase được dựng hoàn toàn bằng mã trong `bi/metabase_setup.py` qua giao diện lập trình của Metabase: tạo tài khoản quản trị lần đầu, kết nối ba cơ sở dữ liệu bằng tài khoản chỉ đọc, xóa dữ liệu mẫu, đặt định dạng số kiểu Việt Nam, tạo 15 câu hỏi SQL và một dashboard cho mỗi tập dữ liệu, kèm bộ lọc khoảng ngày và chi nhánh, rồi tạo liên kết công khai để nhúng. Chạy lại chương trình cho cùng kết quả. Trang Tổng quan của ứng dụng ở Hình 4.4 nhúng dashboard của tập đang chọn và truyền bộ lọc chi nhánh, thời gian ở thanh bên qua địa chỉ, nên người dùng không phải chọn lại ở hai nơi.

IMAGE: figures/h4_3_tong_quan.png || Hình 4.4. Trang Tổng quan: dashboard Metabase trên kho phục vụ, nhúng vào ứng dụng (tập phát triển, toàn chuỗi) || 16

## 4.9. Ứng dụng

### 4.9.1. Tổ chức ứng dụng

Ứng dụng Streamlit (`app/main.py`) có 14 trang gồm trang chủ và bốn nhóm Nguồn dữ liệu, Dữ liệu, Phân tích vận hành, Kiểm chứng, xếp theo dòng dữ liệu như thiết kế ở mục 3.8. Mỗi trang là một tệp trong `app/views/`; các thành phần giao diện dùng chung nằm trong `app/ui.py` và theme của Streamlit, theo một kiểu thống nhất: nền trắng, viền mảnh, một màu nhấn cho thao tác chính và mức cảnh báo, trạng thái thể hiện bằng chấm màu kèm chữ, mỗi trang mở đầu bằng tiêu đề và một câu mô tả. Phần dùng chung về dữ liệu như đọc Gold, bộ nhớ đệm, bộ lọc và định dạng số kiểu Việt Nam nằm trong `app/common.py`. Bộ nhớ đệm được khóa theo tập dữ liệu và thời điểm sửa của tệp kho, nên khi đường ống vừa ghi dữ liệu mới, ứng dụng tự đọc lại. Ứng dụng chỉ mở kho DuckDB ở chế độ đọc và đóng ngay sau mỗi lần đọc, để không giữ khóa tệp làm đường ống không ghi được. Mục này trình bày các trang chính; ảnh chụp các trang còn lại ở Phụ lục H.

### 4.9.2. Các trang phân tích vận hành

Trang Trung tâm cảnh báo ở Hình 4.5 hiển thị bản đồ nhiệt mức cảnh báo theo chi nhánh × tuần và danh sách cảnh báo với nguyên nhân, điểm, bằng chứng, thiệt hại ước tính và người phụ trách, sắp theo thiệt hại. Người dùng có thể thay ngưỡng điểm để xem sự đánh đổi giữa bỏ sót và báo động giả; chọn một dòng sẽ mở trang Truy vết của đúng chi nhánh và tuần đó.

Trang Truy vết nguyên nhân mở đầu bằng kết luận và đề xuất xử lý như Hình 4.6, tiếp theo là biểu đồ doanh thu thực tế so với kỳ vọng qua các tuần tương tự Hình 5.3, cây KPI theo kênh, số đơn và AOV, các tín hiệu theo từng giả thuyết và các yếu tố bình thường của tuần. Cuối trang là mục bằng chứng gốc, hiện thực yêu cầu FR8 và NFR3: tùy nguyên nhân, trang liệt kê các bản ghi làm căn cứ cùng tên tệp và số dòng gốc mà tầng Bronze đã lưu, và một nút mở thẳng tệp gốc ở trang Tệp nguồn với dòng đó được lọc sẵn. Ví dụ, từ cảnh báo gian lận ở CN8 tuần 01/07/2024, người dùng đi tới hóa đơn POS-08-03-20240701-00065 do thu ngân NV0093 thu tiền mặt lúc 14:13 và hủy 14,8 phút sau, nằm trong tệp `pos/POS-08/pos_export_2024-07-01.json`. Như vậy một cảnh báo truy ngược được tới đúng dòng dữ liệu thô mà hệ thống nguồn đã xuất.

IMAGE: figures/h4_4_canh_bao.png || Hình 4.5. Trang Trung tâm cảnh báo (tập phát triển) || 16

IMAGE: figures/h4_5_truy_vet.png || Hình 4.6. Phần kết luận và đề xuất xử lý của trang Truy vết nguyên nhân: CN2, tuần 06/05/2024 (tập phát triển) || 15

### 4.9.3. Các trang dữ liệu và kiểm chứng

Trang Vận hành hằng ngày ở Hình 4.7 cho phép đưa dữ liệu của một hoặc bảy ngày kinh doanh mới vào môi trường vận hành bằng cách kích hoạt DAG nguồn, rồi theo dõi từng bước xử lý: số bản ghi kéo qua API, tệp mới, số dòng nạp, cửa chặn chất lượng, kiểm thử dbt, cảnh báo mới và lượt đưa sang kho phục vụ. Bước gặp sự cố nhưng không chặn các bước sau, như API nguồn không phản hồi, được hiện ở mức cảnh báo, tách khỏi mức lỗi. Trang Chất lượng dữ liệu tổng hợp kết quả cửa chặn, 158 kiểm thử dbt, đối soát số dòng, bảng cách ly và độ mới từng nguồn; trang Mô hình và phả hệ vẽ lineage và lược đồ hình sao trực tiếp từ metadata dbt, nên luôn khớp với mã nguồn.

IMAGE: figures/h4_6_van_hanh.png || Hình 4.7. Trang Vận hành hằng ngày sau khi đưa vào bảy ngày kinh doanh mới (môi trường vận hành) || 16

Trang Bộ mô phỏng ở Hình 4.8, thuộc nhóm Kiểm chứng, đặt các con số sự thật của một ngày cạnh những gì từng hệ thống ghi lại, lấy từ kho dữ liệu đúng như đường ống nhìn thấy. Ở ngày 11/05/2024 của CN2, giữa kịch bản thiếu nhân sự, 216 đơn tại quầy khớp với số hóa đơn POS còn hiệu lực và 92 đơn App khớp với App, nhưng 38 khách bỏ về không được hệ thống nào ghi nhận, và 5 đơn sàn không được nhập POS lộ ra đúng bằng phần thiếu ở hai dòng GrabFood, ShopeeFood. Trang còn mở được tệp gốc của ngày đó, liệt kê lỗi dữ liệu trong tệp cùng cách tầng Silver xử lý và vẽ dòng thời gian các kịch bản sự cố. Trang này đọc đáp án nên chỉ dùng để trình bày và kiểm chứng; đường ống và bộ phát hiện không dùng nó.

IMAGE: figures/h4_7_mo_phong.png || Hình 4.8. Trang Bộ mô phỏng: sự thật của một ngày đặt cạnh những gì các hệ thống nguồn ghi lại (CN2, 11/05/2024, tập phát triển) || 15

### 4.9.4. Phần mở rộng: trợ lý phân tích

Ngoài phạm vi ban đầu, ứng dụng có thêm trang Trợ lý phân tích cho phép hỏi bằng tiếng Việt, ví dụ "tuần này chi nhánh nào đáng lo nhất và vì sao". Trợ lý dùng mô hình ngôn ngữ lớn Claude theo cơ chế gọi công cụ: mô hình không tự tính số liệu mà gọi năm hàm có sẵn của hệ thống để lấy danh sách cảnh báo, truy vết một chi nhánh × tuần, lấy chỉ số chi nhánh, liệt kê bảng và truy vấn kho. Truy vấn SQL do mô hình viết bị giới hạn hai lớp: chương trình chỉ chấp nhận một câu `SELECT` hoặc `WITH`, và kết nối DuckDB được mở ở chế độ chỉ đọc, tắt truy cập bên ngoài, giới hạn 200 dòng và 15 giây. Sau mỗi câu trả lời, chương trình đối chiếu các con số trong câu trả lời với kết quả của công cụ và hiển thị tỷ lệ có căn cứ. Phần này được kiểm thử bằng một mô hình giả lập; chưa được đánh giá với mô hình thật nên không thuộc kết quả của Chương 5. Trang chỉ xuất hiện trong thanh điều hướng khi đã cấu hình khóa của mô hình.

## 4.10. Điều phối và vận hành tăng dần

### 4.10.1. Đóng gói bằng Docker Compose

Tệp `docker-compose.yml` dựng năm dịch vụ.

- `airflow` chạy Apache Airflow 2.10.5 ở chế độ standalone, kèm môi trường Python riêng có DuckDB và dbt cùng phiên bản với máy phát triển.
- `warehouse-db` chạy PostgreSQL 16, vừa là kho phục vụ vừa chứa cơ sở dữ liệu ứng dụng của Metabase.
- `metabase` là công cụ BI.
- `app` là ứng dụng Streamlit.
- `source-api` là API giả lập của POS đám mây và App; dịch vụ này thuộc phía doanh nghiệp chứ không thuộc đường ống.

Thư mục dự án được gắn vào các dịch vụ Airflow và ứng dụng, nên mã nguồn và dữ liệu là một bản duy nhất trên máy; dịch vụ API chỉ được gắn thư mục dữ liệu ở chế độ chỉ đọc. Toàn bộ hệ thống được bật bằng một lệnh `docker compose up -d`.

Hình 4.9 là sơ đồ triển khai của nền tảng. Mọi thành phần chạy trong các container trên cùng một máy và giao tiếp qua mạng nội bộ của Docker. Kho DuckDB nằm trong thư mục dự án, được gắn vào container airflow để ghi và vào container app để đọc; kho phục vụ PostgreSQL có volume riêng, Metabase đọc nó bằng tài khoản chỉ đọc. Khi chạy trên máy cá nhân, trình duyệt mở thẳng cổng của ứng dụng, Airflow và Metabase. Cấu hình cho máy chủ trong thư mục `deploy/` ghép thêm một container Caddy đứng trước, cấp HTTPS tự động và chuyển tiếp tới ba giao diện web đó; các cổng còn lại, kể cả PostgreSQL và API giả lập, không được mở ra ngoài.

IMAGE: figures/h4_trien_khai.png || Hình 4.9. Sơ đồ triển khai của nền tảng trên Docker Compose || 16

### 4.10.2. Hai DAG và cơ chế kích hoạt theo dữ liệu

Tệp `airflow/dags/fastfat_pipeline.py` khai báo hai DAG như Hình 3.11. Bước ghi dữ liệu của DAG nguồn khai báo đầu ra là Dataset `file:///opt/fastfat/data/live/source_systems`; trang Tải tệp lên cũng báo cập nhật Dataset này qua giao diện lập trình của Airflow. DAG đường ống dùng lịch `DatasetOrTimeSchedule`, nên chạy khi Dataset cập nhật hoặc vào đầu mỗi giờ. Bước đầu `extract` gọi bộ kết nối API; nếu API không phản hồi, bước này kết thúc với trạng thái cảnh báo chứ không lỗi, để các bước sau vẫn xử lý các nguồn tệp. Nếu không có ngày mới qua API, bước này không ghi nhật ký, tránh mỗi giờ sinh một dòng vô nghĩa. Bước `check` so các tệp trong thư mục nguồn với nhật ký nạp theo đường dẫn, kích thước và thời điểm sửa. Nếu không có tệp mới, chương trình thoát với mã 99 và Airflow đánh dấu các bước sau là bỏ qua thay vì lỗi. Nếu tệp mới nhất vừa được ghi trong vòng 5 giây, hệ thống nguồn có thể còn đang ghi, nên bước này chờ thêm từng đợt 5 giây, tối đa tám đợt, rồi mới cho các bước sau chạy. Mỗi bước gọi `pipeline/run_daily.py --step <tên bước>`; cùng chương trình này chạy được cả ngoài Airflow để kiểm thử. Bước nào lỗi được Airflow thử lại một lần sau 2 phút. Tệp DuckDB không cho ghi khi một tiến trình khác đang mở đọc, và lỗi này đã thực sự xảy ra: một lượt xử lý thất bại ở bước `check` vì đúng lúc ghi nhật ký, trang Tải tệp lên đang tự làm mới và mở kho để đọc. Sau lần đó, mọi chỗ đường ống mở kho, từ bước nạp, cửa chặn, ghi nhật ký, ghi cảnh báo tới lúc giao kho cho dbt, đều chờ và thử lại tối đa 120 giây khi gặp lỗi khóa tệp, kèm kiểm thử dùng một tiến trình thật giữ khóa; phía ứng dụng, khi kho đang được ghi thì trang tạm không hiện số liệu và tự đọc lại ở lần làm mới sau.

### 4.10.3. Một lượt chạy với dữ liệu ngày mới

Môi trường vận hành, tức tập `live`, là bản sao của tập phát triển, dùng riêng cho vận hành hằng ngày để hai tập đánh giá không bị thay đổi. Để minh họa luồng từ dữ liệu mới đến cảnh báo, môi trường này có cài sẵn hai sự cố bắt đầu từ ngày 23/09/2024: thiếu nhân sự ca tối ở CN3 và ShopeeFood tính hoa hồng 27% ở CN1. Hai sự cố này chỉ phục vụ trình diễn, không thuộc hai tập đánh giá. Bảng 4.12 là nhật ký một lượt xử lý thật trong Docker ngày 18/10/2026: người dùng bấm gửi bảy ngày kinh doanh 23–29/09/2024 ở trang Vận hành hằng ngày, hệ thống nguồn ghi dữ liệu trong vài giây, rồi Airflow tự kích hoạt đường ống mà không có thao tác nào của người dùng.

TABLE: Bảng 4.12. Một lượt đường ống kích hoạt theo dữ liệu mới (môi trường vận hành, bảy ngày, nhật ký `ops.pipeline_runs`)
WIDTHS: 2,1.6,8
| Bước | Thời gian | Kết quả ghi nhận |
| extract | 8,6 giây | POS đám mây: 7 ngày, 10.365 hóa đơn, 55 trang, 6 lần thử lại; App: 7 ngày, 3.880 đơn, 24 trang, 1 lần thử lại |
| check | 22,5 giây | 236 tệp mới: 77 POS, 7 App, 77 chấm công, 66 nhập kho, 7 thời tiết, 1 GrabFood, 1 ShopeeFood |
| ingest | 33,8 giây | 236 tệp, 18.798 dòng mới, 0 tệp lỗi |
| quality | 3,4 giây | 15/15 mục đạt (độ mới, khối lượng, đầy đủ theo chi nhánh, tệp lỗi, sai hợp đồng, không nhận dạng, cấu trúc) |
| dbt | 21,0 giây | 211/211 bước đạt |
| detect | 2,5 giây | Tuần 23/09/2024: 2 cảnh báo, CN1 P1a điểm 6,0; CN3 P3 điểm 4,8 |
| publish | 8,6 giây | 22 bảng, 1.500.446 dòng sang PostgreSQL, đối soát số dòng khớp |

Từ lúc bấm nút đến khi dữ liệu lên kho phục vụ mất 146 giây; các lượt khác đo được từ 152 đến 199 giây, và 328 giây khi máy đang chạy việc nặng khác. Phần lớn thời gian là liệt kê và đọc tệp qua thư mục gắn từ Windows vào Docker; để giảm phần này, bước nạp chỉ băm lại tệp có kích thước hoặc thời điểm sửa khác lần nạp trước, nhờ đó bước nạp một ngày trong Docker giảm từ 74 xuống 20 giây. Chi phí mỗi lượt tỷ lệ với lượng dữ liệu mới, đáp ứng yêu cầu NFR7. Hai cảnh báo trùng đúng hai sự cố đã cài, với số liệu y hệt khi POS đám mây và App còn đi đường tệp; riêng CN1 bị thu thừa 528.250 đồng. Từ trang Vận hành hằng ngày ở Hình 4.7, người dùng mở thẳng trang Truy vết của từng cảnh báo.

## 4.11. Tiểu kết chương

Các thành phần thiết kế ở Chương 3 đều đã được hiện thực và chạy được trên một máy tính cá nhân. Bộ mô phỏng tạo đúng tác động của cả mười hai kịch bản và các biến động bình thường. Tầng thu thập nhận dữ liệu qua ba kênh, từ chối tệp sai hợp đồng và chịu được lỗi tạm thời của API. Từ Bronze tới Gold, số dòng được bảo toàn và không dòng nào bị loại im lặng; 158 kiểm thử đạt trên cả ba tập dữ liệu và doanh thu thuần khớp tuyệt đối giữa Silver và Gold. Các bộ phát hiện, kho phục vụ, ứng dụng và hai DAG điều phối chạy nối tiếp nhau không cần thao tác tay; một lượt bảy ngày đi từ lúc dữ liệu nguồn được ghi đến khi cảnh báo lên kho phục vụ trong 146 đến 199 giây ở các lượt đo được. Chương 5 đánh giá định lượng chất lượng dữ liệu và khả năng phát hiện, truy vết của hệ thống.
