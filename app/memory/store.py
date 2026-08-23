import json
from pathlib import Path


MEMORY_FILE = Path(__file__).resolve().parent / "memory.json"


class MemoryStore:
    def __init__(self):
        self.file = MEMORY_FILE
        self.data = self._load()

    def _load(self):
        if not self.file.exists():
            return {}

        try:
            with self.file.open(
                "r",
                encoding="utf-8",
            ) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self):
        with self.file.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.data,
                f,
                indent=2,
                ensure_ascii=False,
            )

    def remember(self, key: str, value: str) -> str:
        self.data[key.lower().strip()] = value.strip()
        self._save()

        return f"I'll remember that {key} is {value}."

    def recall(self, key: str) -> str:
        key = key.lower().strip()

        value = self.data.get(key)

        if value is None:
            return f"I don't remember anything about {key}."

        return f"{key} is {value}."

    def forget(self, key: str) -> str:
        key = key.lower().strip()

        if key not in self.data:
            return f"I wasn't remembering anything about {key}."

        del self.data[key]
        self._save()

        return f"I forgot {key}."

    def all_memory(self) -> dict:
        return dict(self.data)