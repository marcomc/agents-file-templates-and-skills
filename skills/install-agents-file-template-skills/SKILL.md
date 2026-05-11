---
name: install-agents-file-template-skills
description: Use when installing this repository's portable Agent Skills into one or more local coding-agent skill directories
---

# Install Agents File Template Skills

Use this skill after cloning `agents-file-templates` to install the repository's
skills into local coding-agent environments.

## Workflow

1. Identify the template repository path.
2. Ask which agents the user wants to support when not specified.
3. Ask whether the user wants copies or symlinks when not specified.
4. Run a dry run first.
5. Apply only after the destination list is acceptable.

## Commands

Dry run for common local agents:

```bash
python3 scripts/install_agent_template_skills.py --agent openai --agent claude --agent opencode
```

Install by copying:

```bash
python3 scripts/install_agent_template_skills.py --agent openai --agent claude --apply
```

Install by symlinking to a central repository by adding `--mode symlink`:

```bash
python3 scripts/install_agent_template_skills.py --agent openai --agent claude --mode symlink --apply
```

## Agent Support

- OpenAI/Codex: installs skills into `${HOME}/.agents/skills`.
- Claude Code: installs skills into `${HOME}/.claude/skills`.
- OpenCode: uses Claude-compatible skills in `${HOME}/.claude/skills`.
- GitHub Copilot: does not consume portable `SKILL.md` directories directly.
  Use project instruction files such as `.github/copilot-instructions.md`.
- Gemini: use `GEMINI.md` project instructions; skill directory support depends
  on the local Gemini CLI version and configuration.

Installed skill copies include a local `config/template_repo_path.txt` file so
the skills can find the cloned template repository later.
