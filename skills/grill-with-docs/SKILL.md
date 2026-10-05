---
name: grill-with-docs
description: "Resolve unsettled requirements and record confirmed decisions in the current task. Use for documented discovery, not clear requests or already-confirmed Grill conclusions."
license: MIT
---

# Grill with Docs

Adapted from Matt Pocock's AIHero skills. This is a documented planning capability; `grill-me` remains the explicit stateless conversation.

## Planning ownership

In Trellis, read `.trellis/workflow.md`, resolve the current task, and read its PRD/design/plan and relevant domain/decision specs. Task creation follows existing authorization; consultation alone does not authorize creating a task. This capability replaces the interview inside Phase 1.1, not the task lifecycle. Do not run a second `trellis-brainstorm` interview afterward.

Without Trellis, use the project's established planning documents. Do not initialize Trellis, run upstream setup, or create another tracker/spec hierarchy.

## Interview and capture

1. Inspect repository facts and reuse confirmed decisions before questioning. A clear request needs artifacts rather than an interview.
2. Map unsettled choices by prerequisite. Ask the currently answerable frontier in manageable rounds, with recommendations and trade-offs; follow a user's preference for one question at a time. Do not ask dependent questions before their prerequisites are settled. The `grilling` support skill supplies this method when available.
3. Challenge ambiguous domain terms with concrete cases and check code/spec agreement. Use `domain-modeling` for vocabulary and durable trade-offs when relevant.
4. Capture only confirmed requirements and acceptance criteria in the current PRD. Put task-specific technical choices in `design.md`, execution order in `implement.md`, stable terms in the existing domain location, and durable cross-task trade-offs in the existing decision location. In this project those are `.trellis/spec/domain/` and `.trellis/spec/decisions/`.
5. For research/prototype-dependent choices, record the missing evidence and completion condition; continue independent branches. Investigation does not authorize production implementation or destructive prototype cleanup.
6. End with the agreed scope, testable acceptance criteria, and genuine blockers. Ask only for decisions still requiring user input; reuse explicit implementation authorization when the scope is settled.

Avoid duplicating PRD/design content or creating empty glossary/ADR scaffolds. Do not start implementation, change task status, or perform Git operations merely because the interview finished; return to the native planning gate.

Source: [skills/engineering/grill-with-docs/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/grill-with-docs/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
