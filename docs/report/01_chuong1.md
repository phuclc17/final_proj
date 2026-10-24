# CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

## 1.1. Bối cảnh và lý do chọn đề tài

Ngành ăn uống (F&B), đặc biệt là mô hình nhà hàng phục vụ nhanh (Quick-Service Restaurant – QSR), có tần suất giao dịch rất cao, giá trị mỗi đơn hàng nhỏ, vòng đời nguyên liệu ngắn và chịu ảnh hưởng mạnh của thời điểm cũng như cách thức vận hành. Một chi nhánh đồ ăn nhanh có thể phục vụ hàng trăm đơn mỗi ngày, tập trung vào vài khung giờ cao điểm. Chỉ cần thiếu một nhân viên bếp trong ca tối, một lô nguyên liệu tươi bị hỏng vì không xuất kho đúng thứ tự, hay một sai lệch nhỏ trong cách sàn giao đồ ăn tính phí, lợi nhuận của chi nhánh đã có thể giảm đáng kể mà người quản lý khó nhận ra.

Thị trường ăn uống Việt Nam có quy mô lớn và cạnh tranh gay gắt. Theo khảo sát hơn 4.000 nhà hàng và quán ăn của iPOS.vn (2025), doanh thu ngành F&B năm 2024 đạt gần 689.000 tỷ đồng, tăng 16,6% so với năm trước, với khoảng 323.000 cửa hàng, nhưng chỉ khoảng 14,7% doanh nghiệp ghi nhận tăng trưởng và hơn một phần ba gặp khó khăn trong kinh doanh. Kênh giao đồ ăn trực tuyến tăng nhanh nhất khu vực: tổng giá trị giao dịch năm 2024 đạt khoảng 1,8 tỷ USD, tăng 26%, và gần như chia đều cho hai sàn GrabFood và ShopeeFood (Momentum Works, 2025). Người tiêu dùng trẻ đã quen đặt món qua ứng dụng (Vu et al., 2023), trong khi các sàn thu hoa hồng cao trên mỗi đơn, tạo áp lực lớn lên biên lợi nhuận của nhà hàng (Feldman et al., 2023; Li et al., 2020). Trong bối cảnh tăng trưởng không đồng đều và biên lợi nhuận mỏng, khả năng nhận ra sớm nguyên nhân làm doanh thu và lợi nhuận suy giảm trở thành một năng lực cạnh tranh.

Song song với đó, mô hình bán hàng của các chuỗi đồ ăn nhanh đã chuyển sang đa kênh. Bên cạnh bán tại quầy, chuỗi thường có ứng dụng đặt hàng riêng và đồng thời bán qua các sàn giao đồ ăn như GrabFood, ShopeeFood. Mỗi kênh vận hành trên một hệ thống khác nhau và tạo ra dữ liệu theo cách riêng. Hệ thống bán hàng tại quầy (POS) ghi nhận từng hóa đơn; ứng dụng riêng lưu đơn hàng và thông tin khách hàng; sàn giao đồ ăn chỉ gửi báo cáo đối soát tổng hợp theo tuần; kho được quản lý bằng sổ nhập kho và phiếu kiểm kê, nhiều nơi vẫn do quản lý cửa hàng tự ghi bằng Excel; nhân sự được theo dõi bằng máy chấm công. Các hệ thống này dùng những bộ mã khác nhau cho cùng một chi nhánh, một nhân viên hay một nguyên liệu, và không thống nhất về định dạng ngày giờ, đơn vị tính cũng như chất lượng dữ liệu.

Hệ quả là khi doanh thu hoặc lợi nhuận của một chi nhánh biến động, nhà quản lý thường chỉ nhìn thấy con số tổng hợp, còn câu hỏi biến động đó đến từ đâu thì rất khó trả lời. Tổng quan của Mariani et al. (2018) về trí tuệ kinh doanh và dữ liệu lớn trong ngành khách sạn, nhà hàng cũng cho thấy các nghiên cứu ứng dụng phân tích dữ liệu trong lĩnh vực này còn rời rạc về phạm vi và hạn chế về phương pháp. Doanh thu giảm có thể là chuyện bình thường, chẳng hạn trời mưa khiến khách ít đến quầy hay kỳ nghỉ lễ vừa kết thúc, nhưng cũng có thể là dấu hiệu của một sự cố vận hành, chẳng hạn chi nhánh thiếu người nên phải hủy đơn và bị tụt hạng trên sàn. Lợi nhuận giảm trong khi doanh thu không đổi có thể do sàn tính sai phí hoa hồng, nguyên liệu hao hụt bất thường, hàng tồn kho bị thất thoát hoặc có gian lận tại quầy thu ngân. Muốn lý giải một con số trong ngành F&B, người phân tích phải đặt nó vào ba bối cảnh là thời gian và ca làm việc, chi phí ẩn và hao hụt, trải nghiệm của khách hàng; trong khi dữ liệu của ba bối cảnh này lại nằm ở ba nhóm hệ thống khác nhau.

