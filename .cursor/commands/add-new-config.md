# Add New Config

Import an existing command, agent, standard, or MCP server into the shared agent-config for distribution to the team.

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user may specify the config type and/or a file path upfront (e.g. "command from ~/.claude/commands/deploy-preview.md"). Parse what is provided and skip the corresponding questions below.

## Step 1 — Determine the config type

If not already clear from the arguments, ask the user:

> What type of config do you want to add?
> 1. **Command** — a slash command (`agent-config/commands/<name>.md`)
> 2. **Agent** — an autonomous agent (`agent-config/agents/<name>.md`)
> 3. **Standard** — a coding guidelines document (`agent-config/standards/<name>.md`)
> 4. **MCP server** — an MCP server entry (`agent-config/mcp/mcp.json`)

Wait for the user's answer before proceeding.

## Step 2 — Find the source

Ask the user where the config currently lives. Then search the relevant locations to find it.

**For commands**, search these locations and list what you find:
- `~/.claude/commands/*.md` (global Claude Code commands)
- `~/.cursor/commands/*.md` (global Cursor commands)
- `~/.cursor/skills/*/SKILL.md` (Cursor skills)
- If the user mentions a specific repo, check `<repo>/.claude/commands/` and `<repo>/.cursor/commands/`

**For agents**, search:
- `~/.claude/agents/*.md` (global Claude Code agents)
- `~/.cursor/agents/*.md` (global Cursor agents)
- If the user mentions a specific repo, check `<repo>/.claude/agents/`

**For standards**, search:
- `~/.cursor/standards/*.md` (global Cursor standards)
- Ask the user for a file path if nothing is found

**For MCP servers**, search:
- `~/.claude/settings.json` — list the keys under `mcpServers`
- `~/.cursor/mcp.json` — list the keys under `mcpServers`
- Ask the user to point to a JSON file if needed

Present what you found and let the user pick which one to import. If nothing is found in the standard locations, ask the user for the full file path.

**Important:** Do not just search one location and stop. Search all the relevant locations listed above, present the results, and let the user choose.

## Step 3 — Read the source and the reference example

Read two things:

1. **The source file** the user selected in Step 2 — this is what we are importing.
2. **A reference example** from this repo to understand the conventions we need to match:
   - Command: read `agent-config/commands/run-tests.md`
   - Agent: read `agent-config/agents/database-auditor.md`
   - Standard: read `agent-config/standards/python.md`
   - MCP server: read `agent-config/mcp/mcp.json`

Compare the source against the reference. Note what needs to change to match this repo's conventions.

## Step 4 — Adapt and create the config file

Copy the source content into the correct location under `agent-config/`, adapting it to match the repo's conventions. Show the user what you changed and confirm before writing.

### Adapting a command

Target: `agent-config/commands/<name>.md`

