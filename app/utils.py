from urllib.parse import unquote

def decode_url_param(param: str) -> str:
    """Decode URL-encoded parameter and normalize"""
    decoded = unquote(param)
    # Normalize spaces (handle both %20 and +)
    normalized = decoded.replace('+', ' ').strip()
    return normalized.lower()

def normalize_query(query: str) -> str:
    """Normalize user query"""
    return query.lower().strip()
