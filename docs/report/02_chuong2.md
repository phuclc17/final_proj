# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÁC NGHIÊN CỨU LIÊN QUAN

Chương này trình bày cơ sở cho khóa luận theo hai mạch. Mạch nghiệp vụ (mục 2.1) giải thích các chỉ số quản trị vận hành của chuỗi F&B, từ đó xác định dữ liệu cần thu thập và dấu vết mà mỗi vấn đề để lại. Mạch kỹ thuật (mục 2.2 đến 2.7) trình bày kiến trúc dữ liệu, mô hình hóa chiều, chất lượng dữ liệu, phát hiện bất thường, dữ liệu mô phỏng và công nghệ được chọn. Mục 2.8 tổng quan các nghiên cứu liên quan; mục 2.9 nêu khoảng trống nghiên cứu.

## 2.1. Nghiệp vụ vận hành chuỗi đồ ăn nhanh và các chỉ số then chốt

### 2.1.1. Bán hàng đa kênh và đối soát với sàn giao đồ ăn

Một chuỗi đồ ăn nhanh thường bán qua bốn kênh: tại quầy qua hệ thống POS, ứng dụng đặt hàng riêng, và các sàn giao đồ ăn như GrabFood, ShopeeFood. Với kênh sàn, tiền khách trả đi qua sàn; mỗi tuần sàn gửi cho cửa hàng một báo cáo đối soát (settlement report) gồm doanh thu món, số đơn, phí hoa hồng, khuyến mãi, quảng cáo và số tiền thực nhận. Quy trình này có hai rủi ro. Thứ nhất, hoa hồng thực tế có thể lệch so với hợp đồng, và vì báo cáo chỉ ghi số tiền chứ không ghi tỷ lệ, sai lệch chỉ lộ ra khi tính lại tỷ lệ hiệu dụng rồi so với hợp đồng. Rủi ro này đáng kể vì hoa hồng là khoản chi lớn nhất của kênh sàn và là nguồn xung đột chính giữa nhà hàng với nền tảng (Feldman et al., 2023; Li et al., 2020). Thứ hai, khi nhân viên phải nhập tay đơn sàn vào POS, đơn bị bỏ sót làm doanh thu nội bộ thiếu so với báo cáo của sàn trong khi nguyên liệu vẫn bị tiêu hao; chỉ đối chiếu số đơn giữa hai nguồn mới phát hiện được.

### 2.1.2. Giá vốn hàng bán và chênh lệch thực tế – lý thuyết

Giá vốn hàng bán (Cost of Goods Sold – COGS) là giá trị nguyên liệu đã tiêu hao để tạo ra doanh thu. Chỉ số quản trị phổ biến nhất là tỷ lệ giá vốn trên doanh thu:

EQ: \mathrm{COGS\%} = \frac{\text{Giá vốn hàng bán}}{\text{Doanh thu thuần}} \times 100\% || (2.1)

Để biết giá vốn tăng vì sao, các tài liệu về kiểm soát chi phí F&B phân biệt hai loại giá vốn (Dopson & Hayes, 2019). *Giá vốn lý thuyết* là giá vốn lẽ ra phải có nếu mọi món được chế biến đúng định mức:

EQ: \text{Giá vốn lý thuyết} = \sum_{i} q_{i} \sum_{j} a_{ij}\, p_{j} || (2.2)

NOINDENT: trong đó $q_{i}$ là số lượng bán của món $i$ trong kỳ, $a_{ij}$ là định mức nguyên liệu $j$ cho một phần món $i$ và $p_{j}$ là đơn giá của nguyên liệu $j$. *Giá vốn thực tế* được tính từ biến động kho trong một kỳ kiểm kê, quy ra giá trị:

EQ: \text{Giá vốn thực tế} = \text{Tồn đầu kỳ} + \text{Nhập trong kỳ} - \text{Tồn cuối kỳ} || (2.3)

Chênh lệch giữa hai đại lượng, gọi là chênh lệch thực tế – lý thuyết (Actual versus Theoretical – AvT), đo phần nguyên liệu tiêu hao không tạo ra doanh thu: hư hỏng do bảo quản hoặc không xuất kho theo nguyên tắc nhập trước – xuất trước (FIFO), chế biến sai định lượng hoặc thất thoát. Hao hụt phát sinh ở mọi khâu từ nhập, bảo quản, sơ chế đến phục vụ, nên phải đo theo từng khâu mới tìm được biện pháp phòng ngừa (Papargyropoulou et al., 2016). Không có ngưỡng COGS% chung cho mọi nhà hàng, vì tỷ lệ này phụ thuộc mô hình kinh doanh và cơ cấu món (Dopson & Hayes, 2019); khóa luận vì vậy so COGS% và AvT của một chi nhánh với lịch sử của nó và với các chi nhánh cùng hạng.

### 2.1.3. Chi phí và hiệu suất nhân công

