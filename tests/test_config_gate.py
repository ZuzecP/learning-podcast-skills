import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LP = ROOT / "skills/learning-podcast"


def read(path):
    return path.read_text(encoding="utf-8")


class ConfigGateTest(unittest.TestCase):
    def test_run_gate_in_skill(self):
        text = read(LP / "SKILL.md")
        for needle in ("learning-podcast.config.json", "setup_completed", "REPLACE-ME", "learning-podcast-setup"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_language_comes_from_config_with_english_fallback(self):
        text = read(LP / "references/notebooklm.md")
        self.assertIn("`language`", text)
        self.assertIn("English", text)

    def test_failures_cover_the_gate_rows(self):
        text = read(LP / "references/failures.md")
        for needle in ("REPLACE-ME", "unreachable", "Language"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_prompt_skill_reads_names_rule_and_rules_file(self):
        text = read(ROOT / "skills/podcast-prompt/SKILL.md")
        self.assertIn("names_rule", text)
        self.assertIn("rules_file", text)
        self.assertIn("--rules", text)


if __name__ == "__main__":
    unittest.main()
