import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/learning-podcast/scripts"))
import length  # noqa: E402


class ChooseLengthTest(unittest.TestCase):
    def one(self, fmt="Deep Dive", **src):
        return length.choose_length([src], fmt)

    def test_conversation_threshold_60_minutes(self):
        self.assertEqual(self.one(kind="conversation", minutes=59), "Default")
        self.assertEqual(self.one(kind="conversation", minutes=60), "Long")

    def test_talk_threshold_30_minutes(self):
        self.assertEqual(self.one(kind="talk", minutes=29), "Default")
        self.assertEqual(self.one(kind="talk", minutes=30), "Long")

    def test_written_threshold_3000_words(self):
        self.assertEqual(self.one(kind="written", words=2999), "Default")
        self.assertEqual(self.one(kind="written", words=3000), "Long")

    def test_other_uses_the_unit_it_has(self):
        self.assertEqual(self.one(kind="other", minutes=70), "Long")
        self.assertEqual(self.one(kind="other", words=2000), "Default")

    def test_more_than_one_source_is_always_long(self):
        two = [{"kind": "written", "words": 500}, {"kind": "talk", "minutes": 5}]
        self.assertEqual(length.choose_length(two), "Long")

    def test_long_only_exists_for_deep_dive(self):
        for fmt in ("Critique", "Debate"):
            with self.subTest(fmt=fmt):
                self.assertEqual(self.one(fmt, kind="talk", minutes=90), "Default")

    def test_brief_has_no_length(self):
        self.assertIsNone(self.one("Brief", kind="talk", minutes=90))

    def test_errors(self):
        with self.assertRaises(ValueError):
            length.choose_length([])
        with self.assertRaises(ValueError):
            self.one(kind="talk", words=100)
        with self.assertRaises(ValueError):
            self.one(kind="video", minutes=10)
        with self.assertRaises(ValueError):
            self.one("Panel", kind="talk", minutes=10)


class ParseSourceTest(unittest.TestCase):
    def test_minutes_and_words(self):
        self.assertEqual(length.parse_source("conversation:45m"), {"kind": "conversation", "minutes": 45})
        self.assertEqual(length.parse_source("written:3200w"), {"kind": "written", "words": 3200})

    def test_bad_spec(self):
        for bad in ("talk", "talk:", "talk:45", "talk:xm"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                length.parse_source(bad)


class CliTest(unittest.TestCase):
    def run_main(self, argv):
        from io import StringIO
        from contextlib import redirect_stdout, redirect_stderr

        out = StringIO()
        with redirect_stdout(out), redirect_stderr(StringIO()):
            code = length.main(argv)
        return code, out.getvalue().strip()

    def test_cli(self):
        self.assertEqual(self.run_main(["conversation:45m"]), (0, "Default"))
        self.assertEqual(self.run_main(["talk:45m", "written:900w"]), (0, "Long"))
        self.assertEqual(self.run_main(["--format", "Brief", "talk:40m"]), (0, "none (Brief)"))
        self.assertEqual(self.run_main(["talk:abc"])[0], 2)


if __name__ == "__main__":
    unittest.main()
