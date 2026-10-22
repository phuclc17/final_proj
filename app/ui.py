"""He thanh phan giao dien dung chung: mot kieu cho moi trang.
Nguyen tac: nen trang, vien manh xam, bo goc nho, khong bong do, khong vien mau trang tri, khong bieu tuong cam xuc;
trang thai la cham tron nho ve bang CSS kem chu; mau chi dung cho y nghia (canh bao, theo doi, binh thuong, thao tac chinh).
"""
import html

import streamlit as st

INK, MUTED, LINE = "#111827", "#6B7280", "#E5E7EB"
RED, AMBER, GREEN, GRAY, BLUE = "#B42318", "#B54708", "#067647", "#9CA3AF", "#1D4ED8"
LEVEL = {"Cảnh báo": RED, "Theo dõi": AMBER, "Bình thường": GREEN,
         "chặn": RED, "lỗi": RED, "cảnh báo": AMBER, "đạt": GREEN, "chạy": BLUE, "chờ": GRAY, "bỏ qua": GRAY}

CSS = f"""
<style>
.block-container {{max-width: 1320px; padding-top: 2.4rem; padding-bottom: 3rem;}}
h1 {{letter-spacing: -0.015em;}}
h2, h3 {{letter-spacing: -0.01em;}}
[data-testid="stCaptionContainer"] p {{color: {MUTED};}}
[data-testid="stCaptionContainer"] {{opacity: 1;}}
[data-testid="stPageLink-NavLink"] {{padding: 3px 0;}}
[data-testid="stPageLink-NavLink"] p {{color: {BLUE};}}
[data-testid="stMetric"] [data-testid="stMetricLabel"] p {{color: {MUTED}; font-weight: 500;}}
[data-testid="stMetricValue"] {{font-variant-numeric: tabular-nums;}}
[data-baseweb="tag"] {{background-color: #EEF0F3 !important;}}
[data-baseweb="tag"] span {{color: {INK} !important;}}
[data-baseweb="tag"] svg {{fill: {MUTED} !important;}}
.ff-grid {{display: grid; gap: 12px; margin: 4px 0 18px 0;}}
.ff-card {{background: #fff; border: 1px solid {LINE}; border-radius: 8px; padding: 14px 16px; min-width: 0;}}
.ff-card .k {{font-size: 12.5px; color: {MUTED}; font-weight: 500;}}
.ff-card .v {{font-size: 22px; font-weight: 600; color: {INK}; line-height: 1.25; margin-top: 6px;
             font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}}
.ff-card .d {{font-size: 13px; color: {MUTED}; margin-top: 4px; line-height: 1.45;}}
.ff-card .n {{font-size: 11.5px; color: #9CA3AF; font-weight: 500; float: right;}}
.ff-dot {{display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 7px;
          vertical-align: middle; position: relative; top: -1px;}}
.ff-status {{font-size: 13.5px; font-weight: 500; color: #374151; white-space: nowrap;}}
.ff-note {{border: 1px solid {LINE}; border-left: 3px solid var(--c); border-radius: 6px; background: #fff;
          padding: 12px 16px; margin: 6px 0 18px 0;}}
.ff-note .h {{font-weight: 600; color: {INK}; font-size: 15px;}}
.ff-note .b {{color: #4B5563; font-size: 14px; margin-top: 3px; line-height: 1.5;}}
.ff-steps {{display: grid; gap: 8px; margin: 6px 0 4px 0;}}
.ff-step {{border: 1px solid {LINE}; border-radius: 6px; padding: 9px 11px; background: #fff; min-width: 0;}}
.ff-step .t {{font-size: 13px; font-weight: 600; color: {INK}; white-space: nowrap; overflow: hidden;
              text-overflow: ellipsis;}}
.ff-step .s {{font-size: 12.5px; color: {MUTED}; margin-top: 3px; white-space: nowrap; overflow: hidden;
              text-overflow: ellipsis;}}
.ff-table {{width: 100%; border-collapse: collapse; font-size: 14px; margin: 4px 0 14px 0;}}
.ff-table th {{text-align: left; font-weight: 500; color: #4B5563; background: #F9FAFB; padding: 8px 10px;
              border-bottom: 1px solid {LINE};}}
.ff-table td {{padding: 8px 10px; border-bottom: 1px solid #F1F2F4; vertical-align: top; color: {INK};
              overflow-wrap: anywhere;}}
.ff-table td.num {{text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap;}}
.ff-table .ff-status {{white-space: normal;}}
</style>
"""


def setup():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(x):
    return html.escape(str(x))


def header(title, sub=None):
    """Tieu de trang va mot cau mo ta."""
    st.title(title)
    if sub:
        st.caption(sub)


def dot(color):
    return f"<span class='ff-dot' style='background:{color}'></span>"


def status(text, level=None):
    """Chu trang thai kem cham mau; level mac dinh la chinh chu do."""
    return f"<span class='ff-status'>{dot(LEVEL.get(level or text, GRAY))}{esc(text)}</span>"


def note(head, body="", level="Cảnh báo"):
    """Khoi tom tat trung tinh: vach mau ben trai theo muc do, khong to nen."""
    c = LEVEL.get(level, GRAY)
    b = f"<div class='b'>{body}</div>" if body else ""
    st.markdown(f"<div class='ff-note' style='--c:{c}'><div class='h'>{dot(c)}{head}</div>{b}</div>",
                unsafe_allow_html=True)


def cards(items, cols=4):
    """items: [(nhan, gia tri, mo ta, so thu tu hoac None)]."""
    cells = []
    for it in items:
        k, v, d = it[:3]
        n = f"<span class='n'>{esc(it[3])}</span>" if len(it) > 3 and it[3] else ""
        cells.append(f"<div class='ff-card'>{n}<div class='k'>{esc(k)}</div><div class='v'>{esc(v)}</div>"
                     + (f"<div class='d'>{d}</div>" if d else "") + "</div>")
    st.markdown(f"<div class='ff-grid' style='grid-template-columns:repeat({cols},minmax(0,1fr))'>{''.join(cells)}</div>",
                unsafe_allow_html=True)


def table(df, num=(), widths=None):
    """Bang tinh, chu tu xuong dong (dung khi noi dung dai can doc tron ven); num: cot so can le phai;
    widths: ti le do rong cac cot."""
    head = "".join(f"<th>{esc(c)}</th>" for c in df.columns)
    def cell(c, v):
        s = str(v)
        body = s if s.startswith("<span class='ff-status'>") else esc(s)   # chi giu HTML cua nhan trang thai
        return f"<td class='num'>{body}</td>" if c in num else f"<td>{body}</td>"
    rows = "".join("<tr>" + "".join(cell(c, v) for c, v in zip(df.columns, r)) + "</tr>"
                   for r in df.itertuples(index=False))
    cols = ""
    if widths:
        tot = sum(widths)
        cols = "<colgroup>" + "".join(f"<col style='width:{100 * w / tot:.1f}%'>" for w in widths) + "</colgroup>"
    layout = " style='table-layout:fixed'" if widths else ""
    st.markdown(f"<table class='ff-table'{layout}>{cols}<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>",
                unsafe_allow_html=True)
