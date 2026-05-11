#!/usr/bin/env python3
"""Mine AGENTS.md files and produce draft template updates."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


INSTRUCTION_FILE_PATTERNS = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    ".github/instructions/*.instructions.md",
)

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[A-Za-z0-9._-]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[0-1]))(?:\.\d{1,3}){2,3}\b"),
    re.compile(r"(?i)\b(?:token|secret|password|cookie|api[_-]?key)\b\s*[:=]"),
]

KEYWORDS = (
    "must",
    "always",
    "never",
    "prefer",
    "run ",
    "validate",
    "test",
    "lint",
    "secret",
    "deploy",
    "release",
    "readme",
    "changelog",
    "shellcheck",
    "markdownlint",
)


def load_manifest(template_repo: Path) -> dict:
    if yaml is None:
        raise SystemExit("PyYAML is required to read templates.yml")
    return yaml.safe_load((template_repo / "templates.yml").read_text(encoding="utf-8"))


def is_ignored(path: Path, ignored: set[str]) -> bool:
    return any(part in ignored for part in path.parts)


def agents_depth(root: Path, instruction_path: Path) -> int:
    project = project_root_for_instruction(instruction_path)
    rel_parent = project.relative_to(root)
    return len(rel_parent.parts)


def is_instruction_file(root: Path, path: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    return any(fnmatch.fnmatch(rel, f"**/{pattern}") or fnmatch.fnmatch(rel, pattern) for pattern in INSTRUCTION_FILE_PATTERNS)


def project_root_for_instruction(path: Path) -> Path:
    if path.name == "copilot-instructions.md" and path.parent.name == ".github":
        return path.parent.parent
    if path.name.endswith(".instructions.md") and path.parent.parent.name == ".github":
        return path.parent.parent.parent
    return path.parent


def instruction_kind(path: Path) -> str:
    if path.name == "AGENTS.md":
        return "agents"
    if path.name == "CLAUDE.md":
        return "claude"
    if path.name == "GEMINI.md":
        return "gemini"
    if path.name == "copilot-instructions.md":
        return "copilot-repository"
    if path.name.endswith(".instructions.md"):
        return "copilot-path-specific"
    return "unknown"


def find_agents(roots: list[Path], max_depth: int, ignored: set[str]) -> list[Path]:
    found: list[Path] = []
    for root in roots:
        for current, dirs, files in os.walk(root):
            current_path = Path(current)
            rel = current_path.relative_to(root)
            if is_ignored(rel, ignored):
                dirs[:] = []
                continue
            depth = 0 if rel == Path(".") else len(rel.parts)
            if depth >= max_depth:
                dirs[:] = []
            else:
                dirs[:] = [item for item in dirs if item not in ignored]
            for name in files:
                candidate = current_path / name
                if is_instruction_file(root, candidate) and agents_depth(root, candidate) <= max_depth:
                    found.append(candidate)
    return sorted(set(found))


def project_files(project: Path, ignored: set[str]) -> list[str]:
    files: list[str] = []
    for root, dirs, names in os.walk(project):
        dirs[:] = [d for d in dirs if d not in ignored]
        for name in names:
            files.append((Path(root) / name).relative_to(project).as_posix())
    return files


def glob_matches(pattern: str, files: list[str]) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return any(path == prefix or path.startswith(f"{prefix}/") for path in files)
    return any(fnmatch.fnmatch(path, pattern) for path in files)


def classify(project: Path, agents_text: str, manifest: dict) -> tuple[list[str], list[str]]:
    ignored = set(manifest.get("scan_defaults", {}).get("ignored_dirs", []))
    files = project_files(project, ignored)
    text = agents_text.lower()
    detected: list[str] = []
    evidence: list[str] = []
    for item in manifest.get("project_types", []):
        detector = item.get("detect", {})
        file_hits = [pattern for pattern in detector.get("file_globs", []) if glob_matches(pattern, files)]
        marker_hits = [marker for marker in detector.get("content_markers", []) if marker.lower() in text]
        if file_hits or marker_hits:
            detected.append(item["id"])
            evidence.append(f"{item['id']}: files={file_hits[:3]} markers={marker_hits[:3]}")
    return detected, evidence


def privacy_notes(text: str) -> list[str]:
    notes = []
    for pattern in PRIVATE_PATTERNS:
        if pattern.search(text):
            notes.append("contains private or secret-shaped material; review before reuse")
            break
    return notes


def reusable_categories(text: str) -> list[str]:
    lowered = text.lower()
    categories = []
    checks = {
        "validation": ["lint", "test", "validate", "markdownlint", "shellcheck"],
        "release": ["release", "changelog", "tag"],
        "secrets": ["secret", "token", "password", "no_log"],
        "containers": ["docker", "container", "compose"],
        "docs": ["readme", "documentation", "table of contents"],
        "deployment": ["deploy", "production"],
    }
    for name, markers in checks.items():
        if any(marker in lowered for marker in markers):
            categories.append(name)
    return categories


def redact(line: str) -> str:
    line = re.sub(r"/Users/[A-Za-z0-9._-]+", "${HOME}", line)
    line = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "${EMAIL}", line)
    line = re.sub(r"\b192\.168\.\d{1,3}\.\d{1,3}\b", "${PRIVATE_IP}", line)
    line = re.sub(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "${PRIVATE_IP}", line)
    return line


def candidate_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("|") or len(line) > 220:
            continue
        lowered = line.lower()
        if any(keyword in lowered for keyword in KEYWORDS):
            lines.append(redact(line))
    return lines


def write_matrix(template_repo: Path, agents_files: list[Path], roots: list[Path], manifest: dict) -> list[dict]:
    records = []
    for agents_path in agents_files:
        project = project_root_for_instruction(agents_path)
        text = agents_path.read_text(encoding="utf-8", errors="ignore")
        detected, evidence = classify(project, text, manifest)
        root = next((item for item in roots if agents_path.is_relative_to(item)), roots[0])
        records.append(
            {
                "project_path": str(project),
                "agents_path": str(agents_path),
                "instruction_kind": instruction_kind(agents_path),
                "relative_depth": agents_depth(root, agents_path),
                "detected_types": detected,
                "evidence": evidence,
                "reusable_instruction_categories": reusable_categories(text),
                "privacy_risk_notes": privacy_notes(text),
                "candidate_templates": detected or ["generic-development"],
            }
        )

    matrix_dir = template_repo / ".work" / "matrix"
    matrix_dir.mkdir(parents=True, exist_ok=True)
    (matrix_dir / "projects.json").write_text(json.dumps(records, indent=2), encoding="utf-8")

    summary = ["# Agents Matrix Summary", "", f"- Generated: {date.today().isoformat()}", f"- Files: {len(records)}", ""]
    counts: dict[str, int] = defaultdict(int)
    for record in records:
        for type_id in record["candidate_templates"]:
            counts[type_id] += 1
    summary.append("## Candidate Template Counts")
    summary.append("")
    for type_id, count in sorted(counts.items()):
        summary.append(f"- `{type_id}`: {count}")
    summary.append("")
    (matrix_dir / "summary.md").write_text("\n".join(summary), encoding="utf-8")
    return records


def draft_for_template(template_repo: Path, records: list[dict], template: str) -> Path:
    draft_dir = template_repo / ".work" / "drafts" / template
    draft_dir.mkdir(parents=True, exist_ok=True)
    candidates: list[str] = []
    for record in records:
        if template not in record["candidate_templates"]:
            continue
        text = Path(record["agents_path"]).read_text(encoding="utf-8", errors="ignore")
        candidates.extend(candidate_lines(text))

    unique = []
    for line in candidates:
        if line not in unique:
            unique.append(line)

    draft = [
        f"# Draft: {template}",
        "",
        "This ignored draft contains mined candidate rules. Review and sanitize",
        "before editing curated templates.",
        "",
        "## Candidate Rules",
        "",
    ]
    draft.extend(f"- {line.lstrip('- ')}" for line in unique[:80])
    draft.append("")
    path = draft_dir / "draft.md"
    path.write_text("\n".join(draft), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-repo", default=".")
    parser.add_argument("--scan-root", action="append", default=[])
    parser.add_argument("--max-depth", type=int, default=None)
    parser.add_argument("--template", default="")
    parser.add_argument("--current-project", default="")
    args = parser.parse_args()

    template_repo = Path(args.template_repo).expanduser().resolve()
    manifest = load_manifest(template_repo)
    ignored = set(manifest.get("scan_defaults", {}).get("ignored_dirs", []))
    max_depth = args.max_depth or int(manifest.get("scan_defaults", {}).get("max_depth", 2))

    if args.current_project:
        current_project = Path(args.current_project).expanduser().resolve()
        candidates = [
            current_project / "AGENTS.md",
            current_project / "CLAUDE.md",
            current_project / "GEMINI.md",
            current_project / ".github" / "copilot-instructions.md",
        ]
        candidates.extend((current_project / ".github" / "instructions").glob("*.instructions.md"))
        agents_files = [path for path in candidates if path.exists()]
        roots = [current_project]
    else:
        roots = [Path(item).expanduser().resolve() for item in args.scan_root] or [Path.cwd()]
        agents_files = find_agents(roots, max_depth, ignored)

    records = write_matrix(template_repo, agents_files, roots, manifest)
    print(f"Wrote matrix for {len(records)} AGENTS.md files.")

    if args.template:
        path = draft_for_template(template_repo, records, args.template)
        print(f"Wrote {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
