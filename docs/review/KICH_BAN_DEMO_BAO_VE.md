# KỊCH BẢN DEMO BẢO VỆ — ứng dụng hợp nhất (cập nhật 17/10/2026, sau khi có kênh thu thập và API nguồn)

Mạch demo đi theo đường của một sản phẩm thật: dữ liệu đến từ các hệ thống nguồn bằng nhiều kênh → đường ống tự xử lý → cảnh báo và truy vết cho người quản lý. Bộ mô phỏng và phần đánh giá chỉ xuất hiện ở cuối, đúng vai "kiểm chứng". Mọi con số dưới đây lấy từ chính ứng dụng. Số của môi trường Vận hành là của lượt chạy ngày 17/10/2026; số của phần phân tích lấy trên tập phát triển, bộ lọc "Toàn chuỗi", toàn bộ khoảng thời gian.

---

## 1. Chuẩn bị (30 phút trước giờ)

1. Mở Docker Desktop, đợi biểu tượng chuyển sang trạng thái chạy. Mở terminal ở `D:\khoaluan`:
   ```
   docker compose up -d
   .venv\Scripts\python tools\chuan_bi_demo.py --khoi-phuc
   .venv\Scripts\python tools\kiem_tra_truoc_demo.py
   ```
   Lệnh khôi phục đưa môi trường Vận hành về 22/09/2024 (hệ thống nguồn tự sinh thêm một ngày lúc 23:00 mỗi đêm nên sáng hôm bảo vệ luôn phải chạy). Lệnh kiểm tra mất khoảng 2 phút, dòng cuối phải là `SẴN SÀNG`. Nếu có dòng `!` "Mã ứng dụng mới hơn container" thì chạy `docker restart fastfat-app` rồi kiểm tra lại với `--nhanh`.
2. Trình duyệt, phóng to 90%, mở 3 tab:
   - http://localhost:8501 — ứng dụng, môi trường mặc định là "Vận hành".
   - http://localhost:8600/docs — tài liệu của API nguồn (POS đám mây, App).
   - http://localhost:8080 — Airflow (admin / admin), mở sẵn danh sách DAG.
3. Mở sẵn bằng Excel hai tệp, đúng hai tệp có trong Hình 4.2 của báo cáo:
   - `data\calibration\source_systems\warehouse_receipts\CN01\NhapKho_CN01_20240313.xlsx`
   - `data\calibration\source_systems\warehouse_receipts\CN03\receipts_CN03_20240904.xlsx`
4. Mở sẵn `docs\BaoCao_KhoaLuan.pdf`, tắt thông báo của Windows (Focus assist).

**Phương án dự phòng**

| Sự cố | Cách xử lý |
|---|---|
| Docker không lên | `.venv\Scripts\streamlit run app\main.py --server.port 8504`, mở http://localhost:8504. Các trang phân tích chạy được trên hai tập đánh giá; bỏ qua Tổng quan (cần Metabase), Vận hành hằng ngày và Tải tệp lên (cần Airflow, API nguồn). |
| Lượt dữ liệu mới chạy lâu hơn dự kiến | Nói tiếp phần Tệp nguồn, Tải tệp lên; quay lại trang Vận hành hằng ngày khi cả tám ô bước đều "Xong". Một lượt bảy ngày thường mất khoảng ba phút. |
| Lỡ bấm gửi dữ liệu hai lần hoặc trạng thái lạ | Chạy lại `tools\chuan_bi_demo.py --khoi-phuc` (khoảng 20 giây). |
| Máy hỏng hoặc không chiếu được | Mở video `docs\review\demo_ung_dung.webm` và nói theo mạch bên dưới. |

---

## 2. Mạch demo đầy đủ (khoảng 11 phút)

> Câu mở đầu: *"Em xin demo sản phẩm. Ngoài thực tế, dữ liệu của một chuỗi đồ ăn nhanh không nằm sẵn một chỗ: POS đám mây có API, POS cài tại máy và máy chấm công xuất tệp, báo cáo sàn và sổ kho do người gửi. Sản phẩm nhận cả ba đường đó, tự xử lý và đưa ra cảnh báo có nguyên nhân. Các trang xếp đúng theo đường đi của dữ liệu."*

**Bước 0 — Sơ đồ hệ thống (30 giây).** Trang chủ, môi trường Vận hành.
- *"Dữ liệu đến bằng ba kênh, vào vùng tiếp nhận, nạp Bronze, làm sạch ở Silver, mô hình hóa ở Gold, bộ phát hiện quét mọi chi nhánh mọi tuần, kết quả sang PostgreSQL cho Metabase và tới người quản lý ở trang truy vết. Airflow tự chạy cả chuỗi khi có dữ liệu mới."*

