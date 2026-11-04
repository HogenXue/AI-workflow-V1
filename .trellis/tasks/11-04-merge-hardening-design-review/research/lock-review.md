# Incoming lock-adoption design review

Task: `.trellis/tasks/11-04-merge-hardening-design-review`
Date: 2026-11-04 (Asia/Shanghai)
Pinned main: `43ca2442e3c98f464f22bd806d1a3047f27f3517`
Pinned incoming: `7d685b9c740df2361f8c71f2a65df84a02179884`

Read-only review of Git objects and the current task PRD/design/check references. Reproductions used an extracted incoming package and temporary fixture files under this directory. No index, repository, real HOME, global host config, live installation, Git mutation or full suite was touched.

## Spec findings

### P2 — duplicate JSON keys silently discard independent lock entries

Incoming `scripts/lib/adopt_skill_lock.py:25` uses ordinary `json.loads`, which accepts duplicate object keys by selecting the last one. Given two `skills` mappings, one containing an independent registered capability and the later one containing `tdd`, `--apply --skills tdd` returns 0 and rewrites the lock without the earlier independent capability. Preview accepts the same ambiguous file, so a full install can mutate payloads before detecting nothing wrong.

Reproduced: exit 0; `independent-first` lost; `independent-last` retained. See `probe-results.json`.

This contradicts the incoming ownership spec's preservation of unrelated names/all JSON metadata and this task's exact ownership/preservation requirement. Reject duplicate keys before backup or Skill mutation, including nested keys, using strict JSON object-pair validation. Main's MCP JSON parser already applies this safeguard. Keep exact bytes on no-op/decline, and add malformed/duplicate-lock cases proving no backup or payload write occurs.

### P2 — a custom symlink target can select the wrong ownership lock

Incoming `scripts/install-lib.sh:137-147` classifies targets by resolved physical path before its caller-adjacent custom-target fallback. A caller target `custom/skills` symlinked to the standard `.agents/skills` directory resolves to the global `.agents/.skill-lock.json`; the custom caller-adjacent lock is ignored. This differs from incoming `10-20-oneclick-agents-review/design.md` and the appended installer spec, both of which promise caller-visible adjacent lock ownership for custom symlink targets.

Reproduced with two temporary roots: resolver returned the standard global lock instead of `custom/.skill-lock.json`. See `probe-results.json`.

Prefer lexical normalized standard-root matching (support `.` spellings without following a custom alias into a different ownership scope), then preserve the caller-adjacent custom parent. Alternatively introduce an explicit documented lock selection, but do not silently reinterpret this custom target's ownership. Cover a custom symlink specifically pointing into a standard root; the existing branch test only points into another custom directory and misses this case.

## Standards finding

### P2 — lock adoption has no PowerShell peer and its helper breaks supported Windows Python

Incoming adds `--adopt-skill-lock`, the resolver, backup/rollback state and wizard consent only to Bash. Existing main `install-skills.ps1` has no such flag, and the PS wizard/lib contain no counterpart. Main's installer contract lines 23-26 requires peer CLI/behavior parity or an explicit exemption; the current task explicitly asks to integrate this behavior across shell peers.

The shared helper additionally calls `os.fchmod` at line 38. Windows support was added only in Python 3.13; the repository supports Python >=3.10 and its Windows CI uses 3.12. Merely adding a PS wrapper around this helper would therefore still fail on supported Windows Python 3.10-3.12. Official source: https://docs.python.org/3/library/os.html#os.fchmod . This is version-specific, not a claim that current Windows Python always lacks fchmod.

A bounded capability simulation removing `os.fchmod` raised `AttributeError` before publication and retained the original lock, confirming the failure path. No Windows runtime acceptance is claimed.

Use a shared cross-platform resolver/strict JSON helper for both peers, retain independent default-no adoption consent, and copy permissions using a portable path operation as main's atomic writer does. Add Windows-3.12 fixture coverage, PS opt-in/decline/no-op/rollback cases, and verify CLI exit propagation.

## Integration obligations, not separate inherited bugs

- Preserve main's strict `skill_catalog.py` preflight before any new lock backup or payload mutation. Incoming ownership tests seed `SKILL.md` with plain `upstream tdd` or only a sentinel; update these fixtures to valid matching name/description instead of weakening the strict guard. Otherwise a rollback test may fail at identity validation and falsely appear to exercise rollback.
- Preserve the 19-capability main manifest (including retro), five host profiles and current template locations. Derive adoption names from the authoritative current catalog, not the old branch's eight-name list.
- Decide/document standard-lock routing for Claude, MiniMax and WorkBuddy when exposing adoption there. Incoming intentionally covered Codex/Cursor only and recognizes three standard roots. This is an integration completeness decision; it is not evidence that their existing MCP/native profiles are broken.
- Keep shared lock metadata separate from host payload files: explicit adoption may detach the shared registry while leaving other hosts' installed trees intact, as the incoming design already documents.
- Preserve current no-write previews, alias/independent-identity refusal, external-lock opt-out, native MCP formats, exact hook ownership and final discovery audit. Do not resurrect the old root `AGENTS.global.md` or older installer implementations during conflict resolution.

## Atomicity and verification limits

The examined helper stages a new file and replaces only after JSON serialization. A forced rename failure retained the original lock bytes and left zero `.skill-lock-*` temporary payloads; this part passed. The branch's outer Bash rollback records the exact lock backup and restores it after copy/adoption failure. Its structure is consistent with the existing component transaction contract; this review did not rerun the full branch rollback suite or claim concurrent external-writer safety.

One investigated hypothesis was rejected: an ordinary no-adoption custom-target preview with an irrelevant cyclic CODEX_HOME still returned 0. Do not report it as a defect.

The full five-host suite and final merge gate remain owned by the main session. No new broad test run or live installation is recommended merely for these findings.
