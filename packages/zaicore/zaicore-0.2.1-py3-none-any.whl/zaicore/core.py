import json
import os
from .utils.data_handler import load_memory, save_memory


class ZAICore:
    def __init__(self, memory_path="zai_memory.json"):
        self.memory_path = memory_path
        self.memory = load_memory(memory_path)
        print("🧠 ZAI Core v0.2.0 initialized — Persistent Brain Online.")

    def learn(self, key, value):
        """Store new information permanently."""
        self.memory[key] = value
        save_memory(self.memory, self.memory_path)
        print(f"[Learning] Stored: {key} -> {value}")

    def recall(self, key):
        """Retrieve learned information."""
        if key in self.memory:
            print(f"[Recall] {key}: {self.memory[key]}")
            return self.memory[key]
        else:
            print(f"[Recall] No data found for key: '{key}'")
            return None

    def forget(self, key):
        """Delete specific memory entry."""
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
