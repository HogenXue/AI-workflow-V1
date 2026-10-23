# Design

## Boundary

Trellis remains the sole task/artifact/check owner. Package Skills offer bounded
capabilities; existing user authorization is reused without creating parallel
interviews, implementations, checks or Git lifecycles. Main-session integration
owns source writes and final verification; independent audits/candidate patches
are scoped to this Task and never own task state or live installation.

## Changes

1. Align native Cursor/Claude review, brainstorm, continue, retrospective,
   finish-work and GitNexus guidance with the packaged authorization policy.
   Add one portable `retro` capability and route native retrospective to it
   when available; retain a bounded native fallback for standalone projects.
2. Introduce a strict common Skill catalog reader and read-only discovery audit.
   Validate names, directory/frontmatter identity, duplicate manifest entries,
   invocation metadata and host discovery roots. Same-name different-content
   variants and aliases within a selected root are actionable conflicts;
   same-source cross-host copies are reported separately. Preserve unrelated
   useful Skills. Explicit migration backs up only exact selected owned names.
3. Harden MCP parsing/merging to preserve legitimate TOML forms and WorkBuddy
   JSONC. Parse before/after, preserve keep bytes, reject unsupported destructive
   rewrites before mutation. A shared merge implementation serves Bash/PowerShell.
4. Merge managed hook entries/files precisely for Codex/Cursor without deleting
   third-party data; share the Codex Python runtime across Unix/Windows. Preview
   writes nothing. Respect existing hooks=false and report active instruction
   overrides instead of overwriting them.
5. Document native discovery/capability/trust boundaries; add missing Windows CI
   coverage. New/changed hooks may require native /hooks review; file/smoke
   verification does not claim application trust/activation.

## Installation

Use approved four-host update only after gates pass, with fresh durable private
before-state, sanitized transcripts, file fingerprints and backup inventory.
Preflight managed identity conflicts across actual discovery roots. Back up and
remove obsolete variants only within explicit package-owned scope. Preserve all
MCP URLs, unrelated keys, native settings, Graphify, independent/plugin Skills,
existing overrides and repository dirty work. Existing independent host copies
remain valid only when their managed payloads agree; do not delete unselected
host capabilities merely to reduce counts.

## Verification and rollback

Use isolated temporary homes for behavior/regressions, clearing inherited native
host overrides. Full Python unittest suite and package validation are appropriate
because changes span shared installation/MCP/Skill contracts; unavailable pwsh or
Windows runtime is not_run. Add meaningful error/keep/rollback and discovery
cases before fixes. Run independent realistic Skill-routing checks and compare
remaining local data to the saved baseline. Installer backups preserve originals;
source changes remain uncommitted. No app restart/trust bypass or Git publication.
