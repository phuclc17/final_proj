"""Quay video demo tu A den Z cua san pham: tu tep goc cua he thong nguon, qua Bronze, Silver, Gold, kiem tra chat luong,
dieu phoi, toi canh bao, truy vet va quay ve dung dong trong tep goc. Khong co tieng; chu thich chi noi buoc dang lam
va cho can chu y tren man hinh (khung do), so lieu lay tu kho ngay luc quay.

Can ca he thong Docker (ung dung :8501, Airflow :8080, API nguon, Metabase). Moi truong Van hanh phai o diem demo:
    .venv/Scripts/python tools/chuan_bi_demo.py --khoi-phuc
roi chay:
    .venv/Scripts/python tools/quay_video_demo.py              # quay ca ba doan roi noi
    .venv/Scripts/python tools/quay_video_demo.py --doan 2 3   # quay lai doan 2, 3 (doan 1 giu ban da quay)
    .venv/Scripts/python tools/quay_video_demo.py --noi        # chi noi cac doan da quay

Doan 1: nguon va kenh den, bam gui 7 ngay moi, xem vai buoc dau tu chay. Khong quay luc cho duong ong (vai phut).
Doan 2: ket qua luot chay, du lieu tho, Bronze, Silver, cach ly, Gold, chat luong, Airflow, dashboard, canh bao, truy vet.
Doan 3: kenh nguoi gui tep (gui 9 tep mau), kiem chung tren tap phat trien. Sau khi quay can --khoi-phuc lai.
"""
import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

import duckdb
import imageio_ffmpeg
import pandas as pd
import requests
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
URL = "http://localhost:8501"
AF_UI = "http://localhost:8080"
AF_API, AUTH = f"{AF_UI}/api/v1/dags/fastfat_pipeline/dagRuns", ("admin", "admin")
OUT = ROOT / "docs" / "review" / "demo_ung_dung.webm"
TMP = OUT.parent / "_video_doan"          # giu lai cac doan da quay de quay lai tung doan
LIVE = ROOT / "data" / "live"
SIZE = {"width": 1440, "height": 860}
ROW_H, HEAD_H = 35, 35                     # chieu cao dong va dong tieu de cua bang st.dataframe
TOTAL = 18                                 # so buoc hien o goc tren


# ------------------------------------------------------------------ thao tac co ban
def idle(pg, extra=1.2):
    time.sleep(0.8)
    for _ in range(240):
        if pg.locator('[data-testid="stStatusWidget"]').count() == 0:
            break
        time.sleep(0.5)
    time.sleep(extra)


def main(pg):
    return pg.locator('[data-testid="stMain"]')


def wait_text(pg, text, timeout=180):
    try:
        main(pg).get_by_text(text, exact=False).first.wait_for(timeout=timeout * 1000)
    except Exception:
        pg.screenshot(path=str(TMP / "_loi_quay.png"))
        raise
    idle(pg, 0.8)


def nav(pg, name, wait=None):
    unmark(pg)
    pg.locator('[data-testid="stSidebarNav"]').get_by_text(name, exact=True).click()
    idle(pg)
    if wait:
        wait_text(pg, wait)


def select(pg, label, text, scope='[data-testid="stMain"]'):
    for _ in range(4):
        box = pg.locator(f'{scope} [data-testid="stSelectbox"]').filter(has=pg.get_by_text(label, exact=True)).first
        box.click()
        time.sleep(0.3)
        pg.keyboard.type(text, delay=50)
        time.sleep(0.5)
        pg.keyboard.press("Enter")
        idle(pg, 1.5)
        if text.strip().lower() in box.locator("input").first.input_value().lower():
            return
        pg.keyboard.press("Escape")
    raise RuntimeError(f"khong chon duoc {text!r} o {label!r}")


def click(pg, name, exact=False):
    unmark(pg)
    main(pg).get_by_role("button", name=name, exact=exact).first.click()
    idle(pg)


def tab(pg, name):
    unmark(pg)
    pg.get_by_role("tab", name=name).first.click()
    idle(pg, 0.8)


def to_text(pg, text, offset=90):
    """Cuon toi doan chu, dat no gan dau vung noi dung."""
    unmark(pg)
    el = main(pg).get_by_text(text, exact=False).first
    el.wait_for(timeout=60000)
    el.evaluate("(e, o) => { e.scrollIntoView({block: 'start'}); "
                "const s = document.querySelector('[data-testid=stMain]'); if (s) s.scrollBy(0, -o); }", offset)
    time.sleep(1.0)


def to_top(pg):
    unmark(pg)
    pg.evaluate("() => { const s = document.querySelector('[data-testid=stMain]'); if (s) s.scrollTo(0, 0); }")
    time.sleep(0.6)


def hscroll(pg, dx=6000):
    """Cuon ngang bang toi cot cuoi (bang ve bang canvas, cuon bang banh xe ngang)."""
    unmark(pg)
    b = grid(pg, -1).bounding_box()
    if b:
        pg.mouse.move(b["x"] + b["width"] / 2, b["y"] + b["height"] / 2)
        for _ in range(6):
            pg.mouse.wheel(dx / 6, 0)
            time.sleep(0.12)
        time.sleep(0.8)
        mark(pg, grid(pg, -1))


