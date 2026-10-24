# CHƯƠNG 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

NGUON: Đề xuất của nghiên cứu

Chương này trình bày thiết kế của nền tảng theo phương pháp nghiên cứu khoa học thiết kế đã nêu ở mục 1.6: mỗi quyết định thiết kế có căn cứ từ Chương 2 và có tiêu chí kiểm chứng ở Chương 5. Mục 3.1 đi từ câu hỏi nghiên cứu đến yêu cầu của hệ thống; các mục tiếp theo đi theo chiều của dữ liệu, từ kiến trúc tổng thể, bộ mô phỏng tạo dữ liệu nguồn, đường ống tới tầng Silver, kho dữ liệu, kiểm soát chất lượng, lớp phân tích, đến ứng dụng, kho phục vụ và điều phối.

## 3.1. Phân tích yêu cầu

### 3.1.1. Từ câu hỏi nghiên cứu đến thiết kế

Mỗi câu hỏi nghiên cứu ở mục 1.3 được chuyển thành một giả thuyết thiết kế, tức một nhận định về cách tổ chức hệ thống mà nếu đúng thì câu hỏi được trả lời, kèm thành phần hiện thực và tiêu chí kiểm chứng (Bảng 3.1). Theo Hevner et al. (2004), sản phẩm thiết kế phải được đánh giá bằng tiêu chí xác định trước, gắn với vấn đề nó giải quyết; nhờ vậy thiết kế ở chương này và đánh giá ở Chương 5 dùng chung một khung.

TABLE: Bảng 3.1. Liên hệ giữa câu hỏi nghiên cứu, giả thuyết thiết kế và cách kiểm chứng
WIDTHS: 1.3,5,3.2,4.5
| Câu hỏi | Giả thuyết thiết kế | Thành phần hiện thực | Tiêu chí kiểm chứng |
| RQ1 | Tách thu thập, lưu bản gốc, làm sạch có cách ly và kiểm thử giữa các tầng thì tích hợp được bảy nguồn không đồng nhất mà không thất lạc hay làm sai dữ liệu | Tầng thu thập, Bronze, Silver, Gold, kiểm soát chất lượng (mục 3.4–3.6) | Số dòng bảo toàn giữa các tầng; số kiểm thử đạt; lỗi dữ liệu được phát hiện và xử lý; khả năng chịu dữ liệu bất thường; thời gian xử lý một ngày (mục 5.2) |
| RQ2 | So mỗi chỉ số với nhóm chi nhánh cùng hạng và lịch sử của chính chi nhánh, kết hợp luật đối soát và kiểm định trên số đếm, thì phát hiện được các sự cố mà theo dõi doanh thu bỏ sót | Mức kỳ vọng, năm bộ phát hiện (mục 3.7) | Precision, recall, F1 và độ trễ trên tập kiểm tra độc lập; so với hai phương án cơ sở; độ nhạy theo ngưỡng và cách tính mức kỳ vọng (mục 5.3, 5.5) |
| RQ3 | Đặt phân rã doanh thu theo cây KPI cạnh dấu hiệu đặc trưng của từng nguyên nhân trên nhiều nguồn thì gán được nguyên nhân và không nhầm biến động bình thường thành sự cố | Cây KPI, chấm điểm giả thuyết, bằng chứng gốc (mục 3.7, 3.8) | Tỷ lệ sự cố được gán đúng nguyên nhân hạng một; số cảnh báo trong các tuần lễ, mưa, điều chỉnh giá (mục 5.4) |

Ràng buộc chung cho cả ba câu hỏi là tính độc lập của đánh giá: đường ống và các bộ phát hiện không được đọc đáp án của bộ mô phỏng, và mọi tham số chỉ được chọn trên tập phát triển.

### 3.1.2. Yêu cầu chức năng và phi chức năng

Hệ thống phục vụ bốn nhóm người dùng. Quản lý vận hành chuỗi cần biết chi nhánh nào có vấn đề, vấn đề gì và mất bao nhiêu tiền; kế toán cần danh sách sai lệch đối soát, chênh lệch kiểm kê và hóa đơn hủy bất thường; quản lý chi nhánh cần biết ca nào thiếu người, nguyên liệu nào hao hụt; kỹ sư dữ liệu cần đường ống tự nạp dữ liệu mới và cho biết dòng nào bị cách ly, vì sao. Từ đó hình thành chín yêu cầu chức năng (Bảng 3.2) và tám yêu cầu phi chức năng (Bảng 3.3).

TABLE: Bảng 3.2. Yêu cầu chức năng
WIDTHS: 1,8,3
| Mã | Yêu cầu | Người dùng |
| FR1 | Thu nhận dữ liệu từ bảy nhóm hệ thống nguồn qua đúng kênh mỗi hệ thống hỗ trợ (API, tệp xuất tự động, tệp do người gửi); nhận dạng tệp theo nội dung, từ chối tệp sai hợp đồng dữ liệu kèm lý do; chỉ nạp phần mới | Kỹ sư dữ liệu, kế toán, quản lý chi nhánh |
| FR2 | Làm sạch, chuẩn hóa và giải quyết định danh chi nhánh, nhân viên, món, nguyên liệu giữa các hệ thống | Kỹ sư dữ liệu |
| FR3 | Cách ly dòng vi phạm quy tắc kèm lý do; báo cáo tình trạng chất lượng dữ liệu | Kỹ sư dữ liệu |
| FR4 | Lưu dữ liệu sạch vào kho dạng lược đồ hình sao, giữ lịch sử thay đổi giá món và lương | Kỹ sư dữ liệu |
| FR5 | Tính các chỉ số vận hành theo chi nhánh, ngày, ca, kênh: doanh thu, số đơn, AOV, COGS%, Labor%, OPLH, thời gian chuẩn bị, tỷ lệ hủy | Quản lý vận hành |
| FR6 | Phát hiện năm loại sự cố P1–P5, đưa ra danh sách cảnh báo có mức độ, bằng chứng và thiệt hại ước tính | Quản lý vận hành, kế toán |
| FR7 | Truy vết biến động doanh thu của một chi nhánh trong một tuần về kênh, thành phần lượng và giá, và nguyên nhân vận hành | Quản lý vận hành |
| FR8 | Xem bản ghi gốc làm căn cứ cho một cảnh báo | Quản lý vận hành, chi nhánh |
| FR9 | Tự động chạy toàn bộ đường ống khi có dữ liệu mới và đưa kết quả sang kho phục vụ cho công cụ báo cáo | Kỹ sư dữ liệu |

TABLE: Bảng 3.3. Yêu cầu phi chức năng
WIDTHS: 1,3,8
| Mã | Thuộc tính | Yêu cầu |
| NFR1 | Tái lập | Cùng dữ liệu nguồn và mã nguồn cho cùng kết quả; dữ liệu mô phỏng tái lập được nhờ hạt giống ngẫu nhiên cố định |
| NFR2 | Lũy đẳng, tăng dần | Chạy lại không sinh dữ liệu trùng; mỗi ngày chỉ xử lý dữ liệu mới |
| NFR3 | Truy vết nguồn gốc | Mọi dòng dữ liệu truy ngược được về tệp và dòng gốc |
| NFR4 | Kiểm chứng được | Kiểm thử chất lượng tự động sau mỗi lần biến đổi; đối soát số dòng và tổng tiền giữa các tầng |
| NFR5 | Giải thích được | Mọi cảnh báo kèm chỉ số, ngưỡng và dữ liệu làm căn cứ; không dùng mô hình hộp đen |
| NFR6 | Độc lập đánh giá | Đường ống và bộ phát hiện không đọc đáp án của bộ mô phỏng; tham số chỉ chọn trên tập phát triển |
| NFR7 | Hiệu năng | Chạy trên một máy tính cá nhân; xử lý một ngày dữ liệu mới trong vài phút |
| NFR8 | Chịu lỗi nguồn | Tệp hỏng, sai hợp đồng, thiếu tệp hay API không phản hồi không làm dừng các nguồn khác, không bị bỏ qua im lặng và không dẫn tới kết luận sự cố sai |

### 3.1.3. Ca sử dụng

