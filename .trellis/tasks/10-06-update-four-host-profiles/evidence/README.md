# Durable installation evidence

## Evidence classes

| Artifact | What it proves | Boundary |
| --- | --- | --- |
| `installation-2026-10-06.redacted.log` | Actual captured PTY output, selections, backups, keep decisions and completion | Recovered from 20 retained tool outputs; not a reenactment; URLs replaced with SHA-256 values |
| `historical-verification-2026-10-06.json` | The original executed checker reported success/counts | Does not restore its lost before/after fingerprint inputs |
| `provenance.json` | Source session, stable record lines, output hashes and private-copy location | Whole session hash is its recovery-time snapshot; future appended turns do not invalidate record-line hashes |
| `backup-inventory.json` | All 86 original backup paths remain available, with observed file/tree fingerprints | Fingerprints were observed on 2026-10-10, not captured in the original run |
| `mcp-backup-comparison-2026-10-10.json` | Original merge-before backups compared with today's MCP files/definitions/URLs | SHA-256 only; no raw headers, tokens or configuration values; not an October 6 post-state snapshot |
| `installed-file-observation-2026-10-10.json` | Today's Skill/default/document fingerprints compared with pinned source `029d9a4` | Current observation, not evidence that today's drift happened during installation |
| `recovery-summary.json` | Recovery and fresh-observation counts with historical limitations | Historical protection baseline is explicitly unrecoverable |

## Reproducibility and privacy

For each terminal chunk, `provenance.json` identifies its original JSONL line,
call/chunk identity, exact line hash and output hash. The historical checker JSON
is traceable to its own original output. The sanitized transcript retains actual
decisions and all backup paths; it does not copy unrelated conversation history.

Backup inventories include content hashes and relative tree entries. MCP
comparisons include canonical definition hashes and URL hashes, so sensitive
values do not enter the repository. The private raw MCP copies have file mode
0600 under directories with mode 0700, outside the repository and host runtime
configuration roots. Copies are labeled `backup-derived-before` or
`observed-2026-10-10`; neither is described as a recovered October 6 post-state.

Current MCP observations retain all 11 URL values. Codex `node_repl` has a
different definition; current Skill payloads also differ from some pinned-source
trees. These later differences are documented, not repaired by this evidence task.

## Historical limitation

The original temporary `before.json`, protected-state baseline, original dirty
diff and full October 6 post-state fingerprint inventory are unavailable. Their
checks were reported as passing in the recovered execution result, but cannot be
independently repeated now. Keep the corresponding original acceptance item open
until adequate original evidence exists; do not treat a new snapshot or modifying
reinstallation as a reconstruction of the old one.
