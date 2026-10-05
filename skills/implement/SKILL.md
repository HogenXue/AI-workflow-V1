---
name: implement
description: "Implement an authorized, reviewed spec or slice through native execution. Use after planning gates, not review-only or exploratory requests."
license: MIT
---

# Implement

Adapted from Matt Pocock's AIHero skills. Implement the user's accepted work; do not start a second workflow or commit automatically.

## Ready to execute

In Trellis, resolve the matching task, read `prd.md`, `design.md`/`implement.md` when present, and applicable specs/research. Confirm authorization and blockers, satisfy the native planning gate, and use `task.py start` before production edits. Consultation or spec creation alone is not implementation approval. Follow configured inline/subagent execution; do not force unavailable platform tools or spawn a second implement agent from an implement role. Load native before-development guidance or read its equivalent specs.

Outside Trellis use established requirements and workflow; do not initialize new task machinery.

## Build and verify

- Implement one smallest verifiable behavior/slice at a time; preserve unrelated dirty work.
- Use the local `tdd` skill for behavior changes that need automated evidence: verified RED, minimal GREEN, and relevant REFACTOR checks. Documentation/config work uses proportional validation rather than fabricated RED.
- Run required impact analysis before cross-module/high-risk contracts. If evidence is unavailable, report the limitation and resolve the project gate before editing.
- Run focused tests/type checks during meaningful batches and selected final checks after the implementation stabilizes. Do not run all suites after every edit or relax tests to mask failures.
- If source evidence exposes a requirement/design gap, return to native planning rather than silently expanding scope.
- At completion use one native `trellis-check`; `code-review` supplies Spec/Standards analysis within that gate. If native helpers are unavailable, perform and record their equivalent review/check steps without claiming they ran.

Report changed behavior, real verification, and limits in current task records. Checks passing do not authorize commit, push, PR creation, task completion, or archival; follow explicit Git/native finish authorization.

Source: [skills/engineering/implement/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/implement/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
