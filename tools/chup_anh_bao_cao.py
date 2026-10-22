"""Chup anh ung dung cho Chuong 4 (Hinh 4.3-4.9) vao docs/report/figures/. Can ung dung Docker :8501 dang chay.

    .venv/Scripts/python tools/chup_anh_bao_cao.py phat_trien    # Tong quan, Trung tam canh bao, Truy vet CN2 tuan 06/05
    .venv/Scripts/python tools/chup_anh_bao_cao.py mo_phong      # Bo mo phong, CN2 ngay 11/05/2024 (Hinh 4.7)
    .venv/Scripts/python tools/chup_anh_bao_cao.py phu_luc       # Phu luc H: sau trang con lai, tap phat trien
    .venv/Scripts/python tools/chup_anh_bao_cao.py chay_7_ngay   # dua 7 ngay moi vao tap van hanh thu roi chup trang
                                                                 # Van hanh hang ngay; SAU DO chay tools/chuan_bi_demo.py --khoi-phuc
Anh chup o ty le 2x; cat le tren/duoi bang PIL truoc khi dung (xem lich su: cat 50-60 px CSS phia tren)."""
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = os.environ.get("FASTFAT_APP_URL", "http://localhost:8501")
OUT = Path(r"D:/khoaluan/docs/report/figures")
W = 900          # khung hep: anh thu ve rong 16 cm van doc duoc (chu in khoang 8-9 pt)


def idle(pg, extra=1.5):
    time.sleep(1.0)
    for _ in range(240):
        if pg.locator('[data-testid="stStatusWidget"]').count() == 0:
            break
        time.sleep(0.5)
    time.sleep(extra)


def collapse(pg):
    pg.evaluate("""() => { const b = document.querySelector('[data-testid="stSidebarCollapseButton"] button')
                       || document.querySelector('[data-testid="stSidebarCollapseButton"]'); if (b) b.click(); }""")
    time.sleep(1.2)


def expand(pg):
    pg.evaluate("""() => { const b = document.querySelector('[data-testid="stExpandSidebarButton"]')
                       || document.querySelector('[data-testid="stSidebarCollapsedControl"] button'); if (b) b.click(); }""")
    time.sleep(1.2)


def select(pg, scope, label, text):
    box = pg.locator(f'{scope} [data-testid="stSelectbox"]').filter(has=pg.get_by_text(label, exact=True)).first
    box.click()
    time.sleep(0.4)
    pg.keyboard.type(text, delay=60)
    time.sleep(0.6)
    pg.keyboard.press("Enter")
    idle(pg)


def nav(pg, name):
    pg.locator('[data-testid="stSidebarNav"]').get_by_text(name, exact=True).click()
    idle(pg, 2)


def to_top(pg):
    """Vung noi dung chinh cua Streamlit tu cuon (vd sau khi bam nut); dua ve dau truoc khi do vi tri."""
    pg.evaluate("() => document.querySelectorAll('[data-testid=stMain], section.main').forEach(e => e.scrollTop = 0)")
    time.sleep(0.5)


def shot(pg, name, height, y0=0):
    """Chi chup vung noi dung (bo le trai phai cua Streamlit) de chu trong anh khong bi thu qua nho khi in."""
    box = pg.evaluate("""() => { const e = document.querySelector('[data-testid=stMainBlockContainer]')
        || document.querySelector('.block-container'); const r = e.getBoundingClientRect(), c = getComputedStyle(e);
        return {x: r.x + parseFloat(c.paddingLeft), w: r.width - parseFloat(c.paddingLeft) - parseFloat(c.paddingRight)}; }""")
    x, w = max(0, box["x"] - 14), box["w"] + 28
    pg.mouse.move(2, 2)          # thanh cong cu cua bieu do chi hien khi re chuot
    time.sleep(0.8)
    pg.screenshot(path=str(OUT / f"{name}.png"), clip={"x": x, "y": y0, "width": w, "height": height})
    print("da chup", name, round(w), "x", height, "px")


def between(pg, top_text, bottom_text, pad_top=24, pad_bottom=8, exact=True):
    """Toa do (y0, chieu cao) cua doan trang tu dong chu top_text toi ngay truoc dong chu bottom_text."""
    to_top(pg)
    main = pg.locator('[data-testid="stMain"]')
    top = main.get_by_text(top_text, exact=exact).first.bounding_box()["y"]
    bottom = main.get_by_text(bottom_text, exact=exact).first.bounding_box()["y"]
    return int(top - pad_top), int(bottom - top + pad_top - pad_bottom)


