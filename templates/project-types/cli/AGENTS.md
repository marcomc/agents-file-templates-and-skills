# CLI Overlay

## Command Design

- Keep command names, flags, help text, and documentation consistent.
- Preserve backward compatibility unless the user explicitly asks for a breaking
  change.
- Prefer explicit dry-run and apply modes for commands that mutate files or
  external systems.
- Preserve output contracts for scripts and automation. Human-friendly color,
  links, or progress output should be disabled or guarded for non-TTY output.

## Validation

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
