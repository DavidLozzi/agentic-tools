# Agentic Engineering Tools

Get the most out of AI coding agents (Claude Code, Cursor) with shared slash commands, autonomous agents, coding standards, and MCP server configs — all installable in one step.

This repo is the single source of truth for how these AI tools behave across projects. Install once to get shared slash commands, **database-auditor** and **security-auditor** agents, Python standards, and MCP defaults. Updates are pulled by re-running the installer. Maintainer-focused layout and inventory live in **[AGENTS.md](AGENTS.md)** (this README is the contributor-facing summary).

## Table of Contents

- [What's Included](#whats-included)
  - [Slash Commands](#slash-commands)
  - [Autonomous Agents](#autonomous-agents)
  - [MCP Servers](#mcp-servers)
- [Install the AI Tooling](#install-the-ai-tooling)
- [Updates](#updates)
- [Contributing](#contributing)

## What's Included

### Slash Commands

Available as slash commands in both Claude Code and Cursor. Both tools also recognize these as **skills** that auto-trigger based on context — no need to invoke them manually. The `description` in each command's frontmatter tells the tool when to activate it.

| Command | What it does |
|---|---|
| `/add-agent-md` | Analyzes the codebase and generates or updates an `AGENTS.md` file to guide AI coding agents |
| `/readme-standard` | Generates consistent, engineer-focused README files — a working doc to get a project running or make changes |
| `/run-tests` | Discovers, runs, and analyzes test suites for the project, then resolves any failures |
| `/update-agent-tools` | Checks for updates to installed commands, agents, standards, and MCP — offers to update if new versions are available |
| `/validate-tests` | Audits test suite quality, enforces 80% coverage, validates CI workflows, and generates missing tests |
| `/verify-plan` | Senior engineer/architect review of a generated plan — tightens it by resolving open questions and ambiguities |

### Autonomous Agents

Background agents that can be invoked for specialized tasks.

| Agent | What it does |
|---|---|
| **database-auditor** | Database performance specialist — optimizes queries, reviews indexes, ORM usage, schema design, and migration safety |
| **security-auditor** | Security specialist — audits code for vulnerabilities, reviews auth flows, secrets handling, and API security posture |

### Coding Standards

Python coding guidelines are bundled into the `/add-agent-md` command — when it generates an `AGENTS.md` for a repo, it offers to include a `CODE.md` with Python stack conventions (FastAPI, Pydantic, httpx, pytest, Black/Flake8, layered directory structure).

Guidelines for other languages (TypeScript, Go, etc.) can be added the same way — see [Contributing](#contributing).

### MCP Servers

| Server | What it provides |
|---|---|
| **Context7** | Up-to-date library and framework documentation lookup |
| **GitHub** | GitHub Copilot hosted MCP — repository, issues, and pull request workflows via `api.githubcopilot.com` (replace `<GITHUB_COPILOT_MCP_PAT>` in the merged MCP config after install) |
| **AWS Documentation** | Server key `awslabs.aws-documentation-mcp-server` — AWS Labs MCP via `uvx awslabs.aws-documentation-mcp-server@latest` for official AWS docs (partition `aws`); requires `uv` / Python on `PATH` |

## Install the AI Tooling

Run `install.py` to install commands, agents, standards, and MCP servers into Claude Code (`~/.claude/`) and/or Cursor (`~/.cursor/`). The script is interactive — it will ask which tools to install for and prompt before overwriting any existing files.

**From a clone of this repo:** run `python3 install.py` from the repository root. No GitHub token is required (files are read from `agent-config/` on disk).

**Download-only `install.py`:** if you save only `install.py` and run it without a local `agent-config/` directory, the script fetches config from the GitHub API. Then you need authentication via **one** of:

- **GitHub CLI (recommended):** Install the [GitHub CLI](https://cli.github.com/) and run `gh auth login`
- **Fine-grained PAT:** Create a token scoped to this repo with **Contents: Read-only** permission
- **Classic PAT:** Create a token with `public_repo` (or `repo` if you use private forks)

### Option A: Using GitHub CLI

If you have the [GitHub CLI](https://cli.github.com/) installed and authenticated:

**Mac / Linux / WSL:**

```bash
curl -sSL -H "Authorization: token $(gh auth token)" \
  -o install.py \
  https://raw.githubusercontent.com/DavidLozzi/agentic-tools/main/install.py
python3 install.py
```

**Windows (PowerShell):**

```powershell
$token = gh auth token
Invoke-WebRequest -Uri https://raw.githubusercontent.com/DavidLozzi/agentic-tools/main/install.py `
  -Headers @{ Authorization = "token $token" } -OutFile install.py
python install.py
```

### Option B: Using a Personal Access Token

Set your token as an environment variable, then download and run:

**Mac / Linux / WSL:**

```bash
export GITHUB_TOKEN="ghp_your_token_here"
curl -sSL -H "Authorization: token $GITHUB_TOKEN" \
  -o install.py \
  https://raw.githubusercontent.com/DavidLozzi/agentic-tools/main/install.py
python3 install.py
```

**Windows (PowerShell):**

```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
Invoke-WebRequest -Uri https://raw.githubusercontent.com/DavidLozzi/agentic-tools/main/install.py `
  -Headers @{ Authorization = "token $env:GITHUB_TOKEN" } -OutFile install.py
python install.py
```

You can delete `install.py` after running it. To update later, re-download and re-run — existing files will be backed up before replacement.

## Updates

Run `/update-agent-tools` in Claude Code or Cursor to check if new commands, agents, standards, or MCP entries are available. If updates are found, the agent will offer to download and install them for you.

You can also watch this repository on GitHub for changes to `main`.

## Contributing

### Adding a new command, agent, standard, or MCP server

The easiest way is to use the `/add-new-config` slash command from Claude Code while working in this repo. It will:

1. Ask what type of config you're adding (command, agent, standard, or MCP server)
2. Search your global config (`~/.claude/`, `~/.cursor/`) and any repo you point it to, then let you pick which one to import
3. Adapt the file to match this repo's conventions (adds required frontmatter, restructures steps, replaces secrets with `<PLACEHOLDER>` values)
4. Add the entry to the appropriate "What's Included" table in this README
5. Verify everything is in order before finishing

To use it, open Claude Code in this repo and type `/add-new-config`.

### Doing it manually

If you prefer to add config by hand:

1. Create the file in the correct `agent-config/` subdirectory:
   - **Commands** (`agent-config/commands/<name>.md`) — must include YAML frontmatter with a `description` field (this is what enables Cursor skill auto-triggering), an H1 title, a `$ARGUMENTS` code block, and step-by-step instructions.
   - **Agents** (`agent-config/agents/<name>.md`) — must include YAML frontmatter with `name`, `description`, and `model: inherit`.
   - **Standards** (`agent-config/standards/<name>.md`) — markdown coding guidelines. Installed into each selected tool’s `standards/` directory. From other distributable files, reference them with `{{STANDARDS_DIR}}` / `{{PYTHON_STANDARD_FILE}}` (expanded by `install.py`).
   - **MCP servers** (`agent-config/mcp/mcp.json`) — add an entry under `mcpServers`. Use `<PLACEHOLDER>` syntax for secrets — never commit real tokens.
2. Update this `README.md` — add a row to the appropriate table in "What's Included."

### Submitting your contribution

Open a pull request against [DavidLozzi/agentic-tools](https://github.com/DavidLozzi/agentic-tools). Once changes are merged to `main`, others pick them up by re-running the installer or running `/update-agent-tools`.

### Ideas and planned work

See [TODO.md](TODO.md) for ideas and planned commands. Contributions are welcome — open a PR with your proposal.
