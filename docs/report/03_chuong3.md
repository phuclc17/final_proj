# CHƯƠNG 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

Chương này trình bày thiết kế của nền tảng theo trình tự dòng dữ liệu: từ yêu cầu của người dùng (mục 3.1) và kiến trúc tổng thể (mục 3.2), đến bộ mô phỏng tạo ra dữ liệu nguồn (mục 3.3), đường ống dữ liệu từ tầng thu thập tới Silver (mục 3.4), kho dữ liệu (mục 3.5), kiểm soát chất lượng (mục 3.6), lớp phân tích (mục 3.7) và cuối cùng là ứng dụng, kho phục vụ và cơ chế điều phối (mục 3.8); mục 3.9 tóm tắt chương.

## 3.1. Phân tích yêu cầu

### 3.1.1. Các bên liên quan và tác nhân

TABLE: Bảng 3.1. Các tác nhân của hệ thống
WIDTHS: 3,5,5
| Tác nhân | Vai trò | Nhu cầu chính với hệ thống |
| Quản lý vận hành chuỗi | Theo dõi hiệu quả toàn chuỗi, ra quyết định điều chỉnh | Biết chi nhánh nào đang có vấn đề, vấn đề gì, mất bao nhiêu tiền; phân biệt biến động bình thường và bất thường |
| Kế toán, kiểm soát tài chính | Đối soát doanh thu với sàn, kiểm soát giá vốn và chi phí | Danh sách sai lệch đối soát theo tuần; chênh lệch kiểm kê; hóa đơn hủy bất thường |
| Quản lý chi nhánh | Điều hành ca, kho, nhân sự tại cửa hàng | Biết ca nào thiếu hoặc thừa người, nguyên liệu nào hao hụt |
| Kỹ sư dữ liệu | Xây dựng và vận hành đường ống dữ liệu | Nạp dữ liệu mới tự động; theo dõi chất lượng dữ liệu; biết dòng nào bị cách ly và vì sao |

### 3.1.2. Yêu cầu chức năng

TABLE: Bảng 3.2. Yêu cầu chức năng
WIDTHS: 1,8,3
| Mã | Yêu cầu | Tác nhân |
| FR1 | Thu nhận dữ liệu từ bảy nhóm hệ thống nguồn qua đúng kênh mà mỗi hệ thống hỗ trợ (kéo qua API, tệp xuất tự động, tệp do người gửi); nhận dạng tệp theo nội dung, từ chối tệp sai hợp đồng dữ liệu kèm lý do; nạp tự động phần mới, không nạp trùng | Kỹ sư dữ liệu, kế toán, quản lý chi nhánh |
| FR2 | Làm sạch, chuẩn hóa và giải quyết định danh chi nhánh, nhân viên, món, nguyên liệu giữa các hệ thống | Kỹ sư dữ liệu |
| FR3 | Cách ly các dòng dữ liệu vi phạm quy tắc kèm lý do; báo cáo tình trạng chất lượng dữ liệu | Kỹ sư dữ liệu |
| FR4 | Lưu dữ liệu sạch vào kho dữ liệu dạng lược đồ hình sao, giữ lịch sử thay đổi giá món và lương | Kỹ sư dữ liệu |
| FR5 | Tính các chỉ số vận hành theo chi nhánh, ngày, ca, kênh: doanh thu, số đơn, AOV, COGS%, Labor%, OPLH, thời gian chuẩn bị, tỷ lệ hủy | Quản lý vận hành |
| FR6 | Phát hiện năm loại sự cố P1–P5 và đưa ra danh sách cảnh báo có mức độ, bằng chứng và ước tính thiệt hại | Quản lý vận hành, kế toán |
| FR7 | Truy vết biến động doanh thu của một chi nhánh trong một tuần về kênh, thành phần (lượng, giá) và nguyên nhân vận hành | Quản lý vận hành |
| FR8 | Xem chi tiết bằng chứng của một cảnh báo (dữ liệu gốc liên quan) | Quản lý vận hành, chi nhánh |
| FR9 | Tự động chạy toàn bộ đường ống khi có dữ liệu mới, đưa kết quả sang kho phục vụ cho công cụ báo cáo | Kỹ sư dữ liệu |

### 3.1.3. Yêu cầu phi chức năng

TABLE: Bảng 3.3. Yêu cầu phi chức năng
WIDTHS: 1,3,8
| Mã | Thuộc tính | Yêu cầu |
| NFR1 | Tái lập | Cùng dữ liệu nguồn và cùng mã nguồn cho cùng kết quả; dữ liệu mô phỏng tái lập được nhờ hạt giống ngẫu nhiên cố định |
| NFR2 | Lũy đẳng, tăng dần | Chạy lại không sinh dữ liệu trùng; mỗi ngày chỉ xử lý dữ liệu mới |
| NFR3 | Truy vết nguồn gốc | Mọi dòng dữ liệu truy ngược được về tệp và dòng gốc |
| NFR4 | Kiểm chứng được | Kiểm thử chất lượng dữ liệu tự động sau mỗi lần biến đổi; đối soát số dòng và tổng tiền giữa các tầng |
| NFR5 | Giải thích được | Mọi cảnh báo phải kèm chỉ số, ngưỡng và dữ liệu làm căn cứ; không dùng mô hình hộp đen |
| NFR6 | Độc lập đánh giá | Đường ống và các bộ phát hiện không được đọc đáp án của bộ mô phỏng; tham số chỉ được chọn trên tập phát triển |
| NFR7 | Hiệu năng | Chạy được trên một máy tính cá nhân; xử lý một ngày dữ liệu mới trong vài phút |
| NFR8 | Chịu lỗi nguồn | Tệp hỏng, sai hợp đồng, thiếu tệp hoặc API nguồn không phản hồi không làm dừng các nguồn khác, không bị bỏ qua im lặng và không dẫn tới kết luận sự cố sai; khi dữ liệu về đủ, lượt chạy sau tự xử lý tiếp |

### 3.1.4. Phân rã chức năng

Từ các yêu cầu chức năng ở Bảng 3.2, nền tảng được phân rã thành năm nhóm chức năng như Hình 3.1. Nhóm thu thập dữ liệu đưa dữ liệu từ các hệ thống nguồn vào vùng tiếp nhận và kiểm tra theo hợp đồng dữ liệu. Nhóm xử lý và lưu trữ biến dữ liệu thô thành kho dữ liệu đã được kiểm thử. Nhóm phân tích vận hành tạo ra cảnh báo, truy vết và đề xuất xử lý cho người dùng nghiệp vụ. Nhóm vận hành nền tảng phục vụ kỹ sư dữ liệu theo dõi và tra cứu. Nhóm kiểm chứng được tách riêng, chỉ dùng để đánh giá phương pháp, và là nơi duy nhất được đọc đáp án của bộ mô phỏng. Mỗi chức năng ở mức dưới cùng ứng với một bước của đường ống hoặc một trang của ứng dụng.

IMAGE: figures/h3_bfd.png || Hình 3.1. Sơ đồ phân rã chức năng của nền tảng || 16

### 3.1.5. Sơ đồ ca sử dụng

Các sơ đồ trong chương này dùng ký hiệu UML 2.5 (Object Management Group, 2017). Hình 3.2 có bốn tác nhân là người và hai tác nhân là hệ thống. Quản lý vận hành dùng các ca phân tích UC01 đến UC03. Quản lý chi nhánh xem tổng quan, truy vết chi nhánh của mình và gửi tệp như sổ nhập kho, phiếu kiểm kê. Kế toán xem cảnh báo, bằng chứng đối soát và gửi báo cáo của sàn. Kỹ sư dữ liệu dùng các ca UC06 đến UC11 để theo dõi nguồn, chất lượng, lượt xử lý và đánh giá bộ phát hiện. Ca UC12 không do người khởi động: hệ thống nguồn ghi dữ liệu mới và Airflow tự chạy đường ống. Ca UC03 luôn bao gồm UC04, vì kết luận truy vết nào cũng phải kèm bằng chứng gốc và đề xuất xử lý.

IMAGE: figures/h3_1_use_case.png || Hình 3.2. Sơ đồ ca sử dụng của hệ thống || 16

### 3.1.6. Đặc tả ca sử dụng

Bảng 3.4 đến Bảng 3.8 đặc tả năm ca sử dụng chính theo cùng một khuôn: tác nhân, mục tiêu, tiền điều kiện, luồng sự kiện chính, luồng thay thế và hậu điều kiện. Các ca còn lại chủ yếu là xem và tra cứu, luồng đơn giản nên không đặc tả riêng. Số thứ tự ở luồng thay thế chỉ bước của luồng chính mà nó rẽ ra.

TABLE: Bảng 3.4. Đặc tả ca sử dụng UC02 Xem cảnh báo sắp theo thiệt hại ước tính
WIDTHS: 2.3,9.7
| Mục | Nội dung |
| Tác nhân | Quản lý vận hành, kế toán |
| Mục tiêu | Biết chi nhánh nào, tuần nào có vấn đề và nên xử lý vấn đề nào trước |
| Tiền điều kiện | Đường ống đã chạy xong ít nhất một lượt; kho có tầng Gold của môi trường đang chọn |
| Luồng chính | 1. Người dùng mở trang Trung tâm cảnh báo, chọn chi nhánh và khoảng thời gian ở thanh bên.<br>2. Hệ thống đọc Gold, quét bộ chỉ số giám sát và chấm điểm năm giả thuyết nguyên nhân cho mọi chi nhánh, tuần trong khoảng đã chọn.<br>3. Hệ thống hiển thị bản đồ mức cảnh báo theo chi nhánh × tuần và danh sách cảnh báo kèm nguyên nhân, điểm, bằng chứng chính, thiệt hại ước tính, người phụ trách, sắp theo thiệt hại.<br>4. Người dùng chọn một dòng và bấm Truy vết để chuyển sang UC03. |
| Luồng thay thế | 2a. Kho đang được đường ống ghi: trang báo đường ống đang ghi dữ liệu, người dùng tải lại sau ít giây.<br>3a. Người dùng thay ngưỡng điểm cảnh báo: bản đồ và danh sách cập nhật theo ngưỡng mới; kết quả chính thức vẫn báo cáo ở ngưỡng 3,5.<br>3b. Không có cảnh báo trong khoảng đã chọn: trang chỉ còn các mục cần theo dõi. |
| Hậu điều kiện | Dữ liệu không thay đổi; trang chỉ đọc kho |

TABLE: Bảng 3.5. Đặc tả ca sử dụng UC03 Truy vết nguyên nhân biến động doanh thu, bao gồm UC04
WIDTHS: 2.3,9.7
| Mục | Nội dung |
| Tác nhân | Quản lý vận hành, quản lý chi nhánh |
| Mục tiêu | Biết biến động doanh thu của một chi nhánh trong một tuần đến từ kênh nào, thành phần nào, nguyên nhân vận hành nào và cần làm gì |
| Tiền điều kiện | Chi nhánh có ít nhất bốn tuần lịch sử để tính mức kỳ vọng |
| Luồng chính | 1. Người dùng mở trang Truy vết từ một cảnh báo, hoặc tự chọn chi nhánh và tuần; mặc định là cảnh báo gần nhất.<br>2. Hệ thống hiển thị kết luận gồm nguyên nhân hạng một, điểm bằng chứng và nghi vấn thứ hai nếu cũng vượt ngưỡng.<br>3. Hệ thống hiển thị đề xuất xử lý gồm việc cần xác minh, việc cần làm, việc theo dõi, người phụ trách, thời hạn và thiệt hại ước tính.<br>4. Hệ thống hiển thị doanh thu so với mức kỳ vọng qua các tuần, cây KPI theo kênh, số đơn và AOV, cùng các tín hiệu của từng giả thuyết.<br>5. Hệ thống liệt kê bằng chứng gốc: các bản ghi làm căn cứ kèm tên tệp và số dòng gốc.<br>6. Người dùng bấm Mở tệp gốc; hệ thống mở trang Tệp nguồn đúng tệp đó, lọc sẵn dòng liên quan. |
| Luồng thay thế | 2a. Không giả thuyết nào đủ điểm mà doanh thu vẫn lệch kỳ vọng: kết luận ghi chưa xác định nguyên nhân, đề xuất kiểm tra chung.<br>2b. Chi nhánh thiếu dữ liệu nguồn trong tuần: giả thuyết dựa trên nguồn đó chỉ ở mức theo dõi, kèm ghi chú chưa kết luận. |
| Hậu điều kiện | Dữ liệu không thay đổi; người dùng có căn cứ để giao việc theo quy trình ở mục 3.7.4 |

