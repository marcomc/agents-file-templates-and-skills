# Generic Development Overlay

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
