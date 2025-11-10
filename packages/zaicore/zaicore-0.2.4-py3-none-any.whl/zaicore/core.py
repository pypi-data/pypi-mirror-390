import json, os, datetime
from .utils.data_handler import load_memory, save_memory, load_config
from .reasoning import get_best_match
from .analytics import reinforce, calculate_insights, stats_summary
from .network import upload_memory, download_memory


class ZAICore:
    """
    ZAI Core v0.2.4 — Adaptive Intelligence
    - Persistent memory (JSON)
    - Auto-learn (optional)
    - Reinforcement (score/last_used)
    - Insights & stats
    - Optional remote sync
    - Config from zai_config.json (if exists)
    """

    def __init__(self, memory_path="zai_memory.json",
                 remote_mode=False, remote_url=None, auto_learn=True):
        # Load config file (overrides defaults if present)
        cfg = load_config()
        self.memory_path = memory_path
        self.remote_mode = cfg.get("remote_mode", remote_mode)
        self.remote_url  = cfg.get("remote_url", remote_url)
        self.auto_learn  = cfg.get("auto_learn", auto_learn)

        self.memory = load_memory(self.memory_path)

        # Optional remote merge
        if self.remote_mode and self.remote_url:
            print("🌐 Loading remote memory ...")
            remote_data = download_memory(self.remote_url)
            if remote_data:
                # Merge: remote wins only for new keys
                for k, v in remote_data.items():
                    if k not in self.memory:
                        self.memory[k] = v

        print("🧠 ZAI Core v0.2.4 initialized — Adaptive Intelligence Online.")

    # ------------------ Core Learning ------------------

    def learn(self, key, value):
        key = key.strip().lower()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = self.memory.get(key, {"count": 0, "score": 0.5})
        entry.update({
            "value": value,
            "learned_at": now,
            "count": entry.get("count", 0) + 1
        })
        self.memory[key] = entry
        self._save()
        print(f"[Learning] {key} → {value}")

    def recall(self, query):
        query = query.lower().strip()
        match = get_best_match(query, list(self.memory.keys()))
        if match:
            val = self.memory[match].get("value")
            reinforce(self.memory, match)
            self._save()
            print(f"[Recall] {match}: {val}")
            return val
        # Auto-learn pending entry
        if self.auto_learn:
            self._create_pending(query)
            print("🤖 I don't know that yet. Saved as pending knowledge.")
        else:
            print("🤖 I don't know that yet.")
        return None

    def list_memory(self):
        if not self.memory:
            print("📭 Memory is empty.")
            return
        print("🧩 Memory Overview:")
        for k, v in self.memory.items():
            value = v.get("value")
            cnt = v.get("count", 0)
            sc  = v.get("score", 0.5)
            lu  = v.get("last_used", "-")
            print(f"- {k}: {value} (count {cnt}, score {sc:.2f}, last_used {lu})")

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

    # ------------------ Insights / Stats / Config ------------------

    def insights(self):
        print(calculate_insights(self.memory))

    def stats(self):
        print(stats_summary(self.memory, self.memory_path, self.remote_mode))

    def show_config(self):
        data = {
            "memory_path": self.memory_path,
            "remote_mode": self.remote_mode,
            "remote_url": self.remote_url,
            "auto_learn": self.auto_learn
        }
        print(json.dumps(data, indent=2))

    def set_config(self, key, value):
        key = key.lower().strip()
        if key == "remote_mode":
            self.remote_mode = (str(value).lower() in ["1", "true", "yes", "on"])
        elif key == "remote_url":
            self.remote_url = str(value)
        elif key == "auto_learn":
            self.auto_learn = (str(value).lower() in ["1", "true", "yes", "on"])
        else:
            print("❌ Unknown config key. Use: remote_mode | remote_url | auto_learn")
            return
        print(f"[Config] {key} set to {value}")

    # ------------------ Internals ------------------

    def _create_pending(self, query):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if query not in self.memory:
            self.memory[query] = {
                "value": "pending",
                "learned_at": now,
                "count": 0,
                "score": 0.4
            }
            self._save()

    def _save(self):
        save_memory(self.memory, self.memory_path)
        if self.remote_mode and self.remote_url:
            upload_memory(self.memory, self.remote_url)
