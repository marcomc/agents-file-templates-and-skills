# Bash and Shell Overlay

## Shell Authoring

- Match the declared shell in the shebang.
- Prefer POSIX-compatible shell for portable scripts unless the project clearly
  uses a shell-specific feature set.
- Quote expansions by default.
- Use arrays only in shells that support them.

## Validation

- Run `shellcheck --enable=all` on edited shell scripts.
- Fix warnings directly unless a suppression is required and justified near the
  line it suppresses.

## Operational Safety

- Avoid destructive commands by default.
- Use dry-run, explicit target, or confirmation modes for scripts that delete,
  overwrite, deploy, or mutate external systems.
