#!/usr/bin/env python3
"""Fetch the public TMOG feedback tracker into research/data/.

Requires the GitHub CLI (`gh auth login`). Raw issue text is deliberately not
committed: it is other people's writing, it goes stale in hours, and 1.8 MB of
JSON in a repository is a liability rather than an artefact. What *is*
committed is the analysis script that turns this data into a dated report.

    python3 research/fetch_issues.py            # all issues, state=all
    python3 research/fetch_issues.py --open     # only open ones
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "research" / "data" / "tmog-feedback-issues.json"
REPO = "PlummersSoftwareLLC/tmog-feedback"
BODY_KEEP = 1200  # characters; enough for the template's structured fields


def gh_json(path: str):
    proc = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"gh api {path} failed:\n{proc.stderr}")
    return json.loads(proc.stdout or "[]")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--open", action="store_true", help="fetch open issues only")
    args = parser.parse_args()
    state = "open" if args.open else "all"

    items, page = [], 1
    while True:
        batch = gh_json(f"repos/{REPO}/issues?state={state}&per_page=100&page={page}")
        if not batch:
            break
        items += batch
        print(f"page {page}: {len(batch)} (total {len(items)})", flush=True)
        if len(batch) < 100:
            break
        page += 1

    trimmed = [
        {
            "number": i["number"],
            "state": i["state"],
            "created": i["created_at"][:10],
            "closed": (i.get("closed_at") or "")[:10],
            "title": i["title"],
            "labels": [label["name"] for label in i.get("labels", [])],
            "comments": i.get("comments", 0),
            "body": (i.get("body") or "")[:BODY_KEEP],
            "author": (i.get("user") or {}).get("login"),
        }
        for i in items
    ]

    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(trimmed, indent=0))
    print(f"saved {len(trimmed)} issues -> {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