Sơ đồ ca sử dụng ở Hình 3.1 dùng ký hiệu UML 2.5 (Object Management Group, 2017). Quản lý vận hành, quản lý chi nhánh và kế toán dùng chung các chức năng phân tích và gửi tệp, nên được khái quát thành tác nhân người dùng nghiệp vụ; bên cạnh đó là kỹ sư dữ liệu và hai tác nhân hệ thống là hệ thống nguồn và Airflow. Các ca sử dụng hợp thành ba luồng. Luồng phân tích dành cho quản lý và kế toán: từ danh sách cảnh báo sắp theo thiệt hại ước tính, người dùng đi vào truy vết gồm kết luận, đề xuất xử lý, doanh thu so với mức kỳ vọng, cây KPI và cuối cùng là bản ghi gốc, vì một kết luận thống kê chỉ có giá trị khi kiểm tra lại được trên dữ liệu thật. Luồng đưa dữ liệu vào: phần lớn dữ liệu đến tự động qua API hoặc tệp xuất theo lịch, còn báo cáo sàn, sổ kho và phiếu kiểm kê do người gửi; hệ thống tự xác định tệp thuộc nguồn nào, đúng hợp đồng không, là bản mới, bản sửa hay bản trùng, và báo ngay lý do nếu từ chối. Luồng vận hành tự động: khi có dữ liệu mới, đường ống tự chạy từ thu thập đến kho phục vụ; nếu dữ liệu thiếu nghiêm trọng hoặc một kiểm thử thất bại, lượt chạy dừng và người dùng tiếp tục thấy bản kết quả trước, không bao giờ thấy kết quả dở dang.

IMAGE: figures/h3_1_use_case.png || Hình 3.1. Sơ đồ ca sử dụng của hệ thống || 16

## 3.2. Kiến trúc tổng thể

Hình 3.2 trình bày nền tảng theo chiều đi của dữ liệu: mỗi cột là một chặng, mỗi khối ghi thành phần, công nghệ và vấn đề mà thành phần đó giải quyết; thanh dưới cùng là thứ tự các bước do Airflow điều phối trong một lượt chạy. Lý do chọn từng công nghệ đã trình bày ở Bảng 2.3.

IMAGE: figures/h3_2_kien_truc.png || Hình 3.2. Kiến trúc tổng thể của nền tảng || 16

Nền tảng gồm sáu lớp. Lớp nguồn và thu thập đưa dữ liệu từ ba kênh, gồm API của POS đám mây và ứng dụng đặt hàng, tệp xuất theo lịch của POS cài tại máy và máy chấm công, tệp do người gửi, về một vùng tiếp nhận và kiểm tra theo hợp đồng dữ liệu. Trong khóa luận, các hệ thống nguồn do bộ mô phỏng đóng vai và phía API do một dịch vụ giả lập phục vụ; khi triển khai thực tế chỉ phần nguồn được thay, các lớp phía sau giữ nguyên. Lớp nạp lưu bản gốc vào tầng Bronze của DuckDB. Lớp biến đổi gồm các mô hình dbt làm sạch, cách ly dòng lỗi ở tầng Silver và tổ chức lược đồ hình sao, bảng chỉ số ở tầng Gold. Lớp phân tích tính mức kỳ vọng, cây KPI, năm bộ phát hiện và đề xuất xử lý. Lớp phục vụ sao tầng Gold và bảng cảnh báo sang PostgreSQL cho Metabase đọc bằng tài khoản chỉ đọc. Lớp trình bày và điều phối gồm ứng dụng Streamlit là địa chỉ duy nhất cho người dùng, và Airflow chạy toàn bộ chuỗi khi có dữ liệu mới.

DuckDB và PostgreSQL có vai trò khác nhau. DuckDB là máy tính toán: mọi phép biến đổi và kiểm thử diễn ra trong một tệp, nhanh và dễ tái lập, nhưng một tệp DuckDB chỉ cho một tiến trình ghi và không có tài khoản người dùng. PostgreSQL phục vụ nhiều người đọc đồng thời, và bản sao chỉ được thay khi một lượt chạy đã qua hết kiểm thử, nên người đọc không bao giờ thấy dữ liệu dở dang. Ràng buộc kiến trúc quan trọng nhất là đáp án của bộ mô phỏng nằm ngoài đường ống: chỉ chương trình kiểm chứng, chương trình đánh giá ở Chương 5 và trang Bộ mô phỏng của ứng dụng được đọc, còn đường ống và các bộ phát hiện chỉ thấy dữ liệu nguồn, giống điều kiện triển khai thực tế.

## 3.3. Thiết kế bộ mô phỏng dữ liệu nguồn

### 3.3.1. Nguyên lý “một thế giới, nhiều góc nhìn”

Sinh ngẫu nhiên từng nguồn độc lập tạo ra dữ liệu không nhất quán: báo cáo sàn không khớp với đơn trong POS, mã thu ngân không ứng với ai trong danh sách chấm công, thiếu nhân sự không ảnh hưởng gì tới doanh thu. Trên dữ liệu như vậy, “tích hợp đa nguồn” chỉ là hình thức và không phương pháp truy vết nào kiểm chứng được. Bộ mô phỏng vì vậy theo nguyên lý ngược lại: mỗi ngày, các sự kiện thật của chuỗi được sinh đúng một lần, gồm đơn hàng, ca làm, tải bếp, nguyên liệu dùng, hỏng, mất, hàng giao và kiểm kê; sau đó mỗi hệ thống nguồn xuất phần sự kiện nó quan sát được theo định dạng riêng, kèm lỗi đặc trưng (Bảng 3.4). Nhờ vậy các nguồn nhất quán với nhau như ngoài thực tế, và một sự cố đưa vào thế giới để lại dấu vết đồng thời ở nhiều nguồn.

TABLE: Bảng 3.4. Các hệ thống nguồn và phần sự kiện mỗi hệ thống quan sát được
WIDTHS: 2,4,3,5
| Hệ thống nguồn | Phần sự kiện quan sát được | Định dạng | Quy ước riêng |
| POS tại quầy | Đơn tại quầy mọi trạng thái và đơn sàn đã hoàn thành do nhân viên nhập tay | JSON theo chi nhánh, theo ngày; 43 trường | Mã chi nhánh theo tiền tố máy POS; mã thu ngân dạng `NV0012` |
| Ứng dụng riêng | Đơn đặt qua ứng dụng mọi trạng thái, khách hàng | JSON từ API theo ngày; 30 trường | Giờ UTC; mã chi nhánh, mã món riêng |
| GrabFood | Tổng hợp tuần của đúng các đơn Grab thật | CSV theo tuần, tiếng Anh | Tên cửa hàng tự do; chỉ có số tiền hoa hồng |
| ShopeeFood | Tổng hợp tuần của đúng các đơn Shopee thật | Excel theo tuần, tiếng Việt | Mã cửa hàng riêng; có dòng tiêu đề báo cáo |
| Sổ nhập kho | Từng lần giao hàng | Excel do quản lý ghi, hai mẫu | Tên nguyên liệu nhập tự do |
| Phiếu kiểm kê | Tồn thực tế hai tuần một lần | Excel dạng phiếu | Mã nguyên liệu `NL01`…`NL22` |
| Máy chấm công | Lượt quẹt vào, ra | CSV theo chi nhánh, theo ngày | Mã nhân viên dạng số, mã chi nhánh `BR01` |
| Hệ thống trụ sở | Danh mục chi nhánh, món, giá, nguyên liệu, công thức, nhân viên, hợp đồng sàn | CSV, xuất lại khi thay đổi | Ảnh chụp theo ngày hiệu lực |
| Thời tiết | Lượng mưa, tình trạng thời tiết theo ngày | JSON theo ngày | Nguồn bên ngoài |

### 3.3.2. Mô hình nhu cầu và chuỗi nhân quả vận hành

Số đơn kỳ vọng của chi nhánh b, kênh k, ngày d được mô hình hóa dạng tích các hệ số:

EQ: \lambda_{b,k,d} = Q_{g(b)} \cdot h_{b} \cdot w_{t(d)} \cdot \varepsilon_{b,d} \cdot s_{k} \cdot L_{k,d} \cdot M_{k,d} \cdot X_{b,k,d} || (3.1)

NOINDENT: trong đó $Q_{g(b)}$ là mức đơn cơ sở theo hạng $g(b)$ của chi nhánh, $h_{b}$ là hệ số riêng của chi nhánh, $w_{t(d)}$ là hệ số theo thứ trong tuần, $\varepsilon_{b,d}$ là nhiễu theo ngày, $s_{k}$ là tỷ trọng kênh, $L_{k,d}$ và $M_{k,d}$ là hệ số ngày lễ và ngày mưa theo kênh, $X_{b,k,d}$ là hệ số thứ hạng trên sàn, chỉ áp dụng cho kênh sàn. Số đơn thực tế rút từ phân phối Poisson với kỳ vọng λ, rồi phân bổ vào các giờ mở cửa theo trọng số giờ (Bảng 3.5).