Nhân công là khoản chi lớn thứ hai sau giá vốn. Hai nhóm chỉ số thường dùng là tỷ lệ chi phí nhân công trên doanh thu và năng suất theo giờ công, trong đó SPLH (Sales per Labor Hour) là doanh thu và OPLH (Orders per Labor Hour) là số đơn trên mỗi giờ công:

EQ: \mathrm{Labor\%} = \frac{\text{Chi phí nhân công}}{\text{Doanh thu thuần}} \times 100\% || (2.4)

EQ: \mathrm{SPLH} = \frac{\text{Doanh thu}}{\text{Tổng giờ công}}, \qquad \mathrm{OPLH} = \frac{\text{Số đơn}}{\text{Tổng giờ công}} || (2.5)

Nhu cầu nhà hàng dao động mạnh theo giờ, nên lịch phân ca phải được lập từ nhu cầu theo khung giờ (Thompson, 1998) và quản trị doanh thu nhà hàng lấy công suất theo khung giờ làm đối tượng điều chỉnh chính (Kimes, 1999). Khi ca đông thiếu người, thời gian chuẩn bị kéo dài, khách bỏ về, cửa hàng hủy đơn trực tuyến và điểm đánh giá trên sàn giảm; vì sàn ưu tiên cửa hàng có điểm cao, thiệt hại doanh thu có thể kéo dài nhiều tuần sau khi tình trạng thiếu người đã kết thúc. Mức Labor% hợp lý phụ thuộc quy mô cửa hàng (Dopson & Hayes, 2019): chi nhánh nhỏ vẫn phải duy trì số người tối thiểu mỗi ca nên Labor% cao hơn mà không có nghĩa là thừa người, do đó so sánh phải đặt trong nhóm cùng hạng.

### 2.1.4. Tồn kho, kiểm kê và thất thoát

Kiểm soát kho gồm kiểm soát hằng ngày, như theo dõi lượng nhập và áp dụng FIFO, và kiểm kê định kỳ, tức đếm tồn thực tế rồi so với tồn sổ sách tính từ lần kiểm kê trước cộng nhập trừ tiêu hao lý thuyết. Chênh lệch âm vượt mức sai số đếm tay là dấu hiệu thất thoát (inventory shrinkage):

EQ: \text{Tỷ lệ chênh lệch kiểm kê} = \frac{\text{Tồn kiểm kê} - \text{Tồn sổ sách}}{\text{Tồn sổ sách}} || (2.6)

Sai lệch tồn kho phổ biến hơn nhiều so với cảm nhận của nhà quản lý: khoảng 65% trong gần 370.000 bản ghi tồn kho của 37 cửa hàng bán lẻ không khớp thực tế, và tần suất kiểm kê là một yếu tố làm giảm sai lệch (DeHoratius & Raman, 2008); thất thoát nhỏ không được ghi nhận, khi tích lũy, đủ gây thiếu hàng nghiêm trọng (Kang & Gershwin, 2005). Khóa luận phân biệt hai vấn đề kho: P2 là hao hụt vượt định mức của hàng tươi giá thấp, thường do bảo quản và chế biến; P4 là thất thoát nguyên liệu giá trị cao, nơi động cơ lấy cắp lớn nhất. Cả hai được đánh giá theo kỳ kiểm kê.

### 2.1.5. Gian lận tại quầy thu ngân

Chức năng hủy hóa đơn (void) và hoàn tiền (refund) của POS có thể bị lạm dụng: thu ngân nhận tiền mặt, giao món, rồi hủy hóa đơn và giữ lại tiền. Doanh thu trên hệ thống giảm nhưng két không thiếu tiền, nên dấu hiệu chỉ nằm ở mẫu hình, đặc biệt là tỷ lệ hủy của một thu ngân cao bất thường so với đồng nghiệp cùng chi nhánh. Phát hiện gian lận bằng thống kê dựa trên việc so hành vi của một đối tượng với chính nó hoặc với các đối tượng tương tự, và kết quả chỉ là mức nghi vấn để con người kiểm tra tiếp (Bolton & Hand, 2002). Về dữ liệu, cần liên kết hóa đơn POS với danh sách nhân viên, trong khi mã nhân viên trên POS thường khác mã trên hệ thống chấm công.

### 2.1.6. Nguyên tắc phân tích dữ liệu vận hành F&B

Từ các đặc thù trên, khóa luận áp dụng bốn nguyên tắc phân tích xuyên suốt:

- Không kết luận từ tổng doanh thu; mọi chỉ số được tách theo thời gian, chi nhánh, kênh và món, và luôn đặt doanh thu cạnh chi phí.
- So sánh trong nhóm đồng nhất: một giá trị chỉ bất thường khi so với lịch sử của chính chi nhánh hoặc với các chi nhánh cùng hạng.
- Phân biệt biến động bình thường với sự cố: ngày lễ, thời tiết và điều chỉnh giá tác động lên nhiều chi nhánh cùng lúc, còn sự cố thường chỉ xảy ra ở một chi nhánh, một kênh hoặc một nhân viên.
- Quy mọi phát hiện ra tác động bằng tiền, kèm hành động đề xuất.

