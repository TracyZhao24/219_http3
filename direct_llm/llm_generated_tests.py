import urllib.parse
import random
import string
from typing import List

def generate_valid_uri():
    """Generates a valid HTTP URI as a baseline."""
    scheme = "http"
    host = "example.com"
    port = "80"
    path = "/valid/path"
    query = "key=value"
    fragment = "section1"
    return f"{scheme}://{host}:{port}{path}?{query}#{fragment}"

def replace_port(uri: str, new_port: str) -> str:
    parsed = urllib.parse.urlsplit(uri)
    host_part = parsed.hostname or ""
    new_netloc = f"{host_part}:{new_port}"
    return urllib.parse.urlunsplit((parsed.scheme, new_netloc, parsed.path, parsed.query, parsed.fragment))

def replace_host(uri: str, new_host: str) -> str:
    parsed = urllib.parse.urlsplit(uri)
    port_part = f":{parsed.port}" if parsed.port else ""
    new_netloc = f"{new_host}{port_part}"
    return urllib.parse.urlunsplit((parsed.scheme, new_netloc, parsed.path, parsed.query, parsed.fragment))

def replace_path(uri: str, new_path: str) -> str:
    parsed = urllib.parse.urlsplit(uri)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, new_path, parsed.query, parsed.fragment))

def insert_illegal_char(uri: str, component: str, char: str) -> str:
    parsed = urllib.parse.urlsplit(uri)
    if component == "path":
        new_path = parsed.path + char
        return replace_path(uri, new_path)
    elif component == "host":
        new_host = (parsed.hostname or "") + char
        return replace_host(uri, new_host)
    return uri

def generate_violations(base_uri: str) -> List[str]:
    violations = []

    # Port violations
    violations.append(replace_port(base_uri, "-1"))
    violations.append(replace_port(base_uri, "65536"))
    violations.append(replace_port(base_uri, "abcd"))

    # Host violations
    violations.append(replace_host(base_uri, "exa..com"))
    violations.append(replace_host(base_uri, "-example.com"))
    violations.append(insert_illegal_char(base_uri, "host", "💥"))

    # Path violations
    violations.append(replace_path(base_uri, "/a/../.."))
    violations.append(replace_path(base_uri, "/./././"))
    violations.append(replace_path(base_uri, "/abc%2G"))
    violations.append(insert_illegal_char(base_uri, "path", "\u2603"))

    # Long path
    long_path = "/" + "a" * 10000
    violations.append(replace_path(base_uri, long_path))

    return violations

def generate_all_violating_uris():
    base_uri = generate_valid_uri()
    return generate_violations(base_uri)

if __name__ == "__main__":
    uris = generate_all_violating_uris()
    # for uri in uris:
    #     print(uri)
    with open('llm_tests.txt', 'w') as file:
        for uri in uris:
            file.write(uri + "\n")
