# Unify Skill routing and native host compatibility

## Goal

Make the package's workflow capabilities coherent and compatible with Codex,
Cursor, Claude Code, MiniMax Code and WorkBuddy. The user explicitly requested
project-wide optimization, no conflicting Skills, and confirmed updating the
four previously selected local profiles after validation.

## Requirements

- Audit all packaged Skills, invocation metadata, global/project templates,
  native Trellis entrypoints, validators and Bash/PowerShell installer profiles.
- Each intent has a clear workflow owner; complementary Skills share native
  artifacts and existing authorization rather than launching duplicate workflows.
- Preserve explicit/stateless Grill behavior, existing MCP addresses and unrelated
  host settings/capabilities. Preserve independent useful Skills and plugins.
- Detect same-name/alias collisions and drift in installed managed Skills;
  migration/removal must identify exact owned scope and retain recoverable backups.
- Provide useful native entrypoints, including the previously requested retro
  capability, through supported discovery/metadata with clear responsibility.
- Verify supported host paths, MCP merge behavior, hook execution and failure
  behavior with isolated fixtures and available native runtimes.
- Update Codex, Cursor, MiniMax Code and WorkBuddy on this Mac only after the
  package checks pass; protect all pre-existing repository work and private data.

## Acceptance

- [x] Evidence-backed audit covers every packaged Skill and all five profiles.
- [x] Documented routing and capability checks reject structural conflicts and
  preserve primary owners, invocation policy and real execution authority.
- [x] Compatibility fixes and regressions pass in isolated host fixtures;
  actual unavailable runtimes/app acceptance are explicitly marked not_run.
- [x] Existing and new Skill entrypoints are discoverable and non-duplicating.
- [x] Four approved local profiles are updated with durable sanitized evidence,
  existing MCP/native settings and independent capabilities preserved.
- [x] Final native quality check, preservation checks and continuation records
  reflect actual outcomes; no unsupported universal compatibility claim.

No commit/push, application restart, plugin uninstall, unrelated Skill deletion
or automatic Task archive is authorized by this optimization request.
