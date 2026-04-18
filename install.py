#!/usr/bin/env python3
"""
Install agent-config commands, agents, standards, and MCP servers
into Claude Code (~/.claude/) and/or Cursor (~/.cursor/).

Cross-platform: works on Windows, Linux, and macOS.

When run from within the agentic-tools repo, files are read locally.
When run standalone (no agent-config/ directory present), files are fetched
from GitHub. Authentication is required: set GITHUB_TOKEN or use `gh auth login`.

Markdown under agent-config may contain install-time placeholders (expanded when
copying into ~/.claude/ or ~/.cursor/):

  {{TOOL_CONFIG_HOME}}       -> absolute path to ~/.claude or ~/.cursor
  {{STANDARDS_DIR}}         -> .../standards
  {{PYTHON_STANDARD_FILE}}  -> .../standards/python.md

Environment variables:
    GITHUB_TOKEN          - Personal access token for GitHub API auth
    GITHUB_API_BASE       - API base URL (default: https://api.github.com)
    AGENT_CONFIG_BRANCH   - Branch to fetch from (default: main)

Usage:
    python install.py
"""

from __future__ import annotations

import atexit
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).parent
AGENT_CONFIG = REPO_ROOT / "agent-config"

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------------------------
# File copy mappings
# ---------------------------------------------------------------------------

CLAUDE_FILE_MAPPINGS: list[tuple[Path, Path]] = [
    (AGENT_CONFIG / "commands", Path.home() / ".claude" / "commands"),
    (AGENT_CONFIG / "agents", Path.home() / ".claude" / "agents"),
    (AGENT_CONFIG / "standards", Path.home() / ".claude" / "standards"),
]

CURSOR_FILE_MAPPINGS: list[tuple[Path, Path]] = [
    (AGENT_CONFIG / "commands", Path.home() / ".cursor" / "commands"),
    (AGENT_CONFIG / "agents", Path.home() / ".cursor" / "agents"),
    (AGENT_CONFIG / "standards", Path.home() / ".cursor" / "standards"),
]

MCP_SOURCE = AGENT_CONFIG / "mcp" / "mcp.json"
CLAUDE_SETTINGS = Path.home() / ".claude" / "settings.json"
CURSOR_MCP = Path.home() / ".cursor" / "mcp.json"
CURSOR_SKILLS = Path.home() / ".cursor" / "skills"


# ---------------------------------------------------------------------------
# GitHub remote fetch
# ---------------------------------------------------------------------------

GITHUB_API_BASE = os.environ.get("GITHUB_API_BASE", "https://api.github.com")
GITHUB_REPO = "DavidLozzi/agentic-tools"
GITHUB_BRANCH = os.environ.get("AGENT_CONFIG_BRANCH", "main")
AGENT_CONFIG_DIRS = ["commands", "agents", "standards", "mcp"]

# Collected during install — maps "subdir/filename" to its git blob SHA.
_file_shas: dict[str, str] = {}


def resolve_github_token() -> str:
    """
    Return a GitHub token for API auth.
    Tries GITHUB_TOKEN env var first, then `gh auth token`.
    Exits with an error if neither works.
    """
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token

    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except FileNotFoundError:
        pass  # gh CLI not installed
    except subprocess.TimeoutExpired:
        pass

    print(
        "ERROR: No GitHub token found.\n"
        "  Set GITHUB_TOKEN env var or install the GitHub CLI (gh) and run 'gh auth login'.\n"
        "  A token is required to fetch agent-config from GitHub when agent-config/ is not present locally.",
        file=sys.stderr,
    )
    sys.exit(1)


def github_api_get(path: str, token: str) -> dict | list:
    """
    Make an authenticated GET to the GitHub API.
    `path` is relative, e.g. '/repos/owner/repo/contents/agent-config/commands'.
    Returns parsed JSON.
    """
    url = f"{GITHUB_API_BASE}{path}"
    request = urllib.request.Request(url)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/vnd.github.v3+json")
    request.add_header("User-Agent", "agent-config-installer")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        print(
            f"ERROR: GitHub API request failed.\n"
            f"  URL: {url}\n"
            f"  Status: {exc.code}\n"
            f"  Response: {body[:300]}",
            file=sys.stderr,
        )
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(
            f"ERROR: Could not reach GitHub API at {url}\n"
            f"  Reason: {exc.reason}",
            file=sys.stderr,
        )
        sys.exit(1)


