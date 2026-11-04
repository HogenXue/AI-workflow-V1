# Domain documentation: Trellis

Read `.trellis/spec/domain/` for canonical domain vocabulary and relevant
`.trellis/spec/decisions/` entries for durable trade-offs before exploring the affected area.
Use any more specific locations defined by the project's Trellis rules.

Missing domain documentation does not block work. Create or update it only when a real
term or durable decision has been confirmed through the current workflow.

- Domain terms: define the canonical name and meaning under `.trellis/spec/domain/`.
  Keep implementation details, requirements, plans and task status in their task artifacts.
- Durable decisions: use `.trellis/spec/decisions/` when a choice is hard to reverse,
  surprising without context, and the result of an actual trade-off.
- Task-specific choices: use the current task's design, plan or research instead of an ADR.
- Requirements, scope and acceptance: use only the current task's PRD.

When using `domain-modeling` or another upstream Skill, apply its terminology and decision
method to these canonical Trellis locations. Its default `GLOSSARY.md`, `GLOSSARY-MAP.md`
and `docs/adr/` paths do not create additional sources of truth here.

Preserve existing legacy documents until their contents and migration are explicitly
reviewed. If sources disagree, surface the disagreement and resolve it in the current
Trellis task instead of silently copying or overriding a definition.
