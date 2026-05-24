"""
fetch_file_content.py
Fetches the raw content of one file from a public GitHub repo.
"""
import os
import sys
import requests


def fetch_content(owner: str, repo: str, path: str) -> str:
    token = os.getenv("GITHUB_TOKEN", "")
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.get(raw_url, headers=headers, timeout=10)

    if r.status_code == 200:
        lines = r.text.splitlines()
        if len(lines) > 200:
            truncated = "\n".join(lines[:200])
            return truncated + f"\n\n... [truncated — {len(lines) - 200} more lines]"
        return r.text
    return f"[Could not fetch {path}: HTTP {r.status_code}]"


if __name__ == "__main__":
    print(fetch_content(sys.argv[1], sys.argv[2], sys.argv[3]))