**Bước 1 — Kết nối nguồn (45 giây).** Trang Kết nối nguồn.
- Sơ đồ ba kênh: *"Tám chi nhánh dùng POS đám mây và App chỉ lấy được qua API; ba chi nhánh POS cũ, máy chấm công xuất tệp; báo cáo sàn, sổ kho do người gửi."*
- Bảng nguồn: *"Mỗi nguồn có nhịp riêng: POS, chấm công hằng ngày, sàn hằng tuần, kiểm kê hai tuần một lần; hệ thống biết nguồn nào đang chậm."*
- Mở tab http://localhost:8600/docs trong 10 giây: *"Đây là API của phần mềm POS, phía doanh nghiệp: cần mã xác thực, trả theo trang, giới hạn số lần gọi, thỉnh thoảng lỗi tạm thời như API thật. Bộ kết nối của em phải xử lý được hết những điều đó."*

**Bước 2 — Dữ liệu mới đến (15 giây, rồi để chạy).** Trang Vận hành hằng ngày.
- *"Dữ liệu đang đến ngày 22/09/2024."* Chọn "7 ngày", bấm "Gửi dữ liệu ngày mới". *"Em chỉ bấm cho các hệ thống nguồn ghi dữ liệu của bảy ngày kinh doanh; em không bấm chạy đường ống. Trong lúc chờ khoảng ba phút, em cho thầy cô xem dữ liệu thô và cách đường ống kiểm soát chất lượng."*

**Bước 3 — Dữ liệu thô và chất lượng (1 phút 30 giây), trong lúc đường ống chạy.**
- Trang Tệp nguồn, chọn `pos` → `POS-05` → một tệp bất kỳ: *"Chi nhánh 5 dùng POS bản cũ: ngày theo kiểu khác, tiền là chuỗi '157.000', trường tổng tiền tên khác bản đám mây. Sáu hệ thống ghi mã chi nhánh theo sáu kiểu."* (Tùy chọn) mở hai tệp Excel đã chuẩn bị: sổ mẫu A có tiêu đề, dòng Tổng cộng, chữ ký; sổ mẫu B có dòng cà chua 2300 kg gõ nhầm gam vào cột kg.
- Trang Mô hình và phả hệ: *"Phả hệ dbt tự sinh; lược đồ hình sao 7 bảng chiều, 6 bảng sự kiện; món ăn và nhân viên lưu lịch sử theo SCD loại 2."*
- Trang Chất lượng dữ liệu: *"Bronze bằng Silver cộng dòng cách ly cộng dòng cấu trúc, phần chưa giải thích bằng 0 ở cả 7 nguồn; 158 kiểm thử tự động đều đạt."*

**Bước 4 — Kết quả lượt dữ liệu mới (1 phút).** Quay lại trang Vận hành hằng ngày (nếu các ô bước chưa "Xong" hết thì nói thêm về cửa chặn chất lượng trong lúc đợi).
- Các ô bước đều "Xong": *"Bộ kết nối kéo 10.365 hóa đơn POS và 3.880 đơn App qua 55 và 24 trang, tự thử lại khi API lỗi tạm thời; 236 tệp mới được nạp; 15 mục cửa chặn chất lượng đạt; 211 bước dbt đạt; dữ liệu sang kho phục vụ đối soát khớp."*
- *"Bộ phát hiện tự tìm ra hai sự cố tuần mới: CN1 bị ShopeeFood thu hoa hồng cao hơn hợp đồng, thu thừa 528 nghìn; CN3 thiếu nhân sự ca tối."* Bấm "Truy vết" ở CN1, xem nhanh đề xuất xử lý.
- (Tùy chọn) trang Kết nối nguồn giờ có bảng bộ kết nối: mốc 29/09, số trang, số lần thử lại.

**Bước 5 — Tải tệp lên (1 phút).** Trang Tải tệp lên, bấm "Gửi cả 9 tệp mẫu".
- Bảng Kết quả tiếp nhận: *"Hệ thống nhận dạng tệp theo nội dung, không theo tên. Phiếu kiểm kê đếm lại thì thay bản cũ; báo cáo ShopeeFood gửi lặp thì bỏ qua; báo cáo Grab lưu nhầm thành Excel, tệp chấm công thiếu cột, sổ kho không ghi chi nhánh, bảng lương gửi nhầm, máy POS chưa khai báo thì bị từ chối kèm lý do cụ thể để người gửi sửa. Không tệp nào bị bỏ qua mà không có lý do."*
- *"Tệp hợp lệ được báo cho Airflow, đường ống chạy ngay, khoảng một phút rưỡi sau bảng phía dưới chuyển sang 'đã nạp Bronze'."* Không cần đợi, đi tiếp bước 6.

