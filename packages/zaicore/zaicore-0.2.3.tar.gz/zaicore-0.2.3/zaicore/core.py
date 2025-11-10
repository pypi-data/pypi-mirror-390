import json, os, datetime
from .utils.data_handler import load_memory, save_memory
from .reasoning import get_best_match
from .network import upload_memory, download_memory

class ZAICore:
    def __init__(self, memory_path="zai_memory.json",
                 remote_mode=False, remote_url=None):
        self.memory_path = memory_path
        self.remote_mode = remote_mode
        self.remote_url = remote_url
        self.memory = load_memory(memory_path)

        if self.remote_mode and self.remote_url:
            print("🌐 Loading remote memory ...")
            remote_data = download_memory(self.remote_url)
            if remote_data:
                self.memory.update(remote_data)

        print("🧠 ZAI Core v0.2.3 initialized — Networked Intelligence Online.")

    # ------------------ Core Learning ------------------

    def learn(self, key, value):
        key = key.strip().lower()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = self.memory.get(key, {"count": 0})
        entry.update({"value": value, "learned_at": now,
                      "count": entry["count"] + 1})
        self.memory[key] = entry
        self._save()
        print(f"[Learning] {key} → {value}")

    def recall(self, query):
        query = query.lower().strip()
        match = get_best_match(query, list(self.memory.keys()))
        if match:
            val = self.memory[match]["value"]
            print(f"[Recall] {match}: {val}")
            return val
        print("🤖 I don’t know that yet.")
        return None

    def list_memory(self):
        if not self.memory:
            print("📭 Memory is empty.")
            return
        print("🧩 Memory Overview:")
        for k, v in self.memory.items():
            print(f"- {k}: {v['value']} (learned {v['count']}×, last {v['learned_at']})")

    def forget(self, key):
        key = key.lower().strip()
        if key in self.memory:
            del self.memory[key]
            self._save()
            print(f"[Forget] {key} deleted.")
        else:
            print(f"[Forget] No such key: {key}")

    def wipe_memory(self):
        self.memory = {}
        self._save()
        print("🧹 All memory wiped clean.")

    # ------------------ Internal Helpers ------------------

    def _save(self):
        save_memory(self.memory, self.memory_path)
        if self.remote_mode and self.remote_url:
            upload_memory(self.memory, self.remote_url)