Từ thực tế đó, đề tài hướng tới một nền tảng dữ liệu tích hợp các nguồn không đồng nhất thành một kho dữ liệu sạch và nhất quán, rồi trên kho dữ liệu này áp dụng các phương pháp phân tích có thể giải thích được để phát hiện sự cố và truy vết nguyên nhân biến động, thay vì chỉ dừng ở một bảng điều khiển doanh thu. Bài toán đòi hỏi kết hợp kỹ thuật dữ liệu (Data Engineering) để dựng hạ tầng tích hợp với phân tích dữ liệu (Data Analytics) để diễn giải con số theo nghiệp vụ, và có giá trị ứng dụng trực tiếp đối với các chuỗi F&B. Vì những lý do trên, đề tài “Xây dựng nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn hỗ trợ truy vết nguyên nhân biến động doanh thu cho chuỗi F&B” được lựa chọn làm nội dung khóa luận.

## 1.2. Phát biểu vấn đề

Đề tài tập trung vào năm vấn đề vận hành phổ biến của chuỗi đồ ăn nhanh. Điểm chung của năm vấn đề là không thể phát hiện chắc chắn nếu chỉ nhìn vào một nguồn dữ liệu; người phân tích phải đối chiếu ít nhất hai nguồn với nhau (Bảng 1.1).

TABLE: Bảng 1.1. Năm vấn đề vận hành được nghiên cứu || Tổng hợp từ các tài liệu ở mục 2.1
WIDTHS: 1,4,4,4
| Mã | Vấn đề vận hành | Biểu hiện và lý do khó phát hiện | Nguồn dữ liệu cần đối chiếu |
| P1 | Sai lệch đối soát với sàn giao đồ ăn | Sàn tính phí hoa hồng cao hơn hợp đồng; hoặc nhân viên không nhập đơn sàn vào POS. Báo cáo sàn chỉ có số tổng theo tuần, không ghi tỷ lệ phí | Báo cáo đối soát GrabFood, ShopeeFood; POS; hợp đồng với sàn |
| P2 | Hao hụt nguyên liệu bất thường | Giá vốn thực tế cao hơn giá vốn lý thuyết theo công thức; chỉ thấy khi đặt lượng nhập kho cạnh lượng bán | Sổ nhập kho; POS và ứng dụng; công thức món |
| P3 | Nhân sự không khớp với tải đơn hàng | Thiếu người làm thời gian chuẩn bị tăng, khách bỏ về, cửa hàng hủy đơn, điểm đánh giá trên sàn giảm, kéo doanh thu xuống trong nhiều tuần; thừa người làm chi phí nhân công tăng | Máy chấm công; POS, ứng dụng; báo cáo sàn |
| P4 | Thất thoát hàng tồn kho | Tồn thực tế khi kiểm kê thấp hơn tồn sổ sách; chỉ lộ ra ở kỳ kiểm kê | Phiếu kiểm kê; sổ nhập kho; lượng bán và công thức |
| P5 | Gian lận tại quầy thu ngân | Thu ngân thu tiền mặt rồi hủy hóa đơn; hóa đơn hủy lẫn vào số hủy hợp lệ | POS, gồm người thực hiện hủy; danh sách nhân viên |

Bên cạnh năm vấn đề trên, doanh thu của chuỗi còn biến động vì những lý do bình thường: cuối tuần đông hơn ngày thường, ngày lễ tăng mạnh, ngày mưa khách tại quầy giảm nhưng đơn giao hàng tăng, điều chỉnh giá bán làm giá trị đơn trung bình thay đổi. Một hệ thống truy vết tốt phải phân biệt được biến động bình thường với biến động do sự cố; nếu không, hệ thống sẽ phát ra quá nhiều cảnh báo sai và mất giá trị sử dụng.

