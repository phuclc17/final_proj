"""Van hanh hang ngay: he thong nguon xuat tep -> pipeline tu phat hien tep moi va chay tu nap toi canh bao.
Trang nay luon doc tap Van hanh thu (tap duy nhat nhan du lieu moi), khong phu thuoc tap dang chon o thanh ben."""
import re
import time

import pandas as pd
import streamlit as st

import airflow_client as af
import duckdb

import ui
from common import DEMO, db_path, vn

PROFILE = "live"
STEP_LABEL = {"extract": "Kéo dữ liệu qua API", "check": "Phát hiện tệp mới", "ingest": "Nạp Bronze", "quality": "Kiểm tra đầu vào",
              "dbt": "Silver, Gold, kiểm thử", "detect": "Quét cảnh báo", "publish": "Đưa sang kho phục vụ"}
SYSTEM_LABEL = {"pos": "POS", "app": "App", "grab": "GrabFood", "shopee": "ShopeeFood", "warehouse": "Sổ nhập kho",
                "stock": "Phiếu kiểm kê", "timekeeping": "Chấm công", "weather": "Thời tiết", "master": "Danh mục"}
# trang thai task cua Airflow -> (chu, mau)
STATE = {"success": ("Xong", ui.GREEN), "failed": ("Lỗi", ui.RED), "running": ("Đang chạy", ui.BLUE),
         "queued": ("Chờ", ui.GRAY), "scheduled": ("Chờ", ui.GRAY), "up_for_reschedule": ("Chờ", ui.GRAY),
         "up_for_retry": ("Thử lại", ui.AMBER), "upstream_failed": ("Dừng", ui.RED), "skipped": ("Bỏ qua", ui.GRAY),
         "warn": ("Cảnh báo", ui.AMBER), None: ("Chưa chạy", ui.GRAY)}
OPS_STATE = {"ok": "success", "warn": "warn", "failed": "failed"}

ui.header("Vận hành hằng ngày", "Dữ liệu mới đến từ các hệ thống nguồn, đường ống tự kéo qua API, nạp, kiểm tra, biến đổi "
                                "và quét cảnh báo. Trang này luôn dùng môi trường Vận hành.")


def query(_profile, sql):
    """Doc chi doc; kho dang bi pipeline ghi thi tra None (trang van tu cap nhat, khong dung lai)."""
    try:
        with duckdb.connect(str(db_path(PROFILE)), read_only=True) as con:
            return con.sql(sql).df()
    except (duckdb.IOException, duckdb.CatalogException):
        return None


def pretty(step, note):
    """Ghi chu ky thuat cua tung buoc -> cau tieng Viet cho nguoi xem."""
    note = str(note or "")
    if step == "check" and ":" in note:
        n, rest = note.split(":", 1)
        items = ", ".join(f"{SYSTEM_LABEL.get(k, k)} {v}" for k, v in re.findall(r"([a-z]+) (\d+)", rest))
        return f"{n.split()[0]} tệp mới: {items}"
    if step == "ingest" and (m := re.search(r"(\d+) file moi, (\d+) dong moi, (\d+) file loi", note)):
        return f"{vn(int(m[1]))} tệp, {vn(int(m[2]))} dòng mới, {m[3]} tệp lỗi"
    if step == "dbt" and (m := re.search(r"PASS=(\d+).*ERROR=(\d+).*TOTAL=(\d+)", note)):
        return f"{m[1]}/{m[3]} bước đạt, {m[2]} lỗi"
    if step == "detect" and (m := re.match(r"tuan (\S+): (\d+) canh bao;?\s*(.*)", note)):
        extra = "; ".join(x.replace(".", ",") for x in m[3].split("; ") if x)
        return f"Tuần {m[1]}: {m[2]} cảnh báo" + (f": {extra}" if extra else "")
    if step == "publish" and (m := re.search(r"(\d+) bang, ([\d.]+) dong", note)):
        return f"{m[1]} bảng, {m[2]} dòng sang PostgreSQL, đối soát số dòng khớp"
    return note


def local(t):
    return pd.Timestamp(t).tz_convert("Asia/Ho_Chi_Minh").strftime("%d/%m %H:%M:%S") if t else "—"


def data_until():
    d = query(PROFILE, "select max(date_day) as d, count(*) as n from gold.fact_order")
    return (pd.Timestamp(d.d.iloc[0]), int(d.n.iloc[0])) if d is not None and len(d) else (None, 0)


