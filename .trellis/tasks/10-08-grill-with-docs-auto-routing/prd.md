# Clarify automatic Grill with Docs routing in Trellis

## Goal

Automatically select `grill-with-docs` when evidence leaves a user decision affecting scope, key design choices, or acceptance criteria, while preserving Trellis ownership and avoiding repeated interviews.

## Requirements

- Inspect existing task artifacts, relevant specifications, and repository facts before asking questions; reuse confirmed decisions.
- Select `grill-with-docs` without requiring the user to name it when a material user decision remains unresolved. Clear requests, routine implementation choices, and complexity alone do not trigger an interview.
- Keep documented discovery within the current Trellis task and existing PRD/design/plan. Select one interview owner; use native brainstorm as an equivalent fallback when the skill is unavailable.
- Return implementation-discovered requirement gaps to native planning. Continue independent authorized work while awaiting needed decisions; implementation still follows the native gate.
- Preserve explicit, stateless `grill-me`, existing invocation policy, and all Git/host-install authorization boundaries.
- Update only package guidance, the skill source, and this repository's native workflow/decision records. No installer/runtime changes, new dependency, live global install, or archival. Commit and push require separate explicit authorization, received on 2026-10-08.

## Acceptance Criteria

- [x] The skill description and body identify automatic positive triggers and skip conditions.
- [x] Global/repository guidance and both native planning breadcrumb variants consistently reach the same documented-discovery route.
- [x] Existing conclusions and a previously selected interview owner prevent duplicate interviewing; only newly unresolved choices are reopened.
- [x] Confirmed results return to canonical artifacts and native planning gates without a new lifecycle or implicit implementation authorization.
- [x] Focused routing tests, skill structure validation, task context validation, and diff checks pass; actual verification limits are recorded.

## Notes

- Authorized by the user's 2026-10-08 implementation request after clarification that the target is `grill-with-docs`.
- Lightweight documentation task; no additional design/implementation plan or interview is required. Initial working tree was clean.
- Applicable guidance: `.trellis/spec/guides/index.md`, `.trellis/spec/decisions/aihero-native-trellis.md`, and `.trellis/spec/decisions/codex-instruction-skill-boundaries.md`.
- This local documentation edit changes no code symbol, public/data contract, or runtime call chain; graph impact analysis is not needed.
- Validation and the single native Spec/Standards check will be recorded in `verification.md`. No live model invocation or installation is claimed.
