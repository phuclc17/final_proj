#! MỤC LỤC

[[TOC]]

[[END_FRONT]]

#! ĐỀ CƯƠNG KHÓA LUẬN TỐT NGHIỆP

TABLE: Bảng 1. Thông tin chung
WIDTHS: 3,7
| Nội dung | Thông tin |
| Tên đề tài | Xây dựng nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn hỗ trợ truy vết nguyên nhân biến động doanh thu cho chuỗi F&B |
| Chuyên ngành | Công nghệ thông tin |
| Sinh viên thực hiện | Lê Cao Phúc, MSSV 31231021033 |
| Giảng viên hướng dẫn | TS. Ngô Tấn Vũ Khanh |
| Định hướng | Kỹ thuật dữ liệu (Data Engineering) và phân tích dữ liệu (Data Analytics) |

## 1. Tính cấp thiết của đề tài

Ngành ăn uống, đặc biệt là mô hình nhà hàng phục vụ nhanh (Quick-Service Restaurant – QSR), có tần suất giao dịch cao, giá trị mỗi đơn nhỏ, nguyên liệu nhanh hỏng và hiệu quả phụ thuộc nhiều vào cách vận hành từng ca. Chỉ cần thiếu một nhân viên bếp ở ca tối, một lô nguyên liệu tươi hư hỏng, hay một sai lệch nhỏ trong cách sàn giao đồ ăn tính phí, lợi nhuận của một chi nhánh đã có thể giảm đáng kể mà người quản lý không dễ nhận ra.

Các chuỗi đồ ăn nhanh hiện nay bán hàng đa kênh: tại quầy, qua ứng dụng riêng và qua các sàn như GrabFood, ShopeeFood. Mỗi kênh chạy trên một hệ thống khác nhau. Máy bán hàng tại quầy (POS) ghi từng hóa đơn; ứng dụng riêng lưu đơn hàng và khách hàng; sàn chỉ gửi báo cáo đối soát tổng hợp theo tuần; kho được theo dõi bằng sổ nhập kho và phiếu kiểm kê, nhiều nơi vẫn ghi bằng Excel; nhân sự được theo dõi qua máy chấm công. Các hệ thống này dùng mã định danh khác nhau cho cùng một chi nhánh, nhân viên hay nguyên liệu, định dạng ngày giờ, đơn vị và chất lượng dữ liệu cũng không đồng nhất.

Hệ quả là khi doanh thu của một chi nhánh biến động, nhà quản lý thường chỉ thấy con số tổng hợp mà khó trả lời câu hỏi quan trọng hơn: biến động đó đến từ đâu. Doanh thu giảm có thể hoàn toàn bình thường, như ngày mưa hay sau kỳ nghỉ lễ, nhưng cũng có thể là dấu hiệu của sự cố như chi nhánh thiếu người nên phải hủy đơn và bị tụt hạng trên sàn. Lợi nhuận giảm trong khi doanh thu không đổi có thể do sàn thu phí cao hơn hợp đồng, nguyên liệu hao hụt, hàng tồn bị thất thoát hoặc gian lận tại quầy thu ngân. Những sự cố này không lộ ra trong một nguồn dữ liệu riêng lẻ mà chỉ thấy được khi đối chiếu nhiều nguồn với nhau.

Vì vậy, bài toán không dừng ở một bảng điều khiển doanh thu, mà là xây dựng một nền tảng dữ liệu tích hợp các nguồn không đồng nhất thành một kho dữ liệu sạch, nhất quán, có kiểm chứng, và trên đó áp dụng các phương pháp phân tích giải thích được để phát hiện sự cố, truy vết nguyên nhân của biến động. Bài toán kết hợp cả kỹ thuật dữ liệu và phân tích dữ liệu, phù hợp với định hướng chuyên môn của sinh viên và có giá trị ứng dụng rõ ràng cho các chuỗi F&B quy mô vừa.

## 2. Tổng quan tình hình nghiên cứu

Các công trình và giải pháp liên quan có thể chia thành ba nhóm.

Nhóm thứ nhất là các phần mềm quản lý bán hàng và báo cáo cho nhà hàng do nhà cung cấp POS phát triển. Các phần mềm này mạnh ở báo cáo doanh thu theo kênh, món, ca, nhưng thường chỉ khai thác dữ liệu trong phạm vi hệ thống của chính nhà cung cấp, không tích hợp báo cáo đối soát của sàn, sổ kho ghi tay hay dữ liệu chấm công của bên thứ ba.

