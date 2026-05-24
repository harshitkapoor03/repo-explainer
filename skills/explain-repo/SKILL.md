\---

name: explain-repo
description: >
Given a GitHub repository URL, autonomously fetches the file tree, reads
the most important files, and produces a structured plain-English explanation
of the entire codebase.
version: 1.0.0
---

# Skill: Explain a GitHub Repository

## When This Skill is Triggered

The user provides a GitHub URL like:

* `https://github.com/owner/repo`
* `github.com/owner/repo`
* Just `owner/repo`

## Step-by-Step Process

### Step 1 — Parse the URL

Extract `owner` and `repo` from whatever format the user gave.

### Step 2 — Fetch the file tree

Scan the list and identify:

* Entry points: `main.py`, `index.js`, `app.py`, `server.go`, `main.go`, `index.ts`, `manage.py`
* Config files: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `requirements.txt`
* README: `README.md` or `README.rst`
* Key source folders: `src/`, `lib/`, `app/`, `api/`, `core/`

### Step 3 — Read the important files

Read in this order:

1. README.md — to understand intent
2. package.json / pyproject.toml / go.mod — to understand dependencies
3. The main entry point file
4. 2-3 other files that look most central to the logic

### Step 4 — Produce the explanation in this exact format:

## What this repo does

\[2-sentence plain English summary]

## Project structure

\[Explain each top-level folder and key files in 1-2 sentences each]

## Entry point — where it all starts

\[Explain exactly what file runs first and what it does]

## Key components

\[Explain 3-5 core modules/classes/functions and how they connect]

## Tech stack

\[Languages, frameworks, major libraries]

## How it all fits together

\[One paragraph connecting the dots]

## If you wanted to add a feature...

\[Concrete advice: which file to open, what pattern to follow]

