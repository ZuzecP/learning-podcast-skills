import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/podcast-prompt/scripts"))
import assemble  # noqa: E402

FIXTURES = ROOT / "tests/fixtures"


class RulesTest(unittest.TestCase):
    def test_rules_file_has_every_text_and_a_measured_limit(self):
        texts, limit = assemble.load_rules()
        self.assertEqual(sorted(texts), sorted(assemble.REQUIRED_TEXTS))
        self.assertIsInstance(limit, int)

    def test_examples_match_the_rules(self):
        # After a wording change, regenerate the fixtures (README, "Tests") and review the diff.
        cases = [
            ("example-deep-dive.txt", dict(fmt="Deep Dive", names=True, first_time=True)),
            ("example-brief.txt", dict(fmt="Brief", names=True)),
        ]
        for name, kwargs in cases:
            with self.subTest(example=name):
                block, cuts = assemble.assemble(**kwargs)
                self.assertEqual(cuts, [])
                self.assertEqual(block, (FIXTURES / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