Nhóm thứ hai là các nghiên cứu về phát hiện bất thường và gian lận. Chandola, Banerjee và Kumar (2009) tổng hợp các họ phương pháp phát hiện bất thường và chỉ ra rằng lựa chọn phương pháp phụ thuộc vào bản chất dữ liệu và loại bất thường. Trong bán lẻ và nhà hàng, các nghiên cứu thường tập trung vào một loại sự cố trên một nguồn dữ liệu, ví dụ gian lận trên giao dịch POS. Trong quản trị chi phí F&B, phân tích chênh lệch giữa giá vốn thực tế và giá vốn theo định mức là phương pháp kinh điển để phát hiện hao hụt (Dopson và Hayes, 2019).

Nhóm thứ ba là các tài liệu về kiến trúc và mô hình hóa kho dữ liệu, tiêu biểu là phương pháp mô hình hóa chiều của Kimball và Ross (2013) và kiến trúc lakehouse với các tầng dữ liệu tăng dần chất lượng (Armbrust và cộng sự, 2021). Các tài liệu này tập trung vào kiến trúc, ít đi kèm đánh giá định lượng khả năng phát hiện sự cố trên dữ liệu đã tích hợp.

Khoảng trống mà đề tài hướng tới là kết hợp ba yếu tố thường bị tách rời: tích hợp đầy đủ các nguồn dữ liệu vận hành không đồng nhất của một chuỗi F&B, kể cả nguồn bán cấu trúc do con người ghi tay; một kho dữ liệu có kiểm chứng chất lượng làm nền cho phân tích; và đánh giá định lượng khả năng phát hiện, truy vết nhiều loại sự cố trên một tập kịch bản độc lập có đáp án.

## 3. Mục tiêu nghiên cứu

### 3.1. Mục tiêu tổng quát

Xây dựng một nền tảng dữ liệu hoàn chỉnh, đi từ dữ liệu thô của các hệ thống nguồn đến kho dữ liệu và lớp phân tích, có khả năng tích hợp dữ liệu vận hành đa nguồn của chuỗi F&B, phát hiện các sự cố vận hành và hỗ trợ truy vết nguyên nhân biến động doanh thu.

### 3.2. Mục tiêu cụ thể

1. Xây dựng bộ dữ liệu mô phỏng có tính thực tế cho một chuỗi đồ ăn nhanh, trong đó các nguồn dữ liệu nhất quán với nhau về nhân quả, mang các lỗi dữ liệu đặc trưng của từng hệ thống và có đáp án cho mọi sự cố được đưa vào.
2. Xây dựng đường ống dữ liệu theo kiến trúc Medallion gồm ba tầng Bronze, Silver, Gold: nạp dữ liệu thô tăng dần, làm sạch và chuẩn hóa, giải quyết định danh thực thể giữa các hệ thống, cách ly dòng dữ liệu lỗi.
3. Thiết kế kho dữ liệu theo lược đồ hình sao, có chiều thay đổi chậm và kiểm thử chất lượng dữ liệu tự động giữa các tầng.
4. Xây dựng bộ chỉ số vận hành theo chuẩn ngành F&B và cây KPI để truy vết nguyên nhân biến động doanh thu.
5. Xây dựng các bộ phát hiện cho năm vấn đề vận hành và đánh giá định lượng trên một tập kịch bản độc lập.
6. Xây dựng ứng dụng trực quan cho người dùng nghiệp vụ và cơ chế vận hành tự động hằng ngày.

## 4. Câu hỏi nghiên cứu

- RQ1, tích hợp dữ liệu: Có thể tích hợp dữ liệu vận hành từ bảy hệ thống nguồn không đồng nhất về định dạng, mã định danh và chất lượng thành một kho dữ liệu nhất quán và kiểm chứng được hay không?
- RQ2, phát hiện sự cố: Các phương pháp thống kê và luật nghiệp vụ giải thích được có thể phát hiện năm vấn đề vận hành chính xác đến mức nào, đặc biệt trên các kịch bản chưa từng được dùng để chọn ngưỡng?
- RQ3, truy vết nguyên nhân: Có thể truy một biến động doanh thu về đúng nguyên nhân vận hành, đồng thời phân biệt với biến động bình thường do ngày trong tuần, ngày lễ, thời tiết và điều chỉnh giá hay không?

