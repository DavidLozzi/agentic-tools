---
description: Create or update a README file to enterprise standard. Use when the user asks to create, update, rewrite, standardize, or review a README, or mentions repo documentation, onboarding docs, or getting started guides.
---

# Enterprise README Standard

This command produces consistent, engineer-focused README files across all repositories. The README is a working document for the engineering team — not a marketing page, not an open-source pitch. Every section should help an engineer either get the project running or make changes confidently.

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Core Principles

**Audience is the engineer.** Write for someone who just got added to the team or is picking up a ticket in this repo for the first time. They need to know what this thing does, how to run it, and how to ship changes. Skip anything that doesn't serve that goal.

**Be specific, not aspirational.** Document what actually exists today. If the test suite is flaky, don't pretend it isn't. If there's a manual deploy step, say so. Engineers trust READMEs that reflect reality.

**Concise over comprehensive.** A README that gets read beats a README that covers everything. Keep sections tight. Link out to deeper docs (wikis, Confluence, `docs/` folders) rather than duplicating them here.

**Consistent structure, flexible depth.** Every README follows the same section order so engineers always know where to look. But sections can be as short as a single sentence if that's all the repo warrants. An internal CLI tool doesn't need the same deployment section as a customer-facing service.

## README Structure

Every README follows this section order. Do not reorder sections — consistency across repos is the point. If a section doesn't apply, include it with a one-line note explaining why (e.g., "This is a library consumed as a dependency — there is no standalone deployment.").

### 1. Title and Overview

Start with the repo name as an H1, followed by one to three sentences explaining what this project does in business and functional terms. Answer: "If someone asks what this repo is, what do I tell them?" Avoid implementation details here — focus on the domain and purpose.

Good: "Order Processing Service handles the lifecycle of customer orders from placement through fulfillment, integrating with the payment gateway and warehouse management system."

Bad: "A Node.js microservice using Express and PostgreSQL." (This is implementation detail, not purpose.)

If the project has a status that engineers should know about (actively maintained, in maintenance mode, deprecated, being replaced by X), state it plainly right after the overview.

### 2. Getting Started

This is the most important section. An engineer should be able to go from a fresh clone to a running local instance by following these instructions without asking anyone for help. Structure it as:

**Prerequisites** — List what needs to be installed before setup (runtime versions, databases, CLI tools, access to internal systems). Be version-specific where it matters. If the project uses a version manager (nvm, pyenv, etc.), say so and reference the config file.

**Setup** — Step-by-step instructions from clone to running. Include the actual commands. Cover:
- Installing dependencies
- Environment configuration (what to copy, what to fill in — reference the Configuration section for details)
- Database setup / migrations / seed data
- Any services that need to be running (Docker containers, local stubs, etc.)

**Running the application** — The command(s) to start the project locally and how to verify it's working (e.g., "Visit http://localhost:3000/health and confirm a 200 response").

When writing this section, look at the actual project files to determine the real commands. Check for Makefiles, Dockerfiles, docker-compose files, package.json scripts, build configs, and similar. Use what actually exists rather than guessing.

### 3. Architecture Overview

Give the engineer a mental model of the codebase. This doesn't need to be exhaustive — one to three paragraphs covering:
- The high-level architecture pattern (monolith, microservice, event-driven, etc.)
- Key directories and what lives in them
- Important boundaries or modules and how they relate
- External systems this project talks to

If there is a more detailed architecture document elsewhere (a `docs/` folder, a wiki page, a design doc), link to it here and keep this section as a brief orientation. The goal is that after reading this, an engineer can look at a file path and roughly guess what it does.

### 4. Configuration & Environment Variables

Document the configuration surface of the application:
- Where environment variables are defined (`.env` files, config services, deployment manifests)
- A table or list of the key environment variables with a description of each, whether they are required or optional, and example values (never include actual secrets)
- How configuration differs across environments (local, staging, production) if relevant
- Where to get values for secrets or credentials (e.g., "Request access to the team vault in 1Password" or "See the secrets section in the team wiki")

