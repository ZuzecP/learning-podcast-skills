import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = [
    "Prerequisites", "Install", "Set up", "Use", "Configuration",
    "Limitations", "License / usage terms", "Contributing",
]


class ReadmeTest(unittest.TestCase):
    def setUp(self):
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_headings_are_present_and_in_order(self):
        found = re.findall(r"(?m)^## (.+)$", self.readme)
        positions = [found.index(h) for h in HEADINGS]
        self.assertEqual(positions, sorted(positions))

    def test_states_notion_is_the_only_backend(self):
        self.assertRegex(self.readme, r"(?i)notion only|only (storage )?backend|only supports? notion")

    def test_says_where_language_and_rules_are_set(self):
        for needle in ("`language`", "rules.local.md", "learning-podcast.config.json", "scripts/install.sh"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.readme)

    def test_license_section_names_cc_by_nc(self):
        self.assertIn("CC BY-NC 4.0", self.readme)

    def test_changelog_starts_with_v1_0(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        first = re.findall(r"(?m)^## (.+)$", text)[0]
        self.assertTrue(first.startswith("v1.0"), first)

    def test_docs_exist(self):
        for rel in ("docs/how-it-works.md", "docs/measured-facts.md"):
            with self.subTest(rel=rel):
                self.assertTrue((ROOT / rel).is_file())


if __name__ == "__main__":
    unittest.main()