## 5. Đối tượng và phạm vi nghiên cứu

### 5.1. Đối tượng nghiên cứu

Đối tượng nghiên cứu là dữ liệu vận hành đa nguồn của chuỗi nhà hàng phục vụ nhanh và các phương pháp tích hợp, mô hình hóa, phân tích dữ liệu đó để phát hiện sự cố và truy vết nguyên nhân biến động doanh thu.

Dữ liệu vận hành của doanh nghiệp F&B như hóa đơn, báo cáo đối soát với sàn, sổ kho, chấm công là dữ liệu nhạy cảm, không được công khai. Vì vậy đề tài sử dụng một chuỗi giả định tên Fast&Fat làm đối tượng khảo sát điển hình. Fast&Fat đại diện cho mô hình phổ biến của chuỗi đồ ăn nhanh quy mô vừa tại Thành phố Hồ Chí Minh: 11 chi nhánh chia ba hạng theo quy mô, bán qua bốn kênh, thực đơn 28 món, 22 loại nguyên liệu, khoảng 145 nhân viên làm việc theo ca. Fast&Fat không phải là một doanh nghiệp có thật.

### 5.2. Phạm vi nghiên cứu

Về dữ liệu: 26 tuần, từ 11/03/2024 đến 08/09/2024, cho 11 chi nhánh, khoảng 400 nghìn đơn hàng mỗi tập dữ liệu, từ bảy nhóm hệ thống nguồn: POS, ứng dụng riêng, báo cáo đối soát GrabFood, báo cáo đối soát ShopeeFood, sổ nhập kho và phiếu kiểm kê, máy chấm công, danh mục dữ liệu chủ; kèm dữ liệu thời tiết là nguồn bên ngoài. Hệ thống được thiết kế để tiếp tục nhận dữ liệu mới theo từng ngày.

Về kỹ thuật:

- Xử lý theo lô hằng ngày, không xử lý luồng thời gian thực, vì nhịp ra quyết định vận hành của chuỗi F&B là theo ngày và theo tuần.
- Quy mô dữ liệu cỡ hàng trăm megabyte nên công nghệ được chọn tương xứng, chạy được trên một máy tính cá nhân, không dùng nền tảng dữ liệu lớn phân tán.
- Phát hiện và truy vết bằng thống kê và luật nghiệp vụ giải thích được; không xây dựng mô hình dự báo nhu cầu.

Ngoài phạm vi: tích hợp dữ liệu thật của một doanh nghiệp cụ thể, gửi cảnh báo qua kênh nhắn tin, triển khai trên hạ tầng đám mây. Các nội dung này được đưa vào hướng phát triển.

## 6. Phương pháp nghiên cứu

### 6.1. Cách tiếp cận

Đề tài tiếp cận theo hướng nghiên cứu khoa học thiết kế (Design Science Research) trong hệ thống thông tin (Hevner và cộng sự, 2004): tạo ra một sản phẩm giải quyết vấn đề thực tiễn đã xác định, sau đó đánh giá sản phẩm một cách chặt chẽ. Các phương pháp cụ thể gồm nghiên cứu tài liệu về kiến trúc dữ liệu, mô hình hóa chiều, chất lượng dữ liệu, phát hiện bất thường và quản trị vận hành F&B; phân tích nghiệp vụ đi từ vấn đề kinh doanh đến dữ liệu cần có và giải pháp kỹ thuật; mô phỏng có kiểm soát; thực nghiệm và đánh giá định lượng.

### 6.2. Dữ liệu nghiên cứu

Dữ liệu mô phỏng được dùng rộng rãi khi dữ liệu thật nhạy cảm hoặc khi cần đáp án biết trước để đánh giá phương pháp (Patki, Wedge và Veeramachaneni, 2016). Dữ liệu của đề tài được xây dựng theo phương pháp mô phỏng có neo thực tế, với nguyên lý "một thế giới, nhiều góc nhìn". Các sự kiện vận hành như khách đặt món, nhân viên vào ca, bếp chế biến, nhập kho được sinh một lần theo các quan hệ nhân quả: thiếu nhân sự làm tải bếp tăng, thời gian chuẩn bị kéo dài, khách hủy đơn nhiều hơn, điểm đánh giá giảm và sau vài tuần sàn hiển thị chi nhánh ít hơn. Sau đó, mỗi hệ thống nguồn xuất ra phần dữ liệu nó quan sát được, ở định dạng riêng (JSON, CSV, Excel) và kèm các lỗi đặc trưng như hai phiên bản phần mềm POS ghi khác nhau, tên nguyên liệu gõ tay nhiều biến thể, quẹt thẻ chấm công trùng, quên quẹt ra.

