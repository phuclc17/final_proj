"""Tro ly phan tich: hoi dap tieng Viet, mo hinh goi cac ham phan tich co san cua he thong roi dien dat ket qua.
Hien ro da goi cong cu nao, voi tham so gi, va bao nhieu con so trong cau tra loi khop ket qua cong cu."""
import json

import streamlit as st

import ui
from common import PROFILES, action_context, current_profile, db_path, load_current, vn
from analytics import assistant as A

ui.header("Trợ lý phân tích", "Hỏi bằng tiếng Việt về kinh doanh, cảnh báo và nguyên nhân. Trợ lý gọi các hàm phân "
                              "tích có sẵn và truy vấn chỉ đọc trên kho; mọi con số lấy từ kết quả các hàm đó.")

G, scores, alerts = load_current()
profile = current_profile()
label = next(k for k, v in PROFILES.items() if v == profile)

try:
    client, model, extra, provider = A.make_client()
except A.NoCredentials as e:
    ui.note("Chưa kết nối mô hình ngôn ngữ", str(e), "Theo dõi")
    st.markdown(
        "Đặt một trong hai cấu hình rồi khởi động lại ứng dụng. Không dán khóa vào mã nguồn.\n"
        "- Claude API: biến môi trường `ANTHROPIC_API_KEY`.\n"
        "- Amazon Bedrock: `FASTFAT_LLM_PROVIDER=bedrock`, `AWS_REGION` và thông tin xác thực AWS từ biến môi trường, "
        "tệp `~/.aws` hoặc IAM role của máy chủ.\n\n"
        "Với Docker Compose, đặt các biến này trong tệp `.env` cạnh `docker-compose.yml`.")
    st.stop()

key = f"chat_{profile}"
if key not in st.session_state:
    st.session_state[key] = {"messages": [], "turns": []}
chat = st.session_state[key]
box = A.ToolBox(G, scores, alerts, action_context(), db_path(profile))
system = A.system_prompt(G, label)

c1, c2 = st.columns([4, 1])
c1.caption(f"{provider} · {model} · tập {label}")
if c2.button("Cuộc trò chuyện mới", width="stretch"):
    st.session_state[key] = {"messages": [], "turns": []}
    st.rerun()

EXAMPLES = ["Tuần gần nhất chi nhánh nào cần ưu tiên xử lý, vì sao?",
            "Vì sao doanh thu CN2 tuần 06/05/2024 thấp? Cần làm gì?",
            "So sánh COGS% và Labor% của các chi nhánh hạng C trong tháng 8/2024.",
            "Tổng thiệt hại ước tính của các cảnh báo từ tháng 4 đến tháng 9/2024 là bao nhiêu, theo nguyên nhân?"]


def show_turn(question, t):
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        st.markdown(t.answer or "Không có nội dung.")
        found, total, missing = A.grounding(t.answer, t.calls)
        check = (f"{found}/{total} con số khớp kết quả công cụ" if total else "không có con số cần đối chiếu") + \
            (f" · chưa khớp: {', '.join(missing[:5])}" if missing else "")
        st.caption(f"{len(t.calls)} lượt gọi công cụ · {check} · {vn(t.input_tokens)} token vào, "
                   f"{vn(t.output_tokens)} token ra · khoảng {t.cost_usd:.3f} USD · {t.seconds:.0f} giây")
        if t.calls:
            with st.expander(f"Công cụ đã gọi: {len(t.calls)}"):
                for name, args, out in t.calls:
                    st.markdown(f"**{name}** `{json.dumps(args, ensure_ascii=False)}`")
                    st.json(out, expanded=False)


for q, t in chat["turns"]:
    show_turn(q, t)

if not chat["turns"]:
    st.markdown("**Gợi ý câu hỏi**")
    cols = st.columns(2)
    for i, ex in enumerate(EXAMPLES):
        if cols[i % 2].button(ex, key=f"ex_{i}", width="stretch"):
            st.session_state.pending_question = ex
            st.rerun()

question = st.chat_input("Đặt câu hỏi về vận hành, doanh thu, cảnh báo…") or st.session_state.pop("pending_question", None)
if question:
    if len(chat["messages"]) > 60:   # hoi thoai qua dai: bat dau lai de giu chi phi va do chinh xac
        chat["messages"], chat["turns"] = [], []
    chat["messages"].append({"role": "user", "content": question})
    with st.spinner("Trợ lý đang phân tích…"):
        try:
            turn = A.ask(client, model, extra, system, chat["messages"], box)
        except Exception as e:  # loi ket noi, khoa sai, het han muc...
            chat["messages"].pop()
            st.error(f"Không gọi được mô hình: {type(e).__name__}: {str(e)[:300]}")
            st.stop()
    chat["turns"].append((question, turn))
    st.rerun()
