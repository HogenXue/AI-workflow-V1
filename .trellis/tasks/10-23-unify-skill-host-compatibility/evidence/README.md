# Verification evidence

The installed package came from the uncommitted working tree based on
`a45d78432529414a193f20e722d1b9dde728e52c`. That commit alone does not identify
the installed payload. `source-package.json` records every installable source
file hash and the hash of the privately retained source archive.
`final-source-package.json` records the later repository-only preflight fix;
all host-distributed files remained identical and passed the final strict audit.

- `before-fingerprints.json`: replacement targets, protected paths, existing
  dirty work and MCP definition/URL hashes before installation.
- `installed-fingerprints.json`: source/installed trees, guides, configuration
  payloads, MCP preservation and protected after-state.
- `backup-inventory.json`: each new timestamped backup and matching before-state.
- `installation.redacted.log` and `provenance.json`: actual interactive installer
  transcript, selections, exit status, source identity and log hashes. URL values
  are replaced by hashes; original settings and transcript are private.
- `native-codex-discovery.json`: manifest Skills returned once each and enabled
  by Codex 0.154.0 `skills/list`; the independent malformed Skill is identified
  separately. This does not prove desktop menu refresh or model invocation.
- `native-hook-checks.json`: installed Bash/Python helpers emitted current Task
  context from root/nested directories; foreign hook configuration was preserved.
  Native hook trust/event activation remains untested.
- `managed-skills-before.json` / `managed-skills-after.json`: the four selected
  host discovery sets went from 15 managed conflicts to zero; the final audit
  also requires current content and all 19 capabilities.
- `research/`: official host contracts and the packaged capability audit.
- `validation/`: actual fixture results, routing analysis and reproducible probe
  drivers. The original PowerShell run contains one failure; the corrected
  single-test result supersedes only that failure, not the other results.

Private root:
`/Users/hogenxue/.local/state/codextamplate/installation-audits/2026-10-23-shyz1wxr`
(directory 0700, private files 0600). It retains original MCP files, full before
state, the raw transcript, audit/PTY scripts and the source archive. Timestamped
installer backups remain in their native host backup directories; the public
inventory verifies their exact contents. Temporary research/runtime directories
are not required to interpret the retained results.

The separate pre-development baseline is retained at
`/Users/hogenxue/.local/state/codextamplate/project-audits/2026-10-23-p563orl6`.
It distinguishes unrelated archive/task/root-AGENTS changes from this task.

Rollback, if requested, must use the exact target-to-backup mapping and verify
current contents before restoration. Do not restore an entire host tree or
discard unrelated subsequent changes.

Before Git publication, trailing whitespace was removed from
`validation/identity-red.log`; test outcomes and traceback text are unchanged.
The byte-exact original is retained privately as `identity-red.raw.log`
(SHA-256 `83331aec1d0d1482fcfaa48858b4de7cbb189252a83ef239bf54653a3afb05fd`).