TABLE: Bảng 3.6. Đặc tả ca sử dụng UC05 Gửi tệp nguồn qua trang tải lên
WIDTHS: 2.3,9.7
| Mục | Nội dung |
| Tác nhân | Kế toán, quản lý chi nhánh |
| Mục tiêu | Đưa báo cáo sàn, sổ nhập kho, phiếu kiểm kê hoặc bản sửa vào hệ thống mà không cần kỹ sư dữ liệu |
| Tiền điều kiện | Đang ở môi trường vận hành; tệp dạng JSON, CSV hoặc Excel |
| Luồng chính | 1. Người dùng chọn một hoặc nhiều tệp, bấm Gửi vào hệ thống.<br>2. Với từng tệp, hệ thống nhận dạng nguồn theo nội dung, kiểm tra hợp đồng dữ liệu và tính vị trí chuẩn theo nguồn, chi nhánh, ngày.<br>3. Hệ thống ghi tệp vào vùng tiếp nhận bằng cách ghi tệp tạm rồi đổi tên, sau đó ghi nhật ký tiếp nhận.<br>4. Hệ thống báo Airflow có dữ liệu mới; đường ống tự chạy.<br>5. Hệ thống hiển thị kết quả của từng tệp và theo dõi trạng thái nạp cho tới khi xong. |
| Luồng thay thế | 2a. Tệp không thuộc nguồn nào hoặc sai hợp đồng: từ chối, lưu bản sao vào thư mục tệp bị từ chối và nêu lý do cụ thể.<br>2b. Đã có tệp ở cùng vị trí với nội dung giống hệt: bỏ qua vì trùng.<br>2c. Đã có tệp ở cùng vị trí nhưng nội dung khác: coi là bản sửa, thay bản cũ ở lượt nạp kế tiếp.<br>2d. Nội dung giống hệt một tệp khác đã có: từ chối để không đếm hai lần.<br>4a. Airflow không chạy: tệp vẫn nằm trong vùng tiếp nhận và được nạp ở lượt kế tiếp. |
| Hậu điều kiện | Tệp hợp lệ nằm đúng vị trí chuẩn; mọi lần gửi đều có một dòng trong nhật ký tiếp nhận |

TABLE: Bảng 3.7. Đặc tả ca sử dụng UC10 Theo dõi lượt xử lý hằng ngày
WIDTHS: 2.3,9.7
| Mục | Nội dung |
| Tác nhân | Kỹ sư dữ liệu |
| Mục tiêu | Biết dữ liệu đã đến ngày nào, lượt xử lý gần nhất đạt hay dừng ở bước nào và có cảnh báo mới không |
| Tiền điều kiện | Airflow đang chạy |
| Luồng chính | 1. Người dùng mở trang Vận hành hằng ngày.<br>2. Hệ thống đọc trạng thái hai DAG qua REST API của Airflow và nhật ký ops.pipeline_runs, hiển thị tám ô trạng thái từ hệ thống nguồn tới kho phục vụ; khi có lượt đang chạy, các ô tự làm mới mỗi ba giây.<br>3. Hệ thống hiển thị kết quả từng bước của lượt gần nhất: số bản ghi kéo qua API, số tệp mới, số dòng nạp, các mục cửa chặn, số bước dbt đạt, số cảnh báo và số dòng sang PostgreSQL.<br>4. Hệ thống liệt kê cảnh báo của tuần mới nhất; người dùng mở được UC03 từ đây. |
| Luồng thay thế | 1a. Người dùng bấm Gửi dữ liệu ngày mới: hệ thống kích hoạt DAG nguồn, các ô chuyển trạng thái lần lượt khi đường ống tự chạy.<br>2a. Airflow không phản hồi: trang báo Airflow chưa chạy, phần nhật ký đọc từ kho vẫn hiển thị.<br>3a. Một bước lỗi hoặc bị chặn: ô của bước đó hiện mức lỗi, các bước sau ở trạng thái chưa chạy. |
| Hậu điều kiện | Dữ liệu không thay đổi, trừ khi người dùng kích hoạt DAG nguồn ở luồng 1a |

TABLE: Bảng 3.8. Đặc tả ca sử dụng UC12 Thu thập và xử lý dữ liệu mới
WIDTHS: 2.3,9.7
| Mục | Nội dung |
| Tác nhân | Airflow, hệ thống nguồn |
| Mục tiêu | Đưa dữ liệu mới từ mọi nguồn qua các tầng tới cảnh báo và kho phục vụ mà không cần thao tác tay |
| Tiền điều kiện | Hệ thống nguồn đã ghi dữ liệu mới, hoặc có tệp được gửi vào vùng tiếp nhận; không có lượt nào khác đang chạy |
| Luồng chính | 1. Hệ thống nguồn báo Dataset cập nhật, hoặc đến lượt kiểm tra mỗi giờ.<br>2. Bước extract kéo các ngày mới qua API theo mốc ngày.<br>3. Bước check đối chiếu tệp nguồn với nhật ký nạp và xác nhận có tệp mới.<br>4. Bước ingest nạp tệp mới vào Bronze.<br>5. Bước quality chạy cửa chặn chất lượng đầu vào.<br>6. Bước dbt dựng Silver, Gold và chạy 158 kiểm thử.<br>7. Bước detect quét chỉ số và ghi cảnh báo.<br>8. Bước publish đối soát số dòng rồi thay bản sao Gold và các bảng vận hành trên PostgreSQL. |
| Luồng thay thế | 2a. API không phản hồi sau sáu lần thử: ghi trạng thái cảnh báo, các nguồn tệp vẫn được xử lý.<br>3a. Không có tệp mới: kết thúc lượt, không ghi nhật ký.<br>5a. Có mục ở mức chặn: dừng lượt, kho phục vụ giữ bản cũ.<br>6a. Có kiểm thử lỗi: dừng lượt, kho phục vụ giữ bản cũ.<br>Ở bất kỳ bước nào trừ check: bước lỗi được Airflow thử lại một lần sau hai phút. |
| Hậu điều kiện | Mỗi bước đã chạy có một dòng trong ops.pipeline_runs; kho phục vụ hoặc là bản mới đã đối soát, hoặc giữ nguyên bản cũ |

## 3.2. Kiến trúc tổng thể

IMAGE: figures/h3_2_kien_truc.png || Hình 3.3. Kiến trúc tổng thể của nền tảng || 16

Nền tảng gồm sáu lớp chức năng như Hình 3.3.

1. Lớp nguồn và thu thập. Bảy nhóm hệ thống nguồn giữ dữ liệu theo cách riêng. Các phần mềm có API như POS đám mây và ứng dụng đặt hàng chỉ cho lấy dữ liệu qua API; phần mềm cài tại máy và máy chấm công xuất tệp theo lịch; báo cáo sàn, sổ kho, phiếu kiểm kê do người lập và gửi. Tầng thu thập đưa cả ba đường về một vùng tiếp nhận, kiểm tra từng tệp theo hợp đồng dữ liệu của nguồn (mục 3.4.2). Trong khóa luận, các hệ thống nguồn do bộ mô phỏng đóng vai (mục 3.3), phía API do một dịch vụ giả lập phục vụ. Khi triển khai thực tế, chỉ phần nguồn được thay bằng hệ thống thật; tầng thu thập và các lớp phía sau giữ nguyên.
2. Lớp nạp và lưu trữ thô, tức tầng Bronze. Một chương trình Python đọc các file mới, giữ nguyên giá trị gốc, bổ sung siêu dữ liệu và ghi vào kho DuckDB.
3. Lớp biến đổi. Các mô hình dbt làm sạch, chuẩn hóa, giải quyết định danh và cách ly dòng lỗi ở tầng Silver, rồi tổ chức thành lược đồ hình sao và các bảng chỉ số ở tầng Gold, kèm kiểm thử chất lượng dữ liệu.
4. Lớp phân tích tính mức kỳ vọng của các chỉ số, cây KPI truy vết, năm bộ phát hiện sự cố và đề xuất xử lý cho từng cảnh báo.
5. Lớp phục vụ. Sau mỗi lượt chạy, tầng Gold và các bảng cảnh báo được sao sang PostgreSQL. Công cụ BI Metabase đọc từ đây bằng tài khoản chỉ đọc.
6. Lớp trình bày và điều phối. Ứng dụng Streamlit là địa chỉ duy nhất cho người dùng, trong đó trang Tổng quan nhúng dashboard Metabase; Airflow phát hiện dữ liệu mới và chạy toàn bộ chuỗi các bước.

DuckDB và PostgreSQL có vai trò khác nhau. DuckDB là máy tính toán của đường ống: dbt chạy trên đó, mọi phép biến đổi và kiểm thử diễn ra trong một tệp, nhanh và dễ tái lập. Nhưng một tệp DuckDB chỉ cho một tiến trình ghi và không có tài khoản người dùng, nên không phù hợp để nhiều người và nhiều công cụ cùng đọc trong lúc đường ống đang ghi. PostgreSQL đảm nhận phần đó. Tách hai vai trò cũng giúp người đọc không bao giờ thấy dữ liệu dở dang: bản sao chỉ được thay khi một lượt chạy đã qua hết các kiểm thử.

Ràng buộc kiến trúc quan trọng nhất là đáp án của bộ mô phỏng nằm ngoài đường ống. Thư mục đáp án chỉ được đọc bởi chương trình kiểm chứng bộ mô phỏng, chương trình đánh giá ở Chương 5 và trang Bộ mô phỏng của ứng dụng, nơi trình bày và kiểm chứng dữ liệu được sinh ra. Đường ống dữ liệu và các bộ phát hiện chỉ nhìn thấy dữ liệu nguồn, giống hệt điều kiện triển khai thực tế.

## 3.3. Thiết kế bộ mô phỏng dữ liệu nguồn

### 3.3.1. Nguyên lý “một thế giới, nhiều góc nhìn”

Cách đơn giản nhất để tạo dữ liệu thử nghiệm là sinh ngẫu nhiên từng nguồn một cách độc lập. Cách này tạo ra dữ liệu không nhất quán: báo cáo đối soát của sàn không khớp với đơn hàng trong POS, mã nhân viên trên hóa đơn không ứng với ai trong danh sách chấm công, thiếu nhân sự không làm ảnh hưởng gì đến doanh thu. Trên dữ liệu như vậy, việc “tích hợp đa nguồn” chỉ là hình thức, và mọi phương pháp truy vết nguyên nhân đều không thể kiểm chứng.

Bộ mô phỏng của khóa luận được thiết kế theo nguyên lý ngược lại, gọi là “một thế giới, nhiều góc nhìn”. Mỗi ngày, bộ mô phỏng sinh ra các sự kiện thật của chuỗi đúng một lần: khách nào đặt đơn qua kênh nào, vào giờ nào, gồm món gì; nhân viên nào đi làm ca nào; bếp chịu tải bao nhiêu; nguyên liệu được dùng, hỏng, mất bao nhiêu; hàng được giao lúc nào; kho được kiểm kê ra sao. Sau đó, mỗi hệ thống nguồn xuất ra phần sự kiện mà nó quan sát được, theo định dạng và quy ước riêng, kèm các lỗi đặc trưng của hệ thống đó. Nhờ vậy, các nguồn dữ liệu nhất quán với nhau như ngoài đời thực, và các sự cố được đưa vào thế giới sẽ để lại dấu vết đồng thời ở nhiều nguồn.

