# Fix main CI runtime isolation and Bash text portability

## Goal

Fix the failures at main `4f3753f` without changing installer ownership or weakening preservation checks.

## Requirements

- Normalize Python text consumed by Bash for catalog names, default mode, and Skill lock resolution/adoption while preserving failed command exit codes and stderr.
- Isolate PowerShell runtime state from the empty HOME used to test installer previews. Keep the exact empty-HOME assertions.
- Add regression coverage for CRLF text, failed helpers, and inherited runtime environment variables.
- Repair subsequent confirmed CI portability/concurrency failures while retaining backup safety assertions and actual installer execution.
- Use an isolated branch and temporary installation fixtures. Preserve user work; do not merge, deploy, or install into real host profiles.

## Acceptance Criteria

- [x] CRLF catalog output supports preview and copying the full package.
- [x] CRLF lock paths support adoption without losing unrelated lock metadata.
- [x] Failed Python catalog commands retain their exit status and do not create targets.
- [x] PowerShell startup state is isolated and the existing strict no-write previews pass.
- [x] The exact pushed repair commit passes Ubuntu, macOS, and Windows CI; all actual results and skips are recorded.
- [x] The observed Ubuntu parallel-backup failure is diagnosed and fixed; Windows preservation/catalog tests use the actual PATH-resolved Bash and isolate native runtime state.

## Notes

- User authorized repair, regression checks, commits and pushing this isolated branch for CI. No additional implementation approval is pending.
