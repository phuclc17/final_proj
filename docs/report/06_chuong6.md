# CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

Chương này tổng kết kết quả của khóa luận theo các mục tiêu đã đặt ra, nêu những điều chỉnh so với đề cương, các hạn chế còn tồn tại và hướng phát triển.

## 6.1. Kết quả đạt được

Đối chiếu với các mục tiêu cụ thể ở mục 1.4.2, khóa luận đã đạt được các kết quả sau.

- Về bộ dữ liệu mô phỏng, theo mục tiêu thứ nhất: bộ mô phỏng theo nguyên lý “một thế giới, nhiều góc nhìn” sinh dữ liệu nhất quán về nhân quả cho bảy hệ thống vận hành cùng danh mục và thời tiết, có đủ các lỗi dữ liệu đặc trưng, thành hai tập độc lập 26 tuần với 385 đến 435 nghìn đơn mỗi tập. Cả mười hai kịch bản sự cố tạo ra tác động đúng thiết kế, như Bảng 4.3 và Bảng 4.4 cho thấy.
- Về đường ống dữ liệu, theo mục tiêu thứ hai: dữ liệu đến qua ba kênh như thực tế và được kiểm tra theo hợp đồng dữ liệu; Bronze nạp tăng dần và lũy đẳng; Silver hợp nhất hai phiên bản POS, giải quyết định danh giữa sáu hệ mã và cách ly 1.352 dòng lỗi kèm lý do, với phần chênh lệch số dòng không giải thích được bằng 0 ở cả bảy nguồn. Đường ống xử lý đúng 11 tình huống dữ liệu bất thường xảy ra cùng lúc và một lần API nguồn không phản hồi, theo mục 5.2.4.
- Về kho dữ liệu và kiểm thử, theo mục tiêu thứ ba: lược đồ hình sao gồm sáu bảng sự kiện và bảy bảng chiều, trong đó có hai chiều thay đổi chậm loại 2; 158 kiểm thử dbt đạt trên cả ba tập và doanh thu thuần Gold khớp tuyệt đối với Silver.
- Về chỉ số và cây KPI, theo mục tiêu thứ tư: bộ 24 chỉ số giám sát được so với mức kỳ vọng theo nhóm cùng hạng và lịch sử của chính chi nhánh. Cây KPI chỉ đúng nhánh bị ảnh hưởng trong ví dụ CN2, và không tuần lễ, tuần mưa hay tuần đổi giá nào bị gán nguyên nhân do biến động chung.
- Về bộ phát hiện và đánh giá, theo mục tiêu thứ năm: trên tập kiểm tra chạy một lần với ngưỡng đã chốt, hệ thống bắt bốn trên sáu sự cố với F1 0,52 và độ trễ trung vị 6 ngày, so với 5/6 và F1 0,79 trên tập phát triển. Ở mọi sự cố có tín hiệu, nguyên nhân đúng xếp hạng một, và phương pháp vượt rõ hai phương án cơ sở.
- Về ứng dụng, báo cáo và điều phối, theo mục tiêu thứ sáu: hệ thống gồm ứng dụng 14 trang, kho phục vụ PostgreSQL với dashboard Metabase, và hai DAG Airflow đưa bảy ngày dữ liệu mới từ hệ thống nguồn đến cảnh báo và dashboard trong 146 đến 199 giây. Toàn bộ hệ thống chạy bằng một lệnh Docker Compose.

Về mặt học thuật, khóa luận đóng góp một cách tiếp cận đánh giá có kiểm soát cho bài toán phát hiện sự cố vận hành trên dữ liệu đa nguồn, trong đó dữ liệu mô phỏng nhất quán nhân quả và tập kịch bản kiểm tra độc lập cho phép đo lường định lượng thay vì chỉ minh họa. Về mặt thực tiễn, nền tảng minh họa rằng một chuỗi F&B quy mô vừa có thể xây dựng hệ thống dữ liệu tuân theo các nguyên tắc kỹ thuật dữ liệu chuẩn mực bằng công cụ mã nguồn mở, chạy trên một máy tính cá nhân; kết quả đánh giá cũng cho thấy nhìn doanh thu tổng hợp gần như không phát hiện được sự cố vận hành nào, trong khi đối chiếu chéo các nguồn thì có.

