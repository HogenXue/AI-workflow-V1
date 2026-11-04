# Merge hardening branch and optimize the combined design

## Goal and authorization

On 2026-11-04 the user requested latest code, design review and optimization,
then explicitly selected merging origin/codex/ai-workflow-hardening into main.
Main starts at 43ca2442e3c98f464f22bd806d1a3047f27f3517; the incoming tip is
7d685b9 (resolve and record its full SHA before merge). The branches have 27/7
exclusive commits. This task supersedes neither prior task acceptance nor local work.

## Requirements

- Merge the named remote branch into local main and resolve both sides' intent.
- Retain main's five host profiles, 19 existing capabilities including retro,
  strict identity preflight, MCP/native hook preservation and current template paths.
- Integrate the branch's explicit third-party lock ownership adoption and routing
  improvements without resurrecting obsolete setup workflows or root template paths.
- Review combined design against native Trellis ownership, Bash/PowerShell parity,
  opt-in writes, recoverable backup/rollback, native configuration and CI evidence.
- Fix reproducible task-owned issues, using meaningful isolated regression tests.
- Preserve all 67 pre-existing dirty paths, staged state, independent work and actual
  global settings. No live host install, graph rebuild, unrelated cleanup or push.
- Complete the authorized local merge commit only after selected checks pass.

## Acceptance

- [x] Named incoming tip is the prepared second merge parent; both intents retained, with final ancestry verified from the completed commit graph.
- [x] Spec/Standards findings and design decisions are recorded and resolved within scope.
- [x] New behavior/failure cases and shell peers have appropriate fixture evidence.
- [x] Native quality gate, package/Task/whitespace checks and preservation checks pass.
- [x] No unresolved merge, accidental staged work or unrelated content loss remains.
- [x] Local merge result and runtime/platform limitations are reported accurately.
