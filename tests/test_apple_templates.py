from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_helper(name: str, skill: str, script: str):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "skills" / skill / "scripts" / script
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INIT = load_helper("apple_init", "init-agents-file", "init_agents_file.py")
UPDATE = load_helper(
    "apple_update", "update-agents-file-templates", "update_agents_templates.py"
)


class AppleTemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = INIT.load_manifest(ROOT)

    def assert_detected(self, project: Path, *, apple: bool, macos: bool) -> None:
        initialized = INIT.detect_types(project, self.manifest)
        mined, _ = UPDATE.classify(project, "", self.manifest)
        for result in (initialized, mined):
            self.assertEqual("apple-app" in result, apple, result)
            self.assertEqual("macos" in result, macos, result)

    def test_xcode_projects_and_resources_detect_apple_without_macos(self) -> None:
        fixtures = (
            "Phone.xcodeproj/project.pbxproj",
            "apps/Tablet/Tablet.xcodeproj/project.pbxproj",
            "App.xcworkspace/contents.xcworkspacedata",
            "apps/Mobile/App.xcworkspace/contents.xcworkspacedata",
            "Main.storyboard",
            "Resources/View.xib",
            "App.entitlements",
        )
        for fixture in fixtures:
            with self.subTest(fixture=fixture), tempfile.TemporaryDirectory() as raw:
                project = Path(raw)
                source = project / fixture
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("fixture\n", encoding="utf-8")
                self.assert_detected(project, apple=True, macos=False)

    def test_swift_package_alone_does_not_imply_apple_or_macos(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            (project / "Package.swift").write_text("// portable package\n")
            source = project / "Sources" / "Library.swift"
            source.parent.mkdir()
            source.write_text("struct Library {}\n")
            self.assert_detected(project, apple=False, macos=False)
            rendered = INIT.render(
                project, ROOT, ["apple-app"], [], "standard", "AGENTS.md"
            )
            self.assertIn("<!-- BEGIN TEMPLATE: apple-app -->", rendered)
            self.assertNotIn("<!-- BEGIN TEMPLATE: macos -->", rendered)

    def test_macos_markers_complement_common_apple_profile(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            pbxproj = project / "Desktop.xcodeproj" / "project.pbxproj"
            pbxproj.parent.mkdir()
            pbxproj.write_text("fixture\n")
            text = "# Desktop\n\nA macOS AppKit application.\n"
            (project / "README.md").write_text(text)
            initialized = INIT.detect_types(project, self.manifest)
            mined, _ = UPDATE.classify(project, text, self.manifest)
            for result in (initialized, mined):
                self.assertIn("apple-app", result)
                self.assertIn("macos", result)

    def test_applescript_still_detects_desktop_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            (project / "automation.scpt").write_text("fixture\n")
            self.assert_detected(project, apple=False, macos=True)

    def test_generated_apple_instructions_preserve_local_rules(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            pbxproj = project / "App.xcodeproj" / "project.pbxproj"
            pbxproj.parent.mkdir()
            pbxproj.write_text("fixture\n")
            (project / "AGENTS.md").write_text(
                "<!-- BEGIN PROJECT LOCAL -->\n"
                "- Preserve this local SDK contract.\n"
                "<!-- END PROJECT LOCAL -->\n"
            )
            rendered = INIT.render(project, ROOT, [], [], "standard", "AGENTS.md")
            self.assertEqual(rendered.count("<!-- BEGIN TEMPLATE: apple-app -->"), 1)
            self.assertIn("Preserve this local SDK contract.", rendered)
            self.assertIn("${HOME}/AGENTS.md", rendered)
            self.assertNotIn(str(Path.home()), rendered)
            (project / "AGENTS.md").write_text(rendered)
            self.assert_detected(project, apple=True, macos=False)
            mined, _ = UPDATE.classify(project, rendered, self.manifest)
            self.assertIn("apple-app", mined)
            self.assertNotIn("macos", mined)


if __name__ == "__main__":
    unittest.main()