def flow(src_run, src_tasks, pipe_run, pipe_tasks):
    """Dai the: He thong nguon -> 6 buoc pipeline, moi o co trang thai cua luot gan nhat."""
    def box(title, state, sub=""):
        text, color = STATE.get(state, STATE[None])
        return (f"<div class='ff-step'><div class='t'>{title}</div>"
                f"<div class='s'>{ui.dot(color)}{text}{' · ' + sub if sub else ''}</div></div>")
    exp = src_tasks.get("xuat_tep", {})
    parts = [box("Hệ thống nguồn", exp.get("state") if src_run else None,
                 local(exp.get("end_date") or exp.get("start_date")) if src_run and exp.get("start_date") else "")]
    for s in af.PIPELINE_STEPS:
        t = pipe_tasks.get(s, {})
        parts.append(box(STEP_LABEL[s], t.get("state") if pipe_run else None,
                         f"{t['duration']:.0f} giây" if t.get("duration") else ""))
    parts = [x.replace("<div class='t'>", f"<div class='t'>{i}. ", 1) for i, x in enumerate(parts, 1)]
    st.markdown("<div class='ff-steps' style='grid-template-columns:repeat(4,minmax(0,1fr))'>"
                + "".join(parts) + "</div>", unsafe_allow_html=True)
    if pipe_run:
        how = {"dataset_triggered": "khởi động khi có dữ liệu mới",
               "scheduled": "lượt kiểm tra định kỳ mỗi giờ", "manual": "chạy tay"}.get(pipe_run["run_type"], "")
        st.caption(f"Lượt đường ống gần nhất có xử lý dữ liệu bắt đầu {local(pipe_run.get('start_date'))}, {how}.")


def from_warehouse(pipe_run):
    """Kho la nguon su that cua lan xu ly gan nhat. Neu luot Airflow moi nhat khong co trong nhat ky kho (moi truong
    vua duoc khoi phuc ve diem demo, nen du lieu cua luot do da bi go), dung nhat ky kho de cac o khop voi bang ben duoi."""
    log = query(PROFILE, "select * from ops.pipeline_runs where run_id = (select run_id from ops.pipeline_runs "
                         "order by finished_at desc limit 1)")
    if log is None or log.empty or (pipe_run and pipe_run["dag_run_id"] in set(log.run_id)):
        return None
    start = pd.Timestamp(log.finished_at.min()) - pd.Timedelta(seconds=float(log.seconds.iloc[0]))
    run = {"dag_run_id": log.run_id.iloc[0], "run_type": log.run_id.iloc[0].split("__")[0],
           "start_date": start.tz_localize("Asia/Ho_Chi_Minh").isoformat()}
    return run, {r.step: {"state": OPS_STATE.get(r.status, r.status), "duration": r.seconds} for r in log.itertuples()}


def is_busy():
    """Mot dinh nghia duy nhat: co luot nao cua 2 DAG dang chay/cho, hoac vua bam nut chua qua 60 giay
    (khoang giao giua luc he thong nguon xong va pipeline bat dau)."""
    return af.busy() or time.time() < st.session_state.get("poll_until", 0)


def panel(busy_now):
    try:
        src_run = (af.runs(af.SOURCE, 1) or [None])[0]
        src_tasks = af.tasks(af.SOURCE, src_run["dag_run_id"]) if src_run else {}
        newest = (af.runs(af.PIPELINE, 1) or [None])[0]
        if newest and newest["state"] in ("running", "queued"):
            pipe_run, pipe_tasks = newest, af.tasks(af.PIPELINE, newest["dag_run_id"])
        else:
            pipe_run, pipe_tasks = af.last_processing_run()
            synced = from_warehouse(pipe_run)
            if synced:      # luot cua he thong nguon di kem cung da bi go: chi con biet la da xong
                pipe_run, pipe_tasks = synced
                src_tasks = {"xuat_tep": {"state": "success"}}
    except Exception:
        st.caption("Airflow chưa chạy. Bật bằng `docker compose up -d` rồi tải lại trang.")
        return
    flow(src_run, src_tasks, pipe_run, pipe_tasks)
    d, n = data_until()
    c1, c2, c3 = st.columns(3)
    c1.metric("Dữ liệu đến ngày", f"{d:%d/%m/%Y}" if d is not None else "Đang ghi", border=True)
    c2.metric("Số đơn trong kho", vn(n) if d is not None else "—", border=True)
    c3.metric("Trạng thái", "Đang xử lý" if busy_now else "Sẵn sàng", border=True)


busy = is_busy()


@st.fragment(run_every=3 if busy else None)
def live():
    now = is_busy()
    panel(now)
    if busy and not now:      # vua xu ly xong: chay lai ca trang de cap nhat ket qua, mo lai nut bam
        st.rerun()


live()

# ---------------------------------------------------------------- dieu khien
st.subheader("Nhận dữ liệu ngày mới")
c1, c2, c3 = st.columns([1.3, 1.6, 3])
days = c1.selectbox("Số ngày", [1, 7], index=1, format_func=lambda x: f"{x} ngày", label_visibility="collapsed")
if c2.button("Gửi dữ liệu ngày mới", type="primary", disabled=busy):
    try:
        af.trigger_source(days)
        st.session_state.poll_until = time.time() + 60
        st.toast(f"Hệ thống nguồn đang ghi dữ liệu của {days} ngày mới.")
        st.rerun()
    except Exception as e:  # Airflow tu choi hoac chua chay
        st.error(f"Không gửi được lệnh: {e}")
