---
name: prototype
description: "Build a disposable demo to settle one authorized UI or state-design question. Does not implement a production feature."
license: MIT
---

# Prototype

Adapted from Matt Pocock's AIHero skills. A prototype answers one question; it is not an authorization to ship production behavior.

State the question, authorized scope, audience, and what observation would settle it. Use existing project patterns. For logic/state questions, expose transitions and edge cases with visible state (often a standalone HTML demo). For visual questions, provide a few meaningfully different UI shapes with an easy switch. Resolve genuine branch ambiguity from context or user intent before building.

Keep the demo clearly named as a prototype and easy to run. Use memory/scratch data by default; do not touch production data or broaden dependencies for polish. In Trellis, place disposable evidence/assets under the current task's `research/` unless an existing project route is necessary; document the run command and boundaries. Without Trellis follow existing prototype locations.

Use validation proportional to the experiment. Follow the project's test policy: where skipping test-first work requires approval, obtain it; do not declare a blanket test exemption. At minimum verify the demo runs and shows the question's relevant states.

Record the observed verdict, remaining uncertainty, and the artifact/run pointer in current research/design. A promising demo does not automatically become production code. Return accepted changes to ordinary implementation/TDD/native checks. Do not automatically delete files, create branches, commit, push, or publish; cleanup must preserve unrelated work and follow authorization.

Source: [skills/engineering/prototype/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/prototype/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
