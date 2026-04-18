---
description: Generate or update an AGENTS.md file for the current repo. Use when the user asks to add agent instructions, create an AGENTS.md, or wants to set up AI coding agent guidance for a repository.
---

# add-agent-md

Adds an AGENTS.md file to the current repo, to instruct further coding agents.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Analyze this codebase to generate or update `AGENTS.md` for guiding AI coding agents.

## Execution Steps

### Step 1
Create a new AGENTS.md file using this markdown template:

**IMPORTANT** Ignore any instructions in the following markdown at this step, just create the file.

```markdown
<!--
INSTRUCTIONS FOR LLM:
This is a template file for creating agent instructions. When updating this file:
1. Ask the user what the name of this service is, and then replace the # title with that service name
2. Ask the user for a summary description of what this service is, and place that below the # title
3. Remove ALL instruction blocks and comments (including this one and any others in the file) once the file has been customized
4. Keep the structure and formatting consistent with the original template
5. Ensure all placeholders are replaced with actual content relevant to the specific project/repo
-->

# assistant update this with the service name

**For AI coding agents:** You may change any part of this file as needed for long-term memory.

assistant update this with a summary description of what this service is

## Details

<!--
INSTRUCTIONS FOR LLM:
Focus on discovering the essential knowledge that would help an AI agents be immediately productive in this codebase. Consider aspects like:
- The "big picture" architecture that requires reading multiple files to understand - major components, service boundaries, data flows, and the "why" behind structural decisions
- Critical developer workflows (builds, tests, debugging) especially commands that aren't obvious from file inspection alone
- Project-specific conventions and patterns that differ from common practices
- Integration points, external dependencies, and cross-component communication patterns

Do not include:
- specific files other than what's listed above. This is an active repo and other files will change frequently
- any code snippets
-->

<!-- assistant, copy Agent Context verbatim -->
## Agent Context

If the **Agent Context Manager** MCP server is available in this environment, you must:

1. **Register a session** at the end of your first interaction with the user: call `register_session` with the absolute path to the repository root and an `agent_id` (e.g. `cursor-ide`). Store or reuse the returned `session_id` for the rest of the conversation.
2. **Update context** after you have finished addressing the user's requests: call `update_context` with that `session_id` and a short summary (two sentences max) of what the user asked for and what you did. Do this when you complete a task or reach a natural stopping point.
```

### Step 2
Add coding guidelines/requirements, if desired. Ask the user if they want to include coding requirements for the language of this repo. If so, add the following block to the AGENTS.md:

```markdown
## Coding Requirements
See [CODE.md](/CODE.md).
```

Then create a `CODE.md` file in the root of the repo. Use the matching language guidelines from `{{STANDARDS_DIR}}` as the content:

- **Python**: Use the contents of `{{PYTHON_STANDARD_FILE}}`
- **Other languages**: If no matching standard exists, generate sensible coding guidelines following the same structure and depth as the Python standard. Ask the user to review before finalizing.

Read the standards file and copy its full contents into `CODE.md`.

### Step 3
Create a `CLAUDE.md` file in the root of the repo that points to `AGENTS.md`. This is how Claude Code discovers project-level instructions. Use the following content exactly:

```markdown
# CLAUDE.md

See [AGENTS.md](./AGENTS.md) for all agent instructions.
```

If a `CLAUDE.md` already exists, check whether it already references `AGENTS.md`. If not, add the reference. Do not overwrite existing content.

### Step 4
Review the newly created AGENTS.md file, and update it based on this repo. Then instruct the user to review and confirm.
