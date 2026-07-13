from pathlib import Path
import json
from rc_config import data_path

DATA_FILE = data_path(
    "research_admin",
    "research_objects.json",
    legacy="research/research_objects.json",
)


def load_objects() -> list:
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_objects(objects: list):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(objects, f, ensure_ascii=False, indent=2)