### 3.3.2. Các hệ thống nguồn và định dạng dữ liệu

TABLE: Bảng 3.9. Các hệ thống nguồn và phần sự kiện mỗi hệ thống quan sát được
WIDTHS: 2,4,3,5
| Hệ thống nguồn | Phần sự kiện quan sát được | Định dạng | Quy ước riêng |
| POS tại quầy | Đơn tại quầy (mọi trạng thái) và đơn sàn đã hoàn thành do nhân viên nhập tay | JSON theo chi nhánh, theo ngày; 43 trường | Mã chi nhánh theo tiền tố máy POS; mã thu ngân dạng `NV0012` |
| Ứng dụng riêng | Đơn đặt qua ứng dụng (mọi trạng thái), khách hàng | JSON xuất từ API theo ngày; 30 trường | Giờ UTC; mã chi nhánh và mã món riêng của ứng dụng |
| GrabFood | Tổng hợp tuần của đúng các đơn Grab thật | CSV theo tuần, tiếng Anh | Tên cửa hàng dạng tự do; chỉ có số tiền hoa hồng |
| ShopeeFood | Tổng hợp tuần của đúng các đơn Shopee thật | Excel theo tuần, tiếng Việt | Mã cửa hàng riêng; có dòng tiêu đề báo cáo |
| Sổ nhập kho | Từng lần giao hàng | Excel do quản lý ghi, hai mẫu khác nhau | Tên nguyên liệu nhập tự do |
| Phiếu kiểm kê | Tồn thực tế hai tuần một lần | Excel dạng phiếu | Mã nguyên liệu `NL01`…`NL22` |
| Máy chấm công | Lượt quẹt vào, ra | CSV theo chi nhánh, theo ngày | Mã nhân viên dạng số, mã chi nhánh `BR01` |
| Hệ thống trụ sở | Danh mục chi nhánh, món, giá, nguyên liệu, công thức, nhân viên, hợp đồng sàn | CSV, xuất lại khi có thay đổi | Ảnh chụp theo ngày hiệu lực |
| Dữ liệu thời tiết | Lượng mưa, tình trạng thời tiết theo ngày | JSON theo ngày | Nguồn bên ngoài |

### 3.3.3. Mô hình nhu cầu và biến động bình thường

Số đơn kỳ vọng của chi nhánh b, kênh k, ngày d được mô hình hóa dạng tích các hệ số:

EQ: λ(b,k,d) = Q(hạng b) × h(b) × w(thứ của d) × ε(b,d) × s(k) × L(k,d) × M(k,d) × X(b,k,d) || (3.1)

trong đó Q là mức đơn cơ sở theo hạng chi nhánh, h là hệ số riêng của chi nhánh, w là hệ số ngày trong tuần, ε là nhiễu ngẫu nhiên theo ngày, s là tỷ trọng kênh, L và M là hệ số ngày lễ và ngày mưa theo kênh, X là hệ số thứ hạng trên sàn, chỉ áp dụng cho kênh sàn và được mô tả ở mục 3.3.4. Số đơn thực tế được rút từ phân phối Poisson với kỳ vọng λ, sau đó phân bổ vào các giờ mở cửa theo trọng số giờ. Các tham số được trình bày ở Bảng 3.10.

TABLE: Bảng 3.10. Tham số chính của mô hình nhu cầu
WIDTHS: 4,8
| Tham số | Giá trị |
| Mức đơn cơ sở theo hạng (đơn/ngày) | Hạng A: 380; hạng B: 170; hạng C: 60 (3, 5 và 3 chi nhánh) |
| Tỷ trọng kênh | Tại quầy 55%, ứng dụng riêng 20%, GrabFood 15%, ShopeeFood 10% |
| Hệ số ngày trong tuần (T2 → CN) | 0,92; 0,90; 0,95; 0,98; 1,10; 1,25; 1,20 |
| Ngày lễ | 18/4, 30/4, 1/5, 2/9, 3/9/2024: tại quầy ×1,35; ứng dụng ×1,30; sàn ×1,15 |
| Ngày mưa | Mùa mưa (tháng 5–10) 45% số ngày, mùa khô 8%; tại quầy ×0,75; ứng dụng ×1,20; sàn ×1,25 |
| Giờ mở cửa và cao điểm | 7h–22h; khung 11h–14h và 18h–21h có trọng số gấp ba |
| Số món mỗi đơn | 1, 2, 3, từ 4 món với xác suất 42%, 32%, 16%, 10% (hiệu chỉnh từ dữ liệu thật, mục 3.3.8) |
| Mức độ bán chạy của món | Phân phối Zipf số mũ 1,06 theo thứ hạng món (hiệu chỉnh từ dữ liệu thật, mục 3.3.8) |
| Độ dao động ngẫu nhiên theo ngày | Độ lệch chuẩn 0,075 trên thang logarit (hiệu chỉnh từ dữ liệu thật, mục 3.3.8) |
| Điều chỉnh giá | Ngày 01/06/2024 tăng giá 6 món (căn cứ để xây dựng SCD kiểu 2) |
| Khách hàng ứng dụng | 4.200 khách, tần suất mua theo phân phối dạng Zipf (ít khách mua rất nhiều) |

TODO: ghi nguồn cho các tham số nếu có.

### 3.3.4. Mô hình nhân quả vận hành

Đây là phần thiết kế quan trọng nhất của bộ mô phỏng, tạo ra mối liên hệ giữa nhân sự và doanh thu (Hình 3.4).

Về nhân sự, mỗi nhân viên có một ca ưu tiên, ca sáng từ 6h45 đến 14h hoặc ca tối từ 13h45 đến 22h, và đi làm với xác suất phụ thuộc ngày trong tuần, cao hơn vào cuối tuần. Quản lý chi nhánh luôn gọi người làm bù nếu một ca có ít hơn số nhân viên bếp tối thiểu, lần lượt là 3, 2 và 1 người với chi nhánh hạng A, B và C. Các kịch bản sự cố về nhân sự được áp dụng sau bước này, tức là tình trạng thiếu người do quản lý điều phối sai, không phải do vắng ngẫu nhiên.

IMAGE: figures/h3_3_chuoi_nhan_qua.png || Hình 3.4. Chuỗi nhân quả vận hành trong bộ mô phỏng || 16

Về tải bếp, với mỗi giờ h, mức tải được tính bằng số đơn chia cho năng lực bếp:

EQ: u(h) = Số đơn trong giờ h / ( c(b) × Số nhân viên bếp trong giờ h ) || (3.2)

Năng lực c(b), tính bằng số đơn một nhân viên bếp làm được mỗi giờ, được hiệu chỉnh riêng cho từng chi nhánh sao cho vào giờ cao điểm của ngày đông nhất, nếu ca chỉ có số nhân viên bếp tối thiểu thì tải bằng 95%. Như vậy khi vận hành bình thường, tải giờ cao điểm thường dưới 1 và chỉ vượt 1 khi nhân sự thiếu hụt.

Thời gian chuẩn bị tăng phi tuyến khi tải tiến gần năng lực, theo dạng của mô hình hàng đợi ở mục 2.6, với ρ = min(u, 0,97):

EQ: Thời gian chuẩn bị (phút) = 4 + 6 / (1 − ρ)^0,6 || (3.3)

Quá tải để lại nhiều hệ quả. Khi tải vượt 0,90, một phần khách tại quầy bỏ về, với tỷ lệ 0,60 × (u − 0,90) và tối đa 40%. Đơn của khách bỏ về không xuất hiện trong bất kỳ hệ thống nào; đây là phần doanh thu mất đi mà không để lại dấu vết trực tiếp. Khi tải vượt 0,85, cửa hàng hủy đơn trực tuyến với xác suất 0,006 + 0,30 × (u − 0,85). Khi thời gian chuẩn bị vượt 18 phút, khách đặt trực tuyến tự hủy với xác suất tăng thêm 0,004 cho mỗi phút. Điểm đánh giá mỗi đơn có kỳ vọng 4,7 và giảm 0,05 điểm cho mỗi phút chuẩn bị vượt 15 phút.

Cuối mỗi tuần, điểm đánh giá của cửa hàng trên mỗi sàn được cập nhật theo trung bình trượt có trọng số và bị trừ theo tỷ lệ hủy đơn do cửa hàng:

EQ: R(tuần t) = 0,6 × R(t − 1) + 0,4 × ( Điểm TB tuần t − 2 × Tỷ lệ hủy do cửa hàng ) || (3.4)

Hệ số thứ hạng của tuần sau được tính từ điểm này, giới hạn trong khoảng [0,55; 1,08]:

EQ: X(t + 1) = 1 + 0,8 × ( R(t) − 4,5 ) || (3.5)

Hệ số X nhân trực tiếp vào số đơn kỳ vọng của kênh sàn ở công thức (3.1). Vì vậy một giai đoạn thiếu người làm giảm doanh thu theo hai đường. Đường thứ nhất tác động ngay trong kỳ qua khách bỏ về và đơn bị hủy; đường thứ hai kéo dài nhiều tuần sau kỳ, khi cửa hàng tụt hạng trên sàn rồi hồi phục dần.

### 3.3.5. Mô hình kho

Mỗi buổi sáng từ thứ Hai đến thứ Bảy, hàng tươi được giao, riêng thứ Bảy giao đủ cho cả Chủ nhật; hàng khô được giao vào thứ Hai và thứ Năm. Lượng đặt bằng tiêu hao trung bình bảy ngày gần nhất nhân số ngày cần dự trữ, trừ tồn hiện tại; đơn giá nhập dao động quanh giá chuẩn. Tiêu hao thực tế của mỗi nguyên liệu bằng tiêu hao lý thuyết theo công thức của các món đã làm, nhân với hệ số hao hụt tự nhiên, từ 1,02 đến 1,05 với hàng tươi và từ 1,00 đến 1,02 với hàng khô. Đơn bị hủy trước khi làm không tiêu hao nguyên liệu; đơn bị khách hủy khi đang chờ tiêu hao một nửa. Đơn sàn không được nhập vào POS và hóa đơn bị hủy do gian lận vẫn tiêu hao nguyên liệu. Điều này được thiết kế có chủ đích, để các sự cố P1 và P5 cũng để lại dấu vết chéo ở dữ liệu kho. Kho được kiểm kê vào Chủ nhật, hai tuần một lần.

### 3.3.6. Mô hình lỗi của dữ liệu nguồn

Để phần kỹ thuật dữ liệu phải xử lý các vấn đề có thật, mỗi hệ thống nguồn được thiết kế với các lỗi đặc trưng (Bảng 3.11). Các lỗi này được chọn theo những tình huống phổ biến khi dữ liệu do nhiều phần mềm khác nhau tạo ra hoặc do con người ghi tay.

TABLE: Bảng 3.11. Các lỗi dữ liệu đặc trưng của từng hệ thống nguồn
WIDTHS: 2,7,3
| Hệ thống | Lỗi được mô phỏng | Chiều chất lượng |
| POS | Ba chi nhánh dùng phiên bản phần mềm cũ: ngày giờ dạng ISO thay vì dd/mm/yyyy, số tiền là chuỗi có dấu chấm ngăn cách hàng nghìn (“125.000”), cột tổng tiền mang tên khác, thiếu bốn trường | Nhất quán, hợp lệ |
| POS | Tên món trên hóa đơn có nhiều biến thể; khoảng 3% đơn sàn không được nhập; một số bản ghi đồng bộ lỗi | Nhất quán, đầy đủ |
| Ứng dụng | Thời gian theo giờ UTC; mã chi nhánh, mã món khác hệ thống trụ sở; tên món tiếng Việt có dấu | Nhất quán |
| GrabFood | Tên cửa hàng nhập tự do; ngày dạng “19 Mar 2024”; không có tỷ lệ hoa hồng | Nhất quán |
| ShopeeFood | Tệp Excel có dòng tiêu đề trước bảng; tiêu đề cột tiếng Việt; mã cửa hàng khác | Biểu diễn, nhất quán |
| Sổ nhập kho | Hai mẫu: mẫu A có tiêu đề phiếu, tên tiếng Việt có dấu, đơn vị “quả/lít”, dòng “Tổng cộng”; mẫu B tiếng Anh không dấu, số lượng dính đơn vị (“53.6kg”); khoảng 5% tên nguyên liệu viết tắt; khoảng 0,5% số lượng gõ theo gam vào cột kilôgam | Hợp lệ, nhất quán |
| Phiếu kiểm kê | Sai số đếm tay khoảng ±2%; khoảng 2% ô bỏ trống ghi “chưa đếm” | Chính xác, đầy đủ |
| Máy chấm công | Khoảng 6% lượt quẹt vào bị máy ghi trùng, tức khoảng 3% tổng số lượt quẹt; khoảng 5% ca thiếu lượt quẹt ra | Duy nhất, đầy đủ |

