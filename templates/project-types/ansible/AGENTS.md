# Ansible Overlay

## Module-First Practice

- Prefer Ansible modules over `ansible.builtin.command` or
  `ansible.builtin.shell`.
- Use raw commands only when no suitable module exists, and document the
  rationale, idempotency, and error handling near the task.
- Keep roles reusable by using role-namespaced variables and wiring project
  variables from inventory or group vars.
- Do not hand-edit generated or vendored dependency directories. Update the
  source templates, lock files, or dependency metadata that produce them.

## Role Selection

- Before creating an independent local role, search Ansible Galaxy for
  maintained candidates and assess maintenance, versioning, platform support,
  interface, and fit with the project's requirements.
- Use a version-pinned Galaxy role directly when it satisfies the requirements
  completely.
- When a candidate could fit with a wrapper, narrowly scoped project tasks, a
  companion role, an upstream contribution, or a maintained fork, present the
  alternatives, missing capabilities, and trade-offs, then ask the user to
  choose before implementation.
- Create a local role only when no Galaxy candidate is suitable, or after the
  user selects that option. Document the assessment and rejection reason in the
  owning project.

## Structure

- Put shared conditions on `import_tasks`, `include_tasks`, or `block` sections
  when several adjacent tasks use the same condition.
- Keep secrets out of logs with `no_log: true` on secret-bearing tasks and facts.

## Ansible Validation

- Run the project-approved Ansible lint, syntax, and scenario checks.
- Treat line-length warnings according to the project policy.
- Run YAML linting where the repository requires it.

## Secret-Safe Ansible

- Use `no_log: true` for tasks that transmit, receive, inspect, or derive
  secret-bearing values.
- Treat Docker container metadata as potentially secret-bearing because
  `Config.Env` can expose credentials.
- After adding validation for a secret-bearing service, run the relevant verbose
  playbook path into a temporary log and search for known secret field names
  before handoff.
