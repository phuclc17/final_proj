"""Ve so do UML cho bao cao bang SVG, dat vi tri bang tay de ban in de doc va dung ky hieu UML 2:
  - so do hoat dong (activity): nut bat dau, ket thuc, hanh dong bo goc, quyet dinh hinh thoi kem dieu kien
    [guard] tren canh, lan boi (swimlane), ghi chu;
  - so do tuan tu (sequence): tac nhan, duong doi, thanh kich hoat, thong diep dong bo / tra ve / tu goi,
    khung ket hop alt, loop, opt;
  - so do phan ra chuc nang (cay chuc nang);
  - so do trien khai (deployment): nut dang khoi hop 3 chieu, moi truong thuc thi, tao tac, ket noi kem giao thuc.
Moi ham tra ve mot trang HTML (div#fig chua SVG) de render.py xuat PNG. Chu 13-14 px tren be rong ~800 px
-> khi in rong 16 cm chu khoang 7,5-8 pt.
"""
from html import escape

FONT = "'Segoe UI', Arial, sans-serif"
INK, MUTED, LINE = "#1f2933", "#52606d", "#7b8794"
BLUE, BLUE_BG = "#3b6fb6", "#eef4fb"
FILL = "#ffffff"
LANE_BG = ["#f7f9fb", "#ffffff"]


def page(svg, w, h, extra_css=""):
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="_style.css">'
            f'<style>#fig{{padding:10px}} {extra_css}</style></head><body><div id="fig">'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">{DEFS}{svg}</svg></div></body></html>')


DEFS = f"""<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
  <path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>
<marker id="open" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse">
  <path d="M0,0 L10,5 L0,10" fill="none" stroke="{INK}" stroke-width="1.4"/></marker>
</defs>"""


def text(x, y, s, size=13.5, anchor="middle", weight="normal", color=INK, italic=False, lh=None, halo=False):
    """Chu nhieu dong (tach bang \\n), y la tam theo chieu doc cua ca khoi chu."""
    lines = s.split("\n")
    lh = lh or size * 1.3
    y0 = y - lh * (len(lines) - 1) / 2 + size * 0.35
    style = ' font-style="italic"' if italic else ""
    if halo:   # vien trang quanh chu de chu nam tren duong ke van doc duoc
        style += ' stroke="#fff" stroke-width="4" paint-order="stroke" stroke-linejoin="round"'
    return "".join(f'<text x="{x}" y="{y0 + i * lh:.1f}" font-size="{size}" text-anchor="{anchor}" '
                   f'font-weight="{weight}" fill="{color}"{style}>{escape(t)}</text>' for i, t in enumerate(lines))


def poly(pts, dash=False, arrow="arr", color=INK, width=1.3):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    da = ' stroke-dasharray="6 4"' if dash else ""
    mk = f' marker-end="url(#{arrow})"' if arrow else ""
    return f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da}{mk}/>'


