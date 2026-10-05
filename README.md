# Tiverton Town Results Centre — V18 Online Edition

This repository contains the Tiverton Town Get Results page and its online updater.

## What the online edition does

- GitHub Actions runs the updater every hour (at minute 17) and whenever you manually run the workflow.
- `update_online.py` reads the Southern League Division One South match grid and monthly result pages from Football Web Pages.
- It reads the league table from Tivvy Archive.
- It rebuilds the web data, CSV and fully coloured Excel workbook on a Linux GitHub runner — Microsoft Excel is not required.
- Cloudflare Workers Static Assets publishes the contents of `public/`.
- The website includes iPhone home-screen metadata, so Safari can add it as an app-like icon.

## First-time setup

1. Create a Cloudflare account if you do not already have one.
2. In Cloudflare, create an API token that can deploy Workers for your account.
3. In GitHub open the repository, then Settings -> Secrets and variables -> Actions -> New repository secret.
4. Add `CLOUDFLARE_API_TOKEN` containing the Cloudflare API token.
5. Add `CLOUDFLARE_ACCOUNT_ID` containing your Cloudflare Account ID.
6. Open the repository's Actions tab, choose "Update and deploy Tiverton results", and choose Run workflow.
7. When the workflow finishes, Cloudflare will provide a `workers.dev` address for `tiverton-town-results`.

## iPhone

Open the Cloudflare address in Safari, tap Share, then "Add to Home Screen". The supplied Tiverton Town crest is used as the icon.

## Making the site private

If you want the site restricted to you, protect the Worker with Cloudflare Access and allow only your email address.
