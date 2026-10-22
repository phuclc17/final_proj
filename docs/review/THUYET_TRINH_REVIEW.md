# THUYẾT TRÌNH REVIEW SẢN PHẨM (5 phút) — cập nhật 11/10/2026 (sau khi xong Silver + Gold)

> File này gồm: (1) chuẩn bị trước buổi, (2) lời nói 5 phút, (3) kịch bản demo nếu thầy yêu cầu xem, (4) câu hỏi dễ gặp, (5) những điều không nên nói.
> Gửi kèm cho thầy: `docs/BaoCao_KhoaLuan_BanReview.pdf` (bản xem nhanh, có trang "Tình trạng thực hiện" ngay sau bìa).

---

## 1. Chuẩn bị trước buổi (10 phút trước giờ)

1. Mở terminal ở thư mục `D:\khoaluan`, chạy (nếu Streamlit hỏi email, nhấn Enter bỏ qua):
   ```
   .venv\Scripts\streamlit run tools\data_viewer.py --server.port 8503
   ```
   Mở thêm 1 terminal nữa, chạy:
   ```
   .venv\Scripts\streamlit run app\main.py --server.port 8504
   ```
   Mở trình duyệt 2 tab: http://localhost:8503 (xem dữ liệu các tầng) và http://localhost:8504 (truy vết nguyên nhân — **phần quan trọng nhất**). Bấm thử qua các chế độ cho chắc chạy.
2. Mở sẵn file PDF `docs\BaoCao_KhoaLuan_BanReview.pdf`.
3. Mở sẵn bằng Excel 2 file (để show "dữ liệu thô thật sự bẩn"):
   - `data\calibration\source_systems\warehouse_receipts\CN01\NhapKho_CN01_20240412.xlsx` (mẫu A)
   - `data\calibration\source_systems\warehouse_receipts\CN03\receipts_CN03_20240412.xlsx` (mẫu B)
4. **Không** chạy `pipeline.run_dbt` trong lúc demo (đang có trang mở kho thì vẫn chạy được, nhưng mất 1–2 phút, không cần thiết).
5. (Tùy chọn) Để sẵn một terminal cho demo "dữ liệu mới về mỗi ngày" ở mục 3, bước 6.

---

## 2. Lời nói 5 phút

**[0:00 – 0:45] Vấn đề**

Em chào thầy. Đề tài của em là xây dựng nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn để truy vết nguyên nhân biến động doanh thu cho chuỗi F&B.

Bài toán xuất phát từ thực tế là một chuỗi đồ ăn nhanh bây giờ bán qua nhiều kênh cùng lúc: tại quầy, app riêng, GrabFood, ShopeeFood. Dữ liệu vì vậy nằm rải rác ở nhiều hệ thống: máy POS, app, file đối soát của sàn, sổ kho quản lý ghi Excel, máy chấm công. Mỗi nơi một định dạng, một kiểu mã. Khi doanh thu một chi nhánh giảm, quản lý chỉ thấy con số tổng, không biết là do trời mưa, hết đợt lễ, hay do sự cố như sàn tính sai phí, thiếu người ca tối, nguyên liệu hao hụt, hoặc thu ngân gian lận.

**[0:45 – 1:30] Mục tiêu**

Nên mục tiêu của em là một hệ thống đi đủ ba bước:
- Một: tích hợp 7 nguồn dữ liệu khác nhau thành một kho dữ liệu sạch — đây là phần Data Engineering.
- Hai: tính các chỉ số vận hành chuẩn ngành như giá vốn trên doanh thu, chi phí nhân công, tỷ lệ hủy đơn, hao hụt so với định mức.
- Ba: phát hiện 5 loại sự cố và truy vết xem biến động doanh thu nằm ở nhánh nào, do nguyên nhân gì — phần Data Analytics.

**[1:30 – 2:30] Dữ liệu — ở đâu ra**

Dữ liệu đơn hàng, hóa đơn thật của doanh nghiệp nằm trong hệ thống nội bộ của họ, không công khai và không thu thập hợp pháp được. Nên em làm theo hướng mô phỏng có cơ sở, và nói rõ điều này ngay trong báo cáo.

