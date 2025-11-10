import difflib

def get_best_match(query, keys):
    """Find best matching memory key for a question or phrase."""
    if not keys:
        return None
    best = difflib.get_close_matches(query, keys, n=1, cutoff=0.4)
    if best:
        return best[0]
    for k in keys:
        if k in query:
            return k
    return None
