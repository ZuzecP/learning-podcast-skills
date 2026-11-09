import json
import subprocess
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


class FolderTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()


class ReadTest(FolderTestCase):
    def test_read_card_roundtrip(self):
        card = sample(theme="People & Culture", **{"for": "a: b"},
                      tags=["c#", "plain"], notebook="", first_time_topic=False)
        path = cards.write_card(self.folder, card)
        got = cards.read_card(path)
        self.assertEqual(got["name"], "Psychological safety")
        self.assertEqual(got["theme"], "People & Culture")
        self.assertEqual(got["for"], "a: b")
        self.assertEqual(got["tags"], ["c#", "plain"])
        self.assertIs(got["first_time_topic"], False)
        self.assertEqual(got["notebook"], "")
        self.assertEqual(got["summary"], "A short summary.")

    def test_read_card_unescapes_quotes(self):
        path = cards.write_card(self.folder, sample(theme='say "hi"'))
        self.assertEqual(cards.read_card(path)["theme"], 'say "hi"')


class ScanFindTest(FolderTestCase):
    def setUp(self):
        super().setUp()
        cards.write_card(self.folder, sample(name="Alpha", theme="Career", tags=["b", "a"], **{"for": "Me"}))
        cards.write_card(self.folder, sample(name="Beta", theme="Career", tags=["a", "c"], **{"for": "Sam"},
                                             summary="Talks about Garden soil."))

    def test_scan_collects_distinct_sorted_values(self):
        got = cards.scan(self.folder)
        self.assertEqual(got["themes"], ["Career"])
        self.assertEqual(got["tags"], ["a", "b", "c"])
        self.assertEqual(got["for"], ["Me", "Sam"])
        self.assertEqual(got["names"], ["Alpha", "Beta"])

    def test_scan_skips_non_cards_and_alters_nothing(self):
        plain = self.folder / "plain.md"
        plain.write_bytes(b"just a note\n")
        other = self.folder / "other.md"
        other.write_bytes(b"---\ntitle: x\n---\nbody\n")
        cards.scan(self.folder)
        cards.find(self.folder, "x")
        self.assertEqual(plain.read_bytes(), b"just a note\n")
        self.assertEqual(other.read_bytes(), b"---\ntitle: x\n---\nbody\n")
        self.assertEqual(cards.scan(self.folder)["names"], ["Alpha", "Beta"])

    def test_scan_missing_folder(self):
        with self.assertRaises(cards.CardError) as ctx:
            cards.scan(self.folder / "nope")
        self.assertEqual(ctx.exception.reason, "no_folder")

    def test_find_hits_by_name_tag_and_summary_case_insensitive(self):
        self.assertEqual([c["name"] for c in cards.find(self.folder, "ALPHA")], ["Alpha"])
        self.assertEqual([c["name"] for c in cards.find(self.folder, "c")], ["Alpha", "Beta"])
        self.assertEqual([c["name"] for c in cards.find(self.folder, "garden")], ["Beta"])
        self.assertEqual([c["name"] for c in cards.find(self.folder, "zzz garden")], ["Beta"])

    def test_find_miss(self):
        self.assertEqual(cards.find(self.folder, "zzz"), [])

    def test_find_empty_query_is_bad_input(self):
        with self.assertRaises(cards.CardError) as ctx:
            cards.find(self.folder, "  ")
        self.assertEqual(ctx.exception.reason, "bad_input")

    def test_name_info_reports_exists(self):
        self.assertEqual(cards.name_info(self.folder, "Alpha"), {"stem": "Alpha", "exists": True})
        self.assertEqual(cards.name_info(self.folder, "New: one"), {"stem": "New one", "exists": False})


class CliTest(FolderTestCase):
    def run_cli(self, *args):
        script = ROOT / "skills/learning-podcast/scripts/cards.py"
        done = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
        return done.returncode, json.loads(done.stdout)

    def test_name_write_and_refusals(self):
        code, out = self.run_cli("name", "--folder", str(self.folder), "--name", "X: y")
        self.assertEqual((code, out["ok"], out["stem"], out["exists"]), (0, True, "X y", False))
        card_file = self.folder.parent / (self.folder.name + "-card.json")
        card_file.write_text(json.dumps(sample(name="X: y")), encoding="utf-8")
        try:
            code, out = self.run_cli("write", "--folder", str(self.folder), "--card", str(card_file))
            self.assertEqual((code, out["ok"]), (0, True))
            self.assertTrue((self.folder / "X y.md").is_file())
            code, out = self.run_cli("write", "--folder", str(self.folder), "--card", str(card_file))
            self.assertEqual((code, out["ok"], out["reason"]), (2, False, "exists"))
        finally:
            card_file.unlink()

    def test_scan_and_find_commands(self):
        cards.write_card(self.folder, sample(name="Alpha"))
        code, out = self.run_cli("scan", "--folder", str(self.folder))
        self.assertEqual((code, out["ok"], out["names"]), (0, True, ["Alpha"]))
        code, out = self.run_cli("find", "--folder", str(self.folder), "--query", "alpha")
        self.assertEqual((code, out["ok"], [c["name"] for c in out["cards"]]), (0, True, ["Alpha"]))

    def test_relative_folder_and_bad_arguments_are_bad_input(self):
        code, out = self.run_cli("scan", "--folder", "relative/path")
        self.assertEqual((code, out["reason"]), (2, "bad_input"))
        code, out = self.run_cli("scan")
        self.assertEqual((code, out["reason"]), (2, "bad_input"))

    def test_unreadable_card_json_is_bad_input(self):
        bad = self.folder / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        code, out = self.run_cli("write", "--folder", str(self.folder), "--card", str(bad))
        self.assertEqual((code, out["reason"]), (2, "bad_input"))


if __name__ == "__main__":
    unittest.main()
