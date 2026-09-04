import base64
import io
import zipfile
from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st

from deepseek_client import call_deepseek
from logger import save_log
from prompts import PROMPTS


# =========================================================
# 页面基础设置
# =========================================================

st.set_page_config(
    page_title="GenAI 对话系统",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# 页面样式
# =========================================================

CSS = """
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
    position: fixed;
    top: 22px;
    left: 28px;
    display:flex;
    align-items:center;
    justify-content:flex-start;
    gap:10px;
    padding:0;
    color:#202124;
    z-index:9998;
}

.logo-circle {
    width:32px;
    height:32px;
    border-radius:50%;
    background:linear-gradient(135deg,#4f8cff,#7aa7ff);
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-weight:700;
    font-size:17px;
}

.chat-title {
    font-size:22px;
    font-weight:650;
    letter-spacing:.2px;
    line-height:1.05;
}

.chat-subtitle {
    font-size:12px;
    color:#6b7280;
    margin-left:1px;
    margin-top:2px;
}

@media (max-width:700px) {
    .chat-header {
        top: 14px;
        left: 16px;
        transform: scale(0.9);
        transform-origin: left top;
    }
}

.login-card {
    max-width:480px;
    margin:120px auto 0 auto;
    padding:34px 34px 28px 34px;
    border-radius:22px;
    background:#fff;
    box-shadow:0 12px 35px rgba(0,0,0,.06);
    border:1px solid #eceef3;
}

.login-title {
    text-align:center;
    font-size:26px;
    font-weight:700;
    margin-bottom:8px;
}

.login-subtitle {
    text-align:center;
    color:#6b7280;
    font-size:15px;
    margin-bottom:20px;
}

.welcome {
    text-align:center;
    margin-top:88px;
    margin-bottom:30px;
}

.welcome-title {
    font-size:32px;
    font-weight:720;
    color:#202124;
    margin-bottom:8px;
}

.welcome-subtitle {
    font-size:16px;
    color:#6b7280;
}

.stChatMessage {
    background:transparent;
}

[data-testid="stChatMessageContent"] {
    border-radius:18px;
    padding:12px 16px;
}

.stChatMessage:has([data-testid="chatAvatarIcon-user"])
[data-testid="stChatMessageContent"] {
    background:#e9f1ff;
}

.stChatMessage:has([data-testid="chatAvatarIcon-assistant"])
[data-testid="stChatMessageContent"] {
    background:#fff;
    border:1px solid #edf0f5;
}

[data-testid="stChatInput"] {
    max-width:820px;
    margin:0 auto;
}

[data-testid="stChatInput"] textarea {
    border-radius:18px !important;
    border:1px solid #dfe3ea !important;
    background:#fff !important;
    box-shadow:0 6px 25px rgba(0,0,0,.06);
}

.stButton > button {
    border-radius:14px;
    font-weight:600;
}

.floating-download-panel {
    position: fixed;
    right: 24px;
    top: 22px;
    width: 188px;
    padding: 12px 13px 13px 13px;
    background: #ffffff;
    border: 1px solid #dfe3ea;
    border-radius: 16px;
    box-shadow: 0 10px 28px rgba(0,0,0,.12);
    z-index: 9999;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.floating-download-title {
    font-size:13px;
    font-weight:700;
    color:#202124;
    margin-bottom:4px;
}

.floating-download-desc {
    font-size:11.5px;
    color:#6b7280;
    line-height:1.45;
    margin-bottom:9px;
}

.floating-download-links a {
    display:block;
    text-align:center;
    padding:8px 0;
    border-radius:12px;
    text-decoration:none;
    font-size:12.5px;
    font-weight:650;
    color:white !important;
    background:#4f8cff;
}

@media (max-width:700px) {
    .floating-download-panel {
        right: 12px;
        top: 70px;
        width: 172px;
        padding: 10px 11px;
    }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# =========================================================
# 读取被试分组
# =========================================================

@st.cache_data
def load_participants():
    return pd.read_csv("participants.csv", dtype=str)


participants = load_participants()


# =========================================================
# 基础函数
# =========================================================

def make_conversation_id(participant_id):
    return f"{participant_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def normalize_participant_id(raw_id):
    value = raw_id.strip()

    if not value.isdigit():
        return None

    number = int(value)

    if 1 <= number <= 80:
        return str(number)

    return None


def start_new_conversation():
    st.session_state.messages = [
        {
            "role": "system",
            "content": PROMPTS[st.session_state.condition]
        }
    ]

    st.session_state.turn_index = 0

    st.session_state.conversation_id = make_conversation_id(
        st.session_state.participant_id
    )


def add_record(role, content, turn_index):
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "participant_id": st.session_state.participant_id,
        "condition": st.session_state.condition,
        "conversation_id": st.session_state.conversation_id,
        "role": role,
        "turn_index": turn_index,
        "content": content
    }

    st.session_state.all_chat_records.append(record)


# =========================================================
# 安全保存日志
# 即使日志保存失败，也不影响正常实验
# =========================================================

def safe_save_log(
    participant_id,
    condition,
    conversation_id,
    role,
    content,
    turn_index
):
    try:
        save_log(
            participant_id,
            condition,
            conversation_id,
            role,
            content,
            turn_index
        )

    except Exception as e:
        print(">>> 日志保存失败：", repr(e))


# =========================================================
# 构建 TXT 对话记录
# =========================================================

def build_txt_record():
    participant_id = st.session_state.get("participant_id", "")
    condition = st.session_state.get("condition", "")
    records = st.session_state.get("all_chat_records", [])

    lines = [
        f"被试编号：{participant_id}",
        f"实验条件：{condition}",
        f"导出时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "======== 对话记录 ========",
        ""
    ]

    if not records:
        lines.append("暂无对话内容。")

    else:
        current_conversation = None

        for record in records:

            if record["conversation_id"] != current_conversation:
                current_conversation = record["conversation_id"]

                lines.append("")
                lines.append(
                    f"---- 对话编号：{current_conversation} ----"
                )
                lines.append("")

            role_label = (
                "用户"
                if record["role"] == "user"
                else "系统"
            )

            lines.append(
                f"[{role_label} 第{record['turn_index']}轮]"
            )

            lines.append(
                str(record.get("content") or "")
            )

            lines.append("")

    return "\n".join(lines)


# =========================================================
# 构建 CSV 对话记录
# =========================================================

def build_csv_record():
    records = st.session_state.get("all_chat_records", [])

    rows = [
        "timestamp,participant_id,condition,"
        "conversation_id,role,turn_index,content"
    ]

    for record in records:

        content = str(record.get("content") or "")

        content = (
            content
            .replace('"', '""')
            .replace("\n", "\\n")
        )

        rows.append(
            f'"{record["timestamp"]}",'
            f'"{record["participant_id"]}",'
            f'"{record["condition"]}",'
            f'"{record["conversation_id"]}",'
            f'"{record["role"]}",'
            f'"{record["turn_index"]}",'
            f'"{content}"'
        )

    return "\n".join(rows)


# =========================================================
# 构建 ZIP
# =========================================================

def build_zip_record():
    participant_id = st.session_state.get(
        "participant_id",
        "participant"
    )

    export_time = datetime.now().strftime("%Y%m%d%H%M%S")

    txt_name = (
        f"{participant_id}_{export_time}_chat_record.txt"
    )

    csv_name = (
        f"{participant_id}_{export_time}_chat_record.csv"
    )

    buffer = io.BytesIO()

    with zipfile.ZipFile(
        buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        zip_file.writestr(
            txt_name,
            build_txt_record().encode("utf-8-sig")
        )

        zip_file.writestr(
            csv_name,
            build_csv_record().encode("utf-8-sig")
        )

    return buffer.getvalue()


# =========================================================
# 右上角下载面板
# =========================================================

def render_floating_download_panel():
    records = st.session_state.get(
        "all_chat_records",
        []
    )

    if not records:
        return

    participant_id = st.session_state.get(
        "participant_id",
        "participant"
    )

    export_time = datetime.now().strftime("%Y%m%d%H%M%S")

    zip_name = (
        f"{participant_id}_{export_time}_chat_records.zip"
    )

    zip_bytes = build_zip_record()

    zip_href = (
        "data:application/zip;base64,"
        + base64.b64encode(zip_bytes).decode("utf-8")
    )

    html = f"""
<div class="floating-download-panel">
    <div class="floating-download-title">对话记录</div>
    <div class="floating-download-desc">
        实验结束后，请一键下载并与 Word 任务产出一并提交。
    </div>
    <div class="floating-download-links">
        <a href="{zip_href}" download="{escape(zip_name)}">
            一键下载记录
        </a>
    </div>
</div>
"""

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# =========================================================
# 左上角系统标题
# =========================================================

def render_header():
    st.markdown("""
<div class="chat-header">
    <div class="logo-circle">G</div>
    <div>
        <div class="chat-title">GenAI 对话系统</div>
        <div class="chat-subtitle">Powered by DeepSeek API</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# 初始化
# =========================================================

if "started" not in st.session_state:
    st.session_state.started = False


# =========================================================
# 登录页面
# =========================================================

if not st.session_state.started:

    render_header()

    st.markdown("""
<div class="login-card">
    <div class="login-title">欢迎参加本次实验！</div>
    <div class="login-subtitle">
        请输入您的编号，进入 GenAI 对话系统。
    </div>
</div>
""", unsafe_allow_html=True)

    raw_participant_id = st.text_input(
        "被试编号",
        placeholder="例如：1",
        label_visibility="collapsed"
    )

    if st.button(
        "进入对话",
        type="primary",
        use_container_width=True
    ):

        participant_id = normalize_participant_id(
            raw_participant_id
        )

        if participant_id is None:

            st.error(
                "请输入 1-80 之间的数字编号。"
            )

        else:

            row = participants[
                participants["participant_id"]
                == participant_id
            ]

            if row.empty:

                st.error(
                    "编号不存在，请检查后重新输入，或联系主试。"
                )

            else:

                st.session_state.participant_id = participant_id

                st.session_state.condition = (
                    row.iloc[0]["condition"]
                )

                st.session_state.started = True

                st.session_state.all_chat_records = []

                start_new_conversation()

                st.rerun()


# =========================================================
# 对话页面
# =========================================================

else:

    render_header()

    # -----------------------------------------------------
    # 开启新对话
    # -----------------------------------------------------

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:

        if st.button(
            "＋ 开启新对话",
            use_container_width=True
        ):

            start_new_conversation()

            st.rerun()


    # -----------------------------------------------------
    # 显示已有对话
    # -----------------------------------------------------

    visible_messages = [
        m
        for m in st.session_state.messages
        if m["role"] != "system"
    ]


    if not visible_messages:

        st.markdown("""
<div class="welcome">
    <div class="welcome-title">
        我是 GenAI 对话系统，很高兴见到你！
    </div>
    <div class="welcome-subtitle">
        请根据任务书要求，在下方输入框中开始对话。
    </div>
</div>
""", unsafe_allow_html=True)


    for msg in visible_messages:

        with st.chat_message(
            msg["role"]
        ):

            st.write(
                msg["content"]
            )


    # -----------------------------------------------------
    # 输入框
    # -----------------------------------------------------

    user_input = st.chat_input(
        "给 GenAI 对话系统发送消息"
    )


    # -----------------------------------------------------
    # 用户发送消息
    # -----------------------------------------------------

    if user_input:

        st.session_state.turn_index += 1


        # 用户消息进入模型上下文
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )


        # 保存到实验下载记录
        add_record(
            "user",
            user_input,
            st.session_state.turn_index
        )


        # 安全写入后台日志
        safe_save_log(
            st.session_state.participant_id,
            st.session_state.condition,
            st.session_state.conversation_id,
            "user",
            user_input,
            st.session_state.turn_index
        )


        # 显示用户消息
        with st.chat_message("user"):

            st.write(
                user_input
            )


        # -------------------------------------------------
        # 调用 DeepSeek
        # -------------------------------------------------

        with st.spinner(
            "正在生成回答，请稍候..."
        ):

            try:

                assistant_reply = call_deepseek(
                    st.session_state.messages
                )

                # app.py 第二层空响应保护
                if (
                    assistant_reply is None
                    or not str(
                        assistant_reply
                    ).strip()
                ):

                    raise RuntimeError(
                        "模型返回空响应"
                    )

                call_success = True


            except Exception as e:

                call_success = False

                # 被试只看到简洁提示
                assistant_reply = (
                    "当前服务响应较慢，请稍候重新尝试。"
                    "如果仍无法响应，请联系主试。"
                )

                # 详细错误只输出到后台
                print(
                    ">>> DeepSeek 最终调用失败：",
                    repr(e)
                )


        # -------------------------------------------------
        # 显示 AI 回复
        # -------------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            st.write(
                assistant_reply
            )


        # -------------------------------------------------
        # 只有真实 AI 回复才进入模型上下文
        #
        # API 失败提示不会作为 assistant 历史消息
        # 发送给下一轮 DeepSeek
        # -------------------------------------------------

        if call_success:

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_reply
                }
            )


        # -------------------------------------------------
        # 页面实际显示的内容全部进入实验记录
        #
        # 即使 API 失败，也能在实验记录里发现
        # -------------------------------------------------

        add_record(
            "assistant",
            assistant_reply,
            st.session_state.turn_index
        )


        # -------------------------------------------------
        # assistant 日志安全保存
        # -------------------------------------------------

        safe_save_log(
            st.session_state.participant_id,
            st.session_state.condition,
            st.session_state.conversation_id,
            "assistant",
            assistant_reply,
            st.session_state.turn_index
        )


    # -----------------------------------------------------
    # 右上角下载按钮
    # -----------------------------------------------------

    render_floating_download_panel()