def grid(pg, n=0):
    g = main(pg).locator('[data-testid="stDataFrame"]:visible')
    return g.last if n == -1 else g.nth(n)


def select_last(pg, text):
    """Chon trong o chon cuoi cung cua trang (o chon an nhan, vd o chon tep goc o trang Truy vet)."""
    box = main(pg).locator('[data-testid="stSelectbox"]:visible').last
    box.click()
    time.sleep(0.3)
    pg.keyboard.type(text, delay=40)
    time.sleep(0.5)
    pg.keyboard.press("Enter")
    idle(pg, 1)


# ------------------------------------------------------------------ chu thich va khung
def chip(pg, step, text):
    pg.evaluate("""t => { let d = document.getElementById('demo-chip');
      if (!d) { d = document.createElement('div'); d.id = 'demo-chip';
        d.style.cssText = 'position:fixed;right:24px;top:14px;z-index:2147483647;background:#1F3A5F;color:#fff;' +
          'font:600 14px Inter,Segoe UI,Arial;padding:6px 12px;border-radius:5px;letter-spacing:.2px';
        document.body.appendChild(d); }
      d.textContent = t; }""", f"{step}/{TOTAL} · {text}")


def say(pg, text, hold=None):
    pg.evaluate("""t => { let d = document.getElementById('demo-cap');
      if (!d) { d = document.createElement('div'); d.id = 'demo-cap';
        d.style.cssText = 'position:fixed;left:50%;bottom:20px;transform:translateX(-50%);z-index:2147483647;' +
          'background:rgba(17,24,39,.92);color:#fff;font:500 17px Inter,Segoe UI,Arial;line-height:1.45;' +
          'padding:10px 18px;border-radius:6px;max-width:1150px;text-align:center'; document.body.appendChild(d); }
      d.textContent = t; d.style.display = t ? 'block' : 'none'; }""", text)
    time.sleep(hold if hold is not None else max(3.2, len(text) / 17))


def mark_box(pg, box, pad=4):
    if not box:
        return
    pg.evaluate("""b => { const d = document.createElement('div'); d.className = 'demo-mark';
      d.style.cssText = `position:fixed;left:${b.x}px;top:${b.y}px;width:${b.w}px;height:${b.h}px;z-index:2147483646;` +
        'border:3px solid #D62828;border-radius:5px;pointer-events:none;box-shadow:0 0 0 4000px rgba(0,0,0,.06)';
      document.body.appendChild(d); }""", {"x": box["x"] - pad, "y": box["y"] - pad,
                                           "w": box["width"] + 2 * pad, "h": box["height"] + 2 * pad})


def mark(pg, locator):
    try:
        mark_box(pg, locator.bounding_box())
    except Exception:
        pass


def mark_rows(pg, n_grid, first, count=1):
    """Dong khung cac dong first..first+count-1 cua bang thu n_grid (bang ve bang canvas, tinh theo chieu cao dong)."""
    b = grid(pg, n_grid).bounding_box()
    if b:
        mark_box(pg, {"x": b["x"], "y": b["y"] + HEAD_H + first * ROW_H, "width": b["width"], "height": count * ROW_H}, 1)


def unmark(pg):
    try:
        pg.evaluate("() => document.querySelectorAll('.demo-mark').forEach(e => e.remove())")
    except Exception:
        pass


def sql(pg, text):
    """Go cau SQL vao o truy van cua trang Kho du lieu roi chay."""
    unmark(pg)
    box = main(pg).locator('[data-testid="stTextArea"] textarea').first
    box.click()
    pg.keyboard.press("Control+A")
    pg.keyboard.press("Delete")
    box.type(text, delay=12)
    time.sleep(0.6)
    click(pg, "Chạy truy vấn")
    time.sleep(0.8)
    try:
        grid(pg, -1).evaluate("e => e.scrollIntoView({block: 'center'})")
        time.sleep(0.8)
    except Exception:
        pass


# ------------------------------------------------------------------ so lieu that tu kho (doc sau khi duong ong chay)
def q(sql_text):
    with duckdb.connect(str(LIVE / "warehouse" / "fastfat.duckdb"), read_only=True) as con:
        return con.sql(sql_text).df()


