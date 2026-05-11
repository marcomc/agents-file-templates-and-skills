---
name: update-agents-file-templates
description: Use when mining existing AI-agent instruction files or promoting current-project rules into reusable template overlays
---

# Update Agents File Templates

Use this skill to improve curated `AGENTS.md` templates from real project
instructions. It can mine `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
`.github/copilot-instructions.md`, and
`.github/instructions/*.instructions.md`.

## Modes

- Full mining: scan configured roots and build a project matrix.
- Single-template mining: update the draft for one template from matching
  projects.
- Current-project promotion: extract reusable rules from the current project and
  propose them for one or more templates.

## Workflow

1. Confirm scope before broad scans.
2. Run the helper script to create ignored `.work/` artifacts.
3. Review the matrix to see which instruction file kinds were found.
4. Review drafts for conflicts, overlap, and privacy risk.
5. Edit curated templates manually from the reviewed draft material.
6. Run Markdown validation and the privacy scanner.

## Commands

Scan a known root:

```bash
python3 "${AGENTS_TEMPLATE_REPO}/skills/update-agents-file-templates/scripts/update_agents_templates.py" \
  --template-repo "${AGENTS_TEMPLATE_REPO}" \
  --scan-root "${PROJECT_SCAN_ROOT}" \
  --max-depth 2
```

Draft one template:

```bash
python3 "${AGENTS_TEMPLATE_REPO}/skills/update-agents-file-templates/scripts/update_agents_templates.py" \
  --template-repo "${AGENTS_TEMPLATE_REPO}" \
  --scan-root "${PROJECT_SCAN_ROOT}" \
  --template python \
  --max-depth 2
```

Promote from the current project:

```bash
python3 "${AGENTS_TEMPLATE_REPO}/skills/update-agents-file-templates/scripts/update_agents_templates.py" \
  --template-repo "${AGENTS_TEMPLATE_REPO}" \
  --current-project . \
  --template python
```

## Scope Rules

- If the user names a project, operate on that project first.
- If the user asks to learn from all projects but gives no roots, infer a likely
  development root from the current path and ask before scanning it.
- Do not hardcode another developer's folder layout.

## Safety Rules

- Never commit `.work/` artifacts.
- Never copy personal paths, private domains, hostnames, IPs, secrets, or
  account identifiers into curated templates.
- Prefer placeholders when a rule needs user-specific data.
- Leave conflict notes in reports instead of forcing a questionable merge.
