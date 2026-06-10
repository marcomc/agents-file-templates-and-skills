# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] - 2026-06-06

### Added in 1.1.0

- Composable agent instruction architecture documentation for global director
  policy, reusable atoms, project-local sections, and template refresh flow.
- Learning-upstream draft summaries for ignored
  `.work/learning-upstream/` handoffs from the agent learning system.
- Approved-draft apply support for clean learning-upstream drafts, with curated
  template edits gated behind explicit `--apply`.
- Generated instruction freshness checks through `init-agents-file --check`.
- Out-of-sync reporting for generated project `AGENTS.md` files after template
  changes.
- Unit tests covering safe placeholder rendering, generated-file freshness,
  approved-draft apply, and out-of-sync reports.

### Changed in 1.1.0

- Generated project instructions now keep `${HOME}`-style placeholders instead
  of expanding personal local paths.
- The template update skill now documents reviewed apply and refresh-report
  workflows for learning-upstream drafts.
- Documentation now links this repository's template-side automation contract
  to the learning-system pipeline runbook.

### Fixed in 1.1.0

- Removed the unapproved-draft apply bypass so only approved, clean learning
  drafts can modify curated templates.
- Avoided duplicate learned-rule insertion when the same rule already exists in
  a curated template.

## [1.0.0] - 2026-05-11

### Added

- Initial reusable `AGENTS.md` template repository.
- Public-safe global policy template and project-type overlays.
- `init-agents-file` and `update-agents-file-templates` skills.
- Template manifest, privacy scan, and ignored mining workspace.
- MIT license.
- Multi-agent instruction-file support for Claude Code, GitHub Copilot, Gemini,
  OpenCode, and OpenAI/Codex conventions.
- `make install` and `make uninstall` targets backed by a shell installer for
  copying or symlinking skills into local agent skill directories.

### Fixed

- Preserve local sections from the selected agent-specific output file when
  refreshing generated instructions.
- Include shell scripts in the publication privacy scan.