TABLE: Bảng 3.5. Tham số chính của mô hình nhu cầu
WIDTHS: 4,8
| Tham số | Giá trị |
| Mức đơn cơ sở theo hạng (đơn/ngày) | Hạng A: 380; hạng B: 170; hạng C: 60 (3, 5 và 3 chi nhánh) |
| Tỷ trọng kênh | Tại quầy 55%, ứng dụng riêng 20%, GrabFood 15%, ShopeeFood 10% |
| Hệ số ngày trong tuần (T2 → CN) | 0,92; 0,90; 0,95; 0,98; 1,10; 1,25; 1,20 |
| Ngày lễ | 18/4, 30/4, 1/5, 2/9, 3/9/2024: tại quầy ×1,35; ứng dụng ×1,30; sàn ×1,15 |
| Ngày mưa | Mùa mưa (tháng 5–10) 45% số ngày, mùa khô 8%; tại quầy ×0,75; ứng dụng ×1,20; sàn ×1,25 |
| Giờ mở cửa và cao điểm | 7h–22h; khung 11h–14h và 18h–21h có trọng số gấp ba |
| Số món mỗi đơn | 1, 2, 3, từ 4 món với xác suất 42%, 32%, 16%, 10% (hiệu chỉnh từ dữ liệu thật) |
| Mức độ bán chạy của món | Phân phối Zipf số mũ 1,06 theo thứ hạng món (hiệu chỉnh từ dữ liệu thật) |
| Độ dao động ngẫu nhiên theo ngày | Độ lệch chuẩn 0,075 trên thang logarit (hiệu chỉnh từ dữ liệu thật) |
| Điều chỉnh giá | 01/06/2024 tăng giá 6 món, căn cứ để dựng chiều thay đổi chậm kiểu 2 |
| Khách hàng ứng dụng | 4.200 khách, tần suất mua dạng Zipf |

Các tham số không ghi hiệu chỉnh là giả định cho một chuỗi đồ ăn nhanh tại TP.HCM: hệ số ngày trong tuần và hai khung cao điểm theo đặc điểm nhu cầu theo giờ của nhà hàng (Thompson, 1998); tỷ trọng giao hàng khoảng 45% theo mức phổ biến của giao đồ ăn trực tuyến tại Việt Nam (Momentum Works, 2025), còn tỷ lệ giữa hai sàn là giả định.

Phần quan trọng nhất của bộ mô phỏng là chuỗi nhân quả nối nhân sự với doanh thu (Hình 3.3). Mỗi nhân viên có ca ưu tiên, sáng từ 6h45 đến 14h hoặc tối từ 13h45 đến 22h, và đi làm với xác suất cao hơn vào cuối tuần; quản lý luôn gọi người bù nếu ca có ít hơn số nhân viên bếp tối thiểu, lần lượt 3, 2 và 1 người với chi nhánh hạng A, B và C. Kịch bản thiếu nhân sự được áp dụng sau bước này, tức là thiếu người do điều phối sai chứ không do vắng ngẫu nhiên.

IMAGE: figures/h3_3_chuoi_nhan_qua.png || Hình 3.3. Chuỗi nhân quả vận hành trong bộ mô phỏng || 15

Với mỗi giờ $h$, mức tải bếp $u(h)$ bằng số đơn $n(h)$ chia năng lực bếp, tức số nhân viên bếp có mặt $e(h)$ nhân năng lực $c_{b}$ của một người, tính bằng số đơn mỗi giờ. Năng lực $c_{b}$ được hiệu chỉnh riêng cho từng chi nhánh sao cho giờ cao điểm của ngày đông nhất, với số nhân viên bếp tối thiểu, có tải 95%; khi vận hành bình thường tải dưới 1 và chỉ vượt 1 khi thiếu người. Thời gian chuẩn bị tăng phi tuyến khi tải tiến gần năng lực, theo dạng của mô hình hàng đợi ở mục 2.6, với $\rho = \min(u;\ 0{,}97)$:

EQ: u(h) = \frac{n(h)}{c_{b} \cdot e(h)} || (3.2)

EQ: T_{\text{chuẩn bị}} = 4 + \frac{6}{(1 - \rho)^{0{,}6}} \quad \text{(phút)} || (3.3)

Quá tải để lại nhiều hệ quả. Khi tải vượt 0,90, một phần khách tại quầy bỏ về với tỷ lệ 0,60 × (u − 0,90), tối đa 40%; đơn của họ không xuất hiện trong hệ thống nào, tức phần doanh thu mất đi không để lại dấu vết trực tiếp. Khi tải vượt 0,85, cửa hàng hủy đơn trực tuyến với xác suất 0,006 + 0,30 × (u − 0,85). Khi thời gian chuẩn bị vượt 18 phút, khách đặt trực tuyến tự hủy với xác suất tăng 0,004 mỗi phút; điểm đánh giá mỗi đơn có kỳ vọng 4,7 và giảm 0,05 cho mỗi phút vượt 15 phút. Cuối tuần, điểm cửa hàng trên mỗi sàn được cập nhật theo trung bình trượt có trọng số và bị trừ theo tỷ lệ hủy do cửa hàng, rồi quyết định hệ số thứ hạng của tuần sau, giới hạn trong khoảng 0,55 đến 1,08:

EQ: S_{t} = 0{,}6\, S_{t-1} + 0{,}4 \left( \bar{r}_{t} - 2\, c_{t} \right), \qquad X_{t+1} = 1 + 0{,}8 \left( S_{t} - 4{,}5 \right) || (3.4)

NOINDENT: trong đó $S_{t}$ là điểm của cửa hàng sau tuần $t$, $\bar{r}_{t}$ là điểm trung bình các đơn trong tuần và $c_{t}$ là tỷ lệ đơn bị cửa hàng hủy. Hệ số $X$ nhân vào số đơn kỳ vọng của kênh sàn ở công thức (3.1), nên thiếu người làm giảm doanh thu theo hai đường: ngay trong kỳ qua khách bỏ về và đơn bị hủy, và kéo dài nhiều tuần sau khi cửa hàng tụt hạng trên sàn rồi hồi phục dần.

Về kho, hàng tươi được giao mỗi sáng từ thứ Hai đến thứ Bảy, hàng khô vào thứ Hai và thứ Năm; lượng đặt bằng tiêu hao trung bình bảy ngày nhân số ngày dự trữ trừ tồn hiện tại. Tiêu hao thực tế bằng tiêu hao theo công thức của các món đã làm nhân hệ số hao hụt tự nhiên, 1,02–1,05 với hàng tươi và 1,00–1,02 với hàng khô. Đơn sàn không nhập POS và hóa đơn bị hủy do gian lận vẫn tiêu hao nguyên liệu, có chủ đích để P1 và P5 cũng để lại dấu vết chéo ở dữ liệu kho. Kho được kiểm kê vào Chủ nhật, hai tuần một lần.

### 3.3.3. Mô hình lỗi của dữ liệu nguồn

Để phần kỹ thuật dữ liệu phải xử lý vấn đề có thật, mỗi hệ thống nguồn mang các lỗi đặc trưng của dữ liệu do nhiều phần mềm khác nhau tạo ra hoặc do người ghi tay (Bảng 3.6).

TABLE: Bảng 3.6. Các lỗi dữ liệu đặc trưng của từng hệ thống nguồn
WIDTHS: 2,7,3
| Hệ thống | Lỗi được mô phỏng | Chiều chất lượng |
| POS | Ba chi nhánh dùng phiên bản cũ: ngày dạng ISO thay vì dd/mm/yyyy, tiền là chuỗi có dấu chấm ngăn cách (“125.000”), cột tổng tiền mang tên khác, thiếu bốn trường | Nhất quán, hợp lệ |
| POS | Tên món có nhiều biến thể; khoảng 3% đơn sàn không được nhập; một số bản ghi đồng bộ lỗi | Nhất quán, đầy đủ |
| Ứng dụng | Giờ UTC; mã chi nhánh, mã món khác hệ thống trụ sở; tên món tiếng Việt có dấu | Nhất quán |
| GrabFood | Tên cửa hàng nhập tự do; ngày dạng “19 Mar 2024”; không có tỷ lệ hoa hồng | Nhất quán |
| ShopeeFood | Excel có dòng tiêu đề trước bảng; tiêu đề cột tiếng Việt; mã cửa hàng khác | Biểu diễn, nhất quán |
| Sổ nhập kho | Mẫu A có tiêu đề phiếu, tên có dấu, dòng “Tổng cộng”; mẫu B tiếng Anh không dấu, số lượng dính đơn vị (“53.6kg”); khoảng 5% tên viết tắt; khoảng 0,5% số lượng gõ theo gam vào cột kilôgam | Hợp lệ, nhất quán |
| Phiếu kiểm kê | Sai số đếm tay khoảng ±2%; khoảng 2% ô bỏ trống | Chính xác, đầy đủ |
| Máy chấm công | Khoảng 3% lượt quẹt bị ghi trùng; khoảng 5% ca thiếu lượt quẹt ra | Duy nhất, đầy đủ |

### 3.3.4. Kịch bản sự cố và tập đánh giá

Sự cố được đưa vào thế giới chứ không vào từng tệp, nên tự để lại dấu vết ở mọi nguồn liên quan. Khóa luận thiết kế hai tập kịch bản độc lập với hạt giống ngẫu nhiên riêng (Bảng 3.7). Tập kiểm tra cố ý khó hơn: sự cố nhẹ hơn, một số rơi vào chi nhánh nhỏ có ít dữ liệu, và vào sàn khác.

