# CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

NGUON: Đề xuất của nghiên cứu

Chương này tổng kết kết quả theo các mục tiêu đã đặt ra, rút ra hàm ý quản trị cho các chuỗi F&B, nêu những điều chỉnh so với đề cương, các hạn chế và hướng phát triển.

## 6.1. Kết quả đạt được

Đối chiếu với các mục tiêu cụ thể ở mục 1.4.2, khóa luận đã đạt được các kết quả sau.

- Bộ dữ liệu mô phỏng theo nguyên lý “một thế giới, nhiều góc nhìn” sinh dữ liệu nhất quán về nhân quả cho bảy hệ thống vận hành cùng danh mục và thời tiết, có đủ lỗi dữ liệu đặc trưng, thành hai tập độc lập 26 tuần với 385 đến 435 nghìn đơn mỗi tập; cả mười hai kịch bản sự cố tạo tác động đúng thiết kế (Bảng 4.3).
- Đường ống nhận dữ liệu qua ba kênh như thực tế và kiểm tra theo hợp đồng dữ liệu; Bronze nạp tăng dần và lũy đẳng; Silver hợp nhất hai phiên bản POS, giải quyết định danh giữa sáu hệ mã và cách ly 1.352 dòng lỗi kèm lý do, với chênh lệch số dòng không giải thích được bằng 0 ở cả bảy nguồn; đường ống xử lý đúng 11 tình huống dữ liệu bất thường cùng lúc và một lần API nguồn không phản hồi.
- Kho dữ liệu dạng lược đồ hình sao gồm sáu bảng sự kiện, bảy bảng chiều, trong đó hai chiều thay đổi chậm kiểu 2; 158 kiểm thử dbt đạt trên cả ba tập và doanh thu thuần Gold khớp tuyệt đối với Silver.
- Bộ 24 chỉ số giám sát được so với mức kỳ vọng theo nhóm cùng hạng và lịch sử của chính chi nhánh; cây KPI chỉ đúng nhánh bị ảnh hưởng, và không tuần lễ, tuần mưa hay tuần đổi giá nào bị gán nguyên nhân do biến động chung.
- Trên tập kiểm tra chạy một lần với ngưỡng đã chốt, bộ phát hiện bắt bốn trên sáu sự cố với F1 0,52, độ trễ trung vị 6 ngày, so với 5/6 và F1 0,79 trên tập phát triển; ở mọi sự cố có tín hiệu, nguyên nhân đúng xếp hạng một, và phương pháp vượt rõ hai phương án cơ sở.
- Ứng dụng 14 trang, kho phục vụ PostgreSQL với dashboard Metabase và hai DAG Airflow đưa bảy ngày dữ liệu mới từ hệ thống nguồn đến cảnh báo trong khoảng 150 đến 200 giây; toàn bộ hệ thống chạy bằng một lệnh Docker Compose.

Về học thuật, khóa luận đóng góp một cách đánh giá có kiểm soát cho bài toán phát hiện sự cố vận hành trên dữ liệu đa nguồn, trong đó dữ liệu mô phỏng nhất quán nhân quả và tập kiểm tra độc lập cho phép đo lường định lượng thay vì chỉ minh họa. Về thực tiễn, nền tảng cho thấy một chuỗi F&B quy mô vừa có thể xây dựng hệ thống dữ liệu theo các nguyên tắc kỹ thuật dữ liệu chuẩn mực bằng công cụ mã nguồn mở trên một máy tính, và rằng nhìn doanh thu tổng hợp gần như không phát hiện được sự cố vận hành nào, trong khi đối chiếu chéo các nguồn thì có.

## 6.2. Hàm ý quản trị

Các kết quả được rút ra từ dữ liệu mô phỏng, nên những hàm ý dưới đây là định hướng cho chuỗi F&B quy mô vừa có cơ cấu vận hành tương tự và cần được kiểm chứng lại trên dữ liệu của chính doanh nghiệp.

Thứ nhất, không nên chỉ theo dõi doanh thu tổng hợp. Phương án chỉ giám sát doanh thu không phát hiện được sự cố nào trên tập phát triển và chỉ một trên sáu sự cố trên tập kiểm tra, vì nhiều sự cố gây thiệt hại thật mà doanh thu gần như không đổi. Báo cáo vận hành hằng tuần nên đặt doanh thu cạnh các chỉ số đối chiếu giữa hệ thống: đơn sàn so với đơn trên POS, hoa hồng thực tế so với hợp đồng, hao hụt so với định mức theo nguyên liệu, số ca làm so với lượng đơn, và tỷ lệ hủy, hoàn theo thu ngân.

Thứ hai, đối soát với sàn nên được làm hằng tuần theo điều khoản hợp đồng thay vì chỉ khi thực nhận giảm bất thường. Phí sàn chiếm khoảng một phần tư doanh thu món, nên sai lệch vài điểm phần trăm có thể kéo dài nhiều tháng; thí nghiệm ở mục 5.5.3 cho thấy luật so thẳng với hợp đồng phát hiện được sai lệch suốt thời gian nó tồn tại, còn so với lịch sử chỉ nhận ra trong vài tuần đầu.

