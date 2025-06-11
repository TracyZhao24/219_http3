import re
from urllib.parse import unquote

def is_valid_uri_test_case(test_case):
    """
    Returns True if the test case satisfies URI validity constraints, else False.
    """
    # Extract fields
    scheme = test_case.get("scheme", "")
    authority = test_case.get("authority", "")
    path = test_case.get("path", "")
    query = test_case.get("query", "")
    fragment = test_case.get("fragment", "")

    # 1. Scheme must be http or https
    if scheme not in {"http", "https"}:
        return False

    # 2. Authority must be a non-empty valid hostname (basic check)
    if not authority or not re.match(r"^[a-zA-Z0-9.-]+(:[0-9]+)?$", authority):
        return False

    # 3. Path must start with /
    if not path.startswith("/"):
        return False

    # 4. Check for invalid percent-encoding
    if re.search(r"%(?![0-9A-Fa-f]{2})", path + query + fragment):
        return False

    # 5. Decoded path must not contain null bytes or control characters
    try:
        decoded_path = unquote(path)
    except Exception:
        return False
    if '\x00' in decoded_path or any(ord(c) < 32 for c in decoded_path):
        return False

    # 6. Path length limit (conservative upper bound used by some servers, e.g., 2048)
    if len(path) > 2048:
        return False

    # 7. Prevent directory traversal beyond root (e.g., /../../..)
    segments = path.split('/')
    depth = 0
    for seg in segments:
        if seg == "..":
            depth -= 1
        elif seg and seg != ".":
            depth += 1
    if depth < 0:
        return False

    # 8. Reject unescaped reserved characters in path
    if re.search(r"[ \t\r\n?#]", path):  # Unescaped space, tab, newline, ?, #
        return False

    return True

if __name__ == "__main__":
    # Example test case
    test_case = {
        "scheme": "http",
        "authority": "example.com",
        "path": "%00",
        "query": "",
        "fragment": ""
    }

    print(is_valid_uri_test_case(test_case))  # Should return False due to null byte in path