If the project has a `.env.example` or similar template file, reference it here and explain how to use it.

### 5. Running Tests

Cover the practical details an engineer needs to run the test suite:
- The command to run all tests
- How to run a specific test file or test case
- Any setup required before tests run (test database, fixtures, environment variables)
- What types of tests exist (unit, integration, end-to-end) and how to run each category if they're separated
- Known issues or flaky tests to be aware of

If the project has CI that runs tests, mention what CI runs and note any differences between local and CI test execution.

### 6. Linting & Formatting

Document the code quality tools the project uses:
- What linter(s) and formatter(s) are configured (ESLint, Prettier, Ruff, Black, etc.)
- The command to run linting and formatting
- Whether there is an auto-fix command
- Editor setup recommendations (e.g., "Install the ESLint VS Code extension for real-time feedback")
- Whether CI enforces these checks (and what happens if they fail — does the build break?)

If the project uses pre-commit hooks or similar automation, document those here so engineers aren't surprised by them.

### 7. Deployment

Explain how code gets from a merged PR to production:
- The CI/CD pipeline: what triggers it, what it does, where to monitor it
- Branch strategy and how it relates to environments (e.g., "`main` auto-deploys to staging; production deploys require a manual approval in GitHub Actions")
- Any manual steps required for a deploy
- How to verify a deployment succeeded
- How to rollback if something goes wrong

If deployment is complex and documented in detail elsewhere, keep this section as a summary with links to the full runbook.

### 8. Troubleshooting

A curated list of problems engineers actually hit, with solutions. This section grows over time. Seed it with anything you discover during setup or that is apparent from project configuration. Format each item as:

**Problem:** Brief description of the symptom.
**Solution:** What to do about it.

Common candidates: port conflicts, dependency installation errors on specific OSes, database connection issues, authentication/credential problems, known incompatibilities.

If there is a broader support channel or runbook for production issues, link to it here — this section is for local development gotchas, not production incident response.

### 9. Ownership & Contact

Engineers need to know who to ask when the README doesn't have the answer:
- Which team owns this repo
- Primary communication channel (Slack channel, Teams channel, email distribution list)
- Links to relevant dashboards, on-call rotations, or incident response docs if applicable

Keep this short. One to three lines is usually sufficient.

## Process for Writing or Updating a README

When you are asked to create or update a README:

1. **Examine the repo first.** Before writing anything, look at the project's actual files to understand the tech stack, build tools, directory structure, and existing documentation. Check for: `package.json`, `Makefile`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml`, `Cargo.toml`, `.env.example`, CI config files (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`), and existing `docs/` folders. The README should reflect reality, not assumptions.

2. **Preserve existing useful content.** If updating an existing README, read it thoroughly first. Migrate any accurate, useful information into the new structure rather than discarding it. If something in the old README is outdated, flag it to the user rather than silently dropping it.

3. **Use the section order defined above.** Do not rearrange sections. If a section is not applicable, include the heading with a brief explanation of why it's skipped.

4. **Write in plain, direct language.** Use the imperative for instructions ("Run `npm install`", "Set the `DATABASE_URL` variable"). Avoid jargon unless it's the project's actual terminology. Don't pad sections with filler.

5. **Include real commands.** Every action an engineer needs to take should include the actual command. Don't say "install dependencies" — say `npm install` or `pip install -r requirements.txt` or whatever the project actually uses.

6. **Flag unknowns.** If you can't determine something from the codebase (e.g., who owns the repo, how deploys work, where to get credentials), insert a clear placeholder like `<!-- TODO: [Team] to fill in deployment process -->` so it's obvious what still needs human input.

7. **Keep formatting minimal.** Use headers for the defined sections. Use code blocks for commands. Use tables only for structured data like environment variables. Avoid badges, decorative elements, and excessive formatting. The README is a reference document, not a landing page.