### 3.3.7. Thiết kế kịch bản sự cố và tập đánh giá

Các sự cố được đưa vào thế giới, không đưa vào từng file, nên mỗi sự cố tự động để lại dấu vết ở mọi nguồn liên quan. Khóa luận thiết kế hai tập kịch bản độc lập (Bảng 3.12). Mỗi tập có hạt giống ngẫu nhiên riêng, sự cố rơi vào các chi nhánh và thời điểm khác nhau. Tập kiểm tra cố ý khó hơn: mức độ sự cố nhẹ hơn, một số rơi vào chi nhánh nhỏ, nơi có ít dữ liệu hơn, và vào sàn khác.

TABLE: Bảng 3.12. Hai tập kịch bản sự cố
WIDTHS: 4,6,6
| Vấn đề | Tập phát triển | Tập kiểm tra |
| P1a. Sàn tính sai hoa hồng | S1: CN4, GrabFood, 13/5–2/6; 30% thay vì 25% | H1: CN10, ShopeeFood, 5/8–18/8; 26% thay vì 22% |
| P1b. Đơn sàn không nhập POS | S2: CN6, 15/7–28/7; 20% đơn | H2: CN3, 22/4–5/5; 15% đơn |
| P2. Hao hụt nguyên liệu tươi | S3: CN7, 10/4–20/4; hao hụt ×1,15–1,30 | H3: CN1, 3/6–14/6; ×1,12–1,25 |
| P3. Thiếu nhân sự ca tối | S4: CN2, 6/5–19/5; điều 55% nhân viên ca tối sang ca sáng | H4: CN8, 22/7–31/7; điều 45% |
| P4. Thất thoát kho | S5: CN9, 17/6–30/6; mất 1,5%/ngày tồn thịt, tôm, phô mai | H5: CN5, 12/8–25/8; mất 1,2%/ngày |
| P5. Gian lận tại quầy | S6: CN8, 1/7–28/7; một thu ngân hủy 12% hóa đơn tiền mặt sau khi thu tiền | H6: CN10, 1/4–28/4; tỷ lệ 10% |

Quy tắc sử dụng hai tập được áp dụng chặt chẽ: mọi lựa chọn về phương pháp, cửa sổ thời gian và ngưỡng của các bộ phát hiện chỉ được thực hiện trên tập phát triển. Tập kiểm tra chỉ được chạy một lần khi các bộ phát hiện đã được cố định. Trong quá trình xây dựng chỉ có một điều chỉnh đối với tập kiểm tra. Kịch bản H6 ban đầu đặt ở chi nhánh nhỏ nhất trong ba tuần chỉ tạo ra ba hóa đơn gian lận, quá ít để bất kỳ phương pháp nào có thể phân biệt với nhiễu, nên được chuyển sang một chi nhánh hạng B trong bốn tuần. Điều chỉnh này dựa trên độ lớn của tác động mà bộ mô phỏng tạo ra, được thực hiện trước khi xây dựng bất kỳ bộ phát hiện nào, nên không ảnh hưởng đến tính độc lập của đánh giá.

### 3.3.8. Hiệu chỉnh tham số bằng dữ liệu giao dịch thật công khai

Dữ liệu đơn hàng và hóa đơn chi tiết của một chuỗi F&B nằm trong hệ thống nội bộ của doanh nghiệp, không được công bố và không thể thu thập hợp pháp từ bên ngoài. Tuy nhiên, các quy luật thống kê của hành vi mua hàng, như số món trong một đơn hay mức độ tập trung vào vài món bán chạy, có thể được ước lượng từ các bộ dữ liệu giao dịch thật đã được công bố công khai dưới dạng ẩn danh. Việc ước lượng phân phối đầu vào của mô hình mô phỏng từ dữ liệu quan sát được gọi là mô hình hóa dữ liệu đầu vào (input modeling), là một bước tiêu chuẩn trong phương pháp mô phỏng (Law, 2015). Khóa luận áp dụng bước này để thay thế một phần các giả định bằng các tham số có căn cứ dữ liệu.

Bộ dữ liệu tham chiếu phải đồng thời (1) là giao dịch thật, không phải của doanh nghiệp giả định; (2) thuộc loại hình bán đồ ăn, thức uống tại quầy; (3) có thông tin từng giao dịch, gồm thời điểm và các món; (4) có giấy phép cho phép sử dụng. Không có bộ dữ liệu công khai nào về chuỗi đồ ăn nhanh tại Việt Nam; nhiều bộ “đơn hàng nhà hàng” phổ biến được mô tả rõ là của nhà hàng giả định dùng để luyện tập, nên bị loại theo tiêu chí (1).

Bộ dữ liệu được chọn là The Bread Basket, gồm các giao dịch thật của một tiệm bánh tại Edinburgh (Vương quốc Anh), được công bố trên kho dữ liệu mở OpenML (mã 43422) với giấy phép CC0 (phạm vi công cộng) (Vanschoren và cộng sự, 2013). Sau khi đọc và làm sạch, bộ dữ liệu có 9.465 giao dịch trong 159 ngày hoạt động, từ 30/10/2016 đến 09/4/2017, mỗi dòng là một món trong một giao dịch kèm thời điểm. Chương trình `simulator/calibrate_public.py` thực hiện toàn bộ việc ước lượng và lưu kết quả để tái lập.

Riêng độ dao động theo ngày cần được ước lượng cẩn thận. Độ lệch chuẩn thô của logarit số giao dịch mỗi ngày (sau khi loại hệ số ngày trong tuần) là 0,381. Con số này không phản ánh đúng độ dao động ngẫu nhiên giữa các ngày, vì nó gồm cả xu hướng mùa đông, kỳ nghỉ cuối năm và nhiễu do quy mô nhỏ, trung bình chỉ 59,5 giao dịch mỗi ngày. Vì vậy độ dao động được ước lượng lại theo ba bước: loại xu hướng bằng trung vị trượt 28 ngày; dùng ước lượng vững dựa trên độ lệch tuyệt đối trung vị (1,4826 × MAD) để giảm ảnh hưởng của các ngày bất thường; và trừ đi phần phương sai do bản chất ngẫu nhiên Poisson của số giao dịch, xấp xỉ 1/λ̄ trên thang logarit:

EQ: σ²(thêm) = σ²(vững) − 1 / λ̄ || (3.6)

Kết quả σ(thêm) = 0,075, rất gần với giá trị 0,08 mà bộ mô phỏng đã giả định trước đó. Như vậy giả định ban đầu được dữ liệu thật xác nhận.

TABLE: Bảng 3.13. Kết quả hiệu chỉnh tham số từ dữ liệu giao dịch thật
WIDTHS: 3.2,2.6,2.4,2.4,4.4
| Quy luật thống kê | Dữ liệu thật | Giả định trước | Sau hiệu chỉnh | Chuyển giao sang bộ mô phỏng? |
| Số món khác nhau mỗi đơn (1 / 2 / 3 / ≥4) | 41,7% / 32,3% / 15,5% / 10,4% | 55% / 30% / 12% / 3% | 42% / 32% / 16% / 10% | Có. Hành vi chọn món tại quầy (món chính kèm đồ uống, đồ ăn kèm) tương đồng giữa các loại hình phục vụ nhanh |
| Số lượng mỗi dòng món (1 / 2) | 92% / 8% | 90% / 10% | 92% / 8% | Có |
| Độ tập trung món bán chạy | Món đầu chiếm 26,7% số phần, 5 món đầu 59,1%; dạng Zipf số mũ 1,06 | Gần như đồng đều giữa các món | Zipf số mũ 1,06 (món đầu 27,7%, 5 món đầu 60,9%) | Có, chỉ lấy độ dốc của phân phối; thứ tự món bán chạy là giả định của tác giả |
| Độ dao động ngẫu nhiên theo ngày | 0,075 (công thức 3.6) | 0,08 | 0,075 | Có; xác nhận giả định ban đầu |
| Hệ số ngày trong tuần | Thứ Bảy 1,51; Chủ nhật 0,92 | Thứ Bảy 1,20; Chủ nhật 1,15 | Giữ giả định | Không. Tiệm bánh ở khu du lịch có nhịp cuối tuần khác hẳn chuỗi đồ ăn nhanh phục vụ gia đình tại Việt Nam |
| Phân bố theo giờ | Cao điểm 10h–13h, gần như không bán sau 17h | Hai cao điểm trưa và tối | Giữ giả định | Không. Tiệm bánh đóng cửa chiều, không có bữa tối |

Tính chuyển giao được xét cho từng quy luật. Chỉ các quy luật phản ánh hành vi mua hàng chung của loại hình bán tại quầy mới được đưa vào, còn các quy luật phụ thuộc giờ mở cửa, văn hóa ăn uống và vị trí thì giữ nguyên giả định, kèm lý do. Các tham số còn lại ở Bảng 3.10 và mục 3.3.4 vẫn là giả định của tác giả.

### 3.3.9. Giả định và giới hạn của bộ mô phỏng

Ngoài các tham số đã được hiệu chỉnh ở mục 3.3.8, các tham số hành vi như hệ số ngày lễ, mức giảm khách tại quầy khi mưa, độ dốc của tỷ lệ hủy theo tải và trọng số cập nhật điểm đánh giá là các giả định hợp lý của tác giả, phản ánh đúng chiều tác động đã biết trong thực tiễn, nhưng chưa được hiệu chỉnh bằng dữ liệu quan sát thật. Quy mô nhân sự và lương giờ lấy từ danh mục nhân viên của chuỗi giả định, nên tỷ lệ chi phí nhân công khác nhau đáng kể giữa các hạng chi nhánh. Bộ mô phỏng chưa mô hình hóa tình trạng hết hàng dẫn đến hủy đơn, biến động giá nhà cung cấp theo mùa, lịch phân ca kế hoạch và dữ liệu đối chiếu két tiền. Các giới hạn này được thảo luận lại ở Chương 5 và Chương 6.

Hai giả định khác giới hạn các phân tích có thể làm trên dữ liệu này. Thứ nhất, nhu cầu trong ngày được mô hình hóa đơn giản: các giờ cao điểm trưa và tối có trọng số gấp ba các giờ còn lại, và nhân viên chỉ làm theo hai ca cố định sáng và tối, không có ca lệch hay nhân viên bán thời gian cho giờ cao điểm như cách các chuỗi đồ ăn nhanh thường xếp ca. Vì vậy dữ liệu đủ để đánh giá số ca theo ngày và theo buổi, nhưng không dùng để phân tích hay đề xuất phân ca theo từng giờ, vì kết quả khi đó chỉ phản ánh lại giả định của bộ mô phỏng. Thứ hai, khách hàng của ứng dụng được chọn ngẫu nhiên theo một phân phối cố định suốt kỳ dữ liệu, không có khách rời bỏ, không có khách quay lại nhiều hơn hay ít hơn sau trải nghiệm tốt, xấu hay sau khuyến mãi. Dữ liệu khách hàng vì vậy chỉ dùng để nhận diện khách mua lần đầu, không dùng để phân tích giữ chân khách hay phân khúc RFM.

