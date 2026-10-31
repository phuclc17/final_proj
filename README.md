# F&B Ops Data Platform

Nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn, hỗ trợ truy vết nguyên nhân biến động doanh thu cho chuỗi F&B.

Khóa luận tốt nghiệp ngành Công nghệ thông tin, Trường Công nghệ và Thiết kế, Đại học Kinh tế TP. Hồ Chí Minh.
Sinh viên thực hiện: Lê Cao Phúc. Giảng viên hướng dẫn: TS. Ngô Tấn Vũ Khanh.

[Trang giới thiệu](https://phuclc17.github.io/fnb-ops-data-platform/) ·
[Ứng dụng trực tuyến](https://phuclc17.github.io/fnb-ops-data-platform/app/) ·
[Video trình diễn](https://phuclc17.github.io/fnb-ops-data-platform/#video) ·
[Báo cáo PDF](docs/BaoCao_KhoaLuan.pdf) ·
[Tài liệu dbt](https://phuclc17.github.io/fnb-ops-data-platform/dbt/)

Ứng dụng trực tuyến mở được ngay trên trình duyệt, không cần cài đặt. Nếu trang đang khởi động, chờ khoảng một đến hai phút.

![Truy vết nguyên nhân](docs/images/truy_vet.png)

## Bài toán

Một chuỗi đồ ăn nhanh 11 chi nhánh bán tại quầy, qua ứng dụng riêng, GrabFood và ShopeeFood. Dữ liệu vận hành nằm ở bảy hệ thống, mỗi hệ thống một định dạng, một bộ mã và kiểu lỗi nhập liệu riêng. Khi doanh thu hay lợi nhuận giảm, quản lý chỉ thấy con số tổng.

Nền tảng đưa dữ liệu của bảy hệ thống về một kho, rồi đối chiếu chéo để phát hiện năm loại sự cố:

| Mã | Sự cố | Dữ liệu đối chiếu |
|---|---|---|
| P1 | Sàn tính sai hoa hồng, đơn sàn không được nhập POS | Báo cáo đối soát sàn, POS, hợp đồng |
| P2 | Hao hụt nguyên liệu vượt định mức | Sổ nhập kho, phiếu kiểm kê, lượng bán theo công thức |
| P3 | Thiếu nhân sự, bếp quá tải | Chấm công, POS, ứng dụng, báo cáo sàn |
| P4 | Thất thoát hàng giá trị cao | Phiếu kiểm kê, sổ nhập kho, lượng bán |
| P5 | Gian lận tại quầy | Hóa đơn hủy, hoàn, giảm giá theo thu ngân |

Mỗi cảnh báo có nguyên nhân, mức thiệt hại ước tính, đề xuất xử lý và đường dẫn về đúng dòng trong tệp gốc.

Fast&Fat là chuỗi giả định. Dữ liệu vận hành của doanh nghiệp không công khai, nên một bộ mô phỏng đóng vai các hệ thống nguồn và sinh kèm hai tập sự cố có đáp án để đánh giá. Đường ống và bộ phát hiện không đọc bộ mô phỏng hay đáp án.

## Một vòng sản phẩm

Ví dụ trên môi trường vận hành, tuần 23–29/09/2024. Ứng dụng trực tuyến giữ đúng trạng thái sau vòng này.

1. Dữ liệu đến. Cuối mỗi ngày, POS đám mây và ứng dụng đặt hàng có hóa đơn mới trên API; POS cài tại máy và máy chấm công xuất tệp; báo cáo đối soát tuần của GrabFood, ShopeeFood và sổ nhập kho được gửi vào vùng tiếp nhận.
2. Đường ống tự chạy. Airflow thấy dữ liệu mới và chạy bảy bước: kéo API theo mốc ngày, phát hiện tệp mới, nạp Bronze, cửa chặn chất lượng, dbt dựng Silver và Gold kèm 158 kiểm thử, quét cảnh báo, đưa sang PostgreSQL. Lượt bảy ngày này nạp 236 tệp, 18.798 dòng trong 146 giây.
3. Cảnh báo. Trung tâm cảnh báo có hai cảnh báo mới. Cảnh báo đầu: ShopeeFood tính hoa hồng 27% trên doanh thu món 10.565.000 đ của CN1, trong khi hợp đồng là 22%, thu thừa 528.250 đ. Cảnh báo thứ hai: CN3 thiếu nhân sự ca tối.
4. Truy vết. Trang Truy vết nguyên nhân cho kết luận, điểm của từng giả thuyết và doanh thu so với kỳ vọng. Mục bằng chứng gốc hiện dòng đối soát kèm tên tệp `ShopeeFood_DoiSoat_20240923_20240929.xlsx` và số dòng; nút "Mở tệp gốc" mở đúng dòng đó trong tệp nguyên văn.
5. Xử lý. Đề xuất giao cho kế toán công nợ sàn: đối chiếu với phụ lục hợp đồng, gửi sàn yêu cầu hoàn 528.250 đ kèm bảng đối soát, theo dõi tỷ lệ hoa hồng ở kỳ kế tiếp. Nếu tuần sau tỷ lệ vẫn lệch, cảnh báo xuất hiện lại.

## Chức năng

Mọi trang dùng chung bộ lọc môi trường dữ liệu, chi nhánh và khoảng thời gian. Môi trường vận hành nhận dữ liệu mới; hai tập đánh giá là dữ liệu cố định dùng để chấm bộ phát hiện.

| Nhóm | Trang | Chức năng |
|---|---|---|
| Nguồn dữ liệu | Kết nối nguồn | Kênh thu thập của từng nguồn, dữ liệu mới nhất, độ trễ, trạng thái bộ kết nối API, tệp bị từ chối |
| | Tải tệp lên | Gửi báo cáo sàn, sổ kho, phiếu kiểm kê; tệp được nhận dạng theo nội dung và báo đã nhận, thay bản cũ, trùng hoặc từ chối kèm lý do |
| | Tệp nguồn | Xem nguyên văn mọi tệp đã nhận, lọc theo nguồn, chi nhánh, ngày |
| Dữ liệu | Vận hành hằng ngày | Đưa dữ liệu ngày mới vào, theo dõi bảy bước của đường ống, xem cảnh báo của tuần vừa xử lý |
| | Kho dữ liệu | Xem bảng Bronze, Silver, Gold; chạy câu SQL chỉ đọc, có sẵn truy vấn mẫu |
| | Mô hình và phả hệ | Phả hệ của từng bảng và lược đồ hình sao, sinh từ siêu dữ liệu dbt |
| | Chất lượng dữ liệu | Kết quả cửa chặn và 158 kiểm thử, đối soát số dòng giữa các tầng, dòng bị cách ly kèm lý do |
| Phân tích vận hành | Tổng quan | Doanh thu, số đơn, AOV, COGS%, Labor%, hủy đơn theo kênh và chi nhánh |
| | Trung tâm cảnh báo | Bản đồ nhiệt chi nhánh × tuần, danh sách cảnh báo sắp theo thiệt hại ước tính, chỉnh được ngưỡng |
| | Truy vết nguyên nhân | Kết luận, đề xuất xử lý, cây KPI, điểm từng giả thuyết, bằng chứng gốc mở tới đúng dòng trong tệp nguồn |
| Kiểm chứng | Bộ mô phỏng | Sự thật của một ngày đặt cạnh những gì từng hệ thống ghi lại; lịch và tác động của các kịch bản sự cố |
| | Đánh giá bộ phát hiện | Kết quả trên hai tập, so với phương án cơ sở, độ nhạy theo ngưỡng và theo cách tính mức kỳ vọng |

Bản trực tuyến chỉ đọc nên không có trang Tải tệp lên và nút đưa dữ liệu mới; Tổng quan vẽ trực tiếp từ kho thay cho dashboard Metabase.

## Kiến trúc

![Kiến trúc](docs/images/kien_truc.png)

| Chặng | Công nghệ | Nội dung |
|---|---|---|
| Thu thập | Python, FastAPI | Kéo API của POS đám mây và ứng dụng theo mốc ngày; nhận tệp theo hợp đồng dữ liệu |
| Bronze | DuckDB | Lưu nguyên văn kèm tệp và số dòng gốc; nạp tăng dần theo mã băm tệp |
| Silver | dbt | Hợp nhất hai phiên bản POS, giải quyết định danh giữa sáu hệ mã, cách ly dòng lỗi kèm lý do |
| Gold | dbt | Lược đồ hình sao: 6 bảng sự kiện, 7 bảng chiều, 2 chiều SCD2, 5 bảng chỉ số; 158 kiểm thử |
| Phân tích | Python | Mức kỳ vọng theo nhóm chi nhánh cùng hạng, cây KPI, năm bộ phát hiện, đề xuất xử lý |
| Phục vụ | PostgreSQL, Metabase, Streamlit | Kho phục vụ chỉ đọc, dashboard kinh doanh, ứng dụng 14 trang |
| Điều phối | Airflow, Docker Compose | Hai DAG nối bằng Dataset: dữ liệu mới về thì đường ống tự chạy |

## Giao diện

| | |
|---|---|
| ![Trung tâm cảnh báo](docs/images/canh_bao.png) | ![Vận hành hằng ngày](docs/images/van_hanh.png) |
| Trung tâm cảnh báo: mọi chi nhánh, mọi tuần, sắp theo thiệt hại ước tính | Vận hành hằng ngày: một lượt đường ống với bảy ngày dữ liệu mới |
| ![Dashboard Metabase](docs/images/tong_quan.png) | ![Phả hệ dbt](docs/images/pha_he.png) |
| Dashboard Metabase trên kho phục vụ PostgreSQL | Phả hệ của bảng fact_order, sinh từ siêu dữ liệu dbt |
| ![Dữ liệu thô](docs/images/du_lieu_tho.png) | ![Bộ mô phỏng](docs/images/mo_phong.png) |
| Dữ liệu thô của các hệ thống nguồn | Một ngày của chi nhánh: sự thật đặt cạnh những gì các hệ thống ghi lại |

## Kết quả

Ngưỡng cảnh báo được chọn trên tập phát triển rồi chạy tập kiểm tra đúng một lần.

| Tập | Sự cố phát hiện | Đúng nguyên nhân | Precision | Recall theo tuần | F1 | Độ trễ trung vị |
|---|---|---|---|---|---|---|
| Phát triển | 5/6 | 5/5 | 0,72 | 0,87 | 0,79 | 6 ngày |
| Kiểm tra | 4/6 | 3/4 | 0,50 | 0,54 | 0,52 | 6 ngày |

Trên tập kiểm tra, chỉ theo dõi doanh thu phát hiện 1/6 sự cố (F1 0,11), Isolation Forest phát hiện 2/6 (F1 0,15). Thất thoát kho với nhịp kiểm kê hai tuần không phát hiện được ở cả hai tập. Chi tiết và phân tích lỗi: [docs/results/KET_QUA_DANH_GIA.md](docs/results/KET_QUA_DANH_GIA.md).

Về dữ liệu: 211/211 bước dbt đạt trên cả ba môi trường; số dòng Bronze bằng Silver cộng cách ly cộng dòng cấu trúc ở cả bảy nguồn; doanh thu thuần ở Gold khớp Silver theo từng chi nhánh và ngày. Một lượt bảy ngày dữ liệu mới đi từ hệ thống nguồn đến cảnh báo trong 146 giây.

## Mã nguồn

| Thư mục | Nội dung |
|---|---|
| `simulator/` | Bộ mô phỏng các hệ thống nguồn và kịch bản sự cố |
| `source_api/` | API giả lập của POS đám mây và ứng dụng đặt hàng |
| `pipeline/` | Thu thập, hợp đồng dữ liệu, nạp Bronze, cửa chặn chất lượng, đưa sang kho phục vụ |
| `dbt/` | Mô hình Silver, Gold và kiểm thử dữ liệu |
| `analytics/` | Bộ phát hiện, đề xuất xử lý, đánh giá, phân tích độ nhạy |
| `app/` | Ứng dụng Streamlit |
| `airflow/`, `docker/`, `docker-compose.yml` | Điều phối và đóng gói |
| `bi/` | Dựng dashboard Metabase bằng mã |
| `deploy/` | Cấu hình chạy trên máy chủ và trên Hugging Face Spaces |
| `tests/` | 89 kiểm thử pytest |
| `docs/` | Báo cáo, kết quả đánh giá, hình |

## Chạy trên máy

<details>
<summary>Yêu cầu Python 3.12 và Docker Desktop</summary>

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt        # Linux, macOS: .venv/bin/pip

# Sinh dữ liệu nguồn 182 ngày cho hai tập đánh giá, khoảng 3,5 phút mỗi tập
.venv/Scripts/python -m simulator.run --profile calibration --days 182 --reset
.venv/Scripts/python -m simulator.run --profile holdout --days 182 --reset

# Nạp Bronze, dựng Silver và Gold, chạy kiểm thử (làm tương tự với --profile holdout)
.venv/Scripts/python -m pipeline.ingest --profile calibration
.venv/Scripts/python -m pipeline.run_dbt --profile calibration build

# Đánh giá bộ phát hiện
.venv/Scripts/python -m analytics.evaluate --profile calibration

# Môi trường vận hành và toàn bộ dịch vụ
.venv/Scripts/python -m pipeline.run_daily --init-live
docker compose up -d --build
```

| Địa chỉ | Thành phần |
|---|---|
| http://localhost:8501 | Ứng dụng |
| http://localhost:8080 | Airflow (admin / admin) |
| http://localhost:3000 | Metabase |
| http://localhost:8600/docs | API nguồn giả lập |

Dashboard Metabase được dựng bằng `python -m pipeline.publish --profile <tập>` rồi `python bi/metabase_setup.py`. Mật khẩu trong `docker-compose.yml` là giá trị mặc định cho máy cá nhân.

</details>
