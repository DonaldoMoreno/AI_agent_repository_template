#!/usr/bin/env python3
"""Fetch basic run/jobs info from GitHub Actions and write to an output file.

This script writes a compact JSON summary to the output file. It requires a
GitHub token available via the `GH_TOKEN` environment variable or the
`--token` argument.
"""
import argparse
import os
import sys
import json
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="owner/repo")
    p.add_argument("--run-id", required=True, help="workflow run id")
    p.add_argument("--out", required=True, help="output file")
    p.add_argument("--token", help="GitHub token (optional, can use GH_TOKEN env)")
    args = p.parse_args()

    token = args.token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: no GitHub token provided (GH_TOKEN or --token)", file=sys.stderr)
        sys.exit(2)

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    base = "https://api.github.com"

    # Fetch run info
    run_url = f"{base}/repos/{args.repo}/actions/runs/{args.run_id}"
    r = requests.get(run_url, headers=headers)
    if r.status_code != 200:
        print(f"Warning: failed to fetch run info: {r.status_code}", file=sys.stderr)
        run_info = {"error": r.text}
    else:
        run_info = r.json()

    # Fetch jobs for the run
    jobs_url = f"{base}/repos/{args.repo}/actions/runs/{args.run_id}/jobs"
    r2 = requests.get(jobs_url, headers=headers)
    if r2.status_code != 200:
        print(f"Warning: failed to fetch jobs: {r2.status_code}", file=sys.stderr)
        jobs_info = {"error": r2.text}
    else:
        jobs_info = r2.json()

    # Assemble summary
    summary = {
        "run": {k: run_info.get(k) for k in ("id", "head_sha", "status", "conclusion", "event")},
        "jobs_summary": [],
        "raw_run": run_info,
        "raw_jobs": jobs_info,
    }

    if isinstance(jobs_info, dict) and "jobs" in jobs_info:
        for job in jobs_info.get("jobs", []):
            summary["jobs_summary"].append({
                "id": job.get("id"),
                "name": job.get("name"),
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
                "html_url": job.get("html_url"),
            })

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
