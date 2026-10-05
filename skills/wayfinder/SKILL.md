---
name: wayfinder
description: "Map prerequisite decisions for a large uncertain effort in current planning artifacts. Use before deliverables are settled, not routine task splitting."
license: MIT
---

# Wayfinder

Adapted from Matt Pocock's AIHero skills. Wayfinding resolves decisions; it does not silently begin delivering the entire effort.

1. Name the destination and scope from the user's request. Read prior planning, decisions, research, and source evidence before reopening settled questions.
2. Map precise unanswered questions, their dependencies, and how to resolve them: source research, user choice, or a bounded prototype. Separate in-scope uncertainty that cannot yet be phrased from explicitly excluded work.
3. Work only prerequisite-ready questions. Do not substitute agent opinions for user choices. Research is evidence, not authorization to implement; prototypes need a bounded question and authorized scope.
4. Record the resolution and evidence at its owning location, then update links/order as dependencies become clear. Reconsider newly invalidated assumptions without duplicating the resolved decisions.
5. Hand off once no blocking decision remains. Use `to-spec`/`to-tickets` within native planning for actual deliverables rather than continuing an artificial decision workflow.

## Trellis map

Use the matching task's `design.md` for its decision map: destination, unresolved choices, prerequisites, next evidence, and pointers to resolutions. Keep requirements in `prd.md`, execution order in `implement.md`, and research under `research/`. Create child tasks only for independently verifiable deliverables, not every question. Durable domain decisions belong in existing spec locations. Use Trellis's real status; do not invent claim/close/frontier statuses, external parent issues, or an extra map file hierarchy.

Without Trellis, follow existing planning/tracker conventions and obtain authorization for external writes. Preserve scope: resolving a decision does not grant task activation, implementation, background agents, commits, or pushes.

Source: [skills/engineering/wayfinder/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/wayfinder/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
