from .core import ZAICore

def main():
    print("🚀 Launching ZAI Core v0.2.0 — CLI Mode")
    ai = ZAICore()
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("🧠 > ").strip()

        if not user_input:
            continue

        command_parts = user_input.split(" ", 1)
        command = command_parts[0].lower()
        args = command_parts[1].strip() if len(command_parts) > 1 else ""

        if command in ["exit", "quit"]:
            print("👋 Shutting down ZAI Core...")
            break

        elif command == "learn":
            if "=" in args:
                key, value = args.split("=", 1)
                ai.learn(key.strip(), value.strip())
            else:
                print("❌ Format salah! Gunakan: learn key=value")

        elif command == "recall":
            if args:
                ai.recall(args)
            else:
                print("❌ Gunakan: recall <key>")

        elif command == "forget":
            if args:
                ai.forget(args)
            else:
                print("❌ Gunakan: forget <key>")

        elif command == "wipe":
            ai.wipe_memory()

        else:
            print("❓ Perintah tidak dikenal. Gunakan: learn / recall / forget / wipe / exit")


if __name__ == "__main__":
    main()