## 3.4. Thiết kế đường ống dữ liệu

### 3.4.1. Tổng quan luồng dữ liệu

Đường ống dữ liệu đưa dữ liệu từ các hệ thống nguồn qua bốn chặng: tầng thu thập nhận và kiểm tra tệp, tầng Bronze lưu bản gốc, tầng Silver làm sạch và chuẩn hóa, tầng Gold tổ chức lại cho phân tích. Mỗi chặng có một trách nhiệm riêng và không làm thay việc của chặng sau, nhờ đó khi một quy tắc làm sạch thay đổi chỉ cần chạy lại từ Bronze mà không phải thu thập lại dữ liệu. Hình 3.5 thể hiện luồng này; các mục 3.4.2 đến 3.4.5 trình bày thiết kế của từng chặng tới hết tầng Silver, còn tầng Gold được trình bày ở mục 3.5.

IMAGE: figures/h3_4_luong_tang.png || Hình 3.5. Luồng dữ liệu qua các tầng Bronze, Silver, Gold || 16

### 3.4.2. Tầng thu thập

Dữ liệu vận hành của một chuỗi F&B không đến bằng một đường. POS bán theo thuê bao giữ hóa đơn trên máy chủ của nhà cung cấp và mở API; POS cài tại máy và máy chấm công xuất tệp theo lịch; báo cáo đối soát sàn do kế toán tải từ cổng đối tác; sổ kho và phiếu kiểm kê do quản lý cửa hàng điền vào Excel. Tầng thu thập được thiết kế theo bốn nguyên tắc.

- Ba kênh dùng chung một vùng tiếp nhận. Bộ kết nối API, tệp xuất tự động và trang tải lên đều ghi vào cùng một vùng tiếp nhận, mỗi nguồn một thư mục. Từ đây mọi nguồn đi chung một đường ống, nên phần phía sau không phụ thuộc vào việc dữ liệu đến bằng kênh nào.
- Mỗi nguồn có một hợp đồng dữ liệu, khai báo định dạng, cột hoặc khóa bắt buộc và cách đọc chi nhánh, ngày từ nội dung. Tệp được nhận dạng theo nội dung chứ không theo tên; tệp sai hợp đồng, không đọc được hoặc không thuộc nguồn nào bị từ chối kèm lý do, không bị bỏ qua im lặng.
- Dữ liệu được kéo tăng dần theo mốc. Bộ kết nối lưu ngày kinh doanh cuối cùng đã lấy đủ, mỗi lượt lấy các ngày sau mốc và lấy lại chính ngày mốc để nhận hóa đơn đồng bộ trễ, đối chiếu số bản ghi với tổng do API báo rồi mới dời mốc.
- Lỗi của một nguồn không làm dừng các nguồn khác. Lỗi tạm thời được thử lại với thời gian chờ tăng dần; API không phản hồi không chặn các nguồn tệp. Phần dữ liệu thiếu được cửa chặn chất lượng phát hiện như mô tả ở mục 3.8, và bộ phát hiện không kết luận sự cố trên phần đó theo mục 3.7.3.

Hình 3.6 mô tả hoạt động tiếp nhận một lần gửi tệp. Điểm chính của thiết kế là thứ tự kiểm tra. Tệp phải khớp hợp đồng dữ liệu trước khi được tính vị trí chuẩn, rồi mới được so với tệp đang có ở vị trí đó để phân biệt bản sửa với bản gửi trùng. Một tệp có nội dung giống hệt tệp khác nhưng rơi vào vị trí khác, chẳng hạn gửi nhầm tên ngày, bị từ chối vì nạp thêm sẽ làm doanh thu hoặc lượng nhập kho bị đếm hai lần. Mọi kết quả, kể cả từ chối, đều được ghi vào nhật ký tiếp nhận.

IMAGE: figures/h3_act_tiep_nhan.png || Hình 3.6. Sơ đồ hoạt động tiếp nhận tệp do người gửi || 16

Hình 3.7 mô tả tương tác của bộ kết nối với API nguồn trong một lượt kéo. Bộ kết nối đọc mốc ngày, hỏi API danh sách ngày đã có, rồi lấy từng ngày theo trang. Lỗi tạm thời và lỗi vượt giới hạn tần suất được xử lý bằng cách chờ tăng dần rồi gọi lại. Chỉ khi số bản ghi nhận được khớp với tổng số API báo, dữ liệu của ngày đó mới được ghi vào vùng tiếp nhận và mốc mới được dời. Nhờ vậy, một lượt bị gián đoạn giữa chừng sẽ làm tiếp đúng từ ngày chưa lấy đủ.

IMAGE: figures/h3_seq_api.png || Hình 3.7. Sơ đồ tuần tự của bộ kết nối khi kéo dữ liệu qua API nguồn || 16

Hiện thực của từng nguyên tắc được trình bày ở mục 4.3.

### 3.4.3. Tầng Bronze

Tầng Bronze cũng được thiết kế theo bốn nguyên tắc.

- Giữ nguyên giá trị gốc. Mọi giá trị được lưu dưới dạng chuỗi ký tự; bản ghi JSON được lưu nguyên văn trong một cột `payload`. Bronze không ép kiểu, không đổi định dạng, không loại bỏ dòng nào, kể cả dòng “Tổng cộng” trong sổ kho. Mọi quyết định làm sạch thuộc về tầng Silver, để khi quy tắc thay đổi có thể xử lý lại từ bản gốc.
- Bổ sung siêu dữ liệu truy vết. Mỗi dòng có tệp nguồn (`_source_file`), mã băm nội dung tệp (`_file_hash`), số thứ tự dòng trong tệp (`_row_number`), mã lô nạp (`_batch_id`) và thời điểm nạp (`_ingested_at`). Với tệp Excel dạng phiếu, các dòng tiêu đề phía trên bảng như tên chi nhánh, ngày, người lập được giữ trong các cột `_doc_line_k`.
- Nạp tăng dần và lũy đẳng. Bảng nhật ký `bronze._ingest_log` ghi lại mọi tệp đã xử lý cùng mã băm MD5. Tệp đã nạp với cùng nội dung bị bỏ qua; tệp bị sửa thì bản cũ được xóa và nạp lại; tệp không đọc được, tệp sai hợp đồng dữ liệu và tệp không thuộc nguồn nào được ghi nhận với trạng thái và lý do riêng mà không làm dừng các tệp khác.
- Ghi theo giao dịch của từng nguồn. Dữ liệu và nhật ký của mỗi nguồn được ghi trong cùng một giao dịch, nên lỗi giữa chừng không để lại dữ liệu dở dang.

Hai mẫu sổ nhập kho khác nhau được nạp vào hai bảng Bronze riêng; việc hợp nhất là trách nhiệm của tầng Silver. Kết quả nạp các bảng Bronze được trình bày ở mục 4.3.4.

### 3.4.4. Tầng Silver

Tầng Silver chuyển mỗi bảng Bronze thành một hoặc nhiều bảng sạch, đúng kiểu dữ liệu, đúng đơn vị và gắn với định danh chuẩn của hệ thống trụ sở. Các quy tắc chính được tóm tắt ở Bảng 3.14.

TABLE: Bảng 3.14. Quy tắc làm sạch và chuẩn hóa chính ở tầng Silver
WIDTHS: 2,7,4
| Nguồn | Xử lý | Dòng vi phạm |
| POS | Hợp nhất hai phiên bản lược đồ: nhận diện định dạng ngày giờ, chuyển “125.000” thành số, đổi tên cột tổng tiền; tách mảng món thành bảng dòng món; xác định chi nhánh từ tiền tố máy POS, nhân viên từ mã thu ngân; giữ lại hóa đơn hủy, hoàn tiền và gắn cờ | Thiếu hoặc trùng số hóa đơn, thời gian hoặc tổng tiền không đọc được, tổng tiền âm, không xác định được chi nhánh, hóa đơn không có món → cách ly |
| Ứng dụng | Đổi UTC sang giờ Việt Nam (UTC+7), xác định lại ngày theo giờ địa phương; ánh xạ mã chi nhánh; ánh xạ món qua tên đã chuẩn hóa; tính thời gian chuẩn bị | Không ánh xạ được món hoặc chi nhánh → cách ly |
| GrabFood, ShopeeFood | Hợp nhất hai định dạng báo cáo về một lược đồ chung; tách ngày đầu tuần từ chuỗi kỳ báo cáo; ánh xạ tên/mã cửa hàng về chi nhánh; tính tỷ lệ hoa hồng hiệu dụng | Không ánh xạ được cửa hàng → cách ly |
| Sổ nhập kho | Hợp nhất hai mẫu; tách dòng tổng cộng, dòng chữ ký ra khỏi dòng dữ liệu; lấy ngày và chi nhánh từ dòng tiêu đề phiếu hoặc đường dẫn tệp; tách số lượng và đơn vị; chuẩn hóa đơn vị; ánh xạ tên nguyên liệu (mục 3.4.5) | Số lượng lớn hơn 20 lần trung vị của cùng nguyên liệu (nghi gõ gam vào cột kg) → cách ly |
| Phiếu kiểm kê | Lấy ngày, chi nhánh từ tiêu đề; ánh xạ mã nguyên liệu; ô trống giữ là giá trị thiếu kèm cờ, không thay bằng 0 | — |
| Chấm công | Ánh xạ mã nhân viên; ghép cặp vào – ra theo nhân viên và ngày; ca thiếu lượt ra được gắn cờ, không tự gán số giờ ở tầng Silver | Lượt quẹt cùng loại lặp lại trong vòng 5 phút (máy ghi trùng) → cách ly |
| Danh mục | Xây dựng lịch sử hiệu lực từ các ảnh chụp danh mục (giá món, vai trò và lương nhân viên) | — |

Bảng cách ly `silver.silver_quarantine` lưu mọi dòng bị loại cùng nguồn, tệp, số dòng gốc và quy tắc vi phạm, để kỹ sư dữ liệu xem xét. Bảng `silver.silver_row_reconciliation` đối soát cho từng nguồn: số dòng Bronze phải bằng số dòng Silver cộng số dòng bị cách ly cộng số dòng cấu trúc (dòng tổng cộng, chữ ký); phần chênh lệch không giải thích được phải bằng 0.

### 3.4.5. Giải quyết định danh thực thể

Cùng một thực thể được gọi theo nhiều cách ở các hệ thống khác nhau (Bảng 3.15).

