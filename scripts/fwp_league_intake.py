#!/usr/bin/env python3
"""Read-only FWP Division One South intake and validation.

This deliberately NEVER writes the published results or programme files.
GitHub Actions must supply FWP_API_KEY as an encrypted repository secret.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.footballwebpages.co.uk/v2/"
COMPETITION = 10
TIVERTON = 180
OUTPUT = Path("staging/fwp")
USER_AGENT = "TivertonTownDataEngine/0.1"


def get_json(endpoint):
    key = os.environ.get("FWP_API_KEY", "")
    if not key:
        raise RuntimeError("FWP_API_KEY is not set. No request attempted.")
    request = urllib.request.Request(
        API + endpoint,
        headers={
            "FWP-API-Key": key,
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(request, timeout=35) as response:
        if response.status != 200:
            raise RuntimeError("FWP returned HTTP " + str(response.status))
        return json.load(response)


def normalize_match(match):
    home, away = match.get("home-team") or {}, match.get("away-team") or {}
    status = match.get("status") or {}
    return {
        "match_id": match.get("id"),
        "competition_id": (match.get("competition") or {}).get("id"),
        "date": match.get("date"),
        "time": match.get("time"),
        "home_id": home.get("id"),
        "home": home.get("name"),
        "away_id": away.get("id"),
        "away": away.get("name"),
        "home_goals": home.get("score"),
        "away_goals": away.get("score"),
        "status": status.get("short"),
    }


def validate(matches, teams):
    problems = []
    team_ids = {str(t.get("id")) for t in teams if t.get("id") is not None}
    if len(team_ids) != 22:
        problems.append(f"Expected 22 unique league teams, found {len(team_ids)}")
    if str(TIVERTON) not in team_ids:
        problems.append("Tiverton Town team ID 180 missing from league")
    if not matches:
        problems.append("No league fixtures returned")
    seen = set()
    for match in matches:
        mid = match.get("match_id")
        home, away = str(match.get("home_id")), str(match.get("away_id"))
        if mid is None or mid in seen:
            problems.append(f"Missing/duplicate match ID: {mid}")
        seen.add(mid)
        if home == away or home not in team_ids or away not in team_ids:
            problems.append(f"Invalid clubs for match {mid}")
        if match.get("status") == "FT":
            hg, ag = match.get("home_goals"), match.get("away_goals")
            if not isinstance(hg, int) or not isinstance(ag, int) or hg < 0 or ag < 0:
                problems.append(f"Invalid final score for match {mid}")
        if match.get("competition_id") not in (None, COMPETITION):
            problems.append(f"Wrong competition for match {mid}")
    return sorted(set(problems))


def main():
    now = datetime.now(timezone.utc).isoformat()
    league = get_json(f"fixtures-results.json?comp={COMPETITION}")
    teams_response = get_json(f"teams.json?comp={COMPETITION}")
    matches = (league.get("fixtures-results") or {}).get("matches")
    teams = teams_response.get("teams")
    if not isinstance(matches, list) or not isinstance(teams, list):
        raise RuntimeError("Unexpected FWP schema; intake safely halted")
    normalized = [normalize_match(m) for m in matches]
    problems = validate(normalized, teams)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "schema_version": 1,
        "source": "FWP",
        "competition_id": COMPETITION,
        "retrieved_utc": now,
        "teams": [{"id": t.get("id"), "name": t.get("full-name")} for t in teams],
        "matches": normalized,
    }
    (OUTPUT / "league-snapshot.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    report = {
        "retrieved_utc": now,
        "status": "review_required" if problems else "source_a_valid",
        "matches": len(normalized),
        "finished_matches": sum(m["status"] == "FT" for m in normalized),
        "problems": problems,
        "source_b_checked": False,
        "published": False,
        "note": "Source A only. Southern League independent reconciliation and editorial checks pending.",
    }
    (OUTPUT / "validation-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 2 if problems else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ValueError, KeyError, urllib.error.URLError) as exc:
        print("FWP intake failed safely: " + str(exc), file=sys.stderr)
        sys.exit(1)
