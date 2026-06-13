from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = ROOT / "scripts" / "install_agent_template_skills.sh"


class InstallAgentTemplateSkillsTests(unittest.TestCase):
    def write_template_repo(self, directory: Path, skill_count: int = 3) -> Path:
        repo = directory / "template repo"
        skills = repo / "skills"
        skills.mkdir(parents=True)
        (repo / "templates.yml").write_text("---\nversion: 1\n", encoding="utf-8")
        for index in range(1, skill_count + 1):
            skill = skills / f"skill-{index}"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                f"---\nname: skill-{index}\ndescription: Test skill {index}.\n---\n\n# Skill {index}\n",
                encoding="utf-8",
            )
        return repo

    def run_installer(self, home: Path, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = {
            **os.environ,
            "HOME": str(home),
            "CODEX_HOME": str(home / ".codex"),
            "CLAUDE_CONFIG_DIR": str(home / ".claude"),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "AGENTS_TEMPLATE_REPO": "",
        }
        return subprocess.run(
            [str(INSTALL_SCRIPT), "--repo", str(repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            env=env,
            cwd=home,
        )

    def assert_agent_link(self, home: Path, root: Path, skill_name: str) -> None:
        target = root / skill_name
        self.assertTrue(target.is_symlink(), target)
        self.assertEqual(os.readlink(target), str(home / ".agents" / "skills" / skill_name))

    def test_installs_all_discovered_skills_and_fans_out_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            home = directory / "home with spaces"
            home.mkdir()
            repo = self.write_template_repo(directory)

            self.run_installer(
                home,
                repo,
                "--agent",
                "codex",
                "--agent",
                "claude",
                "--agent",
                "opencode",
                "--agent",
                "github-copilot",
                "--agent",
                "openclaw",
                "--apply",
            )

            canonical_root = home / ".agents" / "skills"
            expected_skills = {"skill-1", "skill-2", "skill-3"}
            self.assertEqual(
                {path.name for path in canonical_root.iterdir() if path.is_dir()},
                expected_skills,
            )
            for skill_name in expected_skills:
                self.assertTrue((canonical_root / skill_name / "SKILL.md").is_file())
                self.assertEqual(
                    (canonical_root / skill_name / "config" / "template_repo_path.txt").read_text(
                        encoding="utf-8"
                    ).strip(),
                    str(repo),
                )
                self.assert_agent_link(home, home / ".codex" / "skills", skill_name)
                self.assert_agent_link(home, home / ".claude" / "skills", skill_name)
                self.assert_agent_link(home, home / ".config" / "opencode" / "skills", skill_name)
                self.assert_agent_link(home, home / ".copilot" / "skills", skill_name)
                self.assert_agent_link(home, home / ".openclaw" / "skills", skill_name)

    def test_symlink_mode_links_canonical_to_repo_and_agents_to_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            home = directory / "home"
            home.mkdir()
            repo = self.write_template_repo(directory, skill_count=1)

            self.run_installer(
                home,
                repo,
                "--agent",
                "codex",
                "--mode",
                "symlink",
                "--apply",
            )

            canonical_skill = home / ".agents" / "skills" / "skill-1"
            self.assertTrue(canonical_skill.is_symlink(), canonical_skill)
            self.assertEqual(os.readlink(canonical_skill), str(repo / "skills" / "skill-1"))
            self.assert_agent_link(home, home / ".codex" / "skills", "skill-1")


if __name__ == "__main__":
    unittest.main()
