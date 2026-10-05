---
name: code-review
description: "Review a defined diff against requirements and project standards. Read-only unless fixes are authorized; share the native Trellis quality gate."
license: MIT
---

# Code Review

Adapted from Matt Pocock's AIHero skills. This is analysis inside the current quality workflow, not another task lifecycle or automatic fix/commit command.

## Fix the scope

Use the user's stated branch/commit/base or the verified current task baseline. Confirm it resolves. For branch changes inspect the merge-base diff and commits; for current work also include staged, unstaged, and task-owned untracked files. A clean working tree does not exclude earlier task commits. Separate unrelated user changes. An unresolved base or task boundary is a limitation to resolve, not permission to choose an arbitrary diff.

In Trellis read the task PRD, relevant design/plan, and project specs. Do not ask for upstream setup or a tracker when these exist. Outside Trellis use the established originating requirement document; if absent, explicitly mark Spec review unavailable.

## Two dimensions

- **Spec**: map acceptance criteria to behavior and evidence; identify missing/partial requirements, incorrect edge/failure behavior, contract/design mismatches, and unauthorized scope growth. Cite the criterion and relevant file/line.
- **Standards**: cite documented rules for hard violations. Consider naming, duplication, scattered changes, unnecessary abstractions, and module boundaries as relevant design heuristics, not universal violations. Project conventions override generic preferences; avoid repeating issues already enforced by tooling.

Report both dimensions separately, with severity, evidence, and practical implications; one passing does not establish the other. Never manufacture findings. Independent reviewers are optional under configured/authorized dispatch, not mandatory.

## Native gate

In Trellis, use native `trellis-check` in read-only or authorized-fix mode as appropriate; when this analysis is requested from an ongoing native check, perform it there instead of launching another review. Share the same scope/check evidence. Run only selected checks whose evidence is needed and record unrun coverage honestly. Fix task-caused issues only when implementation/fixes are authorized; review alone means report findings.

No automatic task-state changes, commit, push, PR posting, or external review comments.

Source: [skills/engineering/code-review/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/code-review/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