def vn(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def facts():
    f = {}
    run = q("select * from ops.pipeline_runs where run_id = (select run_id from ops.pipeline_runs "
            "order by finished_at desc limit 1)")
    f["run_note"] = dict(zip(run.step, run.note.astype(str)))
    f["run_sec"] = round(run.seconds.sum())
    import re
    note = f["run_note"]
    src = {"pos": "POS", "timekeeping": "chấm công", "warehouse": "sổ kho", "app": "App", "weather": "thời tiết",
           "grab": "GrabFood", "shopee": "ShopeeFood", "stock": "kiểm kê"}
    parts = re.findall(r"([a-z]+) (\d+)", note.get("check", "").split(":", 1)[-1])
    parts = sorted(((src.get(k, k), int(v)) for k, v in parts), key=lambda x: -x[1])
    f["n_files"] = sum(v for _, v in parts)
    f["files_by_src"] = ", ".join(f"{k} {v}" for k, v in parts)
    m = re.search(r"(\d+) dong moi", note.get("ingest", ""))
    f["n_rows"] = int(m.group(1)) if m else 0
    m = re.search(r"PASS=(\d+)", note.get("dbt", ""))
    f["dbt_pass"] = m.group(1) if m else "?"
    m = re.search(r"([\d.]+) dong", note.get("publish", ""))
    f["pub_rows"] = m.group(1) if m else "?"
    w = q("select max(week_start) w from ops.alerts").w.iloc[0]
    f["week"] = pd.Timestamp(w)
    al = q(f"select branch_id, cause, cause_name, score from ops.alerts where level = 'Cảnh báo' "
           f"and week_start = '{f['week']:%Y-%m-%d}' order by score desc")
    f["alerts"] = al
    br = q("select branch_id, shopee_store_code from gold.dim_branch").set_index("branch_id")
    p1 = al[al.cause == "P1a"]
    f["p1_branch"] = b = int(p1.branch_id.iloc[0]) if len(p1) else 1
    f["shopee_code"] = br.shopee_store_code[b]
    s = q(f"""select s.week_start, s.gross_sales, s.commission, s.effective_commission_rate r, s.contract_commission_rate c,
                     f.commission_overcharge o, s._source_file, s._row_number
              from silver.stg_marketplace__settlement s join gold.fact_marketplace_settlement f using (settlement_key)
              where s.branch_id = {b} and s.platform = 'SHOPEEFOOD' order by s.week_start desc limit 4""")
    f["shopee"] = s
    f["shopee_file"] = s._source_file.iloc[0]
    raw = pd.read_excel(LIVE / "source_systems" / f["shopee_file"], header=None, dtype=str).fillna("")
    f["shopee_raw_row"] = int(raw.index[raw.iloc[:, 0] == f["shopee_code"]][0])
    f["shopee_header_row"] = int(raw.index[raw.iloc[:, 0].str.contains("cửa hàng", case=False)][0])
    p3 = al[al.cause == "P3"]
    f["p3_branch"] = int(p3.branch_id.iloc[0]) if len(p3) else None
    if f["p3_branch"]:
        k = q(f"""select avg(kitchen_evening) filter (where date_day >= '{f['week']:%Y-%m-%d}') tuan,
                         avg(kitchen_evening) filter (where date_day < '{f['week']:%Y-%m-%d}') truoc,
                         avg(app_avg_prep_min) filter (where date_day >= '{f['week']:%Y-%m-%d}') prep,
                         avg(app_avg_prep_min) filter (where date_day < '{f['week']:%Y-%m-%d}') prep0
                  from gold.mart_branch_daily where branch_id = {f['p3_branch']}
                    and date_day between '{f['week'] - pd.Timedelta(days=56):%Y-%m-%d}'
                                     and '{f['week'] + pd.Timedelta(days=6):%Y-%m-%d}'""")
        f["p3"] = k.iloc[0]
    d0 = f["week"].strftime("%Y-%m-%d")
    qu = q("""select q.source_table, q.dq_issue, q._source_file, q.record_key, q._row_number
              from silver.silver_quarantine q join bronze._ingest_log l on l.file_path = q._source_file
              where l.batch_id = (select max(batch_id) from bronze._ingest_log)""")
    f["quarantine"] = qu
    f["q_counts"] = qu.groupby("dq_issue").size().to_dict()
    gam = qu[qu.dq_issue == "nghi_go_gam_vao_cot_kg"]
    f["gam_example"] = str(gam.record_key.iloc[0]) if len(gam) else None
    f["dup"] = None
    for r in qu[qu.dq_issue == "quet_trung"].sort_values("_source_file").to_dict("records"):
        # tim cap quet trung loc duoc bang mot chuoi thoi gian chung (cung phut), de dua ca cap len dau bang
        raw = pd.read_csv(LIVE / "source_systems" / r["_source_file"], dtype=str)
        i = int(r["_row_number"]) - 1
        emp, t1 = raw.employee_code[i], raw.event_time[i]
        prev = raw[(raw.employee_code == emp) & (raw.event_type == raw.event_type[i]) & (raw.index < i)]
        if not len(prev) or prev.event_time.iloc[-1][:15] != t1[:15]:
            continue
        key, t0 = t1[:15], prev.event_time.iloc[-1]
        shown = raw[raw.apply(lambda row: row.astype(str).str.contains(key, regex=False).any(), axis=1)].reset_index()
        rows = shown.index[shown["index"].isin([prev.index[-1], i])].tolist()
        f["dup"] = {"file": r["_source_file"], "emp": emp, "key": key, "rows": rows, "t0": t0[11:], "t1": t1[11:],
                    "gap": int((pd.Timestamp(t1) - pd.Timestamp(t0)).total_seconds())}
        break
    f["d0"] = d0
    f["pos"] = {}
    for b in (5, f["p1_branch"]):
        rec = json.load(open(LIVE / "source_systems" / "pos" / f"POS-{b:02d}" / f"pos_export_{d0}.json", encoding="utf-8"))[0]
        col = "grand_total" if "grand_total" in rec else "total_paid"
        f["pos"][b] = {"time": rec["txn_time"], "ver": rec.get("pos_software_version", "?"), "col": col,
                       "total": rec[col]}
    return f


# ------------------------------------------------------------------ mo ung dung, quay, noi
def open_app(pg):
    pg.goto(URL, wait_until="networkidle")
    pg.locator('[data-testid="stSidebarNav"]').wait_for(timeout=120000)
    # them khoang trong cuoi trang de cuon duoc bang cuoi len tren dong chu thich
    pg.add_style_tag(content='[data-testid="stMainBlockContainer"]{padding-bottom:45vh !important}')
    idle(pg, 1.5)


def warm_up(browser, pages):
    """Mo truoc cac trang (khong quay) cho bo nho dem cua ung dung va Metabase nong."""
    pg = browser.new_page(viewport=SIZE)
    open_app(pg)
    for name in pages:
        nav(pg, name)
        time.sleep(2 if name != "Tổng quan" else 12)
    pg.close()


def record(browser, name, scenes, *args):
    folder = TMP / name
    shutil.rmtree(folder, ignore_errors=True)
    ctx = browser.new_context(viewport=SIZE, record_video_dir=str(folder), record_video_size=SIZE)
    t0 = time.time()
    pg = ctx.new_page()
    open_app(pg)
    start = time.time() - t0
    scenes(pg, *args)
    ctx.close()
    video = next(folder.glob("*.webm"))
    (folder / "bat_dau.json").write_text(json.dumps({"video": video.name, "start": start}), encoding="utf-8")
    return video


def last_run():
    r = requests.get(AF_API, params={"order_by": "-start_date", "limit": 1}, auth=AUTH, timeout=10).json()
    return (r.get("dag_runs") or [{}])[0]


def wait_pipeline(before, timeout=1200):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = last_run()
        if r.get("dag_run_id") != before and r.get("state") in ("success", "failed"):
            return r
        time.sleep(5)
    raise TimeoutError("duong ong chua chay xong")


def join(names):
    parts = []
    for n in names:
        meta = json.loads((TMP / n / "bat_dau.json").read_text(encoding="utf-8"))
        parts.append((TMP / n / meta["video"], meta["start"]))
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    lst = TMP / "danh_sach.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\ninpoint {max(0.0, s - 0.3):.2f}\n" for p, s in parts), encoding="utf-8")
    subprocess.run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:v", "libvpx", "-b:v", "1500k", "-crf", "8", "-an", str(OUT)], check=True)


