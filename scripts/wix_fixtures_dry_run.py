#!/usr/bin/env python3
"""Read-only reconciliation of completed Southern League results against a Wix CMS CSV export.

Usage:
  python scripts/wix_fixtures_dry_run.py --wix-csv fixtures-export.csv --results-json public/data.json

Never writes to Wix. Produces a JSON report on stdout.
"""
import argparse
import csv
import json
import re
from pathlib import Path


def norm(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").casefold())


ALIASES = {
    "dorchester": "dorchestertown",
    "portlandutd": "portlandunited",
    "swindonsm": "swindonsupermarine",
    "weymouthfc": "weymouth",
    "westbury": "westburyunited",
    "slimbridgeafc": "slimbridge",
    "bideford": "bidefordafc",
    "hungerford": "hungerfordtown",
}


def team_key(name):
    key = norm(name)
    return ALIASES.get(key, key)


def cms_date(row):
    raw = row.get("Date") or row.get("date") or ""
    return raw[:10]


def cms_homeaway(row):
    return (row.get("HomeAway") or row.get("homeAway") or "").strip().upper()[:1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wix-csv", required=True, type=Path)
    parser.add_argument("--results-json", type=Path, default=Path("public/data.json"))
    args = parser.parse_args()
    with args.results_json.open(encoding="utf-8") as handle:
        source = json.load(handle)
    with args.wix_csv.open(encoding="utf-8-sig", newline="") as handle:
        cms_rows = list(csv.DictReader(handle))

    # Only compare Southern League matches; cup ties can share an opponent and date.
    league = [r for r in cms_rows if norm(r.get("Competition", "")) in
              {"sld1s", "southernleaguedivisiononesouth"}]
    by_key = {}
    for row in league:
        key = (cms_date(row), team_key(row.get("Opposition")), cms_homeaway(row))
        by_key.setdefault(key, []).append(row)
    suggestions = []
    unmatched = []
    no_dates = []
    for result in source.get("results", []):
        if team_key(result.get("home")) == "tivertontown":
            side, opp = "H", result.get("away")
        elif team_key(result.get("away")) == "tivertontown":
            side, opp = "A", result.get("home")
        else:
            continue
        date = result.get("date")
        if not date:
            no_dates.append({"opposition": opp, "side": side, "score": result.get("score")})
            continue
        key = (date, team_key(opp), side)
        candidates = by_key.get(key, [])
        if len(candidates) != 1:
            unmatched.append({"date": date, "opposition": opp, "side": side,
                              "reason": "missing" if not candidates else "ambiguous"})
            continue
        row = candidates[0]
        official = result.get("score", "")
        existing = row.get("Result", "")
        # Scores are home-away; preserve CMS notation and never infer scorers.
        if official and norm(official) not in norm(existing):
            suggestions.append({
                "date": date, "opposition": opp, "side": side,
                "cmsResult": existing, "officialHomeAwayScore": official,
                "action": "REVIEW_ONLY",
                "note": "Check the result and W/D/L before any CMS update; scorers are untouched.",
            })
    print(json.dumps({
        "mode": "DRY_RUN_NO_WRITES",
        "cmsRows": len(cms_rows), "cmsLeagueRows": len(league),
        "officialResults": len(source.get("results", [])),
        "review": suggestions, "unmatched": unmatched,
        "missingOfficialDates": no_dates,
        "warning": "A match appearing unmatched is NOT permission to create or overwrite an item.",
    }, indent=2))


if __name__ == "__main__":
    main()
