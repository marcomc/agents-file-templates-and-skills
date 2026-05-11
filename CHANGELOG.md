# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
