# Agentic Engineering Tools (`agentic-tools`)

**For AI coding agents:** You may change any part of this file as needed for long-term memory.

This repository maintains **slash commands**, **subagents**, **coding standards**, and **MCP defaults** for Claude Code and Cursor. The distributable tree is **`agent-config/`**; consumers install it with root **`install.py`**. Human-oriented overview and tables live in **`README.md`** (they can drift—**`agent-config/`** is the source of truth for what ships).

Project entry for Claude Code in this repo: **`CLAUDE.md`** → points here.

---

## Architecture

### 1. Distributable payload (`agent-config/`)

Installed by **`install.py`** into the user’s **Claude** (`~/.claude/`) and/or **Cursor** (`~/.cursor/`) trees, depending on the interactive choice.

| Area | Role |
|------|------|
| **`commands/*.md`** | Slash commands (same files go to both tools when both are selected). YAML frontmatter must include **`description`** so Cursor can auto-generate **skills** under `~/.cursor/skills/<name>/SKILL.md`. |
| **`agents/*.md`** | Subagent definitions: frontmatter `name`, `description`, `model: inherit`. |
| **`standards/*.md`** | Coding guidelines. Copied to **`<tool>/standards/`** for each installed tool (Claude **and** Cursor each get a copy when selected). |
| **`mcp/mcp.json`** | `mcpServers` merged into `~/.claude/settings.json` and/or `~/.cursor/mcp.json`. Secrets use **`<PLACEHOLDER>`** tokens, never real values. |

### 2. Repo-only tooling (not installed by `install.py`)

- **`.claude/commands/`** and **`.cursor/commands/`** — e.g. **`/add-new-config`** for importing configs into `agent-config/` while working in this repository.

### 3. Not part of the installer

- **`cursor_template/`** is **gitignored**; it is not read by `install.py` and is not the canonical copy of the payload. Ignore it unless the maintainer uses it manually.

---

## Current `agent-config/` inventory

**Commands:** `add-agent-md`, `update-agent-tools`, `verify-plan`, `readme-standard`, `validate-tests`, `run-tests`

**Agents:** `database-auditor`, `security-auditor`

**Standards:** `python.md`

**MCP servers (keys in `mcp.json`):** `context7`, `github`, `awslabs.aws-documentation-mcp-server`

---

## Install and update

- **Local mode:** Run `python3 install.py` from a clone; reads `agent-config/` on disk (no GitHub token).
- **Remote mode:** Run with only `install.py` and no local `agent-config/`; fetches from GitHub API for repo **`DavidLozzi/agentic-tools`** (override with `GITHUB_REPO` / `AGENT_CONFIG_BRANCH` / `GITHUB_API_BASE` if you fork). Requires **`GITHUB_TOKEN`** or **`gh auth token`**.
- **Manifest:** After install, **`.agent-config-manifest.json`** is written under the chosen tool home(s); **`/update-agent-tools`** compares those SHAs to GitHub and can re-run the installer.
- **Path placeholders** in `commands/*.md` and `agents/*.md`: `{{TOOL_CONFIG_HOME}}`, `{{STANDARDS_DIR}}`, `{{PYTHON_STANDARD_FILE}}` — replaced with **absolute paths** per destination when copying (Claude vs Cursor). Do not hardcode `~/.claude` or `~/.cursor` in distributable markdown.

---

## Conventions for new or edited configs

- **Commands:** Frontmatter `description`, H1, **`$ARGUMENTS`** fenced block, line that the user input must be considered, numbered steps (often discovery first), **Output** section. Match existing commands as templates.
- **Agents:** Frontmatter as above; open with role; discovery first; findings grouped by severity where applicable.
- **Standards:** Clear H1, H2 sections, imperative bullets.
- **MCP:** Add servers under `mcpServers`; use **`<DESCRIPTIVE_TOKEN>`** for any secret or per-user string.

New files under existing `agent-config/` subdirs are picked up by **`install.py`** globs—no code change unless you add a new category of artifact.

---

## Contributing (short)

1. Add or edit files under **`agent-config/`** (or use **`/add-new-config`** in this repo).
2. Update **`README.md`** “What’s Included” if you are exposing something new to readers.
3. Land on **`main`**; users refresh via **`install.py`** or **`/update-agent-tools`**.

---

## TODO

See **[TODO.md](TODO.md)**. Append new TODOs when asked. If you notice an open item, mention it and only implement it when the user explicitly asks.

---

## Agent Context (optional MCP)

If an **Agent Context Manager** MCP is configured in the environment:

1. After the first user turn, call **`register_session`** with the repo root path and an `agent_id`; keep the returned **`session_id`**.
2. When work pauses or finishes, call **`update_context`** with that **`session_id`** and a ≤2-sentence summary of ask + outcome.

If that MCP is not available, skip these steps.
