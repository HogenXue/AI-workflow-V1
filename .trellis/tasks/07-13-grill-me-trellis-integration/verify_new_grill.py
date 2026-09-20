"""Verify the single Grill Me package, installer behavior, and active Codex configuration."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
AGENTS_HOME = Path.home() / ".agents"
CODEX_HOME = Path.home() / ".codex"
EXPECTED_SKILLS = [
    "memory",
    "gitnexus",
    "release",
    "karpathy-guidelines-zh",
    "grill-me",
    "tdd",
    "diagnosing-bugs",
    "codebase-design",
    "resolving-merge-conflicts",
]


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store"
    }


run(sys.executable, "scripts/validate-all-skills.py")
run(
    sys.executable,
    "-m",
    "unittest",
    "tests.test_grill_with_docs_trellis_route",
    "tests.test_install",
    "tests.test_validate_all_skills",
    "tests.test_install_interactive",
)
run(
    "bash",
    "-n",
    "scripts/install-codex-merge.sh",
    "scripts/install-skills.sh",
    "scripts/install-agents.sh",
    "scripts/install-config.sh",
)
run("git", "diff", "--check")

manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
assert manifest["skills"] == EXPECTED_SKILLS
for name in EXPECTED_SKILLS:
    source = ROOT / "skills" / name
    installed = AGENTS_HOME / "skills" / name
    assert tree_hashes(source) == tree_hashes(installed), name

for removed in ("grill-with-docs", "grilling", "domain-modeling"):
    assert not (AGENTS_HOME / "skills" / removed).exists(), removed
    assert not (CODEX_HOME / "skills" / removed).exists(), removed

grill = (AGENTS_HOME / "skills" / "grill-me" / "SKILL.md").read_text(encoding="utf-8")
agent = yaml.safe_load(
    (AGENTS_HOME / "skills" / "grill-me" / "agents" / "openai.yaml").read_text(
        encoding="utf-8"
    )
)
for phrase in ("stateless", "decision tree", "frontier", "do not write files"):
    assert phrase in grill
assert agent["policy"]["allow_implicit_invocation"] is False

for relative in (
    "__init__.py",
    "consumers.yaml",
    "defaults.yaml",
    "effective_config.py",
    "project-config.schema.yaml",
    "workflow_check.py",
):
    assert (AGENTS_HOME / "config" / relative).is_file(), relative

assert (ROOT / "AGENTS.global.md").read_bytes() == (CODEX_HOME / "AGENTS.md").read_bytes()
config = tomllib.loads((CODEX_HOME / "config.toml").read_text(encoding="utf-8"))
config_text = (CODEX_HOME / "config.toml").read_text(encoding="utf-8")
assert config["model"] == "gpt-5.6-sol"
assert config["model_reasoning_effort"] == "high"
assert config.get("features", {}).get("hooks") is True
assert "disable_response_storage" not in config_text
assert "type" not in config["mcp_servers"]["gitnexus"]
assert "type" not in config["mcp_servers"]["headroom"]
for name in ("gitnexus", "recallium", "mem0"):
    assert name in config.get("mcp_servers", {}), name

hooks = json.loads((CODEX_HOME / "hooks.json").read_text(encoding="utf-8"))["hooks"]
for event in ("PermissionRequest", "PreToolUse", "PostToolUse", "Stop", "SessionStart"):
    assert event in hooks, event
assert len(hooks["SessionStart"]) == 1
session_hook = CODEX_HOME / "hooks" / "session-start.sh"
assert session_hook.is_file() and os.access(session_hook, os.X_OK)

egm = Path("/Users/hogenxue/Projects/EGM/Agents.md").read_text(encoding="utf-8")
assert "`$grill-me` 是唯一 Grill Skill" in egm
for removed in ("`$grill-with-docs`", "`grilling`", "`domain-modeling`"):
    assert removed not in egm

print("PASS: single Grill Me, nine Skills, config runtime, model, MCPs and merged hooks verified")
