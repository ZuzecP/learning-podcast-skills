import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS = {"data_source_id", "database_url", "for_default", "language", "names_rule", "rules_file"}


class ConfigExampleTest(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "config.example.json").read_text(encoding="utf-8"))

    def test_has_exactly_the_documented_keys_and_no_completed_marker(self):
        self.assertEqual(set(self.config), KEYS)
        self.assertNotIn("setup_completed", self.config)

    def test_ids_are_placeholders(self):
        self.assertEqual(self.config["data_source_id"], "REPLACE-ME")
        self.assertEqual(self.config["database_url"], "REPLACE-ME")

    def test_defaults(self):
        self.assertEqual(self.config["for_default"], "Me")
        self.assertEqual(self.config["language"], "English")
        self.assertIs(self.config["names_rule"], False)
        self.assertIsNone(self.config["rules_file"])


if __name__ == "__main__":
    unittest.main()