Các tham số nền như vị trí chi nhánh, giá món, tỷ lệ giá vốn, lương giờ lấy theo mức phổ biến trên thị trường. Một số quy luật hành vi mua hàng như số món mỗi đơn, mức độ tập trung vào món bán chạy và độ dao động doanh số theo ngày được ước lượng từ bộ dữ liệu giao dịch thật công khai The Bread Basket trên OpenML (giấy phép CC0), có phân tích quy luật nào chuyển giao được sang bối cảnh đồ ăn nhanh và quy luật nào không. Đây là bước mô hình hóa dữ liệu đầu vào trong phương pháp mô phỏng (Law, 2015).

Trên dữ liệu này, đề tài đưa vào các kịch bản sự cố có đáp án biết trước. Đáp án được lưu tách riêng, đường ống dữ liệu và các bộ phát hiện không bao giờ đọc tới. Cách tiếp cận này cho phép đánh giá định lượng độ chính xác, điều gần như không thể làm với dữ liệu thật vì dữ liệu thật không có đáp án đối chứng cho từng sự cố.

### 6.3. Phương pháp phân tích

Biến động doanh thu được đánh giá so với mức kỳ vọng thay vì so với tuần trước. Mức kỳ vọng của một chi nhánh trong một tuần được xác định từ nhóm chi nhánh cùng hạng trong cùng tuần, điều chỉnh theo độ chênh lệch thường ngày của chính chi nhánh đó. Cách so sánh này loại bỏ các yếu tố tác động lên cả nhóm như ngày lễ, thời tiết, mùa vụ. Mức bất thường được đo bằng điểm chuẩn bền vững dựa trên trung vị và độ lệch tuyệt đối trung vị (Iglewicz và Hoaglin, 1993), để các tuần có sự cố trước đó không làm lệch mức nền.

Khoảng chênh lệch doanh thu được phân rã theo cây KPI: doanh thu bằng tổng theo kênh, doanh thu mỗi kênh bằng số đơn nhân giá trị đơn bình quân. Mỗi nguyên nhân vận hành được nhận diện qua một nhóm tín hiệu đặc trưng, đối chiếu từ nhiều nguồn. Với bài toán tuân thủ hợp đồng như phí sàn, đề tài dùng luật đối soát trực tiếp thay cho phương pháp thống kê. Với gian lận tại quầy, đề tài so từng thu ngân với các thu ngân khác cùng chi nhánh bằng kiểm định tỷ lệ có hiệu chỉnh so sánh bội.

### 6.4. Phương pháp đánh giá

Đề tài sinh hai tập dữ liệu độc lập với các kịch bản sự cố khác nhau về chi nhánh, thời điểm và mức độ. Tập phát triển dùng để xây dựng phương pháp và chọn ngưỡng. Tập kiểm tra chỉ được chạy một lần để đánh giá cuối cùng, không chỉnh sửa sau khi xem kết quả, nhằm tránh hiện tượng quá khớp.

Các độ đo gồm: với đường ống dữ liệu, tỷ lệ dòng được đối soát giữa các tầng, số kiểm thử chất lượng đạt, thời gian xử lý toàn bộ và tăng dần; với bộ phát hiện, precision, recall, F1 và độ trễ phát hiện tính theo ngày; với truy vết, tỷ lệ nguyên nhân đúng được xếp hạng đầu. Kết quả được so sánh với một phương án đối chứng chỉ theo dõi doanh thu tổng, và phân tích độ nhạy theo mức độ nghiêm trọng của sự cố.

## 7. Nội dung và giải pháp dự kiến

### 7.1. Năm vấn đề vận hành

