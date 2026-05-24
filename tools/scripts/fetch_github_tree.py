"""
fetch_github_tree.py
Fetches the complete file tree of a public GitHub repo.

"""
import os
import sys
import json
import subprocess


def fetch_tree(owner: str, repo: str) -> list[str]:
    token = os.getenv("GITHUB_TOKEN", "")

    # First get the default branch name
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    cmd = ["curl", "-s", "-L", "--max-time", "15"]
    if token:
        cmd += ["-H", f"Authorization: Bearer {token}"]
    cmd += ["-H", "User-Agent: repo-explainer-gitagent/1.0"]
    cmd.append(repo_url)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if result.returncode != 0:
        raise RuntimeError(f"Network error fetching repo info.")

    try:
        repo_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid response from GitHub API.")

    if "message" in repo_data:
        msg = repo_data["message"]
        if "rate limit" in msg.lower():
            raise RuntimeError(
                "GitHub API rate limit hit.\n"
                "Fix: Set GITHUB_TOKEN in your environment.\n"
                "Get a free token at: https://github.com/settings/tokens"
            )
        if "not found" in msg.lower():
            raise RuntimeError(f"Repo '{owner}/{repo}' not found. Is it public?")
        raise RuntimeError(f"GitHub API error: {msg}")

    default_branch = repo_data.get("default_branch", "main")

    # Fetching the full recursive tree
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    cmd2 = ["curl", "-s", "-L", "--max-time", "20"]
    if token:
        cmd2 += ["-H", f"Authorization: Bearer {token}"]
    cmd2 += ["-H", "User-Agent: repo-explainer-gitagent/1.0"]
    cmd2.append(tree_url)

    result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=25)
    if result2.returncode != 0:
        raise RuntimeError("Network error fetching file tree.")

    try:
        tree_data = json.loads(result2.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Invalid response when fetching file tree.")

    if "message" in tree_data:
        raise RuntimeError(f"GitHub API error: {tree_data['message']}")

    if "tree" not in tree_data:
        raise RuntimeError("No tree data in GitHub response.")

    return [item["path"] for item in tree_data["tree"] if item["type"] == "blob"]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fetch_github_tree.py <owner> <repo>")
        sys.exit(1)
    owner, repo = sys.argv[1], sys.argv[2]
    try:
        files = fetch_tree(owner, repo)
        print(json.dumps(files, indent=2))
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
