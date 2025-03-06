import os
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


def main():
    subdirectories = get_files('./model_fs')
    paths = generate_paths(subdirectories)
    # if "B/a/A/b" in paths:
    #     print("Found B/a/A/b")

    with open('fs_paths.txt', 'w') as file:
        for path in paths:
            file.write(path + '\n')


if __name__ == "__main__":
    main()
    