## 1.3. Câu hỏi nghiên cứu

Từ vấn đề trên, khóa luận đặt ra ba câu hỏi nghiên cứu:

- RQ1, về tích hợp dữ liệu: có thể tích hợp dữ liệu vận hành từ bảy hệ thống nguồn không đồng nhất về định dạng, mã định danh và chất lượng thành một kho dữ liệu nhất quán và kiểm chứng được hay không?
- RQ2, về phát hiện sự cố: các phương pháp thống kê và luật nghiệp vụ có thể giải thích được phát hiện năm vấn đề vận hành P1–P5 chính xác đến mức nào, đặc biệt trên các kịch bản chưa từng được dùng để chọn ngưỡng?
- RQ3, về truy vết nguyên nhân: có thể truy một biến động doanh thu hoặc lợi nhuận về đúng nguyên nhân vận hành, đồng thời phân biệt với biến động bình thường do ngày trong tuần, ngày lễ, thời tiết và điều chỉnh giá hay không?

## 1.4. Mục tiêu nghiên cứu

### 1.4.1. Mục tiêu tổng quát

Xây dựng một nền tảng dữ liệu hoàn chỉnh, đi từ dữ liệu thô của các hệ thống nguồn đến kho dữ liệu và các phân tích, có khả năng tích hợp dữ liệu vận hành đa nguồn của chuỗi F&B, phát hiện các sự cố vận hành và hỗ trợ truy vết nguyên nhân biến động doanh thu.

### 1.4.2. Mục tiêu cụ thể

1. Xây dựng bộ dữ liệu mô phỏng sát thực tế cho một chuỗi đồ ăn nhanh, trong đó các nguồn dữ liệu nhất quán với nhau về mặt nhân quả, mang các lỗi dữ liệu đặc trưng của từng hệ thống và có đáp án (ground truth) cho mọi sự cố được đưa vào.
2. Xây dựng đường ống dữ liệu theo kiến trúc Medallion: nạp dữ liệu thô tăng dần, làm sạch và chuẩn hóa, giải quyết định danh thực thể giữa các hệ thống, cách ly các dòng dữ liệu lỗi.
3. Thiết kế và xây dựng kho dữ liệu theo phương pháp mô hình hóa chiều với lược đồ hình sao, có kiểm thử chất lượng dữ liệu tự động giữa các tầng.
4. Xây dựng bộ chỉ số vận hành theo chuẩn ngành F&B và cây KPI để truy vết nguyên nhân biến động.
5. Xây dựng năm bộ phát hiện cho năm vấn đề P1–P5 và đánh giá định lượng trên một tập kịch bản độc lập.
6. Xây dựng ứng dụng trực quan cho người dùng nghiệp vụ, lớp báo cáo kinh doanh và cơ chế vận hành tự động hằng ngày.

## 1.5. Đối tượng và phạm vi nghiên cứu

### 1.5.1. Đối tượng nghiên cứu

Đối tượng nghiên cứu là dữ liệu vận hành đa nguồn của chuỗi nhà hàng phục vụ nhanh cùng các phương pháp tích hợp, mô hình hóa và phân tích dữ liệu đó để phát hiện sự cố, truy vết nguyên nhân biến động doanh thu.

Dữ liệu vận hành của doanh nghiệp F&B, gồm hóa đơn bán hàng, báo cáo đối soát với sàn, sổ kho và dữ liệu chấm công, mang tính nhạy cảm thương mại và không được công khai. Vì vậy, đề tài khảo sát một chuỗi F&B giả định, đặt tên là Fast&Fat, như một trường hợp điển hình (representative case study). Fast&Fat đại diện cho mô hình vận hành phổ biến của chuỗi đồ ăn nhanh quy mô vừa tại Thành phố Hồ Chí Minh: 11 chi nhánh được phân thành ba hạng theo quy mô, bán qua bốn kênh là tại quầy, ứng dụng riêng, GrabFood và ShopeeFood, có thực đơn 28 món, 22 loại nguyên liệu và 145 nhân viên làm việc theo ca. Fast&Fat không phải là một doanh nghiệp có thật.

