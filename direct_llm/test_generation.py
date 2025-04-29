import string
import json

def generate_invalid_schemes():
    """
    Return a list of invalid schemes. A valid scheme (per RFC 3986) should:
      - Start with a letter
      - Followed by letters, digits, '+', '-', or '.'
    We'll systematically break these rules.
    """
    invalid_schemes = []

    # Empty scheme
    invalid_schemes.append("")

    # Starts with a digit
    invalid_schemes.append("1http")

    # Contains invalid characters (spaces, '@', '/', etc.)
    invalid_schemes.append("ht tp")
    invalid_schemes.append("ht@tp")
    invalid_schemes.append("ht/tp")

    # Only punctuation
    invalid_schemes.append("!!!")

    # Contains uppercase letters beyond standard allowance
    # (Although uppercase letters are allowed, let's add a random invalid char)
    invalid_schemes.append("HTTP:")

    # Leading hyphen
    invalid_schemes.append("-http")

    return invalid_schemes


def generate_invalid_authorities():
    """
    Return a list of invalid authorities. A valid authority might look like:
      userinfo@host:port
    Where 'host' (like example.com or an IP) must not be empty, etc.
    We'll break these in different ways.
    """
    invalid_authorities = []

    # Empty authority
    invalid_authorities.append("")

    # Missing host after userinfo
    invalid_authorities.append("user@")

    # Invalid port (non-digit)
    invalid_authorities.append("example.com:port")

    # Extra colon
    invalid_authorities.append("example.com::80")

    # Spaces
    invalid_authorities.append("exam ple.com")

    # Invalid characters
    invalid_authorities.append("exa#mple.com")

    # Just a colon (missing host)
    invalid_authorities.append(":")

    # Leading/trailing dot
    invalid_authorities.append(".example.com.")
    
    return invalid_authorities


def generate_invalid_paths():
    """
    Return a list of invalid paths. A valid path can contain many characters,
    but certain characters must be percent-encoded (spaces, #, etc.).
    We'll add some systematically invalid examples.
    """
    invalid_paths = []

    # Path with space
    invalid_paths.append("/this is/invalid")

    # Unescaped control character
    invalid_paths.append("/this/\x00/path")

    # Invalid path with unescaped hash (should be used for fragment)
    invalid_paths.append("/this/is#notallowed")

    # Double question marks messing up path
    invalid_paths.append("/this??/something")

    # Empty path is technically valid if is the entire path segment, 
    # but let's say we produce something obviously malformed:
    invalid_paths.append(" //leading-slash")

    return invalid_paths


def generate_invalid_queries():
    """
    Return a list of invalid queries. A valid query can contain many characters,
    but certain characters must be percent-encoded, and we do not usually embed
    spaces unencoded. Let's systematically produce some invalid ones.
    """
    invalid_queries = []

    # Query with space
    invalid_queries.append("?q=hello world")

    # Unescaped '#' in query
    invalid_queries.append("?q=abc#def")

    # Control character
    invalid_queries.append("?q=abc\x1fdef")

    # Only question marks
    invalid_queries.append("???")

    # Leading '=' with no parameter name
    invalid_queries.append("?=value")

    # Contains newline
    invalid_queries.append("?q=line1\nline2")

    return invalid_queries


def generate_invalid_fragments():
    """
    Return a list of invalid fragments. A valid fragment follows '#' and can
    contain many characters, but certain ones require percent-encoding,
    and control characters are disallowed. We'll produce some invalid examples.
    """
    invalid_fragments = []

    # Fragment with space
    invalid_fragments.append("#some section")

    # Contains control character
    invalid_fragments.append("#section\x08")

    # Contains unescaped slash that might confuse path
    invalid_fragments.append("#/this/looks/like/path")

    # Only '#' with nothing else (not necessarily invalid from a strict RFC standpoint,
    # but we can still turn it into a test)
    invalid_fragments.append("#")

    # Contains newline
    invalid_fragments.append("#section\n1")

    return invalid_fragments


def build_test_case(component_name, bad_value,
                    scheme="http",
                    authority="example.com",
                    path="/this/is/valid",
                    query="?q=test",
                    fragment="#section-1"):
    """
    Build a URI test case dict, substituting the 'bad_value' into the specified 'component_name'.
    Return the dictionary of URI components.
    """
    test_case = {
        "scheme": scheme,
        "authority": authority,
        "path": path,
        "query": query,
        "fragment": fragment,
        "reason": "Invalid " + component_name
    }

    # Overwrite the component with the invalid piece
    if component_name == "scheme":
        test_case["scheme"] = bad_value
    elif component_name == "authority":
        test_case["authority"] = bad_value
    elif component_name == "path":
        test_case["path"] = bad_value
    elif component_name == "query":
        test_case["query"] = bad_value
    elif component_name == "fragment":
        test_case["fragment"] = bad_value

    return test_case


def generate_uri_test_cases():
    """
    Generate a systematic set of test URIs, each one violating a single constraint
    in the scheme, authority, path, query, or fragment.
    Returns a list of test cases, each one a dict of URI components.
    """

    test_cases = []

    # For each invalid scheme
    for invalid_value in generate_invalid_schemes():
        test_cases.append(build_test_case("scheme", invalid_value))

    # For each invalid authority
    for invalid_value in generate_invalid_authorities():
        test_cases.append(build_test_case("authority", invalid_value))

    # For each invalid path
    for invalid_value in generate_invalid_paths():
        test_cases.append(build_test_case("path", invalid_value))

    # For each invalid query
    for invalid_value in generate_invalid_queries():
        test_cases.append(build_test_case("query", invalid_value))

    # For each invalid fragment
    for invalid_value in generate_invalid_fragments():
        test_cases.append(build_test_case("fragment", invalid_value))

    return test_cases


if __name__ == "__main__":
    all_test_cases = generate_uri_test_cases()
    with open("llm_tests_5.json", "w", encoding="utf-8") as f:
        json.dump(all_test_cases, f, indent=4, ensure_ascii=False)