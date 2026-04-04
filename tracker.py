import json
from pathlib import Path
from datetime import date

DATA_FILE = Path(__file__).parent / "data" / "progress.json"


def load() -> dict:
    if not DATA_FILE.exists():
        return {"coding": {}, "system_design": {}, "behavioral": {}}
    with open(DATA_FILE) as f:
        return json.load(f)


def save(data: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record(category: str, question_id: str, result: str, note: str = "") -> None:
    """result: 'got_it' | 'struggled' | 'skipped'"""
    data = load()
    if category not in data:
        data[category] = {}
    entry = data[category].get(question_id, {"attempts": 0, "got_it": 0, "history": []})
    entry["attempts"] += 1
    if result == "got_it":
        entry["got_it"] += 1
    entry["history"].append({"date": str(date.today()), "result": result, "note": note})
    entry["last_result"] = result
    data[category][question_id] = entry
    save(data)


def get_stats(category: str) -> dict:
    data = load()
    return data.get(category, {})


def get_summary() -> dict:
    data = load()
    summary = {}
    for cat, questions in data.items():
        total = len(questions)
        got_it = sum(1 for q in questions.values() if q.get("last_result") == "got_it")
        struggled = sum(1 for q in questions.values() if q.get("last_result") == "struggled")
        summary[cat] = {"total_attempted": total, "got_it": got_it, "struggled": struggled}
    return summary


def get_review_list(category: str) -> list[str]:
    """Return question IDs where last result was 'struggled'."""
    stats = get_stats(category)
    return [qid for qid, data in stats.items() if data.get("last_result") == "struggled"]