def fetch_agent_config_to_temp() -> Path:
    """
    Download the agent-config directory tree from GitHub into a temp dir.
    Returns the Path to the temp agent-config root.
    Registers atexit cleanup for the temp dir.
    """
    token = resolve_github_token()
    tmp_dir = tempfile.mkdtemp(prefix="agent-config-")
    atexit.register(shutil.rmtree, tmp_dir, True)

    print(f"Fetching agent-config from {GITHUB_REPO}@{GITHUB_BRANCH} ...")

    base_api_path = f"/repos/{GITHUB_REPO}/contents/agent-config"

    for subdir in AGENT_CONFIG_DIRS:
        api_path = f"{base_api_path}/{subdir}?ref={GITHUB_BRANCH}"
        entries = github_api_get(api_path, token)

        if not isinstance(entries, list):
            print(f"  WARNING: Unexpected response for {subdir}/ — skipping.")
            continue

        dest_dir = Path(tmp_dir) / subdir
        dest_dir.mkdir(parents=True, exist_ok=True)

        for entry in entries:
            if entry.get("type") != "file":
                continue
            name = entry["name"]
            file_data = github_api_get(
                f"{base_api_path}/{subdir}/{name}?ref={GITHUB_BRANCH}", token
            )
            content_b64 = file_data.get("content", "")
            content_bytes = base64.b64decode(content_b64)

            dest_file = dest_dir / name
            dest_file.write_bytes(content_bytes)
            if "sha" in file_data:
                _file_shas[f"{subdir}/{name}"] = file_data["sha"]
            print(f"    {subdir}/{name}")

    print()
    return Path(tmp_dir)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Must match longest keys first so partial overlaps never apply incorrectly.
_INSTALL_PLACEHOLDER_ORDER = (
    "{{PYTHON_STANDARD_FILE}}",
    "{{STANDARDS_DIR}}",
    "{{TOOL_CONFIG_HOME}}",
)


def expand_install_placeholders(text: str, tool: str) -> str:
    """
    Replace {{...}} paths for the target tool (claude | cursor).
    Uses absolute paths so file reads work on every OS.
    """
    if tool not in ("claude", "cursor"):
        raise ValueError(f"unknown tool: {tool!r}")
    root = Path.home() / (".claude" if tool == "claude" else ".cursor")
    standards = root / "standards"
    replacements = {
        "{{TOOL_CONFIG_HOME}}": str(root),
        "{{STANDARDS_DIR}}": str(standards),
        "{{PYTHON_STANDARD_FILE}}": str(standards / "python.md"),
    }
    for key in _INSTALL_PLACEHOLDER_ORDER:
        text = text.replace(key, replacements[key])
    return text


def prompt_yes_no(message: str, default_yes: bool = False) -> bool:
    suffix = " [Y/n]: " if default_yes else " [y/N]: "
    while True:
        answer = input(message + suffix).strip().lower()
        if answer == "":
            return default_yes
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please enter y or n.")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """
    Parse YAML-style frontmatter from a markdown file.
    Returns (metadata_dict, body_without_frontmatter).
    If no frontmatter, returns ({}, original_text).
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    frontmatter = text[3:end].strip()
    body = text[end + 3:].lstrip("\n")
    metadata: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()
    return metadata, body


def install_skills(src_dir: Path, dest_dir: Path) -> list[tuple[str, str]]:
    """
    Convert command .md files with frontmatter into Cursor skill folders.
    Each skill becomes dest_dir/{name}/SKILL.md with name + description frontmatter.
    Returns list of (skill_name, status) tuples.
    """
    results = []
    if not src_dir.exists():
        return results

    for src_file in sorted(src_dir.glob("*.md")):
        text = src_file.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(text)
        description = expand_install_placeholders(
            metadata.get("description", "").strip(), "cursor"
        )
        if not description:
            continue  # skip commands without a description

        skill_name = src_file.stem
        skill_dir = dest_dir / skill_name
        skill_file = skill_dir / "SKILL.md"

        body = expand_install_placeholders(body, "cursor")
        skill_content = f"---\nname: {skill_name}\ndescription: {description}\n---\n\n{body}"

        if skill_file.exists():
            replace = prompt_yes_no(f"  Skill {skill_name}/ already exists. Replace?")
            if not replace:
                results.append((skill_name, "skipped"))
                continue
            backup_file(skill_file)

        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(skill_content, encoding="utf-8")
        results.append((skill_name, "installed"))

    return results


def backup_file(path: Path) -> Path:
    backup = path.with_suffix(f"{path.suffix}.bak.{TIMESTAMP}")
    shutil.copy2(path, backup)
    return backup


