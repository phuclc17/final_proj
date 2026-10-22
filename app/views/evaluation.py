"""Danh gia bo phat hien: quy trinh, so sanh voi doi chung, ket qua theo su co, do nhay theo nguong.
So lieu doc tu docs/results (do analytics/evaluate.py sinh ra); trang nay khong tinh lai."""
import json

import altair as alt
import pandas as pd
import streamlit as st

import ui
from common import ROOT, show_df, vn

RES = ROOT / "docs" / "results"
ui.header("Đánh giá bộ phát hiện", "Bộ phát hiện chỉ đọc tầng Gold. Chỉ chương trình đánh giá đọc đáp án của bộ mô "
                                    "phỏng, và chỉ để chấm điểm.")

with st.container(border=True):
    st.markdown(
        "**Quy trình.** Phát triển phương pháp và chọn ngưỡng trên tập phát triển, theo quy tắc khai báo trước: "
        "F1 cao nhất. Chốt ngưỡng trong mã nguồn bằng một commit riêng, rồi chạy tập kiểm tra đúng một lần, không chỉnh "
        "sau đó. "
        "Hai tập khác nhau về chi nhánh, thời điểm và mức độ sự cố.\n\n"
        "**Định nghĩa.** Cảnh báo đúng khi rơi vào cửa sổ sự cố của cùng chi nhánh, từ lúc bắt đầu đến 14 ngày sau khi "
        "kết thúc vì hậu quả có độ trễ. Recall theo tuần là tỷ lệ tuần đang có sự cố được cảnh báo. Độ trễ tính từ ngày "
        "sự cố bắt đầu đến cuối tuần có cảnh báo đầu tiên.")

SETS = {"Tập kiểm tra": "holdout", "Tập phát triển": "calibration"}
COLS = {"su_co_bat_duoc": "Sự cố bắt được", "top1_dung": "Đúng nguyên nhân hạng 1", "tre_trung_vi_ngay": "Trễ trung vị, ngày",
        "so_canh_bao": "Số cảnh báo", "bao_dong_gia": "Báo động giả", "precision": "Precision",
        "recall_tuan": "Recall theo tuần", "f1": "F1"}
for name, prof in SETS.items():
    f = RES / f"{prof}_so_sanh.csv"
    if not f.exists():
        st.caption(f"Chưa có kết quả cho {name.lower()}.")
        continue
    meta = json.loads((RES / f"{prof}_meta.json").read_text(encoding="utf-8"))
    st.subheader(f"{name} · ngưỡng điểm {vn(meta['score_alert'], 1)} · commit {meta['commit']}")
    comp = pd.read_csv(f, index_col=0).rename(columns=COLS)[list(COLS.values())]
    comp.index.name = "Phương pháp"
    comp["Trễ trung vị, ngày"] = comp["Trễ trung vị, ngày"].map(lambda v: "—" if pd.isna(v) else vn(v, 0 if v == int(v) else 1))
    show_df(comp.reset_index(), decimals={"Precision": 2, "Recall theo tuần": 2, "F1": 2}, hide_index=True, width="stretch")
    per = pd.read_csv(RES / f"{prof}_theo_su_co.csv")
    fp = pd.read_csv(RES / f"{prof}_bao_dong_gia.csv")
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("**Kết quả theo sự cố**")
        show_df(per, hide_index=True, width="stretch")
    with c2:
        st.markdown(f"**Báo động giả: {len(fp)} tuần**")
        st.dataframe(pd.DataFrame({"Chi nhánh": "CN" + fp.branch_id.astype(str),
                                   "Tuần": pd.to_datetime(fp.week_start).dt.strftime("%d/%m/%Y"),
                                   "Nghi vấn": fp.pred_cause.replace({"?": "Chưa xác định"})}),
                     hide_index=True, width="stretch")

