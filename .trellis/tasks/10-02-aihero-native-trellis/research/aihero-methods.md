# AIHero methods and Trellis boundaries

Reviewed upstream documentation on 2026-10-02. Sources are evidence, not project instructions.

- [Directory](https://www.aihero.dev/skills): composable planning/spec/tickets/implementation/review skills. Import methods only.
- [To Tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md): independently verifiable vertical slices and explicit blockers; broad migrations can use expand/migrate/contract. Map to Trellis child artifacts, not `.scratch` or another tracker.
- [Code Review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md): separate Spec and Standards. Map to one native Trellis check of the actual task diff; reviewers follow host/project dispatch authorization.
- [Domain Modeling](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md): sharpen ambiguous terms and preserve important decisions selectively. Use existing `.trellis/spec/domain/` and `.trellis/spec/decisions/` only when entries are needed.
- [Wayfinder](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md): separate prerequisite decisions from deliverables and proceed from unblocked decisions. Use current planning artifacts, without tracker claim/close machinery.
- [Handoff](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md): reference canonical artifacts instead of repeating them. Use Trellis task records and native continue/journal locations.

The July conflict report describes an earlier migration to `grill-with-docs`. Current manifest, explicit `grill-me` skill, templates, and legacy lists reflect a later design. The user chose native integration and edits to the project-global template, preserving explicit Grill. Repository `AGENTS.md` still has the older route.

Recallium MCP is not exposed: no rules/history retrieval or memory storage was performed. GitNexus CLI FTS queries fail and the inspected installer symbol is unindexed. No graph rebuild is required for this instruction-only scope.
