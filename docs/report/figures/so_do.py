"""So do khoi cho bao cao, ve theo loi so do hoc thuat: khung chu nhat goc vuong net den manh, nen trang,
font Times New Roman nhu than bai, mui ten tam giac dac, duong noi gap khuc vuong goc, nhom bang khung net dut.
Toa do dat bang tay; co chu 14,5-15 px tren be rong 830-930 px -> khi in rong 15-16 cm chu khoang 8 pt.

  .venv/Scripts/python docs/report/figures/so_do.py              # sinh tat ca roi xuat PNG
  .venv/Scripts/python docs/report/figures/so_do.py h3_2_kien_truc
"""
import math
import sys
from html import escape
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
FONT = "'Times New Roman', Times, serif"
K = "#000000"
SIZE = 15


def page(body, w, h):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0;background:#fff}}'
            f'#fig{{display:inline-block;padding:8px;background:#fff}}</style></head><body><div id="fig">'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}" fill="{K}">'
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{K}"/></marker>'
            f'<marker id="o" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10" fill="none" stroke="{K}" stroke-width="1.3"/>'
            f'</marker></defs>{body}</svg></div></body></html>')


def text(x, y, s, size=SIZE, anchor="middle", bold=False, italic=False, halo=False):
    """Chu nhieu dong tach bang \\n; y la tam doc cua ca khoi. Dong bat dau bang '!' in dam, '*' in nghieng."""
    lines = s.split("\n")
    lh = size * 1.22
    y0 = y - lh * (len(lines) - 1) / 2 + size * 0.34
    out = []
    for i, t in enumerate(lines):
        b, it = bold, italic
        if t.startswith("!"):
            t, b = t[1:], True
        if t.startswith("*"):
            t, it = t[1:], True
        st = ' font-weight="bold"' if b else ""
        st += ' font-style="italic"' if it else ""
        if halo:
            st += ' stroke="#fff" stroke-width="4" paint-order="stroke" stroke-linejoin="round"'
        out.append(f'<text x="{x:.1f}" y="{y0 + i * lh:.1f}" font-size="{size}" text-anchor="{anchor}"{st}>'
                   f'{escape(t)}</text>')
    return "".join(out)


def box(x, y, w, h, label="", size=SIZE, dash=False, sw=1.1, fill="#fff"):
    da = ' stroke-dasharray="5 3"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{K}" stroke-width="{sw}"{da}/>'
            + (text(x + w / 2, y + h / 2, label, size) if label else ""))


def line(pts, arrow="a", dash=False, sw=1.1):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    da = ' stroke-dasharray="5 3"' if dash else ""
    mk = f' marker-end="url(#{arrow})"' if arrow else ""
    return f'<polyline points="{d}" fill="none" stroke="{K}" stroke-width="{sw}"{da}{mk}/>'


def save(name, html):
    (SRC / f"{name}.html").write_text(html, encoding="utf-8")
    return name


