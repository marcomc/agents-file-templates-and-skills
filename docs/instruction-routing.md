# Instruction Routing and Budget

Use the smallest instruction layer that reliably reaches the agent when it is
needed. Small root files improve relevance; they must not hide mandatory safety
or validation controls in optional references.

## Routing Matrix

| Content | Destination | Test before promotion |
| --- | --- | --- |
| Cross-project safety, privacy, and authority boundaries | Global policy | It applies to nearly every task. |
| Project identity, stable commands, and universal constraints | Root instruction file | It is needed for most work in that repository. |
| Rules limited to a subtree with an independent lifecycle | Nested instruction file | The target agent resolves nested files for the task working directory. |
| Repeatable task with a trigger, steps, tools, and validation | Skill | It has occurred more than once or prevents a costly recurring failure. |
| Explanatory or detailed reference material | Documentation | The agent can discover it from a concise task-relevant link. |

## Root Instruction Rules

- Keep the root file to project identity, nonstandard commands, universal
  constraints, and links to detailed guidance.
- Do not append a new rule for every failure. First identify whether the cause
  is a missing universal constraint, a scoped workflow, a missing test, or a
  one-off task detail.
- Keep required safety, authorization, validation, and mutation boundaries in
  directly loaded instructions or in an explicitly invoked skill.
- Keep repository layout descriptions high-level. A stale file-by-file map is
  worse than no map.

## Scoped Instructions

- Add a nested instruction file only for a coherent subtree such as an app,
  package, service, or independently deployed component.
- The root file must point to the subtree when agents can start outside it.
- Do not rely on nested inheritance until the target agent's discovery behavior
  has been verified in that repository and working-directory model.

## Skills and Documentation

- A skill is for a repeatable procedure, not a long reference document. Its
  name and description must state when to load it.
- Keep `SKILL.md` short; place deterministic work in bundled scripts and put
  deep reference material under `references/`.
- Use documentation for detailed conventions that are useful only during a
  particular task. Link it from the root instruction or the relevant skill.

## Budget Review

The generator's budget report is a warning, not a hard gate. It highlights
always-loaded instruction files that need routing review:

```bash
python3 skills/init-agents-file/scripts/init_agents_file.py \
  --project <PROJECT_PATH> --template-repo <TEMPLATE_REPO> \
  --budget-report --json
```

Investigate an over-budget result by reviewing the reported template and local
sections. Preserve justified safety controls; move only conditional detail to a
skill or task-relevant document.
