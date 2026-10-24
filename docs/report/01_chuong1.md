# CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

## 1.1. Bối cảnh và lý do chọn đề tài

Ngành ăn uống (F&B), đặc biệt là mô hình nhà hàng phục vụ nhanh (Quick-Service Restaurant – QSR), có tần suất giao dịch cao, giá trị mỗi đơn nhỏ, nguyên liệu nhanh hỏng và chịu ảnh hưởng mạnh của cách vận hành. Chỉ cần thiếu một nhân viên bếp ca tối, một lô nguyên liệu tươi bị hỏng hay một sai lệch nhỏ trong cách sàn giao đồ ăn tính phí, lợi nhuận của chi nhánh đã có thể giảm mà người quản lý khó nhận ra. Thị trường ăn uống Việt Nam lớn và cạnh tranh gay gắt: theo khảo sát hơn 4.000 nhà hàng của iPOS.vn (2025), doanh thu ngành năm 2024 đạt gần 689.000 tỷ đồng, tăng 16,6%, với khoảng 323.000 cửa hàng, nhưng chỉ khoảng 14,7% doanh nghiệp ghi nhận tăng trưởng. Kênh giao đồ ăn trực tuyến đạt khoảng 1,8 tỷ USD năm 2024, tăng 26%, chia gần đều cho GrabFood và ShopeeFood (Momentum Works, 2025); người tiêu dùng trẻ đã quen đặt món qua ứng dụng (Vu et al., 2023), trong khi hoa hồng cao của các sàn tạo áp lực lớn lên biên lợi nhuận (Feldman et al., 2023; Li et al., 2020). Trong bối cảnh đó, nhận ra sớm nguyên nhân làm doanh thu và lợi nhuận suy giảm là một năng lực cạnh tranh.

Mô hình bán hàng đa kênh khiến dữ liệu vận hành nằm rải rác ở nhiều hệ thống: POS ghi từng hóa đơn tại quầy, ứng dụng riêng lưu đơn và khách hàng, sàn giao đồ ăn chỉ gửi báo cáo đối soát tổng hợp theo tuần, kho được quản lý bằng sổ nhập và phiếu kiểm kê thường ghi bằng Excel, nhân sự được theo dõi bằng máy chấm công. Các hệ thống này dùng những bộ mã khác nhau cho cùng một chi nhánh, nhân viên hay nguyên liệu, và không thống nhất về định dạng cũng như chất lượng dữ liệu. Vì vậy khi doanh thu một chi nhánh biến động, nhà quản lý thường chỉ thấy con số tổng hợp. Doanh thu giảm có thể là chuyện bình thường, như trời mưa hay kỳ nghỉ lễ vừa kết thúc, nhưng cũng có thể do chi nhánh thiếu người nên phải hủy đơn và bị tụt hạng trên sàn; lợi nhuận giảm khi doanh thu không đổi có thể do sàn tính sai hoa hồng, nguyên liệu hao hụt, hàng tồn bị thất thoát hoặc gian lận tại quầy. Tổng quan của Mariani et al. (2018) cũng cho thấy các nghiên cứu ứng dụng phân tích dữ liệu trong ngành nhà hàng, khách sạn còn rời rạc về phạm vi và hạn chế về phương pháp.

Từ thực tế đó, đề tài hướng tới một nền tảng tích hợp các nguồn dữ liệu không đồng nhất thành một kho dữ liệu sạch, nhất quán, rồi áp dụng các phương pháp phân tích giải thích được để phát hiện sự cố và truy vết nguyên nhân biến động, thay vì dừng ở một bảng điều khiển doanh thu. Bài toán đòi hỏi kết hợp kỹ thuật dữ liệu (Data Engineering) để dựng hạ tầng tích hợp với phân tích dữ liệu (Data Analytics) để diễn giải con số theo nghiệp vụ. Vì những lý do trên, đề tài “Xây dựng nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn hỗ trợ truy vết nguyên nhân biến động doanh thu cho chuỗi F&B” được lựa chọn làm nội dung khóa luận.

## 1.2. Phát biểu vấn đề

Đề tài tập trung vào năm vấn đề vận hành phổ biến của chuỗi đồ ăn nhanh (Bảng 1.1). Điểm chung của chúng là không thể phát hiện chắc chắn nếu chỉ nhìn một nguồn dữ liệu; phải đối chiếu ít nhất hai nguồn với nhau.

