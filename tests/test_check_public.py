import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-public.sh"

LEAKS = {
    "home path": "see /Users/jane/project",
    "32-char id": "id 0123456789abcdef0123456789abcdef here",
    "collection url": "collection://abc-123",
    "notion page url": "https://app.notion.com/p/abc",
    "notion.so url": "https://www.notion.so/page",
    "gmail address": "write to someone@gmail.com",
    "old fixture name": "the Sedova interview",
    "old guest name": "guest Šedivá",
}


def run(root):
    return subprocess.run(["sh", str(SCRIPT), str(root)], capture_output=True, text=True)


class CheckPublicTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="leak check ")
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_tree_passes(self):
        (self.root / "ok.md").write_text("Nothing personal here. A 40-char sha "
                                         "0123456789abcdef0123456789abcdef01234567 is fine.\n")
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_each_pattern_is_reported_with_path_and_line(self):
        for label, text in LEAKS.items():
            with self.subTest(label=label):
                path = self.root / "leak.md"
                path.write_text("first line\n" + text + "\n")
                result = run(self.root)
                self.assertEqual(result.returncode, 1, label)
                self.assertIn("leak.md:2", result.stdout)
                path.unlink()

    def test_excluded_paths_are_not_scanned(self):
        for rel in (".git/config", ".superpowers/note.md", "scripts/check-public.sh",
                    "tests/test_check_public.py"):
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("/Users/jane someone@gmail.com\n")
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
