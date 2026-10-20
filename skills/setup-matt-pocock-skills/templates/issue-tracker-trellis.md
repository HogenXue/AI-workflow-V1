# Issue tracker: Trellis

Trellis is the sole task and specification tracker for this repository. Read
`.trellis/workflow.md` and applicable project instructions before using engineering Skills.
Resolve the current task through the repository's Trellis CLI; if no task is active,
follow its existing task-creation and planning rules.

## Engineering Skill operations

| Requested operation | Trellis destination |
| --- | --- |
| Read the issue/spec | Current task's `prd.md`, then `design.md` / `implement.md` when present |
| Publish or update a spec (`to-spec`) | Update the current PRD with confirmed requirements and acceptance; design and execution details go in the task's existing design/plan |
| Split work into tickets (`to-tickets`) | Use the task's implementation plan; independently verifiable deliverables may use native parent/child tasks under project rules |
| Read a work map (`wayfinder`) | Use the current task's planning artifacts and existing research; record dependencies in the native plan |
| Claim, resolve, close or triage work | Use native Trellis lifecycle commands and supported statuses; preserve planning, readiness, quality and completion gates |
| Implement (`implement-spec`) | Hand off to Trellis execution with the adapted `tdd`; finish with native `trellis-check` |

Requirements and acceptance have one source: the current PRD. These operations do not
publish another spec to GitHub/GitLab Issues or `.scratch/`. Matt Skills supply techniques
within a Trellis stage; they do not take over scheduling, branch/worktree orchestration,
merges, PR creation, or commits. Existing user authorization and project Git rules apply.

Keep task-scoped research, hypotheses, design decisions and execution evidence in their
native Trellis artifacts. Only stable domain terms and durable decisions belong in the
domain documentation described by `docs/agents/domain.md`.

Triage labels are not Trellis task statuses. Preserve native states and gates; a request
that needs an unsupported mapping must be clarified rather than creating a second tracker.