TABLE: Bảng 2. Các vấn đề vận hành và nguồn dữ liệu cần đối chiếu
WIDTHS: 1,3.4,3.6,3.6
| Mã | Vấn đề | Nguồn dữ liệu cần đối chiếu | Hướng phát hiện |
| P1 | Sai lệch đối soát với sàn: phí hoa hồng cao hơn hợp đồng, đơn sàn không được ghi vào POS | Báo cáo đối soát GrabFood, ShopeeFood; POS; hợp đồng | Luật đối soát tỷ lệ phí; tỷ lệ đơn sàn có mặt trên POS |
| P2 | Hao hụt nguyên liệu vượt định mức | Sổ nhập kho, phiếu kiểm kê, lượng bán, công thức món | Chênh lệch tiêu hao thực tế so với định mức theo kỳ kiểm kê |
| P3 | Nhân sự không khớp tải đơn | Chấm công, POS, ứng dụng, báo cáo sàn | Nhóm tín hiệu: ca bếp, thời gian chuẩn bị, đơn bị hủy, điểm đánh giá |
| P4 | Thất thoát hàng tồn kho | Phiếu kiểm kê, sổ nhập kho, lượng bán | Chênh lệch tồn tập trung ở nguyên liệu giá trị cao |
| P5 | Gian lận tại quầy thu ngân | Hóa đơn hủy, hoàn tiền theo người thực hiện; danh sách nhân viên | So sánh từng thu ngân với đồng nghiệp cùng chi nhánh |

Bên cạnh năm vấn đề trên, dữ liệu có các biến động bình thường như cuối tuần, ngày lễ, ngày mưa, điều chỉnh giá bán. Hệ thống phải phân biệt được biến động bình thường với biến động do sự cố để tránh cảnh báo sai.

### 7.2. Kiến trúc nền tảng

TABLE: Bảng 3. Các tầng của đường ống dữ liệu
WIDTHS: 2,4,6
| Tầng | Câu hỏi trả lời | Nội dung xử lý |
| Bronze | Nguồn đã gửi gì? | Nạp nguyên văn file thô của các hệ thống, ghi kèm tên file, số dòng, mã băm, lô nạp; nạp tăng dần, chạy lại không trùng |
| Silver | Dữ liệu đã đúng và chuẩn chưa? | Chuẩn hóa định dạng ngày giờ, tiền, đơn vị; giải quyết định danh chi nhánh, nhân viên, món, nguyên liệu giữa các hệ thống; đưa dòng lỗi vào bảng cách ly kèm lý do; đối soát số dòng với Bronze |
| Gold | Kinh doanh ra sao, vì sao? | Lược đồ hình sao gồm bảng chiều, bảng sự kiện và các bảng chỉ số; ghép nhiều nguồn để tính giá vốn, chi phí nhân công, hao hụt, đối soát sàn, mức kỳ vọng của từng chỉ số |

Cách phân tầng này tách việc lưu giữ dữ liệu gốc, làm sạch và mô hình hóa nghiệp vụ thành các bước độc lập, mỗi bước có kiểm soát chất lượng riêng, theo các nguyên tắc kỹ thuật dữ liệu phổ biến (Reis và Housley, 2022). Trên tầng Gold là lớp phân tích gồm cây KPI, các bộ phát hiện và ứng dụng trực quan cho phép người quản lý chọn chi nhánh, tuần cần xem, thấy khoảng chênh lệch doanh thu nằm ở kênh nào và các tín hiệu vận hành đi kèm.

### 7.3. Công nghệ sử dụng

TABLE: Bảng 4. Công nghệ dự kiến sử dụng
WIDTHS: 2.6,4,5.4
| Công nghệ | Vai trò | Lý do lựa chọn |
| Python | Bộ mô phỏng, nạp dữ liệu, lớp phân tích | Hệ sinh thái xử lý dữ liệu đầy đủ, phổ biến trong ngành |
| DuckDB | Kho dữ liệu phân tích | Cơ sở dữ liệu cột nhúng, chạy trên máy cá nhân, đủ nhanh cho quy mô hàng trăm megabyte (Raasveldt và Mühleisen, 2019) |
| dbt | Biến đổi dữ liệu bằng SQL, kiểm thử chất lượng, tài liệu hóa | Quản lý phụ thuộc giữa các bảng, kiểm thử tự động, truy vết nguồn gốc dữ liệu (dbt Labs, n.d.) |
| Streamlit | Ứng dụng trực quan | Xây dựng giao diện phân tích nhanh bằng Python |
| Apache Airflow | Điều phối chạy hằng ngày | Công cụ điều phối luồng dữ liệu phổ biến, lập lịch và theo dõi các bước |

Đề tài không sử dụng các nền tảng dữ liệu lớn phân tán vì quy mô dữ liệu không đòi hỏi.

