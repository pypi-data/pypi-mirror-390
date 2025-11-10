class ZAICore:
    def __init__(self):
        self.memory = {}
        print("🧠 ZAI Core initialized — AI brain is online.")

    def learn(self, key, value):
        """Simulate learning by storing key-value pairs."""
        self.memory[key] = value
        print(f"[Learning] Stored: {key} -> {value}")

    def recall(self, key):
        """Recall learned information."""
        response = self.memory.get(key, "I don't know that yet.")
        print(f"[Recall] {key}: {response}")
        return response

if __name__ == "__main__":
    ai = ZAICore()
    ai.learn("name", "Zaidan AI")
    ai.recall("name")