TABLE: Bảng 3.15. Các hệ thống định danh và cách giải quyết
WIDTHS: 2,7,4
| Thực thể | Cách gọi ở các hệ thống (ví dụ chi nhánh 1, nhân viên 12) | Cách giải quyết |
| Chi nhánh | Trụ sở: 1; POS: `POS-01-…`; ứng dụng: `FNF-Q3-01`; GrabFood: “Fast&Fat - District 3 (#1)”; ShopeeFood: `FASTFAT_DISTRICT3_01`; chấm công: `BR01`; sổ kho: tên chi nhánh trong tiêu đề phiếu | Bảng ánh xạ do người hiểu nghiệp vụ duy trì (11 chi nhánh, ổn định) |
| Nhân viên | Trụ sở và chấm công: 12; POS: `NV0012` | Quy tắc chuẩn hóa xác định |
| Món | Trụ sở: mã 1, tên không dấu; POS: `SKU-001`; ứng dụng: mã riêng và tên tiếng Việt có dấu | POS: quy tắc; ứng dụng: so khớp tên sau khi bỏ dấu, chuẩn hóa |
| Nguyên liệu | Trụ sở: mã 1 và tên không dấu; sổ kho mẫu A: tên có dấu, đôi khi viết tắt (“Gà tươi”); mẫu B: tên không dấu; phiếu kiểm kê: mã `NL01` | Ba tầng: chuẩn hóa (bỏ dấu, chữ thường) rồi khớp chính xác → bảng ánh xạ biến thể do người hiểu nghiệp vụ lập → khớp mờ Jaro–Winkler với ngưỡng 0,9; không khớp được thì cách ly |

## 3.5. Thiết kế kho dữ liệu

### 3.5.1. Ma trận bus

Kho dữ liệu được thiết kế theo phương pháp Kimball với sáu quy trình nghiệp vụ, dùng chung các chiều đồng nhất (Bảng 3.16).

TABLE: Bảng 3.16. Ma trận bus của kho dữ liệu
WIDTHS: 4.2,1.1,1.45,1.3,1.1,1.7,1.5,1.6
| Quy trình nghiệp vụ (bảng sự kiện) | Ngày | Chi nhánh | Kênh | Món | Nguyên liệu | Nhân viên | Khách hàng |
| Bán hàng – đơn (`fact_order`) | x | x | x | | | x | x |
| Bán hàng – dòng món (`fact_order_line`) | x | x | x | x | | | |
| Đối soát sàn (`fact_marketplace_​settlement`) | x | x | x | | | | |
| Nhập kho (`fact_inventory_receipt`) | x | x | | | x | | |
| Kiểm kê (`fact_stock_count`) | x | x | | | x | | |
| Ca làm việc (`fact_labor_shift`) | x | x | | | | x | |

### 3.5.2. Bảng sự kiện và hạt dữ liệu

TABLE: Bảng 3.17. Các bảng sự kiện, hạt dữ liệu và đo lường
WIDTHS: 4.2,2.3,3.5,5
| Bảng sự kiện | Loại | Hạt dữ liệu | Đo lường chính |
| `fact_order` | Giao dịch | Một đơn hàng ở một kênh | Tạm tính, giảm giá, tổng tiền, cờ hủy/hoàn/hủy do cửa hàng, thời gian chuẩn bị, phút từ lúc thanh toán đến lúc hủy |
| `fact_order_line` | Giao dịch | Một dòng món trong một đơn | Số lượng, đơn giá, thành tiền, giá vốn lý thuyết theo định mức tại ngày bán |
| `fact_marketplace_​settlement` | Ảnh chụp định kỳ | Một chi nhánh × một sàn × một tuần | Doanh thu món, số đơn, đơn hủy, hoa hồng, tỷ lệ hiệu dụng, tỷ lệ hợp đồng, khuyến mãi, quảng cáo, thực nhận, thời gian chuẩn bị, điểm đánh giá |
| `fact_inventory_receipt` | Giao dịch | Một dòng phiếu nhập | Số lượng (đơn vị chuẩn), đơn giá, thành tiền, hạn sử dụng |
| `fact_stock_count` | Ảnh chụp định kỳ | Một chi nhánh × một nguyên liệu × một kỳ kiểm kê | Tồn đếm được, cờ thiếu số liệu |
| `fact_labor_shift` | Giao dịch | Một nhân viên × một ca | Giờ vào, giờ ra, số giờ, cờ thiếu lượt ra, chi phí nhân công theo lương tại ngày làm |

### 3.5.3. Bảng chiều và chiều thay đổi chậm

- `dim_date`: ngày, thứ, cuối tuần, ngày lễ (tên lễ), tuần, tháng, và thông tin thời tiết của ngày (mưa, lượng mưa). Thời tiết được gắn vào chiều ngày vì áp dụng chung cho toàn thành phố.
- `dim_branch`: mã chi nhánh, tên, quận, hạng, tọa độ, ngày khai trương và toàn bộ mã của chi nhánh ở các hệ thống nguồn.
- `dim_channel`: tại quầy, ứng dụng riêng, GrabFood, ShopeeFood.
- `dim_menu_item` (SCD kiểu 2): mã món, tên, nhóm, giá bán, giá vốn chuẩn, ngày bắt đầu và kết thúc hiệu lực, cờ bản hiện hành.
- `dim_ingredient`: mã, tên chuẩn, đơn vị, nhóm hàng tươi/khô, hạn dùng, đơn giá chuẩn.
- `dim_employee` (SCD kiểu 2): mã nhân viên, tên, chi nhánh, vai trò, lương giờ, khoảng hiệu lực.
- `dim_customer`: mã khách hàng (đã băm), ngày mua đầu tiên.

Các bảng sự kiện liên kết với `dim_menu_item` và `dim_employee` theo phiên bản có hiệu lực tại ngày phát sinh giao dịch, nhờ đó giá vốn lý thuyết và chi phí nhân công được tính đúng cả trước và sau các lần điều chỉnh.

Lịch sử của hai chiều SCD kiểu 2 được dựng từ chuỗi ảnh chụp danh mục có ghi ngày mà trụ sở xuất định kỳ, không dùng chức năng *snapshot* của dbt. Snapshot của dbt ghi lại trạng thái bảng nguồn tại thời điểm đường ống chạy, nên lịch sử phụ thuộc vào việc đường ống đã chạy vào những ngày nào và mất đi khi kho được dựng lại từ đầu. Ảnh chụp có ngày cho cùng một lịch sử mỗi lần dựng lại, phù hợp với chiến lược cập nhật ở mục 3.5.5 và yêu cầu tái lập NFR1. Nếu hệ thống nguồn chỉ cung cấp trạng thái hiện tại mà không lưu ảnh chụp, snapshot của dbt mới là lựa chọn phù hợp.

### 3.5.4. Sơ đồ quan hệ

IMAGE: figures/h3_5_erd.png || Hình 3.8. Sơ đồ quan hệ thực thể của kho dữ liệu (lược đồ hình sao), sinh từ metadata dbt || 16

### 3.5.5. Chiến lược cập nhật kho dữ liệu

Ở các kho dữ liệu lớn, bảng thường được cập nhật tăng dần: mỗi lượt chỉ tính phần dữ liệu mới rồi gộp vào bảng cũ theo khóa. Khóa luận chọn cách khác cho tầng Silver và Gold: mỗi lượt chạy dựng lại toàn bộ các bảng từ Bronze, trừ hai mô hình giải mã JSON của POS và App. Lựa chọn này dựa trên ba lý do.

Thứ nhất, hệ thống nguồn được phép sửa lùi. Phiếu kiểm kê đếm lại hay báo cáo sàn gửi bản điều chỉnh được nạp thay bản cũ ở Bronze (mục 3.4.2). Nếu Silver gộp theo khóa, những dòng có trong bản cũ nhưng không còn trong bản mới vẫn nằm lại trong kho. Thứ hai, bảng chỉ số dùng cửa sổ trượt tám tuần và so sánh giữa các chi nhánh cùng tuần, nên một ngày dữ liệu mới hay một tệp sửa lùi làm thay đổi kết quả của nhiều tuần trước đó; tính tăng dần đúng cho các bảng này phức tạp hơn nhiều so với lợi ích thu được. Thứ ba, ở quy mô khoảng nửa triệu dòng mỗi tập dữ liệu, một lượt dựng lại chỉ mất từ 15 đến 25 giây (mục 4.5.2), và kết quả luôn là một hàm xác định của dữ liệu Bronze hiện có nên dễ kiểm chứng.

Hai mô hình giải mã là ngoại lệ vì đây là bước tốn thời gian nhất và mỗi tệp được giải mã độc lập với các tệp khác. Chúng chạy tăng dần theo thời điểm nạp, với khóa là tệp nguồn: khi một tệp được gửi lại bản sửa, toàn bộ dòng của tệp đó bị xóa rồi giải mã lại, nên vẫn đúng khi nguồn sửa lùi. Như vậy, yêu cầu NFR2 được đáp ứng ở bước nạp Bronze và bước giải mã, là hai bước có chi phí tăng theo lượng dữ liệu; Silver và Gold không xử lý tăng dần nhưng vẫn lũy đẳng, vì chạy lại cho đúng cùng kết quả. Khi dữ liệu tăng tới mức một lượt dbt mất vài phút, hướng chuyển đổi là cập nhật tăng dần theo ngày nghiệp vụ: mỗi lượt xóa rồi tính lại các ngày có tệp mới hoặc tệp sửa, cộng thêm một khoảng lùi đủ phủ cửa sổ tám tuần.

## 3.6. Thiết kế kiểm soát chất lượng dữ liệu

Kiểm soát chất lượng dữ liệu được thiết kế thành bốn lớp nối tiếp nhau trên đường đi của dữ liệu. Lớp thứ nhất là hợp đồng dữ liệu ở tầng thu thập, loại các tệp sai cấu trúc trước khi nạp (mục 3.4.2). Lớp thứ hai là cửa chặn chất lượng đầu vào, kiểm tra cả lô vừa nạp vào Bronze về độ mới, khối lượng, độ đầy đủ theo chi nhánh và thay đổi cấu trúc trước khi dbt chạy (mục 3.8). Lớp thứ ba là quy tắc ở tầng Silver: dòng vi phạm, chẳng hạn tổng tiền âm hay số lượng nhập nghi gõ gam vào cột kilôgam, bị cách ly kèm lý do (Bảng 3.14). Lớp thứ tư là kiểm thử dbt chạy trên kết quả của Silver và Gold sau mỗi lần dựng.

Kiểm thử dbt được tổ chức theo cách dbt khuyến nghị. Các ràng buộc phổ biến như khóa duy nhất, không rỗng, toàn vẹn tham chiếu, miền giá trị dùng kiểm thử dựng sẵn của dbt, khai báo trong tệp cấu hình của mô hình. Ràng buộc khóa ghép, không có sẵn trong dbt, được viết thành một kiểm thử tổng quát bằng macro để dùng lại cho mọi bảng chỉ số. Các luật nghiệp vụ riêng của bài toán, như bảo toàn số dòng hay khớp số tiền, được viết thành kiểm thử dạng câu SQL (*singular test*): câu truy vấn trả về các dòng vi phạm và kiểm thử đạt khi kết quả rỗng. Bảng 3.18 tóm tắt các nhóm kiểm thử và lớp hiện thực tương ứng.

TABLE: Bảng 3.18. Các nhóm kiểm thử chất lượng dữ liệu
WIDTHS: 2.8,6.6,3.6,2
| Nhóm kiểm thử | Nội dung kiểm tra | Cách hiện thực | Chiều chất lượng |
| Khóa | Khóa của mọi bảng Silver và Gold không trùng, không rỗng; bảng chỉ số không trùng tổ hợp khóa, ví dụ chi nhánh × ngày; mỗi chi nhánh × tuần chỉ có một dòng đối soát GrabFood | Kiểm thử dựng sẵn `unique`, `not_null`; kiểm thử tổng quát khóa ghép viết bằng macro; một kiểm thử SQL | Duy nhất, đầy đủ |
| Toàn vẹn tham chiếu | Mọi khóa chi nhánh, món, nguyên liệu, nhân viên trong bảng sự kiện tồn tại ở bảng chiều | Kiểm thử dựng sẵn `relationships` | Nhất quán |
| Miền giá trị | Trạng thái đơn, kênh bán, phiên bản POS, loại lượt chấm công, tên ca, hạng chi nhánh, tên sàn và cách khớp tên nguyên liệu thuộc danh sách cho phép | Kiểm thử dựng sẵn `accepted_values` | Hợp lệ |
| Bảo toàn số dòng | Với mọi nguồn, số dòng Bronze bằng số dòng Silver cộng số dòng cách ly cộng số dòng cấu trúc | Kiểm thử SQL trên bảng đối soát số dòng | Đầy đủ |
| Nhất quán số tiền | Tạm tính hóa đơn POS bằng tổng các dòng món; tiền thực nhận ở báo cáo hai sàn khớp công thức của chính báo cáo; doanh thu thuần ở Gold bằng tổng tính từ Silver theo chi nhánh × ngày | Kiểm thử SQL | Chính xác |
| Lịch sử chiều | Các phiên bản của cùng một món, cùng một nhân viên không chồng lấn, không hở thời gian | Kiểm thử SQL | Nhất quán |
| Độ mới | Ngày dữ liệu mới nhất của mỗi nguồn không cũ hơn ngưỡng: một ngày với dữ liệu ngày, tám ngày với dữ liệu tuần, mười lăm ngày với phiếu kiểm kê | Cửa chặn chất lượng đầu vào, chạy trước dbt | Kịp thời |
| Đầy đủ theo chi nhánh | Mỗi ngày trong lô vừa nạp, chi nhánh thường gửi tệp POS, chấm công mà ngày đó thiếu hoặc tệp rỗng thì cảnh báo; từ một phần ba số chi nhánh trở lên cùng thiếu thì chặn | Cửa chặn chất lượng đầu vào, chạy trước dbt | Đầy đủ |

Hai nhóm cuối không viết bằng dbt vì chúng phải chạy trên Bronze trước khi dbt dựng lại kho: nếu lô vừa nạp thiếu dữ liệu nghiêm trọng, đường ống dừng lại và kho phục vụ giữ nguyên bản trước, thay vì đưa ra kết quả sai.

## 3.7. Thiết kế lớp phân tích

### 3.7.1. Các chỉ số vận hành

Các chỉ số được tính sẵn trong năm bảng chỉ số (mart) của tầng Gold: `mart_branch_daily` (chi nhánh × ngày), `mart_branch_weekly` (chi nhánh × tuần, kèm số liệu đối soát sàn), `mart_ingredient_avt` (chi nhánh × nguyên liệu × kỳ kiểm kê), `mart_cashier_weekly` (thu ngân × tuần) và `mart_kpi_vs_peers_weekly` (chi nhánh × tuần × chỉ số, kèm mức kỳ vọng và điểm bất thường). Định nghĩa các chỉ số chính được trình bày ở Bảng 3.19.

TABLE: Bảng 3.19. Định nghĩa các chỉ số vận hành trong kho dữ liệu
WIDTHS: 3,6,3
| Chỉ số | Cách tính | Nguồn (bảng Gold) |
| Doanh thu thuần theo kênh | Tiền món sau giảm giá của các đơn hoàn thành; đơn bị hủy, hoàn tiền không tính. Kênh sàn tính theo phần cửa hàng ghi trên POS; doanh thu theo báo cáo sàn dùng để đối soát | `fact_order`, `fact_marketplace_settlement` |
| Số đơn, AOV | Số đơn hoàn thành; doanh thu thuần chia số đơn, theo từng kênh và toàn chi nhánh | `fact_order` |
| Giá vốn định mức, COGS% | Công thức (2.2), định mức và giá chuẩn theo phiên bản món tại ngày bán; món combo được tách thành món thành phần; COGS% theo công thức (2.1) | `fact_order_line`, `dim_menu_item` |
| Hao hụt so với định mức (AvT) | Theo kỳ kiểm kê của từng nguyên liệu: tiêu hao thực tế = tồn đầu + nhập − tồn cuối, công thức (2.3); tiêu hao định mức = số món đã làm × công thức; hao hụt là hiệu của hai đại lượng, quy ra tiền | `mart_ingredient_avt` |
| Giờ công, chi phí nhân công, Labor% | Tổng giờ các ca nhân lương giờ theo phiên bản nhân viên tại ngày làm; ca thiếu lượt ra được nội suy bằng trung vị số giờ cùng ca, cùng vai trò và gắn cờ; công thức (2.4). Chỉ gồm lương giờ trực tiếp | `fact_labor_shift`, `dim_employee` |
| Số ca bếp tối, số đơn mỗi ca tối, OPLH | Số ca theo vai trò và ca làm; số đơn trong ca tối chia số ca tối; công thức (2.5) theo ngày | `fact_order`, `fact_labor_shift` |
| Thời gian chuẩn bị, tỷ lệ hủy, đánh giá | Thời gian chuẩn bị trung bình của đơn App và theo báo cáo sàn; tỷ lệ đơn App bị cửa hàng hủy, bị khách hủy vì chờ lâu; điểm đánh giá App và trên sàn | `fact_order`, `fact_marketplace_settlement` |
| Hoa hồng hiệu dụng, chênh lệch hợp đồng | Hoa hồng chia doanh thu món theo báo cáo sàn, trừ tỷ lệ trong hợp đồng có hiệu lực; tiền thu thừa bằng chênh lệch nhân doanh thu món | `fact_marketplace_settlement` |
| Độ phủ POS đơn sàn | Số đơn sàn có trên POS chia số đơn hoàn thành theo báo cáo sàn, theo tuần | `fact_order`, `fact_marketplace_settlement` |
| Tỷ lệ hủy, hoàn, giảm giá tại quầy | Theo chi nhánh và theo từng thu ngân: số hóa đơn bị hủy, bị hoàn tiền, có giảm giá chia số hóa đơn; so với các thu ngân khác cùng chi nhánh, cùng tuần | `fact_order`, `mart_cashier_weekly` |

Bộ chỉ số giám sát gồm 24 chỉ số thuộc sáu nhóm: kết quả kinh doanh (doanh thu, số đơn, AOV, doanh thu từng kênh), vận hành và nhân sự, trải nghiệm khách hàng, đối soát sàn, quầy thu ngân và chi phí. Mỗi chỉ số có một chiều bất thường. Với số ca bếp tối, độ phủ POS và điểm đánh giá, giá trị thấp là xấu; với thời gian chuẩn bị, tỷ lệ hủy và COGS%, giá trị cao là xấu; còn doanh thu và số đơn lệch theo chiều nào cũng đáng chú ý.

### 3.7.2. Mức kỳ vọng và cây KPI truy vết nguyên nhân

Để phân biệt biến động bình thường với biến động do sự cố, mỗi chỉ số của chi nhánh b trong tuần t được so với một mức kỳ vọng gồm hai thành phần: mức của các chi nhánh cùng hạng trong chính tuần đó, và độ chênh thường ngày của b so với nhóm. Với chỉ số dạng mức (doanh thu, số đơn), gọi m(g, t) là trung vị giá trị của các chi nhánh khác cùng hạng g trong tuần t:

EQ: r(b, t) = ln( x(b, t) / m(g, t) );    r̄(b, t) = trung vị của r(b, t − 8), …, r(b, t − 1) || (3.7)

EQ: x̂(b, t) = m(g, t) × exp( r̄(b, t) );    z(b, t) = ( r(b, t) − r̄(b, t) ) / s(b, t) || (3.8)

trong đó x̂ là mức kỳ vọng, s(b, t) là độ dao động tự nhiên, bằng 1,4826 lần độ lệch tuyệt đối trung vị (MAD) của r trong tám tuần trước (Rousseeuw & Croux, 1993), có sàn bằng trung vị độ dao động của các chi nhánh cùng chỉ số, cùng tuần. Với chỉ số dạng tỷ lệ (tỷ lệ hủy, độ phủ POS), phép chia và logarit được thay bằng phép trừ.

Mỗi lựa chọn có lý do riêng. Ngày lễ, mưa hay điều chỉnh giá tác động lên cả nhóm cùng hạng, nên đi vào m(g, t) và tự triệt tiêu khỏi r. Trung vị và MAD được dùng thay trung bình và độ lệch chuẩn để một tuần bất thường trong quá khứ không kéo lệch mức nền của các tuần sau. Sàn độ dao động tránh trường hợp tám tuần quá đều làm z bị thổi phồng. Một chỉ số chỉ được đánh giá khi đã có ít nhất bốn tuần lịch sử.

IMAGE: figures/h3_6_cay_kpi.png || Hình 3.9. Cây KPI dùng để truy vết biến động doanh thu và lợi nhuận || 16

Quy trình truy vết cho một chi nhánh b trong một tuần t gồm bốn bước:

1. Xác định độ lệch: so doanh thu thuần với mức kỳ vọng theo công thức (3.8). Tuần có |z| từ 3 trở lên là bất thường, từ 2 là cần theo dõi.
2. Phân rã theo cây KPI: doanh thu được tách theo kênh theo công thức (2.9), mỗi kênh tách thành số đơn và AOV; mỗi nút có mức kỳ vọng và độ lệch riêng. Vì ln(doanh thu) = ln(số đơn) + ln(AOV), độ lệch của một kênh xấp xỉ bằng tổng độ lệch của hai thành phần, nên dễ thấy biến động nằm ở lượng hay ở giá.
3. Đối chiếu tín hiệu vận hành: xét các chỉ số vận hành gắn với nhánh đó trong cùng tuần và các tuần trước, vì một số tác động đến trễ qua thứ hạng sàn. Chẳng hạn, số đơn sàn giảm kèm thời gian chuẩn bị tăng, cửa hàng tự hủy đơn tăng và số ca bếp tối giảm là dấu hiệu của vấn đề nhân sự P3.
4. Xếp hạng giả thuyết nguyên nhân: các bộ phát hiện ở mục 3.7.3 chấm điểm từng nguyên nhân P1–P5; nguyên nhân có điểm cao nhất được đề xuất, nguyên nhân thứ hai được hiển thị nếu cũng đủ bằng chứng.

Các nhánh chi phí của lợi nhuận gộp vận hành, gồm giá vốn và phí sàn, không làm thay đổi doanh thu bán hàng, nên được giám sát trực tiếp bằng các bộ phát hiện P1a, P2 và P4 thay vì qua độ lệch doanh thu.

### 3.7.3. Thiết kế các bộ phát hiện

Mỗi bộ phát hiện tạo ra một điểm bằng chứng từ 0 đến 6 cho một giả thuyết nguyên nhân, ở mỗi chi nhánh và mỗi tuần. Với tín hiệu đã quy về điểm z, điểm bằng chứng là phần z vượt theo đúng chiều bất thường, cắt trong khoảng [0, 6]. Với kiểm định trên số đếm, xác suất đuôi được đổi ra z tương đương trước khi cắt. Bảng 3.20 tóm tắt năm bộ phát hiện.

TABLE: Bảng 3.20. Thiết kế năm bộ phát hiện
WIDTHS: 2,2.6,6.6,2.3
| Bộ phát hiện | Đơn vị đánh giá | Phương pháp | Loại |
| P1a. Hoa hồng sai hợp đồng | Chi nhánh × sàn × tuần | Tỷ lệ hiệu dụng trên báo cáo trừ tỷ lệ hợp đồng có hiệu lực; vượt dung sai 0,5 điểm % là sai hợp đồng, nhận điểm tối đa | Luật nghiệp vụ |
| P1b. Đơn sàn không vào POS | Chi nhánh × sàn × tuần | Số đơn sàn báo hoàn thành nhưng không có trên POS, so với tỷ lệ thiếu thường ngày của chính chi nhánh (trung vị các tuần trước, sàn 1%) bằng kiểm định Poisson; hiệu chỉnh Bonferroni cho hai sàn (Dunn, 1961) | Kiểm định |
| P2. Hao hụt vượt định mức | Chi nhánh × kỳ kiểm kê | Hao hụt mỗi ngày của nhóm hàng tươi giá thấp, chia tiêu hao định mức thường ngày của chi nhánh; so cắt ngang với các chi nhánh khác cùng kỳ bằng trung vị và MAD, sàn 0,5 điểm % | Thống kê |
| P3. Thiếu nhân sự, bếp quá tải | Chi nhánh × tuần | Trung bình điểm bằng chứng của năm tín hiệu: số ca bếp tối thấp, thời gian chuẩn bị App và Grab cao, tỷ lệ cửa hàng tự hủy đơn App cao, tỷ lệ khách hủy vì chờ lâu cao | Thống kê, gộp bằng chứng |
| P4. Thất thoát hàng giá trị cao | Chi nhánh × kỳ kiểm kê | Như P2, cho nhóm nguyên liệu có giá chuẩn từ 80.000 đồng mỗi đơn vị; điểm giảm một nửa khi hàng tươi giá thấp cũng vượt (giống hao hụt chung hơn là thất thoát) hoặc khi P1b đủ bằng chứng (nguyên liệu dùng cho đơn không vào sổ) | Thống kê, gộp bằng chứng |
| P5. Gian lận tại quầy | Thu ngân × tuần | Số hóa đơn bị hủy, bị hoàn, có giảm giá của từng thu ngân, so với tỷ lệ của các thu ngân khác cùng chi nhánh, cùng tuần; kiểm định Poisson (xấp xỉ nhị thức khi tỷ lệ nhỏ), hiệu chỉnh Bonferroni theo số phép thử; chỉ xét thu ngân có từ 30 hóa đơn | Kiểm định |

Hai quyết định thiết kế cần được giải thích. Thứ nhất, P1a dùng luật thay vì thống kê, vì nếu sàn tính sai liên tục thì mức nền lịch sử cũng sai theo và điểm z không bao giờ phát hiện được. Thứ hai, P5 đánh giá từng thu ngân thay vì tỷ lệ cấp chi nhánh, vì gian lận gắn với người thực hiện; ở chi nhánh nhỏ, tỷ lệ cấp chi nhánh dao động mạnh và dễ báo sai.

Từ điểm bằng chứng, mỗi chi nhánh × tuần được xếp vào một trong ba mức. Mức cảnh báo khi giả thuyết mạnh nhất có điểm từ 3,5, hoặc doanh thu lệch kỳ vọng với |z| từ 3; trường hợp sau mà không giả thuyết nào đủ điểm thì nguyên nhân được ghi là "chưa xác định", không gán bừa. Mức theo dõi khi điểm hoặc |z| từ 2. Còn lại là bình thường. Ngưỡng 3,5 được chọn trên tập phát triển (mục 5.1.2).

Dữ liệu nguồn thiếu tạo ra đúng những tín hiệu mà bộ phát hiện tìm kiếm. Thiếu tệp POS một ngày thì doanh thu thấp và đơn sàn "biến mất" khỏi POS, giống dấu hiệu của P1b; lượng bán ghi nhận thấp lại làm hao hụt so với định mức tăng, giống P2 và P4. Thiếu tệp chấm công thì số ca bếp thấp, giống P3. Vì vậy có hai quy tắc không kết luận. Thứ nhất, chi nhánh có ngày thiếu dữ liệu POS hoặc chấm công trong tuần thì các giả thuyết dựa trên nguồn đó chỉ ở mức theo dõi, kèm ghi chú "thiếu dữ liệu nguồn trong tuần, chưa kết luận". Thứ hai, khi từ một phần ba số chi nhánh trở lên cùng thiếu dữ liệu trong tuần, chẳng hạn vì API nguồn không phản hồi hay mất mạng diện rộng, trung vị của nhóm so sánh bị kéo lệch, chi nhánh đủ dữ liệu cũng trông như bất thường; khi đó các giả thuyết dựa trên so sánh giữa chi nhánh, gồm doanh thu, P2, P3 và P4, cũng không kết luận. Khi tệp được gửi bổ sung, lượt chạy sau tự đánh giá lại. P1a dựa trên báo cáo của sàn và hợp đồng nên không bị ảnh hưởng.

Mỗi cảnh báo gồm chi nhánh, tuần, nguyên nhân hạng một và hạng hai cùng điểm, bằng chứng dạng chữ như "NV0093: 20/270 hóa đơn bị hủy, tức 7,4%, thu ngân khác 1,0%", và doanh thu thực tế so với kỳ vọng. Lớp phân tích bổ sung đề xuất xử lý cho từng nguyên nhân: việc cần xác minh, việc cần làm, việc theo dõi, người phụ trách, thời hạn và thiệt hại ước tính tính từ kho dữ liệu. Danh sách cảnh báo nhờ đó được sắp theo mức thiệt hại (yêu cầu FR6).

### 3.7.4. Quy trình xử lý cảnh báo

Cảnh báo chỉ có giá trị khi được chuyển thành việc cụ thể. Hình 3.10 mô tả quy trình xử lý một cảnh báo theo ba làn: nền tảng, quản lý vận hành và người phụ trách. Nền tảng tự quét và lập danh sách cảnh báo sau mỗi lượt xử lý. Quản lý vận hành chọn cảnh báo theo thiệt hại ước tính, xem truy vết và quyết định đã đủ căn cứ để giao việc hay chưa. Người phụ trách được xác định theo nguyên nhân trong đề xuất xử lý, và phải xác minh bằng nguồn ngoài hệ thống trước khi xử lý, vì thống kê chỉ cho biết nghi vấn. Tuần kế tiếp, nền tảng đánh giá lại chỉ số; nếu còn lệch so với mức kỳ vọng, cảnh báo xuất hiện lại. Nền tảng hiện chưa lưu trạng thái giao việc, nên việc theo dõi kết quả xử lý dựa vào chính các chỉ số của tuần sau; ghi nhận trạng thái xử lý là một hướng mở rộng.

IMAGE: figures/h3_act_canh_bao.png || Hình 3.10. Sơ đồ hoạt động của quy trình xử lý cảnh báo || 16

## 3.8. Thiết kế ứng dụng, kho phục vụ và điều phối

### 3.8.1. Ứng dụng

Ứng dụng là một địa chỉ duy nhất cho cả người dùng nghiệp vụ và kỹ sư dữ liệu. Các trang được xếp theo đúng dòng dữ liệu, thành bốn nhóm sau trang chủ là sơ đồ hệ thống. Nhóm Nguồn dữ liệu gồm kết nối nguồn, tải tệp lên và xem tệp gốc. Nhóm Dữ liệu gồm vận hành hằng ngày, kho dữ liệu có ô truy vấn SQL, mô hình và phả hệ, chất lượng dữ liệu. Nhóm Phân tích vận hành gồm tổng quan, trung tâm cảnh báo và truy vết nguyên nhân. Nhóm Kiểm chứng gồm bộ mô phỏng và đánh giá bộ phát hiện. Nhóm Kiểm chứng là nơi duy nhất đọc đáp án của bộ mô phỏng, tách khỏi phần sản phẩm. Mọi trang dùng chung bộ lọc môi trường dữ liệu, chi nhánh và khoảng thời gian; môi trường mặc định là môi trường vận hành, nơi duy nhất nhận dữ liệu mới, còn hai tập đánh giá chỉ để xem lại kết quả đã chốt.

### 3.8.2. Kho phục vụ và công cụ BI

Sau mỗi lượt chạy thành công, tầng Gold cùng các bảng cảnh báo và nhật ký vận hành được sao sang PostgreSQL: nạp vào lược đồ tạm, đối soát số dòng từng bảng với DuckDB, rồi đổi lược đồ tạm thành lược đồ chính trong một giao dịch, nên người đọc chỉ thấy bản cũ hoặc bản mới hoàn chỉnh. Metabase kết nối bằng tài khoản chỉ đọc và phục vụ các báo cáo chuẩn về doanh thu, số đơn, AOV, COGS%, Labor%, kênh, chi nhánh, thực đơn và cảnh báo. Ứng dụng chỉ tự xây những trang cần logic riêng như cảnh báo và truy vết.

### 3.8.3. Điều phối

Điều phối được tách thành hai đồ thị tác vụ của Airflow theo đúng vai trò trong doanh nghiệp, như Hình 3.11. DAG `fastfat_nguon` đóng vai các hệ thống nguồn, lúc 23 giờ ghi dữ liệu của ngày kinh doanh vừa kết thúc rồi báo cập nhật một Dataset. DAG `fastfat_pipeline` là đường ống dữ liệu, chạy ngay khi Dataset cập nhật và tự kiểm tra thêm mỗi giờ để kéo dữ liệu qua API và nhận tệp do người gửi. Cửa chặn chất lượng giữa Bronze và Silver kiểm tra độ mới, khối lượng so với trung vị 14 ngày, độ đầy đủ theo chi nhánh từng ngày, tệp bị từ chối và thay đổi cấu trúc. Mức chặn gồm ba trường hợp: nguồn hằng ngày chậm từ bốn ngày, một ngày không có dòng nào, và từ một phần ba số chi nhánh cùng thiếu dữ liệu. Nếu có một mục ở mức chặn hoặc một kiểm thử dbt thất bại, các bước phía sau không chạy, nên không có cảnh báo hay báo cáo nào được tạo từ dữ liệu sai; lượt sau tự chạy tiếp khi dữ liệu về đủ. Vì DuckDB chỉ cho một tiến trình ghi, mỗi lúc chỉ một lượt đường ống được chạy.

IMAGE: figures/h3_7_dag.png || Hình 3.11. Hai đồ thị tác vụ: hệ thống nguồn và đường ống dữ liệu kích hoạt theo dữ liệu mới || 14

Hình 3.11 cho thấy cấu trúc của hai DAG. Hình 3.12 mô tả hành vi của một lượt đường ống dưới dạng sơ đồ hoạt động, làm rõ các điểm rẽ nhánh. Một lượt có thể được khởi động bởi Dataset hoặc theo lịch mỗi giờ. API không phản hồi chỉ là cảnh báo, không chặn các nguồn tệp. Không có tệp mới thì lượt kết thúc ngay ở bước check. Cửa chặn ở mức chặn hoặc kiểm thử dbt lỗi thì lượt dừng trước khi tạo cảnh báo và trước khi thay bản sao trên kho phục vụ.

IMAGE: figures/h3_act_lo_du_lieu.png || Hình 3.12. Sơ đồ hoạt động của một lượt đường ống dữ liệu || 16

### 3.8.4. Tương tác giữa các thành phần

Hình 3.13 và Hình 3.14 là sơ đồ tuần tự của hai ca sử dụng có nhiều thành phần tham gia nhất. Khi người dùng gửi tệp, trang Tải tệp lên gọi phần tiếp nhận cho từng tệp, và chỉ báo Airflow một lần sau cùng nếu có ít nhất một tệp được nhận hoặc thay bản cũ; đường ống sau đó chạy độc lập với trang. Khi truy vết, trang Truy vết đọc kho ở chế độ chỉ đọc, gọi các hàm của lớp phân tích để chấm điểm và lập đề xuất, rồi truy vấn các bản ghi bằng chứng kèm tên tệp và số dòng gốc mà tầng Bronze đã lưu. Nút Mở tệp gốc chỉ chuyển trang kèm tên tệp và chuỗi lọc. Trang Tệp nguồn đọc lại tệp nguyên văn trong vùng tiếp nhận, nên người dùng thấy đúng dữ liệu hệ thống nguồn đã xuất chứ không phải bản đã qua xử lý.

IMAGE: figures/h3_seq_tai_len.png || Hình 3.13. Sơ đồ tuần tự khi gửi tệp qua trang Tải tệp lên || 16

IMAGE: figures/h3_seq_truy_vet.png || Hình 3.14. Sơ đồ tuần tự khi truy vết một cảnh báo và mở tệp gốc || 16

## 3.9. Tiểu kết chương

Chương này đã chuyển các yêu cầu nghiệp vụ thành một thiết kế cụ thể. Bộ mô phỏng tạo ra một thế giới vận hành nhất quán, trong đó mỗi hệ thống nguồn chỉ thấy phần của mình và mang lỗi riêng, còn các sự cố để lại dấu vết đồng thời ở nhiều nguồn. Đường ống đi qua tầng thu thập, Bronze, Silver và Gold, mỗi tầng một trách nhiệm, với kiểm soát chất lượng ở cả đầu vào lẫn bên trong kho. Lớp phân tích so mỗi chỉ số với mức kỳ vọng tính từ nhóm chi nhánh cùng hạng và lịch sử của chính chi nhánh, rồi dùng năm bộ phát hiện để chấm điểm từng giả thuyết nguyên nhân. Các sơ đồ phân rã chức năng, ca sử dụng, hoạt động và tuần tự mô tả nền tảng từ góc nhìn người dùng lẫn từ bên trong, làm căn cứ cho phần hiện thực. Chương 4 trình bày cách hiện thực thiết kế này và các kết quả đo được trên dữ liệu.
