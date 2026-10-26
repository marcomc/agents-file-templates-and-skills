# CLI Overlay

## Command Contract

- Keep command names, flags, help, documentation, and backward compatibility
  aligned. Mutating commands need explicit dry-run or apply behavior.
- Preserve non-interactive output contracts. Validate help, an error path, and
  one realistic success path when CLI behavior changes.

## Credentials and Fixtures

- Keep credentials in an approved store or ignored local configuration. Never
  print, log, snapshot, or commit authentication values.
- Keep test fixtures synthetic unless a documented anonymization process exists.