# ------------------------------------------------------------------ doan 1: nguon va du lieu moi den
def part_one(pg):
    chip(pg, 1, "Hệ thống")
    say(pg, "Môi trường vận hành: kho đang có dữ liệu đến hết ngày 22/09/2024. Video đi theo 7 ngày kinh doanh "
            "tiếp theo từ lúc vào tệp gốc đến lúc thành cảnh báo")
    nav(pg, "Kết nối nguồn", "Các nguồn")
    chip(pg, 2, "Nguồn và kênh đến")
    mark(pg, grid(pg, 0))
    say(pg, "7 nhóm nguồn. Cột Kênh: POS đám mây và App chỉ lấy được qua API; POS cũ ở CN5, CN7, CN10 và máy chấm "
            "công xuất tệp; báo cáo sàn, sổ kho, kiểm kê do người gửi", 9)
    to_text(pg, "Bộ kết nối API")
    say(pg, "Bộ kết nối API lấy theo mốc ngày: mỗi lượt lấy các ngày sau mốc và lấy lại chính ngày mốc, "
            "đối chiếu số bản ghi với tổng API báo rồi mới dời mốc", 8)

    nav(pg, "Vận hành hằng ngày", "Lượt xử lý")
    chip(pg, 3, "Dữ liệu ngày mới đến")
    mark(pg, main(pg).locator('[data-testid="stMetric"]').first)
    say(pg, "Dữ liệu đến 22/09/2024", 3)
    unmark(pg)
    mark(pg, main(pg).get_by_role("button", name="Gửi dữ liệu ngày mới"))
    say(pg, "Gửi 7 ngày 23–29/09. Nút này chỉ cho các hệ thống nguồn ghi dữ liệu, không chạy đường ống", 5)
    click(pg, "Gửi dữ liệu ngày mới")
    to_top(pg)
    say(pg, "Ô 1: hệ thống nguồn đang ghi tệp POS, App, chấm công, sổ kho, báo cáo sàn của 7 ngày", 10)
    say(pg, "Ghi xong, hệ thống nguồn báo Dataset thay đổi. Phần chờ khoảng một phút được cắt khỏi video", 4)


STEP_LABEL = {"extract": "2 kéo API", "check": "3 phát hiện tệp mới", "ingest": "4 nạp Bronze",
              "quality": "5 kiểm tra đầu vào", "dbt": "6 Silver, Gold, kiểm thử", "detect": "7 quét cảnh báo",
              "publish": "8 đưa sang kho phục vụ"}