## 2.2. Kiến trúc dữ liệu cho phân tích

### 2.2.1. Kho dữ liệu, hồ dữ liệu và lakehouse

*Kho dữ liệu* (data warehouse) là tập hợp dữ liệu hướng chủ đề, tích hợp, ổn định và có tính lịch sử, phục vụ ra quyết định (Inmon, 2005), được tối ưu cho truy vấn phân tích trực tuyến (OLAP) thay vì ghi nhận giao dịch (Chaudhuri & Dayal, 1997). Cách tiếp cận của Kimball xây dựng kho theo từng quy trình nghiệp vụ bằng mô hình chiều, kết nối với nhau qua các chiều dùng chung (Kimball & Ross, 2013); quy trình thiết kế đi từ yêu cầu phân tích của người dùng đến thiết kế khái niệm, logic và vật lý (Golfarelli & Rizzi, 2009). *Hồ dữ liệu* (data lake) lưu dữ liệu thô nhiều định dạng với chi phí thấp nhưng dễ thành "đầm lầy dữ liệu" nếu không quản lý chất lượng; kiến trúc lakehouse kết hợp lưu trữ mở của hồ dữ liệu với khả năng quản trị và hiệu năng của kho dữ liệu (Armbrust et al., 2021).

### 2.2.2. ELT và kiến trúc Medallion

Theo cách ETL truyền thống, dữ liệu được biến đổi trên máy chủ trung gian rồi mới nạp vào kho (Kimball & Caserta, 2004), với các vấn đề chung như phát hiện thay đổi ở nguồn, chuyển đổi định danh và nạp lại khi lỗi (Vassiliadis, 2009). Cách ELT nạp dữ liệu thô nguyên trạng vào nền tảng phân tích trước rồi biến đổi ngay trong nền tảng bằng SQL, nhờ đó giữ được bản gốc để xử lý lại khi quy tắc làm sạch thay đổi (Reis & Housley, 2022). Kiến trúc Medallion tổ chức dữ liệu ELT thành ba tầng có chất lượng tăng dần (Databricks, n.d.): Bronze giữ nguyên dữ liệu nguồn kèm siêu dữ liệu nạp; Silver ép kiểu, chuẩn hóa, giải quyết định danh và tách dòng lỗi; Gold tổ chức dữ liệu cho phân tích dưới dạng lược đồ hình sao và bảng chỉ số. Mỗi tầng một trách nhiệm, kiểm thử được độc lập, và lỗi ở tầng sau không làm mất dữ liệu gốc ở tầng trước.

### 2.2.3. Thu thập dữ liệu, nạp tăng dần và tính lũy đẳng

Dữ liệu đến nền tảng theo hai kiểu: đẩy, khi hệ thống nguồn hoặc con người gửi tệp, và kéo, khi đường ống chủ động lấy qua API của phần mềm nguồn (Reis & Housley, 2022). Các API này phần lớn theo phong cách REST (Fielding, 2000) và được mô tả bằng đặc tả OpenAPI (OpenAPI Initiative, 2021). Kéo qua API cần một mốc (watermark) để chỉ lấy phần mới, lấy lại một khoảng trước mốc cho dữ liệu đến trễ, đi hết các trang, đối chiếu tổng số bản ghi và thử lại khi lỗi tạm thời. Với dữ liệu đẩy, rủi ro là tệp sai cấu trúc hoặc gửi trùng; cách phòng ngừa là *hợp đồng dữ liệu*, tức thỏa thuận về cấu trúc và ý nghĩa của dữ liệu được kiểm tra tự động ngay khi dữ liệu đến (Reis & Housley, 2022). Khi dữ liệu đến hằng ngày, đường ống cần *nạp tăng dần* (incremental load), chỉ xử lý phần mới, và *lũy đẳng* (idempotency), tức chạy lại cùng một lần nạp cho cùng kết quả. Thao tác lũy đẳng là điều kiện để thử lại an toàn sau lỗi (Kleppmann, 2017), thường đạt được bằng nhật ký nạp ghi mã băm của từng tệp và giao dịch bao trọn mỗi lần nạp.

## 2.3. Mô hình hóa dữ liệu chiều

### 2.3.1. Bảng sự kiện, bảng chiều và lược đồ hình sao

Mô hình hóa chiều tổ chức dữ liệu thành *bảng sự kiện* (fact table) lưu các đo lường của một quy trình nghiệp vụ và *bảng chiều* (dimension table) lưu ngữ cảnh mô tả sự kiện (Kimball & Ross, 2013). Khái niệm trung tâm là *hạt dữ liệu* (grain), tức mỗi dòng của bảng sự kiện đại diện cho điều gì; khai báo hạt ở mức chi tiết nhất giúp bảng sự kiện trả lời được nhiều câu hỏi chưa lường trước. Bảng sự kiện có thể là bảng giao dịch hoặc bảng ảnh chụp định kỳ, như tồn kho tại kỳ kiểm kê. Trong *lược đồ hình sao* (star schema), mỗi bảng sự kiện liên kết trực tiếp với các bảng chiều đã phi chuẩn hóa, dễ hiểu với người dùng và truy vấn nhanh. Khi có nhiều quy trình, các bảng sự kiện dùng chung *chiều đồng nhất* (conformed dimension), được thiết kế bằng *ma trận bus* (Kimball & Ross, 2013); trong đề tài, chiều chi nhánh và chiều ngày phải dùng chung thì mới đặt được doanh thu cạnh giá vốn và chi phí nhân công của cùng chi nhánh, cùng ngày.

