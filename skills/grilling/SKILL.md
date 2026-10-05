---
name: grilling
description: "Support an ongoing Grill or planning interview with prerequisite-ready questions. Does not start a second interview or write task artifacts."
license: MIT
---

# Grilling

Adapted from Matt Pocock's AIHero skills. This capability produces shared understanding, not task state or permission to implement.

Read available code, tests, specs, and prior decisions to answer factual questions yourself. Do not ask users for discoverable facts. Use source inspection inline; delegate only when the host/project/user actually authorizes it.

Map decisions as a tree. The frontier contains only choices whose prerequisites are settled. In each manageable round, number the independent questions, give a recommendation and trade-off, and wait for the user's answers. Follow a request for one question at a time. Recompute dependencies after each answer; never assume the user's choice or ask a downstream question while its prerequisite is unresolved.

Stop a branch when external evidence or a bounded prototype is needed; state the question and evidence that would settle it. Continue independent questions. Do not replace an empirical question with endless interviews.

Reuse accepted answers. Finish with confirmed choices, acceptance criteria, and remaining blockers; seek confirmation only where shared understanding is still uncertain. This support skill does not write documents, create/start tasks, or implement. The enclosing `grill-with-docs`/Trellis planning role owns persistence; `grill-me` remains stateless. No automatic Git operations.

Source: [skills/productivity/grilling/SKILL.md](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/productivity/grilling/SKILL.md). Pinned adaptation: `24fe0ef7737efae15c87225755e9f6f5965e4888`. See [MIT license](LICENSE).
