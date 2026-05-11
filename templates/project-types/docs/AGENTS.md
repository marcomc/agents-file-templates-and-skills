# Documentation Overlay

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