### 2.3.2. Chiều thay đổi chậm

Thuộc tính của chiều thay đổi theo thời gian, như giá món hay lương nhân viên. Kỹ thuật *chiều thay đổi chậm* (Slowly Changing Dimension – SCD) xác định cách lưu các thay đổi này (Bảng 2.1). Đề tài dùng SCD kiểu 2 cho chiều món và chiều nhân viên, vì giá bán và lương tại thời điểm giao dịch quyết định giá vốn lý thuyết và chi phí nhân công; nếu ghi đè, mọi phân tích trước ngày điều chỉnh giá sẽ sai.

TABLE: Bảng 2.1. Các kiểu chiều thay đổi chậm phổ biến || Kimball và Ross (2013)
WIDTHS: 2,5,5
| Kiểu | Cách xử lý | Hệ quả |
| Kiểu 0 | Giữ nguyên giá trị ban đầu | Không phản ánh thay đổi |
| Kiểu 1 | Ghi đè giá trị cũ | Mất lịch sử; sự kiện cũ hiển thị theo giá trị mới |
| Kiểu 2 | Thêm dòng mới với khoảng hiệu lực và cờ bản hiện hành | Giữ đầy đủ lịch sử; sự kiện liên kết đúng phiên bản tại thời điểm xảy ra |
| Kiểu 3 | Thêm cột lưu giá trị trước đó | Chỉ giữ được một mức lịch sử |

## 2.4. Chất lượng dữ liệu

### 2.4.1. Các chiều chất lượng dữ liệu

Chất lượng dữ liệu là mức độ phù hợp của dữ liệu với mục đích sử dụng. Wang và Strong (1996) đề xuất khung chất lượng nhìn từ phía người sử dụng; các nghiên cứu sau tổng hợp thành những chiều đo lường được (Batini & Scannapieco, 2016) và định lượng từng chiều bằng các tỷ lệ đơn giản như tỷ lệ bản ghi đầy đủ hay hợp lệ (Pipino et al., 2002). Rahm và Do (2000) phân biệt lỗi trong một nguồn, như sai miền, trùng, thiếu, với lỗi chỉ xuất hiện khi tích hợp nhiều nguồn, như một thực thể mang nhiều mã; dữ liệu của đề tài có cả hai loại (Bảng 2.2).

TABLE: Bảng 2.2. Các chiều chất lượng dữ liệu và ví dụ trong đề tài || Tổng hợp từ Wang và Strong (1996), Batini và Scannapieco (2016)
WIDTHS: 2,4,6
| Chiều | Định nghĩa | Ví dụ lỗi trong dữ liệu nguồn của đề tài |
| Đầy đủ (completeness) | Dữ liệu cần có thì phải có | Quên quẹt thẻ khi ra ca; ô kiểm kê bỏ trống; đơn sàn không được nhập vào POS |
| Hợp lệ (validity) | Giá trị đúng kiểu, định dạng, miền giá trị | Số lượng nhập kho gõ theo gam vào cột kilôgam; số lượng dính đơn vị như “53.6kg” |
| Duy nhất (uniqueness) | Một thực thể chỉ được ghi một lần | Máy chấm công ghi trùng lượt quẹt |
| Nhất quán (consistency) | Cùng thông tin thống nhất giữa các nguồn | Một chi nhánh có sáu cách gọi trên sáu hệ thống; tên nguyên liệu có dấu và không dấu |
| Kịp thời (timeliness) | Dữ liệu sẵn sàng đúng lúc cần | Báo cáo đối soát sàn chỉ có sau khi kết thúc tuần |
| Chính xác (accuracy) | Phản ánh đúng thực tế | Sai số đếm tay khi kiểm kê |

### 2.4.2. Kiểm thử dữ liệu, cách ly và phả hệ

Kiểm thử dữ liệu (data testing) là các khẳng định tự động chạy sau mỗi lần biến đổi: khóa không trùng, khóa ngoại tồn tại, giá trị thuộc miền cho phép, tổng tiền không đổi qua các tầng. Các hệ thống kiểm định dữ liệu trong công nghiệp như Deequ (Schelter et al., 2018) và kiểm định dữ liệu trong TFX của Google (Breck et al., 2019) đều khai báo ràng buộc và kiểm tra tự động mỗi lô dữ liệu mới, vì sự phụ thuộc vào dữ liệu là nguồn nợ kỹ thuật khó nhận ra (Sculley et al., 2015). Dòng vi phạm có thể được *cách ly* (quarantine) sang bảng riêng kèm lý do, để các dòng hợp lệ tiếp tục được xử lý mà dòng lỗi không bị bỏ qua im lặng. Cần phân biệt lỗi kỹ thuật, như lượt quẹt thẻ bị ghi trùng, với tín hiệu nghiệp vụ, như hóa đơn bị hủy hay quên quẹt ra: loại sau là bằng chứng cho tầng phân tích nên phải được giữ lại và gắn cờ. Để truy một con số về dữ liệu gốc, mỗi bản ghi cần mang thông tin nguồn gốc, gọi là phả hệ dữ liệu (data provenance) (Simmhan et al., 2005).

