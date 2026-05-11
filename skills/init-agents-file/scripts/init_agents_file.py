#!/usr/bin/env python3
"""Generate a project AGENTS.md from reusable template overlays."""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


BEGIN_LOCAL = "<!-- BEGIN PROJECT LOCAL -->"
END_LOCAL = "<!-- END PROJECT LOCAL -->"

AGENT_OUTPUTS = {
    "standard": "AGENTS.md",
    "openai": "AGENTS.md",
    "codex": "AGENTS.md",
    "opencode": "AGENTS.md",
    "claude": "CLAUDE.md",
    "gemini": "GEMINI.md",
    "copilot": ".github/copilot-instructions.md",
}

AGENT_GLOBAL_PATHS = {
    "standard": "${HOME}/AGENTS.md",
    "openai": "${HOME}/AGENTS.md",
    "codex": "${HOME}/AGENTS.md",
    "opencode": "${HOME}/.config/opencode/AGENTS.md",
    "claude": "${HOME}/.claude/CLAUDE.md",
    "gemini": "${HOME}/.gemini/GEMINI.md",
    "copilot": "GitHub Copilot personal or organization custom instructions",
}


def load_manifest(template_repo: Path) -> dict:
    if yaml is None:
        raise SystemExit("PyYAML is required to read templates.yml")
    manifest_path = template_repo / "templates.yml"
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8"))


def iter_project_files(project: Path, ignored_dirs: set[str]) -> list[str]:
    paths: list[str] = []
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        root_path = Path(root)
        for name in files:
            rel = (root_path / name).relative_to(project).as_posix()
            paths.append(rel)
    return paths


def glob_matches(pattern: str, files: list[str]) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return any(path == prefix or path.startswith(f"{prefix}/") for path in files)
    return any(fnmatch.fnmatch(path, pattern) for path in files)


def detect_types(project: Path, manifest: dict) -> list[str]:
    ignored = set(manifest.get("scan_defaults", {}).get("ignored_dirs", []))
    files = iter_project_files(project, ignored)
    content = ""
    agents = project / "AGENTS.md"
    readme = project / "README.md"
    for candidate in (agents, readme):
        if candidate.exists():
            content += "\n" + candidate.read_text(encoding="utf-8", errors="ignore").lower()

    detected: list[str] = []
    for item in manifest.get("project_types", []):
        detector = item.get("detect", {})
        file_hit = any(glob_matches(pattern, files) for pattern in detector.get("file_globs", []))
        content_hit = any(marker.lower() in content for marker in detector.get("content_markers", []))
        if file_hit or content_hit:
            detected.append(item["id"])
    return detected


def strip_title(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip()
    return markdown.strip()


def existing_local_section(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        rf"{re.escape(BEGIN_LOCAL)}(?P<body>.*?){re.escape(END_LOCAL)}",
        re.DOTALL,
    )
    match = pattern.search(text)
    return match.group("body").strip() if match else ""


def placeholder_values(project: Path, pairs: list[str], agent: str) -> dict[str, str]:
    values = {
        "HOME": str(Path.home()),
        "USER_NAME": os.environ.get("USER", ""),
        "USER_WORKSPACE_ROOT": str(Path.home()),
        "GLOBAL_AGENTS_PATH": AGENT_GLOBAL_PATHS.get(agent, AGENT_GLOBAL_PATHS["standard"]),
        "MARKDOWNLINT_CONFIG": str(Path.home() / ".markdownlint.json"),
        "OBSIDIAN_VAULT_PATH": "${OBSIDIAN_VAULT_PATH}",
        "PRIMARY_DOMAIN": "${PRIMARY_DOMAIN}",
        "AUTHORIZED_WORK_CONTEXT": "${AUTHORIZED_WORK_CONTEXT}",
        "PROJECT_NAME": project.name,
        "PROJECT_DESCRIPTION": "${PROJECT_DESCRIPTION}",
        "GENERATED_DATE": date.today().isoformat(),
    }
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"Invalid --set value, expected KEY=VALUE: {pair}")
        key, value = pair.split("=", 1)
        values[key] = value
    return values