def install_file(src: Path, dest: Path, tool: str) -> str:
    """
    Write src to dest with install placeholders expanded for `tool`.
    If dest exists, ask the user whether to replace it.
    Returns a status string: 'installed', 'replaced', 'skipped'.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    already_existed = dest.exists()

    if already_existed:
        replace = prompt_yes_no(f"  {dest} already exists. Replace?")
        if not replace:
            return "skipped"
        backup = backup_file(dest)
        print(f"    Backed up to {backup.name}")

    text = expand_install_placeholders(src.read_text(encoding="utf-8"), tool)
    dest.write_text(text, encoding="utf-8")
    return "replaced" if already_existed else "installed"


def install_directory(src_dir: Path, dest_dir: Path, tool: str) -> list[tuple[str, str]]:
    """
    Copy all *.md files from src_dir into dest_dir with placeholders expanded.
    Returns list of (filename, status) tuples.
    """
    results = []
    if not src_dir.exists():
        return results

    for src_file in sorted(src_dir.glob("*.md")):
        dest_file = dest_dir / src_file.name
        status = install_file(src_file, dest_file, tool)
        results.append((src_file.name, status))

    return results


def find_placeholders(obj: object, path: str = "") -> list[tuple[str, str]]:
    """
    Recursively find values matching <...> pattern in a JSON-like structure.
    Returns list of (dot-path, value) tuples.
    """
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.extend(find_placeholders(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(find_placeholders(v, f"{path}[{i}]"))
    elif isinstance(obj, str) and re.search(r"<[^>]+>", obj):
        found.append((path, obj))
    return found


def git_blob_sha(data: bytes) -> str:
    """Compute the SHA-1 hash the same way git does for blob objects."""
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def collect_local_shas() -> None:
    """Walk AGENT_CONFIG subdirs and compute git blob SHAs for each file."""
    for subdir in AGENT_CONFIG_DIRS:
        src_dir = AGENT_CONFIG / subdir
        if not src_dir.exists():
            continue
        for src_file in sorted(src_dir.iterdir()):
            if src_file.is_file():
                key = f"{subdir}/{src_file.name}"
                _file_shas[key] = git_blob_sha(src_file.read_bytes())


def write_manifest(tool_dir: Path) -> None:
    """Write .agent-config-manifest.json into the tool's config directory."""
    manifest = {
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": GITHUB_REPO,
        "branch": GITHUB_BRANCH,
        "files": dict(sorted(_file_shas.items())),
    }
    manifest_path = tool_dir / ".agent-config-manifest.json"
    write_json(manifest_path, manifest)
    print(f"  Manifest written to {manifest_path}")


