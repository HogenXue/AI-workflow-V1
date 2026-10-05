---
name: to-tickets
description: "Split approved scope into verifiable native tasks with explicit blockers. Use for deliverable decomposition, not unresolved decision mapping."
license: MIT
---

# To Tickets

Adapted from Matt Pocock's AIHero skills. Read the agreed requirements, design, existing task tree, and source evidence before proposing slices.

## Slice outcomes

Prefer a small complete path through the necessary layers, verifiable or demonstrable on its own. Do not split solely into schema/API/UI layers, duplicate overlapping acceptance, or create children for routine checklist steps. Record each slice's outcome, acceptance criteria, dependencies, and evidence that clears blockers. Order by actual prerequisites, not numbering.

Broad migrations may require expand, migrate in bounded batches, then contract. Keep compatibility and verification boundaries explicit; do not promise each batch is green if an integration boundary is required. Unresolved decisions remain planning questions, not implementation-ready tickets.

## Use native tasks

In Trellis, resolve and keep the parent task path explicitly. Its PRD is the source requirement set and its `implement.md` is the map/order. Create planning children via `.trellis/scripts/task.py create ... --parent <parent> --no-start`, or link existing children with `add-subtask`. `create` normally changes the session's active-task pointer; `--no-start` preserves the parent planning context while drafting children. Each child owns its PRD and needed design/implementation artifacts; write its real blockers and readiness conditions there. Parent/child links are grouping, not dependency enforcement. Do not create `.scratch` tickets, another tracker, or custom status fields.

Check the project's native `create --help` before using version-specific options. If `--no-start` is unavailable, report the compatibility limit and use only a documented equivalent that preserves planning context; do not use `task.py start` just to restore a pointer, because it can advance status to `in_progress`. After drafting, verify the parent still owns the session and children remain `planning`; explicitly select/activate the authorized deliverable only through the native planning gate.

Present the proposed breakdown when granularity or dependencies require a user decision; reuse an already approved split. Creating children does not start them, close the parent, dispatch agents, or authorize implementation. Choose the next authorized unblocked deliverable through native task activation.

Outside Trellis, use the configured task system and native blocker relationships; if no destination is established, agree one before publication. Do not run setup automatically. External issue writes need authorization. No automatic Git operations.

Source: [skills/engineering/to-tickets/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/to-tickets/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
