import streamlit as st
import pandas as pd
from datetime import datetime
from prompts import PROMPTS
from deepseek_client import call_deepseek
from logger import save_log

st.set_page_config(
    page_title="DeepSeek",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: #f7f8fb;
}

.block-container {
    max-width: 880px;
    padding-top: 1.2rem;
    padding-bottom: 7rem;
}

.chat-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 16px 0 8px 0;
    color: #202124;
}

.logo-circle {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4f8cff, #7aa7ff);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 18px;
}

.chat-title {
    font-size: 24px;
    font-weight: 650;
    letter-spacing: 0.2px;
}

.top-actions {
    display: flex;
    justify-content: center;
    margin: 6px 0 12px 0;
    color: #6b7280;
    font-size: 13px;
}

.login-card {
    max-width: 480px;
    margin: 80px auto 0 auto;
    padding: 34px 34px 28px 34px;
    border-radius: 22px;
    background: #ffffff;
    box-shadow: 0 12px 35px rgba(0,0,0,0.06);
    border: 1px solid #eceef3;
}

.login-title {
    text-align: center;
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 8px;
}

.login-subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 20px;
}

.welcome {
    text-align: center;
    margin-top: 88px;
    margin-bottom: 30px;
}

.welcome-title {
    font-size: 32px;
    font-weight: 720;
    color: #202124;
    margin-bottom: 8px;
}

.welcome-subtitle {
    font-size: 16px;
    color: #6b7280;
}

.stChatMessage {
    background: transparent;
}

[data-testid="stChatMessageContent"] {
    border-radius: 18px;
    padding: 12px 16px;
}

.stChatMessage:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: #e9f1ff;
}

.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: #ffffff;
    border: 1px solid #edf0f5;
}

[data-testid="stChatInput"] {
    max-width: 820px;
    margin: 0 auto;
}

[data-testid="stChatInput"] textarea {
    border-radius: 18px !important;
    border: 1px solid #dfe3ea !important;
    background: #ffffff !important;
    box-shadow: 0 6px 25px rgba(0,0,0,0.06);
}

.stButton > button {
    border-radius: 14px;
    font-weight: 600;
}

[data-testid="stSidebar"] {
    background: #ffffff;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_data
def load_participants():
    return pd.read_csv("participants.csv", dtype=str)

participants = load_participants()

def make_conversation_id(participant_id):
    """
    为每一次新对话生成唯一编号，方便后续区分同一被试的多段对话。
    """
    time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{participant_id}_{time_str}"

def start_new_conversation():
    """
    开启新对话：清空当前聊天界面，但保留被试编号与实验组别。
    旧对话日志已经写入 data/chat_logs.csv，不会被删除。
    """
    st.session_state.messages = [
        {"role": "system", "content": PROMPTS[st.session_state.condition]}
    ]
    st.session_state.turn_index = 0
    st.session_state.conversation_id = make_conversation_id(st.session_state.participant_id)

if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.markdown("""
    <div class="chat-header">
        <div class="logo-circle">D</div>
        <div class="chat-title">DeepSeek</div>
    </div>
    <div class="login-card">
        <div class="login-title">欢迎使用</div>
        <div class="login-subtitle">请输入主试提供的被试编号，进入对话系统。</div>
    </div>
    """, unsafe_allow_html=True)

    participant_id = st.text_input("被试编号", placeholder="例如：P001", label_visibility="collapsed")

    if st.button("进入对话", type="primary", use_container_width=True):
        row = participants[participants["participant_id"] == participant_id.strip()]

        if row.empty:
            st.error("编号不存在，请检查后重新输入，或联系主试。")
        else:
            condition = row.iloc[0]["condition"]
            st.session_state.participant_id = participant_id.strip()
            st.session_state.condition = condition
            st.session_state.started = True
            start_new_conversation()
            st.rerun()

else:
    st.markdown("""
    <div class="chat-header">
        <div class="logo-circle">D</div>
        <div class="chat-title">DeepSeek</div>
    </div>
    """, unsafe_allow_html=True)

    # 顶部“开启新对话”按钮
    top_col1, top_col2, top_col3 = st.columns([1, 1, 1])
    with top_col2:
        if st.button("＋ 开启新对话", use_container_width=True):
            start_new_conversation()
            st.rerun()

    visible_messages = [m for m in st.session_state.messages if m["role"] != "system"]

    if not visible_messages:
        st.markdown("""
        <div class="welcome">
            <div class="welcome-title">我是 DeepSeek，很高兴见到你！</div>
            <div class="welcome-subtitle">请根据任务书要求，在下方输入框中开始对话。</div>
        </div>
        """, unsafe_allow_html=True)

    for msg in visible_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("给 DeepSeek 发送消息")

    if user_input:
        st.session_state.turn_index += 1

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        save_log(
            participant_id=st.session_state.participant_id,
            condition=st.session_state.condition,
            conversation_id=st.session_state.conversation_id,
            role="user",
            content=user_input,
            turn_index=st.session_state.turn_index
        )

        with st.chat_message("user"):
            st.write(user_input)

        try:
            assistant_reply = call_deepseek(st.session_state.messages)
        except Exception as e:
            assistant_reply = f"系统调用出错，请联系主试。错误信息：{e}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })

        save_log(
            participant_id=st.session_state.participant_id,
            condition=st.session_state.condition,
            conversation_id=st.session_state.conversation_id,
            role="assistant",
            content=assistant_reply,
            turn_index=st.session_state.turn_index
        )

        with st.chat_message("assistant"):
            st.write(assistant_reply)

    with st.sidebar:
        st.markdown("### 对话信息")
        st.write("请按照任务书要求完成实验。")
        st.write("任务产出请填写在 Word 文档中。")
        st.divider()
        if st.button("开启新对话"):
            start_new_conversation()
            st.rerun()
        if st.button("结束当前对话"):
            st.success("对话已结束。请根据任务书继续完成后续步骤。")
