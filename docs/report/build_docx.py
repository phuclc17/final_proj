"""
Ghep noi dung bao cao (docs/report/*.md, theo thu tu ten file) vao template UEH -> docs/BaoCao_KhoaLuan.docx.
Giu nguyen trang bia cua template; thay toan bo phan con lai.

Cu phap file nguon (moi dong la mot doan van):
  # Tieu de          Heading 1 (chuong / muc phan dau), sang trang moi, co trong muc luc
  ## Tieu de         Heading 2
  ### Tieu de        Heading 3
  #! Tieu de         tieu de KHONG vao muc luc (vd: MUC LUC)
  [[TOC]]  [[LIST_TABLES]]  [[LIST_FIGURES]]
  [[END_FRONT]]      ket thuc phan dau sach (so trang La Ma); phan sau danh so trang tu 1
  - y   /   "  - y"  gach dau dong cap 1 / cap 2
  1. y               danh sach so (cac dong lien tiep la mot danh sach)
  TABLE: Bang 1.1. Ten bang [|| nguon]   (tuy chon dong ke tiep: WIDTHS: 2,3,5) roi cac dong | o | o |; "<br>" trong o = xuong doan
  FIGURE: Hinh 3.1. Ten hinh || mo ta noi dung hinh se chen
  IMAGE: duong/dan.png || Hinh 3.1. Ten hinh || chieu_rong_cm [|| nguon]
                     moi bang/hinh co dong "Nguon: ..." can phai; nguon mac dinh dat bang dong "NGUON: ..." (ap dung cho cac bang, hinh phia sau)
  EQ: cong thuc LaTeX || (2.1)   -> phuong trinh Word (OMML), so hieu can phai; trong doan van: $cong thuc$
  TODO: noi dung     doan nen vang [CAN BO SUNG] - phai xoa het truoc khi nop
  CENTER: / RIGHT: / NOINDENT: / REF: (tai lieu tham khao, thut treo)
  CODE ... ENDCODE   khoi ma / cay thu muc
  PAGEBREAK
  Trong dong: **dam**, *nghieng*, `ma`
Can: lxml, latex2mathml (cong thuc) va MML2OMML.XSL cua Microsoft Office.
Chay: python docs/report/build_docx.py            (ban day du, con TODO)
      python docs/report/build_docx.py --de-cuong (de cuong: nguon docs/de_cuong/*.md -> docs/DeCuong_KhoaLuan.docx)
      python docs/report/build_docx.py --review   (ban cho giang vien xem: bo TODO/khung hinh, them trang tinh trang)
"""
import re
import struct
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "khoaluan_ueh.docx"
OUTPUT = HERE.parent / "BaoCao_KhoaLuan.docx"

PAGE_W, PAGE_H = 11900, 16840
MARGIN = {"top": 1134, "right": 1134, "bottom": 1134, "left": 1701}
TEXT_W = PAGE_W - MARGIN["left"] - MARGIN["right"]
COVER_PARAGRAPHS = 19          # so doan cua trang bia trong template
FOOTER_RID = "rId8"
BULLET_NUM, DECIMAL_ABS = 900, 901
NS_PIC = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
          'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ------------------------------------------------------------------ run & doan van
