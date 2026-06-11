import csv
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("data/chat_logs.csv")

def save_log(participant_id, condition, conversation_id, role, content, turn_index):
    """
    保存完整对话日志。
    conversation_id 用于区分同一被试开启的不同新对话。
    role: user / assistant
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_exists = LOG_FILE.exists()

    with LOG_FILE.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "participant_id",
                "condition",
                "conversation_id",
                "role",
                "turn_index",
                "content"
            ])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            participant_id,
            condition,
            conversation_id,
            role,
            turn_index,
            content
        ])
