# Project maintenance log

Daily, **automatically generated** inventory checks for public repositories owned by [raliegh2](https://github.com/raliegh2). This project demonstrates a small, reproducible GitHub Actions monitoring workflow. Reports are automation output, not evidence of daily manual coding or a security audit.

**Setup status:** The collector and first report are published. The scheduled workflow is prepared locally but awaits GitHub OAuth `workflow` permission before it can be uploaded and enabled. Daily automation is not active yet.

## What it checks

The workflow reads public GitHub metadata: repository availability, default branch, latest branch commit, license declaration, README presence, and security policy presence. Missing documentation is reported as an observation, not a vulnerability. No application code, deployments, private repositories, secrets, or customer data are modified or collected.

Daily JSON evidence lives in `reports/`; [latest.md](latest.md) summarizes the latest completed collection. API failures are recorded as unknown/error, never as passing checks. If inventory collection fails completely, no report is committed and the workflow fails.

## Schedule and attribution

GitHub Actions runs at 14:17 UTC (09:17 Bogota) with a fallback at 20:47 UTC (15:47 Bogota). Only one report is written per Bogota calendar date. Scheduled delivery is best effort; GitHub can delay or drop runs. You can also run the workflow manually from the Actions tab.

Report commits use the owner's GitHub noreply email as author and `github-actions[bot]` as committer. Every report and commit message identifies the automation. Attribution does not mean a person manually performed these checks.

The workflow token has write access only to this log repository. The collector uses unauthenticated, read-only public GitHub API calls and never pushes to monitored projects. A pinned checkout action checks out this repository. Disable the workflow in the Actions tab to stop updates.

## Run locally

Requires Python 3.11 or newer, with no third-party packages:

```sh
python scripts/collect.py
```

The account and log repository name are configured at the top of the collector. Archived repositories, forks, and this log repository are excluded. New public non-fork repositories are discovered automatically.
