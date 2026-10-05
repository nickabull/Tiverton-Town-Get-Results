# Tiverton Town Results Centre — V18 Online Edition

This repository contains the Tiverton Town Get Results page and its automatic online updater.

## What the online edition does

- GitHub Actions runs the updater every hour (at minute 17), whenever the repository changes, and whenever you manually run the workflow.
- `update_online.py` reads the Southern League Division One South match grid and monthly result pages from Football Web Pages.
- It reads the league table from Tivvy Archive.
- It rebuilds the web data, CSV and fully coloured Excel workbook on a Linux GitHub runner — Microsoft Excel is not required.
- GitHub Pages publishes the finished contents of `public/`.
- The website includes iPhone home-screen metadata, so Safari can add it as an app-like icon.

## Website address

Once GitHub Pages is enabled, the site will be available at:

https://nickabull.github.io/Tiverton-Town-Get-Results/

## iPhone

Open the GitHub Pages address in Safari, tap Share, then **Add to Home Screen**. The supplied Tiverton Town crest is used as the icon.

## Updating

Open the repository's **Actions** tab, choose **Update and deploy Tiverton results**, then choose **Run workflow**. The scheduled hourly update will also run automatically.
