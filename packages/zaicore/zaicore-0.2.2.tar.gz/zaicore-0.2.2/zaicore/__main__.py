from .core import ZAICore

def main():
    import sys
    chat_mode = "--chat" in sys.argv

    ai = ZAICore()
    print("🚀 Launching ZAI Core CLI — Cognitive Mode")
    print("Type 'help' for commands, or 'exit' to quit.\n")

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
        elif command == "help":
            print("Commands: learn key=value | recall <key/question> | list | rm <key> | wipe | info | chat | exit")
        elif command == "learn":
            if "=" in args:
                key, value = args.split("=", 1)
                ai.learn(key.strip(), value.strip())
            else:
                print("❌ Format: learn key=value")
        elif command in ["recall", "ask"]:
            ai.recall(args)
        elif command in ["list", "ls"]:
            ai.list_memory()
        elif command in ["forget", "rm"]:
            ai.forget(args)
        elif command == "wipe":
            ai.wipe_memory()
        elif command == "info":
            print("ZAI Core — Cognitive Layer v0.2.2 | Memory File: zai_memory.json")
        elif chat_mode or command == "chat":
            print("🤖 Entering Chat Mode (type 'exit' to leave)")
            while True:
                msg = input("💬 You: ").strip()
                if msg.lower() in ["exit", "quit"]:
                    print("🧠 Exiting Chat Mode...")
                    break
                ai.recall(msg)
        else:
            ai.recall(user_input)

if __name__ == "__main__":
    main()