TABLE: Bảng 1.1. Năm vấn đề vận hành được nghiên cứu || Tổng hợp từ các tài liệu ở mục 2.1
WIDTHS: 1,4,4,4
| Mã | Vấn đề vận hành | Biểu hiện và lý do khó phát hiện | Nguồn dữ liệu cần đối chiếu |
| P1 | Sai lệch đối soát với sàn giao đồ ăn | Sàn tính hoa hồng cao hơn hợp đồng; hoặc đơn sàn không được nhập vào POS. Báo cáo sàn chỉ có số tổng theo tuần, không ghi tỷ lệ phí | Báo cáo đối soát GrabFood, ShopeeFood; POS; hợp đồng với sàn |
| P2 | Hao hụt nguyên liệu bất thường | Giá vốn thực tế cao hơn giá vốn lý thuyết theo công thức; chỉ thấy khi đặt lượng nhập kho cạnh lượng bán | Sổ nhập kho; POS và ứng dụng; công thức món |
| P3 | Nhân sự không khớp với tải đơn hàng | Thiếu người làm thời gian chuẩn bị tăng, khách bỏ về, cửa hàng hủy đơn, điểm trên sàn giảm, kéo doanh thu xuống nhiều tuần | Máy chấm công; POS, ứng dụng; báo cáo sàn |
| P4 | Thất thoát hàng tồn kho | Tồn kiểm kê thấp hơn tồn sổ sách; chỉ lộ ra ở kỳ kiểm kê | Phiếu kiểm kê; sổ nhập kho; lượng bán và công thức |
| P5 | Gian lận tại quầy thu ngân | Thu ngân thu tiền mặt rồi hủy hóa đơn; hóa đơn hủy lẫn vào số hủy hợp lệ | POS, gồm người thực hiện hủy; danh sách nhân viên |

Bên cạnh năm vấn đề trên, doanh thu còn biến động vì những lý do bình thường: cuối tuần, ngày lễ, ngày mưa, điều chỉnh giá bán. Một hệ thống truy vết tốt phải phân biệt được hai loại biến động này; nếu không, nó sẽ phát ra quá nhiều cảnh báo sai và mất giá trị sử dụng.

## 1.3. Câu hỏi nghiên cứu

- RQ1, về tích hợp dữ liệu: có thể tích hợp dữ liệu vận hành từ bảy hệ thống nguồn không đồng nhất về định dạng, mã định danh và chất lượng thành một kho dữ liệu nhất quán và kiểm chứng được hay không?
- RQ2, về phát hiện sự cố: các phương pháp thống kê và luật nghiệp vụ giải thích được phát hiện năm vấn đề P1–P5 chính xác đến mức nào, đặc biệt trên các kịch bản chưa từng được dùng để chọn ngưỡng?
- RQ3, về truy vết nguyên nhân: có thể truy một biến động doanh thu hoặc lợi nhuận về đúng nguyên nhân vận hành, đồng thời phân biệt với biến động bình thường do ngày trong tuần, ngày lễ, thời tiết và điều chỉnh giá hay không?

## 1.4. Mục tiêu nghiên cứu

### 1.4.1. Mục tiêu tổng quát

Xây dựng một nền tảng dữ liệu hoàn chỉnh, đi từ dữ liệu thô của các hệ thống nguồn đến kho dữ liệu và phân tích, có khả năng tích hợp dữ liệu vận hành đa nguồn của chuỗi F&B, phát hiện sự cố vận hành và hỗ trợ truy vết nguyên nhân biến động doanh thu.

### 1.4.2. Mục tiêu cụ thể

1. Xây dựng bộ dữ liệu mô phỏng cho một chuỗi đồ ăn nhanh, trong đó các nguồn nhất quán về nhân quả, mang lỗi dữ liệu đặc trưng của từng hệ thống và có đáp án cho mọi sự cố được đưa vào.
2. Xây dựng đường ống dữ liệu theo kiến trúc Medallion: thu thập và nạp tăng dần, làm sạch, chuẩn hóa, giải quyết định danh và cách ly dòng lỗi.
3. Thiết kế kho dữ liệu theo mô hình hóa chiều với lược đồ hình sao, có kiểm thử chất lượng tự động giữa các tầng.
4. Xây dựng bộ chỉ số vận hành theo chuẩn ngành F&B và cây KPI để truy vết nguyên nhân biến động.
5. Xây dựng năm bộ phát hiện cho P1–P5 và đánh giá định lượng trên một tập kịch bản độc lập.
6. Xây dựng ứng dụng cho người dùng nghiệp vụ, lớp báo cáo kinh doanh và cơ chế vận hành tự động hằng ngày.

## 1.5. Đối tượng và phạm vi nghiên cứu

### 1.5.1. Đối tượng nghiên cứu

Đối tượng nghiên cứu là dữ liệu vận hành đa nguồn của chuỗi nhà hàng phục vụ nhanh cùng các phương pháp tích hợp, mô hình hóa và phân tích dữ liệu đó để phát hiện sự cố, truy vết nguyên nhân biến động doanh thu. Do dữ liệu vận hành của doanh nghiệp F&B mang tính nhạy cảm thương mại và không được công khai, đề tài khảo sát một chuỗi giả định tên Fast&Fat như một trường hợp điển hình (representative case study): 11 chi nhánh tại Thành phố Hồ Chí Minh chia thành ba hạng theo quy mô, bán qua bốn kênh, thực đơn 28 món, 22 loại nguyên liệu và 145 nhân viên làm theo ca. Dữ liệu được xây dựng bằng mô phỏng có neo thực tế (reality-anchored simulation): tham số nền như giá món, tỷ lệ giá vốn, lương giờ lấy theo mức phổ biến trên thị trường; một số quy luật mua hàng được hiệu chỉnh từ dữ liệu giao dịch thật công khai (mục 3.3.5); các giao dịch được sinh theo đúng quy luật vận hành, trong đó nhân sự quyết định tải bếp, tải bếp quyết định thời gian chuẩn bị, tỷ lệ hủy đơn và thứ hạng trên sàn. Cách tiếp cận này cho phép đưa vào các kịch bản sự cố có đáp án biết trước để đánh giá định lượng, điều gần như không làm được với dữ liệu thật.

