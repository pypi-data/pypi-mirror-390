import difflib

def get_best_match(query, keys):
    if not keys:
        return None
    best = difflib.get_close_matches(query, keys, n=1, cutoff=0.45)
    if best:
        return best[0]
    # fallback: substring
    for k in keys:
        if k in query or query in k:
            return k
    return None
