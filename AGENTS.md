# AGENTS.md Instructions

<!-- generated-by: agents-file-templates-and-skills/init-agents-file -->
<!-- generated-date: 2026-06-10 -->

Follow `${HOME}/AGENTS.md` for canonical user-wide policy.

## Project Context

- Project: `agents-file-templates-and-skills`
- Description: Reusable AGENTS.md template and skill repository

## Project-Type Overlays

<!-- BEGIN TEMPLATE: generic-development -->
### Generic Development

## Project Orientation

- Start by reading the nearest `README.md`, package metadata, and existing task
  or changelog files before editing.
- Prefer existing project commands, wrappers, and documented workflows over
  inventing new entrypoints.
- Keep changes scoped to the user request and the affected module boundaries.

## Change Discipline

- Do not revert unrelated local changes.
- Preserve generated-file boundaries and edit source templates instead of
  generated outputs.
- Add or update tests when behavior changes.
- Report validation that was run and any checks that could not be run.
- Treat lint output as actionable unless it is clearly unrelated pre-existing
  noise; call out any pre-existing noise separately.
- Do not create commits, tags, pushes, pull requests, or releases unless the
  user explicitly asks for that action.

## Documentation

- Keep project-facing documentation concise and operational.
- Update setup, usage, or runbook instructions in the same change when behavior
  changes.
- Keep contributor, maintainer, and operational notes in agent-facing documents
  when they are not needed by normal users.
- Prefer one canonical document per topic and link to it instead of duplicating
  long explanations across files.

## Public-Safe Project Content

- Keep project content portable and public-safe unless the repository explicitly
  declares itself private operational documentation.
- Before finishing, check changed source, docs, configs, tests, fixtures, and
  generated artifacts for personal data, local paths, private network details,
  live credentials, and copied sensitive command output.
- Use stable placeholders in examples, such as `<HOSTNAME>`,
  `<LOCAL_USERNAME>`, `<HOME_DIR>`, `<PATH_TO_PROJECT>`, and `<SECRET_NAME>`.

<!-- END TEMPLATE: generic-development -->

<!-- BEGIN TEMPLATE: python -->
### Python

## Python Workflow

- Prefer the project-managed environment and commands from `pyproject.toml`,
  lockfiles, task runners, or the README.
- Keep package metadata, console scripts, and import paths consistent.
- Use standard-library functionality where it is adequate.
- Keep installed CLI behavior and direct module behavior consistent when both
  entrypoints are advertised.
- Preserve text output contracts for piped output; terminal color, links, or
  progress UI must be guarded by TTY detection.

## Testing and Quality

- Run the narrowest relevant tests first, then broader checks when shared
  behavior changes.
- Run formatting, linting, and type checks only through project-approved tools.
- Avoid adding runtime dependencies for simple scripting problems unless the
  dependency already exists or the tradeoff is documented.
- Use the repository's aggregate validation command when available. Otherwise
  run applicable lint, format, type, import, and test checks for the changed
  package layout.

## Packaging

- When changing public CLI behavior, update help text, README examples, and
  changelog or release notes if the project uses them.
- When cutting a release, update every version source of truth used by the
  project and verify version-reporting smoke checks.

## Data Tool Safety

- Treat generated data, active input files, exports, reports, and local caches
  as potentially sensitive unless the repository explicitly says otherwise.
- Keep private operational inputs ignored. Commit structural templates with
  placeholder data instead.
- For tools that mutate files or external systems, prefer dry-run or preview
  modes and require explicit apply intent.

<!-- END TEMPLATE: python -->

<!-- BEGIN TEMPLATE: bash -->
### Bash

## Shell Authoring

- Match the declared shell in the shebang.
- Prefer POSIX-compatible shell for portable scripts unless the project clearly
  uses a shell-specific feature set.
- Quote expansions by default.
- Use arrays only in shells that support them.

## Bash Validation

- Run `shellcheck --enable=all` on edited shell scripts.
- Fix warnings directly unless a suppression is required and justified near the
  line it suppresses.

## Operational Safety

- Avoid destructive commands by default.
- Use dry-run, explicit target, or confirmation modes for scripts that delete,
  overwrite, deploy, or mutate external systems.

<!-- END TEMPLATE: bash -->

<!-- BEGIN TEMPLATE: docs -->
### Docs