**Bước 6 — Tổng quan và cảnh báo trên lịch sử dài (1 phút 15 giây).** Ở thanh bên đổi môi trường sang "Đánh giá · tập phát triển" (26 tuần dữ liệu).
- Trang Tổng quan: *"Báo cáo kinh doanh chuẩn dùng đúng công cụ BI: dashboard Metabase dựng bằng mã, đọc kho phục vụ bằng tài khoản chỉ đọc. Toàn chuỗi 37,9 tỷ doanh thu, 430 nghìn đơn, COGS 31%, Labor 11,6%."*
- Trang Trung tâm cảnh báo: *"Quét 11 chi nhánh × 22 tuần theo 24 chỉ số: 18 tuần cảnh báo, 31 mục theo dõi, sắp theo thiệt hại ước tính. Đứng đầu là CN2 tuần 06/05, nghi thiếu nhân sự, ước tính 48,3 triệu."* Chọn dòng đầu, bấm "Truy vết".

**Bước 7 — Truy vết CN2, tuần 06/05–12/05/2024 (2 phút) — phần quan trọng nhất.**
- Kết luận nhanh: *"P3 thiếu nhân sự, điểm 4,3."* Đề xuất xử lý: *"Doanh thu thấp hơn kỳ vọng 48,3 triệu; bù khoảng 12 ca bếp tối mỗi tuần tốn khoảng 2,6 triệu."*
- Doanh thu so với kỳ vọng: *"Thực tế 233,4 triệu, kỳ vọng 281,7 triệu, thấp hơn 17,2%. Kỳ vọng tính theo các chi nhánh cùng hạng trong chính tuần này, nên lễ, mưa, đổi giá đã bị trừ ra."*
- Cây KPI: *"Hụt chủ yếu ở số đơn, giá trị đơn gần như không đổi: mất khách, không phải khách mua ít đi."* Tab P3: *"Ca bếp tối 11 so với kỳ vọng 23; chuẩn bị đơn App 21 phút so với 14; cửa hàng tự hủy 6,2% đơn App."*
- Diễn biến quanh tuần: *"Tuần 20/05 nhân sự về bình thường nhưng đơn Grab vẫn thấp vì điểm đánh giá giảm: hậu quả đến sau 1–3 tuần."*

**Bước 8 — Từ cảnh báo về tận dòng dữ liệu thô (45 giây).** Đổi Chi nhánh sang CN8, Tuần 01/07.
- *"Nghi vấn gian lận tại quầy: NV0093 có 20 hóa đơn bị hủy trên 270, các thu ngân khác 1%."* Kéo xuống Bằng chứng gốc, bấm "Mở tệp gốc": *"Ứng dụng mở đúng tệp POS của ngày đó và lọc đúng hóa đơn POS-08-03-20240701-00065. Hệ thống chỉ nêu nghi vấn; kết luận phải đối chiếu camera, két tiền."*

**Bước 9 — Kiểm chứng: làm sao biết hệ thống đúng (2 phút).** Nhóm trang Kiểm chứng.
- Trang Đánh giá bộ phát hiện: *"Dữ liệu là mô phỏng nên có đáp án để đo. Ngưỡng 3,5 chọn trên tập phát triển và chốt bằng commit, rồi chạy tập kiểm tra đúng một lần. Tập phát triển 5/6 sự cố, F1 0,79; tập kiểm tra 4/6, F1 0,52. Chỉ theo dõi doanh thu bắt 0/6 và 1/6; Isolation Forest 3/6 và 2/6. Em giữ nguyên các trường hợp bỏ sót."*
- Trang Bộ mô phỏng, CN2 ngày 11/05/2024: *"Đây là sự thật của một ngày đặt cạnh những gì từng hệ thống ghi lại: 216 đơn tại quầy khớp POS; 38 khách bỏ về không hệ thống nào ghi; Grab 111 đơn nhưng POS chỉ 108 vì quên nhập. Mọi nguồn sinh từ cùng một tập sự kiện nên nhất quán như ngoài đời. Đây là nhóm duy nhất đọc đáp án; đường ống và bộ phát hiện không đọc."*