def task_states():
    run = last_run()
    r = requests.get(f"{AF_API}/{run['dag_run_id']}/taskInstances", auth=AUTH, timeout=10).json()
    return {t["task_id"]: t["state"] for t in r.get("task_instances", [])}


def wait_mid_pipeline(before, timeout=900):
    """Cho toi khi duong ong moi dang chay giua chung (da qua buoc phat hien tep) de quay doan ngan."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        run = last_run()
        if run.get("dag_run_id") != before and run.get("state") == "running":
            st = task_states()
            if st.get("check") == "success":
                return
        time.sleep(2)
    raise TimeoutError("duong ong chua chay")


def part_one_b(pg):
    nav(pg, "Vận hành hằng ngày", "Nhận dữ liệu ngày mới")
    chip(pg, 3, "Đường ống tự chạy")
    say(pg, "Airflow thấy Dataset nguồn thay đổi và tự chạy DAG fastfat_pipeline, không ai bấm nút", 5)
    for _ in range(6):
        st = task_states()
        done = [STEP_LABEL[k] for k in STEP_LABEL if st.get(k) == "success"]
        now = [STEP_LABEL[k] for k in STEP_LABEL if st.get(k) == "running"]
        if not now and st.get("publish") == "success":
            break
        say(pg, (f"Đang chạy ô {', '.join(now)}. " if now else "") + (f"Xong: ô {', '.join(done)}" if done else ""), 5)
    say(pg, "Các bước còn lại được cắt, video tiếp tục khi lượt chạy kết thúc", 3)


# ------------------------------------------------------------------ doan 2: tu tep goc den canh bao
def part_two(pg, f):
    note = f["run_note"]
    s = f["shopee"]
    b1, code = f["p1_branch"], f["shopee_code"]
    nav(pg, "Vận hành hằng ngày", "Lượt xử lý")
    chip(pg, 4, "Lượt xử lý vừa chạy")
    say(pg, f"Đường ống đã tự chạy xong 7 bước trong {f['run_sec']} giây, không có thao tác tay nào", 4)
    to_text(pg, "Lượt xử lý gần nhất")
    mark(pg, grid(pg, 0))
    say(pg, f"Bước phát hiện thấy {f['n_files']} tệp mới: {f['files_by_src']}", 7)
    say(pg, f"Nạp {vn(f['n_rows'])} dòng vào Bronze, 0 tệp lỗi; dbt chạy {f['dbt_pass']} bước đều đạt; "
            f"{f['pub_rows']} dòng sang PostgreSQL, đối soát số dòng khớp", 8)

    # ---- tep goc
    nav(pg, "Tệp nguồn", "Số dòng")
    chip(pg, 5, "Tệp gốc: báo cáo ShopeeFood")
    select(pg, "Hệ thống", "shopeefood")
    select(pg, "Tệp", Path(f["shopee_file"]).name[:30])
    wait_text(pg, "Số dòng")
    to_text(pg, "Lọc dòng chứa chuỗi", 160)
    say(pg, f"Một tệp Excel cho cả 11 chi nhánh, tuần 23–29/09. Hai dòng đầu là tiêu đề báo cáo, chưa phải dữ liệu", 6)
    mark_rows(pg, -1, f["shopee_header_row"])
    say(pg, "Tiêu đề cột tiếng Việt, tiền có đơn vị trong tên cột. Sàn chỉ ghi số tiền phí dịch vụ, không ghi tỷ lệ", 7)
    unmark(pg)
    mark_rows(pg, -1, f["shopee_raw_row"])
    say(pg, f"CN{b1} không có tên chi nhánh, chỉ có mã cửa hàng của Shopee: {code}. Theo dòng này qua các tầng", 7)

    # POS hai phien ban
    to_top(pg)
    chip(pg, 6, "Tệp gốc: POS hai phiên bản")
    select(pg, "Hệ thống", "pos")
    select(pg, "Thư mục", "POS-05")
    select(pg, "Tệp", f"pos_export_{f['week']:%Y-%m-%d}")
    wait_text(pg, "Số dòng")
    to_text(pg, "Lọc dòng chứa chuỗi", 160)
    p5, p1 = f["pos"][5], f["pos"][b1]
    mark(pg, grid(pg, -1))
    say(pg, f"CN5 dùng POS cài tại máy, xuất tệp mỗi đêm. Cột txn_time ghi '{p5['time']}'", 6)
    hscroll(pg)
    say(pg, f"Cuối bảng: phiên bản {p5['ver']}, tổng tiền nằm ở cột {p5['col']} và là chuỗi "
            f"'{p5['total']}', dấu chấm ngăn hàng nghìn", 7)
    to_top(pg)
    select(pg, "Thư mục", f"POS-{b1:02d}")
    select(pg, "Tệp", f"pos_export_{f['week']:%Y-%m-%d}")
    wait_text(pg, "Số dòng")
    to_text(pg, "Lọc dòng chứa chuỗi", 160)
    mark(pg, grid(pg, -1))
    say(pg, f"CN{b1} dùng POS đám mây, tệp này vừa được bộ kết nối kéo qua API. Cột txn_time ghi '{p1['time']}'", 6)
    hscroll(pg)
    say(pg, f"Phiên bản {p1['ver']}: tổng tiền ở cột {p1['col']} và là số {p1['total']}. Silver phải đưa hai kiểu "
            "này về một lược đồ", 7)

    # cham cong quet trung
    dup = f["dup"]
    if dup is not None:
        to_top(pg)
        chip(pg, 7, "Tệp gốc: máy chấm công")
        parts = dup["file"].split("/")
        select(pg, "Hệ thống", "timekeeping")
        select(pg, "Thư mục", parts[1])
        select(pg, "Tệp", parts[2][:24])
        wait_text(pg, "Số dòng")
        box = main(pg).locator('[data-testid="stTextInput"] input').first
        box.fill(dup["key"])
        box.press("Enter")
        idle(pg, 1)
        to_text(pg, "Lọc dòng chứa chuỗi", 160)
        for r in dup["rows"]:
            mark_rows(pg, -1, r)
        say(pg, f"Nhân viên mã {dup['emp']}: máy ghi hai lượt vào lúc {dup['t0']} và {dup['t1']}, cách nhau "
                f"{dup['gap']} giây. Silver sẽ tách lượt sau ra bảng cách ly, không xóa", 8)

    # ---- Bronze
    nav(pg, "Kho dữ liệu", "Tầng")
    chip(pg, 8, "Bronze: nạp nguyên văn")
    pg.locator('[data-testid="stMain"] [data-testid="stButtonGroup"]').get_by_text("Bronze", exact=True).click()
    idle(pg)
    tab(pg, "Truy vấn SQL")
    sql(pg, f"select ma_cua_hang, doanh_thu_mon_vnd, phi_dich_vu_vnd, _doc_line_2, _source_file, _row_number\n"
            f"from bronze.shopee_settlement\nwhere ma_cua_hang = '{code}' and _source_file like '%{f['week']:%Y%m%d}%'")
    mark(pg, grid(pg, -1))
    say(pg, "Bronze giữ đúng giá trị trong tệp, vẫn là chuỗi; thêm tên tệp và số dòng gốc để truy ngược", 7)

    # ---- Silver
    chip(pg, 9, "Silver: làm sạch, chuẩn hóa")
    sql(pg, f"select branch_id, week_start, gross_sales, commission,\n"
            f"       effective_commission_rate as ty_le_thuc, contract_commission_rate as ty_le_hop_dong\n"
            f"from silver.stg_marketplace__settlement\nwhere branch_id = {b1} and platform = 'SHOPEEFOOD'\n"
            f"order by week_start desc limit 4")
    mark(pg, grid(pg, -1))
    say(pg, f"Mã {code} thành chi nhánh {b1}, chuỗi thành số, tỷ lệ thực tự tính = phí ÷ doanh thu món, "
            "ghép tỷ lệ của hợp đồng đang hiệu lực", 8)
    unmark(pg)
    mark_rows(pg, -1, 0)
    r0, r1 = s.iloc[0], s.iloc[1]
    say(pg, f"Tuần {r0.week_start:%d/%m}: sàn thu {vn(r0.r * 100, 1)}%, hợp đồng {vn(r0.c * 100, 1)}%. "
            f"Tuần {r1.week_start:%d/%m} trở về trước: {vn(r1.r * 100, 1)}%, đúng hợp đồng", 7)

    qu = f["quarantine"]
    if len(qu):
        chip(pg, 10, "Silver: bảng cách ly")
        sql(pg, "select q.source_table, q.dq_issue, count(*) as so_dong\n"
                "from silver.silver_quarantine q join bronze._ingest_log l on l.file_path = q._source_file\n"
                "where l.batch_id = (select max(batch_id) from bronze._ingest_log)\n"
                "group by all order by 3 desc")
        mark(pg, grid(pg, -1))
        c = f["q_counts"]
        extra = f", ví dụ phiếu nhập ghi '{f['gam_example']}'" if f["gam_example"] else ""
        say(pg, f"Lô nạp vừa chạy: {c.get('quet_trung', 0)} lượt quẹt trùng và {c.get('nghi_go_gam_vao_cot_kg', 0)} "
                f"dòng nghi gõ gam vào cột kg{extra}. Không vào Gold, vẫn tra được tệp và dòng gốc", 9)

    # ---- Gold
    chip(pg, 11, "Gold: lược đồ hình sao")
    sql(pg, f"select week_start, channel, effective_commission_rate - contract_commission_rate as chenh_lech,\n"
            f"       commission_overcharge as thu_thua_vnd\nfrom gold.fact_marketplace_settlement\n"
            f"where branch_id = {b1} and channel = 'SHOPEEFOOD' order by week_start desc limit 4")
    mark_rows(pg, -1, 0)
    say(pg, f"Gold quy ra tiền: tuần {r0.week_start:%d/%m} CN{b1} bị thu thừa {vn(r0.o)} đồng", 6)
    nav(pg, "Mô hình và phả hệ", "Phả hệ")
    select(pg, "Xem phả hệ của một bảng", "fact_marketplace")
    time.sleep(1.5)
    mark(pg, main(pg).locator('[data-testid="stGraphVizChart"]').first)
    say(pg, "Phả hệ do dbt tự sinh: bảng này lấy từ báo cáo Grab và Shopee ở Silver, gốc là hai bảng Bronze", 7)
    tab(pg, "Lược đồ hình sao")
    say(pg, "6 bảng sự kiện, 7 bảng chiều. Mỗi đường nối là một khóa ngoại có kiểm thử chạy trên dữ liệu", 6)

    # ---- chat luong
    nav(pg, "Chất lượng dữ liệu", "Kiểm tra đầu vào")
    chip(pg, 12, "Kiểm tra chất lượng")
    time.sleep(1.5)
    mark(pg, grid(pg, 0))
    say(pg, "Cửa chặn trước Silver: " + note.get("quality", "")[:60] + ". Mục ở mức chặn sẽ dừng đường ống, "
            "không có cảnh báo nào từ dữ liệu thiếu", 8)
    tab(pg, "Đối soát và cách ly")
    time.sleep(1.5)
    mark(pg, grid(pg, 0))
    say(pg, "Mỗi nguồn: số dòng Bronze = Silver + cách ly + dòng cấu trúc. Cột cuối là phần không giải thích được, "
            "phải bằng 0", 8)

    # ---- Airflow
    unmark(pg)
    chip(pg, 13, "Điều phối: Airflow")
    pg.goto(f"{AF_UI}/login/")
    pg.fill("#username", AUTH[0])
    pg.fill("#password", AUTH[1])
    pg.click("input[type=submit], button[type=submit]")
    time.sleep(2)
    pg.goto(f"{AF_UI}/dags/fastfat_pipeline/grid")
    time.sleep(4)
    chip(pg, 13, "Điều phối: Airflow")
    say(pg, "DAG fastfat_pipeline: lượt cuối được kích hoạt bởi Dataset, không theo giờ. 7 tác vụ nối tiếp; "
            "lượt màu hồng là lần kiểm tra mỗi giờ không thấy tệp mới nên bỏ qua", 9)
    open_app(pg)

    # ---- phan tich
    nav(pg, "Tổng quan")
    time.sleep(6)
    chip(pg, 14, "Kho phục vụ và dashboard")
    say(pg, "Dashboard Metabase đọc bản sao trên PostgreSQL, vừa được thay ở bước cuối của đường ống: dữ liệu đến 29/09",
        7)
    nav(pg, "Trung tâm cảnh báo", "cảnh báo,")
    chip(pg, 15, "Cảnh báo")
    time.sleep(1.5)
    mark(pg, main(pg).locator('[data-testid="stVegaLiteChart"]').first)
    say(pg, f"Bản đồ cảnh báo 11 chi nhánh × tuần, quét lại toàn bộ sau mỗi lượt chạy. Cột cuối bên phải là tuần "
            f"{f['week']:%d/%m} vừa có dữ liệu", 7)
    a = f["alerts"]
    nav(pg, "Vận hành hằng ngày", "Lượt xử lý")
    to_text(pg, f"Cảnh báo tuần {f['week']:%d/%m}")
    names = "; ".join(f"CN{r.branch_id} {r.cause_name.lower()}, điểm {vn(r.score, 1)}" for r in a.itertuples())
    say(pg, f"Tuần {f['week']:%d/%m} có {len(a)} cảnh báo mới: {names}", 8)
    unmark(pg)
    mark(pg, main(pg).get_by_role("button", name="Truy vết").first)
    say(pg, f"Mở truy vết CN{b1}", 2)
    unmark(pg)
    main(pg).get_by_role("button", name="Truy vết").first.click()
    idle(pg)
    wait_text(pg, "Đề xuất xử lý")
    chip(pg, 16, f"Truy vết CN{b1}")
    mark(pg, main(pg).locator('[data-testid="stMetric"]').first)
    say(pg, f"Kết luận P1a, sàn thu thừa {vn(r0.o)} đồng trong tuần; bên dưới là việc kế toán cần làm và hạn xử lý", 7)
    to_text(pg, "Bằng chứng gốc trong tệp nguồn")
    mark(pg, grid(pg, -1))
    say(pg, "Bằng chứng là chính dòng đối soát của sàn, kèm tên tệp và số dòng gốc", 5)
    select_last(pg, "shopeefood/Shopee")
    mark(pg, main(pg).get_by_role("button", name="Mở tệp gốc"))
    say(pg, "Mở tệp gốc của báo cáo ShopeeFood", 2.5)
    click(pg, "Mở tệp gốc")
    wait_text(pg, "Số dòng")
    to_text(pg, "Lọc dòng chứa chuỗi", 160)
    mark(pg, grid(pg, -1))
    say(pg, f"Quay về đúng dòng {code} trong tệp Excel của Shopee, nơi video bắt đầu ở bước 5", 7)

    if f["p3_branch"]:
        k = f["p3"]
        nav(pg, "Vận hành hằng ngày", "Lượt xử lý")
        to_text(pg, f"Cảnh báo tuần {f['week']:%d/%m}")
        mark(pg, main(pg).get_by_role("button", name="Truy vết").nth(1))
        say(pg, f"Mở truy vết CN{f['p3_branch']}", 2)
        unmark(pg)
        main(pg).get_by_role("button", name="Truy vết").nth(1).click()
        idle(pg)
        wait_text(pg, "Đề xuất xử lý")
        chip(pg, 16, f"Truy vết CN{f['p3_branch']}")
        say(pg, f"CN{f['p3_branch']} cùng tuần: ca bếp tối trung bình {vn(k.tuan, 1)} mỗi ngày so với "
                f"{vn(k.truoc, 1)} của 8 tuần trước; chuẩn bị đơn App {vn(k.prep, 1)} phút so với {vn(k.prep0, 1)}", 8)
        to_text(pg, "Bằng chứng gốc trong tệp nguồn")
        mark(pg, grid(pg, -1))
        say(pg, "Bằng chứng: số ca bếp tối từng ngày đếm từ máy chấm công, và từng đơn App cửa hàng tự hủy", 6)


# ------------------------------------------------------------------ doan 3: kenh nguoi gui va kiem chung
def part_three(pg):
    nav(pg, "Tải tệp lên", "Tệp mẫu")
    chip(pg, 17, "Kênh người gửi tệp")
    say(pg, "Kế toán, quản lý chi nhánh gửi tệp bằng tay. Gửi 9 tệp mẫu, trong đó có 6 tệp sai hoặc trùng", 5)
    click(pg, "Gửi cả 9 tệp mẫu")
    wait_text(pg, "Kết quả tiếp nhận")
    to_text(pg, "Kết quả tiếp nhận")
    mark(pg, main(pg).locator("table").last)
    say(pg, "Nhận dạng theo nội dung, không theo tên: phiếu kiểm kê sửa lại thay bản cũ; báo cáo Shopee gửi lại "
            "dưới tên khác bị bỏ qua vì trùng nội dung", 9)
    say(pg, "Bị từ chối kèm lý do: GrabFood lưu thành .xlsx thay vì CSV gốc; tệp chấm công mất cột event_type; "
            "sổ nhập kho không ghi chi nhánh; máy POS-12 chưa khai báo; bảng lương không thuộc nguồn nào", 11)

    say(pg, "", 0)
    nav(pg, "Sơ đồ hệ thống")
    select(pg, "Môi trường dữ liệu", "tập phát", scope='[data-testid="stSidebar"]')
    nav(pg, "Bộ mô phỏng", "Sự thật của ngày")
    chip(pg, 18, "Kiểm chứng")
    say(pg, "Phần kiểm chứng tách khỏi sản phẩm: bộ mô phỏng giữ sự thật của từng ngày, đường ống không được đọc", 6)
    to_text(pg, "Mỗi hệ thống ghi lại được")
    mark(pg, main(pg).locator("table").last)
    say(pg, "CN2 ngày 11/05: 216 đơn tại quầy khớp POS; 38 khách bỏ về không hệ thống nào ghi; "
            "3 đơn Grab và 2 đơn Shopee không được nhập POS", 9)
    nav(pg, "Đánh giá bộ phát hiện", "Tập kiểm tra")
    to_text(pg, "Tập kiểm tra")
    mark(pg, grid(pg, 0))
    say(pg, "Ngưỡng chốt trên tập phát triển, tập kiểm tra chạy đúng một lần: bắt 4/6 sự cố, F1 0,52. "
            "Chỉ theo dõi doanh thu bắt 1/6", 9)
    say(pg, "", 0.5)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--doan", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--noi", action="store_true", help="chi noi cac doan da quay")
    a = ap.parse_args()
    TMP.mkdir(parents=True, exist_ok=True)
    if not a.noi:
        with sync_playwright() as p:
            b = p.chromium.launch()
            if 1 in a.doan:
                warm_up(b, ["Kết nối nguồn", "Vận hành hằng ngày"])
                before = last_run().get("dag_run_id")
                record(b, "doan_1", part_one)
                print("doan 1 xong; cho duong ong bat dau (khong quay)", flush=True)
                wait_mid_pipeline(before)
                record(b, "doan_1b", part_one_b)
                print("doan 1b xong; cho duong ong xong (khong quay)", flush=True)
                print("duong ong", wait_pipeline(before).get("state"), flush=True)
                time.sleep(15)
            if 2 in a.doan:
                f = facts()
                print("so lieu:", {k: v for k, v in f.items() if k in ("week", "p1_branch", "shopee_code", "p3_branch")},
                      flush=True)
                warm_up(b, ["Tệp nguồn", "Kho dữ liệu", "Mô hình và phả hệ", "Chất lượng dữ liệu", "Tổng quan",
                            "Trung tâm cảnh báo", "Truy vết nguyên nhân"])
                record(b, "doan_2", part_two, f)
                print("doan 2 xong", flush=True)
            if 3 in a.doan:
                record(b, "doan_3", part_three)
                print("doan 3 xong", flush=True)
            b.close()
    join([n for n in ("doan_1", "doan_1b", "doan_2", "doan_3") if (TMP / n / "bat_dau.json").exists()])
    print("da ghi", OUT, round(OUT.stat().st_size / 1e6, 1), "MB")
