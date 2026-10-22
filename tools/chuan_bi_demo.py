"""Anh chup tap 'Van hanh thu' de demo luong "du lieu moi -> pipeline tu xu ly -> canh bao" lap lai duoc.

  .venv/Scripts/python tools/chuan_bi_demo.py --luu        # chup trang thai hien tai (lam 1 lan, khi du lieu o diem mong muon)
  .venv/Scripts/python tools/chuan_bi_demo.py --khoi-phuc  # truoc moi lan tap duot / bao ve: quay ve anh chup

Khoi phuc: cho Airflow ranh, tam dung 2 DAG, chep lai tep nguon + trang thai bo mo phong + kho DuckDB, dua lai sang
Postgres de dashboard khop, roi bat lai DAG. Anh chup nam o data/_demo_snapshot/ (khong dua vao git).
"""
import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parent.parent
LIVE, SNAP = ROOT / "data" / "live", ROOT / "data" / "_demo_snapshot" / "live"
PARTS = ["source_systems", "_simulator_state", "warehouse", "ground_truth", "landing", "_he_thong_nguon"]
AF = os.environ.get("AIRFLOW_URL", "http://localhost:8080").rstrip("/") + "/api/v1"
AUTH = (os.environ.get("AIRFLOW_USER", "admin"), os.environ.get("AIRFLOW_PASSWORD", "admin"))
DAGS = ["fastfat_nguon", "fastfat_pipeline"]
sys.stdout.reconfigure(encoding="utf-8")


def data_date(base):
    import duckdb
    with duckdb.connect(str(base / "warehouse" / "fastfat.duckdb"), read_only=True) as con:
        return con.sql("select max(date_day) from gold.fact_order").fetchone()[0]


def copy(src, dst):
    for part in PARTS:
        if (dst / part).exists():
            shutil.rmtree(dst / part)
        if (src / part).exists():
            shutil.copytree(src / part, dst / part)


def airflow(method, path, params=None, json_body=None):
    """Goi REST API cua Airflow bang thu vien chuan (chay duoc ca trong moi truong pipeline khong co requests)."""
    url = f"{AF}{path}" + (f"?{parse.urlencode(params)}" if params else "")
    data = json.dumps(json_body).encode() if json_body is not None else None
    req = request.Request(url, data=data, method=method, headers={
        "Authorization": "Basic " + base64.b64encode(f"{AUTH[0]}:{AUTH[1]}".encode()).decode(),
        "Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=10) as r:
            return json.loads(r.read() or b"null")
    except (error.URLError, OSError, ValueError):
        return None


def busy():
    for d in DAGS:
        for state in ("running", "queued"):
            r = airflow("GET", f"/dags/{d}/dagRuns", params={"state": state, "limit": 1})
            if r and r["total_entries"]:
                return d
    return None


def set_paused(paused):
    for d in DAGS:
        airflow("PATCH", f"/dags/{d}", params={"update_mask": "is_paused"}, json_body={"is_paused": paused})


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--luu", action="store_true")
    g.add_argument("--khoi-phuc", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    if args.luu:
        SNAP.mkdir(parents=True, exist_ok=True)
        copy(LIVE, SNAP)
        print(f"Đã lưu ảnh chụp tập Vận hành thử, dữ liệu đến ngày {data_date(SNAP):%d/%m/%Y} ({time.time() - t0:.0f} giây)")
        return
    if not SNAP.exists():
        sys.exit("Chưa có ảnh chụp. Chạy: tools/chuan_bi_demo.py --luu")
    for _ in range(60):
        d = busy()
        if not d:
            break
        print(f"Đang chờ {d} chạy xong...")
        time.sleep(10)
    set_paused(True)
    try:
        copy(SNAP, LIVE)
        print(f"Đã khôi phục dữ liệu đến ngày {data_date(LIVE):%d/%m/%Y}, đang đưa lại sang Postgres...")
        r = subprocess.run([sys.executable, "-m", "pipeline.publish", "--profile", "live"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print((r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "")
    finally:
        set_paused(False)
    print(f"Xong sau {time.time() - t0:.0f} giây. Bấm 'Gửi dữ liệu ngày mới' trong ứng dụng để demo.")


if __name__ == "__main__":
    main()
