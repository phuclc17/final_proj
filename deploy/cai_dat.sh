#!/usr/bin/env bash
# Cai dat ban trinh dien tren may chu Ubuntu (22.04/24.04), chay MOT lan sau khi da co ma nguon va thu muc data/.
#   cd ~/fastfat && bash deploy/cai_dat.sh
# Chay lai duoc: buoc nao da xong thi bo qua hoac lam lai khong hai.
set -euo pipefail
cd "$(dirname "$0")/.."
DIR=$(pwd)
DC="docker compose -f docker-compose.yml -f deploy/docker-compose.server.yml --env-file deploy/.env"

say() { printf '\n== %s\n' "$*"; }

# ------------------------------------------------------------ 1. Docker
if ! command -v docker >/dev/null; then
  say "Cài Docker"
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER" || true
fi
SUDO=""; docker info >/dev/null 2>&1 || SUDO="sudo"
DC="$SUDO $DC"

# ------------------------------------------------------------ 2. Bo nho tam (may 4 GB RAM can them swap cho Metabase + Airflow)
if [ "$(swapon --show | wc -l)" -eq 0 ]; then
  say "Tạo 4 GB swap"
  sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

# ------------------------------------------------------------ 3. Mat khau va ten mien
if [ ! -f deploy/.env ]; then
  say "Tạo deploy/.env với mật khẩu ngẫu nhiên"
  IP=$(curl -fsS https://api.ipify.org)
  pw() { openssl rand -base64 18 | tr -dc 'A-Za-z0-9' | head -c 20; }
  cat > deploy/.env <<EOF
DOMAIN=${IP//./-}.sslip.io
AIRFLOW_ADMIN_PASSWORD=$(pw)
AIRFLOW_VIEWER_PASSWORD=$(pw)
PG_ADMIN_USER=fastfat
PG_ADMIN_PASSWORD=$(pw)
BI_READER_PASSWORD=$(pw)
MB_DB_PASSWORD=$(pw)
METABASE_ADMIN_EMAIL=admin@fastfat.local
METABASE_ADMIN_PASSWORD=$(pw)
SOURCE_API_TOKEN=$(pw)
EOF
  chmod 600 deploy/.env
fi
set -a; . deploy/.env; set +a

# ------------------------------------------------------------ 4. Du lieu va quyen ghi
for d in data/calibration data/holdout data/live data/_demo_snapshot/live; do
  if [ ! -f "$d/warehouse/fastfat.duckdb" ]; then
    echo "Thiếu $d/warehouse/fastfat.duckdb. Tải thư mục data/ lên trước (xem deploy/HUONG_DAN.md)."; exit 1
  fi
done
# container Airflow chay voi uid 50000, nhom 0: can quyen ghi vao data/, dbt/, landing...
sudo chown -R 50000:0 "$DIR"
sudo chmod -R g+rwX "$DIR"
sudo chown "$(id -u):$(id -g)" deploy/.env && chmod 600 deploy/.env   # docker compose doc tep nay bang tai khoan hien tai

# ------------------------------------------------------------ 5. Khoi dong
say "Dựng và khởi động các dịch vụ (lần đầu mất vài phút)"
$DC up -d --build

say "Chờ Airflow và Metabase sẵn sàng"
for i in $(seq 1 90); do
  a=$($DC exec -T airflow curl -fsS localhost:8080/health 2>/dev/null | grep -c healthy || true)
  m=$($DC exec -T app python -c "import requests;print(requests.get('http://metabase:3000/api/health',timeout=3).json()['status'])" 2>/dev/null || true)
  [ "$a" -ge 1 ] && [ "$m" = ok ] && break
  sleep 10
done

# ------------------------------------------------------------ 6. Kho phuc vu, Metabase, diem ban dau cua moi truong van hanh
PY="cd /opt/fastfat && /opt/fastfat-venv/bin/python"
for p in calibration holdout; do
  say "Đưa tập $p sang PostgreSQL"
  $DC exec -T airflow bash -c "$PY -m pipeline.publish --profile $p"
done
say "Đưa môi trường vận hành về điểm ban đầu"
$DC exec -T airflow bash -c "$PY tools/chuan_bi_demo.py --khoi-phuc"
say "Dựng dashboard Metabase"
$DC exec -T app python bi/metabase_setup.py --url http://metabase:3000
$DC restart app >/dev/null

say "Xong"
cat <<EOF
  Ứng dụng:  https://${DOMAIN}
  Metabase:  https://bi.${DOMAIN}       (dashboard nhúng sẵn trong trang Tổng quan)
  Airflow:   https://airflow.${DOMAIN}  tài khoản chỉ xem: giangvien / ${AIRFLOW_VIEWER_PASSWORD}
  Mật khẩu quản trị nằm trong deploy/.env (giữ riêng, không đưa vào báo cáo).
EOF