## 8. Kết quả dự kiến

- Bộ mô phỏng và hai tập dữ liệu nguồn ở định dạng JSON, CSV, Excel, kèm đáp án các kịch bản sự cố.
- Đường ống dữ liệu Bronze, Silver, Gold chạy tự động, nạp tăng dần, có kiểm thử chất lượng và đối soát giữa các tầng.
- Kho dữ liệu lược đồ hình sao cùng bộ chỉ số vận hành: doanh thu, số đơn, giá trị đơn theo kênh, tỷ lệ giá vốn, tỷ lệ chi phí nhân công, tỷ lệ hủy đơn, thời gian chuẩn bị, hao hụt so với định mức.
- Các bộ phát hiện năm vấn đề vận hành và kết quả đánh giá định lượng trên tập kiểm tra, có so sánh với phương án đối chứng và nêu rõ các trường hợp phát hiện chưa tốt.
- Ứng dụng truy vết nguyên nhân biến động doanh thu cho người dùng nghiệp vụ.
- Báo cáo khóa luận và mã nguồn có thể tái lập.

## 9. Ý nghĩa khoa học và thực tiễn

Về khoa học, đề tài đề xuất một cách đánh giá định lượng nền tảng dữ liệu vận hành bằng dữ liệu mô phỏng nhất quán về nhân quả, có đáp án và tách tập phát triển với tập kiểm tra. Bộ mô phỏng có thể tái sử dụng để kiểm thử các đường ống dữ liệu và phương pháp phân tích khác.

Về thực tiễn, đề tài minh họa một cách làm khả thi cho các chuỗi F&B quy mô vừa: dùng công cụ mã nguồn mở, chạy được trên một máy tính cá nhân, nhưng tuân theo các nguyên tắc kỹ thuật dữ liệu chuẩn mực như phân tầng dữ liệu, kiểm thử chất lượng, truy vết nguồn gốc. Kiến trúc được thiết kế để có thể thay bộ mô phỏng bằng dữ liệu thật của doanh nghiệp mà không phải thay đổi các tầng phía sau.

## 10. Kết cấu dự kiến của khóa luận

Ngoài phần mở đầu, tài liệu tham khảo và phụ lục, khóa luận dự kiến gồm sáu chương:

- Chương 1. Tổng quan đề tài: bối cảnh, vấn đề, câu hỏi nghiên cứu, mục tiêu, phạm vi và phương pháp.
- Chương 2. Cơ sở lý thuyết và các nghiên cứu liên quan: nghiệp vụ vận hành F&B và các chỉ số then chốt, kiến trúc dữ liệu, mô hình hóa chiều, chất lượng dữ liệu, phát hiện bất thường và truy vết nguyên nhân, dữ liệu mô phỏng, công nghệ sử dụng.
- Chương 3. Phân tích và thiết kế hệ thống: yêu cầu, kiến trúc tổng thể, thiết kế bộ mô phỏng, đường ống dữ liệu, kho dữ liệu, kiểm soát chất lượng, lớp phân tích và ứng dụng.
- Chương 4. Hiện thực hệ thống: cài đặt từng thành phần và kết quả kiểm chứng.
- Chương 5. Thực nghiệm và đánh giá: đánh giá đường ống dữ liệu, các bộ phát hiện, khả năng truy vết, phân tích độ nhạy và các phát hiện kinh doanh.
- Chương 6. Kết luận và hướng phát triển.

## 11. Kế hoạch thực hiện

Khóa luận được thực hiện trong 10 tuần, từ ngày 16/08/2026 đến ngày 24/10/2026. Các công việc được sắp theo thứ tự phụ thuộc: dữ liệu nguồn phải có trước khi xây dựng đường ống, kho dữ liệu phải hoàn chỉnh trước khi xây dựng lớp phân tích, và việc đánh giá trên tập kiểm tra chỉ thực hiện sau khi đã chốt phương pháp trên tập phát triển.

