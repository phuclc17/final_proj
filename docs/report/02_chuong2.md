# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÁC NGHIÊN CỨU LIÊN QUAN

Chương này trình bày các kiến thức nền tảng cho khóa luận theo hai mạch. Mạch nghiệp vụ (mục 2.1) giải thích các khái niệm và chỉ số quản trị vận hành của chuỗi F&B, là cơ sở để xác định dữ liệu nào cần thu thập và vấn đề nào cần phát hiện. Mạch kỹ thuật (mục 2.2 đến 2.7) trình bày lý thuyết về kiến trúc dữ liệu, mô hình hóa chiều, chất lượng dữ liệu, phát hiện bất thường, dữ liệu mô phỏng và các công nghệ được lựa chọn. Mục 2.8 điểm qua các nghiên cứu và giải pháp liên quan; mục 2.9 chỉ ra khoảng trống mà đề tài hướng đến và tóm tắt chương.

## 2.1. Nghiệp vụ vận hành chuỗi đồ ăn nhanh và các chỉ số then chốt

### 2.1.1. Mô hình bán hàng đa kênh và đối soát với sàn giao đồ ăn

Một chuỗi đồ ăn nhanh hiện đại thường bán qua bốn kênh: bán tại quầy, nơi khách đến cửa hàng và thanh toán qua POS; ứng dụng đặt hàng riêng của chuỗi; và các sàn giao đồ ăn như GrabFood, ShopeeFood. Với kênh sàn, khách đặt món trên ứng dụng của sàn, cửa hàng chuẩn bị món, tài xế của sàn nhận và giao. Tiền khách trả đi qua sàn; định kỳ, thường là mỗi tuần, sàn gửi cho cửa hàng một báo cáo đối soát (settlement report) gồm doanh thu món, số đơn hoàn thành, số đơn hủy, phí hoa hồng, chi phí khuyến mãi mà cửa hàng tài trợ, phí quảng cáo, các khoản điều chỉnh và số tiền thực nhận.

Quy trình đối soát có hai rủi ro chính. Thứ nhất, phí hoa hồng thực tế có thể lệch so với tỷ lệ trong hợp đồng, do thay đổi chính sách, áp dụng sai gói dịch vụ hoặc sai sót hệ thống. Vì báo cáo thường chỉ ghi số tiền hoa hồng mà không ghi tỷ lệ, sai lệch chỉ lộ ra khi tính lại tỷ lệ hiệu dụng, tức số tiền hoa hồng chia cho doanh thu món, rồi so với hợp đồng. Thứ hai, ở nhiều cửa hàng, nhân viên phải nhập tay đơn sàn vào POS để quản lý bếp và kho. Nếu đơn không được nhập vào POS, doanh thu nội bộ bị thiếu so với báo cáo của sàn, trong khi nguyên liệu vẫn bị tiêu hao. Việc phát hiện đòi hỏi đối chiếu số đơn và doanh thu giữa POS và báo cáo đối soát.

### 2.1.2. Giá vốn hàng bán và chênh lệch giá vốn thực tế – lý thuyết

Giá vốn hàng bán (Cost of Goods Sold – COGS) trong F&B là giá trị nguyên liệu đã tiêu hao để tạo ra doanh thu. Chỉ số quản trị phổ biến nhất là tỷ lệ giá vốn trên doanh thu:

EQ: COGS% = Giá vốn hàng bán / Doanh thu thuần × 100% || (2.1)

Doanh thu cao chưa chắc đã có lãi. Nếu COGS% tăng cùng doanh thu, chuỗi có thể đang bán nhiều hơn nhưng thất thoát nhiều hơn. Để biết giá vốn tăng vì sao, các tài liệu về kiểm soát chi phí F&B (Dopson & Hayes, 2019) phân biệt hai loại giá vốn. *Giá vốn lý thuyết* là giá vốn lẽ ra phải có nếu mọi món được chế biến đúng định mức công thức:

EQ: Giá vốn lý thuyết = Σ món [ số lượng bán × Σ nguyên liệu (định mức × đơn giá) ] || (2.2)

*Giá vốn thực tế* được tính từ biến động kho trong một kỳ kiểm kê:

EQ: Giá vốn thực tế = Tồn đầu kỳ + Nhập trong kỳ − Tồn cuối kỳ (quy ra giá trị) || (2.3)

Chênh lệch giữa hai đại lượng, gọi là chênh lệch giá vốn thực tế – lý thuyết (Actual versus Theoretical – AvT), đo phần nguyên liệu tiêu hao không tạo ra doanh thu: hư hỏng do bảo quản hoặc không xuất kho theo nguyên tắc nhập trước – xuất trước (FIFO), chế biến sai định lượng, món làm lại, hoặc thất thoát. Một mức chênh lệch nhỏ là bình thường; chênh lệch tăng đột biến ở một chi nhánh là tín hiệu cần điều tra. Việc tính AvT đòi hỏi tích hợp ít nhất ba nguồn: dữ liệu bán hàng từ mọi kênh, công thức món và dữ liệu kho.

TODO: tìm nguồn cho ngưỡng COGS% 28–35%; không có nguồn thì ghi là ngưỡng doanh nghiệp tự đặt.

### 2.1.3. Chi phí và hiệu suất nhân công

Nhân công là khoản chi phí lớn thứ hai sau giá vốn. Hai nhóm chỉ số thường dùng là tỷ lệ chi phí nhân công trên doanh thu và năng suất lao động theo giờ:

EQ: Labor% = Chi phí nhân công / Doanh thu thuần × 100% || (2.4)

EQ: SPLH = Doanh thu / Tổng giờ công;    OPLH = Số đơn / Tổng giờ công || (2.5)

