# Generic Development Overlay

## Project Work

- Read the nearest `README.md`, package metadata, and relevant task or release
  notes before editing. Use the project's documented commands and wrappers.
- Keep changes within the requested module boundary; preserve unrelated work and
  edit sources rather than generated outputs.
- Verify changed behavior with the narrowest relevant checks, treat lint output
  as actionable, and report checks that could not run.
- Update the affected operational documentation when behavior changes. Keep one
  canonical document per topic instead of duplicating detailed guidance.
- Do not create commits, tags, pushes, pull requests, or releases unless asked.

## Public-Safe Content

- Keep tracked content portable. Replace personal, network, credential, and
  environment-specific values with stable placeholders.

## Learned Rules

- Treat shipped example configs as real runtime inputs: keep them public-safe and exercise them through the actual install and parser paths, including fallback parsers when present.
- For dependency installation, upgrades, restore copies, generated temp/cache work or cleanup, read `${GLOBAL_AGENTS_PATH}` and follow its artifact lifecycle policy; retain ownership, retention and cleanup evidence before task closure.
