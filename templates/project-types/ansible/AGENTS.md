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

## Structure

- Put shared conditions on `import_tasks`, `include_tasks`, or `block` sections
  when several adjacent tasks use the same condition.
- Keep secrets out of logs with `no_log: true` on secret-bearing tasks and facts.

## Validation

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