Trong đó SPLH (Sales per Labor Hour) là doanh thu trên mỗi giờ công và OPLH (Orders per Labor Hour) là số đơn trên mỗi giờ công. Các chỉ số này cần được xem theo khung giờ chứ không chỉ theo ngày. Một chi nhánh có thể đủ người tính theo cả ngày nhưng lại thừa người ca sáng và thiếu người ca tối. Khi thiếu người, OPLH tăng nhưng thời gian chuẩn bị món cũng kéo dài, khách tại quầy bỏ về, cửa hàng phải hủy đơn trực tuyến và điểm đánh giá của cửa hàng trên sàn giảm. Vì thuật toán xếp hạng của sàn ưu tiên cửa hàng có điểm cao và ít hủy đơn, thiệt hại doanh thu có thể kéo dài nhiều tuần sau khi tình trạng thiếu người đã kết thúc. Ngược lại, thừa người làm Labor% tăng mà không mang lại doanh thu tương ứng.

TODO: tìm nguồn cho ngưỡng Labor% 20–25%.

### 2.1.4. Quản lý tồn kho, kiểm kê và thất thoát

Quản lý kho trong F&B có hai tầng kiểm soát bổ trợ nhau. Tầng thứ nhất là kiểm soát hằng ngày: theo dõi lượng nhập, áp dụng FIFO, duy trì định mức tồn tối thiểu (par level) và điểm đặt hàng lại cho từng nguyên liệu, nhằm phát hiện sớm hao hụt bất thường. Tầng thứ hai là kiểm kê định kỳ: đếm thực tế tồn kho và so với tồn sổ sách. Tồn sổ sách được tính từ lần kiểm kê trước, cộng lượng nhập và trừ lượng tiêu hao lý thuyết theo bán hàng. Chênh lệch âm vượt mức sai số đếm tay và hao hụt tự nhiên là dấu hiệu thất thoát (inventory shrinkage):

EQ: Tỷ lệ chênh lệch kiểm kê = (Tồn kiểm kê − Tồn sổ sách) / Tồn sổ sách || (2.6)

Kiểm kê chỉ cho biết đã mất bao nhiêu sau khi sự việc xảy ra, trong khi kiểm soát hằng ngày mới giúp giữ được tiền. Khóa luận phân biệt hai loại vấn đề kho: P2 là hao hụt vượt định mức của hàng tươi giá thấp, thường do bảo quản, xuất kho và chế biến; P4 là thất thoát nguyên liệu giá trị cao, nơi động cơ lấy cắp lớn nhất. Vì dữ liệu kho trong đề tài chỉ có tồn thực tế tại các lần kiểm kê, cả hai được đánh giá theo từng kỳ kiểm kê (mục 3.7.3).

### 2.1.5. Gian lận tại quầy thu ngân

Hệ thống POS cho phép hủy hóa đơn (void) và hoàn tiền (refund) để xử lý các tình huống hợp lệ như khách đổi ý hoặc nhập sai món. Chính các chức năng này có thể bị lạm dụng: thu ngân nhận tiền mặt của khách, giao món, sau đó hủy hóa đơn và giữ lại tiền. Do hóa đơn bị hủy, doanh thu trên hệ thống giảm nhưng không có khoản tiền mặt nào bị thiếu khi đối chiếu két. Dấu hiệu của hành vi này nằm ở mẫu hình: hóa đơn tiền mặt bị hủy sau khi đã in, thời điểm hủy cách thời điểm thanh toán vài phút, và người hủy chính là thu ngân tạo hóa đơn thay vì quản lý ca. Đặc biệt, tỷ lệ hủy của một thu ngân cao bất thường so với đồng nghiệp cùng chi nhánh. Thực tiễn quản lý nhà hàng thường giải quyết vấn đề này bằng báo cáo ngoại lệ (exception report) theo từng nhân viên. Về mặt dữ liệu, phát hiện cần liên kết hóa đơn POS với danh sách nhân viên, trong khi mã nhân viên trên POS thường khác mã trên hệ thống chấm công và hồ sơ nhân sự.

### 2.1.6. Nguyên tắc phân tích dữ liệu vận hành F&B

Từ đặc thù trên, khóa luận áp dụng một số nguyên tắc phân tích xuyên suốt:

- Không kết luận từ tổng doanh thu; mọi chỉ số được tách theo thời gian, ca, chi nhánh, kênh và món.
- Luôn đặt doanh thu cạnh chi phí: doanh thu tăng đi kèm COGS% hoặc Labor% tăng là một cảnh báo chứ không phải tin tốt.
- So sánh trong nhóm đồng nhất. Chi nhánh lớn và chi nhánh nhỏ khác nhau về quy mô và cơ cấu kênh, nên một giá trị chỉ được coi là bất thường khi so với lịch sử của chính chi nhánh, hoặc với các chi nhánh cùng hạng, cùng ngày trong tuần.
- Phân biệt biến động bình thường với biến động do sự cố. Ngày trong tuần, ngày lễ, thời tiết và điều chỉnh giá tác động lên nhiều chi nhánh cùng lúc, còn sự cố vận hành thường chỉ xảy ra ở một chi nhánh, một kênh hoặc một nhân viên.
- Quy mọi phát hiện ra tác động kinh doanh bằng tiền, đơn hàng hoặc khách hàng, kèm hành động đề xuất, không dừng ở mức “có bất thường”.

