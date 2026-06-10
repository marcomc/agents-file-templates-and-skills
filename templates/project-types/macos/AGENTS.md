# macOS Overlay

## macOS Workflow

- Prefer project-approved Xcode, SwiftPM, or app wrapper commands.
- Keep entitlements, signing, sandboxing, and notarization changes explicit.
- Avoid AppleScript automation unless the task specifically requires UI-level
  control.

## macOS Validation

- Build and run the target that matches the changed code.
- For UI changes, inspect the app in the relevant simulator or local runtime.
- Note whether validation was performed on simulator, local Mac, or device.
