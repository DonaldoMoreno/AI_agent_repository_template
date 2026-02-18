#!/usr/bin/env python3
"""Post a comment to a PR using the GitHub REST API.

Usage: fixbot_comment.py --repo owner/repo --pr 123 --message "..."
Requires `GH_TOKEN` environment variable (or pass --token).
"""
import argparse
import os
import sys
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--pr", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--token", help="GitHub token (optional)")
    args = p.parse_args()

    token = args.token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GH_TOKEN or --token required", file=sys.stderr)
        sys.exit(2)

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{args.repo}/issues/{args.pr}/comments"
    data = {"body": args.message}
    r = requests.post(url, json=data, headers=headers)
    if r.status_code not in (200, 201):
        print(f"Failed to post comment: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)
    print("Comment posted: ", r.json().get("html_url"))


if __name__ == "__main__":
    main()