TABLE: Bảng 2.1. Các chỉ số vận hành then chốt được sử dụng trong khóa luận
WIDTHS: 3,5,5
| Chỉ số | Định nghĩa | Ý nghĩa quản trị |
| Doanh thu, số đơn, AOV | Doanh thu thuần, số đơn hoàn thành và giá trị trung bình mỗi đơn, theo kênh | Phân rã doanh thu thành lượng (số đơn) và giá (AOV) |
| COGS%, chênh lệch AvT | Công thức (2.1)–(2.3) | Phát hiện hao hụt, thất thoát nguyên liệu |
| Labor%, SPLH, OPLH | Công thức (2.4)–(2.5), theo ca | Phát hiện thừa hoặc thiếu nhân sự |
| Thời gian chuẩn bị | Từ lúc nhận đơn đến lúc món sẵn sàng | Chất lượng dịch vụ, áp lực tải bếp |
| Tỷ lệ hủy đơn | Đơn bị hủy chia tổng đơn, tách hủy do cửa hàng và do khách | Mất doanh thu trực tiếp, ảnh hưởng thứ hạng trên sàn |
| Tỷ lệ hoa hồng hiệu dụng | Tiền hoa hồng chia doanh thu món, theo sàn và tuần | Đối chiếu với hợp đồng |
| Tỷ lệ chênh lệch kiểm kê | Công thức (2.6) | Thất thoát tồn kho |
| Tỷ lệ hủy hóa đơn theo thu ngân | Hóa đơn bị hủy chia số hóa đơn đã tạo, theo nhân viên | Phát hiện gian lận tại quầy |

## 2.2. Kiến trúc dữ liệu cho phân tích

### 2.2.1. Kho dữ liệu, hồ dữ liệu và lakehouse

*Kho dữ liệu* (data warehouse) là tập hợp dữ liệu hướng chủ đề, tích hợp, ổn định và có tính lịch sử, phục vụ cho việc ra quyết định (Inmon, 2005). Khác với cơ sở dữ liệu tác nghiệp được tối ưu cho ghi nhận giao dịch, kho dữ liệu được tối ưu cho truy vấn phân tích trên khối lượng lớn dữ liệu lịch sử. Hai trường phái thiết kế kinh điển là cách tiếp cận từ trên xuống của Inmon, với kho dữ liệu doanh nghiệp chuẩn hóa làm trung tâm, và cách tiếp cận từ dưới lên của Kimball, xây dựng các kho dữ liệu theo quy trình nghiệp vụ bằng mô hình chiều và kết nối với nhau qua các chiều dùng chung (Kimball & Ross, 2013).

*Hồ dữ liệu* (data lake) lưu dữ liệu ở dạng thô, nhiều định dạng, với chi phí thấp, chấp nhận việc áp đặt cấu trúc khi đọc thay vì khi ghi. Hồ dữ liệu linh hoạt nhưng dễ trở thành “đầm lầy dữ liệu” nếu không quản lý chất lượng và siêu dữ liệu. Kiến trúc lakehouse kết hợp hai cách tiếp cận: dữ liệu lưu ở định dạng mở như hồ dữ liệu, nhưng có các tính năng quản trị, giao dịch và hiệu năng truy vấn của kho dữ liệu (Armbrust và cộng sự, 2021).

### 2.2.2. ETL và ELT

Quy trình đưa dữ liệu từ nguồn vào kho truyền thống là ETL (Extract – Transform – Load): trích xuất, biến đổi trên một máy chủ trung gian, rồi nạp dữ liệu đã sạch vào kho (Kimball & Caserta, 2004). Khi năng lực xử lý của các hệ quản trị phân tích tăng lên, cách tiếp cận ELT (Extract – Load – Transform) trở nên phổ biến: dữ liệu thô được nạp nguyên trạng vào nền tảng phân tích trước, sau đó được biến đổi ngay trong nền tảng bằng SQL. ELT giữ lại bản thô để có thể xử lý lại khi quy tắc làm sạch thay đổi và tách bạch rõ bước nạp với bước biến đổi (Reis & Housley, 2022). Khóa luận áp dụng ELT.

### 2.2.3. Kiến trúc Medallion

Kiến trúc Medallion tổ chức dữ liệu thành ba tầng có chất lượng tăng dần (Databricks, n.d.):

- Tầng Bronze, hay tầng thô, chứa dữ liệu được nạp nguyên trạng từ nguồn, chỉ bổ sung siêu dữ liệu như tệp nguồn, thời điểm nạp, mã lô nạp. Tầng này là bản lưu trữ trung thực, cho phép xử lý lại toàn bộ khi cần.
- Tầng Silver, hay tầng làm sạch và chuẩn hóa, chứa dữ liệu đã được ép kiểu, chuẩn hóa định dạng và đơn vị, loại trùng, giải quyết định danh giữa các hệ thống; các dòng lỗi được tách ra bảng riêng.
- Tầng Gold, hay tầng nghiệp vụ, tổ chức dữ liệu theo mô hình phục vụ phân tích, như các bảng sự kiện và bảng chiều của lược đồ hình sao, cùng các bảng tổng hợp chỉ số.

Ưu điểm của cách tổ chức này là mỗi tầng có một trách nhiệm rõ ràng, có thể kiểm thử độc lập, và lỗi ở tầng sau không làm mất dữ liệu gốc ở tầng trước.

### 2.2.4. Nạp dữ liệu tăng dần và tính lũy đẳng

Trong vận hành thực tế, dữ liệu nguồn đến liên tục theo ngày. Nạp lại toàn bộ dữ liệu mỗi ngày là lãng phí và không mở rộng được; vì vậy đường ống cần *nạp tăng dần* (incremental load), chỉ xử lý dữ liệu mới. Đi kèm là yêu cầu *lũy đẳng* (idempotency): chạy lại cùng một lần nạp nhiều lần phải cho cùng kết quả, không sinh dữ liệu trùng. Cách phổ biến để đạt được cả hai là duy trì nhật ký nạp ghi lại từng tệp đã xử lý cùng mã băm nội dung, và thực hiện mỗi lần nạp trong một giao dịch để lỗi giữa chừng không để lại dữ liệu dở dang (Reis & Housley, 2022).

