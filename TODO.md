# TODO

## Table of Contents

- [Optional Enhancements](#optional-enhancements)
- [Investigation Notes](#investigation-notes)

## Optional Enhancements

- Add cross-tool synchronization for `CLAUDE.md`, `.github/copilot-instructions.md`,
  `.cursor/rules`, and similar files.
  - Investigate Ruler, Rulesync, Agentlink, and native Codex behavior before
    choosing the output model.
  - Prefer one canonical source and generated aliases.
- Add contradiction and staleness checks across templates.
  - Detect rules that conflict across global, project-type, and local sections.
  - Report conflicts without silently rewriting curated templates.
- Add a stronger codebase detector.
  - Consider tree-sitter or language-specific package metadata.
  - Keep simple file-based detection as the fallback.
- Add machine-readable reports for CI.
  - JSON should include changed templates, privacy findings, and ambiguous
    promotion candidates.
- Add nested monorepo mode.
  - Support package-level overlays without creating noisy root instructions.
  - Require explicit user scope before scanning deep trees.
- Add template provenance metadata.
  - Keep source annotations generic and non-identifying.
  - Do not leak private project names or paths in committed templates.
- Add an out-of-sync checker.
  - Compare generated project `AGENTS.md` files with the current template
    manifest and report drift.
- Add optional pre-commit integration.
  - Run privacy checks and Markdown validation before committing template
    changes.

## Investigation Notes

External projects worth reviewing before implementing optional features:

- OpenAI `agents.md` for file conventions and hierarchy expectations.
- `danielrosehill/Agents.md-Templates` for template library organization.
- `ivawzh/agents-md` for composable fragment generation.
- Ruler for multi-tool rule propagation and status checks.
- Rulesync and Agentlink for alias generation and overwrite protection.
- Kurka Labs AGENTS.md Starter Kit for local override patterns.
