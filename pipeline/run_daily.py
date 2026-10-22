"""
Pipeline du lieu cua mot tap (mac dinh 'live' - moi truong van hanh thu, KHONG phai tap danh gia).
He thong nguon (o day la bo mo phong, buoc 'simulate') chay RIENG: phan mem co API (POS dam may, App) ghi vao kho
cua chinh no, phan mem chi xuat tep thi ghi tep vao vung tiep nhan. Pipeline:
  0. extract  : bo ket noi keo du lieu moi tu API ve vung tiep nhan (chi tap live); API loi khong chan cac nguon tep
  1. check    : co tep nguon moi chua nap khong? khong co -> thoat ma 99 (Airflow danh dau bo qua cac buoc sau)
  2. ingest   : nap file moi vao Bronze
  3. quality  : cua chan chat luong dau vao (do moi, khoi luong, tep loi, cau truc); muc 'chan' -> dung truoc dbt
  4. dbt      : dbt build (Silver + Gold + kiem thu; mo hinh giai ma JSON chay tang dan)
  5. detect   : quet bo chi so giam sat, ghi canh bao vao schema ops
  6. publish  : dua Gold, ops sang kho phuc vu PostgreSQL (Metabase, tro ly AI doc tu do)

  python -m pipeline.run_daily --profile live --step simulate --days 7   # he thong nguon xuat tep 7 ngay moi
  python -m pipeline.run_daily --profile live                 # pipeline: extract -> check -> ... -> publish
  python -m pipeline.run_daily --profile live --step ingest   # chay 1 buoc (Airflow goi tung buoc)
  python -m pipeline.run_daily --init-live                    # tao tap live tu ban sao tap phat trien (1 lan)
Moi lan chay ghi 1 dong vao ops.pipeline_runs (thoi diem, buoc, thoi gian, trang thai, ghi chu).
"""
import argparse
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from . import dbutil

ROOT = Path(__file__).resolve().parent.parent
STEPS = ["extract", "check", "ingest", "quality", "dbt", "detect", "publish"]   # "simulate" la he thong nguon
NO_NEW_FILES = 99
QUIET = 98    # buoc chay xong, khong co gi moi: khong ghi nhat ky (keo API moi gio ma khong co ngay moi)
WARN = 97     # buoc gap su co nhung khong chan cac buoc sau (API nguon khong lay duoc)
SETTLE_SECONDS = 5   # tep vua ghi trong khoang nay coi nhu dang duoc ghi do, cho them


def db_file(profile):
    return ROOT / "data" / profile / "warehouse" / "fastfat.duckdb"


def log_run(profile, run_id, step, seconds, status, note):
    with dbutil.connect(db_file(profile)) as con:
        con.execute("create schema if not exists ops")
        con.execute("""create table if not exists ops.pipeline_runs (
            run_id varchar, step varchar, finished_at timestamp, seconds double, status varchar, note varchar)""")
        con.execute("insert into ops.pipeline_runs values (?, ?, ?, ?, ?, ?)",
                    [run_id, step, datetime.now(), round(seconds, 1), status, note[:1000]])


