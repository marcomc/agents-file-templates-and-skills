# Global Agent Rules

These rules apply to agent work rooted under `${USER_WORKSPACE_ROOT}`.

## Required Validation

- Run `markdownlint` on every Markdown file you create or edit.
- Use `${MARKDOWNLINT_CONFIG}` as the Markdown lint config.
- Run `shellcheck --enable=all` on every shell script you create or edit.
- Run the relevant linter or test command for every file type you create or
  edit before finishing.
- Prefer targeted checks for changed files, then run broader checks when shared
  behavior or project-wide configuration changes.
- Fix lint findings instead of silencing them unless a suppression is technically
  required and justified in the file.
- If a required tool is unavailable, report the missing tool and the exact check
  that could not be run.

## Markdown Rules

- Keep `README.md` files lint-clean.
- For new projects, create a `README.md` and include a table of contents.
- When you materially update a project `README.md`, add or refresh its table of
  contents.

## Shell Rules

- Prefer portable, explicit shell code.
- Quote expansions unless unquoted behavior is required.
- Keep scripts compatible with their declared shell.

## User Context

- Primary public domain: `${PRIMARY_DOMAIN}`.
- Authorized work context: `${AUTHORIZED_WORK_CONTEXT}`.

## Obsidian Vault

- The canonical active Obsidian vault is `${OBSIDIAN_VAULT_PATH}`.
- Save new Obsidian notes and runbooks under that vault unless the user
  explicitly requests a different vault.

## Security-Sensitive Wording

- Use precise, authorization-first wording for hardware, firmware, protocol, and
  telemetry work.
- Make the owned or authorized maintenance context explicit when it is relevant.
- If a request appears to involve unauthorized access, evasion, credential
  theft, exploitation, or defeating security controls, state the concern plainly
  and ask for authorization and scope before proceeding.

## Privacy and Secret Safety

- Never commit or print secrets, tokens, API keys, private keys, passwords,
  cookies, signed URLs, OAuth credentials, or credential-bearing command output.
- Treat copied logs and verbose command output as potentially sensitive. Redact
  values before placing output in documentation, issues, pull requests, or chat.
- Do not add personal identifiers or environment-specific details to tracked
  files. Replace names, emails, usernames, private hostnames, local device
  names, account identifiers, private IP addresses, and machine-specific paths
  with placeholders.
- Use repository-relative paths in documentation. Use `${HOME}` or `~` only when
  a home-relative path is part of the documented interface.
- Keep live data files, generated exports, caches, local config files, and
  credential files out of version control. Add or update ignore rules when a
  workflow creates those files.
