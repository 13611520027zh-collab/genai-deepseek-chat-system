from openai import OpenAI
import streamlit as st


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


def call_deepseek(messages, model="deepseek-v4-flash", temperature=0):
    client = get_client()

    print(">>> 准备调用 DeepSeek")
    print(">>> 当前 messages 数量：", len(messages))

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            timeout=300
        )

        print(">>> DeepSeek 已返回 response")

        choice = response.choices[0]
        content = choice.message.content

        print(">>> finish_reason:", choice.finish_reason)
        print(">>> content 类型:", type(content))
        print(
            ">>> content 长度:",
            len(content) if content is not None else "None"
        )

        return content

    except Exception as e:
        print(">>> DeepSeek 调用发生异常：", repr(e))
        raise