## 6.2. Điều chỉnh so với đề cương

Mục tiêu tổng quát, câu hỏi nghiên cứu và phạm vi giữ nguyên như đề cương; riêng mục tiêu cụ thể thứ sáu được bổ sung lớp báo cáo kinh doanh. Những nội dung đề cương đã xếp ngoài phạm vi vẫn nằm ngoài phạm vi, gồm dữ liệu thật của doanh nghiệp, gửi cảnh báo qua kênh nhắn tin, triển khai trên hạ tầng đám mây và mô hình dự báo nhu cầu. Phần bổ sung so với đề cương gồm năm nội dung.

- Kho phục vụ PostgreSQL và công cụ báo cáo kinh doanh Metabase, để tách DuckDB, máy tính toán của đường ống, khỏi nơi phục vụ người đọc, và để các báo cáo chuẩn dùng đúng công cụ BI thay vì tự viết.
- Cơ chế kích hoạt đường ống theo dữ liệu mới, bên cạnh việc chạy theo lịch.
- Tầng thu thập với ba kênh, hợp đồng dữ liệu và một API giả lập phía nguồn, để đường đi của dữ liệu giống thực tế thay vì mọi nguồn đều là tệp đặt sẵn.
- Đề xuất xử lý và thiệt hại ước tính cho từng cảnh báo.
- Một trợ lý phân tích dùng mô hình ngôn ngữ lớn, là phần mở rộng chưa được đánh giá.

Nguyên tắc của các điều chỉnh là ưu tiên chất lượng của đường ống và của đánh giá, chỉ thêm một thành phần khi nó giải quyết một nhu cầu cụ thể của người dùng, không thêm công nghệ chỉ để có mặt.

## 6.3. Hạn chế

