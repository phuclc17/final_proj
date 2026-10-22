# Đưa bản trình diễn lên máy chủ để giảng viên chấm

Bản trình diễn chạy đúng bộ Docker Compose của dự án trên một máy chủ Ubuntu, thêm Caddy để có HTTPS và ba địa chỉ:

| Địa chỉ | Nội dung | Đăng nhập |
|---|---|---|
| `https://<DOMAIN>` | Ứng dụng Streamlit, đủ 12 trang | Không cần |
| `https://bi.<DOMAIN>` | Dashboard Metabase, đã nhúng trong trang Tổng quan | Không cần với dashboard công khai |
| `https://airflow.<DOMAIN>` | Airflow, xem hai DAG và lịch sử các lượt chạy | Tài khoản chỉ xem `giangvien` |

Khác với chạy trên máy cá nhân:

- Ứng dụng ở chế độ trình diễn. Trang Tải tệp lên bị ẩn, nút bật hoặc tắt lịch chạy bị ẩn, ô SQL chỉ chạy được một câu SELECT và không đọc được tệp ngoài kho.
- Người xem vẫn bấm được "Gửi dữ liệu ngày mới" ở trang Vận hành hằng ngày để thấy đường ống tự chạy. Mỗi đêm lúc 02:00, DAG `fastfat_dat_lai_demo` đưa môi trường vận hành về điểm ban đầu, nên người xem nào cũng thấy cùng một trạng thái khớp với báo cáo.
- Hệ thống nguồn không tự sinh ngày mới lúc 23:00.
- PostgreSQL, API nguồn giả lập và các cổng nội bộ không mở ra ngoài. Trợ lý phân tích không bật.

## 1. Thuê máy chủ

Cấu hình tối thiểu: Ubuntu 24.04, 2 vCPU, 4 GB RAM, 40 GB ổ đĩa, có IPv4 công khai. Máy 8 GB RAM chạy thoải mái hơn. Mở cổng 22, 80, 443 trong tường lửa của nhà cung cấp.

## 2. Đưa mã nguồn và dữ liệu lên

Trên máy cá nhân, trong thư mục dự án, chạy bằng Git Bash. Thay `<IP>` bằng IP máy chủ, `ubuntu` bằng tên tài khoản của nhà cung cấp.

```bash
git archive --format=tar.gz -o "$TEMP/fastfat_code.tgz" HEAD
tar -czf "$TEMP/fastfat_data.tgz" data/calibration data/holdout data/live data/_demo_snapshot data/public_reference
scp "$TEMP/fastfat_code.tgz" "$TEMP/fastfat_data.tgz" ubuntu@<IP>:~
```

Dữ liệu nén khoảng vài GB, nên tải lên mất từ vài phút đến vài chục phút tùy mạng.

Trên máy chủ:

```bash
mkdir -p ~/fastfat && cd ~/fastfat
tar -xzf ~/fastfat_code.tgz && tar -xzf ~/fastfat_data.tgz
bash deploy/cai_dat.sh
```

Tập lệnh cài Docker nếu chưa có, tạo swap, sinh `deploy/.env` với mật khẩu ngẫu nhiên và tên miền dạng `<IP>.sslip.io`, khởi động các dịch vụ, đưa ba tập dữ liệu sang PostgreSQL, dựng dashboard Metabase. Cuối cùng nó in ba địa chỉ và mật khẩu tài khoản chỉ xem của Airflow. Lần đầu mất khoảng 15 đến 30 phút.

## 3. Kiểm tra trước khi gửi đường dẫn

- Mở `https://<DOMAIN>`, xem trang Tổng quan có dashboard, trang Trung tâm cảnh báo có cảnh báo, trang Truy vết mở được.
- Ở trang Vận hành hằng ngày, bấm "Gửi dữ liệu ngày mới" với 7 ngày. Sau vài phút phải có hai cảnh báo tuần 23/09/2024: CN1 hoa hồng sàn sai hợp đồng, CN3 thiếu nhân sự.
- Đăng nhập Airflow bằng tài khoản `giangvien` và xem DAG `fastfat_pipeline`.
- Nếu muốn đưa về điểm ban đầu ngay mà không chờ đến 02:00, chạy:

```bash
cd ~/fastfat
docker compose -f docker-compose.yml -f deploy/docker-compose.server.yml --env-file deploy/.env \
  exec -T airflow bash -c "cd /opt/fastfat && /opt/fastfat-venv/bin/python tools/chuan_bi_demo.py --khoi-phuc"
```

## 4. Vận hành và tắt

```bash
DC="docker compose -f docker-compose.yml -f deploy/docker-compose.server.yml --env-file deploy/.env"
$DC ps                 # trạng thái
$DC logs -f app        # nhật ký ứng dụng
$DC restart            # khởi động lại
$DC down               # tắt (dữ liệu giữ nguyên)
```

Cập nhật mã sau này: tải `fastfat_code.tgz` mới lên, chạy `cd ~/fastfat && sudo tar -xzf ~/fastfat_code.tgz` (thư mục đã được giao cho tài khoản 50000 của container Airflow), rồi chạy lại `bash deploy/cai_dat.sh`.

Sau khi có điểm, xóa máy chủ ở trang của nhà cung cấp để không mất thêm phí.
