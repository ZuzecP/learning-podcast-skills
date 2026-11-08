import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install.sh"
SKILLS = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())


def run(project, *flags):
    return subprocess.run(["sh", str(SCRIPT), *flags, str(project)], capture_output=True, text=True)


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="install test ")
        self.project = Path(self.tmp.name) / "my project"
        self.project.mkdir()
        self.skills = self.project / ".claude" / "skills"

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_links_for_every_skill(self):
        result = run(self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreaterEqual(len(SKILLS), 3)
        for name in SKILLS:
            with self.subTest(skill=name):
                link = self.skills / name
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), (ROOT / "skills" / name).resolve())

    def test_second_run_changes_nothing(self):
        run(self.project)
        before = {n: os.readlink(self.skills / n) for n in SKILLS}
        result = run(self.project)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {n: os.readlink(self.skills / n) for n in SKILLS})

    def test_refuses_real_directory_and_changes_nothing(self):
        target = self.skills / "learning-podcast"
        target.mkdir(parents=True)
        (target / "mine.txt").write_text("keep me")
        result = run(self.project)
        self.assertEqual(result.returncode, 1)
        self.assertTrue((target / "mine.txt").is_file())
        self.assertFalse(target.is_symlink())
        for name in SKILLS:
            if name != "learning-podcast":
                with self.subTest(skill=name):
                    self.assertFalse((self.skills / name).exists() or (self.skills / name).is_symlink())

    def test_foreign_link_needs_force(self):
        other = Path(self.tmp.name) / "elsewhere"
        other.mkdir()
        self.skills.mkdir(parents=True)
        (self.skills / "podcast-prompt").symlink_to(other)
        result = run(self.project)
        self.assertEqual(result.returncode, 1)
        self.assertEqual((self.skills / "podcast-prompt").resolve(), other.resolve())

    def test_force_repoints_foreign_link(self):
        other = Path(self.tmp.name) / "elsewhere"
        other.mkdir()
        self.skills.mkdir(parents=True)
        (self.skills / "podcast-prompt").symlink_to(other)
        result = run(self.project, "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.skills / "podcast-prompt").resolve(),
                         (ROOT / "skills" / "podcast-prompt").resolve())

    def test_missing_project_folder_exits_1(self):
        result = run(Path(self.tmp.name) / "does not exist")
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
