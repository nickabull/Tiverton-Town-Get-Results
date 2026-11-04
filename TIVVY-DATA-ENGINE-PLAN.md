# Tivvy Data Engine — automation and notification rules

## Present status (4 November 2026)
- Read-only FWP league collector: `scripts/fwp_league_intake.py`.
- Staging workflow: `.github/workflows/fwp-league-staging.yml`.
- Requires GitHub Actions repository secret `FWP_API_KEY`; it is NOT the same as Google Apps Script Script Properties.
- This is a **staging collector**, not a production publisher. No notifications may claim website or programme updates have happened.

## Sources
A. FWP API, competition 10, Tiverton 180; stable match and player identifiers.
B. Southern League independent results, fixtures and league table check. Not yet implemented in this staging workflow.
C. Darren Holmes and verified club reports for human/editorial reconciliation.

## Publish gate
Only A/B-agreed finished results may update allowlisted fields after validation. Missing or conflicting data holds its affected fields and retains last trusted publication. Do not overwrite editorial overrides or the locked Canva master. Every verified change must produce a durable change summary that records the source IDs, old/new values, target and deployed version.

## Notifications
- **SUCCESS:** After a verified production deploy (not data retrieval alone) and only if published content changed, notify the user with the changed fixtures, standings/statistics, deployment link and timestamp.
- **REVIEW REQUIRED:** On A/B/C discrepancy, missing information, duplicate IDs, suspicious corrections, or inaccessible source, retain prior published data and notify with details.
- **FAILED:** On fetch, test, backup, deploy or verification failure, retain prior trusted published version and alert promptly.
- **NO CHANGE:** Log it, but no routine email.
- Prefer a dedicated notification service using a protected email destination in GitHub Actions secrets and approved sender credentials, or GitHub notifications. Never hardcode a personal email in source. Confirm deliverability with a real test before claiming email alerts are enabled.
- Use deduplication keyed to match ID + conflict type or deployment commit, and include audit/history links. Alert only after a successful post-deployment readback where possible.

## Long-term outputs
- Match Centre / player stats: data-driven updates with approved layout untouched.
- Programme Centre: only fields classified AUTO; never alter locked design assets/master. GUIDED or EDITORIAL waits for review.
- Media hub: timeline, substitutions, scoring, player IDs, attendance and report handoff.