TABLE: Bảng 3.7. Hai tập kịch bản sự cố
WIDTHS: 4,6,6
| Vấn đề | Tập phát triển | Tập kiểm tra |
| P1a. Sàn tính sai hoa hồng | S1: CN4, GrabFood, 13/5–2/6; 30% thay vì 25% | H1: CN10, ShopeeFood, 5/8–18/8; 26% thay vì 22% |
| P1b. Đơn sàn không nhập POS | S2: CN6, 15/7–28/7; 20% đơn | H2: CN3, 22/4–5/5; 15% đơn |
| P2. Hao hụt nguyên liệu tươi | S3: CN7, 10/4–20/4; hao hụt ×1,15–1,30 | H3: CN1, 3/6–14/6; ×1,12–1,25 |
| P3. Thiếu nhân sự ca tối | S4: CN2, 6/5–19/5; điều 55% nhân viên ca tối sang ca sáng | H4: CN8, 22/7–31/7; điều 45% |
| P4. Thất thoát kho | S5: CN9, 17/6–30/6; mất 1,5%/ngày tồn thịt, tôm, phô mai | H5: CN5, 12/8–25/8; mất 1,2%/ngày |
| P5. Gian lận tại quầy | S6: CN8, 1/7–28/7; một thu ngân hủy 12% hóa đơn tiền mặt sau khi thu tiền | H6: CN10, 1/4–28/4; tỷ lệ 10% |

Mọi lựa chọn về phương pháp, cửa sổ thời gian và ngưỡng chỉ được thực hiện trên tập phát triển; tập kiểm tra chỉ chạy một lần khi các bộ phát hiện đã cố định. Chỉ có một điều chỉnh đối với tập kiểm tra: H6 ban đầu đặt ở chi nhánh nhỏ nhất trong ba tuần chỉ tạo ba hóa đơn gian lận, quá ít để phân biệt với nhiễu, nên được chuyển sang một chi nhánh hạng B trong bốn tuần. Điều chỉnh này dựa trên độ lớn tác động và được làm trước khi xây dựng bộ phát hiện nào, nên không ảnh hưởng tính độc lập của đánh giá.

### 3.3.5. Hiệu chỉnh từ dữ liệu giao dịch thật công khai và giới hạn

Hóa đơn chi tiết của chuỗi F&B nằm trong hệ thống nội bộ, không thể thu thập hợp pháp từ bên ngoài, nhưng các quy luật thống kê của hành vi mua hàng có thể ước lượng từ bộ dữ liệu giao dịch thật đã công bố ẩn danh. Đây là bước mô hình hóa dữ liệu đầu vào (input modeling) của phương pháp mô phỏng (Law, 2015). Bộ dữ liệu tham chiếu phải là giao dịch thật chứ không của doanh nghiệp giả định, thuộc loại hình bán đồ ăn, thức uống tại quầy, có từng giao dịch kèm thời điểm và món, và có giấy phép sử dụng; các bộ “đơn hàng nhà hàng” phổ biến được mô tả là của nhà hàng giả định nên bị loại. Bộ được chọn là The Bread Basket, giao dịch thật của một tiệm bánh tại Edinburgh trên OpenML (mã 43422, giấy phép CC0) (Vanschoren et al., 2013), gồm 9.465 giao dịch trong 159 ngày. Toàn bộ việc ước lượng nằm trong `simulator/calibrate_public.py` để tái lập.

Độ dao động theo ngày cần ước lượng cẩn thận. Độ lệch chuẩn thô của logarit số giao dịch mỗi ngày sau khi loại hệ số thứ là 0,381, nhưng con số này gồm cả xu hướng mùa và nhiễu do quy mô nhỏ, trung bình chỉ 59,5 giao dịch mỗi ngày. Độ dao động vì vậy được ước lượng lại theo ba bước: loại xu hướng bằng trung vị trượt 28 ngày, dùng ước lượng vững 1,4826 × MAD, và trừ phần phương sai do bản chất Poisson, xấp xỉ $1/\bar{\lambda}$ trên thang logarit:

EQ: \sigma^{2}_{\text{thêm}} = \sigma^{2}_{\text{vững}} - \frac{1}{\bar{\lambda}} || (3.5)

NOINDENT: trong đó $\bar{\lambda}$ là số giao dịch trung bình mỗi ngày. Kết quả $\sigma_{\text{thêm}} = 0{,}075$, rất gần giá trị 0,08 đã giả định trước, tức giả định ban đầu được dữ liệu thật xác nhận. Bảng 3.8 cho thấy từng quy luật được xét riêng về khả năng chuyển giao: chỉ những quy luật phản ánh hành vi mua hàng chung của loại hình bán tại quầy mới được đưa vào.

TABLE: Bảng 3.8. Kết quả hiệu chỉnh tham số từ dữ liệu giao dịch thật || Tính toán từ dữ liệu The Bread Basket (OpenML, 2022)
WIDTHS: 3.2,2.6,2.4,2.4,4.4
| Quy luật thống kê | Dữ liệu thật | Giả định trước | Sau hiệu chỉnh | Chuyển giao sang bộ mô phỏng? |
| Số món khác nhau mỗi đơn (1 / 2 / 3 / ≥4) | 41,7% / 32,3% / 15,5% / 10,4% | 55% / 30% / 12% / 3% | 42% / 32% / 16% / 10% | Có. Hành vi chọn món chính kèm đồ uống, đồ ăn kèm tương đồng giữa các loại hình phục vụ nhanh |
| Số lượng mỗi dòng món (1 / 2) | 92% / 8% | 90% / 10% | 92% / 8% | Có |
| Độ tập trung món bán chạy | Món đầu 26,7% số phần, 5 món đầu 59,1%; Zipf số mũ 1,06 | Gần như đồng đều | Zipf 1,06 | Có, chỉ lấy độ dốc; thứ tự món là giả định |
| Độ dao động theo ngày | 0,075 (công thức 3.5) | 0,08 | 0,075 | Có; xác nhận giả định |
| Hệ số ngày trong tuần | Thứ Bảy 1,51; Chủ nhật 0,92 | Thứ Bảy 1,20; Chủ nhật 1,15 | Giữ giả định | Không. Tiệm bánh ở khu du lịch có nhịp cuối tuần khác chuỗi đồ ăn nhanh phục vụ gia đình |
| Phân bố theo giờ | Cao điểm 10h–13h, gần như không bán sau 17h | Hai cao điểm trưa và tối | Giữ giả định | Không. Tiệm bánh đóng cửa chiều |

Các tham số hành vi còn lại, như hệ số ngày lễ, mức giảm khách khi mưa hay độ dốc tỷ lệ hủy theo tải, phản ánh đúng chiều tác động đã biết nhưng chưa được hiệu chỉnh bằng dữ liệu thật. Hai giả định còn giới hạn phạm vi phân tích: nhân viên chỉ làm hai ca cố định nên dữ liệu không dùng để đề xuất phân ca theo giờ; khách hàng ứng dụng được chọn theo một phân phối cố định, không có rời bỏ, nên không dùng cho phân tích giữ chân hay phân khúc RFM.

## 3.4. Thiết kế đường ống dữ liệu

Đường ống đưa dữ liệu qua bốn chặng: tầng thu thập nhận và kiểm tra tệp, tầng Bronze lưu bản gốc, tầng Silver làm sạch và chuẩn hóa, tầng Gold tổ chức lại cho phân tích (mục 3.5). Mỗi chặng một trách nhiệm và không làm thay chặng sau, nhờ đó khi một quy tắc làm sạch thay đổi chỉ cần chạy lại từ Bronze mà không phải thu thập lại.

### 3.4.1. Tầng thu thập

Tầng thu thập theo bốn nguyên tắc. Thứ nhất, ba kênh API, tệp xuất tự động và tải lên ghi vào cùng một vùng tiếp nhận, mỗi nguồn một thư mục, nên phần phía sau không phụ thuộc dữ liệu đến bằng kênh nào. Thứ hai, mỗi nguồn có một hợp đồng dữ liệu khai báo định dạng, cột hoặc khóa bắt buộc và cách đọc chi nhánh, ngày từ nội dung; tệp được nhận dạng theo nội dung chứ không theo tên, và tệp sai hợp đồng bị từ chối kèm lý do. Tệp phải khớp hợp đồng trước khi được tính vị trí chuẩn, rồi mới so với tệp đang có ở vị trí đó để phân biệt bản sửa với bản trùng; tệp có nội dung giống hệt tệp khác nhưng rơi vào vị trí khác, như gửi nhầm tên ngày, bị từ chối vì nạp thêm sẽ đếm doanh thu hai lần. Thứ ba, dữ liệu API được kéo tăng dần theo mốc, như Hình 3.4: bộ kết nối lưu ngày kinh doanh cuối cùng đã lấy đủ, mỗi lượt lấy các ngày sau mốc và lấy lại chính ngày mốc để nhận hóa đơn đồng bộ trễ, xử lý lỗi tạm thời và giới hạn tần suất bằng chờ tăng dần, và chỉ ghi dữ liệu, dời mốc khi số bản ghi khớp tổng do API báo; lượt bị gián đoạn vì vậy làm tiếp đúng từ ngày chưa lấy đủ. Thứ tư, lỗi của một nguồn không làm dừng nguồn khác: API không phản hồi không chặn các nguồn tệp, phần dữ liệu thiếu được cửa chặn chất lượng phát hiện (mục 3.6) và bộ phát hiện không kết luận trên phần đó (mục 3.7.3).

