# Tivvy Data Centre — seven-day automatic match completion

## Goal
Any finished league fixture, on **any day**, should propagate once to a shared, verified results data set. Both the Wix Match Centre and Programme Centre must consume the same published revision. This is event-driven by newly completed matches, not a "Saturday round" cutoff.

## Existing components (14 November 2026)
- `.github/workflows/update-and-deploy.yml` already rebuilds the public Get Results website **hourly**, using Football Web Pages public grid/results and Tivvy Archive league table. This rebuild is not the verified multi-source publish gate.
- `.github/workflows/fwp-league-staging.yml` runs **daily**: 12:17, 12:47 … 23:47 UTC and overnight 00:17–11:17 UTC. It obtains the authenticated FWP competition **10** snapshot using the encrypted `FWP_API_KEY` GitHub Actions secret when present, validates match IDs, team IDs, status and scores, and saves downloadable 30-day staging artifacts. **It does not publish matches**, by design.
- Existing post-match verified inputs live in `verified-results.json` and `verified-standings-2026-11-11.json` (the latter currently has an as-of date of 2026-11-14). Downstream Match Centre and Programme renderers are being aligned to these files.
- `league_reconcile.py` can advance a fully reconciled baseline, but is not yet an independently sourced automatic approval service.

## Automatic publication gate (next engineering phase; NOT ACTIVE)
1. Poll FWP competition 10 and independent Southern League API. Cover all week dates, including postponed/rearranged fixtures and days with only one game.
2. Keep an immutable fixture identity (competition + FWP match ID, mapped to Southern League ID); normalize team names with approved aliases, timestamps to Europe/London, and states: scheduled, live, FT, postponed, abandoned.
3. Detect **new FT transitions or corrections** by comparing to the last published event journal; never infer finality from a clock or from a score alone.
4. Verify FWP and Southern League agree on both team pairing and full-time score. Validate no duplicate identity, no accidental replay-overwrite, and league standings arithmetic. Where one source lags, keep the previous approved value and flag `REVIEW REQUIRED`; do not guess.
5. Create one atomic revision of canonical fixtures, results, standings and Tivvy match/player facts. Full table calculation requires a reconciled baseline that accounts for all results and any points deductions.
6. Publish only if validation passes and a revision changes. Consumers: Get Results public data, Wix Match Centre, Programme Centre league table, match matrix, Tivvy at a Glance, League So Far and player statistics. All previously approved visual templates stay unchanged.
7. Inspect deployed endpoints to confirm the matching revision. Emit a change audit with fixture IDs, date, old/new score, affected league rows, Git SHA and source timestamps.
8. Notify on verified publication (changed items only), validation disagreement, or deployment error. No-change runs stay quiet. Approved editorial/report text and native Canva design stay in guided/manual workflow.

## Next build tasks
- Implement a Southern League independent results collector and normalization fixtures with sample payloads.
- Connect FWP staging snapshots and independent Southern League snapshots to the **same** reconciliation job.
- Unit-test FT, postponement, abandonment, correction, single-game weekday, points deductions, source lag and duplicate rows.
- Add an allowlisted, atomic publication job with idempotency and rollback.
- Replace individual ad-hoc snapshot overlays with a single canonical published revision identifier.
- Verify GitHub `FWP_API_KEY` secret availability via workflow execution (cannot inspect secret contents via connector).
- Test actual live deployment and source agreement before enabling automatic writeback.

**Operational rule:** Never confuse scheduled read-only data intake with a successfully verified, deployed public update.
