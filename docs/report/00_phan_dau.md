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

Các chuỗi kinh doanh đồ ăn nhanh hiện bán hàng đồng thời qua nhiều kênh: tại quầy, ứng dụng riêng và các sàn giao đồ ăn. Dữ liệu vận hành vì vậy bị phân tán ở nhiều hệ thống có định dạng, mã định danh và chất lượng khác nhau, gồm hệ thống bán hàng tại quầy (POS), ứng dụng đặt hàng, báo cáo đối soát của sàn, sổ nhập kho, phiếu kiểm kê và máy chấm công. Khi doanh thu hay lợi nhuận biến động, nhà quản lý thường chỉ quan sát được ở mức tổng hợp và khó xác định nguyên nhân là do yếu tố bình thường như mùa vụ, thời tiết, hay do sự cố vận hành như sai lệch đối soát, thất thoát nguyên liệu, thiếu nhân sự hoặc gian lận tại quầy.

Khóa luận xây dựng một nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn nhằm hỗ trợ truy vết nguyên nhân biến động doanh thu cho chuỗi F&B. Do dữ liệu vận hành của doanh nghiệp không được công khai, đề tài xây dựng một bộ mô phỏng theo nguyên lý “một thế giới, nhiều góc nhìn”: các sự kiện vận hành được sinh một lần theo các quan hệ nhân quả, với một số phân phối hành vi mua hàng được hiệu chỉnh từ dữ liệu giao dịch thật công khai, sau đó mỗi hệ thống nguồn xuất phần dữ liệu nó quan sát được kèm các lỗi đặc trưng. Bộ mô phỏng sinh dữ liệu 26 tuần cho 11 chi nhánh với khoảng 435 nghìn đơn hàng, dưới dạng tệp JSON, CSV và Excel của bảy hệ thống vận hành, cùng dữ liệu danh mục và thời tiết. Dữ liệu đến nền tảng bằng ba kênh như ngoài thực tế: bộ kết nối kéo tăng dần qua API của phần mềm POS đám mây và ứng dụng đặt hàng, tệp xuất tự động, và tệp do người gửi; mỗi tệp được kiểm tra theo hợp đồng dữ liệu của nguồn. Trên dữ liệu này, khóa luận xây dựng đường ống dữ liệu theo kiến trúc Medallion (Bronze, Silver, Gold) với DuckDB và dbt, mô hình hóa kho dữ liệu dạng lược đồ hình sao, kiểm thử chất lượng dữ liệu giữa các tầng, xây dựng bộ chỉ số vận hành, cây KPI để truy vết và năm bộ phát hiện bất thường cho năm vấn đề vận hành. Kết quả được đưa sang kho phục vụ PostgreSQL cho dashboard Metabase và một ứng dụng Streamlit; Airflow tự chạy đường ống khi có dữ liệu mới. Ngưỡng của các bộ phát hiện được chọn trên một tập kịch bản phát triển và đánh giá trên một tập kịch bản kiểm tra độc lập.

Đường ống vượt qua 158 kiểm thử dữ liệu, đối soát số dòng giữa các tầng không có chênh lệch không giải thích được, và xử lý một ngày dữ liệu mới trong khoảng 80 giây. Trên tập kiểm tra, hệ thống phát hiện bốn trên sáu sự cố với F1 0,52 và độ trễ trung vị 6 ngày, so với năm trên sáu và F1 0,79 trên tập phát triển. Ở mọi sự cố có tín hiệu, nguyên nhân đúng được xếp hạng một, và biến động của ngày lễ, ngày mưa không bị nhầm thành sự cố. Trong khi đó, chỉ theo dõi doanh thu phát hiện được nhiều nhất một sự cố. Thất thoát kho với nhịp kiểm kê hai tuần là loại sự cố chưa phát hiện được. Trong thử nghiệm 11 tình huống dữ liệu bất thường cùng lúc và một lần API nguồn không phản hồi, đường ống xử lý đúng mọi tình huống, không đưa ra cảnh báo từ dữ liệu thiếu và tự xử lý tiếp khi dữ liệu về đủ.

NOINDENT: **Từ khóa:** kỹ thuật dữ liệu, kho dữ liệu, kiến trúc Medallion, chất lượng dữ liệu, phát hiện bất thường, truy vết nguyên nhân, F&B, dữ liệu mô phỏng.

# ABSTRACT

Quick-service restaurant chains sell through several channels at the same time: in-store, a proprietary ordering app and food-delivery marketplaces. Their operational data is therefore scattered across systems with different formats, identifiers and quality levels, including point-of-sale (POS) exports, app orders, marketplace settlement reports, goods-received notes, stock-count sheets and time-clock logs. When revenue or profit fluctuates, managers usually observe only aggregate figures and cannot tell whether the change is caused by normal factors such as seasonality and weather, or by operational problems such as settlement discrepancies, ingredient waste, understaffing or cashier fraud.

This thesis builds a platform that integrates and analyses multi-source operational data to support root-cause tracing of revenue fluctuations in an F&B chain. Because real operational data is commercially sensitive and unavailable, the study designs a simulator based on a “one world, many views” principle: operational events are generated once according to explicit causal relations, with several purchasing-behaviour distributions calibrated on a public real-world transaction dataset, and each source system then exports only the part it observes, together with its own characteristic data defects. The simulator produces 26 weeks of data for 11 branches with about 435 thousand orders, delivered as JSON, CSV and Excel files from seven operational systems, plus master data and weather. Data reaches the platform through the three channels used in practice: a connector that incrementally pulls the cloud POS and ordering-app APIs, scheduled file exports, and files submitted by staff, each checked against the data contract of its source. On top of this data, the thesis implements a Medallion pipeline (Bronze, Silver, Gold) with DuckDB and dbt, a star-schema data warehouse, cross-layer data quality tests, a set of operational KPIs, a KPI tree for root-cause tracing and five anomaly detectors for five operational problems. Results are published to a PostgreSQL serving database for a Metabase dashboard and a Streamlit application, and Airflow runs the pipeline whenever new source files arrive. Detectors are calibrated on one scenario set and evaluated on an independent hold-out scenario set.

The pipeline passes 158 data tests, row-count reconciliation between layers shows no unexplained difference, and one new day of data is processed in about 80 seconds. On the hold-out set, the system detects four of six incidents with an F1 of 0.52 and a median delay of six days, compared with five of six and an F1 of 0.79 on the development set. Whenever an incident produced a signal, the correct cause was ranked first, and holiday or rain effects were not mistaken for incidents. Monitoring revenue alone detects at most one incident. Inventory theft under a two-week stock-count cycle remains undetected. In a test with eleven simultaneous data defects and an outage of the source API, the pipeline handled every case correctly, raised no alert from incomplete data, and resumed on its own once the data arrived.

NOINDENT: **Keywords:** data engineering, data warehouse, Medallion architecture, data quality, anomaly detection, root-cause analysis, food and beverage, synthetic data.

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