Dữ liệu được xây dựng theo phương pháp mô phỏng có neo thực tế (reality-anchored simulation). Các tham số nền như vị trí chi nhánh, mức giá món, tỷ lệ giá vốn theo món, lương giờ và cơ cấu nhân sự được lấy theo các mức phổ biến trên thị trường. Một số quy luật hành vi mua hàng, gồm số món mỗi đơn, mức độ tập trung vào các món bán chạy và độ dao động doanh số theo ngày, được hiệu chỉnh từ một bộ dữ liệu giao dịch thật đã công bố công khai (mục 3.3.8). Các giao dịch cụ thể được sinh có kiểm soát theo đúng quy luật vận hành: nhu cầu thay đổi theo giờ, theo ngày trong tuần, theo ngày lễ và thời tiết; nhân sự quyết định tải bếp, tải bếp quyết định thời gian chuẩn bị, tỷ lệ hủy đơn và thứ hạng trên sàn. Cách tiếp cận này cho phép đưa vào các kịch bản sự cố có đáp án biết trước để đánh giá định lượng độ chính xác của hệ thống. Với dữ liệu thật, việc đánh giá như vậy gần như không thực hiện được vì không có đáp án đối chứng độc lập cho từng sự cố.

### 1.5.2. Phạm vi nghiên cứu

Về dữ liệu, đề tài dùng dữ liệu 26 tuần, từ 11/03/2024 đến 08/09/2024, của 11 chi nhánh, với khoảng 435 nghìn đơn hàng được phục vụ ở tập dữ liệu chính, đến từ bảy nhóm hệ thống nguồn. Hệ thống được thiết kế để tiếp tục nhận dữ liệu mới theo từng ngày.

Về kỹ thuật, phạm vi được giới hạn như sau:

- Dữ liệu được xử lý theo lô hằng ngày, không xử lý luồng thời gian thực, vì chuỗi F&B ra quyết định vận hành theo nhịp ngày và tuần.
- Quy mô dữ liệu ở mức hàng trăm megabyte, nên công nghệ được chọn tương xứng, không dùng các nền tảng dữ liệu lớn phân tán. Đường ống tính toán trên DuckDB; tầng Gold được sao sang PostgreSQL làm kho phục vụ cho công cụ báo cáo kinh doanh (BI).
- Dữ liệu đến nền tảng bằng ba kênh như ngoài thực tế: kéo qua API, tệp xuất tự động và tệp do người gửi. Do không có quyền truy cập hệ thống của doanh nghiệp, API của phần mềm nguồn là một dịch vụ giả lập.
- Việc phát hiện sự cố và truy vết dựa trên thống kê và luật nghiệp vụ có thể giải thích được; đề tài không xây dựng mô hình dự báo nhu cầu.
- Đề tài không tích hợp dữ liệu thật của doanh nghiệp, không gửi cảnh báo qua kênh nhắn tin và không triển khai trên hạ tầng đám mây. Toàn bộ hệ thống được đóng gói bằng Docker Compose và chạy trên một máy; cách chuyển lên đám mây được trình bày ở phần hướng phát triển.

## 1.6. Phương pháp nghiên cứu

Khóa luận tiếp cận theo hướng nghiên cứu khoa học thiết kế (Design Science Research) trong lĩnh vực hệ thống thông tin (Hevner et al., 2004). Theo hướng này, sản phẩm nghiên cứu là một nền tảng dữ liệu giải quyết một vấn đề thực tiễn đã xác định, và sản phẩm đó phải được đánh giá bằng thực nghiệm có kiểm soát. Quy trình thực hiện đi theo sáu hoạt động của phương pháp nghiên cứu khoa học thiết kế do Peffers et al. (2007) đề xuất: xác định vấn đề, xác định mục tiêu của giải pháp, thiết kế và phát triển, trình diễn, đánh giá và truyền đạt kết quả. Đề tài kết hợp bốn phương pháp:

