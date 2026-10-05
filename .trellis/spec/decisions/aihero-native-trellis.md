# AIHero methods inside native Trellis

Date: 2026-10-02. Status: accepted by the user.

Updated 2026-10-05: the user requested main-flow and support skills as independently installable adapted capabilities. The earlier method-only packaging boundary is superseded; Trellis ownership remains. Eleven added skills cover documented interviewing, spec synthesis, task slicing, decision mapping, research, prototypes, implementation, review, and handoff.

## Decision

Trellis owns task lifecycle, requirements/design/implementation artifacts, checks, and session records. AIHero contributes evidence-first decision questioning, outcome slicing with real blockers, selective domain/decision capture, separate Spec/Standards review, and artifact-based continuity.

Keep `grill-me` explicit and stateless. Documented discovery uses task-bound `grill-with-docs` or equivalent native `trellis-brainstorm`, once. Confirmed conclusions do not trigger another interview. Neither complexity nor cross-module scope alone starts an interview.

Use existing Trellis parent/child tasks and artifact paths. Do not add upstream setup/tracker routing, `.scratch` tickets, a second spec/ADR tree, or upstream implementation/commit orchestration. Native `trellis-check` owns both review dimensions and task-selected checks; independent dimensions do not mandate additional agents.

## Trade-off

Importing the entire upstream chain would offer its native issue-tracker experience but create competing lifecycle and persistence owners. Adapting methods retains Trellis's established contracts and existing explicit Grill behavior, at the cost of maintaining integration guidance locally.

## Distribution boundary

Maintain portable guidance in `agents/AGENTS.global.md` and project additions in `agents/AGENTS.project.md`. Explicit installers distribute those templates and the adapted skills. Development validation uses isolated roots, never live user-level `.codex/AGENTS.md`. Local native instructions apply here; downstream workflows remain project-owned, with capability adaptation included in the installed skills.

## Verification boundary

Batch child planning preserves the parent session pointer with supported native `create --parent ... --no-start`. Default create activates the new child even though its status remains planning. Verify context and statuses explicitly; using start only to restore a pointer can advance status and must not bypass planning gates.

Include actual task scope: staged, unstaged, new files, and earlier task commits when relevant. Report Spec and Standards separately with criterion/rule evidence. Reuse checks while coverage remains valid; identify pre-existing failures without repairing unrelated work. Successful checks do not authorize Git operations or archival.

## References

- [AIHero directory](https://www.aihero.dev/skills)
- [Outcome slicing](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md)
- [Two review dimensions](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md)
- [Selective domain decisions](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md)
- [Artifact-based handoff](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md)
