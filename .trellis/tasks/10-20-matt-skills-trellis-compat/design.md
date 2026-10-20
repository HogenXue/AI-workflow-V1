# Design

## Setup ownership

Distribute setup as the tenth manifest Skill. It discovers the selected host and repository
workflow before proposing project-local `docs/agents` configuration. Trellis templates map
tracker verbs to the existing task PRD/plan and domain documentation to Trellis spec paths.
Execution continues through native Trellis skills, including `trellis-check`; upstream Matt
implementation orchestration is not activated by setup. Non-Trellis projects use existing
conventions and require an explicit choice only when the tracker cannot be inferred.

Codex updates the project's `AGENTS.md` outside managed blocks; an existing CLAUDE-only
project can receive a small discoverable AGENTS entry pointing to shared instructions.
Preview precedes edits, existing files are backed up, and repeating setup updates its block.

## Installer ownership

Add opt-in `skills --adopt-skill-lock`. The only lock target is
`<parent of target skills directory>/.skill-lock.json`. Read and validate it before mutating
Skills. A small standard-library helper removes only exact manifest names, preserves other
JSON content, and writes atomically. Missing locks or absent names are no-ops. Symlink or
invalid locks fail before installation. Detaching update registration leaves the adapted
copies under AI-workflow's installer; an explicit future upstream reinstall can overwrite
them and must be documented.

The existing timestamped backup helper and per-component rollback cover both Skills and
the lock. Back up the lock before replacing any Skill; update it only after all copies
succeed. If the lock update fails, restore Skills and the exact old lock.

## Impact and limits

The shared shell installer and its tests are affected; MCP, hooks and task state-machine
code are untouched. GitNexus query returned no installer flows and impact reported the Bash
target was not indexed, so no graph-based risk conclusion is claimed. Source review and
temporary-directory installation tests supply evidence instead.
