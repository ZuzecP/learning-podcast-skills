import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/podcast-prompt/scripts"))
import assemble  # noqa: E402

MINI_RULES = """# Rules

Instruction box limit: 5000 characters (test)

## Section texts

NAMES: Use simple names.
TONE: Calm.
FACTS: Sources only.
BRIEF: Brisk.
DEPTH: Go deep.
LEVELS: Junior, mid, senior.
ACTIONS: Three steps.
GAPS: Name the gaps.
GAPS (brief): The single most important gap.
STUDY FURTHER: Three places.
"""


def labels(block):
    return [line.split(":", 1)[0] for line in block.splitlines()]


class AssembleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.rules = Path(cls.tmp.name) / "rules.md"
        cls.rules.write_text(MINI_RULES, encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def build(self, fmt="Deep Dive", **kw):
        return assemble.assemble(fmt, rules_path=self.rules, **kw)

    def test_full_first_time_has_every_full_section_in_order(self):
        block, cuts = self.build(names=True, first_time=True)
        self.assertEqual(
            labels(block),
            ["NAMES", "TONE", "FACTS", "DEPTH", "LEVELS", "ACTIONS", "GAPS", "STUDY FURTHER"],
        )
        self.assertEqual(cuts, [])

    def test_texts_are_copied_verbatim(self):
        block, _ = self.build(names=True)
        self.assertIn("NAMES: Use simple names.\n", block)
        self.assertIn("TONE: Calm.\n", block)

    def test_names_only_when_asked(self):
        block, _ = self.build()
        self.assertEqual(labels(block)[0], "TONE")

    def test_study_further_only_for_first_time(self):
        block, _ = self.build("Critique")
        self.assertNotIn("STUDY FURTHER", labels(block))

    def test_brief_gets_the_reduced_set_and_brief_gaps(self):
        block, _ = self.build("Brief", names=True, first_time=True)
        self.assertEqual(labels(block), ["NAMES", "TONE", "FACTS", "BRIEF", "GAPS"])
        self.assertIn("GAPS: The single most important gap.\n", block)

    def test_cuts_skip_sections_the_block_does_not_have(self):
        full, _ = self.build(names=True)
        block, cuts = self.build(names=True, limit=len(full) - 1)
        self.assertEqual(cuts, ["ACTIONS"])
        self.assertNotIn("ACTIONS", labels(block))

    def test_brief_cuts_start_at_gaps(self):
        full, _ = self.build("Brief", names=True)
        _, cuts = self.build("Brief", names=True, limit=len(full) - 1)
        self.assertEqual(cuts, ["GAPS"])

    def test_cuts_follow_the_order(self):
        _, cuts = self.build(names=True, first_time=True, limit=100)
        self.assertEqual(cuts, assemble.CUT_ORDER[: len(cuts)])
        self.assertGreater(len(cuts), 1)

    def test_core_is_never_cut(self):
        with self.assertRaises(ValueError):
            self.build(names=True, limit=20)

    def test_limit_comes_from_rules(self):
        _, limit = assemble.load_rules(self.rules)
        self.assertEqual(limit, 5000)

    def test_missing_text_is_an_error(self):
        broken = Path(self.tmp.name) / "broken.md"
        broken.write_text(MINI_RULES.replace("FACTS: Sources only.\n", ""), encoding="utf-8")
        with self.assertRaises(ValueError):
            assemble.load_rules(broken)

    def test_unknown_format(self):
        with self.assertRaises(ValueError):
            self.build("Panel")


class CliTest(unittest.TestCase):
    def run_main(self, argv):
        from io import StringIO
        from contextlib import redirect_stdout, redirect_stderr

        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = assemble.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_names_flag_and_notes(self):
        code, out, err = self.run_main(["--format", "Brief", "--names"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("NAMES: "))
        self.assertIn("cuts: none", err)

    def test_no_names_line_without_the_flag(self):
        _, out, _ = self.run_main(["--format", "Brief"])
        self.assertNotIn("NAMES: ", out)

    def test_too_long_exits_2(self):
        code, out, err = self.run_main(["--format", "Brief", "--limit", "20"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("too long even after all cuts", err)


if __name__ == "__main__":
    unittest.main()
