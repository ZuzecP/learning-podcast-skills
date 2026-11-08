import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LayoutTest(unittest.TestCase):
    def test_skill_folders_exist(self):
        for rel in ("skills/podcast-prompt/scripts", "skills/learning-podcast/scripts"):
            with self.subTest(rel=rel):
                self.assertTrue((ROOT / rel).is_dir())

    def test_docs_exist(self):
        for rel in ("README.md", "CHANGELOG.md", "LICENSE", "CONTRIBUTING.md"):
            with self.subTest(rel=rel):
                self.assertTrue((ROOT / rel).is_file())


if __name__ == "__main__":
    unittest.main()