Thứ ba, cần bảo vệ định biên nhân sự tối thiểu của từng ca kể cả khi muốn giảm chi phí nhân công. Thiếu nhân sự bếp ca tối là sự cố gây thiệt hại lớn nhất, ước tính 94,6 triệu đồng doanh thu trong hai tuần, và còn ảnh hưởng sau khi nhân sự đã trở lại; thời gian chuẩn bị và tỷ lệ đơn bị cửa hàng hủy là hai chỉ báo sớm nên theo dõi cùng số ca làm. Labor% của chi nhánh nhỏ cần so với chi nhánh cùng hạng, vì hạng C có Labor% gấp khoảng 3,4 lần hạng A chỉ do phải duy trì số người tối thiểu.

Thứ tư, kiểm soát nội bộ dựa trên dữ liệu nhưng không kết luận chỉ từ thống kê. Tỷ lệ hủy, hoàn và giảm giá theo thu ngân là căn cứ để chọn ca cần xem lại hóa đơn và camera, chưa đủ để kết luận gian lận. Với hàng tồn kho, nhịp kiểm kê hai tuần không đủ để phát hiện thất thoát ở nguyên liệu tồn chỉ vài ngày, nên cần kiểm kê hằng tuần hoặc đột xuất cho nhóm giá trị cao như thịt bò, thịt gà và phô mai.

Thứ năm, chiến lược kênh và thực đơn nên tính theo biên đóng góp chứ không theo doanh thu. Sau phí sàn và giá vốn, mỗi 100 đồng bán qua GrabFood chỉ còn khoảng 41 đồng so với 69 đồng tại quầy, nên kéo khách giao hàng sang ứng dụng riêng mang lại lợi ích rõ, nhất là ngày mưa; món bán chạy nhất có lãi mỗi phần dưới bình quân, nên gợi ý bán kèm sang combo lãi cao hiệu quả hơn tăng giá.

Cuối cùng, doanh nghiệp cần coi dữ liệu vận hành là tài sản được quản lý: thống nhất mã chi nhánh, mã nhân viên, tên nguyên liệu giữa các hệ thống; yêu cầu đối tác và nhà cung cấp phần mềm xuất dữ liệu theo khuôn dạng cố định; lưu lại toàn bộ dữ liệu gốc để mọi con số truy ngược được về chứng từ ban đầu; và xử lý cảnh báo theo thiệt hại ước tính để nguồn lực kiểm tra tập trung vào nơi mất mát nhiều nhất.

## 6.3. Điều chỉnh so với đề cương

Mục tiêu tổng quát, câu hỏi nghiên cứu và phạm vi giữ nguyên như đề cương; riêng mục tiêu cụ thể thứ sáu được bổ sung lớp báo cáo kinh doanh. Các nội dung đề cương đã xếp ngoài phạm vi vẫn nằm ngoài phạm vi, gồm dữ liệu thật của doanh nghiệp, gửi cảnh báo qua kênh nhắn tin, triển khai trên đám mây và dự báo nhu cầu. Phần bổ sung gồm kho phục vụ PostgreSQL và Metabase để tách máy tính toán khỏi nơi phục vụ người đọc; cơ chế kích hoạt đường ống theo dữ liệu mới bên cạnh chạy theo lịch; tầng thu thập với ba kênh, hợp đồng dữ liệu và API giả lập phía nguồn để đường đi của dữ liệu giống thực tế; đề xuất xử lý và thiệt hại ước tính cho từng cảnh báo; và một trợ lý phân tích thử nghiệm chưa được đánh giá. Nguyên tắc của các điều chỉnh là ưu tiên chất lượng của đường ống và của đánh giá, chỉ thêm thành phần khi nó giải quyết một nhu cầu cụ thể, không thêm công nghệ chỉ để có mặt.

## 6.4. Hạn chế

Hạn chế lớn nhất là dữ liệu mô phỏng: nền tảng chưa được kiểm chứng trên dữ liệu vận hành thật. Một số quy luật mua hàng đã được hiệu chỉnh từ dữ liệu giao dịch thật công khai nhưng thuộc loại hình và bối cảnh khác; các tham số vận hành còn lại là giả định, và một số kết luận như số đơn không giảm sau điều chỉnh giá phản ánh giả định hơn là hành vi khách hàng. Nhu cầu theo giờ dạng bậc thang, hai ca cố định và khách hàng chọn ngẫu nhiên khiến chưa phân tích được phân ca theo giờ và giữ chân khách (mục 3.3.5). Các kịch bản đơn giản hơn thực tế, mỗi tập chỉ sáu kịch bản nên tỷ lệ phát hiện chỉ mang tính chỉ báo, và bộ mô phỏng cùng bộ phát hiện được xây dựng trong cùng một nghiên cứu.