Bộ mô phỏng theo nguyên tắc "một thế giới, nhiều góc nhìn": em sinh các sự kiện thật một lần — khách đặt món gì, giờ nào, ai đi làm ca nào, bếp tải bao nhiêu — rồi mỗi hệ thống xuất ra phần nó nhìn thấy, kèm lỗi riêng của nó. Ví dụ thiếu người ca tối thì bếp quá tải, món ra chậm, cửa hàng phải hủy đơn, điểm đánh giá giảm, vài tuần sau sàn đẩy ít đơn hơn. Một số quy luật mua hàng em hiệu chỉnh từ bộ giao dịch thật công khai The Bread Basket trên OpenML.

Em có 2 tập dữ liệu, mỗi tập 26 tuần, 11 chi nhánh, khoảng 400 nghìn đơn, mỗi tập 6 kịch bản sự cố có đáp án: tập đầu để phát triển, tập sau giữ riêng chỉ để đánh giá cuối.

**[2:30 – 3:15] Kiến trúc và công nghệ**

Đường ống theo kiến trúc Medallion: Bronze nạp nguyên trạng file thô, Silver làm sạch và chuẩn hóa, Gold tổ chức thành kho dữ liệu hình sao và các bảng chỉ số. Em dùng DuckDB làm kho, dbt cho biến đổi và kiểm thử dữ liệu, Streamlit cho giao diện, Airflow để chạy hằng ngày. Em không dùng Spark hay Kafka vì dữ liệu chỉ vài trăm MB.

**[3:15 – 4:30] Tiến độ**

Đến hôm nay em đã xong toàn bộ phần dữ liệu:
- Bộ mô phỏng: cả 12 kịch bản đều tạo đúng tác động.
- Tầng Bronze: hơn 6 nghìn file, khoảng 500 nghìn dòng trong 80 giây; ngày mới về chỉ mất 5 giây, chạy lại không trùng.
- Tầng Silver: làm sạch 7 nguồn, dòng lỗi đưa vào bảng cách ly kèm lý do, đối soát số dòng Bronze–Silver không mất dòng nào.
- Tầng Gold: 7 bảng chiều — trong đó món ăn và nhân viên có lưu lịch sử thay đổi giá, lương — 6 bảng sự kiện gộp đơn của cả 4 kênh, và 5 bảng chỉ số tính sẵn cho truy vết. Tổng cộng 209 kiểm thử dữ liệu tự động đều đạt trên cả hai tập; doanh thu ở Gold khớp tuyệt đối với Silver.
- Một trang truy vết nguyên nhân chạy trên tầng Gold, em xin demo ngay sau đây.

Tiếp theo: bộ phát hiện chính thức và đánh giá trên tập kiểm tra 14–17/10, giao diện và chạy tự động 18/10, sau đó hoàn thiện báo cáo.

**[4:30 – 5:00] Kết**

Em xin demo nhanh phần truy vết, và nếu thầy muốn em cho xem dữ liệu thô và kho dữ liệu. Em cảm ơn thầy.

---

## 3. Kịch bản demo — khoảng 4 phút

> Câu định hướng: *"Phần dữ liệu em đã xong đến tầng Gold. Trang truy vết em sắp cho xem chạy trên Gold, không đọc đáp án của bộ mô phỏng. Phần xếp hạng nguyên nhân hiện là quy tắc sơ bộ; bộ phát hiện chính thức có ngưỡng và số đo precision/recall trên tập kiểm tra sẽ xong 16–17/10."*
>
> Nếu thời gian ít: làm **Bước 5 trước** (truy vết), các bước khác chỉ làm khi thầy hỏi.

**Bước 1 — Dữ liệu thô "bẩn" thật (8503, chế độ "File nguồn")**
- Mở 2 file Excel sổ nhập kho đã mở sẵn: *"Cùng là sổ nhập kho nhưng chi nhánh 1 ghi kiểu phiếu tiếng Việt có dòng Tổng cộng; chi nhánh 3 ghi kiểu bảng tiếng Anh, số lượng dính đơn vị như 53.6kg."*
- `pos` → `POS-07` → `pos_export_2024-04-12.json`, rồi `POS-08` cùng ngày: *"Chi nhánh 7 dùng phần mềm POS cũ: ngày giờ, tiền, tên cột đều khác chi nhánh 8."*

**Bước 2 — Bronze (8503, "Kho dữ liệu (Bronze/Silver/Gold)" → Bronze)**
- 4 con số trên cùng: 17 bảng, ~500 nghìn dòng, ~6.300 tệp, 0 tệp lỗi.
- Tab "Truy vấn SQL" → "Chạy truy vấn": *"Em truy vấn thẳng trên JSON thô, thấy 2 phiên bản POS dùng 2 cột tổng tiền khác nhau."*

