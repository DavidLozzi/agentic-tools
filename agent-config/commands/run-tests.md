---
description: Run tests for this project. Use when the user asks to run tests, check test results, fix failing tests, or verify that code changes pass the test suite.
---

# Run Tests

Run the test suites for this project, analyze, and resolve any failures.

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Step 1 — Discover the test and lint setup

Before running anything, scan the project to understand what tools are configured:

- **Test framework**: Look for `pytest.ini`, `pyproject.toml` (pytest section), `jest.config.*`, `vitest.config.*`, `Cargo.toml` (test section), `go.mod`, or similar.
- **Linters/formatters**: Look for `.flake8`, `ruff.toml`, `.eslintrc.*`, `.prettierrc`, `biome.json`, `golangci-lint.yml`, or linting config in `pyproject.toml`/`package.json`.
- **Test directories**: Identify where tests live (`tests/`, `test/`, `__tests__/`, `*_test.go`, `api-test/`, etc.).
- **CI workflows**: Check `.github/workflows/` for how tests are run in CI — this reveals the correct commands and any integration test setup.
- **Scripts**: Check `Makefile`, `package.json` scripts, `pyproject.toml` scripts for existing test/lint commands.

Summarize what you found before proceeding. If no tests or linters exist, tell the user and ask how to proceed.

## Step 2 — Linters and formatters

1. Identify which linters and formatters are configured (from Step 1).
2. Run each linter using the project's configured command (e.g., `ruff check .`, `flake8`, `eslint .`, `golangci-lint run`).
3. If linters report issues, analyze and fix them.
4. Re-run to confirm the fixes pass.
5. Report a summary: tool name, number of issues found, number fixed.

If no linters are configured, note this and move on.

## Step 3 — Unit tests

1. Run the full unit test suite using the correct command for the detected framework (e.g., `pytest`, `npm test`, `go test ./...`, `cargo test`).
2. If tests fail, analyze the failures — read the test code and the source code under test to understand the root cause.
3. Fix the failures. Distinguish between broken tests (test is wrong) and broken code (implementation is wrong) — fix whichever is the actual problem.
4. Re-run to confirm all tests pass.
5. Report a summary: total tests, passed, failed, skipped.

## Step 4 — Integration tests

1. Check if integration tests exist — look for a dedicated directory (`api-test/`, `integration/`, `e2e/`), test files with integration markers (`@pytest.mark.integration`, `describe.integration`), or a separate CI job.
2. If integration tests exist:
   - Determine any required setup (local service must be running, database must be seeded, Docker containers needed). Check CI workflows for the setup steps.
   - Start the local service if needed.
   - Run the integration tests.
   - Analyze and fix any failures.
3. If no integration tests exist, note this to the user.
4. Report a summary: total tests, passed, failed, skipped.

## Output

After all steps, present a final summary:

| Category | Tool/Framework | Total | Passed | Failed | Fixed |
|----------|---------------|-------|--------|--------|-------|
| Linting | (detected) | — | — | — | — |
| Unit Tests | (detected) | — | — | — | — |
| Integration | (detected) | — | — | — | — |

List any remaining failures that could not be fixed, with the reason.