# ====================================================================== so do hoat dong
class Activity:
    """Nut dat theo toa do tam (x, y). Canh noi theo cong: b (duoi), t (tren), l (trai), r (phai);
    duong gap khuc vuong goc, co the cho them diem trung gian (via)."""

    def __init__(self, w, h, lanes=None, lane_head=34):
        self.w, self.h, self.lanes, self.lane_head = w, h, lanes or [], lane_head
        self.nodes, self.svg_nodes, self.svg_edges = {}, [], []

    # ---- nut
    def start(self, id, x, y):
        self.nodes[id] = (x, y, 10, 10)
        self.svg_nodes.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{INK}"/>')

    def end(self, id, x, y, label=None):
        self.nodes[id] = (x, y, 12, 12)
        self.svg_nodes.append(f'<circle cx="{x}" cy="{y}" r="12" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'
                              f'<circle cx="{x}" cy="{y}" r="7.5" fill="{INK}"/>')
        if label:
            self.svg_nodes.append(text(x + 18, y, label, 12, "start", color=MUTED))

    def flow_end(self, id, x, y, label=None):
        """Ket thuc luong (vong tron co dau X): mot nhanh dung lai, cac nhanh khac van chay."""
        self.nodes[id] = (x, y, 11, 11)
        k = 7.5
        self.svg_nodes.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'
                              f'<path d="M{x-k},{y-k} L{x+k},{y+k} M{x+k},{y-k} L{x-k},{y+k}" stroke="{INK}" '
                              f'stroke-width="1.6"/>')
        if label:
            self.svg_nodes.append(text(x + 18, y, label, 12, "start", color=MUTED))

    def action(self, id, x, y, label, w=210, h=None, fill=FILL, stroke=INK, size=13.5):
        n = label.count("\n") + 1
        h = h or 18 + n * size * 1.3
        self.nodes[id] = (x, y, w / 2, h / 2)
        self.svg_nodes.append(f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="11" fill="{fill}" '
                              f'stroke="{stroke}" stroke-width="1.4"/>' + text(x, y, label, size))

    def decision(self, id, x, y, label=None, r=15):
        """Hinh thoi quyet dinh / gop; label (tuy chon) ghi canh hinh thoi de nguoi doc biet dang hoi gi."""
        self.nodes[id] = (x, y, r, r)
        self.svg_nodes.append(f'<path d="M{x},{y - r} L{x + r},{y} L{x},{y + r} L{x - r},{y} z" fill="#fff" '
                              f'stroke="{INK}" stroke-width="1.4"/>')
        if label:
            self.svg_nodes.append(text(x + r + 8, y - r - 2, label, 12.5, "start", color=MUTED, italic=True))

    def time_event(self, id, x, y, label=None):
        """Su kien thoi gian (dong ho cat): luong bat dau theo lich, vd moi gio."""
        self.nodes[id] = (x, y, 9, 12)
        self.svg_nodes.append(f'<path d="M{x - 9},{y - 12} H{x + 9} L{x - 9},{y + 12} H{x + 9} z" fill="#fff" '
                              f'stroke="{INK}" stroke-width="1.5"/>')
        if label:   # ghi duoi dong ho cat de khong vuong canh di ra
            self.svg_nodes.append(text(x, y + 26, label, 12.5, color=MUTED))

    def bar(self, id, x, y, w=160):
        """Thanh re nhanh / hop nhanh (fork / join)."""
        self.nodes[id] = (x, y, w / 2, 3)
        self.svg_nodes.append(f'<rect x="{x - w / 2}" y="{y - 3}" width="{w}" height="6" fill="{INK}"/>')

    def note(self, x, y, label, w=200, size=13, attach=None):
        n = label.count("\n") + 1
        h = 14 + n * size * 1.3
        f = 10
        x0, y0 = x - w / 2, y - h / 2
        s = (f'<path d="M{x0},{y0} H{x0 + w - f} L{x0 + w},{y0 + f} V{y0 + h} H{x0} z" fill="#fffbe6" '
             f'stroke="#b59b3c" stroke-width="1.1"/><path d="M{x0 + w - f},{y0} V{y0 + f} H{x0 + w}" fill="none" '
             f'stroke="#b59b3c" stroke-width="1.1"/>' + text(x, y, label, size, color=MUTED))
        if attach:
            ax, ay = self.port(attach[0], attach[1])
            ex = x0 if ax < x0 else x0 + w if ax > x0 + w else x
            ey = y if ax < x0 or ax > x0 + w else (y0 if ay < y0 else y0 + h)
            s = poly([(ex, ey), (ax, ay)], dash=True, arrow=None, color="#b59b3c", width=1.1) + s
        self.svg_nodes.append(s)

    # ---- canh
    def port(self, id, p):
        x, y, hw, hh = self.nodes[id]
        return {"b": (x, y + hh), "t": (x, y - hh), "l": (x - hw, y), "r": (x + hw, y)}[p]

    def edge(self, a, b, pa="b", pb="t", label=None, via=None, lpos=None, dash=False):
        p0, p1 = self.port(a, pa), self.port(b, pb)
        pts = [p0]
        if via:
            pts += via
        elif p0[0] != p1[0] and p0[1] != p1[1]:
            if pa in "lr" and pb in "tb":           # di ngang roi doc
                pts.append((p1[0], p0[1]))
            elif pa in "tb" and pb in "lr":         # di doc roi ngang
                pts.append((p0[0], p1[1]))
            elif pa in "lr" and pb in "lr":
                xm = (p0[0] + p1[0]) / 2
                pts += [(xm, p0[1]), (xm, p1[1])]
            else:                                   # doc - ngang - doc
                ym = (p0[1] + p1[1]) / 2
                pts += [(p0[0], ym), (p1[0], ym)]
        pts.append(p1)
        self.svg_edges.append(poly(pts, dash=dash))
        if label:
            if lpos:
                lx, ly, anchor = lpos
            else:   # canh doan dau tien
                (x0, y0), (x1, y1) = pts[0], pts[1]
                if abs(x1 - x0) > abs(y1 - y0):
                    lx, ly, anchor = (x0 + x1) / 2, y0 - 9, "middle"
                else:
                    lx, ly, anchor = x0 + 7, y0 + 15, "start"
            self.svg_edges.append(text(lx, ly, label, 13, anchor, color="#7a2e2e", halo=True))

    def render(self):
        s = []
        if self.lanes:
            for i, (title, x0, x1) in enumerate(self.lanes):
                s.append(f'<rect x="{x0}" y="0" width="{x1 - x0}" height="{self.h}" fill="{LANE_BG[i % 2]}" '
                         f'stroke="{LINE}" stroke-width="1.2"/>')
                s.append(f'<rect x="{x0}" y="0" width="{x1 - x0}" height="{self.lane_head}" fill="#e9eef4" '
                         f'stroke="{LINE}" stroke-width="1.2"/>')
                s.append(text((x0 + x1) / 2, self.lane_head / 2, title, 14, weight="600"))
        return page("".join(s + self.svg_edges + self.svg_nodes), self.w, self.h)