**Bước 3 — Silver (gạt sang "Silver")**
- Tab đối soát: *"Bronze phải bằng Silver cộng dòng bị cách ly cộng dòng cấu trúc như dòng Tổng cộng. Cột unexplained_rows bằng 0 ở cả 7 nguồn."*
- Bảng cách ly: `timekeeping_punches / quet_trung` (~3%), `warehouse_receipts / nghi_go_gam_vao_cot_kg`: *"Lỗi kỹ thuật thật của máy chấm công và lỗi gõ tay, em tách ra kèm lý do chứ không xóa."*

**Bước 4 — Gold (gạt sang "Gold")**
- Bảng danh sách: *"Gold chia 3 nhóm: bảng chiều `dim_`, bảng sự kiện `fact_`, bảng phân tích `mart_`."*
- Tab "Xem bảng" → `dim_menu_item`, lọc món 1: *"Món gà giòn có 2 phiên bản: 35 nghìn đến 31/5, 37 nghìn từ 1/6. Đơn bán ngày nào thì gắn đúng giá và giá vốn của ngày đó — đây là SCD loại 2."*
- Tab "Truy vấn SQL" → "Chạy truy vấn" (câu có sẵn): *"Doanh thu, số đơn, AOV, COGS% từng chi nhánh: COGS% định mức khoảng 31%, đúng khoảng thường gặp của đồ ăn nhanh."*
- Nếu bị hỏi về Labor% (khoảng 8–12%, thấp): *"Đây mới là lương giờ trực tiếp theo chấm công, chưa có lương cố định quản lý, bảo hiểm, phụ cấp — em sẽ ghi rõ định nghĩa trong báo cáo."*

**Bước 5 — Truy vết nguyên nhân (8504) — PHẦN QUAN TRỌNG NHẤT**

*Ca 1: CN2, tuần 06/05/2024 (mặc định khi mở trang) — thiếu nhân sự ca tối*
- **① Bản đồ cảnh báo:** *"Mỗi ô là một chi nhánh một tuần, màu đỏ là doanh thu thấp bất thường so với kỳ vọng. Quản lý nhìn vào đây để biết nên xem chỗ nào."* Gạt "Số tín hiệu vận hành" để thấy các điểm nóng khác.
- **② Doanh thu so với kỳ vọng:** *"Kỳ vọng không phải là tuần trước, mà là: các chi nhánh cùng hạng tuần này bán bao nhiêu, nhân với độ chênh thường ngày của CN2 so với nhóm trong 8 tuần trước. Như vậy lễ, mưa, mùa vụ tác động cả nhóm đã bị trừ ra. CN2 thấp hơn kỳ vọng khoảng 48 triệu, tức 17%."*
- **③ Cây KPI:** *"Khoảng hụt nằm ở tại quầy và App nhiều nhất; số đơn giảm khoảng 14% còn giá trị mỗi đơn gần như không đổi — tức là mất khách/mất đơn, không phải khách mua ít đi."*
- **④ Tab P3 · Nhân sự & bếp:** *"Số ca bếp tối chỉ 11 so với kỳ vọng khoảng 23; thời gian chuẩn bị đơn App lên gần 21 phút so với 14; cửa hàng tự hủy 6,2% đơn App so với khoảng 1%; khách hủy vì chờ lâu tăng; điểm đánh giá Grab còn 4,3."* — đây là đúng chuỗi nhân quả.
- **⑤ Diễn biến:** *"Tuần 20/05 nhân sự đã về bình thường nhưng số đơn Grab vẫn thấp hơn kỳ vọng khoảng 19% vì điểm đánh giá còn thấp — sàn hạ thứ hạng hiển thị. Hậu quả đến sau nguyên nhân 1–2 tuần; nếu chỉ nhìn tuần đó sẽ không hiểu vì sao."*
- **⑥ Gợi ý nguyên nhân:** P3 đứng đầu, kèm bằng chứng chính.

*Ca 2: CN6, tuần 15/07 — đơn sàn không được ghi vào POS*
- ② doanh thu thấp hơn kỳ vọng khoảng 12%. Tab **P1b**: *"Grab báo 188 đơn hoàn thành nhưng cửa hàng chỉ ghi 163 trên POS; Shopee 129 so với 99. Bình thường độ phủ khoảng 97%. Doanh thu trên POS giảm không phải vì mất khách mà vì có đơn bán rồi không vào sổ — đây là lỗ hổng thất thoát tiền, phải đối soát nhiều nguồn mới thấy."*

