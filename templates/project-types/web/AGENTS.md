# Web Overlay

## Frontend Workflow

- Use the package manager implied by the lockfile.
- Use the Node.js version declared by the repository.
- Follow the existing component system, routing model, and styling conventions.
- Prefer accessible native controls and semantic HTML.

## UI Quality

- Verify responsive behavior for mobile and desktop when changing layout.
- Keep text from overflowing containers.
- Avoid decorative complexity that makes core workflows harder to scan.

## Validation

- Run the project lint, typecheck, unit tests, and browser checks that match the
  changed surface.
- For visual or interaction changes, inspect the running app in a browser before
  handoff.

## Frontend Secret Boundary

- Treat anything shipped to the browser as public, including build-time injected
  variables and framework-specific public environment variables.
- Never embed API keys, service credentials, access tokens, or private account
  data in frontend bundles, static assets, Docker image layers, or client-side
  configuration.
- If browser code needs secret-backed third-party access, use a server-side
  component with authentication, input validation, rate limiting, and runtime
  secret access.
- Update documentation or runbooks when secret storage, injection, rotation, or
  runtime configuration changes.