c3.caption("Các hệ thống nguồn ghi dữ liệu của những ngày kinh doanh kế tiếp; trong khóa luận, hệ thống nguồn do bộ mô "
           "phỏng đóng vai. " + ("Trên bản trình diễn, việc này chỉ chạy khi bấm nút; đường ống tự xử lý sau đó khoảng "
                                 "ba đến năm phút." if DEMO else "Bình thường việc này diễn ra lúc 23:00 mỗi ngày."))

# ---------------------------------------------------------------- ket qua luot xu ly gan nhat
log = query(PROFILE, "select * from ops.pipeline_runs order by finished_at")
if log is not None and not log.empty:
    rid = log.run_id.iloc[-1]
    last = log[log.run_id == rid].set_index("step")
    st.subheader("Lượt xử lý gần nhất")

    def note(step):
        return str(last.note.get(step, "")) if step in last.index else ""
    rows = [{"Bước": STEP_LABEL.get(s, s), "Trạng thái": {"ok": "Đạt", "warn": "Cảnh báo"}.get(last.status.get(s), "Lỗi"),
             "Thời gian, giây": round(float(last.seconds.get(s, 0))), "Kết quả": pretty(s, note(s))}
            for s in af.PIPELINE_STEPS if s in last.index]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    alerts = query(PROFILE, """select week_start, branch_id, branch_name, cause, cause_name, score, gap_vs_expected
                               from ops.alerts where level = 'Cảnh báo'
                                 and week_start = (select max(week_start) from ops.alerts) order by score desc""")
    wk = query(PROFILE, "select max(week_start) as w from ops.alerts")
    if wk is not None and len(wk) and pd.notna(wk.w.iloc[0]):
        w = pd.Timestamp(wk.w.iloc[0])
        st.subheader(f"Cảnh báo tuần {w:%d/%m} – {w + pd.Timedelta(days=6):%d/%m/%Y}")
        st.caption("Tuần mới nhất đã đủ bảy ngày. Tuần đang dở được đánh giá khi kết thúc.")
        if alerts is None or alerts.empty:
            st.caption("Không có cảnh báo trong tuần này.")
        for r in (alerts.itertuples() if alerts is not None else []):
            a, b = st.columns([6, 1], vertical_alignment="center")
            with a:
                ui.note(f"CN{r.branch_id} · {r.branch_name} · {r.cause_name}",
                        f"Điểm {vn(r.score, 1)}. Doanh thu so với kỳ vọng {vn(r.gap_vs_expected)} đ.")
            if b.button("Truy vết", key=f"tv_{r.branch_id}_{r.cause}", width="stretch"):
                st.session_state.profile_next = "Vận hành"
                st.session_state.trace_branch = int(r.branch_id)
                st.session_state.trace_week = pd.Timestamp(r.week_start)
                st.switch_page("views/trace.py")

    # xem ngay vua sinh: su that cua the gioi mo phong canh nhung gi cac he thong ghi lai
    newest, _ = data_until()
    if newest is not None:
        b0 = int(alerts.branch_id.iloc[0]) if alerts is not None and len(alerts) else 1
        a, b = st.columns([5, 1.4], vertical_alignment="center")
        a.caption(f"Đối chiếu ngày {newest:%d/%m/%Y} với sự thật của bộ mô phỏng ở nhóm Kiểm chứng.")
        if b.button("Mở bộ mô phỏng"):
            st.session_state.profile_next = "Vận hành"
            st.session_state.sim_goto = ("live", b0, newest)
            st.switch_page("views/simulator.py")

    with st.expander("Nhật ký các lượt xử lý"):
        hist = log.groupby("run_id").agg(ket_thuc=("finished_at", "max"), giay=("seconds", "sum"),
                                         trang_thai=("status", lambda x: "Đạt" if (x == "ok").all() else "Cảnh báo" if x.isin(["ok", "warn"]).all() else "Lỗi"),
                                         buoc=("step", "count")).sort_values("ket_thuc", ascending=False).reset_index()
        st.dataframe(pd.DataFrame({"Lượt": hist.run_id, "Kết thúc": hist.ket_thuc.dt.strftime("%d/%m/%Y %H:%M"),
                                   "Số bước": hist.buoc, "Thời gian, giây": hist.giay.round(0),
                                   "Trạng thái": hist.trang_thai}), hide_index=True, width="stretch")

with st.expander("Lịch chạy"):
    try:
        for d, label in ((af.SOURCE, "Hệ thống nguồn: 23:00 mỗi ngày"),
                         (af.PIPELINE, "Đường ống: khi có dữ liệu mới, kiểm tra thêm mỗi giờ")):
            info = af.dag(d)
            a, b = st.columns([4, 1], vertical_alignment="center")
            a.markdown(f"{label} · {'Tạm dừng' if info['is_paused'] else 'Đang bật'}")
            if not DEMO and b.button("Bật" if info["is_paused"] else "Tạm dừng", key=f"p_{d}"):
                af.set_paused(d, not info["is_paused"])
                st.rerun()
        st.link_button("Mở Airflow", af.PUBLIC_URL)
    except Exception:
        st.caption("Airflow chưa chạy.")
