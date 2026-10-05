# Implementation Plan

- [x] Record baseline and source evidence, then activate this session's task.
- [x] Integrate AIHero methods into the project-global template and align project routing.
- [x] Improve native planning, workflow, review, and continuation instructions without lifecycle machinery.
- [x] Record the durable ownership decision in Trellis specs.
- [x] Run native `task.py validate`, skill structure validation, selected route checks, and task-scoped whitespace checks.
- [x] Perform native `trellis-check` against Spec and Standards; record results and uncovered boundaries in `verification.md`.

## Verification scope

Documentation-only: validate modified native skill frontmatter, packaged skill structure/config consumers, and existing routing tests. Do not change wording-only tests to mirror new instructions. Inspect breadcrumb/phase agreement and task scope manually. Record pre-existing/concurrent failures without repairing unrelated behavior.

## Rollback points

Project-global/project-routing hunks; native workflow/skills/continue/check-agent hunks; new decision document. No installer execution or Git action is authorized. Keep the task in progress until the authorized Git/finish sequence is completed.