def run(text, bold=False, italic=False, code=False, size=None, color=None):
    rpr = ""
    if code:
        rpr += '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
    if bold:
        rpr += "<w:b/><w:bCs/>"
    if italic:
        rpr += "<w:i/><w:iCs/>"
    if color:
        rpr += f'<w:color w:val="{color}"/>'
    if size or code:
        sz = size or 22
        rpr += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+?`|\$[^$]+?\$|\*[^*\s][^*]*?\*)")

# ------------------------------------------------------------------ cong thuc: LaTeX -> MathML -> OMML (phuong trinh that cua Word)
MML2OMML = Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL")
_XSLT = []
SPACES = {r"\qquad": "\u2003\u2003", r"\quad": "\u2003", r"\;": "\u2005", r"\,": "\u2009"}
TNR = '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/></w:rPr>'


def omml(tex):
    """Bang chuyen doi cua Word bo qua khoang trang (mspace) -> doi \\quad... thanh ky tu trang trong \\text{};
    so thap phan "0{,}6" bi tach thanh 3 run -> gop lai; chu trong \\text{} dung Times New Roman nhu than bai."""
    from lxml import etree
    import latex2mathml.converter
    if not _XSLT:
        _XSLT.append(etree.XSLT(etree.parse(str(MML2OMML))))
    for k, v in SPACES.items():
        tex = tex.replace(k, r"\text{" + v + "}")
    root = _XSLT[0](etree.fromstring(latex2mathml.converter.convert(tex))).getroot()
    # \sum_i x: bang chuyen doi de than tong (m:e) rong va dat x ra ngoai -> Word chua o trong; dua phan sau vao than tong
    M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    for nary in reversed(list(root.iter(M + "nary"))):
        body = nary.find(M + "e")
        if body is not None and len(body) == 0:
            for sib in list(nary.itersiblings()):
                body.append(sib)
    xml = etree.tostring(root, encoding="unicode")
    xml = re.sub(r' xmlns:\w+="[^"]*"', "", xml)
    xml = re.sub(r"(\d)</m:t></m:r><m:r><m:t>,</m:t></m:r><m:r><m:t>(\d)", r"\1,\2", xml)
    return xml.replace("<m:rPr><m:nor/></m:rPr>", "<m:rPr><m:nor/></m:rPr>" + TNR)


def inline(text, bold=False, italic=False, size=None, code_size=None):
    out = []
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("$") and part.endswith("$") and len(part) > 2:
            out.append(omml(part[1:-1]))
        elif part.startswith("**") and part.endswith("**"):
            out.append(run(part[2:-2], bold=True, italic=italic, size=size))
        elif part.startswith("`") and part.endswith("`"):
            out.append(run(part[1:-1], code=True, bold=bold, size=code_size or (size and size - 2)))
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            out.append(run(part[1:-1], italic=True, bold=bold, size=size))
        else:
            out.append(run(part, bold=bold, italic=italic, size=size))
    return "".join(out)


def para(content, style="Body", num=None, jc=None, ind=None, spacing=None, keep_next=False, sect=None, tabs=None):
    ppr = f'<w:pStyle w:val="{style}"/>'
    if keep_next:
        ppr += "<w:keepNext/>"
    if num:
        ppr += f'<w:numPr><w:ilvl w:val="{num[1]}"/><w:numId w:val="{num[0]}"/></w:numPr>'
    if tabs:
        ppr += "<w:tabs>" + "".join(f'<w:tab w:val="{v}" w:pos="{p}"/>' for v, p in tabs) + "</w:tabs>"
    if spacing:
        ppr += spacing
    if ind:
        ppr += ind
    if jc:
        ppr += f'<w:jc w:val="{jc}"/>'
    if sect:
        ppr += sect
    return f"<w:p><w:pPr>{ppr}</w:pPr>{content}</w:p>"


def field(instr, placeholder, style):
    return (f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
            f'<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> {esc(instr)} </w:instrText></w:r>'
            f'<w:r><w:fldChar w:fldCharType="separate"/></w:r>{run(placeholder, italic=True)}'
            f'<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')


def sect_pr(page_fmt, footer=True, margin=None):
    m = margin or MARGIN
    foot = f'<w:footerReference w:type="default" r:id="{FOOTER_RID}"/>' if footer else ""
    num = f'<w:pgNumType w:fmt="{page_fmt}" w:start="1"/>' if page_fmt else ""
    return (f'<w:sectPr>{foot}<w:pgSz w:w="{PAGE_W}" w:h="{PAGE_H}"/>'
            f'<w:pgMar w:top="{m["top"]}" w:right="{m["right"]}" w:bottom="{m["bottom"]}" w:left="{m["left"]}" '
            f'w:header="567" w:footer="567" w:gutter="0"/>{num}<w:cols w:space="720"/></w:sectPr>')


# ------------------------------------------------------------------ bang
DEFAULT_SOURCE = "Đề xuất của nghiên cứu"


def source_line(src, keep_next=False):
    return para(run("Nguồn: ", italic=True, size=22) + inline(src, italic=True, size=22), style="NguonHinh",
                keep_next=keep_next)


CAPTION = re.compile(r"^((?:Bảng|Hình) [0-9A-Z]+\.\d+\.)\s*(.*)$")
NUMBER = re.compile(r"(?:[\d\s.,%/×≈<>+−\-–—~()]*\d[\d\s.,%/×≈<>+−\-–—~()]*"
                    r"(?: (?:giây|phút|giờ|ngày|tuần|MB|GB|đ|đồng|triệu đ|tỷ đ|nghìn đ|dòng|tệp|lần|đơn|ca|bước))?)|[—–]")


def caption_runs(text):
    """Nhan "Bang 3.1." / "Hinh 3.1." in dam, ten bang/hinh chu thuong (nhu Table 1. / Fig. 1. cua bai bao mau)."""
    m = CAPTION.match(text)
    return run(m.group(1) + " ", bold=True) + inline(m.group(2)) if m else inline(text)


def is_number(text):
    """O chi gom so lieu (0,72; 5/6; 158/158; −17,2%; —) thi can giua cho de so theo cot."""
    return bool(NUMBER.fullmatch(text.strip()))


def table(caption, rows, widths=None, source=None):
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    if widths:
        w = [float(x) for x in widths]
    else:
        w = [max(4.0, min(40.0, max(len(r[c]) for r in rows) ** 0.8)) for c in range(ncol)]
    cols = [int(TEXT_W * x / sum(w)) for x in w]
    cols[-1] += TEXT_W - sum(cols)
    # kieu ba duong ngang cua bai bao khoa hoc: duong dam tren cung va duoi cung, duong mong duoi dong tieu de,
    # khong ke doc; giua cac dong chi co net xam rat mong de de doc o co nhieu dong
    borders = ('<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
               '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
               '<w:left w:val="nil"/><w:right w:val="nil"/><w:insideV w:val="nil"/>'
               '<w:insideH w:val="single" w:sz="2" w:space="0" w:color="BFBFBF"/>')
    xml = [para(caption_runs(caption), style="ChuThichBang", keep_next=True) if caption else "",
           f'<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="{TEXT_W}" w:type="dxa"/>'
           f'<w:jc w:val="center"/><w:tblBorders>{borders}</w:tblBorders><w:tblLayout w:type="fixed"/>'
           f'<w:tblCellMar><w:left w:w="85" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar>'
           f'<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" '
           f'w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>'
           + "".join(f'<w:gridCol w:w="{c}"/>' for c in cols) + "</w:tblGrid>"]
    # cot so lieu (da so o la so) duoc can giua ca cot, ke ca o kem don vi nhu "6 ngay"
    body = rows[1:]
    num_col = [bool(body) and sum(is_number(r[c]) for r in body) >= 0.6 * len(body) for c in range(ncol)]
    for i, r in enumerate(rows):
        header = i == 0
        trpr = "<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>" if header else "<w:trPr><w:cantSplit/></w:trPr>"
        cells = []
        for c, text in enumerate(r):
            shd = '<w:tcBorders><w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/></w:tcBorders>' if header else ""
            jc = '<w:jc w:val="center"/>' if header or num_col[c] or is_number(text) or text.strip() == "x" else ""
            # "<br>" trong o: tach thanh nhieu doan (vd cac buoc cua luong su kien trong bang dac ta ca su dung)
            paras = "".join(f'<w:p><w:pPr><w:pStyle w:val="TableText"/>{jc}</w:pPr>'
                            f'{inline(part.strip(), bold=header, code_size=18)}</w:p>'
                            for part in text.split("<br>"))
            cells.append(f'<w:tc><w:tcPr><w:tcW w:w="{cols[c]}" w:type="dxa"/>{shd}<w:vAlign w:val="center"/></w:tcPr>'
                         f'{paras}</w:tc>')
        xml.append(f"<w:tr>{trpr}{''.join(cells)}</w:tr>")
    xml.append("</w:tbl>")
    if caption:
        xml.append(source_line(source or DEFAULT_SOURCE))
    xml.append(para("", style="AfterTable"))
    return "".join(xml)


def equation(tex, number):
    """Phuong trinh dong rieng, danh so ben phai: bang 3 cot khong vien (le trai | phuong trinh dang hien thi | so hieu).
    oMathPara giu phan so co kich thuoc day du; oMath nam giua dong van ban se bi thu nho nhu cong thuc trong dong."""
    side = 1000
    cols = [side, TEXT_W - 2 * side, side]
    nob = "".join(f'<w:{b} w:val="nil"/>' for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
    cell = lambda w, body, jc: (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
                                f'<w:p><w:pPr><w:pStyle w:val="Equation"/><w:jc w:val="{jc}"/></w:pPr>{body}</w:p></w:tc>')
    math = f'<m:oMathPara><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr>{omml(tex)}</m:oMathPara>'
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>{nob}</w:tblBorders>'
            f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/>'
            f'</w:tblCellMar><w:tblLook w:val="0000"/></w:tblPr><w:tblGrid>' + "".join(f'<w:gridCol w:w="{c}"/>' for c in cols)
            + '</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>'
            + cell(cols[0], "", "left") + cell(cols[1], math, "center") + cell(cols[2], run(number), "right")
            + "</w:tr></w:tbl>"
            # doan rat thap sau bang: hai phuong trinh lien tiep khong bi Word gop thanh mot bang
            + para("", spacing='<w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'))


# ------------------------------------------------------------------ hinh
class Images:
    def __init__(self):
        self.items = []  # (rid, zip_name, data)

    def add(self, path):
        data = Path(path).read_bytes()
        ext = Path(path).suffix.lower().lstrip(".")
        idx = len(self.items) + 1
        rid, name = f"rIdImg{idx}", f"media/report_img{idx}.{ext}"
        self.items.append((rid, name, data))
        return rid, data


def png_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    raise ValueError("Chi ho tro PNG cho IMAGE:")


def image(path, caption, width_cm, images, uid, source=None):
    rid, data = images.add(path)
    w, h = png_size(data)
    cx = int(float(width_cm) * 360000)
    cy = int(cx * h / w)
    drawing = (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
               f'<wp:docPr id="{uid}" name="Hinh {uid}"/><wp:cNvGraphicFramePr>'
               f'<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
               f'</wp:cNvGraphicFramePr><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
               f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic {NS_PIC}>'
               f'<pic:nvPicPr><pic:cNvPr id="{uid}" name="hinh{uid}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
               f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
               f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
               f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
               f'</wp:inline></w:drawing></w:r>')
    return (para(drawing, style="FigureBox", keep_next=True) + source_line(source or DEFAULT_SOURCE, keep_next=True)
            + para(caption_runs(caption), style="ChuThichHinh"))


# ------------------------------------------------------------------ chuyen markup -> XML
def convert(lines, images, numbering):
    out, i, uid = [], 0, 5000
    src_default = DEFAULT_SOURCE  # doi bang dong "NGUON: ..." cho cac bang, hinh phia sau
    while i < len(lines):
        line = lines[i].rstrip("\n")
        s = line.strip()
        i += 1
        if not s or s.startswith("<!--"):
            continue
        if s.startswith("NGUON:"):
            src_default = s[6:].strip()
        elif s == "PAGEBREAK":
            out.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        elif s == "[[TOC]]":
            out.append(field('TOC \\o "1-3" \\h \\z \\u', "Mở file bằng Word, nhấn chuột phải vào đây → Update Field để cập nhật mục lục.", "TOC1"))
        elif s == "[[LIST_TABLES]]":
            out.append(field('TOC \\h \\z \\t "ChuThichBang,1"', "Cập nhật trường để hiện danh mục bảng.", "TOC1"))
        elif s == "[[LIST_FIGURES]]":
            out.append(field('TOC \\h \\z \\t "ChuThichHinh,1"', "Cập nhật trường để hiện danh mục hình.", "TOC1"))
        elif s == "[[END_FRONT]]":
            out.append(para(run(" ", size=2), style="Body", sect=sect_pr("lowerRoman")))
        elif s.startswith("#! "):
            out.append(para(inline(s[3:]), style="FrontTitle"))
        elif s.startswith("### "):
            out.append(para(inline(s[4:]), style="Heading3"))
        elif s.startswith("## "):
            out.append(para(inline(s[3:]), style="Heading2"))
        elif s.startswith("# "):
            out.append(para(inline(s[2:]), style="Heading1"))
        elif s.startswith("TABLE:"):
            caption, _, source = s[6:].partition("||")
            caption, source, widths, rows = caption.strip(), source.strip() or None, None, []
            while i < len(lines) and lines[i].strip().startswith("WIDTHS:"):
                widths = lines[i].strip()[7:].split(",")
                i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = lines[i].strip().strip("|").split("|")
                if not all(re.fullmatch(r"\s*:?-{2,}:?\s*", c) for c in cells):
                    rows.append([c.strip() for c in cells])
                i += 1
            out.append(table(caption, rows, widths, source or src_default))
        elif s.startswith("FIGURE:"):
            caption, _, desc = s[7:].partition("||")
            box = run("[HÌNH SẼ CHÈN] ", bold=True, color="7F7F7F", size=22) + run(desc.strip(), italic=True, color="7F7F7F", size=22)
            out.append(para(box, style="FigurePlaceholder", keep_next=True))
            out.append(para(caption_runs(caption.strip()), style="ChuThichHinh"))
        elif s.startswith("IMAGE:"):
            path, caption, width, *source = [x.strip() for x in s[6:].split("||")]
            uid += 1
            out.append(image(HERE / path, caption, width, images, uid, source[0] if source else src_default))
        elif s.startswith("EQ:"):
            formula, _, number = s[3:].partition("||")
            out.append(equation(formula.strip(), number.strip()))
        elif s.startswith("TODO:"):
            out.append(para(run("[CẦN BỔ SUNG] ", bold=True) + inline(s[5:].strip()), style="TodoNote"))
        elif s.startswith("CENTER:"):
            out.append(para(inline(s[7:].strip()), style="BodyNoIndent", jc="center"))
        elif s.startswith("RIGHT:"):
            out.append(para(inline(s[6:].strip()), style="BodyNoIndent", jc="right"))
        elif s.startswith("NOINDENT:"):
            out.append(para(inline(s[9:].strip()), style="BodyNoIndent"))
        elif s.startswith("REF:"):
            out.append(para(inline(s[4:].strip()), style="Reference"))
        elif s == "CODE":
            while i < len(lines) and lines[i].strip() != "ENDCODE":
                out.append(para(run(lines[i].rstrip("\n") or " ", code=True, size=18), style="Code"))
                i += 1
            i += 1
        elif re.match(r"^\s*- ", line):
            level = 1 if line.startswith("  ") else 0
            out.append(para(inline(s[2:]), style="ListBody", num=(BULLET_NUM, level)))
        elif re.match(r"^\d+\. ", s):
            num_id = numbering.new_decimal()
            while True:
                out.append(para(inline(re.sub(r"^\d+\. ", "", s)), style="ListBody", num=(num_id, 0)))
                if i < len(lines) and re.match(r"^\d+\. ", lines[i].strip()):
                    s = lines[i].strip()
                    i += 1
                else:
                    break
        else:
            out.append(para(inline(s)))
    return "".join(out)


class Numbering:
    def __init__(self):
        self.decimal_ids = []

    def new_decimal(self):
        nid = 910 + len(self.decimal_ids)
        self.decimal_ids.append(nid)
        return nid

    def patch(self, xml):
        lvl = lambda ilvl, fmt, text, left: (
            f'<w:lvl w:ilvl="{ilvl}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/><w:lvlText w:val="{text}"/>'
            f'<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="{left}" w:hanging="284"/></w:pPr>'
            f'<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:hint="default"/></w:rPr></w:lvl>')
        abstract = (f'<w:abstractNum w:abstractNumId="{BULLET_NUM}"><w:multiLevelType w:val="hybridMultilevel"/>'
                    f'{lvl(0, "bullet", "–", 851)}{lvl(1, "bullet", "+", 1418)}</w:abstractNum>'
                    f'<w:abstractNum w:abstractNumId="{DECIMAL_ABS}"><w:multiLevelType w:val="hybridMultilevel"/>'
                    f'{lvl(0, "decimal", "%1.", 851)}{lvl(1, "lowerLetter", "%2)", 1418)}</w:abstractNum>')
        nums = f'<w:num w:numId="{BULLET_NUM}"><w:abstractNumId w:val="{BULLET_NUM}"/></w:num>'
        for nid in self.decimal_ids:
            nums += (f'<w:num w:numId="{nid}"><w:abstractNumId w:val="{DECIMAL_ABS}"/>'
                     f'<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>')
        first_num = xml.find("<w:num ")
        xml = xml[:first_num] + abstract + xml[first_num:]
        last_num_end = xml.rindex("</w:num>") + len("</w:num>")  # w:num phai dung truoc numIdMacAtCleanup
        return xml[:last_num_end] + nums + xml[last_num_end:]


# ------------------------------------------------------------------ style
def style(sid, name, ppr, rpr, based="Normal", nxt="Body"):
    return (f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="{sid}"><w:name w:val="{name}"/>'
            f'<w:basedOn w:val="{based}"/><w:next w:val="{nxt}"/><w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')


SZ = lambda n: f'<w:sz w:val="{n}"/><w:szCs w:val="{n}"/>'
BOX = ('<w:pBdr>' + "".join(f'<w:{b} w:val="single" w:sz="4" w:space="4" w:color="A6A6A6"/>' for b in ("top", "left", "bottom", "right"))
       + '</w:pBdr>')

STYLES = {
    "Heading1": ('<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>'
                 '<w:next w:val="Body"/><w:uiPriority w:val="9"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/>'
                 '<w:pageBreakBefore/><w:spacing w:before="0" w:after="360" w:line="360" w:lineRule="auto"/>'
                 f'<w:jc w:val="center"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:bCs/>{SZ(28)}</w:rPr></w:style>'),
    "Heading2": ('<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>'
                 '<w:next w:val="Body"/><w:uiPriority w:val="9"/><w:unhideWhenUsed/><w:qFormat/><w:pPr><w:keepNext/>'
                 '<w:keepLines/><w:spacing w:before="240" w:after="120" w:line="360" w:lineRule="auto"/>'
                 f'<w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:bCs/>{SZ(26)}</w:rPr></w:style>'),
    "Heading3": ('<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/>'
                 '<w:next w:val="Body"/><w:uiPriority w:val="9"/><w:unhideWhenUsed/><w:qFormat/><w:pPr><w:keepNext/>'
                 '<w:keepLines/><w:spacing w:before="120" w:after="120" w:line="360" w:lineRule="auto"/>'
                 f'<w:outlineLvl w:val="2"/></w:pPr><w:rPr><w:b/><w:bCs/><w:i/><w:iCs/>{SZ(26)}</w:rPr></w:style>'),
}
NEW_STYLES = [
    style("Body", "Than van ban", '<w:spacing w:before="0" w:after="120" w:line="360" w:lineRule="auto"/>'
          '<w:ind w:firstLine="567"/><w:jc w:val="both"/>', SZ(26)),
    style("BodyNoIndent", "Than van ban khong thut", '<w:spacing w:before="0" w:after="120" w:line="360" w:lineRule="auto"/>'
          '<w:jc w:val="both"/>', SZ(26)),
    style("ListBody", "Danh sach", '<w:spacing w:before="0" w:after="60" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/>', SZ(26)),
    style("FrontTitle", "Tieu de phan dau", '<w:keepNext/><w:pageBreakBefore/><w:spacing w:before="0" w:after="360" '
          'w:line="360" w:lineRule="auto"/><w:jc w:val="center"/>', "<w:b/><w:bCs/>" + SZ(28)),
    style("ChuThichBang", "ChuThichBang", '<w:keepNext/><w:spacing w:before="120" w:after="80" w:line="300" '
          'w:lineRule="auto"/><w:jc w:val="center"/>', SZ(24)),
    style("ChuThichHinh", "ChuThichHinh", '<w:spacing w:before="60" w:after="240" w:line="300" w:lineRule="auto"/>'
          '<w:jc w:val="center"/>', SZ(24)),
    style("NguonHinh", "Nguon hinh bang", '<w:spacing w:before="40" w:after="60" w:line="264" w:lineRule="auto"/>'
          '<w:jc w:val="right"/>', SZ(22)),
    style("TableText", "Chu trong bang", '<w:spacing w:before="20" w:after="20" w:line="264" w:lineRule="auto"/>', SZ(24)),
    style("AfterTable", "Sau bang", '<w:spacing w:before="0" w:after="120" w:line="240" w:lineRule="auto"/>', SZ(12)),
    style("FigureBox", "Khung hinh", '<w:keepNext/><w:spacing w:before="120" w:after="60"/><w:jc w:val="center"/>', SZ(26)),
    style("FigurePlaceholder", "Cho chen hinh", f'<w:keepNext/>{BOX}<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>'
          '<w:spacing w:before="240" w:after="60" w:line="300" w:lineRule="auto"/><w:ind w:left="567" w:right="567"/>'
          '<w:jc w:val="center"/>', SZ(22)),
    style("Equation", "Cong thuc", '<w:spacing w:before="120" w:after="120" w:line="300" w:lineRule="auto"/>', SZ(26)),
    style("TodoNote", "Ghi chu can bo sung", '<w:pBdr><w:left w:val="single" w:sz="18" w:space="4" w:color="BF8F00"/></w:pBdr>'
          '<w:shd w:val="clear" w:color="auto" w:fill="FFF2CC"/><w:spacing w:before="60" w:after="120" w:line="300" '
          'w:lineRule="auto"/><w:jc w:val="both"/>', '<w:i/><w:iCs/><w:color w:val="7F6000"/>' + SZ(24)),
    style("Reference", "Tai lieu tham khao", '<w:spacing w:before="0" w:after="120" w:line="300" w:lineRule="auto"/>'
          '<w:ind w:left="567" w:hanging="567"/><w:jc w:val="left"/>', SZ(26)),
    style("Code", "Ma nguon", '<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/><w:spacing w:before="0" w:after="0" '
          'w:line="240" w:lineRule="auto"/><w:ind w:left="284" w:right="284"/>',
          '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>' + SZ(18)),
]

FOOTER = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
          '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
          '<w:p><w:pPr><w:pStyle w:val="Footer"/><w:jc w:val="center"/></w:pPr>'
          '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
          '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r>'
          '</w:p></w:ftr>')


def patch_styles(xml):
    for sid, new in STYLES.items():
        xml, n = re.subn(rf'<w:style w:type="paragraph" w:styleId="{sid}">.*?</w:style>', lambda _: new, xml, flags=re.S)
        if n != 1:
            raise RuntimeError(f"Khong tim thay style {sid} trong template")
    # template co style bang "a" khong co w:name -> Word bao "Styles 1" va bat sua tep khi mo; dat ten cho moi style thieu ten
    xml = re.sub(r'(<w:style\b[^>]*w:styleId="([^"]+)"[^>]*>)(?!<w:name )', r'\1<w:name w:val="Style \2"/>', xml)
    for sid in ("TOC1", "TOC2", "TOC3"):  # muc luc: giu style template, bo dam o cap 3
        xml = re.sub(rf'(<w:style [^>]*w:styleId="{sid}">.*?)<w:b/>(.*?</w:style>)', r"\1\2", xml, flags=re.S)
    return xml.replace("</w:styles>", "".join(NEW_STYLES) + "</w:styles>")


# ------------------------------------------------------------------ tach phan tu cap 1 trong <w:body>
TAG = re.compile(r"<(/?)([A-Za-z0-9_:]+)[^>]*?(/?)>")


def body_children(xml):
    start = xml.index("<w:body>") + len("<w:body>")
    end = xml.rindex("</w:body>")
    children, depth, cur = [], 0, None
    for m in TAG.finditer(xml, start, end):
        closing, selfclosing = m.group(1) == "/", m.group(3) == "/"
        if not closing and depth == 0:
            cur = m.start()
        if closing:
            depth -= 1
        elif not selfclosing:
            depth += 1
        if depth == 0 and cur is not None:
            children.append(xml[cur:m.end()])
            cur = None
    return xml[:start], children


def cover(children):
    paras = [c for c in children if c.startswith("<w:p ") or c.startswith("<w:p>")][:COVER_PARAGRAPHS]
    last = paras[-1]
    ppr_end = last.index("</w:pPr>")
    runs_start = ppr_end + len("</w:pPr>")
    first_rpr = re.search(r"<w:r [^>]*>(<w:rPr>.*?</w:rPr>)", last).group(1)
    date = f'<w:r>{first_rpr}<w:t xml:space="preserve">TP. Hồ Chí Minh, tháng 10 năm 2026</w:t></w:r>'
    original_margin = {"top": 1440, "right": 1440, "bottom": 1440, "left": 1440}
    last = last[:ppr_end] + sect_pr(None, footer=False, margin=original_margin) + "</w:pPr>" + date + "</w:p>"
    return "".join(paras[:-1]) + last


HEADING = re.compile(r"^(#{1,3}) ")


def review_filter(lines):
    """Ban review cho giang vien: bo TODO, khung cho hinh, bang khung cho so lieu; muc rong ghi 'dang thuc hien'."""
    kept, i = [], 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith(("TODO:", "FIGURE:")) or s in ("# DANH MỤC HÌNH", "[[LIST_FIGURES]]"):
            i += 1
            continue
        if s.startswith("TABLE:") and "chờ số liệu" in s:
            i += 1
            while i < len(lines) and lines[i].strip().startswith(("WIDTHS:", "|")):
                i += 1
            continue
        kept.append(lines[i])
        i += 1
    out = []
    for k, line in enumerate(kept):
        out.append(line)
        m = HEADING.match(line.strip())
        if not m:
            continue
        level = len(m.group(1))
        nxt = next((x.strip() for x in kept[k + 1:] if x.strip()), "")
        m2 = HEADING.match(nxt)
        if not nxt or nxt == "[[END_FRONT]]" or (m2 and len(m2.group(1)) <= level):
            out += ["", "*Phần này đang được thực hiện.*"]
    return out


def build(review=False, out=None, de_cuong=False):
    md_files = sorted((HERE.parent / "de_cuong").glob("*.md")) if de_cuong else sorted(HERE.glob("*.md"))
    lines = []
    if review:
        lines += (HERE / "review" / "tinh_trang.md").read_text(encoding="utf-8").splitlines() + [""]
    for f in md_files:
        lines += f.read_text(encoding="utf-8").splitlines() + [""]
    if review:
        lines = review_filter(lines)
    output = OUTPUT.with_name("BaoCao_KhoaLuan_BanReview.docx") if review else OUTPUT
    if de_cuong:
        output = OUTPUT.with_name("DeCuong_KhoaLuan.docx")
    if out:  # ghi ra noi khac (vd. khi file dich dang mo trong Word)
        output = Path(out)
    images, numbering = Images(), Numbering()
    body_xml = convert(lines, images, numbering)

    zin = zipfile.ZipFile(TEMPLATE)
    doc = zin.read("word/document.xml").decode("utf-8")
    prefix, children = body_children(doc)
    cover_xml = cover(children)
    if de_cuong:
        assert ">KHÓA LUẬN TỐT NGHIỆP<" in cover_xml, "khong tim thay dong tieu de tren bia template"
        cover_xml = cover_xml.replace(">KHÓA LUẬN TỐT NGHIỆP<", ">ĐỀ CƯƠNG KHÓA LUẬN TỐT NGHIỆP<")
    new_doc = prefix + cover_xml + body_xml + sect_pr("decimal") + "</w:body></w:document>"

    rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
    rels = rels.replace("</Relationships>", "".join(
        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{name}"/>'
        for rid, name, _ in images.items) + "</Relationships>")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = new_doc.encode("utf-8")
            elif item.filename == "word/styles.xml":
                data = patch_styles(data.decode("utf-8")).encode("utf-8")
            elif item.filename == "word/numbering.xml":
                data = numbering.patch(data.decode("utf-8")).encode("utf-8")
            elif item.filename == "word/footer1.xml":
                data = FOOTER.encode("utf-8")
            elif item.filename == "word/_rels/document.xml.rels":
                data = rels.encode("utf-8")
            elif item.filename == "docProps/core.xml":
                data = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>Khoa luan tot nghiep</dc:title>", data.decode("utf-8")).encode("utf-8")
            zout.writestr(item, data)
        for _, name, data in images.items:
            zout.writestr(f"word/{name}", data)
    todo = sum(1 for l in lines if l.strip().startswith("TODO:"))
    print(f"Da tao {output.name}: {len(md_files)} file nguon, {len(lines)} dong, {len(images.items)} hinh, {todo} muc TODO")


if __name__ == "__main__":
    args = sys.argv[1:]
    build(review="--review" in args, out=args[args.index("--out") + 1] if "--out" in args else None,
          de_cuong="--de-cuong" in args)
    sys.exit(0)
