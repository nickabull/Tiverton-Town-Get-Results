#!/usr/bin/env python3
"""Read-only comparison of Wix CMS export with Get Results JSON. No Wix writes."""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict

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

def canon(value):
    key = re.sub(r"[^a-z0-9]", "", str(value or "").casefold())
    return ALIASES.get(key, key)

def is_league(value):
    return canon(value) in {"sld1s", "southernleaguedivisiononesouth", "southernleagued1south"}

def result_view(side, score):
    match = re.fullmatch(r"\s*(\d+)\s*[-–:]\s*(\d+)\s*", str(score or ""))
    if not match:
        return None
    home, away = map(int, match.groups())
    ours, theirs = (home, away) if side == "H" else (away, home)
    outcome = "W" if ours > theirs else ("D" if ours == theirs else "L")
    return f"{outcome} {ours}-{theirs}"

def compare(wix_rows, source):
    identifiers = Counter(row.get("ID", "") for row in wix_rows)
    keys = defaultdict(list)
    for row in wix_rows:
        if is_league(row.get("Competition")):
            keys[(str(row.get("Date", ""))[:10],
                  canon(row.get("Opposition")),
                  str(row.get("HomeAway", "")).strip().upper())].append(row)

    changes, unchanged, unmatched, undated = [], [], [], []
    for item in source.get("results", []):
        if canon(item.get("home")) == "tivertontown":
            side, opposition = "H", item.get("away")
        elif canon(item.get("away")) == "tivertontown":
            side, opposition = "A", item.get("home")
        else:
            continue

        when = str(item.get("date") or "")[:10]
        if not when:
            undated.append({"opposition": opposition, "score": item.get("score")})
            continue

        matches = keys.get((when, canon(opposition), side), [])
        if len(matches) != 1:
            unmatched.append({
                "date": when, "opposition": opposition, "homeAway": side,
                "reason": "missing" if not matches else "ambiguous"
            })
            continue

        record = matches[0]
        actual = (record.get("Result") or "").strip()
        expected = result_view(side, item.get("score"))
        if expected is None:
            unmatched.append({"date": when, "opposition": opposition, "reason": "invalid score"})
        elif actual.casefold() == expected.casefold():
            unchanged.append({"wixId": record.get("ID"), "date": when})
        else:
            changes.append({
                "wixId": record.get("ID"), "date": when, "opposition": opposition,
                "homeAway": side, "current": actual,
                "suggested": expected, "action": "REVIEW_ONLY"
            })

    return {
        "mode": "DRY_RUN_NO_WRITES",
        "wixRows": len(wix_rows),
        "leagueRows": sum(is_league(r.get("Competition")) for r in wix_rows),
        "duplicateIds": [i for i, n in identifiers.items() if not i or n > 1],
        "duplicateLeagueKeys": [list(k) for k, v in keys.items() if len(v) > 1],
        "unchanged": unchanged, "proposedChanges": changes,
        "unmatchedResults": unmatched, "undatedSourceResults": undated,
        "warning": "No suggested changes may be written without verification."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wix-csv", required=True)
    parser.add_argument("--results-json", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    with open(args.wix_csv, newline="", encoding="utf-8-sig") as file:
        wix_rows = list(csv.DictReader(file))
    with open(args.results_json, encoding="utf-8") as file:
        source = json.load(file)
    report = json.dumps(compare(wix_rows, source), indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(report + "\n")
    else:
        print(report)

if __name__ == "__main__":
    main()
