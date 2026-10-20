"""Regression tests for the read-only Wix fixture reconciler."""
import unittest
from wix_fixtures_dry_run import compare, result_view, canon

class FixturesSyncTests(unittest.TestCase):
    def test_home_score(self):
        self.assertEqual(result_view("H", "3-1"), "W 3-1")

    def test_away_score(self):
        self.assertEqual(result_view("A", "1-4"), "W 4-1")
        self.assertEqual(result_view("A", "4-1"), "L 1-4")

    def test_alias(self):
        self.assertEqual(canon("BIDEFORD AFC"), canon("Bideford"))

    def test_separate_cup_and_league(self):
        wix = [
            {"ID":"league","Date":"2026-10-20T12:00:00Z","Opposition":"Bideford AFC",
             "HomeAway":"H","Competition":"SLD1S","Result":"P-P"},
            {"ID":"cup","Date":"2026-10-20T12:00:00Z","Opposition":"Bideford AFC",
             "HomeAway":"H","Competition":"ST LUKE'S CUP","Result":""},
        ]
        feed = {"results":[{"date":"2026-10-20","home":"Tiverton Town",
                            "away":"Bideford","score":"2-1"}]}
        report = compare(wix, feed)
        self.assertEqual(report["proposedChanges"][0]["wixId"], "league")
        self.assertEqual(report["proposedChanges"][0]["suggested"], "W 2-1")
        self.assertEqual(len(report["proposedChanges"]), 1)

if __name__ == "__main__":
    unittest.main()
