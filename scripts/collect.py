"""Read public repository metadata and record transparent automated evidence."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

OWNER = "raliegh2"
LOG_REPO = "project-maintenance-log"
ROOT = Path(__file__).resolve().parents[1]
BOGOTA = timezone(timedelta(hours=-5))


def get(path):
    request = Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "raliegh2-public-maintenance-log",
    })
    try:
        with urlopen(request, timeout=20) as response:
            return json.load(response), None
    except HTTPError as error:
        return None, f"HTTP {error.code}"
    except (URLError, TimeoutError, ValueError, OSError):
        return None, "Request failed or returned invalid JSON"


def presence(path):
    value, error = get(path)
    if error == "HTTP 404":
        return "absent"
    if error:
        return "unknown (" + error + ")"
    return "present" if value else "unknown"


def collect():
    now = datetime.now(timezone.utc)
    day = now.astimezone(BOGOTA).date().isoformat()
    report_path = ROOT / "reports" / (day + ".json")
    if report_path.exists():
        print("Report already exists for " + day + "; no changes.")
        return

    inventory = []
    for page in range(1, 101):
        repos, error = get(f"/users/{OWNER}/repos?type=owner&per_page=100&page={page}")
        if error or not isinstance(repos, list):
            raise RuntimeError("Public inventory unavailable: " + (error or "invalid response"))
        inventory.extend(repo for repo in repos if not repo.get("private")
                         and not repo.get("fork") and not repo.get("archived")
                         and repo["name"] != LOG_REPO)
        if len(repos) < 100:
            break
    else:
        raise RuntimeError("Inventory exceeded pagination limit; refusing a partial report.")
    if not inventory:
        raise RuntimeError("No public repositories found; refusing an empty success report.")

    results = []
    for repo in sorted(inventory, key=lambda item: item["name"].lower()):
        base = "/repos/" + repo["full_name"]
        branch = repo.get("default_branch")
        commit, commit_error = get(base + "/commits/" + quote(branch, safe="")) if branch else (None, "No default branch")
        results.append({
            "repository": repo["full_name"], "url": repo["html_url"],
            "availability": "public metadata retrieved",
            "default_branch": branch,
            "latest_commit_sha": commit.get("sha") if isinstance(commit, dict) else None,
            "commit_lookup_error": commit_error,
            "license": (repo.get("license") or {}).get("spdx_id"),
            "readme": presence(base + "/readme"),
            "security_policy": None,
        })
        community, community_error = get(base + "/community/profile")
        results[-1]["security_policy"] = (
            "unknown (" + community_error + ")" if community_error
            else "present" if (community or {}).get("files", {}).get("security") else "absent"
        )

    report = {"date_bogota": day, "collected_at_utc": now.isoformat(),
              "generated_by": "automated GitHub Actions/public metadata collector",
              "scope": "Public repository inventory; not a security assessment or manual coding activity",
              "repositories": results}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Latest automated maintenance inventory", "",
             f"Bogota date: {day}. Collected at {now.isoformat()}.", "",
             "Generated automatically. These observations are not a security assessment or proof of daily manual coding.", "",
             f"[JSON evidence](reports/{day}.json)", "",
             "| Public repository | Default branch | README | Security policy | License | Commit lookup |",
             "| --- | --- | --- | --- | --- | --- |"]
    for row in results:
        lines.append(f"| [{row['repository']}]({row['url']}) | {row['default_branch'] or 'None'} | {row['readme']} | {row['security_policy']} | {row['license'] or 'Not declared'} | {row['commit_lookup_error'] or 'Retrieved'} |")
    (ROOT / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Recorded {len(results)} public repositories for {day}.")


if __name__ == "__main__":
    collect()
