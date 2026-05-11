# Agents File Templates

Reusable `AGENTS.md` templates and skills for creating and maintaining
project-specific agent instructions.

## Table of Contents

- [Purpose](#purpose)
- [Repository Layout](#repository-layout)
- [How to Use](#how-to-use)
- [Configuration](#configuration)
- [Skills](#skills)
- [Vendor Conventions](#vendor-conventions)
- [Build Workflow](#build-workflow)
- [Template Safety](#template-safety)
- [Development](#development)

## Purpose

This repository keeps a reusable library of agent-instruction templates. It is
designed for people who want one canonical global policy in `${HOME}/AGENTS.md`
and smaller project overlays that can be merged into each project.

The repository supports two recurring workflows:

- Initialize or refresh a project `AGENTS.md` from curated templates.
- Mine existing project `AGENTS.md` files and promote reusable rules back into
  the curated template library.

## Repository Layout

```text
.
├── README.md
├── TODO.md
├── templates.yml
├── scripts/
│   └── privacy_scan.py
├── skills/
│   ├── install-agents-file-template-skills/
│   ├── init-agents-file/
│   └── update-agents-file-templates/
└── templates/
    ├── global/
    │   └── AGENTS.md
    └── project-types/
        ├── ansible/
        ├── bash/
        ├── cli/
        ├── docker/
        ├── docs/
        ├── generic-development/
        ├── github-release/
        ├── hardware-device/
        ├── home-assistant/
        ├── macos/
        ├── python/
        ├── raspberry-pi/
        ├── web/
        └── workspace/
```

Temporary mining outputs belong under `.work/`. That directory is ignored and
must not be committed.

## How to Use

Clone the repository, then install the skills into the agents you use:

```bash
git clone <REPOSITORY_URL> agents-file-templates
cd agents-file-templates
python3 skills/install-agents-file-template-skills/scripts/install_agent_template_skills.py \
  --agent openai \
  --agent claude \
  --agent opencode \
  --apply
```

By default, the installer copies skills into each agent's skill directory. Add
`--mode symlink` if you want each installed skill to point back to this central
repository instead.

After installation, the normal workflow is to ask your coding agent to use the
skill from inside a project. For example:

```text
Use init-agents-file to initialize this project's agent instructions.
```

The skill should inspect the current project, locate the template repository
from its installed configuration, generate a dry run, and apply only after the
target file and content are clear. By default it writes the portable standard
`AGENTS.md`. If you want an agent-specific file, ask for that explicitly, for
example `CLAUDE.md`, `GEMINI.md`, or `.github/copilot-instructions.md`.

The Python scripts under `skills/*/scripts/` are implementation helpers and
manual fallback entrypoints. They are not the preferred daily interface.

To create a global policy for a new user, start from
`templates/global/AGENTS.md`, replace placeholders, and place the result at
`${HOME}/AGENTS.md`.

## Configuration

`templates.yml` is the manifest for template selection, detection, merge order,
and placeholders.

Important fields:

- `placeholders`: values expected by templates.
- `project_types`: curated overlays and detection hints.
- `scan_defaults`: conservative defaults for mining existing projects.
- `privacy`: patterns and review rules used before template promotion.

The skills must not assume a fixed filesystem layout. Users can configure scan
roots and depth for their own machines. If a request is ambiguous, the agent
should inspect the current project, infer a likely scope, and ask before a broad
scan.

## Skills

The portable skill contract is `SKILL.md` plus optional bundled resources such
as `scripts/`, `references/`, and `assets/`. The files named
`agents/openai.yaml` are only OpenAI/Codex user-interface metadata. They help
Codex display friendly skill names and suggested prompts, but they are not the
skill logic and other agents can ignore them.

There are no equivalent adapter files for Claude Code, GitHub Copilot, Gemini,
or OpenCode because their current conventions use Markdown instruction files,
settings, or their own agent config formats rather than a shared metadata file.
This repository keeps `SKILL.md` as canonical and adds product-specific adapters
only when a product has a real adapter convention.

### `install-agents-file-template-skills`

Use this skill to install or symlink this repository's skills into local agent
skill directories. It supports multiple agents in one run and reports when an
agent uses instruction files instead of portable skill directories. The
installer writes a local `config/template_repo_path.txt` into installed skill
copies so the skills can find this template repository later without users
exporting environment variables.

### `init-agents-file`

Use this skill to create or refresh a project instruction file. It detects
project types, merges matching overlays, replaces placeholders, and preserves a
local editable section. It can generate standard `AGENTS.md` or agent-specific
files such as `CLAUDE.md`, `GEMINI.md`, or
`.github/copilot-instructions.md`.

### `update-agents-file-templates`

Use this skill to update curated templates over time. It supports:

- Full mining from configured project roots.
- Single-template mining, such as updating only the Python template.
- Current-project promotion, where reusable rules from the current project are
  proposed for one or more templates.

Mining creates ignored working artifacts. Curated templates are updated only
after review and privacy scrubbing.

## Vendor Conventions

| Tool / company | Main project instruction file | Global/user instruction file | Skills format | Metadata adapter |
| --- | --- | --- | --- | --- |
| OpenAI Codex | `AGENTS.md` convention, plus Codex skills | Codex-local skills directories | Agent Skills: `SKILL.md` plus optional `scripts/`, `references/`, `assets/` | Optional `agents/openai.yaml`, OpenAI/Codex UI metadata |
| Anthropic Claude Code | `CLAUDE.md` or `.claude/CLAUDE.md` | `~/.claude/CLAUDE.md`; local `CLAUDE.local.md` | Agent Skills in `~/.claude/skills/` or project `.claude/skills/` | No separate adapter required; metadata is in `SKILL.md` frontmatter |
| GitHub Copilot | `.github/copilot-instructions.md`; path-specific `.github/instructions/*.instructions.md`; partial support for `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` varies by feature | Personal and organization instructions in GitHub/Copilot settings | Prompt files `*.prompt.md`; repository instructions are Markdown files | No metadata adapter; mostly Markdown files and GitHub settings |
| Google Gemini CLI | `GEMINI.md` by default | `~/.gemini/GEMINI.md` | Context files and CLI skills, depending on local version and configuration | No vendor adapter for instruction files; configurable context filenames |
| OpenCode | `AGENTS.md` | `~/.config/opencode/AGENTS.md` | Claude-compatible skills and custom agents | Uses `opencode.json` or Markdown frontmatter for custom agents, not an `openai.yaml` equivalent |

The practical rule for this repository is: keep curated templates in
`templates/**/AGENTS.md`, then generate the output filename each target agent
expects.

## Build Workflow

This repository was designed with a multi-agent workflow:

1. Scaffold the repository, manifest, templates, skills, and ignored working
   directories.
2. Scan existing project `AGENTS.md` files into a matrix of project types,
   evidence, reusable instruction categories, and privacy risk notes.
3. Distill category-specific drafts from the matrix and existing project rules.
4. Curate public-safe templates from the drafts.
5. Implement and install the skills.
6. Validate Markdown, scripts, privacy checks, and generated output.

If the process changes during future updates, refresh this section so the
repository remains reproducible.

## Template Safety

Curated templates must be reusable by other people. Do not commit:

- Personal home paths.
- Email addresses.
- Private domains or hostnames.
- Secrets, tokens, passwords, cookies, or account identifiers.
- Local device names, IP addresses, or private network details.

Use placeholders such as `${HOME}`, `${USER_NAME}`, `${PRIMARY_DOMAIN}`,
`${OBSIDIAN_VAULT_PATH}`, and `${PROJECT_NAME}` instead.

## Development

Validate changes before committing:

```bash
markdownlint --config ~/.markdownlint.json README.md TODO.md templates/**/*.md skills/**/*.md
python3 scripts/privacy_scan.py .
python3 skills/init-agents-file/scripts/init_agents_file.py --project .
python3 skills/update-agents-file-templates/scripts/update_agents_templates.py --template-repo . --scan-root . --max-depth 2
python3 skills/install-agents-file-template-skills/scripts/install_agent_template_skills.py --agent openai
```