---

## 3. Bản rút gọn 5 phút

Bước 1 (30 giây) → Bước 2 bấm gửi (15 giây) → trong lúc chờ: Bước 6 chỉ Trung tâm cảnh báo (30 giây) và Bước 7 phần kết luận, đề xuất xử lý, tab P3 (1 phút 30 giây) → Bước 4 (45 giây) → Bước 5 (45 giây) → Bước 9 chỉ trang Đánh giá (45 giây).

---

## 4. Câu hỏi dễ gặp

**Ngoài thực tế dữ liệu đến bằng cách nào? Sao không phải chỉ là tệp đặt sẵn?**
Tùy hệ thống. POS bán theo thuê bao giữ hóa đơn trên máy chủ nhà cung cấp và mở API; POS cài tại máy xuất tệp mỗi đêm; máy chấm công xuất CSV; báo cáo sàn do kế toán tải từ cổng đối tác; sổ kho, phiếu kiểm kê do quản lý điền Excel và gửi. Sản phẩm có đủ ba kênh: bộ kết nối kéo qua API, tệp xuất tự động vào vùng tiếp nhận, và trang tải lên cho tệp do người gửi. Từ vùng tiếp nhận trở đi mọi nguồn đi chung một đường ống.

**API có phải API thật không?**
API là dịch vụ giả lập phía doanh nghiệp (FastAPI, chạy trong Docker), vì em không có quyền truy cập hệ thống của một chuỗi thật. Nó có những đặc điểm khó của API bán hàng: mã xác thực, phân trang, giới hạn tần suất, lỗi tạm thời. Bộ kết nối của em kéo tăng dần theo mốc ngày, lấy lại ngày mốc để bắt hóa đơn đồng bộ trễ, đối chiếu tổng số bản ghi, thử lại khi lỗi. Đường API cho dữ liệu giống từng byte với tệp gốc. API thật của từng nhà cung cấp có thể khác (OAuth, lấy theo thời điểm cập nhật), em ghi ở hạn chế.

**Nếu API sập, hoặc ai đó gửi tệp sai thì sao?**
Em có thử nghiệm "ngày xấu": 11 tình huống cài cùng lúc (tệp hỏng, tệp rỗng, thiếu cột, bảng mã UTF-16, báo cáo lưu sai định dạng, tệp lạ, tệp chép đổi tên ngày, máy POS chưa khai báo, bản sửa, tệp đến muộn, nguồn thêm trường mới) và API không phản hồi. Mọi tình huống xử lý đúng mong đợi. Khi API sập, các nguồn tệp vẫn được nạp, nhưng cửa chặn chất lượng thấy 8–10 chi nhánh thiếu POS nên dừng trước Silver, không có cảnh báo nào từ dữ liệu thiếu; khi API sống lại, lượt sau tự lấy bù và cho đúng hai cảnh báo. Kết quả ở mục 5.2.4 báo cáo.

**Một con số trên màn hình có truy ngược được về dữ liệu gốc không?**
Có. Mỗi bản ghi giữ tên tệp và số dòng gốc từ tầng Bronze. Ở trang Truy vết, mục Bằng chứng gốc liệt kê các bản ghi làm căn cứ, bấm một nút là mở đúng tệp và lọc sẵn dòng đó.

**Dữ liệu này là dữ liệu giả?**
Dữ liệu mô phỏng, em ghi rõ trong báo cáo. Đơn hàng của doanh nghiệp không công khai và không thu thập hợp pháp được. Bộ mô phỏng có chuỗi nhân quả nhân sự → tải bếp → thời gian chờ → hủy đơn → thứ hạng sàn → doanh thu; một số phân phối hiệu chỉnh từ bộ giao dịch thật công khai The Bread Basket. Có đáp án cho từng sự cố nên đo được độ chính xác. Sản phẩm không phụ thuộc vào bộ mô phỏng: thay bằng hệ thống thật thì tầng thu thập và mọi lớp phía sau giữ nguyên.

**Hệ thống có "biết trước kịch bản" không?**
Không. Bộ phát hiện quét mọi chi nhánh mọi tuần theo cùng một bộ 24 chỉ số, không đọc tệp kịch bản hay đáp án. Hai sự cố trong môi trường Vận hành chỉ để trình diễn; bộ phát hiện tự tìm ra chúng giống như với dữ liệu thật.