### 2.4.3. Giải quyết định danh thực thể

Giải quyết định danh thực thể (entity resolution) xác định các bản ghi ở những nguồn khác nhau cùng chỉ một thực thể (Christen, 2012). Fellegi và Sunter (1969) mô hình hóa việc ghép cặp như một bài toán quyết định dựa trên độ tương đồng của các trường; Elmagarmid et al. (2007) tổng hợp các thước đo tương đồng chuỗi, trong đó độ đo Jaro (Jaro, 1989) và biến thể Jaro–Winkler ưu tiên chuỗi trùng phần đầu (Winkler, 1990), phù hợp với tên viết tắt. Thực tiễn thường kết hợp bảng ánh xạ do người hiểu nghiệp vụ lập cho thực thể ít và ổn định, quy tắc chuẩn hóa xác định như bỏ dấu, và khớp mờ có ngưỡng cho trường nhập tự do.

## 2.5. Phát hiện bất thường và truy vết nguyên nhân

### 2.5.1. Phân loại bất thường và phương pháp thống kê vững

Chandola et al. (2009) phân bất thường thành bất thường điểm, bất thường theo ngữ cảnh, khi giá trị chỉ bất thường trong một ngữ cảnh nhất định, và bất thường tập thể, khi một chuỗi giá trị cùng nhau tạo thành mẫu bất thường; Hodge và Austin (2004) phân biệt phương pháp có giám sát và không giám sát tùy việc có dữ liệu gán nhãn hay không. Phần lớn sự cố vận hành F&B thuộc hai loại sau: hao hụt tăng 20% trong mười ngày chỉ lộ ra khi xét trong ngữ cảnh của chi nhánh đó. *Điểm chuẩn* (z-score) đo khoảng cách của một giá trị so với trung bình của tập tham chiếu:

EQ: z = \frac{x - \mu}{\sigma} || (2.7)

NOINDENT: trong đó $\mu$ và $\sigma$ là trung bình và độ lệch chuẩn của tập tham chiếu. Ngưỡng ba độ lệch chuẩn là giới hạn quen thuộc của biểu đồ kiểm soát (Montgomery, 2019), nhưng trung bình và độ lệch chuẩn bị chính các giá trị bất thường kéo lệch. *Điểm chuẩn hiệu chỉnh* dùng trung vị và độ lệch tuyệt đối trung vị (MAD) nên vững hơn trước ngoại lai (Leys et al., 2013; Rousseeuw & Croux, 1993); Iglewicz và Hoaglin (1993) đề xuất coi giá trị có $|M| > 3{,}5$ là ngoại lai:

EQ: M = \frac{0{,}6745\,(x - \tilde{x})}{\mathrm{MAD}}, \qquad \mathrm{MAD} = \mathrm{med}\left(|x_{i} - \tilde{x}|\right) || (2.8)

NOINDENT: trong đó $\tilde{x}$ là trung vị của tập tham chiếu và med là phép lấy trung vị. Để đưa ngữ cảnh vào phép so sánh, *đường cơ sở theo nhóm đồng nhất* so một chi nhánh với lịch sử của chính nó hoặc với các chi nhánh cùng hạng, khiến các yếu tố tác động lên toàn chuỗi như ngày lễ tự triệt tiêu; tách thành phần mùa vụ trước khi xét phần dư là cách làm chuẩn trong phân tích chuỗi thời gian (Hyndman & Athanasopoulos, 2021). Với dịch chuyển nhỏ nhưng kéo dài, biểu đồ tổng tích lũy CUSUM (Page, 1954) nhạy hơn việc xét từng điểm.

### 2.5.2. Luật nghiệp vụ và kiểm định trên số đếm

Với các quy định đã biết trước như tỷ lệ hoa hồng trong hợp đồng, luật so sánh trực tiếp với giá trị cam kết đúng đắn hơn thống kê dựa trên lịch sử: nếu sàn tính sai liên tục, trung bình lịch sử cũng sai theo và z-score không bao giờ phát hiện được. Với tỷ lệ trên số lần thử nhỏ, như tỷ lệ hủy hóa đơn của một thu ngân trong một tuần, *kiểm định nhị thức* đánh giá khả năng quan sát được số lần hủy đó nếu thu ngân có cùng tỷ lệ với đồng nghiệp; khi tỷ lệ nhỏ, phân phối nhị thức được xấp xỉ bằng phân phối Poisson (Agresti, 2013). Khi kiểm định đồng thời nhiều đối tượng, hiệu chỉnh Bonferroni chia mức ý nghĩa cho số phép kiểm định để giữ xác suất dương tính giả chung dưới mức mong muốn (Dunn, 1961).

