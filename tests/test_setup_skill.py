import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/learning-podcast-setup/SKILL.md"
NOTION = ROOT / "skills/learning-podcast/references/notion.md"
THEMES = [
    "People & Culture", "Leadership & Communication", "AI & Technology", "Career",
    "Data & Analytics", "Garden & Plants", "Home & Cooking", "3D Printing", "Personal Development",
]


def notion_properties():
    text = NOTION.read_text(encoding="utf-8")
    table = text.split("## Properties", 1)[1].split("\n\n", 2)[1]
    names = []
    for line in table.splitlines()[2:]:
        match = re.match(r"\| ([^|]+) \|", line)
        if match:
            names.append(match.group(1).strip())
    return names


class SetupSkillTest(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

    def test_frontmatter(self):
        self.assertRegex(self.text, r"(?m)^name: learning-podcast-setup$")
        description = re.search(r"(?m)^description: (.+)$", self.text).group(1)
        self.assertTrue(description.startswith("Use when"), description)
        self.assertIn("the user", description)

    def test_lists_the_nine_starter_themes(self):
        for theme in THEMES:
            with self.subTest(theme=theme):
                self.assertIn(theme, self.text)

    def test_lists_every_notion_property(self):
        properties = notion_properties()
        self.assertGreaterEqual(len(properties), 10)
        for name in properties + ["Created"]:
            with self.subTest(property=name):
                self.assertIn(name, self.text)

    def test_every_default_is_a_keep_it_question(self):
        self.assertGreaterEqual(len(re.findall(r"keep it\?", self.text)), 4)
        for needle in ("English", "Me", "NAMES"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.text)


if __name__ == "__main__":
    unittest.main()
