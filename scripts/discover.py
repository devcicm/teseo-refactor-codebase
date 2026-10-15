#!/usr/bin/env python3
"""Discovery read-only para refactor-codebase v2.3. No modifica el repo."""
from __future__ import annotations
import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "target",
             "bin", "obj", ".venv", "venv", "__pycache__"}
LANG = {
    ".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript",
    ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".jsx": "JavaScript", ".java": "Java", ".cs": "C#",
    ".go": "Go", ".rs": "Rust", ".php": "PHP", ".rb": "Ruby",
    ".cpp": "C++", ".cc": "C++", ".c": "C", ".h": "C/C++",
    ".html": "HTML", ".css": "CSS", ".sql": "SQL",
}
MANIFESTS = {"package.json", "pyproject.toml", "requirements.txt", "go.mod",
             "Cargo.toml", "composer.json", "pom.xml", "Gemfile", "Makefile"}
PATTERNS = {
    "FE-15": re.compile(r"\binnerHTML\s*="),
    "FE-13": re.compile(r"\bvar\s+[A-Za-z_$]"),
    "FE-21/BE-21": re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}", re.S),
    "BE-11": re.compile(r"\breadFileSync\s*\("),
    "BE-20": re.compile(r"\bconsole\.log\s*\("),
    "RES-05": re.compile(r"addEventListener\s*\(|setInterval\s*\(|setTimeout\s*\("),
}

def walk(root: Path):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            yield Path(base) / name

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    langs = Counter(); manifests = []; candidates = defaultdict(list); large = []
    files_seen = 0
    for p in walk(root):
        files_seen += 1
        rel = str(p.relative_to(root))
        if p.name in MANIFESTS or p.suffix in {".sln", ".csproj"}: manifests.append(rel)
        if p.suffix.lower() in LANG: langs[LANG[p.suffix.lower()]] += 1
        try:
            if p.stat().st_size > 250_000: large.append(rel)
            if p.suffix.lower() not in LANG or p.stat().st_size > 1_000_000: continue
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for cid, rx in PATTERNS.items():
            if rx.search(text): candidates[cid].append(rel)
    result = {
        "root": str(root), "files_seen": files_seen, "languages": dict(langs),
        "manifests": sorted(manifests), "large_files": sorted(large),
        "candidates": {k: sorted(v) for k, v in sorted(candidates.items())},
        "warning": "Candidates are not confirmed findings; inspect context before changes."
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
