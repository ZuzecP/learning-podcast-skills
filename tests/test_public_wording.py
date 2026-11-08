import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_FILES = sorted((ROOT / "skills").rglob("*.md"))
SKILL_MDS = sorted((ROOT / "skills").glob("*/SKILL.md"))


class PublicWordingTest(unittest.TestCase):
    def test_skills_exist(self):
        self.assertTrue(SKILL_MDS)

    def test_no_gendered_or_personal_wording(self):
        pattern = re.compile(r"\b(her|hers|she|zuzana)\b", re.IGNORECASE)
        for path in SKILL_FILES:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                with self.subTest(file=path.relative_to(ROOT).as_posix(), line=number):
                    self.assertIsNone(pattern.search(line), line)

    def test_no_personal_paths(self):
        pattern = re.compile("Learning & Development|/Use" + "rs/|" + r"\$HOME/Claude")
        for path in SKILL_FILES:
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                with self.subTest(file=path.relative_to(ROOT).as_posix(), line=number):
                    self.assertIsNone(pattern.search(line), line)

    def test_descriptions_are_trigger_only_and_generic(self):
        for path in SKILL_MDS:
            text = path.read_text(encoding="utf-8")
            description = re.search(r"^description: (.+)$", text, re.MULTILINE).group(1)
            with self.subTest(skill=path.parent.name):
                self.assertTrue(description.startswith("Use when"), description)
                self.assertIn("the user", description)


if __name__ == "__main__":
    unittest.main()