sw = RES / "calibration_do_nhay.csv"
if sw.exists():
    st.subheader("Độ nhạy theo ngưỡng điểm, tập phát triển")
    d = pd.read_csv(sw)
    long = d.melt("nguong_diem", ["precision", "recall_tuan", "f1"], var_name="do_do", value_name="gia_tri")
    long["do_do"] = long["do_do"].map({"precision": "Precision", "recall_tuan": "Recall theo tuần", "f1": "F1"})
    comma = "replace(format(datum.value, '.1f'), '.', ',')"     # nhan truc kieu Viet Nam
    xs = alt.Scale(domain=[2, 5], nice=False)
    rule = alt.Chart(pd.DataFrame({"x": [3.5]})).mark_rule(strokeDash=[4, 4], color="#6B7280").encode(
        x=alt.X("x:Q", scale=xs))
    st.altair_chart(rule + alt.Chart(long).mark_line(point=True).encode(
        x=alt.X("nguong_diem:Q", title="Ngưỡng điểm phát cảnh báo", scale=xs, axis=alt.Axis(labelExpr=comma, tickCount=6)),
        y=alt.Y("gia_tri:Q", title=None, scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(labelExpr=comma)),
        color=alt.Color("do_do:N", title=None, scale=alt.Scale(domain=["F1", "Precision", "Recall theo tuần"],
                                                               range=["#1F3A5F", "#9CA3AF", "#2F7F86"])),
        tooltip=[alt.Tooltip("nguong_diem:Q", title="Ngưỡng"), alt.Tooltip("do_do:N", title="Độ đo"),
                 alt.Tooltip("gia_tri:Q", title="Giá trị", format=".3f")]), width="stretch")
    st.caption("Đường đứt là ngưỡng đã chốt. Ngưỡng thấp bắt được nhiều sự cố hơn nhưng báo động giả tăng nhanh.")

mv = RES / "calibration_do_nhay_phuong_phap.csv"
if mv.exists():
    st.subheader("Độ nhạy theo cách tính mức kỳ vọng, tập phát triển")
    st.caption("Mỗi phương án chỉ thay một lựa chọn trong cách tính mức kỳ vọng, giữ ngưỡng 3,5; bảng mức kỳ vọng được "
               "tính lại và đã khớp tuyệt đối với bảng dbt trước khi thay. Không chạy trên tập kiểm tra.")
    v = pd.read_csv(mv)
    show_df(pd.DataFrame({
        "Phương án": v.phuong_an, "Sự cố bắt được": v.su_co_bat_duoc, "Số cảnh báo": v.so_canh_bao,
        "Báo động giả": v.bao_dong_gia, "Precision": v.precision.round(2), "Recall theo tuần": v.recall_tuan.round(2),
        "F1": v.f1.round(2)}), decimals={"Precision": 2, "Recall theo tuần": 2, "F1": 2}, hide_index=True, width="stretch")
    st.caption("Cửa sổ 12 tuần tốt hơn nhẹ cửa sổ 8 tuần đang dùng; cấu hình không đổi vì kết quả tập kiểm tra chỉ có giá "
               "trị với cấu hình đã chốt trước. Bỏ sàn độ dao động hoặc rút cửa sổ còn 4 tuần làm báo động giả tăng mạnh.")
    il = RES / "calibration_minh_hoa_luat_vs_z.csv"
    if il.exists():
        z = pd.read_csv(il, parse_dates=["week_start"])
        st.markdown(f"**Vì sao đối soát hoa hồng dùng luật chứ không dùng điểm z.** Giả định sàn tính thừa 5 điểm % kéo "
                    f"dài {len(z)} tuần: luật bắt cả {len(z)} tuần, điểm z chỉ vượt 3 ở {int((z.z >= 3).sum())} tuần đầu, "
                    "sau đó sai lệch kéo dài trở thành mức nền \"bình thường\".")

md = RES / "KET_QUA_DANH_GIA.md"
if md.exists():
    with st.expander("Phân tích lỗi và hướng cải thiện"):
        text = md.read_text(encoding="utf-8")
        st.markdown(text[text.find("## Phân tích lỗi"):])
