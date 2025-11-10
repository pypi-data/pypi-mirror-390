import statistics, datetime, os, json

def reinforce(memory, key):
    if key in memory:
        m = memory[key]
        m["score"] = min(1.0, float(m.get("score", 0.5)) + 0.05)
        m["count"] = int(m.get("count", 0)) + 1
        m["last_used"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_insights(memory):
    total = len(memory)
    if total == 0:
        return "📭 Memory empty."
    # most recalled
    sorted_by_count = sorted(memory.items(), key=lambda x: int(x[1].get("count", 0)), reverse=True)
    top_key = sorted_by_count[0][0]
    avg_conf = statistics.mean([float(v.get("score", 0.5)) for v in memory.values()])
    return (
        "📊 Insight Summary:\n"
        f"- Total entries: {total}\n"
        f"- Most recalled: {top_key} ({sorted_by_count[0][1].get('count',0)}x)\n"
        f"- Average confidence: {avg_conf:.2f}"
    )

def stats_summary(memory, memory_path, remote_mode):
    size = 0
    try:
        size = os.path.getsize(memory_path)
    except Exception:
        pass
    return (
        "🧪 Stats:\n"
        f"- Entries: {len(memory)}\n"
        f"- Memory file: {memory_path} ({size} bytes)\n"
        f"- Remote mode: {remote_mode}"
    )