# ====================================================================== so do tuan tu
class Sequence:
    """participants: [(id, nhan, loai, x)], loai 'actor' (hinh nguoi) hoac 'obj' (hinh chu nhat).
    Thong diep them theo thu tu tu tren xuong; y tang dan tu dong."""

    def __init__(self, w, participants, top=12, head=50, step=34):
        self.w, self.top, self.head, self.step = w, top, head, step
        self.p = {pid: (label, kind, x) for pid, label, kind, x in participants}
        self.order = [pid for pid, *_ in participants]
        self.y = top + head + 24
        self.items, self.frames, self.acts, self.open = [], [], [], {}
        self.n = 0

    def x(self, pid):
        return self.p[pid][2]

    def activate(self, pid, y=None):
        self.open.setdefault(pid, []).append(y if y is not None else self.y - 6)

    def deactivate(self, pid, y=None):
        y0 = self.open[pid].pop()
        self.acts.append((pid, y0, (y if y is not None else self.y - 10), len(self.open[pid])))

    def depth(self, pid):
        return len(self.open.get(pid, []))

    def edge_x(self, pid, side, depth=None):
        """Hoanh do mep thanh kich hoat (trai/phai) o muc long `depth`; khong kich hoat thi la duong doi."""
        d = self.depth(pid) if depth is None else depth
        if d == 0:
            return self.x(pid)
        c = self.x(pid) + 6 * (d - 1)
        return c + 6 if side == "r" else c - 6

    def msg(self, a, b, label, kind="sync", act=False, number=True, gap=None):
        """kind: sync (net lien, mui ten dac), async (mui ten mo), ret (net dut, mui ten mo).
        act=True: thanh kich hoat cua b bat dau tu thong diep nay. Thong diep tra ve khong danh so."""
        if number and kind != "ret":
            self.n += 1
            label = f"{self.n}: {label}"
        y = self.y
        right = self.x(b) > self.x(a)
        db = self.depth(b) + (1 if act else 0)
        x0 = self.edge_x(a, "r" if right else "l")
        x1 = self.edge_x(b, "l" if right else "r", db)
        self.items.append(poly([(x0, y), (x1, y)], dash=kind == "ret", arrow="arr" if kind == "sync" else "open"))
        self.items.append(text((x0 + x1) / 2, y - 9, label, 13.5, color=INK if kind != "ret" else MUTED, halo=True))
        if act:
            self.activate(b, y)
        self.y += gap or self.step

    def self_msg(self, a, label, act=False, left=False):
        self.n += 1
        y = self.y
        side, k = ("l", -1) if left else ("r", 1)
        x0 = self.edge_x(a, side)
        x_back = self.edge_x(a, side, self.depth(a) + (1 if act else 0))
        w = 30
        self.items.append(poly([(x0, y), (x0 + k * w, y), (x0 + k * w, y + 18), (x_back, y + 18)]))
        self.items.append(text(x0 + k * (w + 6), y + 9, f"{self.n}: {label}", 13.5, "end" if left else "start",
                               halo=True))
        if act:
            self.activate(a, y + 16)
        self.y += self.step + 12

    def frame(self, kind, a, b, start_y, end_y, guards=(), pad=62, rpad=None):
        """Khung ket hop tu duong doi a toi b; guards: [(y_phan_cach_hoac_None, '[dieu kien]')].
        pad: le ngang tinh tu duong doi, khung long ben trong dung pad nho hon."""
        self.frames.append((kind, a, b, start_y, end_y, guards, pad, pad if rpad is None else rpad))

    def space(self, dy):
        self.y += dy

    def render(self, height=None):
        h = height or self.y + 20
        s = []
        # duong doi va dau
        for pid in self.order:
            label, kind, x = self.p[pid]
            s.append(f'<line x1="{x}" y1="{self.top + self.head}" x2="{x}" y2="{h - 8}" stroke="{LINE}" '
                     f'stroke-width="1.2" stroke-dasharray="6 5"/>')
            if kind == "actor":
                cy = self.top + 6
                s.append(f'<g fill="none" stroke="{INK}" stroke-width="1.8"><circle cx="{x}" cy="{cy + 5}" r="6"/>'
                         f'<path d="M{x} {cy + 11} V{cy + 26} M{x - 10} {cy + 16} H{x + 10} M{x} {cy + 26} '
                         f'L{x - 8} {cy + 36} M{x} {cy + 26} L{x + 8} {cy + 36}"/></g>')
                s.append(text(x, self.top + self.head - 2, label, 13, weight="600"))
            else:
                lines = label.count("\n") + 1
                bw = max(len(t) for t in label.split("\n")) * 7.4 + 22
                bh = 16 + lines * 16
                s.append(f'<rect x="{x - bw / 2}" y="{self.top + self.head - bh}" width="{bw}" height="{bh}" '
                         f'fill="{BLUE_BG}" stroke="{BLUE}" stroke-width="1.4" rx="3"/>')
                s.append(text(x, self.top + self.head - bh / 2, label, 13, weight="600"))
        # khung ket hop (ve truoc thong diep)
        late = []   # chu dieu kien ve sau cung, nam tren thanh kich hoat
        for kind, a, b, y0, y1, guards, pad, rpad in self.frames:
            xa, xb = self.x(a) - pad, self.x(b) + rpad
            s.append(f'<rect x="{xa}" y="{y0}" width="{xb - xa}" height="{y1 - y0}" fill="none" stroke="{MUTED}" '
                     f'stroke-width="1.2"/>')
            tw = len(kind) * 8 + 16
            s.append(f'<path d="M{xa},{y0} H{xa + tw} V{y0 + 12} L{xa + tw - 7},{y0 + 19} H{xa} z" fill="#fff" '
                     f'stroke="{MUTED}" stroke-width="1.2"/>' + text(xa + tw / 2 - 3, y0 + 10, kind, 12.5, weight="700"))
            for gy, g in guards:
                if gy is not None:
                    s.append(f'<line x1="{xa}" y1="{gy}" x2="{xb}" y2="{gy}" stroke="{MUTED}" stroke-dasharray="6 4"/>')
                late.append(text(xa + tw + 8 if gy is None else xa + 10, (y0 + 10) if gy is None else gy + 12, g, 13,
                                 "start", color="#7a2e2e", halo=True))
        # thanh kich hoat
        for pid in list(self.open):
            while self.open[pid]:
                self.deactivate(pid, h - 14)
        for pid, y0, y1, depth in sorted(self.acts, key=lambda a: a[3]):
            x = self.x(pid) + 6 * depth
            s.append(f'<rect x="{x - 6}" y="{y0}" width="12" height="{max(10, y1 - y0)}" fill="#fff" stroke="{INK}" '
                     f'stroke-width="1.2"/>')
        return page("".join(s + self.items + late), self.w, h)


