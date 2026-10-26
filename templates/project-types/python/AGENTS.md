# Python Overlay

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