def upto(pg, top_text, selector, pad_top=24, pad_bottom=12):
    """Toa do (y0, chieu cao) tu dong chu top_text toi het phan tu cuoi cung khop selector."""
    to_top(pg)
    main = pg.locator('[data-testid="stMain"]')
    top = main.get_by_text(top_text, exact=True).first.bounding_box()["y"]
    bottom = pg.evaluate("""(sel) => { const e = [...document.querySelectorAll(sel)].filter(x => x.offsetParent);
        const r = e[e.length - 1].getBoundingClientRect(); return r.bottom; }""", selector)
    return int(top - pad_top), int(bottom - top + pad_top + pad_bottom)


step = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": W, "height": 2400}, device_scale_factor=2)
    pg.goto(URL, wait_until="networkidle")
    pg.locator('[data-testid="stSidebarNav"]').wait_for(timeout=120000)
    idle(pg, 2)
    if step in ("phat_trien", "mo_phong", "phu_luc"):   # hinh bao cao chup tren tap phat trien (moi truong mac dinh la van hanh)
        select(pg, '[data-testid="stSidebar"]', "Môi trường dữ liệu", "tập phát")
    if step == "phat_trien":
        pg.set_viewport_size({"width": 1000, "height": 2400})
        nav(pg, "Tổng quan")
        collapse(pg)
        fr = pg.frame_locator("iframe").first
        fr.get_by_text("Doanh thu", exact=True).first.wait_for(timeout=120000)
        time.sleep(10)
        # nut "..." cua tung o chiem cho lam cat ten o chi so o khung hep; chi an khi chup anh
        for f in pg.frames:
            if "/public/dashboard/" in f.url:
                f.evaluate("() => document.querySelectorAll('[data-testid=public-or-embedded-dashcard-menu]')"
                           ".forEach(e => e.style.display = 'none')")
        time.sleep(2)
        shot(pg, "h4_3_tong_quan", 954)
        expand(pg)
        pg.set_viewport_size({"width": W, "height": 2400})
        nav(pg, "Trung tâm cảnh báo")
        collapse(pg)
        time.sleep(2)
        y0, h = between(pg, "Trung tâm cảnh báo", "cảnh báo,", exact=False)
        shot(pg, "h4_4_canh_bao", h + 420, y0=y0)
        expand(pg)
        nav(pg, "Truy vết nguyên nhân")
        select(pg, '[data-testid="stMain"]', "Chi nhánh", "CN2 ")
        select(pg, '[data-testid="stMain"]', "Tuần", "06/05")
        collapse(pg)
        time.sleep(2)
        y0, h = between(pg, "Truy vết nguyên nhân", "Số tiền là ước tính", exact=False, pad_bottom=10)
        shot(pg, "h4_5_truy_vet", h, y0=y0)
    elif step == "mo_phong":   # Hinh 4.7: trang Bo mo phong, tap phat trien, ngay mac dinh (CN2 11/05/2024)
        pg.set_viewport_size({"width": W, "height": 2400})
        nav(pg, "Bộ mô phỏng")
        collapse(pg)
        time.sleep(2)
        y0, h = between(pg, "1. Sự thật của ngày", "Đơn bị cửa hàng hủy", exact=False, pad_bottom=-3)
        shot(pg, "h4_7_mo_phong", h, y0=y0)
    elif step == "phu_luc":    # Phu luc H: cac trang chua co o Chuong 4
        def page(name, tab=None):
            expand(pg)
            nav(pg, name)
            if tab:
                pg.locator('[data-testid="stMain"]').get_by_text(tab, exact=True).first.click()
                idle(pg, 2)
            collapse(pg)
            time.sleep(2)
        page("Sơ đồ hệ thống")
        y0, h = upto(pg, "Sơ đồ hệ thống", ".ff-grid")
        shot(pg, "ph_so_do", h, y0=y0)
        page("Tệp nguồn")
        y0, h = upto(pg, "Tệp nguồn", '[data-testid="stDataFrame"]')
        shot(pg, "ph_tep_nguon", h, y0=y0)
        page("Kho dữ liệu", "Truy vấn SQL")
        pg.get_by_role("button", name="Chạy truy vấn").click()
        idle(pg, 3)
        y0, h = upto(pg, "Kho dữ liệu", '[data-testid="stDataFrame"]')
        shot(pg, "ph_kho_sql", h, y0=y0)
        page("Mô hình và phả hệ")
        y0, h = between(pg, "Mô hình và phả hệ", "Mũi tên đi từ", exact=False, pad_bottom=-24)
        shot(pg, "ph_pha_he", h, y0=y0)
        page("Chất lượng dữ liệu", "Kiểm thử dữ liệu")
        y0, h = between(pg, "Chất lượng dữ liệu", "Toàn bộ kiểm thử", pad_bottom=10)
        shot(pg, "ph_kiem_thu", h, y0=y0)
        page("Đánh giá bộ phát hiện")
        y0, h = between(pg, "Đánh giá bộ phát hiện", "Tập phát triển · ngưỡng", exact=False, pad_bottom=14)
        shot(pg, "ph_danh_gia", h, y0=y0)
    elif step == "van_hanh":
        select(pg, '[data-testid="stSidebar"]', "Môi trường dữ liệu", "Vận hành")
        nav(pg, "Vận hành hằng ngày")
        collapse(pg)
        time.sleep(3)
        shot(pg, "h4_6_van_hanh", int(sys.argv[2]) if len(sys.argv) > 2 else 1500)
    elif step == "ket_noi":    # Hinh 4.4: chay sau chay_7_ngay, khi bo ket noi API da co trang thai
        select(pg, '[data-testid="stSidebar"]', "Môi trường dữ liệu", "Vận hành")
        pg.set_viewport_size({"width": W, "height": 2400})
        nav(pg, "Kết nối nguồn")
        collapse(pg)
        time.sleep(3)
        y0, h = between(pg, "Các nguồn", "Tài liệu API nguồn", pad_bottom=12)
        shot(pg, "h4_ket_noi", h, y0=y0)
    elif step == "tai_len":    # Hinh 4.3: gui ca 9 tep mau, cho duong ong xu ly xong roi chup
        import requests
        API, AUTH = "http://localhost:8080/api/v1/dags", ("admin", "admin")
        before = requests.get(f"{API}/fastfat_pipeline/dagRuns", params={"order_by": "-start_date", "limit": 1},
                              auth=AUTH).json()["dag_runs"][0]["dag_run_id"]
        select(pg, '[data-testid="stSidebar"]', "Môi trường dữ liệu", "Vận hành")
        pg.set_viewport_size({"width": W, "height": 2400})
        nav(pg, "Tải tệp lên")
        pg.get_by_role("button", name="Gửi cả").click()
        pg.get_by_text("Kết quả tiếp nhận").wait_for(timeout=60000)
        t0 = time.time()
        while time.time() - t0 < 600:
            r = requests.get(f"{API}/fastfat_pipeline/dagRuns", params={"order_by": "-start_date", "limit": 1},
                             auth=AUTH).json()["dag_runs"][0]
            if r["dag_run_id"] != before and r["state"] in ("success", "failed"):
                print("pipeline", r["dag_run_id"], r["state"], round(time.time() - t0), "giay", flush=True)
                break
            time.sleep(10)
        time.sleep(10)
        collapse(pg)
        pg.set_viewport_size({"width": W, "height": 3400})
        time.sleep(3)
        to_top(pg)
        y0, h = between(pg, "Kết quả tiếp nhận", "Tệp đã gửi gần đây", pad_bottom=16)
        shot(pg, "h4_tai_len", h, y0=y0)
    elif step == "chay_7_ngay":
        import requests
        API, AUTH = "http://localhost:8080/api/v1/dags", ("admin", "admin")

        def last(dag):
            r = requests.get(f"{API}/{dag}/dagRuns", params={"order_by": "-start_date", "limit": 1}, auth=AUTH).json()
            return (r["dag_runs"] or [{}])[0]
        before = last("fastfat_pipeline").get("dag_run_id")
        select(pg, '[data-testid="stSidebar"]', "Môi trường dữ liệu", "Vận hành")
        nav(pg, "Vận hành hằng ngày")
        pg.get_by_role("button", name="Gửi dữ liệu ngày mới").click()
        print("da bam", time.strftime("%H:%M:%S"), flush=True)
        t0 = time.time()
        while time.time() - t0 < 600:
            r = last("fastfat_pipeline")
            if r.get("dag_run_id") != before and r.get("state") in ("success", "failed"):
                print("pipeline", r["dag_run_id"], r["state"], round(time.time() - t0), "giay", flush=True)
                break
            time.sleep(10)
        time.sleep(12)
        pg.set_viewport_size({"width": W, "height": 2400})
        idle(pg, 3)
        collapse(pg)
        time.sleep(3)
        y0, h = between(pg, "Lượt xử lý gần nhất", "Đối chiếu ngày", exact=False, pad_bottom=16)
        shot(pg, "h4_6_van_hanh", h, y0=y0)
        # luu nhat ky luot chay de doi chieu bang trong bao cao (truoc khi khoi phuc moi truong)
        import duckdb
        con = duckdb.connect(r"D:/khoaluan/data/live/warehouse/fastfat.duckdb", read_only=True)
        con.sql("select * from ops.pipeline_runs where run_id = (select run_id from ops.pipeline_runs "
                "order by finished_at desc limit 1) order by finished_at").df().to_csv(
            OUT.parent.parent / "results" / "luot_chay_7_ngay.csv", index=False, encoding="utf-8-sig")
        con.close()
    b.close()
