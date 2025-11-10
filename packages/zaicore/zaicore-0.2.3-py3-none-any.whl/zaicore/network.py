import json, requests

def upload_memory(data, endpoint):
    """Upload memory dictionary to remote API endpoint."""
    try:
        requests.post(endpoint, json=data, timeout=5)
        print("🌐 Memory synced remotely.")
    except Exception as e:
        print("⚠️  Remote sync failed:", e)

def download_memory(endpoint):
    """Download memory data from remote API endpoint."""
    try:
        res = requests.get(endpoint, timeout=5)
        if res.status_code == 200:
            print("⬇️  Remote memory downloaded.")
            return res.json()
    except Exception as e:
        print("⚠️  Remote load failed:", e)
    return {}
