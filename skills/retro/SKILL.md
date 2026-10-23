---
name: retro
description: "Retrospect on completed work or a resolved debugging cycle using recorded outcomes, causes and prevention lessons. Use for a retrospective or post-mortem; active diagnosis, code review and continuation handoff retain their own owners."
---

# Retro

Turn a completed task, delivery or debugging cycle into evidence-backed lessons. Resolve the period and task from the user's request and current records; ask only if the intended scope cannot be established. A retrospective may examine unfinished outcomes, but does not declare them completed.

## Read the evidence

Use the relevant request, PRD/design, execution and verification records, diffs/commits, and failure evidence. Reuse context already available. Distinguish the intended result, observed result, known cause, hypothesis and unknown. Passing file checks does not establish application behavior; a proposed prevention is not an implemented fix.

In Trellis, the existing task and its status remain authoritative. Reuse an earlier retrospective for the same work and add only new evidence. If native `trellis-break-loop` routed here, perform one analysis here; do not send it back to that entrypoint. Without Trellis, use the project's existing records or the user's supplied context.

## Explain what changed the outcome

- Compare the intended outcome with actual behavior and acceptance evidence. Identify useful practices as well as failures.
- Trace significant delays, mistakes or repeated fixes to supported causes. For bugs, distinguish missing specification, contract mismatch, incomplete change propagation, coverage gap and unsupported assumption when those categories fit the evidence.
- Explain why earlier attempts failed, where the successful approach differed and which uncertainty remains. Do not invent a debugging history or assign blame from missing evidence.
- Propose the smallest prevention that addresses each established cause. Identify its owner/location and how future work could verify it. Broader architectural changes and new tasks remain recommendations until authorized.

## Capture once and stop

Return the outcome, evidence-backed lessons and prioritized follow-ups. A concise table can map each lesson to its evidence, prevention and current status; omit empty categories.

If the user requested documentation or the current authorized task requires a retrospective record, update its existing verification/continuation record or Journal. Promote only durable, confirmed lessons into existing project specs under the applicable write authorization. Otherwise report in chat. Link canonical evidence instead of copying whole PRDs, logs or private data.

This analysis does not rerun tests or installations, fix code, create tasks or trackers, change task status, archive work, commit, push or publish. Active failures return to the existing diagnostic owner; diff acceptance belongs to code review, and next-session state transfer belongs to handoff. Finish when every material lesson has evidence or an explicit uncertainty and each follow-up is distinguished from completed work.