def run_module(args):
    r = subprocess.run([sys.executable, "-m", *args], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = (r.stdout + r.stderr).strip()
    print(out[-3000:])
    return r.returncode, out.splitlines()[-1] if out else ""


def step_simulate(profile, days):
    return run_module(["simulator.run", "--profile", profile, "--days", str(days)])


def step_extract(profile, _):
    if profile != "live":
        return QUIET, "tap nay khong co nguon API"
    try:
        from . import extract
        state = extract.run(profile)
    except Exception as e:     # bo ket noi hong khong duoc chan cac nguon tep
        return WARN, f"bộ kết nối API lỗi: {e!r}"
    note = extract.summary(state)
    print(note)
    if not all(v.get("ok") for v in state.values()):
        return WARN, note
    return (0 if any(v.get("files_written") for v in state.values()) else QUIET), note


def new_files(profile):
    """Tep nguon chua nap hoac da doi (khac kich thuoc, sua sau lan nap cuoi) -> {he thong: so tep}, tep moi nhat (giay).
    Doi chieu voi bronze._ingest_log theo duong dan, kich thuoc, thoi diem sua; khong bam MD5 de kiem tra cho nhanh
    (buoc ingest moi so MD5). Tep nap loi ma chua sua khong tinh la moi, tranh chay lai mai."""
    from datetime import timezone
    from .ingest import sources
    src = ROOT / "data" / profile / "source_systems"
    seen = {}
    if db_file(profile).exists():
        with dbutil.connect(db_file(profile), read_only=True) as con:
            has = con.sql("select count(*) from duckdb_tables() where schema_name = 'bronze' "
                          "and table_name = '_ingest_log'").fetchone()[0]
            if has:
                seen = {p: (b, t) for p, b, t in con.sql(
                    "select file_path, file_bytes, ingested_at from bronze._ingest_log "
                    "qualify row_number() over (partition by file_path order by ingested_at desc) = 1").fetchall()}
    found, newest = {}, None
    from .ingest import stray_files
    listed = list(sources(src))
    known = {p for _, files, _ in listed for p in files}
    for table, files, _ in listed + [("khongnhandang", stray_files(src, known), None)]:
        for path in files:
            st = path.stat()
            old = seen.get(path.relative_to(src).as_posix())
            mtime = datetime.fromtimestamp(st.st_mtime, timezone.utc).replace(tzinfo=None)
            if old is None or old[0] != st.st_size or mtime > old[1]:
                key = table.split("_")[0] if not table.startswith("master_") else "master"
                found[key] = found.get(key, 0) + 1
                newest = max(newest or 0, st.st_mtime)
    return found, (time.time() - newest) if newest else None


def step_check(profile, _):
    for _ in range(8):
        found, age = new_files(profile)
        if not found:
            print("Khong co tep nguon moi.")
            return NO_NEW_FILES, "khong co tep moi"
        if age is None or age >= SETTLE_SECONDS:
            break
        print(f"Tep moi nhat vua ghi {age:.0f} giay truoc, cho he thong nguon ghi xong...")
        time.sleep(SETTLE_SECONDS)
    note = f"{sum(found.values())} tep moi: " + ", ".join(f"{k} {v}" for k, v in sorted(found.items()))
    print(note)
    return 0, note


def step_ingest(profile, _):
    return run_module(["pipeline.ingest", "--profile", profile])


def step_quality(profile, _):
    code, _last = run_module(["pipeline.quality_gate", "--profile", profile])
    with dbutil.connect(db_file(profile), read_only=True) as con:
        r = con.sql("select level, count(*) from ops.dq_checks where checked_at = (select max(checked_at) "
                    "from ops.dq_checks) group by 1").fetchall()
    return code, ", ".join(f"{n} {lv}" for lv, n in r)


def step_dbt(profile, _):
    code, last = run_module(["pipeline.run_dbt", "--profile", profile, "build"])
    return code, last.split("  ", 1)[-1]


def step_detect(profile, _):
    """Quet canh bao tren Gold va ghi ket qua vao ops.alerts, ops.alert_scores (thay the moi lan chay)."""
    from analytics import detect
    from analytics.data import load_gold
    G = load_gold(profile)
    if G is None:
        return 1, "chua co tang Gold"
    scores = detect.score_all(G)
    alerts = detect.alert_table(G, scores)
    with dbutil.connect(db_file(profile)) as con:
        con.execute("create schema if not exists ops")
        con.register("a", alerts)
        con.register("s", scores)
        con.execute("create or replace table ops.alerts as select *, now() as computed_at from a")
        con.execute("create or replace table ops.alert_scores as select *, now() as computed_at from s")
    last_week = alerts.week_start.max()
    new = alerts[(alerts.week_start == last_week) & (alerts.level == "Cảnh báo")]
    note = f"tuan {last_week:%d/%m/%Y}: {len(new)} canh bao" + \
           ("".join(f"; CN{r.branch_id} {r.cause} {r.score:.1f}" for r in new.itertuples()) if len(new) else "")
    print(note)
    return 0, note


def step_publish(profile, _):
    return run_module(["pipeline.publish", "--profile", profile])


FUNCS = {"simulate": step_simulate, "extract": step_extract, "check": step_check, "ingest": step_ingest, "quality": step_quality, "dbt": step_dbt,
         "detect": step_detect, "publish": step_publish}


def init_live():
    src, dst = ROOT / "data" / "calibration", ROOT / "data" / "live"
    if dst.exists():
        print(f"Da co {dst}, bo qua.")
        return
    print(f"Sao chep {src} -> {dst} ...")
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("ground_truth"))
    print("Xong. Tap live la moi truong van hanh thu, khong dung de danh gia; dap an (neu bo mo phong ghi them) khong duoc pipeline doc.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="live", choices=["calibration", "holdout", "live"])
    ap.add_argument("--step", choices=STEPS + ["simulate"])
    ap.add_argument("--days", type=int, default=1, help="so ngay mo phong them (buoc simulate)")
    ap.add_argument("--no-publish", action="store_true", help="bo buoc dua sang Postgres (khi chua chay kho phuc vu)")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--init-live", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.init_live:
        init_live()
        return
    if args.profile != "live" and not args.step:
        print("Canh bao: dang chay hang ngay tren tap danh gia - du lieu danh gia se bi thay doi.")
    run_id = args.run_id or f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:4]}"
    steps = [args.step] if args.step else [s for s in STEPS if not (s == "publish" and args.no_publish)]
    for s in steps:
        t0 = time.time()
        print(f"== [{args.profile}] buoc {s}")
        try:
            code, note = FUNCS[s](args.profile, args.days)
        except Exception as e:  # ghi lai loi roi bao that bai cho bo dieu phoi
            code, note = 1, repr(e)
        if code == NO_NEW_FILES:          # khong co gi de xu ly: khong ghi nhat ky, bo qua cac buoc sau
            print("== khong co tep moi, dung.")
            sys.exit(NO_NEW_FILES if args.step else 0)
        if code == QUIET:
            print(f"== buoc {s}: khong co gi moi ({note})")
            continue
        status = "ok" if code == 0 else "warn" if code == WARN else "failed"
        if s != "simulate":               # he thong nguon khong ghi vao nhat ky cua kho
            log_run(args.profile, run_id, s, time.time() - t0, status, note)
        print(f"== buoc {s}: {status} sau {time.time() - t0:.0f}s")
        if code not in (0, WARN):
            sys.exit(code)


if __name__ == "__main__":
    main()
