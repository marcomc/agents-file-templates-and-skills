#!/usr/bin/env python3
"""Install this repository's Agent Skills into local agent skill directories."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SKILL_NAMES = (
    "init-agents-file",
    "update-agents-file-templates",
    "install-agents-file-template-skills",
)

AGENT_DESTINATIONS = {
    "openai": [Path("~/.agents/skills")],
    "codex": [Path("~/.agents/skills")],
    "claude": [Path("~/.claude/skills")],
    "opencode": [Path("~/.claude/skills")],
}

NON_SKILL_AGENTS = {
    "copilot": "GitHub Copilot uses repository instruction files, not portable SKILL.md directories.",
    "gemini": "Gemini commonly uses GEMINI.md context files; skill directory support depends on your CLI configuration.",
}


def find_repo(start: Path) -> Path:
    env_path = os.environ.get("AGENTS_TEMPLATE_REPO")
    if env_path:
        return Path(env_path).expanduser().resolve()
    for candidate in [start.resolve(), *start.resolve().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (candidate / "templates.yml").exists() and (candidate / "skills").is_dir():
            return candidate
    raise SystemExit("Could not find agents-file-templates. Run from the repo or set AGENTS_TEMPLATE_REPO.")


def copy_skill(source: Path, dest: Path, mode: str, apply: bool) -> str:
    target = dest / source.name
    if not apply:
        return f"would {mode} {source} -> {target}"

    dest.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)

    if mode == "symlink":
        target.symlink_to(source, target_is_directory=True)
    else:
        shutil.copytree(source, target)
        config_dir = target / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "template_repo_path.txt").write_text(
            f"{source.parents[1]}\n",
            encoding="utf-8",
        )
    verb = "copied" if mode == "copy" else "symlinked"
    return f"{verb} {source} -> {target}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--agent", action="append", default=[])
    parser.add_argument("--mode", choices=["copy", "symlink"], default="copy")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    repo = find_repo(Path(args.repo))
    requested = args.agent or ["openai"]
    if "all" in requested:
        requested = [*AGENT_DESTINATIONS, *NON_SKILL_AGENTS]

    actions: list[str] = []
    install_roots: list[Path] = []
    for agent in requested:
        if agent in NON_SKILL_AGENTS:
            actions.append(f"skip {agent}: {NON_SKILL_AGENTS[agent]}")
            continue
        destinations = AGENT_DESTINATIONS.get(agent)
        if not destinations:
            actions.append(f"skip {agent}: unknown agent")
            continue
        for dest_root in destinations:
            dest = dest_root.expanduser()
            if dest not in install_roots:
                install_roots.append(dest)

    for dest in install_roots:
        for skill_name in SKILL_NAMES:
            source = repo / "skills" / skill_name
            if not source.exists():
                actions.append(f"skip missing skill: {source}")
                continue
            actions.append(copy_skill(source, dest, args.mode, args.apply))

    for action in actions:
        print(action)
    if not args.apply:
        print("Dry run only. Re-run with --apply to install.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
