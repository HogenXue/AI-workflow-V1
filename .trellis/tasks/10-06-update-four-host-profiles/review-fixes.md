# Review fixes — 2026-10-10

## Spec: preserve reviewable installation evidence

Recovered the actual October 6 PTY transcript (20 tool-output chunks, final exit
code 0) and original executed verification JSON from this session's retained
JSONL records. Persisted sanitized output and source line/output hashes in
`evidence/`. All 86 paths identified by the original transcript still exist;
their observed fingerprints are now a durable backup inventory.

Copied original MCP merge-before backups and separately labeled current files to
a restricted persistent private directory. Public evidence contains only file,
definition and URL hashes; no raw configuration/authentication values were copied
to the repository. Current checks retain all 11 original URLs, with later changes
in one server definition and some Skill trees explicitly reported as observations.

The October 6 protected-state baseline and immediate post-state inventory are
irrecoverable from the surviving records. Their original reported pass remains
historical evidence, not a fabricated independent reproduction. The corresponding
original PRD acceptance item remains open. No installation or host configuration
change was performed to manufacture new before/after evidence.

## Standards: align the private HTTP exception

Updated `installer-contracts.md` and the scripts quality checklist to match the
existing validator: exact loopback hosts, RFC1918 IPv4 CIDRs and IPv6 ULA
`fc00::/7`. Explicitly reject non-loopback DNS, public IPs, documentation ranges,
link-local and shared-address space. All five formats and both shell ports share
this Python validator. Runtime implementation and tests were not changed.

## Verification selected for this batch

- Verify original transcript source lines/output hashes, final exit code and
  sanitized reconstruction against the retained source records.
- Verify all 86 backup fingerprints, eight private-copy fingerprints and their
  0700-directory/0600-file permissions; parse JSON and inspect privacy boundaries.
- Compare documented CIDRs with the unchanged implementation and review the
  corrected historical/current evidence classifications.
- Run native Task context validation and `git diff --check`; apply the single
  native Trellis Spec/Standards check to the final batch.
- Reuse the read-only review's four tests, 12 boundary probes and persisted
  private-IPv6 URL checks across five host formats. Their covered runtime content
  and dependencies are unchanged, so no repeated/full repository suite is needed.

No PowerShell runtime, application loading or external business MCP acceptance is
claimed. No commit, push, archive or unrelated dirty-work modification is included.

## Final native Trellis result

The selected artifact checks passed: 20 original output-record hashes and the
original result matched their source lines; 86 backup fingerprints and eight
private-copy hashes/permissions matched; JSON/privacy and CIDR consistency checks
passed. `task.py validate` and `git diff --check` passed. Results are persisted in
`evidence/remediation-checks.json`.

Spec review confirms durable recovered evidence with accurate limitations; the
original protected-state acceptance remains open. Standards review confirms the
formal HTTP policy now matches the unchanged validator. The first artifact check
used a canonical filename for a private before-copy whose name still carried its
backup timestamp; only that private audit-copy filename was normalized, then the
same failed check was rerun successfully. No runtime code/test or native config
was edited during this fix.
