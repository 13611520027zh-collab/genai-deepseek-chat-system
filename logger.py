import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path

def beijing_time():
    return datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

LOG_FILE = Path("data/chat_logs.csv")

def save_log(participant_id, condition, conversation_id, role, content, turn_index):
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
            beijing_time(),
            participant_id,
            condition,
            conversation_id,
            role,
            turn_index,
            content
        ])