### 2.5.3. Phân rã chỉ số và cây KPI

Để truy vết một biến động, chỉ số tổng được phân rã theo *cây KPI* (driver tree), trong đó mỗi nút cha là hàm của các nút con. Với doanh thu $R$ của một chi nhánh, gọi $N_{k}$ là số đơn và $\mathrm{AOV}_{k}$ là giá trị trung bình mỗi đơn của kênh $k$; khi doanh thu thay đổi giữa kỳ gốc (chỉ số 0) và kỳ quan sát (chỉ số 1), phần thay đổi được phân bổ cho từng kênh, từng thành phần lượng và giá:

EQ: R = \sum_{k} N_{k} \cdot \mathrm{AOV}_{k} || (2.9)

EQ: \Delta R = \sum_{k} \left( \Delta N_{k} \cdot \mathrm{AOV}_{k,0} + N_{k,1} \cdot \Delta \mathrm{AOV}_{k} \right) || (2.10)

Phân rã chỉ ra biến động nằm ở nhánh nào; các tín hiệu đi kèm ở nhánh đó, như thời gian chuẩn bị tăng hay giờ công ca tối giảm, thu hẹp về một nguyên nhân vận hành. Bài toán định vị nguyên nhân trên chỉ số cộng dồn nhiều chiều đã được nghiên cứu trong vận hành hệ thống trực tuyến, như Adtributor (Bhagwan et al., 2014), iDice (Lin et al., 2016) và HotSpot (Sun et al., 2018); khóa luận dùng cùng ý tưởng phân rã nhưng kết hợp với tín hiệu từ các nguồn vận hành khác để gán nguyên nhân.

### 2.5.4. Đánh giá bộ phát hiện

Khi có đáp án, chất lượng bộ phát hiện được đo bằng ma trận nhầm lẫn: dương tính đúng (TP) là cảnh báo trùng sự cố thật, dương tính sai (FP) là cảnh báo không ứng với sự cố nào, âm tính sai (FN) là sự cố không được cảnh báo:

EQ: \mathrm{Precision} = \frac{\mathrm{TP}}{\mathrm{TP} + \mathrm{FP}}, \qquad \mathrm{Recall} = \frac{\mathrm{TP}}{\mathrm{TP} + \mathrm{FN}} || (2.11)

EQ: F_{1} = \frac{2 \cdot \mathrm{Precision} \cdot \mathrm{Recall}}{\mathrm{Precision} + \mathrm{Recall}} || (2.12)

Precision quyết định niềm tin của người dùng vào cảnh báo, recall cho biết bao nhiêu sự cố được phát hiện. Với sự cố kéo dài, đánh giá theo *mức sự kiện*, tức một sự cố được tính là phát hiện nếu có ít nhất một cảnh báo đúng trong khoảng thời gian của nó, kèm độ trễ phát hiện, phù hợp với cách quản lý sử dụng hơn; Tatbul et al. (2018) mở rộng precision và recall cho bất thường dạng khoảng thời gian. Khi rất ít tuần có sự cố, precision và recall phản ánh chất lượng tốt hơn độ chính xác tổng thể (Saito & Rehmsmeier, 2015). Điều kiện để kết quả có giá trị là tập đánh giá phải độc lập với tập dùng để chọn tham số, vì chọn và đánh giá trên cùng một tập cho ước lượng lạc quan (Cawley & Talbot, 2010), còn để thông tin của đáp án lọt vào bước xây dựng mô hình là lỗi rò rỉ dữ liệu (Kaufman et al., 2012).

## 2.6. Dữ liệu mô phỏng trong nghiên cứu

Dữ liệu mô phỏng (synthetic data) được dùng khi dữ liệu thật nhạy cảm, khó tiếp cận, hoặc khi cần đáp án biết trước để đánh giá phương pháp. Dữ liệu tổng hợp mô phỏng đúng quan hệ giữa các bảng có thể thay dữ liệu thật trong nhiều tác vụ phát triển và kiểm thử (Patki et al., 2016), nhưng giá trị của nó phụ thuộc vào việc giữ được những tính chất nào của dữ liệu thật (Jordon et al., 2022). PaySim mô phỏng giao dịch ví điện tử từ một mẫu dữ liệu thật để tạo bộ dữ liệu có nhãn gian lận (Lopez-Rojas et al., 2016); các bộ dữ liệu đánh giá phát hiện bất thường cũng thường được dựng có kiểm soát với bất thường biết trước (Emmott et al., 2013; Laptev et al., 2015). Rủi ro chính là dữ liệu quá "sạch" khiến phương pháp trông tốt hơn thực chất. Khóa luận giảm rủi ro này bằng bốn nguyên tắc: mô phỏng đúng các quy luật vận hành đã biết, chẳng hạn thời gian chờ tăng phi tuyến theo $1/(1-\rho)$ khi mức tải $\rho$ tiến gần năng lực (Kleinrock, 1975); sinh mọi nguồn từ cùng một tập sự kiện; đưa vào lỗi dữ liệu đặc trưng của từng hệ thống; và ước lượng phân phối đầu vào từ dữ liệu quan sát thật khi có thể, tức bước mô hình hóa dữ liệu đầu vào (input modeling) của phương pháp mô phỏng (Law, 2015).

