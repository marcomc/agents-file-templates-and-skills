# Home Assistant Overlay

## Home Assistant Workflow

- Spell out `Home Assistant` in user-facing text unless the project already uses
  an accepted abbreviation for a different concept.
- Preserve user data, auth stores, add-ons, custom components, and backup
  semantics when changing automation.
- Treat token, credential, and integration setup as secret-bearing.
- If a task generates or rotates access tokens programmatically, verify token
  type, expiration semantics, storage behavior, and reload or restart behavior
  against the running application version.

## Validation

- Validate changes through the project-approved local or staging path before
  touching a live Home Assistant instance.
- For backup, restore, or failover work, prove the exact scenario the change
  depends on rather than only checking service reachability.
- Avoid side effects inside long-running service containers during validation.
  Prefer helper containers, documented APIs, or wrapper commands.
