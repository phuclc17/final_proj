"""Thu "ngay xau": dua 7 ngay moi vao moi truong van hanh, cai cung luc nhieu tinh huong du lieu bat thuong vao cac tep
do (tep hong, rong, sai hop dong, la, trung, ban sua, den muon, doi bang ma, truong moi, may POS chua khai bao), them
API nguon sap: luot 1 chay khi API POS dam may va App khong phan hoi, luot 2 chay khi API song lai. Do ket qua tung
tinh huong, roi KHOI PHUC moi truong ve anh chup demo.

    .venv/Scripts/python tools/thu_tinh_huong.py        # khoang 4-6 phut; ghi docs/results/TINH_HUONG_BAT_THUONG.md

Can Docker (Postgres cho buoc publish, source-api cho luot 2); Airflow duoc tam dung trong luc thu de khong chay chen.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "live" / "source_systems"
STORE = ROOT / "data" / "live" / "_he_thong_nguon"     # kho cua phan mem POS dam may, App (doc qua API)
DEAD_API = "http://127.0.0.1:9"                           # cong khong co dich vu: API khong phan hoi
SAMPLES = ROOT / "samples" / "tep_mau"
PY = sys.executable
AF, AUTH = "http://localhost:8080/api/v1", ("admin", "admin")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(ROOT))


def sh(*args, env=None):
    r = subprocess.run([PY, *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**os.environ, **(env or {})})
    return r.returncode, (r.stdout + r.stderr)


def pause(on):
    for d in ("fastfat_nguon", "fastfat_pipeline"):
        try:
            requests.patch(f"{AF}/dags/{d}", params={"update_mask": "is_paused"}, json={"is_paused": on}, auth=AUTH,
                           timeout=5)
        except requests.RequestException:
            pass


def main():
    t0 = time.time()
    print("1. Khôi phục môi trường vận hành về điểm demo (22/09/2024)")
    code, out = sh("tools/chuan_bi_demo.py", "--khoi-phuc")
    assert code == 0, out[-800:]
    pause(True)
    try:
        run(t0)
    finally:
        print("\n6. Khôi phục lại môi trường vận hành về điểm demo")
        code, out = sh("tools/chuan_bi_demo.py", "--khoi-phuc")
        print(out.strip().splitlines()[-1] if out.strip() else "")
        pause(False)


def run(t0):
    print("2. Hệ thống nguồn gửi 7 ngày mới (23–29/09)")
    code, out = sh("-m", "pipeline.run_daily", "--profile", "live", "--step", "simulate", "--days", "7")
    assert code == 0, out[-800:]

    print("3. Cài các tình huống bất thường vào tệp")
    d = "2024-09-23"
    cases = []

    def add(name, how, path, expect):
        cases.append({"Tình huống": name, "Cách đưa vào": how, "path": path, "Mong đợi": expect})

    p = SRC / f"pos/POS-05/pos_export_{d}.json"
    p.write_text(p.read_text(encoding="utf-8")[:5000], encoding="utf-8")
    add("Tệp POS bị hỏng (ghi dở, cắt ngang)", "tệp POS CN5 ngày 23/09 bị cắt", f"pos/POS-05/pos_export_{d}.json",
        "không nạp, ghi lỗi đọc; các tệp khác vẫn nạp; cảnh báo thiếu POS của CN5")
    p = SRC / f"pos/POS-10/pos_export_{d}.json"
    p.write_text("[]", encoding="utf-8")
    add("Tệp POS rỗng", "tệp POS CN10 ngày 23/09 không có hóa đơn nào", f"pos/POS-10/pos_export_{d}.json",
        "nạp 0 dòng; cửa chặn coi như thiếu tệp, cảnh báo; không kết luận sự cố cho CN10")
    p = SRC / f"timekeeping/BR04/punch_BR04_{d.replace('-', '')}.csv"
    pd.read_csv(p, dtype=str).drop(columns=["event_type"]).to_csv(p, index=False)
    add("Tệp chấm công thiếu cột bắt buộc", "tệp chấm công CN4 mất cột event_type", p.relative_to(SRC).as_posix(),
        "không nạp, ghi sai hợp đồng; cảnh báo thiếu chấm công CN4")
    p = SRC / f"timekeeping/BR02/punch_BR02_{d.replace('-', '')}.csv"
    p.write_bytes(p.read_text(encoding="utf-8").encode("utf-16"))
    add("Tệp CSV bảng mã UTF-16", "tệp chấm công CN2 xuất từ phần mềm cũ", p.relative_to(SRC).as_posix(),
        "đọc được, nạp bình thường")
    g = sorted((SRC / "grabfood").glob("GrabFood_Settlement_20240916_*.csv"))[0]
    pd.read_csv(g, dtype=str).to_excel(SRC / "grabfood" / "GrabFood_tuan38.xlsx", index=False)
    add("Báo cáo sàn lưu nhầm định dạng", "báo cáo GrabFood tuần 38 lưu thành .xlsx, thả vào thư mục GrabFood",
        "grabfood/GrabFood_tuan38.xlsx", "không nạp, ghi 'không nhận dạng' kèm gợi ý gửi tệp CSV")
    shutil.copy(SAMPLES / "07_bang_luong_thang_9.xlsx", SRC / "bang_luong_thang_9.xlsx")
    add("Tệp lạ không thuộc nguồn nào", "bảng lương thả vào vùng tiếp nhận", "bang_luong_thang_9.xlsx",
        "không nạp, ghi 'không nhận dạng'")
    shutil.copy(SRC / f"pos/POS-07/pos_export_{d}.json", SRC / "pos/POS-07/pos_export_2024-09-30.json")
    add("Tệp trùng nội dung, đặt tên khác", "tệp POS CN7 ngày 23/09 chép thành tên ngày 30/09",
        "pos/POS-07/pos_export_2024-09-30.json", "không nạp: tên tệp ghi ngày 30/09 nhưng nội dung là ngày 23/09")
    (SRC / "pos/POS-12").mkdir(exist_ok=True)
    shutil.copy(SAMPLES / "08_pos_may_moi_POS-12.json", SRC / "pos/POS-12/pos_export_2024-09-22.json")
    add("Máy POS chưa khai báo trong bảng ánh xạ", "tệp POS của máy POS-12", "pos/POS-12/pos_export_2024-09-22.json",
        "Bronze nạp; Silver cách ly vì không gắn được chi nhánh")
    shutil.copy(SAMPLES / "01_KiemKe_CN03_22-09_ban_sua.xlsx", SRC / "stock_counts/CN03/KiemKe_CN03_20240922.xlsx")
    add("Bản sửa gửi lại", "phiếu kiểm kê CN03 ngày 22/09 đếm lại", "stock_counts/CN03/KiemKe_CN03_20240922.xlsx",
        "nạp lại, thay toàn bộ bản cũ")
    shutil.copy(SAMPLES / "09_NhapKho_CN01_22-09_mua_gap.xlsx", SRC / "warehouse_receipts/CN01/NhapKho_CN01_20240922.xlsx")
    add("Tệp đến muộn cho ngày cũ", "phiếu nhập CN01 ngày 22/09 gửi sau khi ngày đó đã xử lý",
        "warehouse_receipts/CN01/NhapKho_CN01_20240922.xlsx", "nạp bình thường, Silver và Gold tính lại kỳ đó")
    p = STORE / f"pos/POS-01/pos_export_{d}.json"      # nha cung cap POS doi API: phia nguon, khong phai tep
    recs = json.loads(p.read_text(encoding="utf-8"))
    for r in recs:
        r["loyalty_tier"] = "gold"
    p.write_text(json.dumps(recs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    add("Nguồn đổi cấu trúc, thêm trường mới", "API POS đám mây trả thêm trường loyalty_tier (CN1 ngày 23/09)",
        f"pos/POS-01/pos_export_{d}.json", "kéo về, nạp bình thường; cửa chặn cảnh báo trường mới")

    def last_run():
        with duckdb.connect(str(ROOT / "data/live/warehouse/fastfat.duckdb"), read_only=True) as con:
            runs = con.sql("select step, status, note from ops.pipeline_runs where run_id = (select run_id from "
                           "ops.pipeline_runs order by finished_at desc limit 1) order by finished_at").df()
            dq = con.sql("select \"check\", source, level, message from ops.dq_checks where checked_at = "
                         "(select max(checked_at) from ops.dq_checks)").df()
            gold = con.sql("select max(date_day) from gold.fact_order").fetchone()[0]
        return runs, dq, gold

    print("4a. Lượt 1, API nguồn không phản hồi: extract → check → ingest → quality → ...")
    t1 = time.time()
    code1, out = sh("-m", "pipeline.run_daily", "--profile", "live", env={"FASTFAT_SOURCE_API": DEAD_API})
    secs1 = time.time() - t1
    print(out[-1500:])
    runs1, dq1, gold1 = last_run()

    print("4b. Lượt 2, API hoạt động lại: chạy như lịch kiểm tra mỗi giờ")
    t1 = time.time()
    code, out = sh("-m", "pipeline.run_daily", "--profile", "live")
    secs = time.time() - t1
    print(out[-1500:])
    api_state = json.loads((ROOT / "data/live/landing/api_connector.json").read_text(encoding="utf-8"))

    print("5. Đo kết quả")
    con = duckdb.connect(str(ROOT / "data/live/warehouse/fastfat.duckdb"), read_only=True)
    log = con.sql("select file_path, status, row_count, error from bronze._ingest_log qualify row_number() over "
                  "(partition by file_path order by ingested_at desc) = 1").df().set_index("file_path")
    quar = con.sql("select _source_file, dq_issue, count(*) n from silver.silver_quarantine group by all").df()
    dq = con.sql("select \"check\", source, level, message from ops.dq_checks where checked_at = "
                 "(select max(checked_at) from ops.dq_checks)").df()
    runs = con.sql("select step, status, note from ops.pipeline_runs where run_id = (select run_id from ops.pipeline_runs "
                   "order by finished_at desc limit 1) order by finished_at").df()
    con.close()
    from analytics.data import load_gold
    from analytics import detect
    G = load_gold("live")
    A = detect.alert_table(G, detect.score_all(G))
    wk = A[(A.week_start == "2024-09-23") & (A.level != "Bình thường")]

    label = {"loaded": "nạp", "reloaded": "nạp lại thay bản cũ", "failed": "không đọc được, không nạp",
             "rejected": "sai hợp đồng, không nạp", "unrecognized": "không nhận dạng, không nạp"}
    rows = []
    for c in cases:
        p = c["path"]
        st = log.loc[p] if p in log.index else None
        q = quar[quar._source_file == p]
        got = (label.get(st.status, st.status) + (f", {int(st.row_count)} dòng" if st.status in ("loaded", "reloaded") else "")
               if st is not None else "không có trong nhật ký")
        if len(q):
            got += "; Silver cách ly " + ", ".join(f"{int(n)} dòng {i}" for i, n in zip(q.dq_issue, q.n))
        rows.append({"Tình huống": c["Tình huống"], "Cách đưa vào": c["Cách đưa vào"], "Mong đợi": c["Mong đợi"],
                     "Kết quả đo được": got,
                     "Ghi chú hệ thống": (str(st.error)[:160] if st is not None and pd.notna(st.error) and st.error else "")})
    warn = dq[dq.level != "đạt"]
    def steps(rs):
        return "; ".join(f"{r.step} {r.status} ({str(r.note)[:90]})" for r in rs.itertuples())

    warn1 = dq1[dq1.level != "đạt"]
    lines = [
        "# Thử nghiệm \"ngày xấu\": nhiều tình huống dữ liệu bất thường cùng lúc",
        "",
        f"Chạy bằng `python tools/thu_tinh_huong.py` lúc {pd.Timestamp.now():%d/%m/%Y %H:%M}, trên môi trường vận hành "
        "(khôi phục về điểm demo trước và sau khi thử). Hệ thống nguồn ghi 7 ngày 23–29/09/2024: POS cài tại máy (CN5, "
        "CN7, CN10), chấm công, kho, sàn xuất tệp vào vùng tiếp nhận; POS đám mây (8 chi nhánh) và App ghi vào kho của "
        "phần mềm, chỉ lấy được qua API. Sau đó các tình huống dưới đây được cài vào. Đường ống chạy hai lượt, không có "
        "thao tác tay nào ở giữa.",
        "",
        "## API nguồn sập rồi hoạt động lại",
        "",
        f"Lượt 1, API không phản hồi: mã thoát {code1}, {secs1:.0f} giây, Gold vẫn đến ngày {gold1:%d/%m/%Y}. Các bước: "
        + steps(runs1),
        "",
        "Cửa chặn chất lượng lượt 1: " + "; ".join(f"[{r.level}] {r.check} {r.source}: {str(r.message)[:160]}"
                                                    for r in warn1.itertuples()),
        "",
        f"Lượt 2, API hoạt động lại: mã thoát {code}, {secs:.0f} giây. Các bước: " + steps(runs),
        "",
        "Bộ kết nối lượt 2: " + "; ".join(f"{v['label']}: {v['status']}, {v['records']} bản ghi, {v['pages']} trang, "
                                         f"{v['calls']} lần gọi, {v['retries']} lần thử lại do API lỗi tạm thời"
                                         for v in api_state.values()),
        "",
        "## Từng tình huống",
        "",
        "| Tình huống | Cách đưa vào | Mong đợi | Kết quả đo được | Ghi chú hệ thống |",
        "|---|---|---|---|---|",
    ] + [f"| {r['Tình huống']} | {r['Cách đưa vào']} | {r['Mong đợi']} | {r['Kết quả đo được']} | "
         f"{r['Ghi chú hệ thống'].replace('|', '/')} |" for r in rows] + [
        "",
        "## Cửa chặn chất lượng ghi nhận",
        "",
        "| Kiểm tra | Nguồn | Mức | Nội dung |", "|---|---|---|---|",
    ] + [f"| {r.check} | {r.source} | {r.level} | {str(r.message).replace('|', '/')[:220]} |" for r in warn.itertuples()] + [
        "",
        "## Bộ phát hiện, tuần 23–29/09",
        "",
        "| Chi nhánh | Mức | Nguyên nhân | Điểm |", "|---|---|---|---|",
    ] + [f"| CN{r.branch_id} | {r.level} | {r.cause} {r.cause_name} | {r.score:.1f} |" for r in wk.itertuples()]
    out_md = ROOT / "docs/results/TINH_HUONG_BAT_THUONG.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nĐã ghi {out_md.relative_to(ROOT)} ({time.time() - t0:.0f} giây)")


if __name__ == "__main__":
    main()