# ====================================================================== cay chuc nang
def bfd(root, groups, w=820, col_w=None, leaf_h=40, gap=10, size=13):
    """root: ten he thong; groups: [(ten nhom, [chuc nang con])]. Kieu so do phan ra chuc nang: goc o tren, nhom
    chuc nang mot hang, chuc nang con xep doc duoi moi nhom, noi bang duong gap khuc ben trai."""
    n = len(groups)
    col_w = col_w or (w - 20) / n
    bw = col_w - 16
    s = []
    rx, ry, rw, rh = w / 2, 28, 360, 40
    s.append(f'<rect x="{rx - rw / 2}" y="{ry - rh / 2}" width="{rw}" height="{rh}" rx="4" fill="#1f3a5f"/>'
             + text(rx, ry, root, 15, weight="700", color="#fff"))
    gy = 112
    bus = 72
    s.append(f'<line x1="{rx}" y1="{ry + rh / 2}" x2="{rx}" y2="{bus}" stroke="{INK}" stroke-width="1.3"/>')
    xs = [10 + col_w * i + col_w / 2 for i in range(n)]
    s.append(f'<line x1="{xs[0]}" y1="{bus}" x2="{xs[-1]}" y2="{bus}" stroke="{INK}" stroke-width="1.3"/>')
    bottom = 0
    for (name, leaves), x in zip(groups, xs):
        gh = 46
        s.append(f'<line x1="{x}" y1="{bus}" x2="{x}" y2="{gy - gh / 2}" stroke="{INK}" stroke-width="1.3"/>')
        s.append(f'<rect x="{x - bw / 2}" y="{gy - gh / 2}" width="{bw}" height="{gh}" rx="4" fill="{BLUE_BG}" '
                 f'stroke="{BLUE}" stroke-width="1.5"/>' + text(x, gy, name, size + 0.5, weight="700"))
        lx = x - bw / 2 + 12
        y = gy + gh / 2 + gap
        for leaf in leaves:
            lines = leaf.count("\n") + 1
            lh = max(leaf_h, 14 + lines * size * 1.3)
            cx = x + 8
            s.append(f'<rect x="{cx - (bw - 16) / 2}" y="{y}" width="{bw - 16}" height="{lh}" rx="3" fill="#fff" '
                     f'stroke="{LINE}" stroke-width="1.2"/>' + text(cx, y + lh / 2, leaf, size))
            s.append(f'<path d="M{lx},{y - gap} V{y + lh / 2} H{cx - (bw - 16) / 2}" fill="none" stroke="{INK}" '
                     f'stroke-width="1.1"/>')
            y += lh + gap
        bottom = max(bottom, y)
    return page("".join(s), w, bottom + 6)


