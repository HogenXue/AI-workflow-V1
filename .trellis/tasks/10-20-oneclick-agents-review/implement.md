# Implementation plan

1. Pin the confirmed baseline and run independent Standards/Spec reviews; record concrete
   findings and the three-template audit without merging the two axes.
2. Complete readiness and activate this task; use TDD for installer behavior.
3. Add failing tests for global lock resolution (Codex, Cursor, XDG, custom fallback) and
   real-TTY full-profile adoption/decline. Observe RED before implementing production code.
4. Add a shared lock resolver, wire explicit adoption prompts into both existing profiles,
   and verify GREEN plus component rollback/metadata tests.
5. Narrow the global template's Trellis-only routes; keep other templates unchanged unless
   review produces a verified issue. Update relevant installer contracts and README.
6. Run targeted suites and native `trellis-check`; finalize evidence/acceptance records,
   then run shared quality once for final contents and completion verification.

Rollback is the ordinary unstaged source diff plus existing installer backups. Tests use
temporary HOME/PTY fixtures and never mutate real host configuration or target projects.