## 2.7. Công nghệ sử dụng

Công nghệ được chọn theo nguyên tắc tương xứng với quy mô. Dữ liệu của bài toán ở mức hàng trăm megabyte mỗi năm, nằm trong khả năng của một máy tính cá nhân, nên đề tài không dùng nền tảng phân tán như Spark hay Hadoop. DuckDB là hệ quản trị phân tích dạng nhúng, lưu theo cột và thực thi theo vector (Raasveldt & Mühleisen, 2019); dbt viết các bước biến đổi bằng SQL có quản lý phiên bản, tự dựng đồ thị phụ thuộc và có sẵn kiểm thử dữ liệu (dbt Labs, n.d.); Apache Airflow điều phối các bước thành đồ thị có hướng không chu trình (DAG), chạy theo lịch hoặc khi một tập dữ liệu vừa cập nhật (Apache Software Foundation, n.d.). PostgreSQL đóng vai kho phục vụ cho nhiều người đọc đồng thời (PostgreSQL Global Development Group, n.d.), vì tách máy tính toán khỏi nơi phục vụ người đọc là cách làm phổ biến (Reis & Housley, 2022). Docker đóng gói mỗi thành phần vào container (Merkel, 2014) và Docker Compose dựng lại cả nền tảng bằng một lệnh (Docker Inc., n.d.). FastAPI được dùng để dựng API giả lập phía nguồn (FastAPI, n.d.); Python cùng pandas (McKinney, 2010), NumPy (Harris et al., 2020) và scikit-learn (Pedregosa et al., 2011) dùng cho bộ mô phỏng, bước nạp và các bộ phát hiện; Metabase phục vụ báo cáo kinh doanh (Metabase, n.d.) và Streamlit cho các trang phân tích có logic riêng (Streamlit, n.d.). Bảng 2.3 tóm tắt lý do chọn từng công nghệ.

TABLE: Bảng 2.3. Lựa chọn công nghệ và lý do || Đề xuất của nghiên cứu
WIDTHS: 3,3,6
| Nhu cầu | Công nghệ chọn | Lý do và phương án không chọn |
| Tính toán và lưu trữ của đường ống | DuckDB | Dữ liệu cỡ trăm MB, một máy; truy vấn phân tích theo cột nhanh, không cần máy chủ; không cần cụm Spark |
| Biến đổi dữ liệu Silver, Gold | dbt (dbt-duckdb) | SQL có kiểm thử, tài liệu và lineage; thay cho các script Python rời rạc khó kiểm thử |
| Thu thập qua API | Bộ kết nối Python dùng thư viện chuẩn | Chỉ có hai nguồn API, cần kiểm soát mốc và đối chiếu theo nghiệp vụ; công cụ dựng sẵn như Airbyte cần thêm một hệ thống chạy riêng |
| Kho phục vụ cho người đọc | PostgreSQL | Tệp DuckDB chỉ cho một tiến trình ghi và không có tài khoản người dùng; PostgreSQL cho nhiều kết nối đọc đồng thời và tài khoản chỉ đọc |
| Báo cáo kinh doanh | Metabase | Mã nguồn mở, chạy trong Docker, dựng dashboard bằng API nên tái lập được; Power BI cần tài khoản trả phí để chia sẻ, nhúng |
| Điều phối | Airflow, Docker Compose | Chạy theo lịch và theo dữ liệu mới, theo dõi lỗi; không cần Kafka vì nhịp nghiệp vụ là theo ngày |
| Ứng dụng phân tích | Streamlit | Xây dựng nhanh bằng Python cho các trang cảnh báo, truy vết, vận hành dữ liệu |

## 2.8. Các nghiên cứu liên quan

Các nghiên cứu liên quan thuộc bốn nhóm. Nhóm thứ nhất nghiên cứu dữ liệu và phân tích trong ngành nhà hàng, khách sạn: tổng quan của Mariani et al. (2018) cho thấy lĩnh vực này tăng nhanh nhưng còn rời rạc về phạm vi và hạn chế về phương pháp; Thompson (1998), Kimes (1999) và Feldman et al. (2023) cung cấp khái niệm về công suất, phân ca và hợp đồng với sàn nhưng không xây dựng hệ thống tích hợp dữ liệu. Nhóm thứ hai nghiên cứu sai lệch tồn kho bằng dữ liệu bán lẻ (DeHoratius & Raman, 2008) và bằng mô hình giải tích, mô phỏng (Kang & Gershwin, 2005), chưa gắn với tiêu hao theo công thức món. Nhóm thứ ba phát hiện bất thường và gian lận trên hóa đơn bán hàng bằng học không giám sát (Malashin et al., 2024) hoặc có giám sát (Begen et al., 2023), đều làm việc trên một nguồn dữ liệu và cần trường hợp bất thường đã biết. Nhóm thứ tư định vị nguyên nhân trên chỉ số nhiều chiều (Bhagwan et al., 2014; Sun et al., 2018), nhưng chỉ trên một chỉ số và các thuộc tính của chính nó. Bảng 2.4 tóm tắt các nghiên cứu tiêu biểu.

