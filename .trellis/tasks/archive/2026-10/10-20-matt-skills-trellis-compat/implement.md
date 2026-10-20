# Implementation plan

1. Run readiness, start this task, and use the package's TDD instructions for installer behavior.
2. Add regression tests for exact-name lock adoption and failure recovery; observe RED.
3. Implement opt-in lock adoption with preflight, backup, atomic write and rollback; verify GREEN.
4. Add the adapted setup Skill, host-aware instructions and Trellis templates; update manifest,
   package expectations and installation guidance.
5. Review temporary project scenarios (Trellis, CLAUDE-only, non-Trellis, repeated setup),
   run targeted tests and native `trellis-check`, then address any findings.
6. Install the verified package into `~/.agents/skills` with replacement and explicit adoption;
   verify adapted contents, backup availability and preservation of unrelated Matt entries.
7. Record acceptance and implementation evidence; run shared quality once after final content
   changes. Leave changes uncommitted for the user.

Rollback uses the installer-produced timestamped backups. Other project repositories and
global Codex config/hooks are outside this task's mutation scope.
