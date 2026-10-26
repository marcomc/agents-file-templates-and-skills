# AGENTS.md Instructions

<!-- generated-by: agents-file-templates-and-skills/init-agents-file -->
<!-- generated-date: 2026-09-16 -->

Follow `${HOME}/AGENTS.md` for canonical user-wide policy.

## Project Context

- Project: `agents-file-templates-and-skills`
- Description: Reusable AGENTS.md template and skill repository

## Project-Type Overlays

<!-- BEGIN TEMPLATE: generic-development -->
### Generic Development

## Project Work

- Read the nearest `README.md`, package metadata, and relevant task or release
  notes before editing. Use the project's documented commands and wrappers.
- Keep changes within the requested module boundary; preserve unrelated work and
  edit sources rather than generated outputs.
- Verify changed behavior with the narrowest relevant checks, treat lint output
  as actionable, and report checks that could not run.
- Update the affected operational documentation when behavior changes. Keep one
  canonical document per topic instead of duplicating detailed guidance.
- Do not create commits, tags, pushes, pull requests, or releases unless asked.

## Public-Safe Content

- Keep tracked content portable. Replace personal, network, credential, and
  environment-specific values with stable placeholders.

<!-- END TEMPLATE: generic-development -->

<!-- BEGIN TEMPLATE: python -->
### Python

## Python Work

- Use the project-managed environment and its approved format, lint, type, and
  test commands. Keep packaging metadata, imports, and advertised entrypoints
  consistent.
- Prefer the standard library when adequate. Preserve non-interactive output
  contracts; guard color, links, and progress UI with TTY detection.
- For public CLI or release changes, update help, examples, release metadata,
  and every applicable version source.

## Data and Mutation Safety

- Treat input data, exports, reports, and caches as sensitive unless documented
  otherwise. Keep live inputs ignored and commit only structural placeholders.
- Use dry-run or preview modes for file or external-system mutation unless the
  user explicitly requests apply.

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

## Documentation Changes

- Write concise, command-backed operational guidance and make it discoverable
  from the README, index, or relevant runbook.
- Update configuration, troubleshooting, setup, or release guidance when the
  corresponding behavior changes. Keep generated content marked and refresh a
  README table of contents after a material structural change.
- Use project-relative paths and public-safe placeholders. Show how to discover
  a local value instead of hard-coding personal or private infrastructure data.

<!-- END TEMPLATE: docs -->

<!-- BEGIN TEMPLATE: cli -->
### Cli

## Command Contract

- Keep command names, flags, help, documentation, and backward compatibility
  aligned. Mutating commands need explicit dry-run or apply behavior.
- Preserve non-interactive output contracts. Validate help, an error path, and
  one realistic success path when CLI behavior changes.

## Credentials and Fixtures

- Keep credentials in an approved store or ignored local configuration. Never
  print, log, snapshot, or commit authentication values.
- Keep test fixtures synthetic unless a documented anonymization process exists.

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
- Match platform detection to the file-only inventory: use actual root/nested
  Xcode project or workspace contents and Apple resources. Keep portable Swift
  packages as a negative case; Swift source alone is not an Apple platform.
  Re-run detection after generation to catch boilerplate-induced false matches.
- Keep installer path fanout data newline-delimited or equivalently structured;
  never depend on shell word splitting for destination paths. Cover paths with
  spaces in installer fixtures and smoke tests.
- When uninstall or fanout logic touches the shared canonical payload, preserve
  ownership markers and cover unknown-target, partial-uninstall, and dry-run
  parity in regression tests.
- Keep `SKILL.md` concise and move deterministic behavior into bundled scripts.
- Keep skill examples configurable. Do not assume every user keeps projects
  under `${HOME}/Development`.

## Instruction Routing

- Use `docs/instruction-routing.md` to route new guidance between global,
  root, nested, skill, and documentation layers.
- Keep mandatory privacy, authority, mutation, and validation controls directly
  loaded or explicitly invoked; do not hide them in optional references.
- Treat the instruction budget as a review signal. Move only conditional,
  repeatable detail after confirming the target agent can discover the new
  documentation or skill at the relevant task boundary.

## Repository Validation

- Run `markdownlint --config /Users/mmassari/.markdownlint.json` on edited Markdown files. <!-- privacy_scan: allow -->
- Run `yamllint -c .yamllint` on edited YAML files.
- Run `python3 -m py_compile` on edited Python helper scripts.
- Run `shellcheck --enable=all` on edited shell helper scripts.
- Run `python3 scripts/privacy_scan.py .` before handoff.
- Run a smoke test for edited skill scripts when behavior changes.
<!-- END PROJECT LOCAL -->
