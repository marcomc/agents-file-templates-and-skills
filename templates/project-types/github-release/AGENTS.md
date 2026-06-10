# GitHub Release Overlay

## Release Discipline

- Start release work from the current changelog, version metadata, and existing
  release process.
- Do not publish tags, releases, or pull requests until the user explicitly asks.
- Keep release notes concise and reviewer-friendly.
- If an `Unreleased` section exists, add user-visible changes there instead of
  creating a new dated release entry.
- Only create or date a release entry when the release is actually being
  finalized.

## Release Validation

- Confirm the working tree state, target branch, tag, and changelog entry before
  release publication.
- If a target version or tag already exists, stop and resolve the collision
  intentionally.
- Verify tests or smoke checks covering version output, package metadata, or
  artifact naming when release metadata changes.
