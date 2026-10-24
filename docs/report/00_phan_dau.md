# LỜI CAM ĐOAN

Tôi xin cam đoan khóa luận “Xây dựng nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn hỗ trợ truy vết nguyên nhân biến động doanh thu cho chuỗi F&B” là công trình nghiên cứu của riêng tôi, được thực hiện dưới sự hướng dẫn của TS. Ngô Tấn Vũ Khanh.

Các số liệu và kết quả trình bày trong khóa luận là trung thực, được đo trực tiếp trên hệ thống do tôi xây dựng. Dữ liệu sử dụng là dữ liệu mô phỏng, cách xây dựng và kiểm chứng được trình bày ở Chương 3 và Chương 4. Các tài liệu tham khảo đều được trích dẫn đầy đủ.

Tôi xin hoàn toàn chịu trách nhiệm về nội dung của khóa luận.

RIGHT: *TP. Hồ Chí Minh, ngày … tháng 10 năm 2026*

RIGHT: **Sinh viên thực hiện**

RIGHT: Lê Cao Phúc

# LỜI CẢM ƠN

Lời đầu tiên, em xin gửi lời cảm ơn sâu sắc đến giảng viên hướng dẫn, TS. Ngô Tấn Vũ Khanh, Đại học Kinh tế TP. Hồ Chí Minh. Sự định hướng và những góp ý trong suốt quá trình thực hiện đã giúp em đi đúng mục tiêu và hoàn thành khóa luận này. Qua quá trình làm khóa luận, em đã học được rất nhiều điều.

Em xin cảm ơn quý thầy cô Khoa Công nghệ Thông tin Kinh doanh, Trường Công nghệ và Thiết kế, đã truyền đạt kiến thức cho em trong những năm học tại trường; những kiến thức đó là nền tảng để em thực hiện đề tài. Em cũng xin cảm ơn gia đình và bạn bè đã luôn tin tưởng, động viên và tạo điều kiện cho em trong thời gian làm khóa luận.

Nhiều kiến thức về kỹ thuật dữ liệu và về nghiệp vụ vận hành chuỗi F&B em phải tự tìm hiểu từ đầu, kinh nghiệm thực tế còn ít, nên khóa luận khó tránh khỏi thiếu sót. Em rất mong nhận được những góp ý quý báu của quý thầy cô để hoàn thiện hơn. Với em, khóa luận không chỉ là điều kiện tốt nghiệp mà còn là kết quả của sự cố gắng trong một khoảng thời gian ngắn.

RIGHT: Lê Cao Phúc

RIGHT: Tháng 10 năm 2026

# TÓM TẮT

Các chuỗi đồ ăn nhanh bán hàng đồng thời tại quầy, qua ứng dụng riêng và qua các sàn giao đồ ăn, nên dữ liệu vận hành nằm rải rác ở máy bán hàng (POS), ứng dụng, báo cáo của sàn, sổ kho và máy chấm công, mỗi nơi một định dạng và một bộ mã riêng. Khi doanh thu hay lợi nhuận biến động, nhà quản lý thường chỉ thấy con số tổng hợp và khó phân biệt biến động bình thường với sự cố vận hành. Các nghiên cứu trước thường chỉ phân tích một nguồn dữ liệu cho một loại sự cố.

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

NOINDENT: 1. API: Application Programming Interface – Giao diện lập trình ứng dụng
NOINDENT: 2. AOV: Average Order Value – Giá trị trung bình mỗi đơn hàng
NOINDENT: 3. AvT: Actual versus Theoretical – Chênh lệch giá vốn thực tế so với định mức
NOINDENT: 4. BI: Business Intelligence – Báo cáo, phân tích kinh doanh
NOINDENT: 5. COGS: Cost of Goods Sold – Giá vốn hàng bán
NOINDENT: 6. CSV: Comma-Separated Values – Tệp văn bản phân tách bằng dấu phẩy
NOINDENT: 7. DAG: Directed Acyclic Graph – Đồ thị có hướng không chu trình
NOINDENT: 8. ELT: Extract – Load – Transform – Trích xuất, nạp, biến đổi
NOINDENT: 9. ETL: Extract – Transform – Load – Trích xuất, biến đổi, nạp
NOINDENT: 10. F&B: Food and Beverage – Ngành ăn uống
NOINDENT: 11. FIFO: First In, First Out – Nhập trước, xuất trước
NOINDENT: 12. JSON: JavaScript Object Notation – Định dạng dữ liệu JSON
NOINDENT: 13. KPI: Key Performance Indicator – Chỉ số hiệu suất then chốt
NOINDENT: 14. MAD: Median Absolute Deviation – Độ lệch tuyệt đối trung vị
NOINDENT: 15. OPLH: Orders per Labor Hour – Số đơn trên mỗi giờ công
NOINDENT: 16. POS: Point of Sale – Hệ thống bán hàng tại quầy
NOINDENT: 17. RFM: Recency – Frequency – Monetary – Gần đây, tần suất, giá trị
NOINDENT: 18. RQ: Research Question – Câu hỏi nghiên cứu
NOINDENT: 19. SCD: Slowly Changing Dimension – Chiều thay đổi chậm
NOINDENT: 20. SPLH: Sales per Labor Hour – Doanh thu trên mỗi giờ công
NOINDENT: 21. SQL: Structured Query Language – Ngôn ngữ truy vấn có cấu trúc
NOINDENT: 22. UML: Unified Modeling Language – Ngôn ngữ mô hình hóa thống nhất
NOINDENT: 23. UTC: Coordinated Universal Time – Giờ phối hợp quốc tế

# DANH MỤC BẢNG

[[LIST_TABLES]]

# DANH MỤC HÌNH

[[LIST_FIGURES]]

[[END_FRONT]]
