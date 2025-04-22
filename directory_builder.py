import os

# Base directory where the site will live
BASE_DIR = "/Users/tracyzhao/Desktop/219_project/html"

# Files to create with content
files = {
    "index.html": "index",
    "path/to/resource.html": "resource",
    "encoded%20path/space.html": "space",
    "a/b/c.html": "deep",
    "weird_chars/file@name.html": "weird",
    "redirect/target.html": "redirect target",
}

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(path, content):
    with open(path, "w") as f:
        f.write(f"<html><body>FILE: {content}</body></html>\n")

def main():
    print(f"Creating URI test site in '{BASE_DIR}'...\n")

    for rel_path, content in files.items():
        full_path = os.path.join(BASE_DIR, rel_path)
        dir_path = os.path.dirname(full_path)
        ensure_dir(dir_path)
        write_file(full_path, content)
        print(f"Created {full_path}")

    print("\n URI test site layout complete.")

if __name__ == "__main__":
    main()