def read_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  WARNING: {path} contains invalid JSON — treating as empty.")
    return {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def install_mcp(config_path: Path, label: str) -> list[str]:
    """
    Merge mcpServers from MCP_SOURCE into config_path.
    For ~/.claude/settings.json: preserves all other keys.
    For ~/.cursor/mcp.json: file is MCP-only.
    Returns list of placeholder warning strings.
    """
    if not MCP_SOURCE.exists():
        print(f"  WARNING: {MCP_SOURCE} not found — skipping MCP install.")
        return []

    source_data = read_json(MCP_SOURCE)
    source_servers: dict = source_data.get("mcpServers", {})

    if not source_servers:
        print("  No mcpServers found in source mcp.json — skipping.")
        return []

    existing_data = read_json(config_path)
    existing_servers: dict = existing_data.get("mcpServers", {})

    backed_up = False
    installed_servers: set[str] = set()
    for server_name, server_config in source_servers.items():
        if server_name in existing_servers:
            replace = prompt_yes_no(
                f"  MCP server \"{server_name}\" already configured in {config_path}. Replace?"
            )
            if not replace:
                print(f"    Skipped \"{server_name}\"")
                continue
            if not backed_up:
                backup = backup_file(config_path)
                print(f"    Backed up {config_path.name} to {backup.name}")
                backed_up = True

        existing_servers[server_name] = server_config
        installed_servers.add(server_name)
        print(f"    Added MCP server: {server_name}")

    existing_data["mcpServers"] = existing_servers
    write_json(config_path, existing_data)

    # Find placeholders only in servers we actually installed
    warnings = []
    for server_name in installed_servers:
        server_config = source_servers[server_name]
        for dot_path, value in find_placeholders(server_config, server_name):
            warnings.append(f"  {config_path}  →  {dot_path} = \"{value}\"")

    return warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def select_tools() -> list[str]:
    print("\nInstall for which tools?")
    print("  [1] Claude Code  (~/.claude/)")
    print("  [2] Cursor       (~/.cursor/)")
    print("  [3] Both")
    print()

    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice == "1":
            return ["claude"]
        if choice == "2":
            return ["cursor"]
        if choice == "3":
            return ["claude", "cursor"]
        print("  Please enter 1, 2, or 3.")


def run_claude(summary: dict, mcp_warnings: list[str]) -> None:
    print("\n── Claude Code ──────────────────────────────")
    results = []

    for src_dir, dest_dir in CLAUDE_FILE_MAPPINGS:
        category = src_dir.name
        print(f"\n  {category}/")
        dir_results = install_directory(src_dir, dest_dir, "claude")
        for filename, status in dir_results:
            print(f"    {status:10s}  {filename}")
        results.extend(dir_results)

    print("\n  MCP servers  (→ ~/.claude/settings.json)")
    mcp_warnings.extend(install_mcp(CLAUDE_SETTINGS, "Claude Code"))

    summary["claude"] = results


def run_cursor(summary: dict, mcp_warnings: list[str]) -> None:
    print("\n── Cursor ───────────────────────────────────")
    results = []

    for src_dir, dest_dir in CURSOR_FILE_MAPPINGS:
        category = src_dir.name
        print(f"\n  {category}/")
        dir_results = install_directory(src_dir, dest_dir, "cursor")
        for filename, status in dir_results:
            print(f"    {status:10s}  {filename}")
        results.extend(dir_results)

    print(f"\n  skills/  (→ {CURSOR_SKILLS})")
    commands_dir = AGENT_CONFIG / "commands"
    skill_results = install_skills(commands_dir, CURSOR_SKILLS)
    for skill_name, status in skill_results:
        print(f"    {status:10s}  {skill_name}/")
    results.extend(skill_results)

    print("\n  MCP servers  (→ ~/.cursor/mcp.json)")
    mcp_warnings.extend(install_mcp(CURSOR_MCP, "Cursor"))

    summary["cursor"] = results


def print_summary(summary: dict, mcp_warnings: list[str]) -> None:
    print("\n── Summary ──────────────────────────────────")
    for tool, results in summary.items():
        if not results:
            continue
        installed = sum(1 for _, s in results if s in ("installed", "replaced"))
        skipped = sum(1 for _, s in results if s == "skipped")
        print(f"  {tool.title():12s}  {installed} installed/replaced, {skipped} skipped")

    if mcp_warnings:
        print("\n  NOTE: The following MCP values contain placeholders you must fill in:")
        seen = set()
        for w in mcp_warnings:
            if w not in seen:
                print(w)
                seen.add(w)

    print()


def main() -> None:
    global AGENT_CONFIG, CLAUDE_FILE_MAPPINGS, CURSOR_FILE_MAPPINGS, MCP_SOURCE

    print("agent-config installer")
    print("======================")

    if not AGENT_CONFIG.exists():
        AGENT_CONFIG = fetch_agent_config_to_temp()
        CLAUDE_FILE_MAPPINGS = [
            (AGENT_CONFIG / "commands", Path.home() / ".claude" / "commands"),
            (AGENT_CONFIG / "agents", Path.home() / ".claude" / "agents"),
            (AGENT_CONFIG / "standards", Path.home() / ".claude" / "standards"),
        ]
        CURSOR_FILE_MAPPINGS = [
            (AGENT_CONFIG / "commands", Path.home() / ".cursor" / "commands"),
            (AGENT_CONFIG / "agents", Path.home() / ".cursor" / "agents"),
            (AGENT_CONFIG / "standards", Path.home() / ".cursor" / "standards"),
        ]
        MCP_SOURCE = AGENT_CONFIG / "mcp" / "mcp.json"
    else:
        collect_local_shas()

    tools = select_tools()
    summary: dict = {}
    mcp_warnings: list[str] = []

    if "claude" in tools:
        run_claude(summary, mcp_warnings)

    if "cursor" in tools:
        run_cursor(summary, mcp_warnings)

    if _file_shas:
        print("\n── Version Tracking ─────────────────────────")
        if "claude" in tools:
            write_manifest(Path.home() / ".claude")
        if "cursor" in tools:
            write_manifest(Path.home() / ".cursor")

    print_summary(summary, mcp_warnings)
    print("Done.")


if __name__ == "__main__":
    main()
