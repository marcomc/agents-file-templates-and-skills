from __future__ import annotations

import json
import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "skills" / "init-agents-file" / "scripts" / "init_agents_file.py"
UPDATE_SCRIPT = ROOT / "skills" / "update-agents-file-templates" / "scripts" / "update_agents_templates.py"


class TemplateWorkflowTests(unittest.TestCase):
    def run_helper(self, script: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )

    def write_template_repo(self, directory: Path) -> Path:
        repo = directory / "templates-repo"
        docs = repo / "templates" / "project-types" / "docs"
        generic = repo / "templates" / "project-types" / "generic-development"
        docs.mkdir(parents=True)
        generic.mkdir(parents=True)
        (repo / "templates.yml").write_text(
            """---
version: 1
scan_defaults:
  max_depth: 2
  ignored_dirs:
    - .git
    - .work
merge:
  always_include:
    - generic-development
project_types:
  - id: generic-development
    path: templates/project-types/generic-development/AGENTS.md
    detect:
      file_globs:
        - README.md
  - id: docs
    path: templates/project-types/docs/AGENTS.md
    detect:
      file_globs:
        - "*.md"
""",
            encoding="utf-8",
        )
        (generic / "AGENTS.md").write_text(
            """# Generic

- Use `${MARKDOWNLINT_CONFIG}` for Markdown validation.
""",
            encoding="utf-8",
        )
        (docs / "AGENTS.md").write_text(
            """# Docs

- Keep documentation operational.
""",
            encoding="utf-8",
        )
        return repo

    def write_project(self, directory: Path) -> Path:
        project = directory / "project"
        project.mkdir()
        (project / "README.md").write_text("# Project\n", encoding="utf-8")
        return project

    def replace_generated_date(self, path: Path, value: str) -> None:
        text = path.read_text(encoding="utf-8")
        updated = re.sub(r"<!-- generated-date: .*? -->", f"<!-- generated-date: {value} -->", text)
        path.write_text(updated, encoding="utf-8")

    def test_generated_output_keeps_home_placeholder_and_check_ignores_date(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)

            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--apply",
            )
            agents = project / "AGENTS.md"
            text = agents.read_text(encoding="utf-8")
            self.assertIn("${HOME}/.markdownlint.json", text)
            self.assertNotIn(str(Path.home()), text)

            agents.write_text(text.replace("<!-- generated-date:", "<!-- generated-date: 2000-01-01 "), encoding="utf-8")
            result = self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--check",
                "--json",
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "current")

    def test_check_preserves_render_time_set_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            template.write_text(
                template.read_text(encoding="utf-8")
                + "\n- Domain: `${PRIMARY_DOMAIN}`.\n"
                + "- Custom value: `${CUSTOM_VALUE}`.\n",
                encoding="utf-8",
            )
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--set",
                "PROJECT_DESCRIPTION=Custom project description",
                "--set",
                "PRIMARY_DOMAIN=example.invalid",
                "--set",
                "CUSTOM_VALUE=custom",
                "--apply",
            )
            self.replace_generated_date(project / "AGENTS.md", "2000-01-01")

            result = self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--check",
                "--json",
            )
            self.assertEqual(json.loads(result.stdout)["status"], "current")

            template.write_text(template.read_text(encoding="utf-8") + "\n- New docs rule.\n", encoding="utf-8")
            result = self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--check",
                "--json",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["status"], "out-of-sync")

    def test_check_detects_project_rename(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = directory / "old"
            project.mkdir()
            (project / "README.md").write_text("# Project\n", encoding="utf-8")
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--apply",
            )

            renamed = directory / "new"
            project.rename(renamed)
            result = self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(renamed),
                "--template-repo",
                str(template_repo),
                "--check",
                "--json",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["status"], "out-of-sync")

    def test_budget_report_separates_template_and_local_instruction_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--apply",
            )
            agents = project / "AGENTS.md"
            agents.write_text(
                agents.read_text(encoding="utf-8").replace(
                    "<!-- BEGIN PROJECT LOCAL -->\n\n<!-- END PROJECT LOCAL -->",
                    "<!-- BEGIN PROJECT LOCAL -->\n"
                    "- Preserve this intentionally local operational constraint.\n"
                    "<!-- END PROJECT LOCAL -->",
                ),
                encoding="utf-8",
            )

            result = self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--budget-report",
                "--budget-warning-words",
                "1",
                "--json",
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "over-budget")
            self.assertGreater(payload["word_count"], 1)
            self.assertGreater(payload["local_rules_word_count"], 0)
            self.assertEqual(
                {section["template"] for section in payload["template_sections"]},
                {"generic-development", "docs"},
            )

    def test_apply_preserves_existing_generated_template_types(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--apply",
            )

            optional = template_repo / "templates" / "project-types" / "optional"
            optional.mkdir(parents=True)
            (optional / "AGENTS.md").write_text("# Optional\n\n- Optional rule.\n", encoding="utf-8")
            manifest = template_repo / "templates.yml"
            manifest.write_text(
                manifest.read_text(encoding="utf-8")
                + """
  - id: optional
    path: templates/project-types/optional/AGENTS.md
    detect:
      file_globs:
        - trigger.txt
""",
                encoding="utf-8",
            )
            (project / "trigger.txt").write_text("trigger\n", encoding="utf-8")

            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--apply",
            )
            text = (project / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("<!-- BEGIN TEMPLATE: docs -->", text)
            self.assertNotIn("<!-- BEGIN TEMPLATE: optional -->", text)

    def test_apply_preserves_existing_render_time_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--set",
                "PROJECT_DESCRIPTION=Preserved project description",
                "--apply",
            )

            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--apply",
            )
            self.assertIn(
                "- Description: Preserved project description",
                (project / "AGENTS.md").read_text(encoding="utf-8"),
            )

    def test_apply_preserves_project_description_after_template_change(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--set",
                "PROJECT_DESCRIPTION=Preserved project description",
                "--apply",
            )
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            template.write_text(template.read_text(encoding="utf-8") + "\n- Updated docs rule.\n", encoding="utf-8")

            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--apply",
            )
            self.assertIn(
                "- Description: Preserved project description",
                (project / "AGENTS.md").read_text(encoding="utf-8"),
            )

    def write_learning_draft(self, template_repo: Path, candidate_rule: str) -> Path:
        draft_dir = template_repo / ".work" / "learning-upstream"
        draft_dir.mkdir(parents=True, exist_ok=True)
        draft = draft_dir / "markdown-validation.md"
        draft.write_text(
            f"""# Learning Upstream Draft: markdown-validation

## Handoff

- Lesson family: `markdown-validation`
- Proposed template: `docs`
- Review status: `approved`
- Privacy verdict: `clean`
- Recurrence check: `new`

## Candidate Rule

{candidate_rule}

## Prevention Targets

- `atom:docs`
""",
            encoding="utf-8",
        )
        return draft

    def write_edit_plan(
        self, directory: Path, template_text: str, replacement: str, draft: Path, candidate_rule: str
    ) -> Path:
        replacement_file = directory / "replacement.md"
        replacement_file.write_text(replacement, encoding="utf-8")
        plan = directory / "edit-plan.json"
        plan.write_text(
            json.dumps(
                {
                    "before_sha256": hashlib.sha256(template_text.encode()).hexdigest(),
                    "replacement_file": replacement_file.name,
                    "replacement_sha256": hashlib.sha256(replacement.encode()).hexdigest(),
                    "operation": "refine",
                    "integrated_rule": "Run markdownlint and tests before completing Markdown documentation changes.",
                    "review_rationale": "Consolidates the existing validation guidance into one concise rule.",
                    "draft_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
                    "candidate_rule": candidate_rule,
                    "coverage_rationale": "The candidate's required documentation check is generalized into the integrated rule.",
                }
            ),
            encoding="utf-8",
        )
        return plan

    def test_apply_learning_draft_requires_reviewed_replacement_plan(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            draft = self.write_learning_draft(
                template_repo, "Run markdownlint before completing Markdown documentation changes."
            )
            candidate_rule = "Run markdownlint before completing Markdown documentation changes."
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            before = template.read_text(encoding="utf-8")

            missing_plan = self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--json",
                check=False,
            )
            self.assertNotEqual(missing_plan.returncode, 0)
            self.assertIn("requires --edit-plan", missing_plan.stderr)
            self.assertEqual(template.read_text(encoding="utf-8"), before)

            plan = self.write_edit_plan(
                directory,
                before,
                "# Docs\n\n- Run markdownlint and tests before completing Markdown documentation changes.\n",
                draft,
                candidate_rule,
            )
            dry_run = self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--edit-plan",
                str(plan),
                "--json",
            )
            self.assertEqual(json.loads(dry_run.stdout)["action"], "would-updated")
            dry_result = json.loads(dry_run.stdout)
            self.assertEqual(dry_result["candidate_rule"], candidate_rule)
            self.assertIn("candidate's required documentation check", dry_result["coverage_rationale"])
            self.assertEqual(template.read_text(encoding="utf-8"), before)

            self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--edit-plan",
                str(plan),
                "--apply",
            )
            written = template.read_text(encoding="utf-8")
            self.assertEqual(written, "# Docs\n\n- Run markdownlint and tests before completing Markdown documentation changes.\n")
            self.assertNotIn("Keep documentation operational.", written)

            # Coverage is detected across multiline markdown, so no review plan is
            # required when existing prose already states the learning.
            template.write_text(
                "# Docs\n\nRun markdownlint before completing\nMarkdown documentation changes.\n",
                encoding="utf-8",
            )
            draft.write_text(draft.read_text(encoding="utf-8").replace("markdownlint", "markdownlint"), encoding="utf-8")
            already_present = self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--json",
            )
            self.assertEqual(json.loads(already_present.stdout)["action"], "would-already-present")

            draft.write_text(draft.read_text(encoding="utf-8").replace("approved", "draft"), encoding="utf-8")
            before = template.read_text(encoding="utf-8")
            result = self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--apply",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not approved", result.stderr)
            self.assertEqual(template.read_text(encoding="utf-8"), before)

    def test_edit_plan_rejects_stale_hashes_and_private_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            draft = self.write_learning_draft(
                template_repo, "Run markdownlint before completing Markdown documentation changes."
            )
            candidate_rule = "Run markdownlint before completing Markdown documentation changes."
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            original = template.read_text(encoding="utf-8")
            clean_replacement = "# Docs\n\n- Run markdownlint and tests before completing Markdown documentation changes.\n"
            plan = self.write_edit_plan(directory, original, clean_replacement, draft, candidate_rule)
            template.write_text(original + "\nNew clause.\n", encoding="utf-8")
            result = self.run_helper(
                UPDATE_SCRIPT, "--template-repo", str(template_repo), "--apply-learning-draft", str(draft),
                "--edit-plan", str(plan), "--apply", check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("before_sha256", result.stderr)

            current = template.read_text(encoding="utf-8")
            plan = self.write_edit_plan(directory, current, clean_replacement, draft, candidate_rule)
            plan_data = json.loads(plan.read_text(encoding="utf-8"))
            plan_data["replacement_sha256"] = "0" * 64
            plan.write_text(json.dumps(plan_data), encoding="utf-8")
            result = self.run_helper(
                UPDATE_SCRIPT, "--template-repo", str(template_repo), "--apply-learning-draft", str(draft),
                "--edit-plan", str(plan), "--apply", check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("replacement_sha256", result.stderr)

            private_replacement = clean_replacement + "\n- Set api_" + "key=placeholder before deployment.\n"
            plan = self.write_edit_plan(directory, current, private_replacement, draft, candidate_rule)
            result = self.run_helper(
                UPDATE_SCRIPT, "--template-repo", str(template_repo), "--apply-learning-draft", str(draft),
                "--edit-plan", str(plan), "--apply", check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("private or secret-shaped", result.stderr)
            self.assertEqual(template.read_text(encoding="utf-8"), current)

    def test_rule_coverage_preserves_negation_scope_and_command_case(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            draft = self.write_learning_draft(template_repo, "Run tests before release.")
            for existing in (
                "# Docs\n\n- Do not run tests before release.\n",
                "# Docs\n\n- Run tests before release when deploying to production.\n",
                "# Docs\n\n- Run Tests before release.\n",
            ):
                with self.subTest(existing=existing):
                    template.write_text(existing, encoding="utf-8")
                    result = self.run_helper(
                        UPDATE_SCRIPT,
                        "--template-repo",
                        str(template_repo),
                        "--apply-learning-draft",
                        str(draft),
                        "--json",
                        check=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("requires --edit-plan", result.stderr)
                    self.assertEqual(template.read_text(encoding="utf-8"), existing)

            template.write_text("# Docs\n\n- Run tests before\n  release.\n", encoding="utf-8")
            result = self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--json",
            )
            self.assertEqual(json.loads(result.stdout)["action"], "would-already-present")

    def test_edit_plan_must_map_current_approved_draft(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            candidate = "Run markdownlint before completing Markdown documentation changes."
            draft = self.write_learning_draft(template_repo, candidate)
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            original = template.read_text(encoding="utf-8")
            replacement = "# Docs\n\n- Run markdownlint and tests before completing Markdown documentation changes.\n"
            plan = self.write_edit_plan(directory, original, replacement, draft, candidate)

            cases = (
                ("stale draft", lambda data: data.update(draft_sha256="0" * 64)),
                ("wrong candidate", lambda data: data.update(candidate_rule="Skip markdownlint.")),
                ("missing mapping", lambda data: data.update(coverage_rationale="")),
            )
            for label, mutate in cases:
                with self.subTest(label=label):
                    data = json.loads(plan.read_text(encoding="utf-8"))
                    mutate(data)
                    plan.write_text(json.dumps(data), encoding="utf-8")
                    result = self.run_helper(
                        UPDATE_SCRIPT, "--template-repo", str(template_repo), "--apply-learning-draft", str(draft),
                        "--edit-plan", str(plan), "--apply", check=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(template.read_text(encoding="utf-8"), original)

            data = json.loads(self.write_edit_plan(directory, original, replacement, draft, candidate).read_text())
            data["integrated_rule"] = "Unrelated deployment rule."
            plan.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_helper(
                UPDATE_SCRIPT, "--template-repo", str(template_repo), "--apply-learning-draft", str(draft),
                "--edit-plan", str(plan), "--apply", check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not a complete rule block", result.stderr)
            self.assertEqual(template.read_text(encoding="utf-8"), original)

    def test_out_of_sync_report_detects_changed_template(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--apply",
            )

            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            template.write_text(template.read_text(encoding="utf-8") + "\n- New docs rule.\n", encoding="utf-8")
            self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--scan-root",
                str(directory),
                "--out-of-sync-report",
            )
            report = json.loads((template_repo / ".work" / "out-of-sync" / "projects.json").read_text(encoding="utf-8"))
            self.assertEqual(report[0]["status"], "out-of-sync")
            self.assertIn("instruction_budget", report[0])

    def test_out_of_sync_report_isolates_recovery_conflicts_and_preserves_consumers(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            ambiguous = self.write_project(directory)
            generic = template_repo / "templates/project-types/generic-development/AGENTS.md"
            docs = template_repo / "templates/project-types/docs/AGENTS.md"
            generic.write_text("# Generic\n\nUse production.\n")
            docs.write_text("# Docs\n\nUse staging.\n")
            self.run_helper(INIT_SCRIPT, "--project", str(ambiguous), "--template-repo", str(template_repo),
                            "--types", "docs", "--apply")
            generic.write_text("# Generic\n\nUse ${TEST_COMMAND}.\n")
            docs.write_text("# Docs\n\nUse ${TEST_COMMAND}.\n")
            healthy = directory / "healthy"
            healthy.mkdir()
            self.run_helper(INIT_SCRIPT, "--project", str(healthy), "--template-repo", str(template_repo),
                            "--types", "docs", "--set", "TEST_COMMAND=make test", "--apply")
            original = {project: (project / "AGENTS.md").read_bytes() for project in [ambiguous, healthy]}
            self.run_helper(UPDATE_SCRIPT, "--template-repo", str(template_repo), "--scan-root", str(directory),
                            "--out-of-sync-report")
            records = json.loads((template_repo / ".work/out-of-sync/projects.json").read_text())
            report = {Path(record["project"]): record for record in records}
            self.assertEqual(set(report), {ambiguous.resolve(), healthy.resolve()})
            self.assertEqual(report[ambiguous.resolve()]["status"], "out-of-sync")
            self.assertIn("TEST_COMMAND", report[ambiguous.resolve()]["recovery_conflict"])
            self.assertEqual(report[healthy.resolve()]["status"], "current")
            self.assertTrue((template_repo / ".work/out-of-sync/summary.md").is_file())
            for project, before in original.items():
                self.assertEqual((project / "AGENTS.md").read_bytes(), before)

    def test_out_of_sync_report_includes_agent_specific_outputs(self) -> None:
        cases = {
            "claude": "CLAUDE.md",
            "gemini": "GEMINI.md",
            "copilot": ".github/copilot-instructions.md",
        }
        for agent, output_name in cases.items():
            with self.subTest(agent=agent):
                with tempfile.TemporaryDirectory() as raw:
                    directory = Path(raw)
                    template_repo = self.write_template_repo(directory)
                    project = self.write_project(directory)
                    self.run_helper(
                        INIT_SCRIPT,
                        "--project",
                        str(project),
                        "--template-repo",
                        str(template_repo),
                        "--types",
                        "docs",
                        "--agent",
                        agent,
                        "--output-mode",
                        "specific",
                        "--apply",
                    )

                    template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
                    template.write_text(template.read_text(encoding="utf-8") + "\n- New docs rule.\n", encoding="utf-8")
                    self.run_helper(
                        UPDATE_SCRIPT,
                        "--template-repo",
                        str(template_repo),
                        "--scan-root",
                        str(directory),
                        "--out-of-sync-report",
                    )
                    report = json.loads(
                        (template_repo / ".work" / "out-of-sync" / "projects.json").read_text(encoding="utf-8")
                    )
                    self.assertEqual(len(report), 1)
                    self.assertEqual(report[0]["status"], "out-of-sync")
                    actual_output = Path(report[0]["output"]).resolve().relative_to(project.resolve()).as_posix()
                    self.assertEqual(actual_output, output_name)

    def test_out_of_sync_report_preserves_opencode_agent_for_agents_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--agent",
                "opencode",
                "--output-mode",
                "specific",
                "--apply",
            )

            self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--scan-root",
                str(directory),
                "--out-of-sync-report",
            )
            report = json.loads((template_repo / ".work" / "out-of-sync" / "projects.json").read_text(encoding="utf-8"))
            self.assertEqual(len(report), 1)
            self.assertEqual(report[0]["status"], "current")
            actual_output = Path(report[0]["output"]).resolve().relative_to(project.resolve()).as_posix()
            self.assertEqual(actual_output, "AGENTS.md")

    def test_out_of_sync_report_includes_nested_copilot_at_max_depth(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            scan_root = directory / "scan-root"
            project = scan_root / "team" / "project"
            project.mkdir(parents=True)
            (project / "README.md").write_text("# Project\n", encoding="utf-8")
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--agent",
                "copilot",
                "--output-mode",
                "specific",
                "--apply",
            )

            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            template.write_text(template.read_text(encoding="utf-8") + "\n- New docs rule.\n", encoding="utf-8")
            self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--scan-root",
                str(scan_root),
                "--max-depth",
                "2",
                "--out-of-sync-report",
            )
            report = json.loads((template_repo / ".work" / "out-of-sync" / "projects.json").read_text(encoding="utf-8"))
            self.assertEqual(len(report), 1)
            self.assertEqual(report[0]["status"], "out-of-sync")
            actual_output = Path(report[0]["output"]).resolve().relative_to(project.resolve()).as_posix()
            self.assertEqual(actual_output, ".github/copilot-instructions.md")

    def test_out_of_sync_report_preserves_render_time_set_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            template.write_text(
                template.read_text(encoding="utf-8")
                + "\n- Domain: `${PRIMARY_DOMAIN}`.\n"
                + "- Custom value: `${CUSTOM_VALUE}`.\n",
                encoding="utf-8",
            )
            self.run_helper(
                INIT_SCRIPT,
                "--project",
                str(project),
                "--template-repo",
                str(template_repo),
                "--types",
                "docs",
                "--set",
                "PROJECT_DESCRIPTION=Custom project description",
                "--set",
                "PRIMARY_DOMAIN=example.invalid",
                "--set",
                "CUSTOM_VALUE=custom",
                "--apply",
            )
            self.replace_generated_date(project / "AGENTS.md", "2000-01-01")

            self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--scan-root",
                str(directory),
                "--out-of-sync-report",
            )
            report = json.loads((template_repo / ".work" / "out-of-sync" / "projects.json").read_text(encoding="utf-8"))
            self.assertEqual(report[0]["status"], "current")

            template.write_text(template.read_text(encoding="utf-8") + "\n- New docs rule.\n", encoding="utf-8")
            self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--scan-root",
                str(directory),
                "--out-of-sync-report",
            )
            report = json.loads((template_repo / ".work" / "out-of-sync" / "projects.json").read_text(encoding="utf-8"))
            self.assertEqual(report[0]["status"], "out-of-sync")


if __name__ == "__main__":
    unittest.main()