*Ca 3: CN8, tuần 08/07 — thu ngân gian lận*
- Tab **P5 · Thu ngân**: *"NV0093 có 14 trên 143 hóa đơn bị hủy, gần 10%, trong khi các thu ngân khác cùng chi nhánh cùng tuần khoảng 1,4%. Em so từng người với chính đồng nghiệp của họ, và có hiệu chỉnh vì mỗi tuần thử nhiều người cùng lúc — nếu không thì tuần nào cũng có một người trông 'bất thường' do ngẫu nhiên."*

*Nếu còn thời gian:* CN4 tuần 13/05, tab **P1a**: hợp đồng 25% nhưng Grab thu hiệu dụng 30%, thu thừa khoảng 265 nghìn tuần đó. *"Bài này là tuân thủ hợp đồng nên em dùng quy tắc đối soát, không dùng thống kê."* Và chọn một tuần bình thường (ví dụ CN1 tuần 19/08): gợi ý đứng đầu là "Biến động bình thường" — trang không phải lúc nào cũng báo đỏ.

**Bước 6 (tùy chọn) — Dữ liệu mới về mỗi ngày**
```
.venv\Scripts\python -m simulator.run --profile calibration --days 1
.venv\Scripts\python -m pipeline.ingest --profile calibration
```
*"Mô phỏng một ngày vận hành mới rồi nạp — chỉ đúng 35 file của ngày đó, vài giây. Đây là cơ chế để Airflow chạy hằng ngày."*

---

## 4. Câu hỏi dễ gặp và gợi ý trả lời

**Dữ liệu này là dữ liệu giả à?**
Là dữ liệu mô phỏng, em nói rõ trong báo cáo. Dữ liệu đơn hàng của doanh nghiệp không công khai và không thu thập hợp pháp được. Bộ mô phỏng có mô hình nhân quả (nhân sự → tải bếp → thời gian chờ → hủy đơn → thứ hạng sàn → doanh thu), một số phân phối hiệu chỉnh từ dữ liệu giao dịch thật công khai. Ưu điểm là có đáp án cho từng sự cố nên đo được độ chính xác.

**Sao không lấy dữ liệu Kaggle?**
Không có bộ nào về chuỗi đồ ăn nhanh Việt Nam; nhiều bộ "đơn hàng nhà hàng" ghi rõ là nhà hàng giả định; và không bộ nào có đủ POS + đối soát sàn + kho + chấm công của cùng một doanh nghiệp.

**Truy vết nguyên nhân làm thế nào khi không dùng AI/ML?**
Phân tích chênh lệch, giống kế toán quản trị:
1. Ước lượng doanh thu kỳ vọng: so với chi nhánh cùng hạng cùng tuần (trừ được lễ, mưa, đổi giá), điều chỉnh theo độ chênh thường ngày của chính chi nhánh.
2. Tách khoảng chênh theo cây KPI: doanh thu = tổng các kênh của (số đơn × giá trị đơn).
3. Xem tín hiệu vận hành đi kèm, mỗi nguyên nhân có một "dấu vân tay" riêng: thiếu người thì ca bếp giảm + chuẩn bị lâu + hủy đơn tăng; đơn sàn không vào POS thì độ phủ POS giảm; gian lận thì hủy hóa đơn tập trung ở một thu ngân; hao hụt thì tiêu hao thực tế vượt định mức.
Ví dụ CN2: thấp hơn kỳ vọng 17% → chủ yếu do số đơn giảm 14%, giá trị đơn gần như không đổi → cùng tuần ca bếp tối giảm một nửa, chuẩn bị lâu hơn 7 phút, cửa hàng tự hủy đơn tăng gấp 6 → nguyên nhân là thiếu người ca tối.

**z là gì, sao không so với tuần trước?**
z là mức chênh so với kỳ vọng chia cho độ dao động tự nhiên của chỉ số đó (đo trên 8 tuần trước). So với tuần trước thì một tuần lễ hay mưa cũng thành "bất thường". Em dùng trung vị và độ lệch tuyệt đối trung vị (MAD) thay cho trung bình và độ lệch chuẩn, để một vài tuần sự cố trước đó không làm lệch mức nền.

