import os
import re

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
patterns = [
    r"data/processed",
    r"processed/train",
    r"processed/dev",
    r"processed/test",
    r"data/benchmark",
    r"v2/train\.jsonl",
    r"v2/dev\.jsonl",
    r"v2/benchmark\.jsonl",
    r"train\.jsonl",
    r"dev\.jsonl",
    r"benchmark\.jsonl"
]
combined_regex = re.compile("|".join(patterns), re.IGNORECASE)

# Ignored directories
ignored_dirs = {".venv", ".git", "__pycache__", "reports", "v2", "v2_frozen", "data"}

results = []

for root, dirs, files in os.walk(base_dir):
    dirs[:] = [d for d in dirs if d not in ignored_dirs]
    for file in files:
        if file.endswith((".py", ".ipynb", ".md", ".yaml", ".yml", ".sh", ".ps1", "Makefile")):
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, base_dir).replace("\\", "/")
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for lnum, line in enumerate(f, 1):
                        m = combined_regex.search(line)
                        if m:
                            results.append({
                                "file": relpath,
                                "line": lnum,
                                "match": m.group(0),
                                "snippet": line.strip()
                            })
            except Exception as e:
                pass

out_path = os.path.join(base_dir, "reports", "verification", "path_audit.md")
os.makedirs(os.path.dirname(out_path), exist_ok=True)

with open(out_path, "w", encoding="utf-8") as f:
    f.write("# Path Audit Report: Old & Hard-Coded Data Paths\n\n")
    f.write("**Date:** 2026-10-21  \n")
    f.write("**Auditor:** Senior ML Engineer  \n")
    f.write(f"**Total Occurrences Found:** {len(results)}\n\n")
    f.write("| # | File | Line | Matched Pattern | Code Snippet |\n")
    f.write("| :--- | :--- | :---: | :--- | :--- |\n")
    for idx, r in enumerate(results, 1):
        clean_snippet = r["snippet"].replace("|", "\\|").replace("`", "'")
        full_p = os.path.join(base_dir, r['file']).replace('\\', '/')
        f.write(f"| {idx} | [`{r['file']}`](file:///{full_p}#L{r['line']}) | {r['line']} | `{r['match']}` | `{clean_snippet[:100]}` |\n")

print(f"Audit complete. Found {len(results)} matches. Saved to {out_path}")
