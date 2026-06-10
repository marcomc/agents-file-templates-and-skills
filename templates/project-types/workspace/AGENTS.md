# Workspace Harness Overlay

## Harness Discipline

- Use the project wrapper commands for normal development, testing, service
  control, and deployment.
- Treat generated workspace directories as disposable outputs.
- Make source changes in the harness configuration or source templates, then
  regenerate the harness.
- Use direct container commands only for diagnostics when no wrapper equivalent
  exists.
- When wrapper command definitions change, regenerate before testing so
  generated commands match source.

## Environment Forwarding

- When wrapper commands forward environment variables into containers or
  subprocesses, update every user-facing command path that depends on the new
  variable.
- Validate the real wrapper command without ad-hoc environment overrides.
- Treat forwarding as a two-step contract: exporting a variable in the shell is
  not enough; it must also be included in the wrapper's forwarded environment
  list.

## Workspace Validation

- After changing harness configuration, run both low-level runner checks and
  the user-facing wrapper entrypoints that exercise them.
- If a scenario or test script is invokable directly by a wrapper command, ensure
  the script is executable and validate the wrapper entrypoint itself.
- Keep control containers clean. Prefer short-lived helper containers for
  diagnostics instead of installing tools into long-running service or control
  containers.
