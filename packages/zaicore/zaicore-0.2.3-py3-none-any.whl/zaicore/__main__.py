from .core import ZAICore

def main():
    import sys
    chat_mode = "--chat" in sys.argv
    ai = ZAICore(remote_mode="--remote" in sys.argv,
                 remote_url="https://example.com/zai_core_api")

    print("🚀 ZAI Core CLI v0.2.3 — Networked Intelligence Mode")
    print("Type 'help' or 'exit'.")

    while True:
        user = input("🧠 > ").strip()
        if not user:
            continue
        cmd, *args = user.split(" ", 1)
        arg = args[0] if args else ""

        if cmd in ["exit", "quit"]:
            print("👋 Bye.")
            break
        elif cmd == "help":
            print("Commands: learn key=value | recall <key> | list | rm <key> | wipe | status")
        elif cmd == "learn" and "=" in arg:
            k, v = arg.split("=", 1)
            ai.learn(k, v)
        elif cmd in ["recall", "ask"]:
            ai.recall(arg)
        elif cmd in ["list", "ls"]:
            ai.list_memory()
        elif cmd in ["forget", "rm"]:
            ai.forget(arg)
        elif cmd == "wipe":
            ai.wipe_memory()
        elif cmd == "status":
            print(f"ZAI Core v0.2.3 | Remote: {ai.remote_mode} | Entries: {len(ai.memory)}")
        else:
            ai.recall(user)

if __name__ == "__main__":
    main()
