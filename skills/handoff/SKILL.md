---
name: handoff
description: "Record continuation context and canonical artifact pointers for the next session. Does not resume work, change status, or grant Git authorization."
license: MIT
---

# Handoff

Adapted from Matt Pocock's AIHero skills. Read actual task/artifact/Git state before summarizing; do not infer completion from conversation alone.

In Trellis use the current task's existing continuation/verification record or Journal; a task-local `handoff.md` is acceptable when no record fits. Reference the PRD, design, plan, research, and relevant decisions rather than restating them. Keep native task status authoritative. Outside Trellis use the user's destination or existing handoff convention; otherwise an OS temporary note is appropriate.

Include:

- The user's current objective and constraints, including changed scope and accepted decisions.
- Exact artifact paths and the active task/status; distinguish completed, verified, unverified, and pending work.
- Next action and genuine blockers, with the evidence or user choice that clears each.
- Actual checks, covered files/behavior, results, and when evidence must be rerun.
- Unrelated dirty changes to preserve, authorization limits, and relevant available skills for continuation.

Redact credentials and sensitive material. Do not start another session, send messages to another agent/chat, modify task state, commit, push, or rerun successful checks just because a handoff was written. Native continue reads canonical artifacts and reuses still-valid evidence.

Source: [skills/productivity/handoff/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/productivity/handoff/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