# ---------------------------------------------------------------------- Hinh 1.1 quy trinh nghien cuu
def h1_1_quy_trinh():
    W, H = 830, 510
    bw, bh, gx = 240, 104, 40
    xs = [20, 20 + bw + gx, 20 + 2 * (bw + gx)]
    ys = [20, 200, 380]
    steps = [
        ("Bước 1. Xác định vấn đề", "năm vấn đề P1–P5, câu hỏi\nvà mục tiêu nghiên cứu", "Chương 1"),
        ("Bước 2. Tổng quan lý thuyết", "chỉ số F&B, kho dữ liệu, chất lượng\ndữ liệu, phát hiện bất thường", "Chương 2"),
        ("Bước 3. Phân tích và thiết kế", "yêu cầu, kiến trúc, kho dữ liệu,\nlớp phân tích", "Chương 3"),
        ("Bước 4. Mô phỏng dữ liệu nguồn", "bảy hệ thống nguồn, hai tập\nkịch bản sự cố có đáp án", "Chương 3, 4"),
        ("Bước 5. Xây dựng đường ống", "thu thập, Bronze, Silver, Gold,\nkiểm thử, điều phối", "Chương 4"),
        ("Bước 6. Xây dựng lớp phân tích", "mức kỳ vọng, cây KPI,\nnăm bộ phát hiện", "Chương 4"),
        ("Bước 7. Chọn tham số", "trên tập phát triển; chốt cấu hình\ntrước khi xem tập kiểm tra", "Chương 5"),
        ("Bước 8. Đánh giá", "trên tập kiểm tra, chạy một lần;\nso với phương án cơ sở", "Chương 5"),
        ("Bước 9. Kết luận", "trả lời câu hỏi nghiên cứu,\nhạn chế, hướng phát triển", "Chương 6"),
    ]
    s = []
    for i, (t, d, ch) in enumerate(steps):
        x, y = xs[i % 3], ys[i // 3]
        s.append(box(x, y, bw, bh))
        s.append(text(x + bw / 2, y + 19, t, bold=True))
        s.append(text(x + bw / 2, y + 55, d))
        s.append(text(x + bw / 2, y + 89, f"({ch})", italic=True))
    for r in range(3):
        for c in range(2):
            y = ys[r] + bh / 2
            s.append(line([(xs[c] + bw, y), (xs[c + 1], y)]))
    for r in range(2):      # chuyen hang: tu khoi cuoi hang xuong khoi dau hang sau
        x_end, x_start = xs[2] + bw / 2, xs[0] + bw / 2
        y0, y1 = ys[r] + bh, ys[r + 1]
        ym = y0 + 22
        s.append(line([(x_end, y0), (x_end, ym), (x_start, ym), (x_start, y1)]))
    # vong lap: buoc 7 quay lai buoc 6
    x7, x6 = xs[0] + bw * 0.8, xs[2] + bw * 0.8
    ym = ys[2] - 18
    s.append(line([(x7, ys[2]), (x7, ym), (x6, ym), (x6, ys[1] + bh)], dash=True))
    s.append(text((x7 + x6) / 2, ym - 11, "chưa đạt trên tập phát triển: quay lại điều chỉnh", 14, italic=True,
                  halo=True))
    return save("h1_1_quy_trinh", page("".join(s), W, H))


# ---------------------------------------------------------------------- Hinh 3.1 ca su dung
def actor(x, y, label):
    """Hinh nguoi UML, tam than o (x, y); nhan o duoi."""
    return (f'<g fill="none" stroke="{K}" stroke-width="1.4"><circle cx="{x}" cy="{y - 27}" r="8"/>'
            f'<path d="M{x},{y - 19} V{y + 6} M{x - 15},{y - 10} H{x + 15} M{x},{y + 6} L{x - 12},{y + 24} '
            f'M{x},{y + 6} L{x + 12},{y + 24}"/></g>' + text(x, y + 44, label))


def ellipse_point(cx, cy, rx, ry, px, py):
    """Diem tren duong elip theo huong tu tam toi (px, py)."""
    dx, dy = px - cx, py - cy
    t = 1 / math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    return cx + dx * t, cy + dy * t


def h3_1_use_case():
    W, H = 930, 640
    s = []
    bx0, bx1 = 285, 755
    s.append(f'<rect x="{bx0}" y="10" width="{bx1 - bx0}" height="620" fill="none" stroke="{K}" stroke-width="1.2"/>')
    s.append(text(bx0 + 10, 30, "Nền tảng dữ liệu vận hành Fast&Fat", anchor="start", bold=True))
    rx, ry = 104, 30
    lx, rxc = 395, 642
    uc = {
        "upload": (lx, 95, "Gửi tệp nguồn\nqua trang tải lên"),
        "dash": (lx, 195, "Xem dashboard kinh doanh\ntheo chi nhánh và kỳ"),
        "alert": (lx, 295, "Xem cảnh báo sắp theo\nthiệt hại ước tính"),
        "trace": (lx, 395, "Truy vết nguyên nhân\nbiến động doanh thu"),
        "evid": (lx, 530, "Xem bằng chứng gốc\nvà đề xuất xử lý"),
        "conn": (rxc, 95, "Theo dõi kết nối nguồn\nvà tệp bị từ chối"),
        "query": (rxc, 170, "Tra cứu dữ liệu\nnguồn và kho"),
        "lineage": (rxc, 245, "Xem mô hình dữ liệu\nvà phả hệ"),
        "dq": (rxc, 320, "Theo dõi chất lượng\ndữ liệu"),
        "runs": (rxc, 395, "Theo dõi lượt xử lý\nhằng ngày"),
        "eval": (rxc, 470, "Đánh giá bộ\nphát hiện"),
        "ingest": (rxc, 575, "Thu thập và xử lý\ndữ liệu mới"),
    }
    # tac nhan khai quat "nguoi dung nghiep vu" va ba vai tro ke thua (quan he khai quat hoa UML)
    px, py = 200, 300
    subs = [(55, 140, "Quản lý\nvận hành"), (55, 320, "Quản lý\nchi nhánh"), (55, 500, "Kế toán")]
    spine = 118
    for x, y, lab in subs:
        s.append(actor(x, y, lab))
        s.append(line([(x + 20, y - 5), (spine, y - 5)], arrow=None, sw=1))
    s.append(line([(spine, subs[0][1] - 5), (spine, subs[-1][1] - 5)], arrow=None, sw=1))
    tip = px - 20
    s.append(line([(spine, py - 5), (tip - 13, py - 5)], arrow=None, sw=1))
    s.append(f'<path d="M{tip - 13},{py - 13} L{tip},{py - 5} L{tip - 13},{py + 3} z" fill="#fff" stroke="{K}" '
             f'stroke-width="1.1"/>')
    s.append(actor(px, py, "Người dùng\nnghiệp vụ"))
    # noi vao mep trai / phai cua elip de duong lien ket khong cat qua elip khac
    for u in ("dash", "alert", "trace", "upload"):
        cx, cy, _ = uc[u]
        s.append(line([(px + 18, py - 5), (cx - rx, cy)], arrow=None, sw=1))
    eng = (855, 280)
    for u in ("conn", "query", "lineage", "dq", "runs", "eval"):
        cx, cy, _ = uc[u]
        s.append(line([(eng[0] - 18, eng[1] - 5), (cx + rx, cy)], arrow=None, sw=1))
    s.append(actor(*eng, "Kỹ sư\ndữ liệu"))
    for y, name in ((540, "Hệ thống nguồn"), (605, "Apache Airflow")):
        s.append(box(790, y - 25, 130, 50))
        s.append(text(855, y - 9, "«system»", 13))
        s.append(text(855, y + 10, name))
        ex, ey = ellipse_point(rxc, 575, rx, ry, 790, y)
        s.append(line([(790, y), (ex, ey)], arrow=None, sw=1))
    for cx, cy, lab in uc.values():
        s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" stroke="{K}" stroke-width="1.1"/>')
        s.append(text(cx, cy, lab, 14.5))
    s.append(line([(lx, 395 + ry), (lx, 530 - ry)], arrow="o", dash=True))
    s.append(text(lx + 8, 462, "«include»", 14, anchor="start"))
    return save("h3_1_use_case", page("".join(s), W, H))


# ---------------------------------------------------------------------- Hinh 3.2 kien truc tong the
def h3_2_kien_truc():
    W, H = 900, 760
    s = []
    C = {1: (10, 150), 2: (190, 165), 3: (385, 200), 4: (615, 140), 5: (780, 110)}   # (x, rong) tung cot
    heads = {1: "Nguồn dữ liệu", 2: "Thu thập", 3: "Lưu trữ và biến đổi", 4: "Phân tích", 5: "Phục vụ"}

    def cx(c):
        return C[c][0] + C[c][1] / 2

    def label(name, tech=None, desc=None):
        return "\n".join([f"!{t}" for t in name.split("\n")] + ([f"*{tech}"] if tech else [])
                         + (desc.split("\n") if desc else []))

    def blk(c, y, h, name, tech=None, desc=None, dash=False):
        x, w = C[c]
        return box(x, y, w, h, dash=dash) + text(x + w / 2, y + h / 2, label(name, tech, desc), 14.5)

    # vung kiem chung, nam ngoai duong ong
    s.append(box(10, 10, 150, 66, dash=True))
    s.append(text(85, 43, "!Bộ mô phỏng\nđóng vai hệ thống nguồn;\nđáp án lưu riêng", 14))
    s.append(box(615, 10, 275, 66, dash=True))
    s.append(text(752, 43, "!Chương trình đánh giá\nso cảnh báo với đáp án,\nkhông thuộc đường ống", 14))
    s.append(line([(160, 30), (615, 30)], dash=True))
    s.append(text(388, 21, "đáp án (đường ống không đọc)", 14, italic=True))
    s.append(line([(24, 76), (24, 135)], dash=True))
    for c, t in heads.items():
        s.append(text(cx(c), 103, t, 15.5, bold=True))
    s.append(f'<line x1="10" y1="118" x2="890" y2="118" stroke="{K}" stroke-width="0.8"/>')
    # cot 1: nguon
    s.append(blk(1, 135, 78, "POS đám mây,\nApp đặt hàng", desc="dữ liệu chỉ lấy\nđược qua API"))
    s.append(blk(1, 260, 78, "POS tại máy,\nchấm công, danh mục", desc="tệp JSON, CSV\nxuất theo lịch"))
    s.append(blk(1, 385, 78, "Báo cáo sàn,\nsổ kho, kiểm kê", desc="tệp CSV, Excel\ndo người gửi"))
    # cot 2: thu thap
    s.append(blk(2, 135, 78, "Bộ kết nối API", "Python", "kéo tăng dần theo mốc\nngày, đối chiếu tổng"))
    s.append(blk(2, 260, 78, "Vùng tiếp nhận", desc="ba kênh về một chỗ,\nmỗi nguồn một thư mục"))
    s.append(blk(2, 385, 78, "Hợp đồng dữ liệu", "Python", "nhận dạng theo nội dung,\ntừ chối tệp sai"))
    for y in (174, 299, 424):
        s.append(line([(160, y), (190, y)]))
    s.append(line([(cx(2), 213), (cx(2), 260)]))
    s.append(line([(cx(2), 385), (cx(2), 338)]))
    # cot 3: DuckDB + dbt
    x3, w3 = C[3]
    s.append(f'<rect x="{x3}" y="135" width="{w3}" height="455" fill="none" stroke="{K}" stroke-width="1.3"/>')
    s.append(text(x3 + w3 / 2, 152, "!DuckDB, dbt", 15))
    ix, iw = x3 + 14, w3 - 28

    def inner(y, h, name, tech, desc, dash=False):
        return box(ix, y, iw, h, dash=dash) + text(ix + iw / 2, y + h / 2, label(name, tech, desc), 14.5)
    s.append(inner(170, 78, "Bronze", "ingest.py", "bản gốc nguyên văn,\nkèm tệp và số dòng"))
    s.append(inner(272, 54, "Cửa chặn chất lượng", None, "lô thiếu dữ liệu thì dừng", dash=True))
    s.append(inner(350, 78, "Silver", "mô hình dbt staging", "làm sạch, ánh xạ sáu hệ\nmã, cách ly dòng lỗi"))
    s.append(inner(452, 96, "Gold", "mô hình dbt marts", "lược đồ hình sao, SCD\nkiểu 2, bảng chỉ số và\nmức kỳ vọng"))
    s.append(text(x3 + w3 / 2, 572, "*158 kiểm thử, đối soát số dòng", 14))
    s.append(line([(355, 299), (370, 299), (370, 209), (ix, 209)]))
    for y0, y1 in ((248, 272), (326, 350), (428, 452)):
        s.append(line([(x3 + w3 / 2, y0), (x3 + w3 / 2, y1)]))
    # cot 4: phan tich
    s.append(blk(4, 260, 110, "Bộ phát hiện\nP1–P5", "Python", "thống kê vững,\nkiểm định Poisson,\nluật đối soát"))
    s.append(blk(4, 400, 96, "Truy vết, đề\nxuất xử lý", desc="cây KPI, bằng chứng\ngốc, thiệt hại\nước tính"))
    gx = ix + iw
    s.append(line([(gx, 480), (600, 480), (600, 315), (615, 315)]))
    s.append(line([(cx(4), 370), (cx(4), 400)]))
    s.append(line([(632, 260), (632, 76)], dash=True))
    # cot 5: phuc vu
    s.append(blk(5, 135, 96, "Ứng dụng\nStreamlit", desc="cảnh báo, truy\nvết, chất lượng\ndữ liệu"))
    s.append(blk(5, 270, 78, "Metabase", desc="dashboard\nkinh doanh"))
    s.append(blk(5, 440, 100, "PostgreSQL", "publish.py", "kho phục vụ,\nbản sao đã\nđối soát"))
    s.append(line([(755, 448), (767, 448), (767, 190), (780, 190)]))
    s.append(line([(cx(5), 440), (cx(5), 348)]))
    s.append(line([(cx(5), 270), (cx(5), 231)]))
    s.append(text(cx(5) + 6, 255, "nhúng", 14, "start", italic=True))
    s.append(line([(gx, 530), (762, 530), (762, 500), (780, 500)]))
    s.append(text(690, 522, "sao chép Gold", 14, italic=True))
    # thanh dieu phoi
    s.append(f'<rect x="10" y="615" width="880" height="130" fill="none" stroke="{K}" stroke-width="1.2"/>')
    s.append(text(20, 634, "!Apache Airflow (trong Docker Compose)", 15, "start"))
    steps = ["extract", "check", "ingest", "quality", "dbt build", "detect", "publish"]
    sw, gap = 96, 27
    x = 20
    for i, st in enumerate(steps):
        s.append(box(x, 655, sw, 34, st, 14.5))
        if i:
            s.append(line([(x - gap, 672), (x, 672)]))
        x += sw + gap
    s.append(text(20, 718, "*Chạy khi hệ thống nguồn báo có dữ liệu mới và tự kiểm tra mỗi giờ; "
                           "một bước lỗi thì các bước sau không chạy.", 14, "start"))
    return save("h3_2_kien_truc", page("".join(s), W, H))


# ---------------------------------------------------------------------- Hinh 3.3 chuoi nhan qua
def rich(x, y, parts, size=SIZE, anchor="middle"):
    """Mot dong chu co bien in nghieng, chi so duoi, mu: parts = [(chu, kieu)], kieu: '', 'i', 'sub', 'isub', 'sup'."""
    out, shift = [], 0
    for t, k in parts:
        dy = {"sub": 4, "isub": 4, "sup": -6}.get(k, 0) - shift
        shift += dy
        st = ' font-style="italic"' if k in ("i", "isub") else ""
        fs = f' font-size="{size * 0.75:.1f}"' if k in ("sub", "isub", "sup") else ""
        out.append(f'<tspan dy="{dy}"{st}{fs}>{escape(t)}</tspan>')
    if shift:
        out.append(f'<tspan dy="{-shift}"></tspan>')
    return (f'<text x="{x:.1f}" y="{y + size * 0.34:.1f}" font-size="{size}" text-anchor="{anchor}">'
            + "".join(out) + "</text>")


def h3_3_chuoi_nhan_qua():
    W, H = 790, 600
    s = []

    def node(x, y, w, h, lines):
        """lines: chuoi thuong (nhieu dong) hoac danh sach dong, moi dong la chuoi hoac danh sach parts cua rich."""
        out = box(x, y, w, h)
        if isinstance(lines, str):
            return out + text(x + w / 2, y + h / 2, lines)
        lh = SIZE * 1.25
        y0 = y + h / 2 - lh * (len(lines) - 1) / 2
        for i, ln in enumerate(lines):
            yy = y0 + i * lh
            out += text(x + w / 2, yy, ln) if isinstance(ln, str) else rich(x + w / 2, yy, ln)
        return out

    s.append(node(200, 20, 200, 46, "Số nhân viên bếp\ncó mặt trong giờ"))
    s.append(node(150, 96, 300, 44, [[("Tải bếp ", ""), ("u", "i"), ("(", ""), ("h", "i"), (") = ", ""), ("n", "i"),
                                       ("(", ""), ("h", "i"), (") / (", ""), ("c", "i"), ("b", "isub"), (" · ", ""),
                                       ("e", "i"), ("(", ""), ("h", "i"), ("))", "")]]))
    s.append(line([(300, 66), (300, 96)]))
    s.append(text(308, 81, "ít người", 14, "start", italic=True))
    # tai bep -> khach bo ve, thoi gian chuan bi, cua hang huy don
    s.append(line([(300, 140), (300, 165)], arrow=None))
    s.append(line([(95, 165), (695, 165)], arrow=None))
    for x in (95, 300, 695):
        s.append(line([(x, 165), (x, 190)]))
    s.append(rich(101, 178, [("u", "i"), (" > 0,90", "")], 14, "start"))
    s.append(rich(701, 178, [("u", "i"), (" > 0,85", "")], 14, "start"))
    s.append(node(20, 190, 150, 50, "Khách tại quầy\nbỏ về"))
    s.append(node(190, 190, 220, 54, ["Thời gian chuẩn bị",
                                      [("T", "i"), (" = 4 + 6 / (1 − ", ""), ("ρ", "i"), (")", ""), ("0,6", "sup"),
                                       (" phút", "")]]))
    s.append(node(625, 190, 140, 50, "Cửa hàng hủy\nđơn trực tuyến"))
    # thoi gian chuan bi -> khach tu huy, diem danh gia
    s.append(line([(300, 244), (300, 270)], arrow=None))
    s.append(line([(240, 270), (380, 270)], arrow=None))
    for x in (240, 380):
        s.append(line([(x, 270), (x, 295)]))
    s.append(rich(234, 283, [("T", "i"), (" > 18 phút", "")], 14, "end"))
    s.append(rich(374, 283, [("T", "i"), (" > 15 phút", "")], 14, "end"))
    s.append(node(165, 295, 150, 52, "Khách đặt trực tuyến\ntự hủy vì chờ lâu"))
    s.append(node(325, 295, 115, 52, "Điểm đánh giá\ntừng đơn giảm"))
    # tac dong tre qua thu hang tren san
    s.append(f'<rect x="455" y="264" width="180" height="270" fill="none" stroke="{K}" stroke-width="1" '
             f'stroke-dasharray="6 4"/>')
    s.append(text(465, 280, "Các tuần sau", 14.5, "start", bold=True))
    s.append(node(465, 298, 160, 76, [[("Điểm cửa hàng ", ""), ("S", "i"), ("t", "isub")], "(trung bình trượt,",
                                      "trừ theo tỷ lệ", "cửa hàng hủy đơn)"]))
    s.append(node(465, 400, 160, 52, ["Hệ số thứ hạng",
                                      [("X", "i"), ("t+1", "isub"), (" = 1 + 0,8(", ""), ("S", "i"), ("t", "isub"),
                                       (" − 4,5)", "")]]))
    s.append(node(465, 476, 160, 46, "Số đơn sàn giảm\ntrong 1–3 tuần"))
    s.append(line([(440, 321), (465, 321)]))
    s.append(line([(545, 374), (545, 400)]))
    s.append(line([(545, 452), (545, 476)]))
    s.append(line([(695, 240), (695, 337), (625, 337)]))
    # doanh thu giam ngay
    s.append(node(20, 545, 300, 40, "Doanh thu tại quầy và App giảm ngay"))
    s.append(line([(95, 240), (95, 545)]))
    s.append(line([(240, 347), (240, 545)]))
    s.append(line([(695, 337), (695, 565), (320, 565)]))
    return save("h3_3_chuoi_nhan_qua", page("".join(s), W, H))


# ---------------------------------------------------------------------- Hinh 3.7 hai DAG
def note(x, y, w, h, label, size=SIZE, anchor="middle"):
    """Ghi chu UML: hinh chu nhat gap goc tren phai."""
    f = 10
    out = (f'<path d="M{x},{y} H{x + w - f} L{x + w},{y + f} V{y + h} H{x} z" fill="#fff" stroke="{K}" '
           f'stroke-width="1.1"/><path d="M{x + w - f},{y} V{y + f} H{x + w}" fill="none" stroke="{K}" '
           f'stroke-width="1.1"/>')
    tx = x + w / 2 if anchor == "middle" else x + 10
    return out + text(tx, y + h / 2, label, size, anchor)


def h3_7_dag():
    W, H = 880, 575
    s = []
    # DAG nguon
    s.append(f'<rect x="10" y="10" width="535" height="100" fill="none" stroke="{K}" stroke-width="1.2"/>')
    s.append(text(20, 27, "DAG fastfat_nguon: hệ thống nguồn, 23:00 hằng ngày", anchor="start", bold=True))
    s.append(box(25, 42, 235, 56, "chờ đường ống rảnh (không ghi\nkhi lô trước đang được xử lý)"))
    s.append(box(290, 42, 240, 56, "ghi dữ liệu ngày kinh doanh mới\n(trong khóa luận: bộ mô phỏng)"))
    s.append(line([(260, 70), (290, 70)]))
    s.append(note(635, 42, 230, 56, "Dataset: dữ liệu nguồn\nđược cập nhật"))
    s.append(line([(545, 70), (635, 70)]))
    s.append(text(590, 60, "báo cập nhật", 14, italic=True))
    # DAG duong ong: tieu de o day khung de mui ten vao buoc 1 khong cat qua chu
    s.append(f'<rect x="10" y="140" width="865" height="318" fill="none" stroke="{K}" stroke-width="1.2"/>')
    s.append(text(20, 440, "DAG fastfat_pipeline: chạy khi Dataset cập nhật, tự kiểm tra thêm mỗi giờ", anchor="start",
                  bold=True))
    steps = [
        ("1. extract", "kéo dữ liệu mới qua API\ncủa POS đám mây và App", "ghi: vùng tiếp nhận, mốc"),
        ("2. check", "có tệp nguồn chưa nạp?\nkhông có thì kết thúc lượt", None),
        ("3. ingest", "nạp Bronze tăng dần theo\nmã băm, kiểm tra hợp đồng", "ghi: bronze.*, _ingest_log"),
        ("4. quality", "cửa chặn: độ mới, khối\nlượng, đầy đủ, cấu trúc", "ghi: ops.dq_checks"),
        ("5. dbt build", "dựng Silver, Gold và\nchạy 158 kiểm thử", "ghi: silver.*, gold.*"),
        ("6. detect", "quét bộ chỉ số giám sát,\nchấm điểm nguyên nhân", "ghi: ops.alerts"),
        ("7. publish", "sao Gold, ops sang\nPostgreSQL, đối soát", "ghi: kho phục vụ"),
    ]
    bw, bh = 195, 98
    xs = [25, 240, 455, 670]
    pos = [(xs[0], 160), (xs[1], 160), (xs[2], 160), (xs[3], 160), (xs[3], 300), (xs[2], 300), (xs[1], 300)]
    for (name, desc, out), (x, y) in zip(steps, pos):
        lab = f"!{name}\n{desc}" + (f"\n*{out}" if out else "")
        s.append(box(x, y, bw, bh) + text(x + bw / 2, y + bh / 2, lab, 14.5))
    for i in range(3):
        y = 160 + bh / 2
        s.append(line([(pos[i][0] + bw, y), (pos[i + 1][0], y)]))
    s.append(line([(xs[3] + bw / 2, 160 + bh), (xs[3] + bw / 2, 300)]))
    for i in (4, 5):
        y = 300 + bh / 2
        s.append(line([(pos[i][0], y), (pos[i + 1][0] + bw, y)]))
    s.append(line([(750, 98), (750, 122), (122, 122), (122, 160)]))
    # ghi chu
    s.append(note(10, 474, 865, 90,
                  "Không có tệp mới: check kết thúc lượt, các bước sau được bỏ qua, không ghi nhật ký.\n"
                  "API không phản hồi: extract chỉ ghi cảnh báo, các nguồn tệp vẫn được xử lý tiếp.\n"
                  "Cửa chặn ở mức chặn hoặc kiểm thử dbt lỗi: các bước sau không chạy, kho phục vụ giữ bản trước.\n"
                  "Mỗi bước ghi một dòng vào ops.pipeline_runs.", 14.5, "start"))
    return save("h3_7_dag", page("".join(s), W, H))


ALL = [h1_1_quy_trinh, h3_1_use_case, h3_2_kien_truc, h3_3_chuoi_nhan_qua, h3_7_dag]

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    names = [f() for f in ALL if not want or f.__name__ in want]
    if "--khong-xuat" not in sys.argv:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from render import render
        render(names)
