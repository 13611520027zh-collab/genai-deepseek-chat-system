from openai import OpenAI
import streamlit as st
import time
import traceback
from datetime import datetime


def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}", flush=True)


def get_client():
    api_key = st.secrets.get("DEEPSEEK_API_KEY", "")

    if not api_key:
        raise RuntimeError(
            "未找到 DEEPSEEK_API_KEY。"
            "请在 .streamlit/secrets.toml 中配置 API Key。"
        )

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )


def call_deepseek(
    messages,
    model="deepseek-v4-flash",
    temperature=0,
    max_retries=3
):

    client = get_client()

    log("=" * 60)
    log("准备调用 DeepSeek")
    log(f"模型：{model}")
    log(f"当前 messages 数量：{len(messages)}")

    # 只记录角色和长度，不打印实验内容
    for i, message in enumerate(messages):
        role = message.get("role", "")
        content = message.get("content", "")
        content_length = len(str(content)) if content is not None else 0

        log(
            f"message[{i}] "
            f"role={role}, "
            f"length={content_length}"
        )

    last_error = None

    for attempt in range(1, max_retries + 1):

        log(f"第 {attempt}/{max_retries} 次调用开始")

        start_time = time.time()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                timeout=300
            )

            elapsed = time.time() - start_time

            log(
                f"DeepSeek 已返回 response，"
                f"耗时 {elapsed:.2f} 秒"
            )

            if response is None:
                raise RuntimeError(
                    "DeepSeek response 为 None"
                )

            if not response.choices:
                raise RuntimeError(
                    "DeepSeek 返回的 choices 为空"
                )

            choice = response.choices[0]

            log(
                f"finish_reason="
                f"{repr(choice.finish_reason)}"
            )

            message = choice.message

            if message is None:
                raise RuntimeError(
                    "DeepSeek 返回的 message 为 None"
                )

            content = message.content

            log(
                f"content 类型="
                f"{type(content)}"
            )

            log(
                f"content repr="
                f"{repr(content)[:500]}"
            )

            log(
                f"content 长度="
                f"{len(content) if content is not None else 'None'}"
            )

            # 记录 usage
            if getattr(response, "usage", None):
                log(
                    f"usage="
                    f"{response.usage}"
                )

            # 检查空响应
            if content is None:
                raise RuntimeError(
                    "DeepSeek 返回 content=None，"
                    f"finish_reason={choice.finish_reason}"
                )

            if not str(content).strip():
                raise RuntimeError(
                    "DeepSeek 返回空字符串，"
                    f"finish_reason={choice.finish_reason}"
                )

            log("本次 DeepSeek 调用成功")
            log("=" * 60)

            return content

        except Exception as e:

            elapsed = time.time() - start_time

            last_error = e

            log(
                f"第 {attempt}/{max_retries} 次调用失败，"
                f"耗时 {elapsed:.2f} 秒"
            )

            log(
                f"异常类型：{type(e).__name__}"
            )

            log(
                f"异常内容：{repr(e)}"
            )

            # 输出完整 traceback 到 Streamlit Cloud 日志
            traceback.print_exc()

            if attempt < max_retries:

                wait_seconds = attempt * 2

                log(
                    f"{wait_seconds} 秒后自动重试"
                )

                time.sleep(wait_seconds)

    log(
        f"连续 {max_retries} 次调用均失败"
    )

    log("=" * 60)

    raise RuntimeError(
        f"DeepSeek 连续 {max_retries} 次调用失败。"
        f"最后一次错误：{last_error}"
    )