### 1.5.2. Phạm vi nghiên cứu

Về dữ liệu, đề tài dùng 26 tuần từ 11/03/2024 đến 08/09/2024 của 11 chi nhánh, khoảng 435 nghìn đơn được phục vụ ở tập dữ liệu chính, từ bảy nhóm hệ thống nguồn; hệ thống được thiết kế để tiếp tục nhận dữ liệu mới theo ngày. Về kỹ thuật, dữ liệu được xử lý theo lô hằng ngày vì chuỗi F&B ra quyết định theo nhịp ngày và tuần; quy mô hàng trăm megabyte nên không dùng nền tảng dữ liệu lớn phân tán. Dữ liệu đến bằng ba kênh như ngoài thực tế là kéo qua API, tệp xuất tự động và tệp do người gửi, trong đó API của phần mềm nguồn là dịch vụ giả lập. Phát hiện sự cố dựa trên thống kê và luật nghiệp vụ giải thích được; đề tài không xây dựng mô hình dự báo nhu cầu, không gửi cảnh báo qua kênh nhắn tin và không triển khai trên hạ tầng đám mây. Toàn bộ hệ thống được đóng gói bằng Docker Compose và chạy trên một máy.

## 1.6. Phương pháp nghiên cứu

Khóa luận tiếp cận theo hướng nghiên cứu khoa học thiết kế (Design Science Research) trong hệ thống thông tin (Hevner et al., 2004): sản phẩm nghiên cứu là một nền tảng giải quyết một vấn đề thực tiễn đã xác định và phải được đánh giá bằng thực nghiệm có kiểm soát. Quy trình đi theo sáu hoạt động của Peffers et al. (2007): xác định vấn đề, xác định mục tiêu của giải pháp, thiết kế và phát triển, trình diễn, đánh giá và truyền đạt kết quả. Đề tài kết hợp phương pháp nghiên cứu tài liệu để tổng hợp lý thuyết; phân tích nghiệp vụ để đi từ vấn đề vận hành đến dữ liệu cần có và đầu ra cho người dùng; mô phỏng có kiểm soát để sinh dữ liệu nguồn và kịch bản sự cố có đáp án; và thực nghiệm với hai tập kịch bản độc lập. Tập phát triển dùng để xây dựng và chọn tham số; tập kiểm tra chỉ được chạy một lần để đánh giá cuối cùng bằng precision, recall và F1, nhằm tránh hiện tượng quá khớp.

Hình 1.1 tóm tắt quy trình nghiên cứu gồm chín bước. Ba bước đầu xác định vấn đề, tổng hợp lý thuyết và thiết kế; ba bước tiếp theo xây dựng bộ mô phỏng, đường ống dữ liệu và lớp phân tích. Bước 6 và 7 được lặp trên tập phát triển cho tới khi chọn xong phương pháp và tham số; sau khi cấu hình được chốt, bước 8 chạy trên tập kiểm tra đúng một lần và kết quả được báo cáo nguyên trạng.

IMAGE: figures/h1_1_quy_trinh.png || Hình 1.1. Quy trình nghiên cứu của khóa luận || 13 || Phát triển từ Peffers et al. (2007)

## 1.7. Đóng góp của đề tài

Về khoa học, khóa luận có ba đóng góp: một bộ mô phỏng dữ liệu vận hành đa nguồn nhất quán về nhân quả, kèm lỗi dữ liệu đặc trưng và hai tập kịch bản sự cố có đáp án, dùng lại được để kiểm thử các phương pháp khác; một đường ống và kho dữ liệu có kiểm chứng giữa các tầng; và các bộ phát hiện cùng cây KPI giải thích được, đánh giá trên tập kiểm tra độc lập. Về thực tiễn, nền tảng cho thấy chuỗi F&B quy mô vừa có thể xây dựng hệ thống như vậy bằng công cụ mã nguồn mở trên một máy tính cá nhân.

## 1.8. Bố cục khóa luận

Ngoài Chương 1, khóa luận gồm Chương 2 về cơ sở lý thuyết và các nghiên cứu liên quan, Chương 3 về phân tích và thiết kế, Chương 4 về hiện thực và kiểm chứng từng thành phần, Chương 5 về thực nghiệm, đánh giá và các phát hiện kinh doanh, và Chương 6 về kết luận, hàm ý quản trị, hạn chế và hướng phát triển.