**Trang truy vết đó đã là sản phẩm cuối chưa?**
Chưa. Phần dữ liệu và chỉ số đã hoàn chỉnh; phần xếp hạng nguyên nhân hiện là quy tắc sơ bộ, em thử trên tập phát triển thì 6 kịch bản và 1 tuần bình thường đều xếp đúng nguyên nhân ở hạng 1, nhưng vẫn có tín hiệu phụ. Tuần tới em làm bộ phát hiện chính thức, chọn ngưỡng trên tập phát triển và đo precision/recall một lần trên tập kiểm tra.

**Có trường hợp nào chưa tốt không?**
Có. Thất thoát kho ở CN9 tín hiệu yếu: kịch bản mất 1,5% lượng tồn mỗi ngày, mà tồn kho chỉ đủ 2–4 ngày bán, nên phần mất chỉ khoảng 4% lượng tiêu hao — gần bằng hao hụt bình thường. Kiểm kê 2 tuần một lần nên cũng không bắt được theo tuần. Em sẽ ghi nhận rõ trong phần đánh giá. Ngoài ra còn tín hiệu phụ, ví dụ hao hụt hàng tươi ở CN7 cũng làm điểm "thất thoát" tăng vì thịt cũng vượt định mức.

**Sao không dùng ML?**
(1) Không có dữ liệu sự cố thật đã gán nhãn để huấn luyện; (2) quản lý cần biết vì sao có cảnh báo, phương pháp thống kê và luật nghiệp vụ giải thích được từng bước; (3) bài như phí sàn sai hợp đồng thì so thẳng với hợp đồng là đúng nhất. Em có thể thêm một mô hình phát hiện bất thường làm phương án so sánh ở chương đánh giá.

**Làm sao biết đánh giá không "ăn gian" khi em tự tạo dữ liệu?**
Đường ống và trang truy vết không đọc đáp án. Có 2 tập kịch bản độc lập: chỉnh phương pháp trên tập đầu, tập sau khác chi nhánh, khác thời điểm, mức độ nhẹ hơn, chỉ dùng một lần khi đánh giá cuối. Các chỉnh sửa em làm hôm nay (dùng trung vị, MAD, hiệu chỉnh so sánh bội) đều xuất phát từ lỗi thấy trên tập đầu.

**Làm sạch dữ liệu rồi thì chắc đúng chưa?**
Em không "sửa" dữ liệu lỗi mà tách nó ra bảng cách ly kèm lý do; đối soát số dòng Bronze–Silver từng nguồn, và đối soát doanh thu Silver–Gold theo từng chi nhánh từng ngày bằng kiểm thử tự động.

**Khác gì một dashboard doanh thu bình thường?**
Dashboard chỉ cho thấy doanh thu giảm. Hệ thống này đối chiếu nhiều nguồn để chỉ ra giảm ở đâu, vì sao, và phân biệt biến động bình thường với biến động do sự cố.

**Sao không dùng Spark, cloud?**
Dữ liệu vài trăm MB, một máy xử lý trong vài chục giây. Dùng Spark là chồng công nghệ không cần thiết.

**Kịp tiến độ không?**
Phần dữ liệu (Bronze, Silver, Gold) đã xong sớm hơn lịch. Còn bộ phát hiện + đánh giá đến 17/10, giao diện + chạy tự động 18/10, 19–24/10 hoàn thiện báo cáo.

---

## 5. Không nên nói

- Đừng nói "dùng Faker sinh dữ liệu" — sai (bộ mô phỏng không dùng Faker) và làm yếu đề tài.
- Đừng nói "hệ thống đã phát hiện chính xác 100%" — mới thử trên vài tuần của tập phát triển, chưa đánh giá trên tập kiểm tra. Nói "trên tập phát triển các ca thử đều xếp đúng hạng 1, đánh giá chính thức làm tuần tới".
- Đừng mở trang "Kiểm chứng bộ mô phỏng" (đọc đáp án) xen giữa lúc demo truy vết — dễ bị hiểu là trang truy vết dùng đáp án. Nếu cần, nói rõ đó là trang kiểm chứng bộ mô phỏng, tách riêng.
- Đừng show ứng dụng cũ ở cổng 8501 (`app.py`) — bản thử nghiệm đầu đã thay thế. Nếu bị hỏi: *"Bản đầu em làm nhanh để thử ý tưởng; khi đánh giá lại thì dữ liệu các nguồn không khớp nhau và chưa có tầng DE thật, nên em làm lại từ phần dữ liệu."*
- Đừng nói tên một doanh nghiệp thật nào gắn với dữ liệu.
