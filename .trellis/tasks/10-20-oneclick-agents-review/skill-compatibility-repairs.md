# Local Skill compatibility repairs

User-authorized scope: repair the six instruction conflicts from the latest audit and
sync installed packaged Skills. Previous review fixes and the untracked Cursor rule
were preserved. No commit, release, tag, graph rebuild or hook installation was executed.

## Results

- `implement` and `implement-spec` now use native Trellis execution/review and require
  matching user authorization before Git orchestration or commits.
- `release-skills` no longer triggers releases for ordinary push or release-note-only
  requests. Its Trellis route uses `release`; per-module commits are proposals until
  authorized, including the former unconditional final "just push" instruction.
- `grill-me` and `grilling` route Trellis interviews to the sole one-question-at-a-time
  `grill-with-docs` interviewer; standalone interview behavior is retained.
- `domain-modeling` uses Trellis domain/decision paths before applying glossary formats.
- Packaged and installed Memory entry/reference now require explicit save consent.
- Shared Graphify selects actual host tools and supports parent persistence of worker
  JSON; no mandatory Claude-only tool, Codex-specific invented arguments or measured
  token counts are assumed. The old Codex duplicate was archived recoverably.
- The package installer backed up and refreshed the ten manifest Skills, including
  the previously repaired setup override handling. No update-lock adoption was requested.

## Backups and validation

Third-party original Skill directories and the removed Codex Graphify are preserved in
`/Users/hogen/.agents/.ai-workflow-backups/skills-compat.3mCSdEjE/`.
The installer also made individual manifest Skill backups with timestamp
`20261030T032854Z` or `20261030T032855Z`.

Package validation passed for all ten Skills. The bundled skill-creator quick validator
rejects the pre-existing third-party `disable-model-invocation` frontmatter extension;
the existing invocation settings were preserved and YAML/name/description were validated
separately. These are instruction changes, so no wording-only synthetic tests were added.
Native review checked routes for plain push, implementation without Git consent, Trellis
interview, domain modeling, decisions without save consent, and Codex graph extraction.
Full repository quality and fingerprint results are authoritative in verification.json.

Third-party adaptations are installed local changes, not newly distributed manifest
Skills. A future upstream reinstall may replace them; retain this backup/repair record.
