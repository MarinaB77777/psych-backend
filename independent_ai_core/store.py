from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from rc_config import data_path


class OfflineCoreStore:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root is not None else data_path(
            "internal",
            "offline_ai_core",
            legacy="data/offline_ai_core",
        )
        self.events_path = self.root / "learning_events.json"
        self.profile_path = self.root / "learning_profile.json"

    def ensure_ready(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

        if not self.events_path.exists():
            self.events_path.write_text("[]\n", encoding="utf-8")

        if not self.profile_path.exists():
            self.profile_path.write_text("{}\n", encoding="utf-8")

    def load_events(self) -> list[dict[str, Any]]:
        self.ensure_ready()

        try:
            data = json.loads(self.events_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

        return data if isinstance(data, list) else []

    def save_events(self, events: list[dict[str, Any]]) -> None:
        self.ensure_ready()
        self.events_path.write_text(
            json.dumps(events, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def append_event(self, event: dict[str, Any]) -> None:
        events = self.load_events()
        events.append(event)
        self.save_events(events)

    def load_profile(self) -> dict[str, Any]:
        self.ensure_ready()

        try:
            data = json.loads(self.profile_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

        return data if isinstance(data, dict) else {}

    def save_profile(self, profile: dict[str, Any]) -> None:
        self.ensure_ready()
        self.profile_path.write_text(
            json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
