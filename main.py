import os

def analyze_directory(path="."):
    total_files = 0
    total_lines = 0
    file_extensions = {}

    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)

            # Skip files in .git and GitHub workflows
            if ".git" in file_path or ".github" in file_path:
                continue

            total_files += 1
            ext = os.path.splitext(file)[1] or "no_ext"
            file_extensions[ext] = file_extensions.get(ext, 0) + 1

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    line_count = sum(1 for _ in f)
                    total_lines += line_count
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")

    return total_files, total_lines, file_extensions


if __name__ == "__main__":
    files, lines, exts = analyze_directory(".")

    print("📊 Repository Analysis")
    print("======================")
    print(f"Total files: {files}")
    print(f"Total lines of code: {lines}")
    print("\nBreakdown by file extension:")
    for ext, count in sorted(exts.items(), key=lambda x: -x[1]):
        print(f"  {ext}: {count} files")