### 2.2.5. Thu thập dữ liệu từ hệ thống nguồn

Trước khi được nạp, dữ liệu phải đi từ hệ thống nguồn tới nơi đường ống đọc được. Có hai kiểu chính. Ở kiểu đẩy, hệ thống nguồn tự gửi dữ liệu đi, thường là tệp xuất theo lịch hoặc tệp do người lập gửi. Ở kiểu kéo, đường ống chủ động lấy dữ liệu, thường qua API của phần mềm nguồn (Reis & Housley, 2022). Một doanh nghiệp thường dùng cả hai, tùy khả năng của từng hệ thống: phần mềm bán theo thuê bao trên đám mây thường mở API, phần mềm cài tại máy chỉ xuất tệp, còn báo cáo của đối tác và sổ sách nội bộ do con người gửi.

Kéo dữ liệu qua API có những vấn đề riêng. Để chỉ lấy phần mới, bên kéo lưu một mốc (watermark), thường là thời điểm hoặc ngày của bản ghi cuối cùng đã lấy, và mỗi lần chỉ lấy từ mốc trở đi. Dữ liệu có thể đến trễ, nên mỗi lần thường lấy lại một khoảng ngay trước mốc. API trả dữ liệu theo trang, giới hạn tần suất gọi và thỉnh thoảng lỗi tạm thời, nên bên kéo phải đi hết các trang, đối chiếu tổng số bản ghi, và thử lại với thời gian chờ tăng dần. Với dữ liệu đẩy, rủi ro nằm ở chỗ tệp sai cấu trúc, sai chỗ, gửi trùng hoặc gửi nhầm. Cách phòng ngừa là một hợp đồng dữ liệu: thỏa thuận giữa bên giữ nguồn và bên sử dụng về cấu trúc, ý nghĩa và nhịp cập nhật của dữ liệu, được kiểm tra tự động ngay khi dữ liệu đến, để dữ liệu vi phạm bị chặn ở cửa thay vì lan vào kho (Reis & Housley, 2022).

## 2.3. Mô hình hóa dữ liệu chiều

### 2.3.1. Bảng sự kiện, bảng chiều và hạt dữ liệu

Mô hình hóa chiều (dimensional modeling) tổ chức dữ liệu thành hai loại bảng (Kimball & Ross, 2013). *Bảng sự kiện* (fact table) lưu các đo lường của một quy trình nghiệp vụ, như số lượng, số tiền, thời lượng; mỗi dòng ứng với một sự kiện ở một mức chi tiết xác định. *Bảng chiều* (dimension table) lưu ngữ cảnh mô tả sự kiện: ai, cái gì, ở đâu, khi nào. Ví dụ chi nhánh, món ăn, nhân viên, ngày.

Khái niệm trung tâm là *hạt dữ liệu* (grain): mỗi dòng của bảng sự kiện đại diện cho điều gì. Kimball và Ross (2013) đề xuất quy trình thiết kế bốn bước: chọn quy trình nghiệp vụ, khai báo hạt dữ liệu, xác định các chiều và xác định các đo lường. Việc khai báo hạt ở mức chi tiết nhất có thể, ví dụ từng dòng món trong hóa đơn thay vì tổng theo ngày, giúp bảng sự kiện trả lời được nhiều câu hỏi chưa lường trước. Bảng sự kiện thường thuộc một trong ba loại: bảng giao dịch, mỗi dòng là một sự kiện; bảng ảnh chụp định kỳ, ghi trạng thái tại các thời điểm đều đặn như tồn kho tại kỳ kiểm kê; và bảng ảnh chụp tích lũy, theo dõi một quy trình qua nhiều mốc.

### 2.3.2. Lược đồ hình sao và ma trận bus

Trong *lược đồ hình sao* (star schema), mỗi bảng sự kiện nằm ở trung tâm và liên kết trực tiếp với các bảng chiều đã phi chuẩn hóa. So với lược đồ bông tuyết, nơi các bảng chiều được chuẩn hóa thành nhiều bảng, lược đồ hình sao dễ hiểu hơn với người dùng nghiệp vụ và cho hiệu năng truy vấn tốt hơn.

Khi kho dữ liệu có nhiều quy trình nghiệp vụ, như bán hàng, nhập kho, chấm công, các bảng sự kiện cần dùng chung những bảng chiều giống hệt nhau, gọi là *chiều đồng nhất* (conformed dimension), để có thể phân tích chéo. Công cụ thiết kế tương ứng là *ma trận bus* (bus matrix): mỗi dòng là một quy trình nghiệp vụ, mỗi cột là một chiều, ô được đánh dấu nếu quy trình dùng chiều đó (Kimball & Ross, 2013). Trong đề tài này, chiều chi nhánh và chiều ngày phải dùng chung cho mọi bảng sự kiện thì mới đặt được doanh thu cạnh chi phí nhân công và giá vốn của cùng chi nhánh, cùng ngày.

### 2.3.3. Chiều thay đổi chậm

Thuộc tính của chiều có thể thay đổi theo thời gian: món ăn được điều chỉnh giá, nhân viên được thăng chức và tăng lương. Kỹ thuật *chiều thay đổi chậm* (Slowly Changing Dimension – SCD) xác định cách lưu các thay đổi này (Kimball & Ross, 2013).