- Phương pháp nghiên cứu tài liệu, dùng để tổng hợp lý thuyết về kiến trúc dữ liệu, mô hình hóa chiều, chất lượng dữ liệu, phát hiện bất thường và các chỉ số quản trị vận hành F&B.
- Phương pháp phân tích nghiệp vụ, đi từ vấn đề vận hành đến câu hỏi kinh doanh, dữ liệu cần có, giải pháp kỹ thuật và đầu ra cho người dùng.
- Phương pháp mô phỏng có kiểm soát, dùng để sinh dữ liệu nguồn nhất quán về nhân quả cùng các kịch bản sự cố có đáp án; các phân phối đầu vào của bộ mô phỏng được hiệu chỉnh từ dữ liệu giao dịch thật công khai ở những chỗ có thể.
- Phương pháp thực nghiệm và đánh giá định lượng với hai tập kịch bản độc lập. Tập phát triển dùng để xây dựng và chọn tham số cho các bộ phát hiện; tập kiểm tra chỉ được dùng một lần để đánh giá cuối cùng bằng các độ đo precision, recall và F1. Cách tách này giúp tránh hiện tượng quá khớp, tức bộ phát hiện chỉ đúng trên chính dữ liệu đã dùng để tinh chỉnh nó.

Hình 1.1 tóm tắt quy trình nghiên cứu gồm chín bước và chương trình bày từng bước. Ba bước đầu xác định vấn đề, tổng hợp cơ sở lý thuyết và thiết kế hệ thống. Ba bước tiếp theo xây dựng sản phẩm: bộ mô phỏng đóng vai các hệ thống nguồn, đường ống dữ liệu và lớp phân tích. Bước 6 và bước 7 được lặp lại nhiều lần trên tập phát triển cho tới khi chọn được phương pháp và tham số; sau khi cấu hình đã được chốt, bước 8 chạy trên tập kiểm tra đúng một lần và kết quả được báo cáo nguyên trạng.

IMAGE: figures/h1_1_quy_trinh.png || Hình 1.1. Quy trình nghiên cứu của khóa luận || 16 || Phát triển từ Peffers et al. (2007)

## 1.7. Đóng góp và ý nghĩa của đề tài

Về mặt khoa học, khóa luận có ba đóng góp chính. Thứ nhất là một bộ mô phỏng dữ liệu vận hành đa nguồn nhất quán về nhân quả, trong đó mọi hệ thống nguồn là những góc nhìn khác nhau của cùng một tập sự kiện, kèm các lỗi dữ liệu đặc trưng và hai tập kịch bản sự cố có đáp án; bộ mô phỏng này có thể dùng lại để kiểm thử các đường ống dữ liệu và phương pháp phân tích khác. Thứ hai là một đường ống và kho dữ liệu có kiểm chứng: nạp tăng dần có tính lũy đẳng, làm sạch và giải quyết định danh giữa sáu hệ mã khác nhau, lược đồ hình sao với chiều thay đổi chậm, kiểm thử chất lượng dữ liệu tự động và đối soát giữa các tầng. Thứ ba là các bộ phát hiện sự cố và cây KPI truy vết có thể giải thích được, được đánh giá trên một tập kịch bản kiểm tra độc lập.

Về mặt thực tiễn, nền tảng minh họa một cách làm khả thi cho các chuỗi F&B quy mô vừa: dùng công cụ mã nguồn mở, chạy được trên một máy tính cá nhân nhưng vẫn tuân theo các nguyên tắc kỹ thuật dữ liệu chuẩn mực.

## 1.8. Bố cục khóa luận

Ngoài phần mở đầu, tài liệu tham khảo và phụ lục, khóa luận gồm sáu chương. Chương 1 trình bày bối cảnh, vấn đề, câu hỏi nghiên cứu, mục tiêu, phạm vi và phương pháp nghiên cứu. Chương 2 tổng hợp cơ sở lý thuyết về nghiệp vụ vận hành F&B, kiến trúc dữ liệu, mô hình hóa chiều, chất lượng dữ liệu, phát hiện bất thường và truy vết nguyên nhân, dữ liệu mô phỏng, công nghệ sử dụng, đồng thời điểm qua các nghiên cứu liên quan để xác định khoảng trống mà đề tài hướng tới. Chương 3 phân tích yêu cầu và thiết kế hệ thống, gồm kiến trúc tổng thể, bộ mô phỏng, đường ống dữ liệu, kho dữ liệu, kiểm soát chất lượng, lớp phân tích và ứng dụng. Chương 4 trình bày việc hiện thực từng thành phần cùng kết quả kiểm chứng. Chương 5 đánh giá đường ống dữ liệu, các bộ phát hiện và khả năng truy vết, phân tích độ nhạy và trình bày các phát hiện kinh doanh. Chương 6 tổng kết kết quả, rút ra hàm ý quản trị cho các chuỗi F&B, nêu hạn chế và hướng phát triển.
