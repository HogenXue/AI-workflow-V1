# Trellis check — 2026-09-20

## Scope

- single `grill-me` Skill and invocation metadata;
- manifest and Bash/PowerShell Skill installers;
- Codex hooks event-level merge behavior;
- global, project, Trellis workflow, and EGM routing text;
- actual `~/.agents` / `~/.codex` installation state.

## Findings

No P0/P1 findings in the reviewed scope.

- The explicit-only policy is present in both Skill frontmatter and `agents/openai.yaml`.
- The Skill is stateless and does not own Trellis persistence, implementation, tests, Git, or deployment.
- The latest Grill method is retained: decision tree, dependency-aware frontier rounds, agent-owned facts, user-owned decisions, and a stopping boundary for ungrillable questions.
- Existing Codex hook events are preserved; the managed SessionStart entry is idempotent and covered by a RED/GREEN regression test.
- Existing user changes to LAN MCP URL validation, the unrelated 09-18 task, and the project-owned `AGENTS.md` deletion were not reverted or included as this task's implementation.

## Verification boundary

The checks prove package structure, installer behavior, file synchronization, and current on-disk configuration. A new Codex task or app restart is still required to verify UI discovery of the updated Skill and adoption of the new default model.