- Hạn chế lớn nhất là dữ liệu mô phỏng. Nền tảng chưa được kiểm chứng trên dữ liệu vận hành thật của một doanh nghiệp. Một số quy luật hành vi mua hàng đã được hiệu chỉnh từ dữ liệu giao dịch thật công khai, nhưng dữ liệu đó thuộc loại hình và bối cảnh khác; các tham số vận hành còn lại là giả định, chưa được hiệu chỉnh bằng dữ liệu quan sát. Một số kết luận kinh doanh, như số đơn không giảm sau điều chỉnh giá, phản ánh giả định của bộ mô phỏng hơn là hành vi khách hàng.
- Một số khía cạnh của dữ liệu chưa đủ để phân tích. Nhu cầu theo giờ là giả định hai cao điểm dạng bậc thang và nhân viên chỉ làm hai ca cố định, nên chưa phân tích được phân ca theo giờ; hành vi khách hàng ứng dụng là ngẫu nhiên, không có rời bỏ hay phản ứng với chất lượng dịch vụ, nên chưa phân tích được giữ chân khách. Hai phân tích này cần dữ liệu ca làm và lịch sử khách hàng thật, như đã nêu ở mục 3.3.9.
- Các kịch bản đơn giản hơn thực tế. Các sự cố có một nguyên nhân chính và hầu như không chồng lấn; mỗi tập chỉ có sáu kịch bản nên các tỷ lệ phát hiện chỉ mang tính chỉ báo. Tác giả vừa thiết kế bộ mô phỏng vừa thiết kế bộ phát hiện.
- Bộ phát hiện còn điểm yếu. Thất thoát kho ở S5 và H5 không phát hiện được với nhịp kiểm kê hai tuần và lượng tồn chỉ vài ngày. Sự cố nhẹ và ngắn nằm sát dưới ngưỡng: thiếu nhân sự H4 đạt điểm 2,82, gian lận H6 đạt 3,44 và chỉ được cảnh báo ở tuần thứ tư dưới nhãn chưa xác định. Nhóm chi nhánh hạng C chỉ có ba chi nhánh nên mức kỳ vọng nhiễu, gây bốn trên bảy báo động giả ở tập kiểm tra. Hiệu năng giảm từ F1 0,79 trên tập phát triển xuống 0,52 trên tập kiểm tra.
- Đánh giá chưa đầy đủ. Phân tích độ nhạy cho thấy cửa sổ mức nền 12 tuần tốt hơn nhẹ cửa sổ 8 tuần đang dùng trên tập phát triển; vì cấu hình đã chốt trước khi chạy tập kiểm tra, điều này chưa được kiểm chứng trên dữ liệu mới. Tầng khớp mờ tên nguyên liệu chưa phải dùng tới lần nào nên chưa được kiểm chứng; trợ lý phân tích mới được kiểm thử với mô hình giả lập.
- Tầng thu thập mới được kiểm chứng với nguồn giả lập. API của POS đám mây là dịch vụ giả lập theo cách các API bán hàng thường làm; API thật của từng nhà cung cấp có thể khác về cách xác thực, cách lấy tăng dần theo thời điểm cập nhật thay vì theo ngày, và giới hạn tần suất. Các tình huống dữ liệu bất thường do tác giả thiết kế, chưa bao quát hết lỗi của hệ thống thật. Mã xác thực API đang để trong biến môi trường, chưa qua kho bí mật.
- Định nghĩa một số chỉ số còn hẹp. Labor% chỉ gồm lương giờ trực tiếp theo chấm công, chưa gồm lương cố định của quản lý và bảo hiểm; giá vốn món dùng định mức, chưa phân bổ hao hụt thực tế theo món.
- Kiểm thử còn thiên về dữ liệu. Kiểm thử dbt kiểm tra kết quả sau khi dựng trên dữ liệu thật của từng tập, chưa có kiểm thử đơn vị cho logic biến đổi của từng mô hình SQL với dữ liệu đầu vào và kết quả mong đợi viết sẵn; một lỗi logic chỉ được phát hiện nếu nó làm vi phạm một luật đã khai báo. Chức năng kiểm thử đơn vị của dbt có thể được dùng cho các mô hình phức tạp nhất như hợp nhất hai phiên bản POS, ghép lượt chấm công và tính hao hụt. Ngoài ra, tầng Silver và Gold được dựng lại toàn bộ mỗi lượt; cách này phù hợp với quy mô hiện tại nhưng cần chuyển sang cập nhật tăng dần theo ngày khi dữ liệu lớn hơn nhiều lần (mục 3.5.5).
- Quy mô và triển khai còn giới hạn. Hệ thống được thiết kế và kiểm chứng cho quy mô một chuỗi vừa trên một máy; DuckDB chỉ cho một tiến trình ghi nên mỗi lúc chỉ chạy một lượt đường ống. Ứng dụng chưa có đăng nhập và phân quyền; dashboard Metabase được nhúng bằng liên kết công khai, chỉ phù hợp trong mạng nội bộ.

## 6.4. Hướng phát triển