## Documentation Style

- Write operational documentation for the next maintainer.
- Keep instructions concise, current, and command-backed.
- Prefer examples that can be copied and adapted safely.
- Keep documentation discoverable through the relevant README, index, or
  navigation file.

## Maintenance

- Update the table of contents when materially changing a README.
- Remove stale setup or release guidance when a workflow changes.
- Keep generated documentation clearly marked.
- Update configuration documentation when adding, renaming, removing, or
  changing config keys, environment variables, CLI flags, or defaults.
- Update troubleshooting or runbook documentation when behavior changes in a way
  users or operators could encounter.

## Documentation Sanitization

- Use project-relative paths and placeholders in public documentation.
- Do not include personal home paths, real usernames, private domains, internal
  hostnames, private IP addresses, device names, service account identifiers, or
  real customer or team data.
- If documentation needs a concrete local value, show how to discover it and
  assign it to a shell variable instead of hard-coding one user's value.

<!-- END TEMPLATE: docs -->

<!-- BEGIN TEMPLATE: cli -->
### Cli

## Command Design

- Keep command names, flags, help text, and documentation consistent.
- Preserve backward compatibility unless the user explicitly asks for a breaking
  change.
- Prefer explicit dry-run and apply modes for commands that mutate files or
  external systems.
- Preserve output contracts for scripts and automation. Human-friendly color,
  links, or progress output should be disabled or guarded for non-TTY output.

## CLI Validation

- Test help output, error paths, and at least one realistic success path.
- Update README examples and changelog entries when user-visible CLI behavior
  changes.

## Credential Handling

- Keep CLI credentials in the platform credential store, tool-specific config
  store, environment, or ignored local config files.
- Never echo, log, snapshot, or commit token values returned by authentication
  flows.
- Keep test fixtures synthetic unless the repository documents a safe
  anonymization process.

<!-- END TEMPLATE: cli -->

## Project Local Rules

<!-- BEGIN PROJECT LOCAL -->
## Template Repository Guardrails

- Treat this repository as public-facing even when the local checkout is private.
- Curated templates under `templates/` must be generic, portable, and
  placeholder-based.
- Do not hardcode personal home paths, private domains, hostnames, LAN IPs,
  device names, account identifiers, or secrets into committed files.
- Use placeholders such as `${HOME}`, `${USER_NAME}`, `${PRIMARY_DOMAIN}`,
  `${OBSIDIAN_VAULT_PATH}`, `${PROJECT_NAME}`, `<HOSTNAME>`, and
  `<PRIVATE_IP>`.

## Mining and Draft Artifacts

- Keep mining outputs, draft distillations, matrices, and temporary reports
  under `.work/`.
- `.work/` must remain ignored and must not be committed.
- Promote only reviewed, sanitized, reusable rules from `.work/` drafts into
  curated templates.
- Preserve conflict notes in temporary reports when mined rules disagree; do not
  force questionable rules into curated templates.

## Skills

- The canonical skill sources live under `skills/`.
- Installed copies under `${HOME}/.agents/skills/` are mirrors. After changing a
  skill, sync the matching folder into `${HOME}/.agents/skills/`.
- Installed skill copies may contain local `config/template_repo_path.txt`
  files created by the installer. Do not commit those local config files into
  this repository.
- Keep `scripts/install_agent_template_skills.sh` and `Makefile` aligned with
  any new supported agent destination or instruction-file convention.
- Installer tests must set or clear `AGENTS_TEMPLATE_REPO` explicitly so ambient
  local configuration cannot bypass fixture repositories.
- Keep `SKILL.md` concise and move deterministic behavior into bundled scripts.
- Keep skill examples configurable. Do not assume every user keeps projects
  under `${HOME}/Development`.

## Repository Validation

- Run `markdownlint --config /Users/mmassari/.markdownlint.json` on edited Markdown files. <!-- privacy_scan: allow -->
- Run `yamllint -c .yamllint` on edited YAML files.
- Run `python3 -m py_compile` on edited Python helper scripts.
- Run `shellcheck --enable=all` on edited shell helper scripts.
- Run `python3 scripts/privacy_scan.py .` before handoff.
- Run a smoke test for edited skill scripts when behavior changes.
<!-- END PROJECT LOCAL -->
