import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/learning-podcast/scripts"))
import cards  # noqa: E402


def sample(**over):
    card = {
        "name": "Psychological safety",
        "theme": "People & Culture",
        "tags": ["teams", "trust"],
        "for": "Me",
        "scenario": "Single",
        "source_types": ["Article"],
        "format": "Deep Dive",
        "length": "Default",
        "first_time_topic": True,
        "notebook": "https://example.com/notebook/1",
        "created": "2026-11-09T12:00:00",
        "summary": "A short summary.",
        "sources": [
            {"title": "An article", "url": "https://example.com/a", "type": "Article",
             "origin": "You", "in_out": "In", "reason": "the user's link"},
        ],
        "prompt": "Focus on the practical side.",
        "run_notes": ["none"],
    }
    card.update(over)
    return card


EXPECTED = """---
theme: "People & Culture"
tags:
  - teams
  - trust
for: Me
scenario: Single
source_types:
  - Article
format: Deep Dive
length: Default
first_time_topic: true
notebook: "https://example.com/notebook/1"
created: "2026-11-09T12:00:00"
---

## Summary
A short summary.
## Sources
| Source | Type | Origin | In or out | Reason |
|---|---|---|---|---|
| [An article](https://example.com/a) | Article | You | In | the user's link |
## Prompt used
```text
Focus on the practical side.
```
## Run notes
- none
"""


class SanitizeTest(unittest.TestCase):
    def test_sanitize_replaces_forbidden_characters(self):
        self.assertEqual(cards.sanitize_name('A: b/c?'), "A b c")

    def test_sanitize_rejects_empty(self):
        with self.assertRaises(cards.CardError) as ctx:
            cards.sanitize_name("///")
        self.assertEqual(ctx.exception.reason, "bad_input")

    def test_sanitize_strips_leading_dots(self):
        self.assertEqual(cards.sanitize_name("../x"), "x")


class YamlScalarTest(unittest.TestCase):
    def test_quotes_risky_values_only(self):
        self.assertEqual(cards.yaml_scalar("People & Culture"), '"People & Culture"')
        self.assertEqual(cards.yaml_scalar("3D"), "3D")
        self.assertEqual(cards.yaml_scalar("2026"), '"2026"')
        self.assertEqual(cards.yaml_scalar("yes"), '"yes"')
        self.assertEqual(cards.yaml_scalar('a "q"'), '"a \\"q\\""')
        self.assertEqual(cards.yaml_scalar(True), "true")
        self.assertEqual(cards.yaml_scalar(False), "false")


class RenderTest(unittest.TestCase):
    def test_render_card_exact(self):
        self.assertEqual(cards.render_card(sample()), EXPECTED)

    def test_length_omitted_and_empty_notebook(self):
        text = cards.render_card(sample(length="", notebook="", tags=[]))
        self.assertNotIn("length:", text)
        self.assertIn("\nnotebook:\n", text)
        self.assertIn("\ntags: []\n", text)

    def test_table_escapes_pipe_and_newline(self):
        src = {"title": "a|b", "url": "", "type": "Paper", "origin": "Claude",
               "in_out": "Out", "reason": "line one\nline two | x"}
        text = cards.render_card(sample(sources=[src]))
        self.assertIn("| a\\|b | Paper | Claude | Out | line one line two \\| x |", text)

    def test_empty_run_notes_say_none(self):
        self.assertIn("## Run notes\n- none\n", cards.render_card(sample(run_notes=[])))


class WriteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_write_card_creates_file_named_by_stem(self):
        path = cards.write_card(self.folder, sample(name="A: b"))
        self.assertEqual(path, self.folder / "A b.md")
        self.assertEqual(path.read_text(encoding="utf-8"), cards.render_card(sample(name="A: b")))

    def test_write_card_refuses_overwrite(self):
        cards.write_card(self.folder, sample())
        path = self.folder / "Psychological safety.md"
        before = path.read_bytes()
        with self.assertRaises(cards.CardError) as ctx:
            cards.write_card(self.folder, sample(summary="changed"))
        self.assertEqual(ctx.exception.reason, "exists")
        self.assertEqual(path.read_bytes(), before)

    def test_write_card_refuses_missing_folder(self):
        with self.assertRaises(cards.CardError) as ctx:
            cards.write_card(self.folder / "nope", sample())
        self.assertEqual(ctx.exception.reason, "no_folder")

    def test_traversal_name_stays_inside_the_folder(self):
        path = cards.write_card(self.folder, sample(name="../x"))
        self.assertEqual(path.parent, self.folder)
        self.assertFalse((self.folder.parent / "x.md").exists())

    def test_missing_required_key_is_bad_input(self):
        card = sample()
        del card["theme"]
        with self.assertRaises(cards.CardError) as ctx:
            cards.write_card(self.folder, card)
        self.assertEqual(ctx.exception.reason, "bad_input")


if __name__ == "__main__":
    unittest.main()