Về phương pháp, thất thoát kho ở S5 và H5 không phát hiện được với nhịp kiểm kê hai tuần; sự cố nhẹ và ngắn nằm sát dưới ngưỡng, như H4 điểm 2,82 và H6 điểm 3,44; nhóm hạng C chỉ ba chi nhánh nên mức kỳ vọng nhiễu, gây bốn trên bảy báo động giả ở tập kiểm tra. Phân tích độ nhạy cho thấy cửa sổ 12 tuần tốt hơn nhẹ 8 tuần trên tập phát triển nhưng chưa được kiểm chứng trên dữ liệu mới; tầng khớp mờ tên nguyên liệu chưa phải dùng tới lần nào. Định nghĩa Labor% chỉ gồm lương giờ trực tiếp, và giá vốn món dùng định mức, chưa phân bổ hao hụt thực tế theo món.

Về kỹ thuật, tầng thu thập mới được kiểm chứng với API giả lập, trong khi API thật có thể khác về xác thực, cách lấy tăng dần và giới hạn tần suất; mã xác thực đang để trong biến môi trường. Kiểm thử dbt kiểm tra kết quả sau khi dựng, chưa có kiểm thử đơn vị cho logic của từng mô hình SQL với đầu vào và kết quả mong đợi viết sẵn, nên một lỗi logic chỉ lộ ra nếu nó vi phạm một luật đã khai báo. Silver và Gold được dựng lại toàn bộ mỗi lượt, phù hợp với quy mô hiện tại nhưng cần chuyển sang cập nhật tăng dần khi dữ liệu lớn hơn nhiều lần (mục 3.5.3). DuckDB chỉ cho một tiến trình ghi nên mỗi lúc chỉ một lượt đường ống; ứng dụng chưa có đăng nhập, phân quyền và dashboard được nhúng bằng liên kết công khai, chỉ phù hợp trong mạng nội bộ.

## 6.5. Hướng phát triển

Hướng đầu tiên và nên ưu tiên là áp dụng trên dữ liệu thật của một doanh nghiệp đối tác sau khi có thỏa thuận về quyền truy cập và bảo mật: viết bộ kết nối cho API của nhà cung cấp POS cụ thể theo khuôn hiện có, chuyển nguồn tệp sang thư mục dùng chung hoặc hộp thư nhận báo cáo, bổ sung hợp đồng dữ liệu cho mẫu tệp thật, rồi hiệu chỉnh lại tham số bộ phát hiện trên dữ liệu đó. Mọi cải tiến khác đều cần được hiệu chỉnh lại trên dữ liệu này.

Về bộ phát hiện, các hướng cụ thể gồm gộp bằng chứng P3 theo trọng số, ưu tiên tín hiệu gốc là số ca bếp; cộng dồn bằng chứng thu ngân qua nhiều tuần bằng tổng tích lũy CUSUM (Page, 1954) để gian lận nhẹ kéo dài được phát hiện sớm; thay trung vị nhóm hạng C bằng mô hình kỳ vọng có biến quy mô; thử cửa sổ mức nền dài hơn. Các cải tiến này cần được đánh giá trên một tập kiểm tra mới, vì tập kiểm tra hiện tại đã được xem kết quả. Về phân tích, khi có dữ liệu ca làm và lịch sử khách hàng thật, có thể dự báo nhu cầu theo chi nhánh, kênh và khung giờ để đề xuất lượng đặt hàng và lịch phân ca, tính biên lợi nhuận theo món có hao hụt thực tế, và phân khúc khách hàng ứng dụng kèm hành động cụ thể. Hệ thống cũng có thể gửi cảnh báo chủ động qua email hoặc kênh nhắn tin cho người phụ trách, và tổ chức cấu hình nguồn, bảng ánh xạ, tham số theo từng doanh nghiệp để phục vụ nhiều chuỗi mà không sửa mã lõi.

Cuối cùng, kiến trúc hiện tại đã tách các vai trò lưu tệp thô, điều phối, tính toán, kho phục vụ và trình bày, nên có thể chuyển lên đám mây mà không đổi logic. Trên Amazon Web Services chẳng hạn, vùng tiếp nhận tương ứng với Amazon S3 kèm thông báo sự kiện thay cho Dataset của Airflow; Airflow chuyển sang dịch vụ Airflow được quản lý và giữ nguyên hai DAG; DuckDB cùng dbt chạy trong container đọc ghi tệp Parquet trên S3, và chỉ khi dữ liệu lớn hơn nhiều bậc mới cần chuyển sang kho phân tán với bộ chuyển dbt tương ứng; kho phục vụ chuyển sang PostgreSQL được quản lý; ứng dụng và Metabase chạy sau bộ cân bằng tải có đăng nhập. Việc chuyển này chỉ thực sự cần khi nền tảng phục vụ nhiều người dùng hoặc nhiều chuỗi cùng lúc.