- Áp dụng trên dữ liệu thật. Nền tảng cần được kết nối với hệ thống của một doanh nghiệp đối tác sau khi có thỏa thuận về quyền truy cập và bảo mật dữ liệu. Công việc gồm viết bộ kết nối cho API của nhà cung cấp POS cụ thể theo cùng khuôn của bộ kết nối hiện có, chuyển các nguồn tệp sang thư mục dùng chung hoặc hộp thư nhận báo cáo, bổ sung hợp đồng dữ liệu cho các mẫu tệp thật; hiệu chỉnh lại tham số của các bộ phát hiện trên dữ liệu đó, và bổ sung các biến thể lỗi mới vào quy tắc làm sạch.
- Cải thiện bộ phát hiện. Các hướng cụ thể gồm gộp bằng chứng P3 theo trọng số, ưu tiên tín hiệu gốc là số ca bếp; cộng dồn bằng chứng thu ngân qua nhiều tuần bằng tổng tích lũy CUSUM để gian lận nhẹ kéo dài được phát hiện sớm; kiểm kê hằng tuần cho nhóm nguyên liệu giá trị cao; thay trung vị nhóm hạng C bằng mô hình kỳ vọng có biến quy mô; thử cửa sổ mức nền dài hơn tám tuần. Mọi cải tiến cần được đánh giá trên một tập kiểm tra mới, vì tập kiểm tra hiện tại đã được xem kết quả.
- Mở rộng phân tích. Khi có dữ liệu ca làm và lịch sử khách hàng thật, có thể dự báo nhu cầu theo chi nhánh, kênh và khung giờ để đề xuất lượng đặt hàng và lịch phân ca, phân tích biên lợi nhuận theo món có tính hao hụt thực tế, gắn hành động cụ thể cho từng phân khúc khách hàng ứng dụng và phân tích phễu chuyển đổi trên ứng dụng.
- Cảnh báo chủ động. Hệ thống có thể gửi cảnh báo và đề xuất xử lý qua email hoặc kênh nhắn tin của từng người phụ trách, kèm đường dẫn đến trang Truy vết.
- Mở rộng sang nhiều chuỗi. Cấu hình nguồn, bảng ánh xạ định danh và tham số phát hiện có thể được tổ chức theo từng doanh nghiệp để nền tảng phục vụ được nhiều chuỗi F&B khác nhau mà không cần sửa mã lõi.
- Triển khai trên đám mây. Kiến trúc hiện tại đã tách riêng các vai trò lưu tệp thô, điều phối, tính toán, kho phục vụ và trình bày, nên mỗi thành phần có thể thay bằng một dịch vụ quản lý tương ứng mà không đổi logic. Bảng 6.1 trình bày lộ trình này.

TABLE: Bảng 6.1. Lộ trình chuyển các thành phần lên Amazon Web Services
WIDTHS: 4,4.4,5.6
| Thành phần hiện tại | Dịch vụ tương ứng trên AWS | Thay đổi cần làm |
| Vùng tiếp nhận `source_systems/` | Amazon S3 (vùng dữ liệu thô) | Bộ kết nối, kênh tải lên và hệ thống xuất tệp ghi lên S3 thay vì thư mục trên máy |
| Bộ kết nối API, mã xác thực trong biến môi trường | Tác vụ ECS chạy theo lịch hoặc AWS Lambda; mã xác thực trong AWS Secrets Manager | Đọc mã xác thực từ Secrets Manager, trạng thái mốc lưu cạnh dữ liệu trên S3 |
| Dataset của Airflow và kiểm tra mỗi giờ | Thông báo sự kiện của S3 qua Amazon EventBridge | Tệp mới trên S3 kích hoạt đường ống |
| Airflow trong Docker | Amazon MWAA (Airflow được quản lý) | Giữ nguyên hai DAG |
| DuckDB và dbt | Container trên Amazon ECS Fargate, đọc ghi tệp Parquet trên S3; khi dữ liệu lớn hơn nhiều bậc, chuyển sang Amazon Athena hoặc Redshift với bộ chuyển dbt tương ứng | Mô hình dbt giữ nguyên phần lớn, chỉ đổi bộ chuyển và một số hàm riêng của DuckDB |
| PostgreSQL kho phục vụ | Amazon RDS for PostgreSQL | Đổi chuỗi kết nối của bước publish |
| Metabase và ứng dụng Streamlit | Container trên ECS Fargate sau bộ cân bằng tải, đăng nhập qua Amazon Cognito | Thêm đăng nhập, bỏ liên kết công khai |
| Trợ lý phân tích | Amazon Bedrock | Mã đã hỗ trợ, chỉ cần cấu hình |
| Nhật ký và giám sát | Amazon CloudWatch | Chuyển nhật ký các bước sang CloudWatch, đặt cảnh báo khi một lượt thất bại |

Trong các hướng trên, áp dụng trên dữ liệu thật nên được ưu tiên trước, vì mọi cải tiến bộ phát hiện và mở rộng phân tích đều cần được hiệu chỉnh lại trên dữ liệu đó. Triển khai trên đám mây chỉ thực sự cần khi nền tảng phục vụ nhiều người dùng hoặc nhiều chuỗi cùng lúc.
