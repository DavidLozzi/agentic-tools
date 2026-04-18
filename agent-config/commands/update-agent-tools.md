---
description: Check for updates to installed agent tools (commands, agents, standards, MCP). Use when the user asks to check for updates, refresh agent tooling, or wants to know if new commands or agents are available.
---

# Update Agent Tools

Check for updates to installed agent commands, agents, standards, and MCP configs.

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

You are checking whether the locally installed agent-config files are up to date with the remote repository. Follow these steps exactly.

### Step 1: Detect the tool

Determine which tool you are running in:
- If `~/.claude/.agent-config-manifest.json` exists, use that (Claude Code).
- If `~/.cursor/.agent-config-manifest.json` exists, use that (Cursor).
- If neither exists, tell the user: "No install manifest found. Run install.py first to install agent-config and enable update checking." Then stop.

Read the manifest file. It contains `repo`, `branch`, and `files` (a map of `"subdir/filename"` to SHA hash).

### Step 2: Get a GitHub token

Try these in order:
1. Check if `GITHUB_TOKEN` environment variable is set.
2. Run `gh auth token` to get a token from the GitHub CLI.

If neither works, tell the user they need to set `GITHUB_TOKEN` or run `gh auth login`, then stop.

### Step 3: Check remote file SHAs

For each subdirectory listed in the manifest files (e.g. `commands`, `agents`, `standards`, `mcp`), call the GitHub Contents API to list the current files and their SHAs:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/{repo}/contents/agent-config/{subdir}?ref={branch}"
```

The response is a JSON array. Each entry has `name` and `sha` fields.

### Step 4: Compare and report

Compare the remote SHAs against the manifest. Categorize each file:

- **Updated**: file exists in both but SHA differs
- **New**: file exists remotely but not in the manifest
- **Removed**: file exists in the manifest but not remotely

If everything matches, report: "Agent config is up to date."

If there are differences, show a summary table like:

| Status | File |
|---|---|
| Updated | commands/run-tests.md |
| New | commands/new-command.md |
| Removed | agents/old-agent.md |

### Step 5: Offer to update

If updates are available, ask the user if they want to update now.

If yes, download and run install.py:

**For Mac / Linux / WSL:**
```bash
curl -sSL -H "Authorization: token $TOKEN" \
  -o /tmp/install.py \
  "https://raw.githubusercontent.com/{repo}/{branch}/install.py"
python3 /tmp/install.py
```

**For Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/{repo}/{branch}/install.py" `
  -Headers @{ Authorization = "token $TOKEN" } -OutFile $env:TEMP\install.py
python $env:TEMP\install.py
```

Replace `{repo}` and `{branch}` with the values from the manifest.