IMAGE: figures/h3_seq_api.png || Hình 3.4. Sơ đồ tuần tự của bộ kết nối khi kéo dữ liệu qua API nguồn || 15

### 3.4.2. Tầng Bronze

Tầng Bronze giữ nguyên giá trị gốc: mọi giá trị lưu dạng chuỗi, bản ghi JSON lưu nguyên văn trong cột `payload`, không ép kiểu và không loại dòng nào, kể cả dòng “Tổng cộng” của sổ kho, để khi quy tắc làm sạch thay đổi có thể xử lý lại từ bản gốc. Mỗi dòng mang siêu dữ liệu truy vết gồm tệp nguồn (`_source_file`), mã băm nội dung (`_file_hash`), số dòng trong tệp (`_row_number`), mã lô (`_batch_id`) và thời điểm nạp (`_ingested_at`); với tệp Excel dạng phiếu, các dòng tiêu đề phía trên bảng được giữ trong các cột `_doc_line_k`. Bảng nhật ký `bronze._ingest_log` ghi mọi tệp đã xử lý cùng mã băm MD5: tệp cùng nội dung bị bỏ qua, tệp bị sửa thì bản cũ bị xóa và nạp lại, tệp hỏng hoặc sai hợp đồng được ghi trạng thái và lý do mà không làm dừng các tệp khác. Dữ liệu và nhật ký của mỗi nguồn được ghi trong một giao dịch, nên lỗi giữa chừng không để lại dữ liệu dở dang.

### 3.4.3. Tầng Silver và giải quyết định danh

Tầng Silver chuyển mỗi bảng Bronze thành bảng sạch, đúng kiểu, đúng đơn vị và gắn với định danh chuẩn của hệ thống trụ sở (Bảng 3.9). Bảng `silver_quarantine` lưu mọi dòng bị loại cùng nguồn, tệp, số dòng gốc và quy tắc vi phạm. Bảng `silver_row_reconciliation` đối soát từng nguồn: số dòng Bronze phải bằng số dòng Silver cộng số dòng cách ly cộng số dòng cấu trúc như dòng tổng cộng, chữ ký; phần chênh không giải thích được phải bằng 0.

TABLE: Bảng 3.9. Quy tắc làm sạch và chuẩn hóa chính ở tầng Silver
WIDTHS: 2,7,4
| Nguồn | Xử lý | Dòng vi phạm |
| POS | Hợp nhất hai phiên bản lược đồ: nhận diện định dạng ngày, chuyển “125.000” thành số, đổi tên cột tổng tiền; tách mảng món thành bảng dòng món; xác định chi nhánh từ tiền tố máy POS; giữ hóa đơn hủy, hoàn và gắn cờ | Thiếu hoặc trùng số hóa đơn, tổng tiền không đọc được hoặc âm, không xác định được chi nhánh, hóa đơn không có món → cách ly |
| Ứng dụng | Đổi UTC sang giờ Việt Nam và xác định lại ngày; ánh xạ chi nhánh; ánh xạ món qua tên đã chuẩn hóa; tính thời gian chuẩn bị | Không ánh xạ được món hoặc chi nhánh → cách ly |
| GrabFood, ShopeeFood | Hợp nhất hai định dạng về một lược đồ; tách ngày đầu tuần từ chuỗi kỳ báo cáo; ánh xạ cửa hàng về chi nhánh; tính tỷ lệ hoa hồng hiệu dụng | Không ánh xạ được cửa hàng → cách ly |
| Sổ nhập kho | Hợp nhất hai mẫu; tách dòng tổng cộng, chữ ký; lấy ngày và chi nhánh từ tiêu đề phiếu hoặc đường dẫn; tách số lượng và đơn vị; ánh xạ tên nguyên liệu | Số lượng lớn hơn 20 lần trung vị cùng nguyên liệu, nghi gõ gam vào cột kg → cách ly |
| Phiếu kiểm kê | Lấy ngày, chi nhánh từ tiêu đề; ánh xạ mã nguyên liệu; ô trống giữ là giá trị thiếu kèm cờ, không thay bằng 0 | — |
| Chấm công | Ánh xạ mã nhân viên; ghép cặp vào – ra; ca thiếu lượt ra được gắn cờ, không tự gán số giờ | Lượt quẹt cùng loại lặp lại trong 5 phút → cách ly |
| Danh mục | Dựng lịch sử hiệu lực từ các ảnh chụp danh mục: giá món, vai trò và lương nhân viên | — |

Cùng một thực thể được gọi theo nhiều cách ở các hệ thống khác nhau, và cách giải quyết được chọn theo mức ổn định của thực thể (Bảng 3.10): bảng ánh xạ do người hiểu nghiệp vụ duy trì cho 11 chi nhánh ít thay đổi, quy tắc xác định cho mã có cấu trúc, và khớp nhiều tầng cho tên nguyên liệu nhập tự do.

