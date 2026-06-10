# Docker Overlay

## Container Workflow

- Prefer project-managed compose or wrapper commands over direct Docker calls.
- Keep image build context small and explicit.
- Avoid installing diagnostics into production images for one-off validation.
- Prefer short-lived helper containers for diagnostics when possible.
- When loopback fidelity matters, launch helper containers in the target service
  container's network namespace.

## Secrets and Logs

- Do not print secret-bearing environment variables, compose files, or container
  metadata unless values are redacted.
- Use temporary helper containers for diagnostics when possible.
- Do not bake secrets, private keys, local config files, or credential material
  into images or image layers.
- Prefer runtime secret delivery through environment variables, mounted secret
  files, orchestrator secrets, or a secret manager.

## Docker Validation

- Rebuild images and restart services through the project workflow when Docker
  files or container entrypoints change.
- Before publishing or handing off an image-related change, check Dockerfiles,
  compose files, build args, generated manifests, and copied logs for secrets
  and machine-specific identifiers.
