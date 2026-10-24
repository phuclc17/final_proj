"""Cac so do UML cua bao cao (Chuong 3, 4): sinh trang HTML vao figures/src/ roi render.py xuat PNG.
Noi dung tung buoc, nhanh lay dung theo ma dang chay:
  hoat dong tiep nhan tep  <- pipeline/intake.py, pipeline/contracts.py, app/views/upload.py
  hoat dong mot lo du lieu <- pipeline/run_daily.py, airflow/dags/fastfat_pipeline.py, pipeline/extract.py
  hoat dong xu ly canh bao <- analytics/detect.py, analytics/actions.py (nguoi phu trach), app/views/trace.py
  tuan tu                  <- pipeline/extract.py + source_api/app.py; upload.py + intake.py; trace.py + sources.py
  phan ra chuc nang        <- thanh dieu huong app/main.py va cac buoc cua duong ong
  trien khai               <- docker-compose.yml, deploy/docker-compose.server.yml

  .venv/Scripts/python docs/report/figures/uml_figures.py          # sinh tat ca roi xuat PNG
  .venv/Scripts/python docs/report/figures/uml_figures.py h3_seq_api   # mot hinh
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uml import (Activity, Sequence, artifact, bfd, node3d, page, poly, text,  # noqa: E402
                 INK, MUTED)

SRC = Path(__file__).resolve().parent / "src"
LABEL = "#000000"


def save(name, html):
    (SRC / f"{name}.html").write_text(html, encoding="utf-8")
    return name


# ---------------------------------------------------------------------- hoat dong: tiep nhan tep tai len
def h3_act_tiep_nhan():
    a = Activity(830, 830, lanes=[("Người gửi tệp", 0, 170), ("Nền tảng: trang Tải tệp lên và phần tiếp nhận", 170, 830)])
    M, R = 500, 712
    a.start("s", 85, 62)
    a.action("u1", 85, 125, "Chọn tệp hoặc\ntệp mẫu, bấm Gửi", w=146)
    a.action("i1", M, 125, "Nhận dạng nguồn theo nội dung:\nkhóa JSON, tiêu đề cột, phiếu", w=230)
    a.decision("d1", M, 192)
    a.action("i2", M, 255, "Chuẩn hóa bảng mã CSV về UTF-8,\ntính vị trí chuẩn theo nguồn, ngày", w=240)
    a.decision("d2", M, 322)
    a.decision("d3", R, 322)
    a.decision("d4", M, 392)
    a.action("rj", 280, 392, "Từ chối: lưu bản sao\nvào _rejected, ghi lý do", w=170)
    a.action("dup", R, 392, "Trùng: bỏ qua,\nkhông ghi tệp", w=150)
    a.action("w", M, 462, "Ghi tệp tạm rồi đổi tên;\nkết quả: đã nhận hoặc thay bản cũ", w=240)
    a.action("log", M, 535, "Ghi nhật ký tiếp nhận", w=200)
    a.decision("d5", M, 600)
    a.action("nt", R, 600, "Báo Airflow: Dataset\nnguồn được cập nhật", w=170)
    a.decision("m", M, 668)
    a.action("show", M, 732, "Hiển thị kết quả từng tệp\nkèm lý do", w=210)
    a.action("u2", 85, 732, "Xem kết quả,\nsửa tệp bị từ chối", w=146)
    a.end("e", 85, 800)

    a.edge("s", "u1")
    a.edge("u1", "i1", "r", "l")
    a.edge("i1", "d1")
    a.edge("d1", "i2", label="[khớp hợp đồng]")
    a.edge("d1", "rj", "l", "t", label="[không nhận dạng được\nhoặc sai hợp đồng]", lpos=(392, 168, "middle"))
    a.edge("i2", "d2")
    a.edge("d2", "d3", "r", "l", label="[đã có tệp ở vị trí đó]")
    a.edge("d3", "dup", label="[nội dung giống hệt]", lpos=(704, 352, "end"))
    a.edge("d3", "w", "r", "r", via=[(808, 322), (808, 462)], label="[nội dung khác: bản sửa]",
           lpos=(800, 300, "end"))
    a.edge("d2", "d4", label="[chưa có]")
    a.edge("d4", "rj", "l", "r", label="[trùng tệp khác]", lpos=(425, 381, "middle"))
    a.edge("d4", "w", label="[không trùng]")
    a.edge("w", "log")
    a.edge("rj", "log", "b", "l")
    a.edge("dup", "log", "b", "r")
    a.edge("log", "d5")
    a.edge("d5", "nt", "r", "l", label="[có tệp nhận\nhoặc thay]", lpos=(571, 579, "middle"))
    a.edge("d5", "m", label="[không]")
    a.edge("nt", "m", "b", "r")
    a.edge("m", "show")
    a.edge("show", "u2", "l", "r")
    a.edge("u2", "e")
    a.note(712, 182, "Lặp lại cho từng tệp\ntrong một lần gửi", w=150, attach=("i1", "r"))
    a.note(712, 772, "Đường ống chạy độc lập;\ntrang tự cập nhật trạng\nthái nạp của từng tệp", w=170)
    return save("h3_act_tiep_nhan", a.render())


# ---------------------------------------------------------------------- hoat dong: xu ly mot lo du lieu moi
def h3_act_lo_du_lieu():
    a = Activity(830, 990, lanes=[("Hệ thống nguồn", 0, 190), ("Airflow: DAG fastfat_pipeline", 190, 830)])
    M, R = 455, 700
    a.start("s", 95, 62)
    a.action("g", 95, 125, "Ghi dữ liệu ngày\nkinh doanh mới", w=160)
    a.action("ds", 95, 200, "Báo Dataset nguồn\nđược cập nhật", w=160)
    a.time_event("t", 300, 62, "mỗi giờ")
    a.decision("m0", M, 125)
    a.action("ex", M, 190, "extract: kéo ngày mới qua API\nPOS đám mây và App theo mốc", w=250)
    a.decision("dapi", M, 255)
    a.action("warn", R, 255, "Ghi trạng thái cảnh báo;\nnguồn tệp vẫn xử lý tiếp", w=200)
    a.decision("m1", M, 318)
    a.action("ck", M, 380, "check: đối chiếu tệp nguồn với\nnhật ký nạp theo đường dẫn,\nkích thước, thời điểm sửa", w=250)
    a.decision("dnew", M, 452)
    a.end("e0", R - 70, 452, "kết thúc lượt, không\nghi nhật ký")
    a.action("in", M, 515, "ingest: nạp Bronze tăng dần;\ntệp sai hợp đồng bị từ chối", w=250)
    a.action("q", M, 585, "quality: kiểm tra độ mới, khối lượng,\nđầy đủ theo chi nhánh, cấu trúc", w=270)
    a.decision("dq", M, 652)
    a.action("stop", R, 652, "Dừng lượt: các bước sau\nkhông chạy; kho phục vụ\ngiữ bản cũ", w=190)
    a.end("e1", R, 745)
    a.action("dbt", M, 718, "dbt build: Silver, Gold\nvà 158 kiểm thử dữ liệu", w=230)
    a.decision("dt", M, 785)
    a.action("det", M, 848, "detect: quét chỉ số, chấm điểm\nnguyên nhân, ghi ops.alerts", w=250)
    a.action("pub", M, 918, "publish: đưa Gold và ops sang\nPostgreSQL, đối soát số dòng", w=250)
    a.end("e2", 300, 918)

    a.edge("s", "g")
    a.edge("g", "ds")
    a.edge("ds", "m0", "r", "l", via=[(250, 200), (250, 125)])
    a.edge("t", "m0", "r", "t", via=[(M, 62)])
    a.edge("m0", "ex")
    a.edge("ex", "dapi")
    a.edge("dapi", "warn", "r", "l", label="[không phản hồi\nsau 6 lần thử]", lpos=(537, 232, "middle"))
    a.edge("dapi", "m1", label="[lấy đủ, tổng khớp]")
    a.edge("warn", "m1", "b", "r")
    a.edge("m1", "ck")
    a.edge("ck", "dnew")
    a.edge("dnew", "e0", "r", "l", label="[không có tệp mới]", lpos=(552, 442, "middle"))
    a.edge("dnew", "in", label="[có tệp mới]")
    a.edge("in", "q")
    a.edge("q", "dq")
    a.edge("dq", "stop", "r", "l", label="[có mục ở\nmức chặn]", lpos=(537, 629, "middle"))
    a.edge("dq", "dbt", label="[đạt hoặc chỉ cảnh báo]")
    a.edge("stop", "e1")
    a.edge("dbt", "dt")
    a.edge("dt", "stop", "r", "r", via=[(812, 785), (812, 652)], label="[có kiểm thử lỗi]", lpos=(548, 775, "start"))
    a.edge("dt", "det", label="[158 kiểm thử đạt]")
    a.edge("det", "pub")
    a.edge("pub", "e2", "l", "r")
    a.note(95, 330, "Trong khóa luận, bộ\nmô phỏng đóng vai hệ\nthống nguồn; người\ngửi tệp cũng báo\nDataset như vậy", w=160)
    a.note(700, 875, "Mỗi bước ghi một dòng\nvào ops.pipeline_runs;\nbước lỗi được Airflow\nthử lại một lần", w=180)
    return save("h3_act_lo_du_lieu", a.render())


# ---------------------------------------------------------------------- hoat dong: xu ly canh bao
def h3_act_canh_bao():
    a = Activity(830, 960, lanes=[("Nền tảng", 0, 270), ("Quản lý vận hành", 270, 550),
                                   ("Người phụ trách", 550, 830)])
    S, Q, P = 140, 410, 690
    a.start("s", S, 62)
    a.action("scan", S, 125, "Sau mỗi lượt xử lý: quét\nchỉ số, chấm điểm 5 nguyên\nnhân cho mọi chi nhánh, tuần", w=220)
    a.action("rank", S, 210, "Lập danh sách cảnh báo,\nước tính thiệt hại, gắn\nngười phụ trách, thời hạn", w=220)
    a.action("view", Q, 210, "Xem Trung tâm cảnh báo,\nsắp theo thiệt hại", w=220)
    a.action("pick", Q, 285, "Chọn cảnh báo,\nmở Truy vết", w=200)
    a.action("trace", S, 285, "Hiện cây KPI, tín hiệu,\nbằng chứng gốc và\nđề xuất xử lý", w=220)
    a.decision("d1", Q, 370)
    a.action("watch", Q, 450, "Ghi nhận, theo dõi thêm\nmột tuần", w=200)
    a.action("assign", P, 370, "Nhận việc theo đề xuất:\nviệc cần xác minh,\nviệc cần làm, thời hạn", w=230)
    a.action("verify", P, 455, "Xác minh ngoài hệ thống:\nđối chiếu sàn, camera, két\ntiền, kiểm kê lại", w=230)
    a.decision("d2", P, 535)
    a.action("fix", P, 610, "Xử lý: đòi hoàn phí, điều\nchỉnh ca, siết kiểm soát", w=230)
    a.action("fp", Q, 535, "Ghi nhận báo động giả", w=200)
    a.decision("m", Q, 690)
    a.action("next", S, 760, "Tuần kế tiếp: đánh giá lại\nchỉ số so với mức kỳ vọng", w=220)
    a.decision("d3", S, 835)
    a.end("e", S, 912, "hết cảnh báo")

    a.edge("s", "scan")
    a.edge("scan", "rank")
    a.edge("rank", "view", "r", "l")
    a.edge("view", "pick")
    a.edge("pick", "trace", "l", "r")
    a.edge("trace", "d1", "b", "l", via=[(S, 370)])
    a.edge("d1", "assign", "r", "l", label="[đủ căn cứ]")
    a.edge("d1", "watch", label="[chưa đủ căn cứ]")
    a.edge("assign", "verify")
    a.edge("verify", "d2")
    a.edge("d2", "fix", label="[xác nhận sự cố]")
    a.edge("d2", "fp", "l", "r", label="[không phải sự cố]", lpos=(612, 525, "middle"))
    a.edge("fix", "m", "b", "r", via=[(P, 690)])
    a.edge("fp", "m")
    a.edge("watch", "m", "l", "l", via=[(296, 450), (296, 690)])
    a.edge("m", "next", "b", "r", via=[(Q, 760)])
    a.edge("next", "d3")
    a.edge("d3", "e", label="[về mức bình thường]")
    a.edge("d3", "scan", "l", "l", via=[(14, 835), (14, 125)], label="[còn lệch]", lpos=(24, 820, "start"))
    a.note(Q, 880, "Hệ thống không lưu trạng thái\ngiao việc; các bước của người\nphụ trách diễn ra ngoài hệ thống", w=240)
    a.note(P, 850, "Người phụ trách theo nguyên\nnhân: P1a kế toán công nợ\nsàn; P3 quản lý chi nhánh,\nquản lý vùng; P5 quản lý\nchi nhánh, kiểm soát nội bộ", w=230)
    return save("h3_act_canh_bao", a.render())


# ---------------------------------------------------------------------- tuan tu: bo ket noi keo du lieu qua API
def h3_seq_api():
    s = Sequence(830, [("af", "Airflow\nbước extract", "obj", 70), ("ex", "Bộ kết nối\nextract.py", "obj", 230),
                       ("api", "API nguồn\nsource-api", "obj", 410), ("vt", "Vùng tiếp nhận\nsource_systems", "obj", 590),
                       ("st", "Tệp trạng thái\napi_connector.json", "obj", 745)], top=8, head=58, step=36)
    s.activate("af", s.y - 12)
    s.msg("af", "ex", "chạy bước extract", act=True)
    s.msg("ex", "st", "đọc mốc ngày đã lấy đủ")
    s.msg("st", "ex", "mốc, ví dụ 22/09/2024", kind="ret")
    s.msg("ex", "api", "GET business-dates, Bearer")
    s.msg("api", "ex", "danh sách ngày đã có", kind="ret")
    y_outer = s.y - 16
    s.space(26)
    y_inner = s.y - 14
    s.space(28)
    s.msg("ex", "api", "GET receipts: ngày, trang", act=True)
    y_alt = s.y - 14
    s.space(28)
    s.msg("api", "ex", "503 lỗi tạm thời hoặc 429 quá tần suất", kind="ret")
    s.self_msg("ex", "chờ tăng dần rồi gọi lại, tối đa 6 lần")
    y_sep = s.y - 14
    s.space(22)
    s.msg("api", "ex", "200: trang bản ghi, tổng số", kind="ret")
    s.deactivate("api", s.y - 26)
    y_alt_end = s.y - 12
    s.space(6)
    y_inner_end = s.y - 10
    s.space(10)
    s.self_msg("ex", "đối chiếu số bản ghi nhận với tổng API báo")
    s.msg("ex", "vt", "ghi tệp tạm rồi đổi tên, mỗi máy POS một tệp")
    s.msg("ex", "st", "dời mốc sang ngày vừa lấy đủ")
    y_outer_end = s.y - 12
    s.space(12)
    s.msg("ex", "af", "tóm tắt lượt kéo", kind="ret")
    s.deactivate("ex", s.y - 26)
    s.deactivate("af", s.y - 18)
    s.frame("loop", "ex", "st", y_outer, y_outer_end, [(None, "[mỗi ngày từ ngày mốc trở đi]")], pad=96, rpad=78)
    s.frame("loop", "ex", "api", y_inner, y_inner_end, [(None, "[còn trang]")], pad=80)
    s.frame("alt", "ex", "api", y_alt, y_alt_end, [(None, "[lỗi tạm thời]"), (y_sep, "[thành công]")], pad=64)
    return save("h3_seq_api", s.render())


# ---------------------------------------------------------------------- tuan tu: gui tep qua trang tai len
def h3_seq_tai_len():
    s = Sequence(830, [("u", "Người gửi", "actor", 50), ("app", "Trang\nTải tệp lên", "obj", 205),
                       ("in", "Phần tiếp nhận\nintake, contracts", "obj", 395), ("vt", "Vùng tiếp nhận", "obj", 575),
                       ("af", "Airflow\nREST API", "obj", 740)], top=8, head=58, step=36)
    s.msg("u", "app", "chọn tệp, bấm Gửi", act=True)
    y_loop = s.y - 14
    s.space(28)
    s.msg("app", "in", "intake(tên tệp, nội dung)", act=True)
    s.self_msg("in", "nhận dạng nguồn, kiểm hợp đồng")
    y_alt = s.y - 14
    s.space(28)
    s.msg("in", "vt", "ghi tệp tạm .part rồi đổi tên")
    y_sep = s.y - 12
    s.space(24)
    s.self_msg("in", "lưu vào _rejected, ghi lý do")
    y_alt_end = s.y - 12
    s.space(4)
    s.msg("in", "app", "trạng thái, nguồn, vị trí, lý do", kind="ret")
    s.deactivate("in", s.y - 26)
    y_loop_end = s.y - 10
    s.space(14)
    y_opt = s.y - 14
    s.space(28)
    s.msg("app", "af", "POST datasets/events: Dataset nguồn")
    s.self_msg("af", "lên lịch lượt DAG fastfat_pipeline", left=True)
    s.msg("af", "app", "đã ghi nhận sự kiện", kind="ret")
    y_opt_end = s.y - 12
    s.space(10)
    s.msg("app", "u", "bảng kết quả tiếp nhận từng tệp", kind="ret")
    s.deactivate("app", s.y - 26)
    s.frame("loop", "app", "vt", y_loop, y_loop_end, [(None, "[mỗi tệp trong lần gửi]")], pad=62, rpad=118)
    s.frame("alt", "in", "vt", y_alt, y_alt_end, [(None, "[tệp mới hoặc bản sửa]"),
                                                   (y_sep, "[trùng, sai hợp đồng, không nhận dạng được]")], pad=46, rpad=100)
    s.frame("opt", "app", "af", y_opt, y_opt_end, [(None, "[có tệp được nhận hoặc thay bản cũ]")], pad=56)
    return save("h3_seq_tai_len", s.render())


# ---------------------------------------------------------------------- tuan tu: truy vet va mo tep goc
def h3_seq_truy_vet():
    s = Sequence(850, [("u", "Quản lý", "actor", 45), ("tr", "Trang\nTruy vết", "obj", 185),
                       ("an", "analytics\ndetect, actions", "obj", 345), ("db", "Kho DuckDB\nGold, Silver", "obj", 505),
                       ("sr", "Trang\nTệp nguồn", "obj", 655), ("vt", "Vùng tiếp nhận", "obj", 785)],
                 top=8, head=58, step=36)
    s.msg("u", "tr", "chọn chi nhánh, tuần", act=True)
    s.msg("tr", "db", "đọc Gold, kết nối chỉ đọc")
    s.msg("db", "tr", "bảng chiều, sự kiện, chỉ số", kind="ret")
    s.msg("tr", "an", "score_all, alert_table", act=True)
    s.msg("an", "tr", "điểm, mức cảnh báo", kind="ret")
    s.deactivate("an", s.y - 26)
    s.msg("tr", "an", "đề xuất xử lý", act=True)
    s.msg("an", "tr", "việc cần làm, thiệt hại", kind="ret")
    s.deactivate("an", s.y - 26)
    s.msg("tr", "db", "bản ghi bằng chứng kèm tệp, dòng gốc")
    s.msg("db", "tr", "hóa đơn, dòng đối soát, ca làm", kind="ret")
    s.msg("tr", "u", "kết luận, cây KPI, bằng chứng gốc", kind="ret")
    s.msg("u", "tr", "bấm Mở tệp gốc")
    s.msg("tr", "sr", "chuyển trang: tệp và chuỗi lọc", act=True)
    s.deactivate("tr", s.y - 26)
    s.msg("sr", "vt", "đọc tệp nguyên văn")
    s.msg("vt", "sr", "nội dung tệp", kind="ret")
    s.msg("sr", "u", "đúng dòng gốc đã lọc sẵn", kind="ret")
    s.deactivate("sr", s.y - 26)
    return save("h3_seq_truy_vet", s.render())


# ---------------------------------------------------------------------- phan ra chuc nang
def h3_bfd():
    groups = [
        ("Thu thập\ndữ liệu", ["Kéo dữ liệu qua\nAPI theo mốc ngày", "Nhận tệp xuất\ntự động", "Tiếp nhận tệp\ntải lên",
                               "Kiểm tra hợp\nđồng dữ liệu", "Theo dõi kết nối\nnguồn", "Xem tệp nguồn\nnguyên văn"]),
        ("Xử lý và\nlưu trữ", ["Nạp Bronze\ntăng dần", "Cửa chặn chất\nlượng đầu vào", "Làm sạch, chuẩn\nhóa, cách ly",
                              "Lược đồ hình sao,\nSCD loại 2", "Kiểm thử, đối\nsoát giữa tầng"]),
        ("Phân tích\nvận hành", ["Dashboard kinh\ndoanh Metabase", "Quét chỉ số,\nchấm nguyên nhân", "Trung tâm\ncảnh báo",
                                "Truy vết theo\ncây KPI", "Đề xuất xử lý,\nbằng chứng gốc"]),
        ("Vận hành\nnền tảng", ["Điều phối hai\nDAG Airflow", "Theo dõi lượt\nxử lý hằng ngày", "Đưa sang kho\nphục vụ",
                               "Tra cứu kho\nbằng SQL", "Mô hình và\nphả hệ dữ liệu"]),
        ("Kiểm chứng", ["Bộ mô phỏng:\nsự thật và ghi\nnhận", "Đánh giá bộ\nphát hiện"]),
    ]
    return save("h3_bfd", bfd("Nền tảng dữ liệu vận hành Fast&Fat", groups, w=820))


# ---------------------------------------------------------------------- trien khai
def h4_trien_khai():
    W, H = 840, 640
    s = []

    def link(pts, label=None, lpos=None, dash=False, anchor="middle"):
        s.append(poly(pts, dash=dash, arrow="open"))
        if label:
            x, y = lpos
            s.append(text(x, y, label, 12, anchor, color=LABEL, halo=True))

    s.append(node3d(20, 26, 210, 66, "Trình duyệt web", "device"))
    s.append(text(30, 80, "người dùng, giảng viên", 12, "start", color=MUTED))
    s.append(node3d(14, 140, 800, 482, "Máy chủ Linux hoặc máy cá nhân", "device", fill="#ffffff", right=True))
    s.append(node3d(32, 206, 762, 400, "Docker Engine, Docker Compose", "execution environment", fill="#ffffff", right=True))
    # hang 1
    s.append(node3d(52, 280, 150, 96, "caddy", "container", dash=True))
    a, _ = artifact(62, 330, 130, "HTTPS tự động,\nchỉ trên máy chủ", 11.5)
    s.append(a)
    s.append(node3d(232, 280, 150, 96, "app :8501", "container"))
    a, _ = artifact(242, 330, 130, "Streamlit\napp/main.py", 11.5)
    s.append(a)
    s.append(node3d(442, 280, 180, 120, "airflow :8080", "container"))
    a, _ = artifact(452, 330, 160, "DAG fastfat_nguon,\nfastfat_pipeline", 11.5)
    s.append(a)
    a, _ = artifact(452, 368, 160, "pipeline/, dbt/", 11.5)
    s.append(a)
    s.append(node3d(662, 280, 116, 96, "source-api", "container"))
    a, _ = artifact(670, 330, 100, "FastAPI\ncổng 8600", 11.5)
    s.append(a)
    # hang 2
    s.append(node3d(52, 458, 150, 96, "metabase :3000", "container"))
    a, _ = artifact(62, 508, 130, "dashboard\ndựng bằng mã", 11.5)
    s.append(a)
    a, vh = artifact(232, 466, 200, "«volume» thư mục dự án\n/opt/fastfat: data/, kho\nDuckDB, vùng tiếp nhận", 11.5)
    s.append(a)
    s.append(node3d(482, 458, 170, 96, "warehouse-db", "container"))
    a, _ = artifact(492, 508, 150, "PostgreSQL 16 :5432\nvolume pgdata", 11.5)
    s.append(a)
    # ket noi
    link([(127, 92), (127, 280)], "HTTPS 443", (133, 116), anchor="start")
    link([(202, 318), (232, 318)])
    link([(160, 280), (160, 252), (532, 252), (532, 280)], "HTTP qua mạng nội bộ", (346, 244))
    link([(127, 376), (127, 458)], "HTTP", (133, 420), anchor="start")
    link([(382, 318), (442, 318)], "REST", (412, 310))
    link([(632, 318), (662, 318)], "HTTP", (647, 306))
    link([(300, 376), (300, 466)], "đọc, chỉ đọc", (306, 420), anchor="start")
    link([(470, 400), (470, 430), (410, 430), (410, 466)], "ghi kho", (440, 422))
    link([(590, 400), (590, 458)], "publish", (596, 432), anchor="start")
    link([(127, 554), (127, 590), (560, 590), (560, 554)], "bi_reader, chỉ đọc", (343, 582))
    s.append(text(814, 60, "Nét đứt: chỉ có ở cấu hình máy chủ.\nKhi chạy trên máy cá nhân, trình duyệt\nmở thẳng các cổng 8501, 8080, 3000.", 12,
                  "end", color=MUTED))
    return save("h4_trien_khai", page("".join(s), W, H))


ALL = [h3_act_tiep_nhan, h3_act_lo_du_lieu, h3_act_canh_bao, h3_seq_api, h3_seq_tai_len, h3_seq_truy_vet, h3_bfd,
       h4_trien_khai]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = [f() for f in ALL if not want or f.__name__ in want]
    if "--khong-xuat" not in sys.argv:
        from render import render
        render(names)