TABLE: Bảng 2.2. Các kiểu chiều thay đổi chậm phổ biến
WIDTHS: 2,5,5
| Kiểu | Cách xử lý | Hệ quả |
| Kiểu 0 | Giữ nguyên giá trị ban đầu | Không phản ánh thay đổi |
| Kiểu 1 | Ghi đè giá trị cũ | Mất lịch sử; sự kiện cũ hiển thị theo giá trị mới |
| Kiểu 2 | Thêm dòng mới với khoảng hiệu lực (từ ngày, đến ngày) và cờ bản hiện hành | Giữ đầy đủ lịch sử; sự kiện liên kết đúng phiên bản tại thời điểm xảy ra |
| Kiểu 3 | Thêm cột lưu giá trị trước đó | Chỉ giữ được một mức lịch sử |

Đề tài sử dụng SCD kiểu 2 cho chiều món ăn và chiều nhân viên. Lý do là giá bán và lương giờ tại thời điểm phát sinh giao dịch quyết định doanh thu kỳ vọng và chi phí nhân công. Nếu ghi đè, mọi phân tích trước ngày điều chỉnh giá sẽ bị sai.

## 2.4. Chất lượng dữ liệu

### 2.4.1. Các chiều chất lượng dữ liệu

Chất lượng dữ liệu được hiểu là mức độ phù hợp của dữ liệu với mục đích sử dụng. Wang và Strong (1996) đề xuất khung chất lượng dữ liệu nhìn từ phía người sử dụng, gồm bốn nhóm: chất lượng nội tại, theo ngữ cảnh, biểu diễn và khả năng truy cập. Các nghiên cứu sau đó (Batini & Scannapieco, 2016) tổng hợp thành những chiều đo lường được, trong đó các chiều thường dùng trong kỹ thuật dữ liệu được trình bày ở Bảng 2.3.

TABLE: Bảng 2.3. Các chiều chất lượng dữ liệu và ví dụ trong đề tài
WIDTHS: 2,4,6
| Chiều | Định nghĩa | Ví dụ lỗi trong dữ liệu nguồn của đề tài |
| Đầy đủ (completeness) | Dữ liệu cần có thì phải có | Nhân viên quên quẹt thẻ khi ra ca; phiếu kiểm kê bỏ trống ô; đơn sàn không được nhập vào POS |
| Hợp lệ (validity) | Giá trị đúng kiểu, định dạng, miền giá trị | Số lượng nhập kho gõ theo gam vào cột kilôgam; số lượng dính đơn vị như “53.6kg” |
| Duy nhất (uniqueness) | Một thực thể chỉ được ghi một lần | Máy chấm công ghi trùng lượt quẹt |
| Nhất quán (consistency) | Cùng một thông tin thống nhất giữa các nguồn | Một chi nhánh có sáu cách gọi khác nhau trên sáu hệ thống; tên nguyên liệu có dấu và không dấu |
| Kịp thời (timeliness) | Dữ liệu sẵn sàng đúng lúc cần | Báo cáo đối soát sàn chỉ có sau khi kết thúc tuần |
| Chính xác (accuracy) | Phản ánh đúng thực tế | Sai số đếm tay khi kiểm kê |

### 2.4.2. Kiểm thử dữ liệu và cách ly dòng lỗi

Tương tự kiểm thử phần mềm, kiểm thử dữ liệu (data testing) là các khẳng định tự động về dữ liệu, chạy sau mỗi lần biến đổi: khóa chính không trùng và không rỗng, khóa ngoại tồn tại ở bảng chiều, giá trị thuộc miền cho phép, tổng số tiền không đổi khi đi qua các tầng. Khi một dòng dữ liệu vi phạm quy tắc, có hai cách xử lý: dừng đường ống, hoặc *cách ly* (quarantine) dòng đó sang một bảng riêng kèm lý do để xem xét sau, trong khi các dòng hợp lệ tiếp tục được xử lý. Cách thứ hai phù hợp với dữ liệu vận hành, nơi một vài dòng nhập liệu sai không nên làm dừng toàn bộ báo cáo, nhưng cũng không được âm thầm bỏ qua.

Một nguyên tắc quan trọng là phân biệt lỗi kỹ thuật với tín hiệu nghiệp vụ. Lượt quẹt thẻ bị máy ghi trùng là lỗi kỹ thuật, cần được loại bỏ. Hóa đơn bị hủy, nhân viên quên quẹt thẻ khi ra ca hay đơn sàn không có trong POS lại là bằng chứng mà tầng phân tích cần để phát hiện sự cố, nên phải được giữ lại và gắn cờ, không được xóa trong quá trình làm sạch.

### 2.4.3. Giải quyết định danh thực thể

Giải quyết định danh thực thể (entity resolution, record linkage) là bài toán xác định các bản ghi ở những nguồn khác nhau cùng chỉ một thực thể ngoài đời thực (Christen, 2012). Lý thuyết nền tảng của Fellegi và Sunter (1969) mô hình hóa việc ghép cặp bản ghi như một bài toán quyết định dựa trên mức độ tương đồng của các trường. Trong thực tiễn kỹ thuật dữ liệu, thường kết hợp ba cách: (1) bảng ánh xạ do người hiểu nghiệp vụ xây dựng cho các thực thể ít và ổn định, ví dụ 11 chi nhánh; (2) quy tắc chuẩn hóa xác định, như bỏ dấu tiếng Việt, đưa về chữ thường, chuẩn hóa mã nhân viên; (3) khớp mờ dựa trên độ tương đồng chuỗi cho các trường nhập tự do, như tên nguyên liệu viết tắt, có ngưỡng chấp nhận và đưa các trường hợp không chắc chắn vào danh sách cần xem xét.

## 2.5. Phát hiện bất thường và truy vết nguyên nhân

### 2.5.1. Khái niệm và phân loại bất thường

