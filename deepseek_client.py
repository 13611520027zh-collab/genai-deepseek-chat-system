from openai import OpenAI
import streamlit as st
import time

def get_client():
    api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "未找到 DEEPSEEK_API_KEY。请在 .streamlit/secrets.toml 中配置 API Key。"
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

    print(">>> 准备调用 DeepSeek")

    print(">>> 当前 messages 数量：", len(messages))

    last_error = None

    for attempt in range(1, max_retries + 1):

        try:

            print(f">>> 第 {attempt}/{max_retries} 次调用 DeepSeek")

            response = client.chat.completions.create(

                model=model,

                messages=messages,

                temperature=temperature,

                timeout=300

            )

            print(">>> DeepSeek 已返回 response")

            # 检查 choices

            if not response.choices:

                raise RuntimeError("DeepSeek 返回的 choices 为空")

            choice = response.choices[0]

            content = choice.message.content

            print(">>> finish_reason:", choice.finish_reason)

            print(">>> content 类型:", type(content))

            print(

                ">>> content 长度:",

                len(content) if content is not None else "None"

            )

            # 核心：检查空响应

            if content is None or not str(content).strip():

                raise RuntimeError(

                    f"DeepSeek 返回空内容，finish_reason={choice.finish_reason}"

                )

            return content

        except Exception as e:

            last_error = e

            print(

                f">>> 第 {attempt}/{max_retries} 次调用失败：",

                repr(e)

            )

            # 不是最后一次则等待后重试

            if attempt < max_retries:

                wait_seconds = attempt * 2

                print(

                    f">>> {wait_seconds} 秒后自动重试..."

                )

                time.sleep(wait_seconds)

    # 连续失败后才真正抛给 app.py

    raise RuntimeError(

        f"DeepSeek 连续 {max_retries} 次调用失败。"

        f"最后一次错误：{last_error}"

    )
