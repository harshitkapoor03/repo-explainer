# 🔍 Repo Explainer Agent

> Give it any GitHub repo URL. It reads the code and explains the entire codebase in plain English — like a senior developer walking you through it.

Built with [GitAgent](https://gitagent.sh) — an open standard for defining AI agents as version-controlled files.
Powered by **Google Gemini** — completely free, no credit card needed.

---

## Demo

```bash
python main.py https://github.com/pallets/flask
```

```
🔍 Analysing github.com/pallets/flask ...

📂 Fetching file tree...
   Found 236 files total.
📖 Reading 8 key files: README.md, pyproject.toml, src/flask/app.py ...

🤖 Generating explanation...

## 🔍 What this repo does
Flask is a lightweight Python web framework for building web applications
with minimal boilerplate. It wraps Werkzeug for HTTP and Jinja2 for
templating, leaving everything else up to you.

## 🗂️ Project structure
- src/flask/   → the entire framework source
- tests/        → pytest test suite
- docs/         → documentation (built with Sphinx)
- pyproject.toml → packaging and dependencies

## 🚀 Entry point — where it all starts
Your code does `from flask import Flask` which imports from
src/flask/__init__.py, exposing the Flask class defined in app.py.
That object is what you call .run() on to start the server.

...

💬 Ask follow-up questions (type 'quit' to exit)

You: how does routing work?
Agent: Flask routing is handled in src/flask/routing.py...
```

---

## Setup (5 minutes, completely free)

### 1. Get your free Gemini API key
- Go to **https://aistudio.google.com/apikey**
- Sign in with your Google account (the one you already have)
- Click "Create API key"
- Copy it — it looks like `AIzaSy...`

### 2. Clone and install
```bash
git clone https://github.com/YOUR_USERNAME/repo-explainer
cd repo-explainer
pip install -r requirements.txt
```

### 3. Set your key
```bash
export GEMINI_API_KEY="AIzaSy..."
```

Or paste it directly into `main.py` at the `GEMINI_API_KEY = ""` line.

### 4. Run it on any public GitHub repo
```bash
python main.py https://github.com/pallets/flask
python main.py https://github.com/fastapi/fastapi
python main.py https://github.com/facebook/react
```

---

## How it works — the GitAgent structure

This is a **GitAgent** — the AI's entire behaviour is defined as plain text files you can read, edit, and version-control. Nothing is hidden in a black box.

| File | What it does |
|------|-------------|
| `agent.yaml` | The manifest — model, tools, skills |
| `SOUL.md` | Agent personality and communication style |
| `RULES.md` | Hard constraints — must always / must never |
| `skills/explain-repo/SKILL.md` | Step-by-step instructions for the task |
| `knowledge/index.yaml` | Reference knowledge (frameworks, entry points) |
| `tools/scripts/` | Python scripts that fetch from GitHub |
| `main.py` | The runner that wires everything together |

Because it's all files, you can `git diff` what changed in the agent's behaviour, fork it, or PR improvements back.

---

## Customize it

**Change the personality** → Edit `SOUL.md`

**Add a rule** (e.g. "always mention test coverage") → Edit `RULES.md`

**Change the output format** → Edit `skills/explain-repo/SKILL.md`

**Switch to a different free model** → Change `GEMINI_MODEL` in `main.py` to `gemini-2.5-flash` or `gemini-1.5-pro`

---

## Free tier limits

Google Gemini's free tier gives you:
- **60 requests per minute**
- **1,500 requests per day**
- **1 million token context window**
- No credit card ever required

That's enough to explain hundreds of repos per day.
