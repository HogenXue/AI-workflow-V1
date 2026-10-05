---
name: to-spec
description: "Synthesize already-agreed requirements into the existing PRD or spec. Use for document synthesis, not interviewing or task decomposition."
license: MIT
---

# To Spec

Adapted from Matt Pocock's AIHero skills. Synthesize what is already agreed; do not manufacture another interview.

In Trellis, resolve the matching task and read its current artifacts/specs. Write requirements to its `prd.md`, design choices to `design.md`, and execution/test commands to `implement.md` where needed. Follow native authorization if a task must be created. Never publish a second spec to `.scratch`, another tracker, or `docs/agents`.

Without Trellis, update the established spec or user-selected tracker destination. An external publication requires the corresponding authorization; drafting locally is not permission to publish or create external issues.

## Synthesis

1. Inspect relevant sources to verify facts, domain language, and contract constraints. Preserve accepted decisions and anchors in an existing specification.
2. State the user problem, goal, in-scope behavior, constraints, scenarios, acceptance criteria, and exclusions. Keep the number of stories proportionate to the feature; do not expand scope merely to fill a template.
3. Make acceptance observable. Prefer existing high-level behavioral seams over implementation-detail assertions; expose a testing choice only if it remains a genuine user decision.
4. Separate known facts from unresolved assumptions. Keep genuine blockers visible; do not silently resolve ambiguity while synthesizing.
5. Read the result for duplicates, contradictions, and requirement-to-acceptance coverage. Preserve previous information, and summarize meaningful changes and remaining blockers.

Complex Trellis work also needs native design/implementation artifacts before start. A completed spec does not itself authorize implementation, task-state changes, or Git operations; reuse existing authorization through the project's planning gate.

Source: [skills/engineering/to-spec/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/to-spec/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