# ====================================================================== so do trien khai
def node3d(x, y, w, h, title, stereo=None, fill="#fff", d=10, size=13.5, dash=False, right=False):
    """Nut UML dang khoi hop: mat truoc + mat tren + mat ben; tieu de o goc trai tren. dash: nut tuy chon."""
    da = ' stroke-dasharray="6 4"' if dash else ""
    s = (f'<path d="M{x},{y} L{x + d},{y - d} H{x + w + d} V{y + h - d} L{x + w},{y + h}" fill="#e3e8ee" '
         f'stroke="{INK}" stroke-width="1.3"{da}/><path d="M{x + w},{y} L{x + w + d},{y - d}" stroke="{INK}" '
         f'stroke-width="1.3"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{INK}" '
         f'stroke-width="1.3"{da}/>')
    ty = y + 16
    tx, anchor = (x + w - 12, "end") if right else (x + 10, "start")
    if stereo:
        s += text(tx, ty, f"«{stereo}»", 12, anchor, color=MUTED)
        ty += 17
    s += text(tx, ty, title, size, anchor, weight="700")
    return s


def artifact(x, y, w, label, size=12.5):
    """Tao tac: hinh chu nhat co bieu tuong tai lieu goc phai."""
    lines = label.count("\n") + 1
    h = 10 + lines * size * 1.3
    ix, iy = x + w - 16, y + 5
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="{LINE}" stroke-width="1.1"/>'
            f'<path d="M{ix},{iy} h7 l4,4 v9 h-11 z M{ix + 7},{iy} v4 h4" fill="none" stroke="{MUTED}" '
            f'stroke-width="1"/>' + text(x + 8, y + h / 2, label, size, "start")), h
