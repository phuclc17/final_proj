# LỜI CAM ĐOAN

Tôi xin cam đoan khóa luận “Xây dựng nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn hỗ trợ truy vết nguyên nhân biến động doanh thu cho chuỗi F&B” là công trình nghiên cứu của riêng tôi dưới sự hướng dẫn của TS. Ngô Tấn Vũ Khanh.

Các số liệu, kết quả trong khóa luận là trung thực. Dữ liệu dùng trong khóa luận là dữ liệu mô phỏng, cách xây dựng được trình bày ở Chương 3. Các tài liệu tham khảo đều được trích dẫn đầy đủ.

Nếu có sai sót, tôi xin hoàn toàn chịu trách nhiệm.

RIGHT: *TP. Hồ Chí Minh, ngày … tháng 10 năm 2026*

RIGHT: **Sinh viên thực hiện**

RIGHT: Lê Cao Phúc

# LỜI CẢM ƠN

Em xin chân thành cảm ơn TS. Ngô Tấn Vũ Khanh đã hướng dẫn và góp ý cho em trong suốt quá trình làm khóa luận.

Em xin cảm ơn quý thầy cô Khoa Công nghệ Thông tin Kinh doanh, Trường Công nghệ và Thiết kế, Đại học Kinh tế TP. Hồ Chí Minh đã truyền đạt kiến thức cho em trong những năm học tại trường.

Em cũng cảm ơn gia đình và bạn bè đã luôn động viên em.

Do kiến thức và thời gian còn hạn chế, khóa luận không tránh khỏi thiếu sót. Em rất mong nhận được góp ý của quý thầy cô.

TODO: viết thêm lời cảm ơn cụ thể.

RIGHT: **Sinh viên thực hiện**

RIGHT: Lê Cao Phúc

# TÓM TẮT

Các chuỗi đồ ăn nhanh hiện bán hàng đồng thời tại quầy, qua ứng dụng riêng và qua các sàn giao đồ ăn, nên dữ liệu vận hành nằm rải rác ở máy bán hàng (POS), ứng dụng, báo cáo của sàn, sổ kho và máy chấm công, mỗi nơi một định dạng và một bộ mã riêng. Khi doanh thu hay lợi nhuận biến động, nhà quản lý thường chỉ thấy con số tổng hợp và khó phân biệt biến động bình thường với sự cố vận hành. Các nghiên cứu trước thường chỉ phân tích một nguồn dữ liệu cho một loại sự cố.

Theo phương pháp nghiên cứu khoa học thiết kế, khóa luận xây dựng một nền tảng tích hợp dữ liệu vận hành đa nguồn và truy vết nguyên nhân biến động doanh thu cho chuỗi đồ ăn nhanh. Do dữ liệu doanh nghiệp không được công khai, đề tài xây dựng bộ mô phỏng bảy hệ thống nguồn của một chuỗi 11 chi nhánh: dữ liệu nhất quán về nhân quả, có lỗi nhập liệu như thực tế, một số quy luật mua hàng được hiệu chỉnh từ dữ liệu giao dịch thật công khai, kèm hai tập kịch bản sự cố độc lập có đáp án. Dữ liệu được thu thập qua API, tệp xuất tự động và tệp tải lên, xử lý theo kiến trúc Medallion bằng DuckDB và dbt thành kho dữ liệu hình sao có kiểm thử. Năm bộ phát hiện dựa trên thống kê vững, kiểm định Poisson và luật đối soát, cùng một cây KPI, phát hiện và truy vết năm vấn đề vận hành; toàn bộ được điều phối bằng Airflow và phục vụ qua Metabase và Streamlit.

Đường ống đạt cả 158 kiểm thử dữ liệu, không thất lạc dòng nào giữa các tầng và xử lý một ngày dữ liệu mới trong khoảng 80 giây. Trên tập kiểm tra độc lập, chạy một lần với tham số đã chốt trước, hệ thống phát hiện 4 trên 6 sự cố với F1 0,52 và độ trễ trung vị 6 ngày, trong đó 3 sự cố được gán đúng nguyên nhân; trên tập phát triển là 5 trên 6 với F1 0,79. Chỉ theo dõi doanh thu phát hiện được nhiều nhất 1 sự cố. Biến động của ngày lễ, ngày mưa và điều chỉnh giá không bị nhầm thành sự cố; thất thoát kho với nhịp kiểm kê hai tuần là loại sự cố chưa phát hiện được.

Kết quả cho thấy việc đối chiếu chéo các nguồn dữ liệu vận hành phát hiện được những sự cố mà chỉ số doanh thu không thể hiện, và một chuỗi F&B quy mô vừa có thể xây dựng nền tảng như vậy bằng công cụ mã nguồn mở.

