#!/usr/bin/env python3
"""Scan committed template files for common personal or secret-bearing text."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_PATTERNS = {
    "absolute_home_path": re.compile(r"/Users/[A-Za-z0-9._-]+"),
    "email_address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "private_ipv4": re.compile(
        r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
        r"192\.168\.\d{1,3}\.\d{1,3}|"
        r"172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})\b"
    ),
    "secret_assignment": re.compile(
        r"(?i)\b(?:token|secret|password|cookie|api[_-]?key)\b\s*[:=]\s*['\"]?[^'\"\s]+"
    ),
}

TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".py", ".sh", ".txt"}
SKIP_DIRS = {".git", ".work", "__pycache__"}


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            files.append(path)
    return files


def scan_file(path: Path, root: Path) -> list[str]:
    findings: list[str] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        if "privacy_scan: allow" in line:
            continue
        for name, pattern in DEFAULT_PATTERNS.items():
            if pattern.search(line):
                rel = path.relative_to(root)
                findings.append(f"{rel}:{line_no}: {name}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    findings: list[str] = []
    for path in iter_files(root):
        findings.extend(scan_file(path, root))

    if findings:
        print("Privacy scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("Privacy scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
