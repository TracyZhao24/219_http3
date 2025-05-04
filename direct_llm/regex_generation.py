import rstr
import re
import random
import json

# === REGEX DEFINITIONS FOR COMPONENTS ===
SCHEME_REGEX = r'^[A-Za-z][A-Za-z0-9+.-]*$'
AUTHORITY_REGEX = r"^(?:(?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=]|:)+@)?(?:\[(?:[0-9A-Fa-f:.]+)\]|(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}|(?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=])*- )(?::\d*)?$"
PATH_REGEX = r"^(?:/(?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=:@]))*$"
QUERY_REGEX = r"^(?:[A-Za-z0-9\-._~]|%[0-9A-Fa-f]{2}|[!$&'()*+,;=:@\/?])*$"
FRAGMENT_REGEX = QUERY_REGEX  # Same character rules

compiled_patterns = {
    "scheme": re.compile(SCHEME_REGEX),
    "authority": re.compile(AUTHORITY_REGEX),
    "path": re.compile(PATH_REGEX),
    "query": re.compile(QUERY_REGEX),
    "fragment": re.compile(FRAGMENT_REGEX),
}

component_to_regex = {
    "scheme": SCHEME_REGEX,
    "authority": AUTHORITY_REGEX,
    "path": PATH_REGEX,
    "query": QUERY_REGEX,
    "fragment": FRAGMENT_REGEX,
}

def generate_valid_component(component_name):
    """
    Generate a valid component based on the provided component name.
    """
    if component_name not in component_to_regex:
        raise ValueError(f"Unknown component: {component_name}")

    regex = component_to_regex[component_name]
    
    # Use rstr to generate a random string that matches the regex
    generated_string = rstr.xeger(regex)
    
    # Validate the generated string
    if not compiled_patterns[component_name].match(generated_string):
        raise ValueError(f"Generated string '{generated_string}' does not match {component_name} regex.")
    
    return generated_string


def mutate_component(component, component_name):
    mutations = []
    
    # interesting ASCII and Unicode characters
    invalid_chars = [' ', '%00', '\x00', '\\', '`', '^', '/', 'é', 'Σ', '€', '$', '%25', '%', '?', '@', '#', '-']

    for ch in invalid_chars:
        pos = random.randint(0, len(component))
        invalid_insert = component[:pos] + ch + component[pos:]
        mutations.append(invalid_insert)

    # corrupt directory traversals
    mutations.append(component.replace('./', '../'))
    mutations.append(component.replace('..', '...'))
    mutations.append(component.replace('.', '...'))

    # corupt percent encodings
    mutations.append(component.replace('%', '%Z'))

    if component_name == "scheme":
        mutations.append("1" + component)
        mutations.append("-" + component)
        mutations.append("." + component)
        mutations.append("b-")
        mutations.append("a.")

    if component_name == "path":
        # Corrupt path separators
        mutations.append(component.replace('/', '\\'))
        mutations.append(component.replace('\\', '/'))
        mutations.append(component.replace('/', '//'))
        # directory traversal
        mutations.append(component.replace('/', '/../../../../../../../../'))
    
    if component_name == "query":
        mutations.append("?")
        mutations.append("??")
        mutations.append("?=value")
        mutations.append("?name=")
        mutations.append("?name=value&")
        mutations.append("?x=1%262")


    return mutations


def generate_tests():
    valid_uri = {
        "scheme": generate_valid_component("scheme"),
        "authority": generate_valid_component("authority"),
        "path": generate_valid_component("path"),
        "query": generate_valid_component("query"),
        "fragment": generate_valid_component("fragment"),
    }

    tests = []
    for name, value in valid_uri.items():
        mutations = mutate_component(value, name)
        for mutation in mutations:
            test_case = valid_uri.copy()
            test_case[name] = mutation
            test_case["reason"] = f"Corrupted {name}"
            tests.append(test_case)
    
    return tests


if __name__ == "__main__":
    all_test_cases = generate_tests()

    with open("regex_test_1.json", "w", encoding="utf-8") as f:
        json.dump(all_test_cases, f, indent=4, ensure_ascii=False)