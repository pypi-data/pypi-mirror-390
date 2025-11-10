from .core import ZAICore

def main():
    import sys
    flags = set(sys.argv[1:])
    ai = ZAICore(
        remote_mode=("--remote" in flags),
        remote_url=None,  # override pakai zai_config.json
        auto_learn=True
    )

    print("🚀 ZAI Core CLI v0.2.4 — Adaptive Intelligence")
    print("Type 'help' for commands, 'exit' to quit.\n")

    while True:
        try:
            user = input("🧠 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye.")
            break
        if not user:
            continue

        parts = user.split(" ", 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ["exit", "quit"]:
            print("👋 Bye.")
            break
        elif cmd == "help":
            print("Commands:")
            print("  learn key=value     -> store knowledge")
            print("  recall <query>      -> smart recall / Q&A")
            print("  list | ls           -> show memory")
            print("  rm <key>            -> delete key")
            print("  wipe                -> wipe all memory")
            print("  insights            -> show insight summary")
            print("  stats               -> show engine stats")
            print("  config              -> show config")
            print("  set <k>=<v>         -> set config (remote_mode/remote_url/auto_learn)")
        elif cmd == "learn" and "=" in arg:
            k, v = arg.split("=", 1)
            ai.learn(k, v)
        elif cmd in ["recall", "ask"]:
            ai.recall(arg)
        elif cmd in ["list", "ls"]:
            ai.list_memory()
        elif cmd == "rm":
            ai.forget(arg)
        elif cmd == "wipe":
            ai.wipe_memory()
        elif cmd == "insights":
            ai.insights()
        elif cmd == "stats":
            ai.stats()
        elif cmd == "config":
            ai.show_config()
        elif cmd == "set" and "=" in arg:
            k, v = arg.split("=", 1)
            ai.set_config(k, v)
        else:
            # fallback: treat any text as a question
            ai.recall(user)

if __name__ == "__main__":
    main()
