import random
import string
import urllib.parse
import json

def gen_scheme():
    valid = "http"
    violations = ["ht+tp", "HTTP", "hTtp", "", "123", "ftp"]
    return valid, violations

def gen_host():
    valid = "example.com"
    violations = [
        "exa..com",             # empty label
        "-example.com",         # leading hyphen
        "example-.com",         # trailing hyphen
        "exämple.com",          # unicode
        "127.0.0.999",          # invalid IPv4
        "[2001::zzz]"           # malformed IPv6
    ]
    return valid, violations

def gen_port():
    valid = "80"
    violations = ["0", "65536", "-1", "abc", "", " "]
    return valid, violations

def gen_userinfo():
    valid = ""
    violations = ["user@", "user:pass@", "admin:password@", "u$er:pa@ss@"]
    return valid, violations

def gen_path():
    valid = "/path/to/resource"
    violations = [
        "/a/b/../../../..",       # path escapes root
        "/..☃/file",              # unicode in segment
        "/a//b//c",               # double slashes
        "/abc%2G",                # invalid percent encoding
        "/" + "a"*10000           # overly long
    ]
    return valid, violations

def gen_query():
    valid = "key=value"
    violations = [
        "key==value",             # extra equals
        "key value",              # unescaped space
        "💥=boom",                # unicode
        "a=%2G",                  # bad percent encoding
        "a=" + "x"*5000           # long value
    ]
    return valid, violations

def gen_fragment():
    valid = "section"
    violations = ["frag#extra", "frag%2Z", "☃section"] 
    return valid, violations

def gen_scheme_specific_part(host, port, path, query, fragment, userinfo=""):
    authority = f"{userinfo}{host}:{port}"
    uri = f"http://{authority}{path}"
    if query: uri += f"?{query}"
    if fragment: uri += f"#{fragment}"
    return uri

def generate_uri_test_cases():
    # --- Step 1: Get valid and invalid components ---
    scheme_valid, scheme_invalids = gen_scheme()
    host_valid, host_invalids = gen_host()
    port_valid, port_invalids = gen_port()
    userinfo_valid, userinfo_invalids = gen_userinfo()
    path_valid, path_invalids = gen_path()
    query_valid, query_invalids = gen_query()
    fragment_valid, fragment_invalids = gen_fragment()

    test_cases = []

    # --- Step 2: Add a completely valid URI ---
    valid_uri = gen_scheme_specific_part(
        host=host_valid,
        port=port_valid,
        path=path_valid,
        query=query_valid,
        fragment=fragment_valid,
        userinfo=userinfo_valid
    )
    test_cases.append({
        "type": "valid uri",
        "violation": "N/A",
        "uri": valid_uri
    })

    # --- Step 3: Helper to construct bad URIs ---
    def build_test_case(component_name, bad_value, **kwargs):
        uri = gen_scheme_specific_part(
            host=kwargs.get("host", host_valid),
            port=kwargs.get("port", port_valid),
            path=kwargs.get("path", path_valid),
            query=kwargs.get("query", query_valid),
            fragment=kwargs.get("fragment", fragment_valid),
            userinfo=kwargs.get("userinfo", userinfo_valid)
        )
        # return (f"{component_name} Violation: {bad_value}", uri)
        return ({
                    "type": f"{component_name} violation",
                    "violation": bad_value,
                    "uri": uri
                })

    # --- Step 4: Generate test cases with a single constraint violation ---

    # Scheme violations
    for bad_scheme in scheme_invalids:
        uri = f"{bad_scheme}://{host_valid}:{port_valid}{path_valid}?{query_valid}#{fragment_valid}"
        test_cases.append({
            "type": "scheme violation",
            "violation": bad_scheme,
            "uri": uri
        })

    # Host violations
    for bad_host in host_invalids:
        test_cases.append(build_test_case("Host", bad_host, host=bad_host))

    # Port violations
    for bad_port in port_invalids:
        test_cases.append(build_test_case("Port", bad_port, port=bad_port))

    # Userinfo violations
    for bad_userinfo in userinfo_invalids:
        test_cases.append(build_test_case("Userinfo", bad_userinfo, userinfo=bad_userinfo))

    # Path violations
    for bad_path in path_invalids:
        test_cases.append(build_test_case("Path", bad_path, path=bad_path))

    # Query violations
    for bad_query in query_invalids:
        test_cases.append(build_test_case("Query", bad_query, query=bad_query))

    # Fragment violations
    for bad_fragment in fragment_invalids:
        test_cases.append(build_test_case("Fragment", bad_fragment, fragment=bad_fragment))

    return test_cases

 
if __name__ == "__main__":
    with open('llm_tests_2.json', 'w') as file:
        json.dump(generate_uri_test_cases(), file, indent=4)