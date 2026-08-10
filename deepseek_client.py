from openai import OpenAI
import streamlit as st

def get_client():
    api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise RuntimeError("未找到 DEEPSEEK_API_KEY。请在 .streamlit/secrets.toml 中配置 API Key。")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def call_deepseek(messages, model="deepseek-v4-flash", temperature=0):
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        timeout=60
    )
    return response.choices[0].message.content