Bất thường (anomaly) là mẫu dữ liệu không phù hợp với hành vi được kỳ vọng. Chandola, Banerjee và Kumar (2009) phân loại bất thường thành ba nhóm: bất thường điểm, khi một giá trị đơn lẻ khác biệt; bất thường theo ngữ cảnh, khi giá trị chỉ bất thường trong một ngữ cảnh nhất định, ví dụ doanh thu thấp vào tối thứ Bảy nhưng bình thường vào sáng thứ Hai; và bất thường tập thể, khi một chuỗi giá trị cùng nhau tạo thành mẫu bất thường dù từng giá trị không nổi bật. Phần lớn sự cố vận hành F&B thuộc hai nhóm sau. Hao hụt tăng 20% trong mười ngày, hay một thu ngân hủy thêm vài hóa đơn mỗi ngày trong bốn tuần, chỉ lộ ra khi xét cả chuỗi trong đúng ngữ cảnh của chi nhánh và nhân viên đó.

### 2.5.2. Các phương pháp thống kê

*Điểm chuẩn* (z-score) đo khoảng cách của một giá trị so với trung bình của tập tham chiếu, tính theo đơn vị độ lệch chuẩn:

EQ: z = (x − μ) / σ || (2.7)

Giá trị có |z| vượt một ngưỡng, thường từ 2,5 đến 3,5, được coi là bất thường. Điểm yếu của z-score là trung bình và độ lệch chuẩn bị chính các giá trị bất thường kéo lệch. *Điểm chuẩn hiệu chỉnh* (modified z-score) dùng trung vị và độ lệch tuyệt đối trung vị (MAD) thay thế, nên vững hơn trước ngoại lai; Iglewicz và Hoaglin (1993) đề xuất ngưỡng |M| > 3,5:

EQ: M = 0,6745 × (x − trung vị) / MAD || (2.8)

Hai kỹ thuật bổ trợ giúp đưa ngữ cảnh vào phép so sánh. *Cửa sổ trượt* (rolling window) cộng dồn chỉ số trong vài ngày để giảm nhiễu hằng ngày và làm nổi các bất thường kéo dài. *Đường cơ sở theo nhóm đồng nhất* (peer-group baseline) chỉ so một chi nhánh với lịch sử của chính nó, cùng ngày trong tuần, hoặc với các chi nhánh cùng hạng; khi đó các yếu tố tác động lên toàn chuỗi như ngày lễ hay thời tiết tự triệt tiêu.

### 2.5.3. Luật nghiệp vụ và kiểm định tỷ lệ

Không phải bài toán nào cũng nên giải bằng phương pháp thống kê dựa trên lịch sử. Với các quy định đã biết trước, như tỷ lệ hoa hồng trong hợp đồng, luật nghiệp vụ so sánh trực tiếp với giá trị cam kết là đúng đắn hơn: nếu sàn tính sai liên tục suốt kỳ quan sát, trung bình lịch sử cũng sai theo và z-score sẽ không bao giờ phát hiện được. Với các chỉ số dạng tỷ lệ trên số lần thử nhỏ, như tỷ lệ hủy hóa đơn của một thu ngân trong một tuần, có thể dùng *kiểm định nhị thức* (Agresti, 2013) để đánh giá khả năng quan sát được số lần hủy đó nếu thu ngân này có cùng tỷ lệ hủy với đồng nghiệp. Cách này tránh kết luận vội từ những tỷ lệ cao do số mẫu quá ít.

### 2.5.4. Phân rã chỉ số và cây KPI

Để truy vết nguyên nhân của một biến động, chỉ số tổng được phân rã thành các thành phần theo một *cây KPI* (KPI tree hay driver tree), trong đó mỗi nút cha là hàm của các nút con. Với doanh thu của một chi nhánh:

EQ: Doanh thu = Σ kênh k ( Số đơn k × AOV k ) || (2.9)

Khi doanh thu thay đổi giữa kỳ gốc (chỉ số 0) và kỳ quan sát (chỉ số 1), phần thay đổi có thể được phân bổ cho từng kênh và từng thành phần lượng và giá:

EQ: ΔDoanh thu = Σ k [ ΔSố đơn k × AOV k,0  +  Số đơn k,1 × ΔAOV k ] || (2.10)

Tương tự, lợi nhuận gộp vận hành được phân rã thành doanh thu trừ giá vốn, chi phí nhân công và phí sàn. Phân rã chỉ ra biến động nằm ở nhánh nào, ví dụ số đơn kênh GrabFood giảm trong khi AOV không đổi. Các tín hiệu đi kèm ở nhánh đó, như thời gian chuẩn bị tăng, đơn hủy do cửa hàng tăng, giờ công ca tối giảm, giúp thu hẹp về một nguyên nhân vận hành cụ thể. Kết hợp với đường cơ sở theo nhóm đồng nhất, cây KPI tách phần biến động chung của toàn chuỗi, vốn là bình thường, khỏi phần biến động riêng của một chi nhánh cần được điều tra.

### 2.5.5. Đánh giá bộ phát hiện

Khi có đáp án, chất lượng của bộ phát hiện được đo bằng ma trận nhầm lẫn: dương tính đúng (TP) là cảnh báo trùng với sự cố có thật, dương tính sai (FP) là cảnh báo không ứng với sự cố nào, âm tính sai (FN) là sự cố không được cảnh báo. Từ đó:

EQ: Precision = TP / (TP + FP);    Recall = TP / (TP + FN);    F1 = 2 × Precision × Recall / (Precision + Recall) || (2.11)

