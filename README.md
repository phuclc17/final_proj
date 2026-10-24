# Fast&Fat: nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn

Mã nguồn khóa luận tốt nghiệp "Xây dựng nền tảng tích hợp và phân tích dữ liệu vận hành đa nguồn hỗ trợ truy vết nguyên nhân biến động doanh thu cho chuỗi kinh doanh đồ ăn nhanh".

Báo cáo đầy đủ: [docs/BaoCao_KhoaLuan.pdf](docs/BaoCao_KhoaLuan.pdf).

## Bài toán

Một chuỗi đồ ăn nhanh 11 chi nhánh bán qua bốn kênh: tại quầy, ứng dụng riêng, GrabFood và ShopeeFood. Dữ liệu vận hành nằm rải rác ở sáu hệ thống: POS hai phiên bản, ứng dụng đặt hàng, báo cáo đối soát của sàn, sổ nhập kho, phiếu kiểm kê và máy chấm công. Mỗi hệ thống có định dạng, mã định danh và lỗi nhập liệu riêng. Khi doanh thu giảm, quản lý chỉ thấy con số tổng mà không biết nguyên nhân.

Nền tảng gom dữ liệu từ các hệ thống đó, làm sạch, dựng kho dữ liệu hình sao, rồi quét mọi chi nhánh × tuần để phát hiện năm nhóm nguyên nhân: sàn tính sai hoa hồng hoặc đơn sàn không vào POS, hao hụt nguyên liệu, thiếu nhân sự, thất thoát kho và gian lận tại quầy. Mỗi cảnh báo có ước tính thiệt hại, đề xuất xử lý và đường dẫn về đúng dòng trong tệp gốc.

Dữ liệu vận hành của doanh nghiệp không công khai, nên đề tài dùng một bộ mô phỏng đóng vai các hệ thống nguồn. Đường ống và bộ phát hiện không đọc bộ mô phỏng hay đáp án; đáp án chỉ dùng để chấm kết quả.

## Kiến trúc

```
Hệ thống nguồn            Thu thập                Kho DuckDB (dbt)                   Phục vụ
(bộ mô phỏng)
POS, App      ── API ──┐
Sàn, kho, chấm công ───┼─ hợp đồng dữ liệu ─► Bronze ─► Silver ─► Gold ─► bộ phát hiện ─► PostgreSQL ─► Metabase
Tệp tải lên  ──────────┘   cửa chặn chất lượng   (thô)   (sạch,   (hình sao,             (kho phục vụ)
                                                          cách ly)  chỉ số)      ứng dụng Streamlit
Điều phối: Apache Airflow, hai DAG nối bằng Dataset. Đóng gói: Docker Compose.
```

| Thư mục | Nội dung |
|---|---|
| `simulator/` | Bộ mô phỏng các hệ thống nguồn: sinh sự kiện một lần, mỗi hệ thống xuất phần nó thấy kèm lỗi riêng; kịch bản sự cố có đáp án |
| `source_api/` | API giả lập của POS đám mây và ứng dụng (FastAPI) |
| `pipeline/` | Thu thập (`extract.py`, `intake.py`, `contracts.py`), nạp Bronze (`ingest.py`), cửa chặn chất lượng, chạy dbt, publish, điều phối một lượt (`run_daily.py`) |
| `dbt/` | Silver (làm sạch, cách ly, giải quyết định danh) và Gold (6 bảng sự kiện, 7 bảng chiều, 2 chiều SCD2, 5 bảng chỉ số); 158 kiểm thử dữ liệu |
| `analytics/` | Bộ phát hiện, đề xuất xử lý, đánh giá, phân tích độ nhạy, trợ lý phân tích |
| `app/` | Ứng dụng Streamlit 14 trang |
| `airflow/`, `docker/`, `docker-compose.yml` | Điều phối và đóng gói |
| `bi/` | Dựng dashboard Metabase bằng mã |
| `deploy/` | Cấu hình chạy trên máy chủ (Caddy, HTTPS) |
| `tests/` | 89 kiểm thử pytest |
| `docs/` | Báo cáo, kết quả đánh giá (`docs/results/`), mã nguồn báo cáo và hình (`docs/report/`) |

## Kết quả chính

- Đường ống: 211 bước dbt (50 mô hình, 3 bảng hạt giống, 158 kiểm thử) đều đạt; số dòng Bronze bằng Silver cộng cách ly cộng dòng cấu trúc ở cả 7 nguồn; doanh thu thuần ở Gold khớp Silver tuyệt đối theo chi nhánh × ngày.
- Bộ phát hiện, ngưỡng chốt trên tập phát triển rồi chạy tập kiểm tra một lần:

| Tập | Sự cố phát hiện | F1 | Độ trễ trung vị |
|---|---|---|---|
| Phát triển | 5/6 | 0,79 | 6 ngày |
| Kiểm tra | 4/6 | 0,52 | 6 ngày |

Đối chứng chỉ theo dõi doanh thu bắt 1/6 sự cố trên tập kiểm tra; Isolation Forest bắt 2/6. Phân tích lỗi và các sự cố bị bỏ sót ở [docs/results/KET_QUA_DANH_GIA.md](docs/results/KET_QUA_DANH_GIA.md).

## Chạy thử

Yêu cầu: Python 3.12, Docker Desktop.

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt        # Linux, macOS: .venv/bin/pip

# Sinh dữ liệu nguồn 182 ngày cho hai tập (khoảng 3,5 phút mỗi tập)
.venv/Scripts/python -m simulator.run --profile calibration --days 182 --reset
.venv/Scripts/python -m simulator.run --profile holdout --days 182 --reset

# Nạp Bronze, dựng Silver và Gold, chạy kiểm thử
.venv/Scripts/python -m pipeline.ingest --profile calibration
.venv/Scripts/python -m pipeline.run_dbt --profile calibration build

# Đánh giá bộ phát hiện
.venv/Scripts/python -m analytics.evaluate --profile calibration

# Bật toàn bộ hệ thống
docker compose up -d --build
```

| Địa chỉ | Thành phần |
|---|---|
| http://localhost:8501 | Ứng dụng |
| http://localhost:8080 | Airflow (admin / admin) |
| http://localhost:3000 | Metabase |
| http://localhost:8600/docs | API nguồn giả lập |

Hướng dẫn đầy đủ, gồm môi trường vận hành hằng ngày và dựng dashboard: [HUONG_DAN_CHAY.txt](HUONG_DAN_CHAY.txt). Mật khẩu trong `docker-compose.yml` là giá trị mặc định cho máy cá nhân; khi chạy trên máy chủ, `deploy/cai_dat.sh` sinh mật khẩu ngẫu nhiên.

## Giới hạn

Dữ liệu là mô phỏng, chưa kiểm chứng trên dữ liệu thật của doanh nghiệp. Một số phân phối hành vi mua hàng được hiệu chỉnh từ bộ dữ liệu giao dịch công khai The Bread Basket (OpenML 43422). Mỗi tập có sáu kịch bản sự cố, nên các tỷ lệ phát hiện chỉ mang tính chỉ báo. Chi tiết ở mục 6.3 của báo cáo.