TABLE: Bảng 5. Kế hoạch thực hiện
WIDTHS: 1.1,2.5,5.4,3
| Tuần | Thời gian | Nội dung công việc | Sản phẩm |
| 1 | 16/08 – 22/08/2026 | Chọn đề tài; khảo sát nghiệp vụ vận hành chuỗi đồ ăn nhanh; xác định các hệ thống nguồn và dữ liệu mỗi hệ thống tạo ra | Phác thảo đề tài |
| 2 | 23/08 – 29/08/2026 | Tổng quan tài liệu về kiến trúc dữ liệu, mô hình hóa chiều, chất lượng dữ liệu, phát hiện bất thường, chỉ số vận hành F&B; xác định vấn đề, câu hỏi nghiên cứu | Đề cương |
| 3 | 30/08 – 05/09/2026 | Phân tích yêu cầu; thiết kế kiến trúc tổng thể, các tầng dữ liệu và lược đồ hình sao; thiết kế bộ chỉ số và cây KPI | Tài liệu thiết kế |
| 4 | 06/09 – 12/09/2026 | Thiết kế và xây dựng bộ mô phỏng: mô hình nhu cầu, mô hình nhân quả vận hành, mô hình kho, mô hình lỗi của từng hệ thống nguồn | Bộ mô phỏng |
| 5 | 13/09 – 19/09/2026 | Hiệu chỉnh tham số từ dữ liệu giao dịch công khai; thiết kế kịch bản sự cố; sinh và kiểm chứng tập phát triển, tập kiểm tra | Hai tập dữ liệu nguồn kèm đáp án |
| 6 | 20/09 – 26/09/2026 | Tầng Bronze: nạp dữ liệu thô tăng dần, ghi siêu dữ liệu truy vết; kiểm tra chạy lại không trùng và nạp thêm ngày mới | Tầng Bronze |
| 7 | 27/09 – 03/10/2026 | Tầng Silver: chuẩn hóa định dạng, giải quyết định danh thực thể, cách ly dòng lỗi, đối soát số dòng với Bronze, kiểm thử chất lượng | Tầng Silver |
| 8 | 04/10 – 10/10/2026 | Tầng Gold: bảng chiều có lịch sử thay đổi, bảng sự kiện, các bảng chỉ số vận hành và mức kỳ vọng; kiểm thử đối soát Silver – Gold | Kho dữ liệu đã kiểm thử |
| 9 | 11/10 – 17/10/2026 | Cây KPI và các bộ phát hiện P1–P5, chọn ngưỡng trên tập phát triển; đánh giá một lần trên tập kiểm tra, so sánh đối chứng, phân tích độ nhạy; ứng dụng truy vết và điều phối chạy hằng ngày | Kết quả đánh giá, ứng dụng |
| 10 | 18/10 – 24/10/2026 | Hoàn thiện báo cáo khóa luận, chuẩn bị slide trình bày, rà soát và nộp | Báo cáo khóa luận |

## 12. Tài liệu tham khảo

REF: Armbrust, M., Ghodsi, A., Xin, R., & Zaharia, M. (2021). Lakehouse: A new generation of open platforms that unify data warehousing and advanced analytics. In *Proceedings of the 11th Conference on Innovative Data Systems Research (CIDR)*.

REF: Chandola, V., Banerjee, A., & Kumar, V. (2009). Anomaly detection: A survey. *ACM Computing Surveys, 41*(3), Article 15.

REF: dbt Labs. (n.d.). *dbt documentation*. https://docs.getdbt.com/

REF: Dopson, L. R., & Hayes, D. K. (2019). *Food and beverage cost control* (7th ed.). Wiley.

REF: Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems research. *MIS Quarterly, 28*(1), 75–105.

REF: Iglewicz, B., & Hoaglin, D. C. (1993). *How to detect and handle outliers*. ASQC Quality Press.

REF: Kimball, R., & Ross, M. (2013). *The data warehouse toolkit: The definitive guide to dimensional modeling* (3rd ed.). Wiley.

REF: Law, A. M. (2015). *Simulation modeling and analysis* (5th ed.). McGraw-Hill Education.

REF: OpenML. (2022). *The-Bread-Basket* (Dataset ID 43422) [Data set]. Giấy phép CC0. https://www.openml.org/d/43422

REF: Patki, N., Wedge, R., & Veeramachaneni, K. (2016). The synthetic data vault. In *2016 IEEE International Conference on Data Science and Advanced Analytics (DSAA)* (pp. 399–410). IEEE.

REF: Raasveldt, M., & Mühleisen, H. (2019). DuckDB: An embeddable analytical database. In *Proceedings of the 2019 International Conference on Management of Data (SIGMOD ’19)* (pp. 1981–1984). ACM.

REF: Reis, J., & Housley, M. (2022). *Fundamentals of data engineering*. O’Reilly Media.
