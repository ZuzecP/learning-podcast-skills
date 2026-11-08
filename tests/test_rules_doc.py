import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/podcast-prompt/scripts"))
import assemble  # noqa: E402

RULES = ROOT / "skills/podcast-prompt/references/rules.md"


class RulesDocTest(unittest.TestCase):
    def test_every_rule_has_a_rationale(self):
        text = RULES.read_text(encoding="utf-8")
        self.assertIn("## Why each rule exists", text)
        section = text.split("## Why each rule exists", 1)[1].split("\n## ", 1)[0]
        for label in assemble.ORDER:
            with self.subTest(label=label):
                self.assertIn(label, section)

    def test_names_is_documented_as_optional(self):
        text = RULES.read_text(encoding="utf-8")
        self.assertIn("names_rule", text)


if __name__ == "__main__":
    unittest.main()
