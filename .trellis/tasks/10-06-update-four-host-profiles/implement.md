# Review remediation plan — 2026-10-10

1. Recover the original PTY output and executed verification result from the
   retained session log. Inventory the 86 persistent installer backups.
2. Persist a sanitized transcript, provenance and SHA-256 manifests in `evidence/`.
   Copy native MCP before-state backups and a fresh read-only observation into
   a private directory outside the repository; distinguish their timestamps.
3. Revise verification/Task/Journal records so missing historical fingerprints
   are not presented as independently reproducible acceptance evidence.
4. Align `.trellis/spec/scripts/installer-contracts.md` and `index.md` with the
   existing RFC1918/ULA literal-IP allowance and public/special-use rejection.
5. Perform one native Trellis check with evidence schema/provenance/digest checks,
   privacy checks, file formatting and Task context validation. Reuse the review's
   successful four tests, 12 address-boundary probes and five-host URL checks,
   because runtime implementation/tests and their dependencies are unchanged.

No fabricated TDD cycle or package-wide tests for this documentation/evidence change.
No installation, host-setting edits, commit, push or automatic archival.