TABLE: Bảng 3.10. Các hệ thống định danh và cách giải quyết
WIDTHS: 2,7,4
| Thực thể | Cách gọi ở các hệ thống (ví dụ chi nhánh 1, nhân viên 12) | Cách giải quyết |
| Chi nhánh | Trụ sở: 1; POS: `POS-01-…`; ứng dụng: `FNF-Q3-01`; GrabFood: “Fast&Fat - District 3 (#1)”; ShopeeFood: `FASTFAT_DISTRICT3_01`; chấm công: `BR01`; sổ kho: tên trong tiêu đề phiếu | Bảng ánh xạ do người hiểu nghiệp vụ duy trì |
| Nhân viên | Trụ sở và chấm công: 12; POS: `NV0012` | Quy tắc chuẩn hóa xác định |
| Món | Trụ sở: mã 1, tên không dấu; POS: `SKU-001`; ứng dụng: mã riêng, tên có dấu | POS: quy tắc; ứng dụng: khớp tên sau khi bỏ dấu, chuẩn hóa |
| Nguyên liệu | Trụ sở: mã và tên không dấu; sổ kho mẫu A: tên có dấu, đôi khi viết tắt; mẫu B: tên không dấu; kiểm kê: mã `NL01` | Ba tầng: khớp chính xác sau chuẩn hóa → bảng biến thể do người hiểu nghiệp vụ lập → khớp mờ Jaro–Winkler ngưỡng 0,9; không khớp thì cách ly |

## 3.5. Thiết kế kho dữ liệu

### 3.5.1. Bảng sự kiện và ma trận bus

Kho dữ liệu được thiết kế theo phương pháp Kimball với sáu quy trình nghiệp vụ dùng chung các chiều đồng nhất. Bảng 3.11 gộp ma trận bus với hạt dữ liệu và đo lường của từng bảng sự kiện.

TABLE: Bảng 3.11. Các bảng sự kiện: hạt dữ liệu, chiều liên kết và đo lường
WIDTHS: 3.6,3.6,3.4,5
| Bảng sự kiện | Loại, hạt dữ liệu | Chiều liên kết | Đo lường chính |
| `fact_order` | Giao dịch; một đơn ở một kênh | Ngày, chi nhánh, kênh, nhân viên, khách hàng | Tạm tính, giảm giá, tổng tiền, cờ hủy, hoàn, hủy do cửa hàng, thời gian chuẩn bị, phút từ thanh toán đến hủy |
| `fact_order_line` | Giao dịch; một dòng món trong đơn | Ngày, chi nhánh, kênh, món | Số lượng, đơn giá, thành tiền, giá vốn định mức tại ngày bán |
| `fact_marketplace_​settlement` | Ảnh chụp định kỳ; chi nhánh × sàn × tuần | Ngày, chi nhánh, kênh | Doanh thu món, số đơn, đơn hủy, hoa hồng, tỷ lệ hiệu dụng và hợp đồng, khuyến mãi, thực nhận, điểm đánh giá |
| `fact_inventory_receipt` | Giao dịch; một dòng phiếu nhập | Ngày, chi nhánh, nguyên liệu | Số lượng theo đơn vị chuẩn, đơn giá, thành tiền |
| `fact_stock_count` | Ảnh chụp định kỳ; chi nhánh × nguyên liệu × kỳ kiểm kê | Ngày, chi nhánh, nguyên liệu | Tồn đếm được, cờ thiếu số liệu |
| `fact_labor_shift` | Giao dịch; một nhân viên × một ca | Ngày, chi nhánh, nhân viên | Giờ vào, ra, số giờ, cờ thiếu lượt ra, chi phí nhân công theo lương tại ngày làm |

### 3.5.2. Bảng chiều và chiều thay đổi chậm

Kho có bảy bảng chiều. `dim_date` gồm thứ, cuối tuần, ngày lễ, tuần, tháng và thời tiết của ngày, vì thời tiết áp dụng chung cho toàn thành phố. `dim_branch` gồm hạng, quận, tọa độ và toàn bộ mã của chi nhánh ở các hệ thống nguồn. `dim_channel` gồm bốn kênh; `dim_ingredient` gồm đơn vị, nhóm hàng tươi hay khô và đơn giá chuẩn; `dim_customer` gồm mã khách đã băm và ngày mua đầu tiên. Hai chiều `dim_menu_item` (giá bán, giá vốn chuẩn) và `dim_employee` (vai trò, lương giờ) là chiều thay đổi chậm kiểu 2 với ngày bắt đầu, kết thúc hiệu lực và cờ bản hiện hành. Bảng sự kiện liên kết với phiên bản có hiệu lực tại ngày phát sinh, nên giá vốn định mức và chi phí nhân công đúng cả trước và sau mỗi lần điều chỉnh.

Lịch sử của hai chiều này được dựng từ chuỗi ảnh chụp danh mục có ghi ngày mà trụ sở xuất định kỳ, không dùng chức năng *snapshot* của dbt. Snapshot ghi lại trạng thái nguồn tại thời điểm đường ống chạy, nên lịch sử phụ thuộc vào những ngày đường ống đã chạy và mất đi khi kho được dựng lại; ảnh chụp có ngày cho cùng một lịch sử mỗi lần dựng lại, phù hợp với NFR1. Snapshot của dbt chỉ là lựa chọn phù hợp khi nguồn chỉ cung cấp trạng thái hiện tại. Hình 3.5 là sơ đồ quan hệ của kho, sinh trực tiếp từ siêu dữ liệu của dbt.

IMAGE: figures/h3_5_erd.png || Hình 3.5. Sơ đồ quan hệ thực thể của kho dữ liệu (lược đồ hình sao), sinh từ siêu dữ liệu dbt || 16

### 3.5.3. Chiến lược cập nhật kho

Kho dữ liệu lớn thường cập nhật tăng dần: mỗi lượt chỉ tính phần mới rồi gộp vào bảng cũ theo khóa. Khóa luận chọn dựng lại toàn bộ tầng Silver và Gold từ Bronze mỗi lượt, trừ hai mô hình giải mã JSON của POS và ứng dụng, vì ba lý do. Thứ nhất, nguồn được phép sửa lùi: phiếu kiểm kê đếm lại hay báo cáo sàn điều chỉnh thay bản cũ ở Bronze, và nếu gộp theo khóa thì dòng chỉ có trong bản cũ vẫn nằm lại trong kho. Thứ hai, bảng chỉ số dùng cửa sổ trượt tám tuần và so sánh giữa chi nhánh cùng tuần, nên một ngày mới hay một tệp sửa lùi làm đổi kết quả của nhiều tuần trước; tính tăng dần đúng cho các bảng này phức tạp hơn nhiều so với lợi ích. Thứ ba, ở quy mô khoảng nửa triệu dòng, một lượt dựng lại chỉ mất 15 đến 25 giây và kết quả luôn là hàm xác định của Bronze nên dễ kiểm chứng.

Hai mô hình giải mã là ngoại lệ vì tốn thời gian nhất và mỗi tệp giải mã độc lập: chúng chạy tăng dần với khóa là tệp nguồn, tệp được gửi lại bản sửa thì toàn bộ dòng của tệp đó bị xóa và giải mã lại. Như vậy NFR2 được đáp ứng ở hai bước có chi phí tăng theo lượng dữ liệu là nạp Bronze và giải mã; Silver và Gold không tăng dần nhưng vẫn lũy đẳng. Khi một lượt dbt mất tới vài phút, hướng chuyển là cập nhật theo ngày nghiệp vụ: mỗi lượt xóa rồi tính lại các ngày có tệp mới hoặc tệp sửa, cộng một khoảng lùi phủ cửa sổ tám tuần.

## 3.6. Thiết kế kiểm soát chất lượng dữ liệu

Kiểm soát chất lượng gồm bốn lớp nối tiếp trên đường đi của dữ liệu: hợp đồng dữ liệu ở tầng thu thập loại tệp sai cấu trúc trước khi nạp; cửa chặn chất lượng kiểm tra cả lô vừa nạp vào Bronze trước khi dbt chạy; quy tắc cách ly ở tầng Silver (Bảng 3.9); và kiểm thử dbt trên Silver, Gold sau mỗi lần dựng. Kiểm thử dbt được tổ chức theo cách dbt khuyến nghị: ràng buộc phổ biến dùng kiểm thử dựng sẵn khai báo trong tệp cấu hình mô hình; ràng buộc khóa ghép được viết thành một kiểm thử tổng quát bằng macro để dùng lại; luật nghiệp vụ riêng như bảo toàn số dòng hay khớp số tiền được viết thành kiểm thử dạng câu SQL (*singular test*), đạt khi câu truy vấn trả về rỗng (Bảng 3.12).

TABLE: Bảng 3.12. Các nhóm kiểm thử chất lượng dữ liệu
WIDTHS: 2.8,6.6,3.6,2
| Nhóm kiểm thử | Nội dung kiểm tra | Cách hiện thực | Chiều chất lượng |
| Khóa | Khóa của mọi bảng Silver, Gold không trùng, không rỗng; bảng chỉ số không trùng tổ hợp khóa; mỗi chi nhánh × tuần chỉ một dòng đối soát GrabFood | `unique`, `not_null`; kiểm thử tổng quát khóa ghép bằng macro; một kiểm thử SQL | Duy nhất, đầy đủ |
| Toàn vẹn tham chiếu | Mọi khóa chi nhánh, món, nguyên liệu, nhân viên trong bảng sự kiện tồn tại ở bảng chiều | `relationships` | Nhất quán |
| Miền giá trị | Trạng thái đơn, kênh, phiên bản POS, loại lượt chấm công, ca, hạng chi nhánh, sàn, cách khớp nguyên liệu thuộc danh sách cho phép | `accepted_values` | Hợp lệ |
| Bảo toàn số dòng | Mọi nguồn: Bronze bằng Silver cộng cách ly cộng dòng cấu trúc | Kiểm thử SQL | Đầy đủ |
| Nhất quán số tiền | Tạm tính hóa đơn POS bằng tổng dòng món; thực nhận ở báo cáo sàn khớp công thức của báo cáo; doanh thu thuần Gold bằng tổng tính từ Silver theo chi nhánh × ngày | Kiểm thử SQL | Chính xác |
| Lịch sử chiều | Phiên bản của cùng món, cùng nhân viên không chồng lấn, không hở | Kiểm thử SQL | Nhất quán |
| Độ mới | Ngày mới nhất mỗi nguồn không cũ hơn ngưỡng: một ngày với dữ liệu ngày, tám ngày với dữ liệu tuần, mười lăm ngày với kiểm kê | Cửa chặn chất lượng, trước dbt | Kịp thời |
| Đầy đủ theo chi nhánh | Chi nhánh thường gửi POS, chấm công mà một ngày trong lô thiếu tệp thì cảnh báo; từ một phần ba số chi nhánh cùng thiếu thì chặn | Cửa chặn chất lượng, trước dbt | Đầy đủ |

Hai nhóm cuối chạy trên Bronze trước khi dbt dựng lại kho: nếu lô vừa nạp thiếu nghiêm trọng, đường ống dừng và kho phục vụ giữ bản trước thay vì đưa ra kết quả sai.

## 3.7. Thiết kế lớp phân tích

### 3.7.1. Các chỉ số vận hành

Các chỉ số được tính sẵn trong năm bảng chỉ số (mart) của tầng Gold theo các hạt chi nhánh × ngày, chi nhánh × tuần kèm số liệu đối soát sàn, chi nhánh × nguyên liệu × kỳ kiểm kê, thu ngân × tuần, và chi nhánh × tuần × chỉ số kèm mức kỳ vọng, điểm bất thường. Bảng 3.13 trình bày định nghĩa các chỉ số chính.

TABLE: Bảng 3.13. Định nghĩa các chỉ số vận hành trong kho dữ liệu
WIDTHS: 3,6,3
| Chỉ số | Cách tính | Nguồn (bảng Gold) |
| Doanh thu thuần theo kênh | Tiền món sau giảm giá của đơn hoàn thành; kênh sàn theo phần ghi trên POS, doanh thu theo báo cáo sàn dùng để đối soát | `fact_order`, `fact_marketplace_settlement` |
| Số đơn, AOV | Số đơn hoàn thành; doanh thu thuần chia số đơn, theo kênh và toàn chi nhánh | `fact_order` |
| Giá vốn định mức, COGS% | Công thức (2.2) theo phiên bản món tại ngày bán, combo tách thành món thành phần; COGS% theo (2.1) | `fact_order_line`, `dim_menu_item` |
| Hao hụt so với định mức (AvT) | Theo kỳ kiểm kê của từng nguyên liệu: tiêu hao thực tế theo (2.3) trừ tiêu hao định mức bằng số món đã làm × công thức, quy ra tiền | `mart_ingredient_avt` |
| Giờ công, Labor% | Giờ ca nhân lương giờ theo phiên bản nhân viên; ca thiếu lượt ra nội suy bằng trung vị cùng ca, vai trò và gắn cờ; công thức (2.4), chỉ gồm lương giờ trực tiếp | `fact_labor_shift`, `dim_employee` |
| Số ca bếp tối, OPLH | Số ca theo vai trò và ca; số đơn ca tối chia số ca tối; công thức (2.5) | `fact_order`, `fact_labor_shift` |
| Thời gian chuẩn bị, hủy, đánh giá | Thời gian chuẩn bị đơn App và theo báo cáo sàn; tỷ lệ đơn App bị cửa hàng hủy, bị khách hủy vì chờ lâu; điểm đánh giá | `fact_order`, `fact_marketplace_settlement` |
| Hoa hồng hiệu dụng, chênh lệch hợp đồng | Hoa hồng chia doanh thu món theo báo cáo sàn, trừ tỷ lệ hợp đồng có hiệu lực; tiền thu thừa bằng chênh lệch nhân doanh thu món | `fact_marketplace_settlement` |
| Độ phủ POS đơn sàn | Số đơn sàn có trên POS chia số đơn hoàn thành theo báo cáo sàn, theo tuần | `fact_order`, `fact_marketplace_settlement` |
| Hủy, hoàn, giảm giá tại quầy | Theo từng thu ngân: số hóa đơn bị hủy, hoàn, có giảm giá chia số hóa đơn, so với thu ngân khác cùng chi nhánh, cùng tuần | `mart_cashier_weekly` |

Bộ chỉ số giám sát gồm 24 chỉ số thuộc sáu nhóm: kết quả kinh doanh, vận hành và nhân sự, trải nghiệm khách hàng, đối soát sàn, quầy thu ngân và chi phí. Mỗi chỉ số có một chiều bất thường: số ca bếp tối, độ phủ POS và điểm đánh giá thấp là xấu; thời gian chuẩn bị, tỷ lệ hủy và COGS% cao là xấu; doanh thu và số đơn lệch chiều nào cũng đáng chú ý.

### 3.7.2. Mức kỳ vọng và cây KPI truy vết nguyên nhân

Để phân biệt biến động bình thường với biến động do sự cố, mỗi chỉ số của chi nhánh $b$ trong tuần $t$ được so với mức kỳ vọng gồm hai thành phần: mức của các chi nhánh cùng hạng trong chính tuần đó, và độ chênh thường ngày của $b$ so với nhóm. Với chỉ số dạng mức, gọi $x_{b,t}$ là giá trị của chi nhánh và $m_{g,t}$ là trung vị của các chi nhánh khác cùng hạng $g$ trong tuần:

EQ: r_{b,t} = \ln \frac{x_{b,t}}{m_{g,t}}, \qquad \bar{r}_{b,t} = \mathrm{med}\left( r_{b,t-8}, \ldots, r_{b,t-1} \right) || (3.6)

EQ: \hat{x}_{b,t} = m_{g,t}\, e^{\bar{r}_{b,t}}, \qquad z_{b,t} = \frac{r_{b,t} - \bar{r}_{b,t}}{s_{b,t}} || (3.7)

NOINDENT: trong đó $\hat{x}_{b,t}$ là mức kỳ vọng, $s_{b,t}$ là độ dao động tự nhiên bằng 1,4826 lần MAD của $r_{b,t}$ trong tám tuần trước (Rousseeuw & Croux, 1993), có sàn bằng trung vị độ dao động của các chi nhánh cùng chỉ số, cùng tuần. Với chỉ số dạng tỷ lệ, phép chia và logarit được thay bằng phép trừ.

Mỗi lựa chọn có lý do riêng. Ngày lễ, mưa hay điều chỉnh giá tác động lên cả nhóm cùng hạng nên đi vào $m_{g,t}$ và tự triệt tiêu khỏi $r_{b,t}$. Trung vị và MAD được dùng để một tuần bất thường trong quá khứ không kéo lệch mức nền các tuần sau. Sàn độ dao động tránh trường hợp tám tuần quá đều làm $z_{b,t}$ bị thổi phồng. Một chỉ số chỉ được đánh giá khi đã có ít nhất bốn tuần lịch sử.

IMAGE: figures/h3_6_cay_kpi.png || Hình 3.6. Cây KPI dùng để truy vết biến động doanh thu và lợi nhuận || 15

Truy vết một chi nhánh trong một tuần đi theo cây KPI ở Hình 3.6 qua bốn bước. Bước một so doanh thu thuần với mức kỳ vọng theo (3.7): |z| từ 3 là bất thường, từ 2 là cần theo dõi. Bước hai tách doanh thu theo kênh theo (2.9), mỗi kênh thành số đơn và AOV, mỗi nút có mức kỳ vọng riêng; vì ln(doanh thu) = ln(số đơn) + ln(AOV), độ lệch của một kênh xấp xỉ tổng độ lệch hai thành phần, nên dễ thấy biến động nằm ở lượng hay giá. Bước ba đối chiếu các chỉ số vận hành gắn với nhánh đó trong cùng tuần và các tuần trước, vì một số tác động đến trễ qua thứ hạng sàn; chẳng hạn số đơn sàn giảm kèm thời gian chuẩn bị tăng, cửa hàng tự hủy đơn tăng và số ca bếp tối giảm là dấu hiệu của P3. Bước bốn xếp hạng các giả thuyết P1–P5 bằng các bộ phát hiện ở mục 3.7.3. Các nhánh chi phí như giá vốn và phí sàn không làm đổi doanh thu bán hàng, nên được giám sát trực tiếp bằng P1a, P2 và P4.

### 3.7.3. Thiết kế các bộ phát hiện

Mỗi bộ phát hiện cho một điểm bằng chứng từ 0 đến 6 cho một giả thuyết, ở mỗi chi nhánh và tuần. Với tín hiệu đã quy về z, điểm là phần z vượt theo đúng chiều bất thường, cắt trong [0, 6]; với kiểm định trên số đếm, xác suất đuôi được đổi ra z tương đương trước khi cắt (Bảng 3.14).

TABLE: Bảng 3.14. Thiết kế năm bộ phát hiện
WIDTHS: 2,2.6,6.6,2.3
| Bộ phát hiện | Đơn vị đánh giá | Phương pháp | Loại |
| P1a. Hoa hồng sai hợp đồng | Chi nhánh × sàn × tuần | Tỷ lệ hiệu dụng trên báo cáo trừ tỷ lệ hợp đồng có hiệu lực; vượt dung sai 0,5 điểm % thì nhận điểm tối đa | Luật nghiệp vụ |
| P1b. Đơn sàn không vào POS | Chi nhánh × sàn × tuần | Số đơn sàn báo hoàn thành mà không có trên POS so với tỷ lệ thiếu thường ngày của chi nhánh (trung vị các tuần trước, sàn 1%) bằng kiểm định Poisson; hiệu chỉnh Bonferroni cho hai sàn (Dunn, 1961) | Kiểm định |
| P2. Hao hụt vượt định mức | Chi nhánh × kỳ kiểm kê | Hao hụt mỗi ngày của hàng tươi giá thấp chia tiêu hao định mức thường ngày; so cắt ngang với các chi nhánh khác cùng kỳ bằng trung vị và MAD, sàn 0,5 điểm % | Thống kê |
| P3. Thiếu nhân sự, bếp quá tải | Chi nhánh × tuần | Trung bình điểm của năm tín hiệu: số ca bếp tối thấp, thời gian chuẩn bị App và Grab cao, tỷ lệ cửa hàng tự hủy đơn App cao, tỷ lệ khách hủy vì chờ lâu cao | Thống kê, gộp bằng chứng |
| P4. Thất thoát hàng giá trị cao | Chi nhánh × kỳ kiểm kê | Như P2 cho nguyên liệu giá chuẩn từ 80.000 đồng mỗi đơn vị; điểm giảm một nửa khi hàng tươi giá thấp cũng vượt, hoặc khi P1b đủ bằng chứng | Thống kê, gộp bằng chứng |
| P5. Gian lận tại quầy | Thu ngân × tuần | Số hóa đơn bị hủy, hoàn, giảm giá của từng thu ngân so với tỷ lệ của thu ngân khác cùng chi nhánh, cùng tuần; kiểm định Poisson, hiệu chỉnh Bonferroni theo số phép thử; chỉ xét thu ngân có từ 30 hóa đơn | Kiểm định |

Hai quyết định cần giải thích. P1a dùng luật thay vì thống kê, vì nếu sàn tính sai liên tục thì mức nền lịch sử cũng sai theo và z không bao giờ phát hiện được. P5 đánh giá từng thu ngân thay vì tỷ lệ cấp chi nhánh, vì gian lận gắn với người thực hiện và ở chi nhánh nhỏ tỷ lệ cấp chi nhánh dao động mạnh. Từ điểm bằng chứng, mỗi chi nhánh × tuần được xếp vào ba mức. Mức cảnh báo khi giả thuyết mạnh nhất có điểm từ 3,5, hoặc doanh thu lệch kỳ vọng với |z| từ 3; trường hợp sau mà không giả thuyết nào đủ điểm thì nguyên nhân ghi là "chưa xác định", không gán bừa. Mức theo dõi khi điểm hoặc |z| từ 2; còn lại là bình thường. Ngưỡng 3,5 được chọn trên tập phát triển theo F1 lớn nhất.

Dữ liệu nguồn thiếu tạo ra đúng những tín hiệu mà bộ phát hiện tìm kiếm: thiếu tệp POS một ngày thì doanh thu thấp và đơn sàn "biến mất" khỏi POS như P1b, lượng bán thấp lại làm hao hụt tăng như P2, P4; thiếu tệp chấm công thì số ca bếp thấp như P3. Vì vậy có hai quy tắc không kết luận. Chi nhánh có ngày thiếu dữ liệu POS hoặc chấm công trong tuần thì các giả thuyết dựa trên nguồn đó chỉ ở mức theo dõi, kèm ghi chú chưa kết luận. Khi từ một phần ba số chi nhánh cùng thiếu, chẳng hạn vì API nguồn không phản hồi, trung vị nhóm so sánh bị kéo lệch, nên các giả thuyết dựa trên so sánh giữa chi nhánh, gồm doanh thu, P2, P3 và P4, cũng không kết luận. Lượt chạy sau tự đánh giá lại khi tệp về đủ; P1a dựa trên báo cáo sàn và hợp đồng nên không bị ảnh hưởng.

Mỗi cảnh báo gồm chi nhánh, tuần, nguyên nhân hạng một và hạng hai cùng điểm, bằng chứng dạng chữ như "NV0093: 20/270 hóa đơn bị hủy, tức 7,4%, thu ngân khác 1,0%", và doanh thu thực tế so với kỳ vọng. Lớp phân tích bổ sung đề xuất xử lý cho từng nguyên nhân gồm việc cần xác minh, việc cần làm, việc theo dõi, người phụ trách, thời hạn và thiệt hại ước tính, nên danh sách cảnh báo được sắp theo thiệt hại (FR6). Người phụ trách phải xác minh bằng nguồn ngoài hệ thống trước khi xử lý, vì thống kê chỉ cho biết nghi vấn; tuần kế tiếp, nếu chỉ số còn lệch so với mức kỳ vọng thì cảnh báo xuất hiện lại. Nền tảng chưa lưu trạng thái giao việc, nên việc theo dõi kết quả xử lý dựa vào chính các chỉ số tuần sau.

## 3.8. Thiết kế ứng dụng, kho phục vụ và điều phối

### 3.8.1. Ứng dụng và truy vết về dữ liệu gốc

Ứng dụng là một địa chỉ duy nhất cho người dùng nghiệp vụ và kỹ sư dữ liệu. Sau trang chủ là sơ đồ hệ thống, các trang xếp theo dòng dữ liệu thành bốn nhóm: Nguồn dữ liệu gồm kết nối nguồn, tải tệp lên và xem tệp gốc; Dữ liệu gồm vận hành hằng ngày, kho dữ liệu có ô truy vấn SQL, mô hình và phả hệ, chất lượng dữ liệu; Phân tích vận hành gồm tổng quan, trung tâm cảnh báo và truy vết nguyên nhân; Kiểm chứng gồm bộ mô phỏng và đánh giá bộ phát hiện, là nhóm duy nhất đọc đáp án và tách khỏi phần sản phẩm. Mọi trang dùng chung bộ lọc môi trường dữ liệu, chi nhánh và khoảng thời gian; môi trường mặc định là môi trường vận hành, nơi duy nhất nhận dữ liệu mới.

Một kết luận chỉ đáng tin khi người dùng kiểm tra lại được trên dữ liệu mà hệ thống nguồn đã xuất. Yêu cầu này được đáp ứng nhờ phả hệ ở mức bản ghi (Simmhan et al., 2005): Bronze lưu tên tệp và số dòng gốc của mỗi dòng, các tầng sau mang theo khóa bản ghi, nên từ một cảnh báo có thể đi ngược về đúng dòng trong tệp gốc. Trang Truy vết đọc kho ở chế độ chỉ đọc, chấm điểm, lập đề xuất và truy vấn các bản ghi bằng chứng kèm tên tệp, số dòng; nút mở tệp gốc chuyển sang trang Tệp nguồn, nơi tệp được đọc lại nguyên văn từ vùng tiếp nhận chứ không phải bản đã qua xử lý.

### 3.8.2. Kho phục vụ và công cụ BI

Sau mỗi lượt chạy thành công, tầng Gold cùng bảng cảnh báo và nhật ký vận hành được sao sang PostgreSQL: nạp vào lược đồ tạm, đối soát số dòng từng bảng với DuckDB, rồi đổi lược đồ tạm thành lược đồ chính trong một giao dịch, nên người đọc chỉ thấy bản cũ hoặc bản mới hoàn chỉnh. Metabase kết nối bằng tài khoản chỉ đọc và phục vụ các báo cáo chuẩn về doanh thu, đơn, AOV, COGS%, Labor%, kênh, chi nhánh, thực đơn và cảnh báo; ứng dụng chỉ tự xây những trang cần logic riêng như cảnh báo và truy vết.

### 3.8.3. Điều phối

Điều phối gồm hai đồ thị tác vụ Airflow theo đúng vai trò trong doanh nghiệp (Hình 3.7). DAG `fastfat_nguon` đóng vai hệ thống nguồn, lúc 23 giờ ghi dữ liệu của ngày kinh doanh vừa kết thúc rồi báo cập nhật một Dataset. DAG `fastfat_pipeline` là đường ống, chạy ngay khi Dataset cập nhật và tự kiểm tra thêm mỗi giờ để kéo dữ liệu API và nhận tệp do người gửi; không có tệp mới thì lượt kết thúc ngay ở bước kiểm tra. Cửa chặn chất lượng giữa Bronze và Silver kiểm tra độ mới, khối lượng so với trung vị 14 ngày, độ đầy đủ theo chi nhánh, tệp bị từ chối và thay đổi cấu trúc; mức chặn gồm nguồn hằng ngày chậm từ bốn ngày, một ngày không có dòng nào, và từ một phần ba số chi nhánh cùng thiếu. Có mục ở mức chặn hoặc một kiểm thử dbt thất bại thì các bước sau không chạy, nên không có cảnh báo hay báo cáo nào từ dữ liệu sai; API không phản hồi chỉ là cảnh báo, không chặn các nguồn tệp. Vì DuckDB chỉ cho một tiến trình ghi, mỗi lúc chỉ một lượt đường ống được chạy.

IMAGE: figures/h3_7_dag.png || Hình 3.7. Hai đồ thị tác vụ: hệ thống nguồn và đường ống dữ liệu kích hoạt theo dữ liệu mới || 16

## 3.9. Tiểu kết chương

Chương này đã chuyển ba câu hỏi nghiên cứu thành giả thuyết thiết kế, yêu cầu và một thiết kế cụ thể có tiêu chí kiểm chứng. Bộ mô phỏng tạo một thế giới vận hành nhất quán, trong đó mỗi hệ thống nguồn chỉ thấy phần của mình và mang lỗi riêng, còn sự cố để lại dấu vết đồng thời ở nhiều nguồn. Đường ống đi qua tầng thu thập, Bronze, Silver và Gold, mỗi tầng một trách nhiệm, với kiểm soát chất lượng ở cả đầu vào lẫn bên trong kho. Lớp phân tích so mỗi chỉ số với mức kỳ vọng tính từ nhóm cùng hạng và lịch sử của chính chi nhánh, rồi dùng năm bộ phát hiện để chấm điểm từng giả thuyết nguyên nhân. Chương 4 trình bày việc hiện thực thiết kế này và các kết quả đo được.
