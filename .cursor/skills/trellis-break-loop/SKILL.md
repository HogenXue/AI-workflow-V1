---
name: trellis-break-loop
description: "Retrospect on a resolved or repeated debugging cycle, using evidence to explain root causes, failed attempts and prevention. Reuses the retro capability when available; active debugging belongs to the diagnostic workflow."
---

# Break the Loop

This is the native Trellis entrypoint for a debugging retrospective. Resolve the current or user-selected task and use its existing reproduction, repair and verification evidence.

## One retrospective owner

If the `retro` capability is available, use it for this same analysis and pass the task scope and existing evidence. Reuse an earlier retrospective rather than starting a second interview or analysis. The native workflow continues to own task state and final acceptance.

## Bounded fallback

When `retro` is unavailable, perform the analysis here:

1. Compare the reported symptom, attempted fixes and verified outcome. Separate facts, causes, hypotheses and missing evidence.
2. Explain why repeated attempts failed and what changed in the successful approach. Consider missing specs, cross-layer contracts, incomplete propagation, test coverage and implicit assumptions where supported.
3. Recommend the smallest useful prevention and how to verify it. Distinguish proposals from changes already implemented. Record wider issues as recommendations within the current task.
4. Return a concise retrospective. When documentation is authorized, update the current task's existing verification record or Journal, and promote durable confirmed lessons to the project's existing spec location. Otherwise report in chat.

The fallback follows the same boundary as `retro`: it does not rerun successful work, implement new fixes, create tasks/trackers, alter task state, archive, commit, push or publish. Preserve private evidence and unrelated files. Spec destinations belong to the actual project; no upstream template tree is assumed.