TABLE: Bảng 2.4. Tổng hợp các nghiên cứu liên quan || Tổng hợp từ các nghiên cứu được trích dẫn
WIDTHS: 2.6,2.8,3.4,3.4,3.8
| Nghiên cứu | Lĩnh vực, dữ liệu | Phương pháp | Kết quả chính | Khác biệt so với khóa luận |
| Mariani et al. (2018) | Nhà hàng, khách sạn, du lịch; các công bố đến năm 2016 | Tổng quan tài liệu có hệ thống | Nghiên cứu tăng nhanh nhưng rời rạc về phạm vi, hạn chế về phương pháp | Khóa luận xây dựng hệ thống trên dữ liệu vận hành đa nguồn |
| DeHoratius và Raman (2008) | Bán lẻ; gần 370.000 bản ghi tồn kho của 37 cửa hàng | Mô hình tuyến tính phân cấp | Khoảng 65% bản ghi tồn kho sai lệch; kiểm kê giúp giảm sai lệch | Khóa luận đối chiếu kiểm kê với tiêu hao theo công thức món |
| Kang và Gershwin (2005) | Hệ thống tồn kho; mô hình và mô phỏng | Mô hình giải tích, mô phỏng | Thất thoát nhỏ tích lũy gây thiếu hàng nghiêm trọng | Khóa luận phát hiện thất thoát từ dữ liệu thay vì mô hình hóa tác động |
| Feldman et al. (2023) | Nhà hàng và sàn giao đồ ăn | Mô hình toán về hợp đồng | Hợp đồng hoa hồng theo tỷ lệ không điều phối được lợi ích hai bên | Khóa luận kiểm tra việc tuân thủ hợp đồng từ báo cáo đối soát |
| Malashin et al. (2024) | Khoảng 2,7 triệu hóa đơn nhà hàng | Isolation Forest, bộ mã hóa tự động, giải thuật di truyền | Phát hiện được 25 trên 100 trường hợp bất thường đã biết ở tập kiểm tra | Một nguồn dữ liệu; mục tiêu là tuân thủ thuế, không truy nguyên nhân vận hành |
| Begen et al. (2023) | Nhật ký POS chuỗi đồ ăn nhanh | Random Forest, XGBoost, LightGBM, cân bằng mẫu | Kết quả khả quan ở giai đoạn đầu | Cần nhãn gian lận; khóa luận dùng kiểm định thống kê không cần nhãn |
| Bhagwan et al. (2014); Sun et al. (2018) | Doanh thu quảng cáo; chỉ số vận hành hệ thống trực tuyến | Phân rã chỉ số nhiều chiều, tìm tổ hợp gây bất thường | Định vị nhanh chiều và giá trị gây biến động | Chỉ trên một chỉ số; khóa luận kết hợp tín hiệu từ nhiều hệ thống nguồn |
| Lopez-Rojas et al. (2016) | Giao dịch ví điện tử | Mô phỏng dựa trên tác tử từ mẫu dữ liệu thật | Bộ dữ liệu có nhãn gian lận cho nghiên cứu | Khóa luận mô phỏng nhiều hệ thống nguồn nhất quán nhân quả |

## 2.9. Khoảng trống nghiên cứu và tiểu kết chương

Các nghiên cứu hiện có hoặc dừng ở khái niệm và mô hình, hoặc phân tích một nguồn dữ liệu cho một loại sự cố. Khoảng trống mà khóa luận hướng tới là kết hợp ba yếu tố thường bị tách rời: tích hợp đầy đủ các nguồn vận hành không đồng nhất của một chuỗi F&B, kể cả sổ kho và phiếu kiểm kê ghi tay; một kho dữ liệu có kiểm chứng chất lượng làm nền cho phân tích; và đánh giá định lượng khả năng phát hiện, truy vết nhiều loại sự cố trên một tập kịch bản độc lập có đáp án. Về nghiệp vụ, chương này xác định các chỉ số COGS%, AvT, Labor%, tỷ lệ hoa hồng hiệu dụng và tỷ lệ hủy theo thu ngân làm dấu vết của các vấn đề P1–P5; về kỹ thuật, kiến trúc Medallion, mô hình hóa chiều, kiểm thử dữ liệu, thống kê vững và cây KPI là công cụ để biến dữ liệu rời rạc thành bằng chứng kiểm chứng được. Chương 3 vận dụng các cơ sở này để thiết kế hệ thống.