def replace_placeholders(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace("${" + key + "}", value)
    return text


def template_map(manifest: dict) -> dict[str, str]:
    return {item["id"]: item["path"] for item in manifest.get("project_types", [])}


def render(project: Path, template_repo: Path, forced_types: list[str], pairs: list[str], agent: str, output_name: str) -> str:
    manifest = load_manifest(template_repo)
    detected = forced_types or detect_types(project, manifest)
    always = manifest.get("merge", {}).get("always_include", [])
    ordered = []
    for item in [*always, *detected]:
        if item not in ordered:
            ordered.append(item)

    paths = template_map(manifest)
    values = placeholder_values(project, pairs, agent)
    output = [
        f"# {output_name} Instructions",
        "",
        "<!-- generated-by: agents-file-templates-and-skills/init-agents-file -->",
        f"<!-- generated-date: {values['GENERATED_DATE']} -->",
        "",
        f"Follow `{values['GLOBAL_AGENTS_PATH']}` for canonical user-wide policy.",
        "",
        "## Project Context",
        "",
        f"- Project: `{values['PROJECT_NAME']}`",
        f"- Description: {values['PROJECT_DESCRIPTION']}",
        "",
        "## Project-Type Overlays",
        "",
    ]

    for type_id in ordered:
        rel_path = paths.get(type_id)
        if not rel_path:
            continue
        template_path = template_repo / rel_path
        body = strip_title(template_path.read_text(encoding="utf-8"))
        body = replace_placeholders(body, values)
        output.extend(
            [
                f"<!-- BEGIN TEMPLATE: {type_id} -->",
                f"### {type_id.replace('-', ' ').title()}",
                "",
                body,
                "",
                f"<!-- END TEMPLATE: {type_id} -->",
                "",
            ]
        )

    local = existing_local_section(project / "AGENTS.md")
    output.extend(
        [
            "## Project Local Rules",
            "",
            BEGIN_LOCAL,
            local,
            END_LOCAL,
            "",
        ]
    )
    return "\n".join(output).replace("\n\n\n", "\n\n")


def ancestors(path: Path) -> list[Path]:
    resolved = path.expanduser().resolve()
    return [resolved, *resolved.parents]


def installed_repo_config() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "config" / "template_repo_path.txt"
        if candidate.exists():
            configured = Path(candidate.read_text(encoding="utf-8").strip()).expanduser()
            if (configured / "templates.yml").exists():
                return configured
    return None


def default_template_repo(project: Path) -> Path:
    env_path = os.environ.get("AGENTS_TEMPLATE_REPO")
    if env_path:
        return Path(env_path).expanduser()

    configured = installed_repo_config()
    if configured:
        return configured

    search_roots = [*ancestors(Path(__file__).resolve()), *ancestors(project), *ancestors(Path.cwd())]
    for candidate in search_roots:
        if (candidate / "templates.yml").exists() and (candidate / "templates").is_dir():
            return candidate

    for name in ("agents-file-templates-and-skills", "agents-file-templates"):
        candidate = Path.home() / "Development" / name
        if candidate.exists():
            return candidate

    raise SystemExit(
        "Could not find agents-file-templates-and-skills. Pass --template-repo or set AGENTS_TEMPLATE_REPO."
    )


def output_for_agent(agent: str, mode: str, explicit_output: str | None) -> str:
    if explicit_output:
        return explicit_output
    if mode == "specific":
        return AGENT_OUTPUTS.get(agent, AGENT_OUTPUTS["standard"])
    return AGENT_OUTPUTS["standard"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--template-repo", default=None)
    parser.add_argument("--types", default="")
    parser.add_argument("--agent", default="standard", choices=sorted(AGENT_OUTPUTS))
    parser.add_argument("--output-mode", default="standard", choices=["standard", "specific"])
    parser.add_argument("--output", default=None)
    parser.add_argument("--set", dest="sets", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    template_repo = Path(args.template_repo).expanduser().resolve() if args.template_repo else default_template_repo(project)
    forced = [item.strip() for item in args.types.split(",") if item.strip()]
    output_name = output_for_agent(args.agent, args.output_mode, args.output)
    content = render(project, template_repo, forced, args.sets, args.agent, output_name)

    output = project / output_name
    if args.apply:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        print(f"Wrote {output}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