Ensure the file has all of these (add or fix what's missing):

1. **YAML frontmatter with `description`** — This is required. Without it, `install.py` will not create a Cursor skill for this command. The description must explain when to use the command (e.g. "Run tests for this project. Use when the user asks to run tests, check test results, fix failing tests, or verify that code changes pass the test suite."). Check the source for an existing description; if missing, write one based on the command's content.
2. **H1 title** — A human-readable title matching the command's purpose.
3. **`$ARGUMENTS` block** — A fenced code block containing `$ARGUMENTS` so the command captures user input.
4. **"You MUST consider the user input"** line after the arguments block.
5. **Step-by-step instructions** — Numbered steps with descriptive headings. The first step should be discovery/scanning when applicable.
6. **Output section** — Describes the expected output format (table, summary, report).

If the source is a Cursor skill (`SKILL.md`), extract the frontmatter description and the body, then restructure into the command format above.

### Adapting an agent

Target: `agent-config/agents/<name>.md`

Ensure the file has:

1. **YAML frontmatter** with exactly three fields:
   - `name`: kebab-case agent name
   - `description`: Starts with a role noun (e.g. "Database performance specialist"). Includes when to use it.
   - `model: inherit`
2. **Opening line** — "You are a [role] auditing/building/reviewing..."
3. **Step 1 is always discovery** — Scan the codebase to understand the landscape before acting.
4. **Severity-grouped output** — Critical, High, Medium. Each finding includes file/line, problem description, and concrete fix.

### Adapting a standard

Target: `agent-config/standards/<name>.md`

Ensure the file has:

1. **H1 title** describing the scope (e.g. "Python Coding Guidelines").
2. **Categorized sections** with H2 headings (e.g. Architecture, API Endpoints, Testing).
3. **Bullet-point guidelines** in imperative voice — concrete and actionable, not vague principles.

### Adapting an MCP server

Target: add entry to `agent-config/mcp/mcp.json` under `mcpServers`

1. Read the existing `agent-config/mcp/mcp.json` first.
2. Add the new server entry. Two patterns exist:
   - **Remote (streamable HTTP):** `"url"` and `"headers"` fields
   - **Local (stdio/Docker):** `"command"`, `"args"`, and `"env"` fields
3. **Replace all real secrets, tokens, and local paths with `<PLACEHOLDER>` syntax** (e.g. `<YOUR_JIRA_TOKEN>`, `<PATH_TO_REPO>`). Never commit real credentials. Placeholder names should be descriptive and match the `<UPPER_SNAKE_CASE>` convention.
4. Preserve the existing JSON structure — add to `mcpServers`, do not overwrite other entries.

## Step 5 — Update the root README.md

Read `README.md` at the repo root. Add a row to the correct table in the "What's Included" section.

**First, ask the engineer if this config is ready for general use or still in progress.** The Slash Commands section has an "In Progress" sub-table for commands that are not yet fully tested or validated. If the engineer says it's still in progress, add it to the "In Progress" table instead, and ask them for a brief status note.

**Match the exact format of existing rows:**

For the main tables:
- **Command:** `| \`/command-name\` | Description starting with a verb (discovers, audits, reviews...) |`
- **Agent:** `| **agent-name** | Role description — what it does (em dash separated) |`
- **Standard:** `| **Standard display name** | What it covers |`
- **MCP server:** `| **Server Name** | What it provides |`

For the "In Progress" table (commands only):
- `| \`/command-name\` | Description | Status note explaining what's left |`

If the README does not yet have an "In Progress" section under the relevant type, create one following the pattern under Slash Commands (an H4 `#### In Progress` heading with a three-column table: Command, What it does, Status).

Insert the new row in a logical position — alphabetical or grouped with related entries.

## Step 6 — Verify completeness

Run through this checklist and report each item:

| Check | Expected |
|-------|----------|
| Config file exists | `agent-config/<type>/<name>.md` (or mcp.json updated) |
| Matches repo conventions | Compare against reference read in Step 3 |
| Root README.md updated | New row in correct table |
| **Commands only:** frontmatter `description` present | Required for Cursor skills — `install_skills()` in install.py skips commands without one |
| **MCP only:** no real secrets | Only `<PLACEHOLDER>` values, no actual tokens or paths |
| install.py changes needed? | No — files in existing directories are auto-discovered by glob. Only flag if the user somehow added a new subdirectory category. |

If anything fails the check, fix it before proceeding.

## Step 7 — Summary and follow-ups

Present a summary:

| Item | Status |
|------|--------|
| Source | `<path to source file>` |
| Config file | Created: `agent-config/<type>/<name>.md` (or mcp.json updated) |
| Root README.md | Updated: added row to `<table name>` table |

Then provide type-specific reminders:

- **Command:** "The `description` in frontmatter is what Cursor uses for skill auto-triggering. Review it to make sure it covers all the scenarios where this command should activate."
- **Agent:** "The `description` field in frontmatter is what Cursor shows in the agent picker. Make sure it clearly says when to use this agent."
- **Standard:** "Standards copy to `{{STANDARDS_DIR}}` for each tool the user installs. In commands/agents, reference them with placeholders: `{{STANDARDS_DIR}}/go-coding-guidelines.md`, `{{PYTHON_STANDARD_FILE}}`, etc. — never hardcode `~/.cursor` or `~/.claude` in distributable agent-config (install.py expands placeholders per target)."
- **MCP server:** "The MCP entry contains placeholder values (in `< >` brackets) that engineers must fill in after install. Make sure the placeholder names are self-explanatory."
- **All types:** "After merging to `main`, engineers pick up the new config by re-running the installer or running `/update-agent-tools`."