Precision cho biết trong số cảnh báo đưa ra, bao nhiêu là thật, quyết định niềm tin của người dùng vào hệ thống. Recall cho biết trong số sự cố xảy ra, bao nhiêu được phát hiện. Với các sự cố kéo dài nhiều ngày, cách đánh giá theo *mức sự kiện*, trong đó một sự cố được tính là đã phát hiện nếu có ít nhất một cảnh báo đúng trong khoảng thời gian của nó, phù hợp với cách người quản lý sử dụng hơn là đánh giá theo từng ngày; độ trễ phát hiện là thước đo bổ sung. Điều kiện để kết quả đánh giá có giá trị là tập dữ liệu dùng để đánh giá phải độc lập với tập đã dùng để chọn tham số.

## 2.6. Dữ liệu mô phỏng trong nghiên cứu

Dữ liệu mô phỏng (synthetic data) được dùng rộng rãi khi dữ liệu thật nhạy cảm, khó tiếp cận, hoặc khi cần một đáp án biết trước để đánh giá phương pháp. Patki, Wedge và Veeramachaneni (2016) chỉ ra rằng dữ liệu tổng hợp được sinh có cấu trúc, mô phỏng đúng quan hệ giữa các bảng, có thể thay thế dữ liệu thật trong nhiều tác vụ phát triển và kiểm thử. Ưu điểm lớn nhất của dữ liệu mô phỏng trong bài toán phát hiện sự cố là có đáp án: người nghiên cứu biết chính xác sự cố nào xảy ra, ở đâu, khi nào, mức độ bao nhiêu. Rủi ro chính là dữ liệu có thể quá “sạch” hoặc quá đơn giản so với thực tế, khiến phương pháp trông tốt hơn thực chất.

Để giảm rủi ro này, khóa luận áp dụng bốn nguyên tắc. Thứ nhất, neo tham số vào thực tế và mô phỏng đúng các quy luật vận hành đã biết. Ví dụ, thời gian chờ trong một hệ thống phục vụ tăng phi tuyến khi mức tải tiến gần năng lực, tỷ lệ với 1/(1 − ρ) trong mô hình hàng đợi cơ bản với ρ là mức sử dụng (Kleinrock, 1975). Thứ hai, sinh mọi nguồn dữ liệu từ cùng một tập sự kiện để các nguồn nhất quán với nhau như ngoài đời thực. Thứ ba, đưa vào các lỗi dữ liệu đặc trưng của từng hệ thống nguồn để phần kỹ thuật dữ liệu phải xử lý những vấn đề có thật. Thứ tư, ước lượng các phân phối đầu vào từ dữ liệu quan sát thật khi có thể. Đây là bước mô hình hóa dữ liệu đầu vào (input modeling) trong phương pháp mô phỏng: thay vì tự đặt, các tham số như phân phối số món mỗi đơn được ước lượng từ dữ liệu thật, sau đó đánh giá xem quy luật đó có chuyển giao được sang bối cảnh mô phỏng hay không (Law, 2015).

## 2.7. Công nghệ sử dụng

Nguyên tắc lựa chọn công nghệ của khóa luận là tương xứng với quy mô và có lý do. Dữ liệu của bài toán ở mức hàng trăm megabyte đến vài gigabyte mỗi năm, nằm trong khả năng xử lý của một máy tính cá nhân. Vì vậy đề tài không sử dụng các nền tảng xử lý phân tán như Spark hay Hadoop, vốn được thiết kế cho dữ liệu lớn hơn nhiều bậc và kéo theo chi phí vận hành không cần thiết.

- DuckDB là hệ quản trị cơ sở dữ liệu phân tích (OLAP) dạng nhúng, chạy trong cùng tiến trình với chương trình, lưu trữ theo cột và thực thi truy vấn theo vector (Raasveldt & Mühleisen, 2019). DuckDB đọc trực tiếp JSON, CSV, Parquet, không cần máy chủ, và toàn bộ kho dữ liệu nằm trong một tệp, nên phù hợp với quy mô đề tài và dễ tái lập.
- dbt (data build tool) cho phép viết các bước biến đổi dưới dạng câu lệnh SQL `SELECT` có quản lý phiên bản, tự dựng đồ thị phụ thuộc giữa các mô hình, có sẵn các kiểm thử dữ liệu và sinh tài liệu kèm sơ đồ dòng dữ liệu (lineage) (dbt Labs, n.d.). dbt hiện thực trực tiếp các nguyên tắc ELT và kiểm thử dữ liệu ở mục 2.2 và 2.4.
- Apache Airflow điều phối các bước của đường ống thành đồ thị có hướng không chu trình (DAG), theo dõi trạng thái và chạy lại khi lỗi; ngoài chạy theo lịch, một DAG có thể được kích hoạt khi tập dữ liệu (Dataset) do DAG khác tạo ra vừa cập nhật (Apache Software Foundation, n.d.). Docker Compose đóng gói các dịch vụ để chạy nhất quán trên mọi máy (Docker Inc., n.d.).
- PostgreSQL là hệ quản trị cơ sở dữ liệu quan hệ theo mô hình máy chủ, cho nhiều kết nối đồng thời và phân quyền chi tiết (PostgreSQL Global Development Group, n.d.). Trong khóa luận, PostgreSQL là kho phục vụ: nhận bản sao tầng Gold để công cụ báo cáo đọc, còn việc tính toán vẫn do DuckDB đảm nhận; tách máy tính toán khỏi nơi phục vụ người đọc là cách làm phổ biến trong thực tiễn (Reis & Housley, 2022).
- Docker đóng gói mỗi thành phần cùng đúng phiên bản thư viện vào một container. Docker Compose khai báo toàn bộ các container, mạng nội bộ và thư mục dùng chung trong một tệp, nên cả nền tảng được dựng lại trên máy khác bằng một lệnh (Docker Inc., n.d.).
- FastAPI là thư viện Python để xây dựng API web, tự sinh tài liệu theo chuẩn OpenAPI (FastAPI, n.d.). Khóa luận dùng FastAPI để dựng API giả lập của phần mềm POS đám mây và ứng dụng đặt hàng, có xác thực, phân trang và giới hạn tần suất như API thật.
- Python được dùng cho bộ mô phỏng, bước nạp dữ liệu, các bộ phát hiện và ứng dụng. Metabase là công cụ BI mã nguồn mở, dựng được bảng điều khiển bằng giao diện lập trình nên tái lập được (Metabase, n.d.). Streamlit dùng để xây dựng các trang phân tích cần logic riêng như cảnh báo và truy vết (Streamlit, n.d.).