**Làm sao biết em không "ăn gian" khi tự tạo dữ liệu?**
Đường ống và bộ phát hiện không đọc đáp án. Hai tập kịch bản độc lập: chọn ngưỡng trên tập phát triển, chốt bằng commit rồi chạy tập kiểm tra một lần. Kết quả tập kiểm tra thấp hơn và em báo cáo đúng như vậy. Các quy tắc thêm sau (không kết luận khi thiếu dữ liệu) được kiểm chứng không làm đổi kết quả đã chốt.

**Sao tập kiểm tra thấp hơn mà em không chỉnh lại?**
Chỉnh lại rồi chạy lại tập kiểm tra thì con số không còn ý nghĩa đánh giá. Phân tích lỗi cho thấy ở cả 5 sự cố có tín hiệu, nguyên nhân đúng đều đứng hạng 1; chỗ yếu là độ nhạy với sự cố nhẹ. Các cải tiến em ghi ở hướng phát triển.

**Truy vết dùng mô hình gì?**
Phân tích chênh lệch kiểu kế toán quản trị, có kiểm định thống kê: mức kỳ vọng theo nhóm chi nhánh cùng hạng, độ dao động tính bằng trung vị và MAD; kiểm định Poisson cho số đơn sàn thiếu và số hóa đơn hủy của từng thu ngân, có hiệu chỉnh Bonferroni; phí sàn so thẳng với hợp đồng. Mỗi nguyên nhân có một "dấu vân tay" chỉ số riêng.

**Sao không dùng ML hay AI tạo sinh để gợi ý?**
Không có sự cố thật đã gán nhãn để huấn luyện; quản lý cần biết vì sao có cảnh báo; và em đã so với Isolation Forest, kết quả kém hơn. Phần gợi ý xử lý làm bằng quy tắc nghiệp vụ, mọi con số tính từ kho nên tái lập và giải thích được.

**Ước tính thiệt hại tính thế nào?**
Mỗi nguyên nhân một cách, đều từ kho dữ liệu: hoa hồng thu thừa cộng dồn các tuần lệch; số đơn sàn thiếu vượt mức thường × giá trị đơn trên sàn; hao hụt vượt mức của các chi nhánh khác cùng kỳ; doanh thu thấp hơn kỳ vọng. Đây là ước tính để xếp ưu tiên.

**Labor% sao thấp (8–12%)?**
Đó mới là lương giờ trực tiếp theo chấm công, chưa gồm lương cố định của quản lý, bảo hiểm, phụ cấp; định nghĩa ghi rõ trong báo cáo.

**Sao không dùng Spark, Kafka, công cụ tích hợp như Airbyte?**
Mỗi tập vài trăm MB, một máy xử lý trong vài chục giây; nhịp nghiệp vụ là theo ngày nên không cần streaming. Chỉ có hai nguồn API, bộ kết nối viết riêng vài trăm dòng kiểm soát được mốc, đối chiếu và hợp đồng dữ liệu; Airbyte cần thêm một hệ thống chạy riêng.

**Hệ thống chạy hằng ngày thế nào?**
Hai DAG: hệ thống nguồn ghi dữ liệu lúc 23:00; đường ống 7 bước tự chạy khi có dữ liệu mới (Airflow Dataset) và tự chạy thêm mỗi giờ để kéo API và nhận tệp người gửi. Bước đầu kéo qua API; không có gì mới thì các bước sau bỏ qua. Bronze nạp tăng dần, chạy lại không trùng. Trên đám mây, mẫu này tương ứng tệp mới trên S3 kích hoạt đường ống qua EventBridge.

**Mã nguồn có tái lập được kết quả không?**
Có. Lệnh `tools\kiem_tra_truoc_demo.py` đối chiếu số của bộ phát hiện với kết quả đã chốt mỗi lần chạy; mã băm bảng điểm và bảng cảnh báo trùng khớp với bản đã dùng để chốt.

---

## 5. Không nên nói

- "Dùng Faker sinh dữ liệu": sai, bộ mô phỏng không dùng Faker.
- "Phát hiện chính xác", "100%": tập kiểm tra chỉ bắt 4/6 sự cố.
- "Hệ thống phát hiện gian lận của nhân viên X": hệ thống chỉ chỉ ra nghi vấn để xác minh.
- "Kết nối được API của nhà cung cấp X": API là giả lập, chỉ nói "API của phần mềm POS đám mây".
- Không mở trang Bộ mô phỏng xen giữa lúc đang truy vết; nếu được hỏi, nói rõ bộ phát hiện không dùng nó.
- Không gắn dữ liệu với tên một doanh nghiệp thật.
