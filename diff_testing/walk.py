import os
import json
import itertools

def get_files(root_path):
    subdirs = set()

    for dirpath, dirnames, filenames in os.walk(root_path):
        subdirs.update(dirnames, filenames)

    return subdirs


def generate_paths(levels, limit = 4):
    levels.discard('.DS_Store') 
    # add current directory and parent directory
    levels.add('.')
    levels.add('..')

    paths = set()

    # generate all paths with depth up to limit
    for depth in range(1, limit + 1):
        for combination in itertools.product(levels, repeat=depth):
            path = os.path.join(*combination)
            paths.add(path)

    return paths


def create_test_cases(subdirectories):
    paths = generate_paths(subdirectories, limit = 4)
    bases = generate_paths(subdirectories, limit = 2)

    tests = []

    for base in bases:
        base_url = "http://localhost:8080/" + base
        for path in paths:
            tests.append({
                "base_uri": base_url,
                "relative_uri": path
            })

    return tests


def main():
    subdirectories = get_files('./model_fs')
    # base_url = "http://localhost:8080"

    tests = create_test_cases(subdirectories)

    with open('fs_relative_paths.json', 'w') as file:
        json.dump(tests, file, indent=4)


if __name__ == "__main__":
    main()
    