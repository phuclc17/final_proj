"""Kiem tra nhanh toan he thong truoc buoi bao ve, demo.

    .venv/Scripts/python tools/kiem_tra_truoc_demo.py           # day du, khoang 3-5 phut
    .venv/Scripts/python tools/kiem_tra_truoc_demo.py --nhanh   # bo qua chay thu 30 trang giao dien va pytest

Kiem tra: Docker va hai dich vu (ung dung :8501, Airflow :8080), luot chay DAG gan nhat, ba kho du lieu, ket qua dbt,
so lieu bo phat hien co KHOP voi ket qua danh gia da chot trong docs/results (de demo khong hien so khac bao cao),
pytest, va chay thu moi trang ung dung tren ca ba tap. Ma thoat 0 = san sang, 1 = co muc loi.
Rieng phan doi chieu ket qua danh gia co doc dap an (qua analytics/evaluate.py) - chi de cham diem, nhu bao cao.
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "app")]
sys.stdout.reconfigure(encoding="utf-8")

from analytics import config as C  # noqa: E402
from analytics import detect, evaluate  # noqa: E402
from analytics.data import PROFILES, db_path, load_gold  # noqa: E402

APP_URL, AIRFLOW_URL = "http://localhost:8501", "http://localhost:8080"
CONTAINERS = ["fastfat-app", "fastfat-airflow", "fastfat-source-api"]
SOURCE_API_URL = "http://localhost:8600"
MARK = {"ok": "✔", "warn": "!", "fail": "✘"}
results = []


def report(status, group, name, detail=""):
    results.append((status, group))
    print(f"  {MARK[status]} {name}" + (f": {detail}" if detail else ""), flush=True)


def section(title):
    print(f"\n{title}", flush=True)


# ---------------------------------------------------------------- 1. docker
def check_docker():
    section("1. Docker")
    try:
        out = subprocess.run(["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.RunningFor}}"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        report("fail", "docker", "Docker", "không gọi được lệnh docker. Mở Docker Desktop rồi chạy: docker compose up -d")
        return
    if out.returncode != 0:
        report("fail", "docker", "Docker", "Docker Desktop chưa chạy. Mở Docker Desktop rồi chạy: docker compose up -d")
        return
    running = dict(line.split("\t", 1) for line in out.stdout.strip().splitlines() if "\t" in line)
    for c in CONTAINERS:
        st = running.get(c, "")
        report("ok" if st.startswith("Up") else "fail", "docker", c,
               st.split("\t")[0] if st else "không chạy. Chạy: docker compose up -d")
    # Streamlit trong container khong tu nap lai ma da sua -> canh bao neu container khoi dong truoc lan sua cuoi
    try:
        started = subprocess.run(["docker", "inspect", "-f", "{{.State.StartedAt}}", "fastfat-app"],
                                 capture_output=True, text=True, timeout=15).stdout.strip()
        t0 = datetime.fromisoformat(started[:26].rstrip("Z") + "+00:00") if started else None
        files = [p for d in ("app", "analytics") for p in (ROOT / d).rglob("*.py")]
        last = max(files, key=lambda p: p.stat().st_mtime)
        t1 = datetime.fromtimestamp(last.stat().st_mtime, tz=timezone.utc)
        if t0 and t1 > t0:
            report("warn", "docker", "Mã ứng dụng mới hơn container",
                   f"{last.relative_to(ROOT)} sửa sau khi container khởi động. Chạy: docker restart fastfat-app")
        elif t0:
            report("ok", "docker", "Container ứng dụng đang chạy mã mới nhất")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass


# ---------------------------------------------------------------- 2. dich vu
def check_services():
    section("2. Dịch vụ")
    try:
        r = requests.get(f"{APP_URL}/_stcore/health", timeout=5)
        report("ok" if r.text.strip() == "ok" else "fail", "service", f"Ứng dụng {APP_URL}", r.text.strip()[:40])
    except requests.RequestException:
        report("fail", "service", f"Ứng dụng {APP_URL}", "không phản hồi")
    try:
        h = requests.get(f"{AIRFLOW_URL}/health", timeout=5).json()
        bad = [k for k in ("metadatabase", "scheduler") if h.get(k, {}).get("status") != "healthy"]
        report("fail" if bad else "ok", "service", f"Airflow {AIRFLOW_URL}",
               ("lỗi: " + ", ".join(bad)) if bad else "cơ sở dữ liệu và bộ lập lịch hoạt động")
    except (requests.RequestException, ValueError):
        report("fail", "service", f"Airflow {AIRFLOW_URL}", "không phản hồi")
        return
    try:
        r = requests.get(f"{SOURCE_API_URL}/health", timeout=5)
        report("ok" if r.ok else "fail", "service", f"API nguồn POS đám mây, App {SOURCE_API_URL}",
               "hoạt động" if r.ok else f"mã {r.status_code}")
    except requests.RequestException:
        report("fail", "service", f"API nguồn POS đám mây, App {SOURCE_API_URL}",
               "không phản hồi: bộ kết nối sẽ không kéo được POS 8 chi nhánh và App. Chạy: docker compose up -d source-api")
    import airflow_client as af
    s = af.status(limit=1)
    if s is None:
        report("fail", "service", "DAG Airflow", "không đọc được qua REST API")
        return
    for d, what in ((af.SOURCE, "hệ thống nguồn 23:00"), (af.PIPELINE, "pipeline tự chạy khi có tệp mới")):
        if s[d]["dag"].get("is_paused"):
            report("warn", "service", f"DAG {d} đang tạm dừng", f"{what} sẽ không chạy; bật lại ở trang Vận hành hằng ngày")
    run, tasks = af.last_processing_run()
    if run is None:
        report("warn", "service", "Pipeline", "chưa có lượt nào xử lý dữ liệu")
        return
    state = run.get("state")
    when = (run.get("end_date") or run.get("start_date") or "")[:16].replace("T", " ")
    report({"success": "ok", "running": "warn", "queued": "warn"}.get(state, "fail"), "service",
           "Lượt pipeline gần nhất có xử lý dữ liệu", f"{state}, {when} UTC, {len(tasks)} bước, kích hoạt: {run['run_type']}")
    snap = ROOT / "data" / "_demo_snapshot" / "live"
    if not snap.exists():
        report("warn", "service", "Ảnh chụp cho demo dữ liệu mới", "chưa có: tools/chuan_bi_demo.py --luu")
    else:
        def until(base):
            with duckdb.connect(str(base / "warehouse" / "fastfat.duckdb"), read_only=True) as con:
                return con.sql("select max(date_day) from gold.fact_order").fetchone()[0]
        s_d, l_d = until(snap), until(ROOT / "data" / "live")
        report("ok" if s_d == l_d else "warn", "service", "Môi trường vận hành ở điểm bắt đầu demo",
               f"đúng, dữ liệu đến {l_d:%d/%m/%Y}" if s_d == l_d else
               f"đang ở {l_d:%d/%m/%Y}, điểm bắt đầu là {s_d:%d/%m/%Y}: chạy tools/chuan_bi_demo.py --khoi-phuc")


# ---------------------------------------------------------------- 3. kho du lieu
def check_warehouses():
    section("3. Kho dữ liệu")
    for label, prof in PROFILES.items():
        path = db_path(prof)
        if not path.exists():
            report("fail", "warehouse", label, f"chưa có {path.relative_to(ROOT)}")
            continue
        try:
            with duckdb.connect(str(path), read_only=True) as con:
                n_gold = con.sql("select count(*) from duckdb_tables() where schema_name = 'gold'").fetchone()[0]
                orders, d0, d1 = con.sql("select count(*), min(date_day), max(date_day) from gold.fact_order").fetchone()
                unexplained = con.sql("select coalesce(sum(unexplained_rows), 0) from silver.silver_row_reconciliation"
                                      ).fetchone()[0]
                last_run = None
                if prof == "live":
                    have = con.sql("select count(*) from duckdb_tables() where schema_name = 'ops' "
                                   "and table_name = 'pipeline_runs'").fetchone()[0]
                    if have:
                        last_run = con.sql("select step, status, finished_at from ops.pipeline_runs "
                                           "order by finished_at desc limit 1").fetchone()
        except duckdb.IOException:
            report("warn", "warehouse", label, "kho đang bị pipeline ghi, thử lại sau ít giây")
            continue
        except duckdb.Error as e:
            report("fail", "warehouse", label, f"lỗi đọc kho: {str(e)[:120]}")
            continue
        ok = n_gold >= 18 and orders > 0 and unexplained == 0
        report("ok" if ok else "fail", "warehouse", label,
               f"{n_gold} bảng Gold, " + f"{orders:,}".replace(",", ".") +
               f" đơn, {d0:%d/%m/%Y}–{d1:%d/%m/%Y}, dòng Bronze chưa giải thích: {unexplained}")
        if last_run:
            report("ok" if last_run[1] in ("thành công", "success", "ok") else "warn", "warehouse",
                   "  Lượt chạy hằng ngày gần nhất", f"{last_run[0]} · {last_run[1]} · {last_run[2]}")

    section("4. Kết quả dbt (run_results.json)")
    for label, prof in PROFILES.items():
        p = ROOT / "dbt" / f"target_{prof}" / "run_results.json"
        if not p.exists():
            report("fail", "dbt", label, "chưa có run_results.json, chạy: python -m pipeline.run_dbt --profile <tập> build")
            continue
        rr = json.loads(p.read_text(encoding="utf-8"))
        counts = pd.Series([r["status"] for r in rr["results"]]).value_counts().to_dict()
        bad = sum(v for k, v in counts.items() if k in ("fail", "error"))
        report("fail" if bad else "ok", "dbt", label,
               f"{len(rr['results'])} bước, " + ", ".join(f"{k} {v}" for k, v in counts.items())
               + f", lúc {rr['metadata']['generated_at'][:16].replace('T', ' ')} UTC")


# ---------------------------------------------------------------- 5. ket qua da chot
KEYS = ["su_co_bat_duoc", "top1_dung", "so_canh_bao", "bao_dong_gia", "precision", "recall_tuan", "f1"]


def check_frozen():
    section("5. Số liệu bộ phát hiện so với kết quả đánh giá đã chốt (docs/results)")
    for prof in ("calibration", "holdout"):
        label = {v: k for k, v in PROFILES.items()}[prof]
        meta = json.loads((ROOT / "docs" / "results" / f"{prof}_meta.json").read_text(encoding="utf-8"))
        if meta["score_alert"] != C.SCORE_ALERT or meta["z_alert"] != C.Z_ALERT:
            report("fail", "frozen", label, f"ngưỡng trong config ({C.SCORE_ALERT}, {C.Z_ALERT}) khác ngưỡng đã chốt "
                                            f"({meta['score_alert']}, {meta['z_alert']})")
            continue
        saved = pd.read_csv(ROOT / "docs" / "results" / f"{prof}_so_sanh.csv", index_col=0, encoding="utf-8-sig").iloc[0]
        G = load_gold(prof)
        scores = detect.score_all(G)
        weeks = [w for w in detect.usable_weeks(G) if (G["mart_branch_weekly"].query("week_start == @w").n_days == 7).all()]
        inc = evaluate.load_incidents(prof)
        labels = evaluate.label_weeks(weeks, inc)
        ours = evaluate.method_ours(G, scores, C.SCORE_ALERT)
        now, *_ = evaluate.evaluate(ours[ours.week_start.isin(weeks)], labels, inc, weeks, G["dim_branch"].shape[0])
        diff = [k for k in KEYS if str(now[k]) != str(saved[k]) and not _num_eq(now[k], saved[k])]
        report("fail" if diff else "ok", "frozen", label,
               ("KHÁC báo cáo ở " + ", ".join(f"{k}: {saved[k]} → {now[k]}" for k in diff)) if diff else
               f"khớp: bắt {now['su_co_bat_duoc']} sự cố, đúng nguyên nhân {now['top1_dung']}, F1 {now['f1']}")


def _num_eq(a, b):
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------- 6. kiem thu
def check_pytest():
    section("6. Kiểm thử tự động (pytest)")
    t = time.time()
    out = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True)
    tail = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr.strip()[-200:]
    report("ok" if out.returncode == 0 else "fail", "pytest", "pytest", f"{tail} ({time.time() - t:.0f} giây)")


def check_pages():
    section("7. Chạy thử mọi trang ứng dụng trên ba tập dữ liệu")
    from streamlit.testing.v1 import AppTest
    import os
    os.chdir(ROOT / "app")
    pages = [None, "views/connectors.py", "views/upload.py", "views/simulator.py", "views/daily_ops.py",
             "views/sources.py", "views/warehouse.py",
             "views/lineage.py", "views/data_ops.py", "views/overview.py", "views/alerts.py", "views/trace.py",
             "views/evaluation.py"]
    sys.path.insert(0, str(ROOT))
    from analytics import assistant
    if assistant.configured():          # trang tro ly chi co trong dieu huong khi da cau hinh mo hinh
        pages.append("views/assistant.py")
    for label in PROFILES:
        t, errors = time.time(), []
        for page in pages:
            at = AppTest.from_file(str(ROOT / "app" / "main.py"), default_timeout=300)
            at.session_state["profile"] = label
            at.run()
            if page:
                at.switch_page(page)
                at.run()
            if at.exception:
                errors.append(f"{page or 'trang chủ'}: {at.exception[0].message[:100]}")
        report("fail" if errors else "ok", "pages", label,
               ("; ".join(errors)) if errors else f"{len(pages)}/{len(pages)} trang chạy được ({time.time() - t:.0f} giây)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", action="store_true", help="bỏ qua pytest và chạy thử giao diện")
    args = ap.parse_args()
    t = time.time()
    print(f"Kiểm tra trước buổi demo · {datetime.now():%d/%m/%Y %H:%M}")
    check_docker()
    check_services()
    check_warehouses()
    check_frozen()
    if not args.nhanh:
        check_pytest()
        check_pages()
    n_fail = sum(s == "fail" for s, _ in results)
    n_warn = sum(s == "warn" for s, _ in results)
    print(f"\n{'SẴN SÀNG' if not n_fail else 'CHƯA SẴN SÀNG'}: {len(results)} mục, {n_fail} lỗi, {n_warn} lưu ý "
          f"({time.time() - t:.0f} giây)")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
