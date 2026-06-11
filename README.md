# DeepSeek 风格实验对话系统：含开启新对话功能

这个版本保留简洁对话界面，并新增“开启新对话”功能。

## 功能

- 被试输入编号进入系统
- 后台根据编号匹配实验条件
- 前端呈现接近 DeepSeek / ChatGPT 的简洁对话界面
- 顶部提供“＋ 开启新对话”按钮
- 开启新对话后，页面聊天记录会清空
- 后台不会删除旧日志，会用 `conversation_id` 区分同一被试的不同对话
- 系统自动保存完整人机交互日志
- 实验任务书和任务产出由 Word 完成

## 配置 API Key

新建文件：

```text
.streamlit/secrets.toml
```

写入：

```toml
DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
```

## 运行

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## 日志字段

运行后自动生成：

```text
data/chat_logs.csv
```

字段包括：

- timestamp
- participant_id
- condition
- conversation_id
- role
- turn_index
- content

其中 `conversation_id` 用于区分同一被试多次点击“开启新对话”后产生的不同对话。
