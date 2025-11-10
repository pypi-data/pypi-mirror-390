import json, os, datetime
from .utils.data_handler import load_memory, save_memory
from .reasoning import get_best_match


class ZAICore:
    def __init__(self, memory_path="zai_memory.json"):
        self.memory_path = memory_path
        self.memory = load_memory(memory_path)
        print("🧠 ZAI Core v0.2.2 initialized — Cognitive Layer Online.")

    def learn(self, key, value):
        """Store new information permanently."""
        key = key.strip().lower()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if key not in self.memory:
            self.memory[key] = {"value": value, "learned_at": now, "count": 1}
        else:
            self.memory[key]["value"] = value
            self.memory[key]["count"] += 1

        save_memory(self.memory, self.memory_path)
        print(f"[Learning] Stored: {key} -> {value}")

    def recall(self, query):
        """Smart recall: answer questions or recall by keyword."""
        query = query.lower().strip()
        match = get_best_match(query, list(self.memory.keys()))
        if match:
            data = self.memory[match]
            print(f"[Recall] {match}: {data['value']}")
            return data["value"]
        else:
            print("🤖 I don't have knowledge about that yet.")
            return None

    def list_memory(self):
        """Show all stored memories."""
        if not self.memory:
            print("📭 Memory is empty.")
            return
        print("🧩 Memory Overview:")
        for k, v in self.memory.items():
            print(f"- {k} : {v['value']} (learned {v['count']}x, last at {v['learned_at']})")

    def forget(self, key):
        """Delete specific memory entry."""
        key = key.lower().strip()
        if key in self.memory:
            del self.memory[key]
            save_memory(self.memory, self.memory_path)
            print(f"[Forget] Key '{key}' removed from memory.")
        else:
            print(f"[Forget] No data found for key: '{key}'")

    def wipe_memory(self):
        """Erase all stored data."""
        self.memory = {}
        save_memory(self.memory, self.memory_path)
        print("🧹 All memory wiped clean.")
