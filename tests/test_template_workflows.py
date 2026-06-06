from __future__ import annotations

import json
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
            template.write_text(template.read_text(encoding="utf-8") + "\n- Domain: `${PRIMARY_DOMAIN}`.\n", encoding="utf-8")
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
                "--apply",
            )

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

    def test_apply_learning_draft_requires_approved_clean_draft(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            draft_dir = template_repo / ".work" / "learning-upstream"
            draft_dir.mkdir(parents=True)
            draft = draft_dir / "markdown-validation.md"
            draft.write_text(
                """# Learning Upstream Draft: markdown-validation

## Handoff

- Lesson family: `markdown-validation`
- Proposed template: `docs`
- Review status: `approved`
- Privacy verdict: `clean`
- Recurrence check: `new`

## Candidate Rule

Run markdownlint before completing Markdown documentation changes.

## Prevention Targets

- `atom:docs`
""",
                encoding="utf-8",
            )

            dry_run = self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--json",
            )
            self.assertEqual(json.loads(dry_run.stdout)["action"], "would-updated")

            self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--apply",
            )
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            self.assertIn("## Learned Rules", template.read_text(encoding="utf-8"))

            template.write_text("# Docs\n\n## Learned Rules\n- Existing rule.\n", encoding="utf-8")
            draft.write_text(draft.read_text(encoding="utf-8").replace("markdownlint", "markdownlint and tests"), encoding="utf-8")
            self.run_helper(
                UPDATE_SCRIPT,
                "--template-repo",
                str(template_repo),
                "--apply-learning-draft",
                str(draft),
                "--apply",
            )
            self.assertIn(
                "- Run markdownlint and tests before completing Markdown documentation changes.",
                template.read_text(encoding="utf-8"),
            )

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

    def test_out_of_sync_report_preserves_render_time_set_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            template_repo = self.write_template_repo(directory)
            project = self.write_project(directory)
            template = template_repo / "templates" / "project-types" / "docs" / "AGENTS.md"
            template.write_text(template.read_text(encoding="utf-8") + "\n- Domain: `${PRIMARY_DOMAIN}`.\n", encoding="utf-8")
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
