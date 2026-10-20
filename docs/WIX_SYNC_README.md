# Wix Fixtures Sync — safe first stage

This branch introduces a **read-only** comparison script. It does not update Wix.

## Inputs
- Current Get Results output: `public/data.json` (produced by `python update_online.py`).
- Wix CMS export as CSV with columns `Date,Opposition,HomeAway,Competition,Result` plus the existing optional columns.

## Run
```bash
python update_online.py
python scripts/wix_fixtures_dry_run.py --wix-csv path/to/wix-export.csv --results-json public/data.json > comparison.json
```
Only league results are compared. A single matching fixture must agree on date, opponent and home/away. Missing and ambiguous fixtures are reported, **never** inserted automatically. Cup matches, friendlies, postponed ties, scorer details, and fixture rearrangements require separate source reconciliation.

## Next steps before any Wix writes
1. Export the current Wix CMS collection and inspect its actual field keys.
2. Run comparison and review each difference, correcting any date/name mismatches.
3. Extend the source feed to cover future fixtures as well as completed results. Treat Southern League as authoritative; Football Web Pages is currently the updater's source, not the league's own API.
4. Add explicit competition keys, stable IDs, manual-override flags, and conflict rules.
5. Obtain secure Wix authentication for the chosen GitHub Actions workflow (store as GitHub Actions secrets, never commit tokens).
6. Test one controlled item in Wix, then implement idempotent updates with dry-run as the default and logs.

**Do not merge or schedule Wix writes yet.** The existing GitHub Action continues independently on the main branch.
