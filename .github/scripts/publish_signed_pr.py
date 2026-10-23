#!/usr/bin/env python3
"""Publish workflow-generated files as a GitHub-verified commit on a pull request.

Catylist ADR-0006 protects the default branch: changes reach it only through
pull requests, and every commit must be verified. A plain ``git push`` from a
runner is rejected on both counts, so generated files are published like this:

1. Stage the given paths in the local index and list what differs from the
   checked-out commit. Nothing is committed or pushed locally.
2. Create the automation branch at that commit, or reset it there. Only this
   workflow-owned branch is ever force-updated, never the base branch.
3. Commit the changes with GraphQL ``createCommitOnBranch`` using the
   workflow's ``GITHUB_TOKEN``. GitHub signs such commits, so they are verified.
4. Open a pull request to the base branch, or leave the existing one open.

Does nothing when the paths are unchanged. GitHub calls go through ``gh``
(preinstalled on hosted runners) with the token in ``GH_TOKEN``. Standard
library only.

Usage:
  publish_signed_pr.py --branch automation/x --title "..." PATH [PATH ...]
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

MUTATION = """
mutation($input: CreateCommitOnBranchInput!) {
  createCommitOnBranch(input: $input) { commit { oid url } }
}
""".strip()


def run(*args: str, stdin: str | None = None) -> str:
    return subprocess.run(args, input=stdin, check=True, capture_output=True, text=True).stdout


def changes(base_sha: str, paths: list[str]) -> tuple[list[dict], list[dict]]:
    run("git", "add", "-A", "--", *paths)
    status = run("git", "diff", "--cached", "--name-status", "--no-renames", "-z", base_sha, "--", *paths)
    fields = status.split("\0")
    additions, deletions = [], []
    for code, path in zip(fields[0::2], fields[1::2]):
        if code == "D":
            deletions.append({"path": path})
        else:
            contents = base64.b64encode(Path(path).read_bytes()).decode("ascii")
            additions.append({"path": path, "contents": contents})
    return additions, deletions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--branch", required=True, help="automation branch owned by this workflow")
    parser.add_argument("--title", required=True, help="commit message and pull request title")
    parser.add_argument("--body", default="", help="pull request body")
    parser.add_argument("--base", default=os.environ.get("GITHUB_REF_NAME", "main"))
    parser.add_argument("--base-sha", default=os.environ.get("GITHUB_SHA"))
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(argv)
    repo = os.environ["GITHUB_REPOSITORY"]
    if not args.base_sha:
        parser.error("--base-sha or GITHUB_SHA is required")
    if args.branch == args.base:
        parser.error("the automation branch must differ from the base branch")

    additions, deletions = changes(args.base_sha, args.paths)
    if not additions and not deletions:
        print("No changes to publish.")
        return 0

    ref = f"refs/heads/{args.branch}"
    try:
        run("gh", "api", f"repos/{repo}/git/{ref}")
        run("gh", "api", "-X", "PATCH", f"repos/{repo}/git/{ref}", "-f", f"sha={args.base_sha}", "-F", "force=true")
    except subprocess.CalledProcessError:
        run("gh", "api", "-X", "POST", f"repos/{repo}/git/refs", "-f", f"ref={ref}", "-f", f"sha={args.base_sha}")

    payload = {
        "query": MUTATION,
        "variables": {
            "input": {
                "branch": {"repositoryNameWithOwner": repo, "branchName": args.branch},
                "expectedHeadOid": args.base_sha,
                "message": {"headline": args.title},
                "fileChanges": {"additions": additions, "deletions": deletions},
            }
        },
    }
    result = json.loads(run("gh", "api", "graphql", "--input", "-", stdin=json.dumps(payload)))
    commit = result["data"]["createCommitOnBranch"]["commit"]
    print(f"Verified commit {commit['oid']} on {args.branch}: {len(additions)} added or changed, {len(deletions)} deleted")

    existing = run("gh", "pr", "list", "--repo", repo, "--head", args.branch, "--base", args.base, "--state", "open", "--json", "url")
    open_prs = json.loads(existing or "[]")
    if open_prs:
        print(f"Pull request already open: {open_prs[0]['url']}")
    else:
        url = run("gh", "pr", "create", "--repo", repo, "--head", args.branch, "--base", args.base,
                  "--title", args.title, "--body", args.body or args.title).strip()
        print(f"Opened {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
