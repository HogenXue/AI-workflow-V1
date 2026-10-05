---
name: domain-modeling
description: "Clarify ambiguous business terms and durable domain decisions in existing documents. Does not redesign module interfaces or implement renames."
license: MIT
---

# Domain Modeling

Adapted from Matt Pocock's AIHero skills. Read existing domain documents, applicable decisions, and code before changing the vocabulary.

## Sharpen the language

- Surface terms that conflict with existing definitions. Use concrete examples to distinguish overloaded meanings, actors, relationships, and boundary cases.
- Check whether code agrees with the proposed meaning; show contradictions rather than deciding business intent yourself.
- Record confirmed canonical terms where the project already maintains domain language. Keep definitions focused on meaning, not implementation, requirements, or scratch notes. Create an entry only when a term is resolved.

## Capture decisions selectively

Keep task-specific choices in the current design document. Record a durable decision only when reversing it is costly, its rationale would surprise a future reader, and it resulted from a real trade-off. Include context, chosen option, alternatives, consequences, and status; update or supersede an existing decision instead of duplicating it.

In Trellis, requirements stay in the task PRD, task design stays in `design.md`, and stable vocabulary/decisions use existing `.trellis/spec/` locations (here `domain/` and `decisions/`). Do not add a root `GLOSSARY.md` or `docs/adr/` alongside them. Without Trellis, use the existing glossary/ADR convention and ask only if the document destination remains ambiguous.

Documentation does not authorize renaming symbols, changing APIs/data models, refactoring, or Git operations. Return proposed implementation to the current task and its required impact/validation gates.

Source: [skills/engineering/domain-modeling/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/domain-modeling/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
