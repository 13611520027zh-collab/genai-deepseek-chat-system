# GenAI 对话系统：80 名被试分组版

本系统用于第五章“GenAI 对话系统主动交互策略效果实验”。系统前端提供统一的网页对话界面，后台通过不同的系统提示词控制实验条件，并调用 DeepSeek API 生成回复。

## 一、系统功能

本版本包含以下功能：

1. 被试输入数字编号进入系统；
2. 编号范围为 1-80；
3. 系统根据编号自动匹配实验条件；
4. 四组界面、模型接口和操作方式保持一致，仅后台策略控制不同；
5. 支持“开启新对话”；
6. 开启新对话只清空当前聊天界面，不删除已产生的实验记录；
7. 右上角提供“一键下载记录”；
8. 下载文件为 ZIP 压缩包，内含 TXT 与 CSV 两份对话记录；
9. 本地运行时，系统同时会将完整日志保存到 `data/chat_logs.csv`。

## 二、被试编号与实验分组

本版本按照 80 名被试设置，采用 4 组平均分配，每组 20 人。

| 编号范围 | condition | 实验条件 |
|---|---|---|
| 1-20 | control | 被动响应组 / 对照组 |
| 21-40 | clarification | 主动澄清组 / 实验组 A |
| 41-60 | suggestion | 主动建议组 / 实验组 B |
| 61-80 | disclosure | 主动披露组 / 实验组 C |

正式实验时，被试只需要输入 1-80 之间的数字编号，例如：`1`、`25`、`48`、`80`。不需要输入 `P001`，也不需要补 0。

## 三、文件说明

| 文件 | 作用 |
|---|---|
| `app.py` | Streamlit 网页主程序 |
| `deepseek_client.py` | DeepSeek API 调用模块 |
| `logger.py` | 对话日志保存模块 |
| `participants.csv` | 被试编号与实验条件对应表 |
| `prompts.py` | 四组实验条件的系统提示词 |
| `requirements.txt` | Python 依赖包 |
| `.streamlit/secrets.example.toml` | API Key 配置示例 |

## 四、本地运行方法

进入项目文件夹后运行：

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## 五、配置 DeepSeek API Key

在项目文件夹中新建：

```text
.streamlit/secrets.toml
```

写入：

```toml
DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
```

注意：正式上传 GitHub 或部署 Streamlit Cloud 时，不要上传真实的 `secrets.toml` 文件。

## 六、部署到 Streamlit Cloud

上传到 GitHub 时，建议上传以下文件：

```text
app.py
deepseek_client.py
logger.py
participants.csv
prompts.py
requirements.txt
README.md
.streamlit/secrets.example.toml
```

不要上传以下内容：

```text
.streamlit/secrets.toml
data/
__pycache__/
```

在 Streamlit Cloud 的 Secrets 中填写：

```toml
DEEPSEEK_API_KEY = "你的 DeepSeek API Key"
```

## 七、正式实验操作提示

任务书中可以写：

> 请使用主试提供的编号进入 GenAI 对话系统。完成实验后，请点击页面右上角“一键下载记录”按钮，将下载得到的 ZIP 压缩包与 Word 任务产出一并提交。

## 八、预测试建议

正式实验前建议至少测试以下编号：

| 测试编号 | 对应实验条件 |
|---|---|
| 1 | 被动响应组 / 对照组 |
| 21 | 主动澄清组 / 实验组 A |
| 41 | 主动建议组 / 实验组 B |
| 61 | 主动披露组 / 实验组 C |
| 80 | 主动披露组 / 实验组 C |

测试重点包括：能否进入系统、能否正常回复、开启新对话后记录是否保留、一键下载 ZIP 是否包含 TXT 和 CSV 两个文件。
