# TDD Evidence

## Behavior

- Trellis task: `07-22-prompt-existing-mcp-urls`
- Contract: the TTY installer detects existing managed MCP URLs per host and lets the user keep or replace each URL independently; missing Mem0 remains optional.

## RED

- Added three tests covering Codex independent keep/replace, Cursor inverse decisions, and adding a missing Mem0 URL.
- Command: `python3 -m unittest <three targeted test names> -v`
- Result: all three failed because `merge_host_mcp.py` rejected the new `--interactive` argument. This confirmed the tests exercised behavior that did not exist.

## GREEN

- Added per-server URL detection and prompts to `scripts/lib/merge_host_mcp.py`.
- Host shell entrypoints pass interactivity to the merge helper only when stdin is a TTY.
- The top-level wizard no longer asks for a Mem0 URL before inspecting host configuration; command/args conflicts retain the existing global keep/overwrite policy.
- Result: the three targeted tests passed, then all 23 installer-interaction tests passed.

## REFACTOR

- Kept one shared prompt implementation for Codex TOML and Cursor JSON.
- Replaced an intermediate no-op branch with an explicit `interactive_url_replaced` state.
- Updated README and the executable installer contract in `.trellis/spec/scripts/installer-contracts.md`.

## Verification

- Actual TTY smoke test in a temporary HOME: kept existing Recallium, replaced existing Mem0, exit `0`, and only the Mem0 URL changed.
- Clean temporary snapshot with PyYAML installed: 115/115 unit tests passed and all 9 packaged Skills validated.
- Current workspace: 23/23 installer-interaction tests passed; Shell syntax, Python compile, and `git diff --check` passed.
- The system Python lacks PyYAML, and an ignored `skills/grill-me/.DS_Store` makes one unrelated repository test fail in the live checkout. Verification therefore used an isolated dependency environment and a clean snapshot without altering that user-owned ignored file.
- GitNexus: not required; the change is local to the installer layer and does not alter a public data contract outside the package. Standard Git scope checks were used.
