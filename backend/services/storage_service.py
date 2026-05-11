import json
import os
from pathlib import Path

# Vercel 서버리스: /tmp 사용, 로컬: backend/data 사용
if os.environ.get("VERCEL"):
    DATA_FILE = Path("/tmp/expenses.json")
else:
    DATA_FILE = Path(__file__).parent.parent / "data" / "expenses.json"


def load_expenses() -> list:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_expenses(data: list) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_expense(item: dict) -> dict:
    import uuid
    from datetime import datetime, timezone

    item["id"] = str(uuid.uuid4())
    item["created_at"] = datetime.now(timezone.utc).isoformat()
    expenses = load_expenses()
    expenses.append(item)
    save_expenses(expenses)
    return item