NOINDENT: **Từ khóa:** kỹ thuật dữ liệu, kho dữ liệu, kiến trúc Medallion, chất lượng dữ liệu, phát hiện bất thường, truy vết nguyên nhân, F&B, dữ liệu mô phỏng.

# ABSTRACT

Fast-food chains now sell over the counter, through their own ordering apps and on food delivery platforms, so their operational data is spread across point-of-sale (POS) systems, apps, platform reports, inventory records and time clocks, each with its own format and identifiers. When revenue or profit changes, managers usually see only aggregate figures and cannot tell a normal fluctuation from an operational problem. Previous studies typically analyse a single data source for a single type of incident.

Following a design science approach, this thesis builds a platform that integrates multi-source operational data and traces the causes of revenue changes in a fast-food chain. Because real operational data is not publicly available, a simulator of seven source systems was built for a chain of 11 branches. It produces causally consistent data with realistic entry errors, partly calibrated on public transaction data, and injects incidents with known ground truth into two independent scenario sets. Data collected through APIs, scheduled exports and uploads is processed in a Medallion architecture with DuckDB and dbt into a tested star-schema warehouse. Five detectors based on robust statistics, Poisson tests and reconciliation rules, together with a KPI tree, detect and explain five operational problems; the pipeline is orchestrated with Airflow and served through Metabase and Streamlit.

The pipeline passes all 158 data tests, loses no rows between layers and processes a new day of data in about 80 seconds. On the independent test set, evaluated once with parameters fixed in advance, the system detects four of six incidents with an F1 score of 0.52 and a median delay of six days, and assigns the correct cause to three of them; on the development set it detects five of six with an F1 score of 0.79. Monitoring revenue alone detects at most one incident. Holidays, rain and price changes are not mistaken for incidents; inventory theft remains undetected under a two-week stock-count cycle. Cross-checking operational sources thus reveals incidents that revenue figures hide, using only open-source tools.

NOINDENT: **Keywords:** data engineering, data warehouse, Medallion architecture, data quality, anomaly detection, root cause analysis, food and beverage, synthetic data.

#! MỤC LỤC

[[TOC]]

# DANH MỤC TỪ VIẾT TẮT

TABLE:
WIDTHS: 2,5,5
| Từ viết tắt | Tiếng Anh | Tiếng Việt |
| AOV | Average Order Value | Giá trị trung bình mỗi đơn hàng |
| AvT | Actual versus Theoretical (food cost) | Chênh lệch giá vốn thực tế so với lý thuyết |
| BI | Business Intelligence | Công cụ báo cáo, phân tích kinh doanh |
| COGS | Cost of Goods Sold | Giá vốn hàng bán |
| CSV | Comma-Separated Values | Tệp văn bản phân tách bằng dấu phẩy |
| DA | Data Analytics | Phân tích dữ liệu |
| DAG | Directed Acyclic Graph | Đồ thị có hướng không chu trình |
| DE | Data Engineering | Kỹ thuật dữ liệu |
| DQ | Data Quality | Chất lượng dữ liệu |
| ELT | Extract – Load – Transform | Trích xuất – Nạp – Biến đổi |
| ETL | Extract – Transform – Load | Trích xuất – Biến đổi – Nạp |
| F&B | Food and Beverage | Ngành ăn uống |
| FIFO | First In, First Out | Nhập trước, xuất trước |
| JSON | JavaScript Object Notation | Định dạng dữ liệu JSON |
| KPI | Key Performance Indicator | Chỉ số hiệu suất then chốt |
| MAD | Median Absolute Deviation | Độ lệch tuyệt đối trung vị |
| OLAP | Online Analytical Processing | Xử lý phân tích trực tuyến |
| OPLH | Orders per Labor Hour | Số đơn trên mỗi giờ công |
| POS | Point of Sale | Hệ thống bán hàng tại quầy |
| QSR | Quick-Service Restaurant | Nhà hàng phục vụ nhanh (đồ ăn nhanh) |
| RFM | Recency – Frequency – Monetary | Gần đây – Tần suất – Giá trị |
| RQ | Research Question | Câu hỏi nghiên cứu |
| SCD | Slowly Changing Dimension | Chiều thay đổi chậm |
| SPLH | Sales per Labor Hour | Doanh thu trên mỗi giờ công |
| SQL | Structured Query Language | Ngôn ngữ truy vấn có cấu trúc |
| UTC | Coordinated Universal Time | Giờ phối hợp quốc tế |

# DANH MỤC BẢNG

[[LIST_TABLES]]

# DANH MỤC HÌNH

[[LIST_FIGURES]]

[[END_FRONT]]
