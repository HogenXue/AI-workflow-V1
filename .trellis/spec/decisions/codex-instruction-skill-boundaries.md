# Codex instruction scope and skill ownership

Date: 2026-10-05. Accepted implementation within the user's official-guidance optimization request.

## Decision

Global templates hold reusable defaults and concise workflow/action boundaries. Project templates hold local artifact destinations, conditional guides and actual validation requirements. Root project additions preserve managed blocks and do not reproduce the global policy. PRD/design supply task facts, not a new prompt privilege hierarchy. Skills support the current action under effective instructions and tool permissions without expanding authorization.

Keep the existing 18-skill local package and invocation policies. Narrow descriptions for the new capabilities so discovery, synthesis, deliverable splitting, uncertain decision mapping, domain language, module design, external research, debugging, prototypes, implementation, review and continuation are distinguishable. Use one primary owner per action and complementary methods only when needed. Native Trellis owns lifecycle, artifacts, dispatch and final checks.

Codex's scoped AGENTS discovery and same-name skill behavior are host mechanisms; do not invent template-name discovery, automatic same-name merging, or a project-skill priority override. If conflicting installed copies exist, select/identify the effective source without unauthorized removal. Source templates become live user guidance only through an explicitly requested install. Other hosts retain their native loading mechanism.

## Why

The former global template repeated validation/authorization rules and presented task artifacts as a custom instruction-priority layer. Broad overlapping descriptions could cause several workflows to claim one request. Concise scope and trigger boundaries reduce context and duplicate actions while retaining non-obvious native state/authorization safeguards.

## Evidence and limits

Official sources were searched and opened on 2026-10-05. Structure checks, a description-based sample with explicit/implicit/negative cases, and isolated distribution checks support this implementation. These are not a guarantee of every future model/tool combination. No plugin migration, live Codex config edit, API/model setup, runtime installer change or global removal is authorized by this decision.

## Sources

- [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Skills](https://learn.chatgpt.com/docs/build-skills)
- [Instruction/description discipline](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Targeted skill evaluations](https://developers.openai.com/blog/eval-skills)
