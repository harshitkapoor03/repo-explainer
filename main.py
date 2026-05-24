"""
main.py — GitHub Repo Explainer (uses Groq)
-------------------------------------------
Run:
    python main.py https://github.com/owner/repo

To get a free Groq API key:
  1. Go to https://console.groq.com
  2. Sign up
  3. Create an API key
  4. Run: set GROQ_API_KEY=your_key_here
"""

import os
import sys
import re
import requests

# Add helper scripts folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools", "scripts"))
from fetch_github_tree import fetch_tree
from fetch_file_content import fetch_content

# API setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"


def load_file(path: str) -> str:
    # Reads a file relative to this script
    full_path = os.path.join(os.path.dirname(__file__), path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def build_system_prompt() -> str:
    # Combines different internal files into one big system prompt
    soul      = load_file("SOUL.md")
    rules     = load_file("RULES.md")
    skill     = load_file("skills/explain-repo/SKILL.md")
    knowledge = load_file("knowledge/index.yaml")

    return f"""
{soul}

---

{rules}

---

# Your Skill: Explain GitHub Repositories
{skill}

---

# Knowledge Base
{knowledge}
""".strip()


def parse_github_url(url: str) -> tuple[str, str]:
    # Extracts owner and repo name from a GitHub URL or shorthand
    url = url.strip().rstrip("/").removesuffix(".git")

    match = re.search(r"github\.com[/:]([^/]+)/([^/\s]+)", url)
    if match:
        return match.group(1), match.group(2)

    # Also supports "owner/repo" format
    if "/" in url and not url.startswith("http"):
        parts = url.split("/")
        if len(parts) == 2:
            return parts[0], parts[1]

    raise ValueError(f"Could not parse GitHub URL: {url!r}")


# Common entry point files
ENTRY_POINT_NAMES = {
    "main.py", "app.py", "run.py", "manage.py", "wsgi.py", "asgi.py",
    "index.js", "index.ts", "server.js", "app.js", "main.ts", "server.ts",
    "main.go", "main.rs", "index.php", "app.rb", "Program.cs",
}

# Config files that help understand dependencies
CONFIG_NAMES = {
    "package.json", "pyproject.toml", "requirements.txt", "setup.py",
    "go.mod", "Cargo.toml", "pom.xml", "Gemfile", "composer.json",
}

# Readme files usually explain the project
README_NAMES = {"README.md", "README.rst", "README.txt", "readme.md"}


def pick_files_to_read(all_files: list[str], max_files: int = 7) -> list[str]:
    # Picks a small but useful subset of files to inspect
    chosen = []
    remaining = list(all_files)

    def grab(condition):
        # Prefer files closer to root (less nested)
        candidates = sorted(remaining, key=lambda f: f.count("/"))
        for f in candidates:
            basename = os.path.basename(f)
            if condition(f, basename) and len(chosen) < max_files:
                chosen.append(f)
                remaining.remove(f)

    # Priority order: README → config → entry points → source files
    grab(lambda f, b: b in README_NAMES and "/" not in f)
    grab(lambda f, b: b in CONFIG_NAMES and "/" not in f)
    grab(lambda f, b: b in ENTRY_POINT_NAMES)

    source_dirs = ("src/", "lib/", "app/", "api/", "core/")
    grab(lambda f, b: any(f.startswith(d) for d in source_dirs)
         and f.endswith((".py", ".js", ".ts", ".go", ".rs", ".java")))

    return chosen


def call_groq(system_prompt: str, messages: list[dict]) -> str:
    """
    Sends a request to Groq API.
    Keeps conversation short and retries if rate limited.
    """
    import time

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    # Only keep last few messages to avoid hitting token limits
    trimmed = messages[-4:] if len(messages) > 4 else messages

    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + trimmed,
        "temperature": 0.3,
        "max_tokens": 2048,
    }

    for attempt in range(3):
        response = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        if response.status_code == 429:
            wait = 15 * (attempt + 1)
            print(f"   [Rate limited - waiting {wait}s...]")
            time.sleep(wait)
            continue

        raise RuntimeError(f"Groq API error {response.status_code}: {response.text[:400]}")

    raise RuntimeError("Rate limit hit after retries. Try again later.")


def main():
    # Expect a GitHub repo URL as input
    if len(sys.argv) < 2:
        print("Usage: python main.py <github-url>")
        print("Example: python main.py https://github.com/pallets/flask")
        sys.exit(1)

    url = sys.argv[1]

    # Check API key
    if not GROQ_API_KEY:
        print("\nNo Groq API key found!\n")
        print("Get one at: https://console.groq.com\n")
        print("Then run: set GROQ_API_KEY=your_key_here\n")
        sys.exit(1)

    try:
        owner, repo = parse_github_url(url)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"\nAnalysing github.com/{owner}/{repo} ...\n")

    # Step 1: get file tree
    print("Fetching file tree...")
    try:
        all_files = fetch_tree(owner, repo)
    except Exception as e:
        print(f"Could not fetch repo: {e}")
        sys.exit(1)

    print(f"   Found {len(all_files)} files total.")

    # Step 2: pick important files
    files_to_read = pick_files_to_read(all_files)
    print(f"Reading {len(files_to_read)} key files: {', '.join(files_to_read)}\n")

    # Step 3: fetch file contents
    file_contents: dict[str, str] = {}
    for path in files_to_read:
        file_contents[path] = fetch_content(owner, repo, path)

    # Keep tree small so prompt doesn't explode
    file_tree_summary = "\n".join(all_files[:100])
    if len(all_files) > 100:
        file_tree_summary += f"\n... and {len(all_files) - 100} more files"

    # Limit file content size as well
    files_text = ""
    for path, content in file_contents.items():
        lines = content.splitlines()[:80]
        files_text += f"\n\n### {path}\n```\n{chr(10).join(lines)}\n```"

    # First prompt to the model
    first_message = f"""Please explain this GitHub repository to me.

Repository: https://github.com/{owner}/{repo}

## File tree (top 100)
{file_tree_summary}

## Key file contents
{files_text}

Now explain this codebase following your skill instructions exactly.
"""

    print("Generating explanation...\n")

    system_prompt = build_system_prompt()
    messages = [{"role": "user", "content": first_message}]

    explanation = call_groq(system_prompt, messages)
    print(explanation)

    messages.append({"role": "assistant", "content": explanation})

    print("\n" + "-" * 60)
    print("Ask follow-up questions (type 'quit' to exit)")
    print("-" * 60 + "\n")

    # Interactive loop
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # If user asks about a file we haven't loaded yet, fetch it
        extra_context = ""
        for f in all_files:
            if (f in question or os.path.basename(f) in question) and f not in file_contents:
                print(f"   [Fetching {f}...]")
                content = fetch_content(owner, repo, f)
                file_contents[f] = content
                lines = content.splitlines()[:80]
                extra_context = f"\n\nContent of {f}:\n```\n{chr(10).join(lines)}\n```"
                break

        messages.append({"role": "user", "content": question + extra_context})

        answer = call_groq(system_prompt, messages)
        print(f"\nAgent: {answer}\n")

        messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()