TABLE: Bảng 2.4. Lựa chọn công nghệ và lý do
WIDTHS: 3,3,6
| Nhu cầu | Công nghệ chọn | Lý do và phương án không chọn |
| Tính toán và lưu trữ của đường ống | DuckDB | Dữ liệu cỡ trăm MB, một máy; truy vấn phân tích theo cột nhanh, không cần máy chủ; không cần cụm Spark |
| Biến đổi dữ liệu Silver/Gold | dbt (dbt-duckdb) | SQL có kiểm thử, tài liệu và lineage; thay cho các script Python rời rạc khó kiểm thử |
| Thu thập qua API | Bộ kết nối viết bằng Python, chỉ dùng thư viện chuẩn | Chỉ có hai nguồn API và cần kiểm soát mốc, đối chiếu, hợp đồng dữ liệu theo đúng nghiệp vụ; công cụ tích hợp dựng sẵn như Airbyte cần thêm một hệ thống chạy riêng, nặng hơn mức cần cho quy mô này |
| API giả lập phía nguồn | FastAPI | Dựng nhanh một API có xác thực, phân trang và tài liệu tự sinh để kiểm chứng bộ kết nối như với phần mềm thật |
| Nạp dữ liệu Bronze | Python | Cần đọc Excel dạng phiếu và JSON lồng nhau, ghi nhật ký nạp |
| Kho phục vụ cho người đọc | PostgreSQL | Tệp DuckDB chỉ cho một tiến trình ghi tại một thời điểm, không có tài khoản người dùng; PostgreSQL cho nhiều kết nối đọc đồng thời, tài khoản chỉ đọc, và là nguồn chuẩn mà công cụ BI nào cũng kết nối được |
| Báo cáo kinh doanh | Metabase | Mã nguồn mở, chạy trong Docker, dựng dashboard bằng API nên tái lập được; Power BI cần tài khoản dịch vụ trả phí để chia sẻ và nhúng; Apache Superset nặng hơn mức cần cho quy mô này |
| Điều phối | Airflow + Docker Compose | Chạy theo lịch và theo dữ liệu mới, theo dõi lỗi; Kafka/streaming không cần vì nhịp nghiệp vụ là theo ngày |
| Ứng dụng phân tích | Streamlit | Xây dựng nhanh bằng Python cho các trang có logic riêng như cảnh báo, truy vết, vận hành dữ liệu |

## 2.8. Các nghiên cứu và giải pháp liên quan

Các giải pháp liên quan đến bài toán của khóa luận có thể chia thành ba nhóm. Nhóm thứ nhất là các phần mềm quản lý bán hàng và báo cáo cho nhà hàng do các nhà cung cấp POS phát triển, mạnh ở báo cáo doanh thu theo kênh, món, ca, nhưng thường chỉ khai thác dữ liệu trong phạm vi hệ thống của chính nhà cung cấp, không tích hợp báo cáo đối soát của sàn, sổ kho ghi tay hay máy chấm công của bên thứ ba. Nhóm thứ hai là các nghiên cứu phát hiện bất thường và gian lận trong bán lẻ, thường tập trung vào một loại sự cố và một nguồn dữ liệu, chẳng hạn giao dịch POS. Nhóm thứ ba là các tài liệu và nghiên cứu điển hình về xây dựng kho dữ liệu, tập trung vào kiến trúc và mô hình hóa, ít đi kèm đánh giá định lượng về khả năng phát hiện sự cố trên dữ liệu đó.

TODO: thêm 4–6 nghiên cứu liên quan có trích dẫn cho ba nhóm trên.

## 2.9. Khoảng trống nghiên cứu và tiểu kết chương

Từ tổng quan trên, khoảng trống mà khóa luận hướng tới là sự kết hợp ba yếu tố thường bị tách rời. Thứ nhất là tích hợp đầy đủ các nguồn dữ liệu vận hành không đồng nhất của một chuỗi F&B, kể cả các nguồn bán cấu trúc do con người ghi tay như sổ kho và phiếu kiểm kê. Thứ hai là một kho dữ liệu có kiểm chứng chất lượng làm nền cho phân tích, thay vì phân tích trực tiếp trên dữ liệu thô. Thứ ba là đánh giá định lượng khả năng phát hiện và truy vết nhiều loại sự cố trên một tập kịch bản độc lập có đáp án.

Tóm lại, chương này đã xác lập hai nhóm cơ sở cho khóa luận. Về nghiệp vụ, các chỉ số COGS%, chênh lệch AvT, Labor%, tỷ lệ hoa hồng hiệu dụng và tỷ lệ hủy theo thu ngân cho biết dữ liệu nào cần thu thập và mỗi vấn đề P1–P5 để lại dấu vết ở đâu. Về kỹ thuật, kiến trúc Medallion, mô hình hóa chiều, kiểm thử chất lượng dữ liệu, các phương pháp thống kê vững cùng cây KPI là những công cụ để biến dữ liệu rời rạc thành bằng chứng có thể kiểm chứng. Chương 3 vận dụng các cơ sở này để thiết kế hệ thống.
