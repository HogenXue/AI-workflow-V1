# CI merge integration review

Task: `.trellis/tasks/11-04-merge-hardening-design-review`.
Date: 2026-11-04 (Asia/Shanghai). Read-only review; no repository, HOME or index writes, no agents spawned, no test suites executed.

## Fixed comparison

- Current main: `43ca2442e3c98f464f22bd806d1a3047f27f3517`.
- Incoming: `7d685b9c740df2361f8c71f2a65df84a02179884` (`origin/codex/ai-workflow-hardening`).
- Merge base: `3bc7af23029a772d3da9672411b30e3d500e98b0`.
- Incoming CI commits: `10c7a0f9afe7988740e57f476b88431f0c9a3f30` adds dependency-cache input; `7d685b9` adds JSON output to the old workflow checker.

The current conflicted CI file has the incoming cache line already merged in the Unix job, while the conflict encloses main's direct checks and the complete Windows job. Selecting the incoming hunk wholesale would remove Windows coverage and invoke a checker deleted on main.

## Decisions required to retain both intents

### 1. Preserve main's native quality commands and Windows job

Retain `python scripts/validate-all-skills.py` and `python -m unittest discover -s tests`; add `-v` to the latter if per-test names/skip reasons are desired in CI logs. Retain the entire `windows-ps-install` job and its PowerShell suite loop.

Do not restore `config/workflow_check.py` or put `--format json` on `unittest`. Incoming's diagnostic fix addresses that old wrapper's behavior: subprocess stdout/stderr were captured and truncated to 4,000 characters in `_run_argv`/`_run_shell`; text output printed only status labels, while JSON exposed the captured fields. Main's direct commands already emit failures and tracebacks to runner logs without the wrapper. Keeping those direct streams retains the intended diagnosis while honoring the removed-checker contract.

Evidence:

- Incoming `config/workflow_check.py:274-281,294-301,498-507` at `7d685b9` records the capture and formatter behavior.
- Main `.github/workflows/ci.yml:27-30,32-77` runs direct checks and owns the Windows job.
- Main `.trellis/spec/scripts/installer-contracts.md:584-590` explicitly requires direct checks and Windows installer coverage.
- Main `tests/test_validate_all_skills.py:418-425` requires validator/unittest references and rejects `workflow_check.py` in CI.
- Existing removal PRD `.trellis/tasks/09-27-remove-workflow-check/prd.md:9-13,18-21` confirms deletion and historical-evidence retention were deliberate.

### 2. Apply cache dependency input to BOTH setup-python steps

After each existing `cache: pip`, add:

```yaml
cache-dependency-path: requirements-dev.txt
```

This must appear for both `quality` and `windows-ps-install`. Preserve main's `requirements-dev.txt`, including its conditional `tomli` dependency; do not overwrite it with incoming's older single-line file. Python 3.12 does not need that conditional package, but the package's Python 3.10 support still does.

Evidence:

- Main `.github/workflows/ci.yml:20-26` and `38-44` contain two cache/install setup pairs.
- Incoming `.github/workflows/ci.yml:25` fixes only the one job present on that older branch.
- Incoming `.trellis/spec/scripts/installer-contracts.md:327-343` says cache hashing and installation must use the same committed file; adapt the old references to “shared quality entry”/JSON to current direct checks rather than importing the paragraph verbatim.
- Main `requirements-dev.txt:1-2` contains PyYAML plus Python-version-conditional tomli; incoming has only PyYAML.

### 3. Preserve all eight existing Windows patterns, and include new adoption PS coverage

The main Windows loop has eight patterns that expand to **14 distinct current test modules**:

- `test_aihero_install.py`
- `test_install_*_ps.py` — 7 modules, including native Windows Codex context hook execution
- `test_install_new_hosts.py`
- `test_host_preservation.py`
- `test_skill_catalog.py`
- `test_mcp_native_formats.py`
- `test_install_wizard.py`
- `test_install_dependencies.py`

Retain PowerShell 7 verification, Developer Mode attempt for symlinks, `-v`, and immediate `$LASTEXITCODE` propagation. These guard both actual execution and honest platform skips. Main spec lines 673-674 explicitly require new-host, preservation, catalog and native-MCP suites in addition to older PS tests.

Incoming's 15 new adoption tests are in `tests/test_install.py:103-380` at `7d685b9`; they call the Bash component. The new real-TTY adoption tests are in `tests/test_install_interactive.py`, also Bash-oriented. Neither module matches the Windows suite list. Preserving that list alone therefore does not establish the new adoption flag's PowerShell parity.

For the root's new PS adoption regressions, prefer adding them to an existing selected PS module, naming a new module `test_install_skill_lock_ps.py`, or explicitly adding a new cross-platform adoption module to `$suites`. Do not simply add all of `test_install.py` to Windows: incoming's FIFO test directly uses `os.mkfifo` and the module hard-codes Bash execution. If a generic adoption module is introduced, guard genuinely POSIX-only cases and exercise the native PS component separately.

Evidence:

- Main CI lines 71-76 define the exact patterns and nonzero propagation.
- Main `tests/test_host_preservation.py:156-159` and `tests/test_install_new_hosts.py:250-253` supply native PowerShell harnesses when pwsh exists.
- Incoming `tests/test_install.py:34-43` invokes `bash`; line 175's FIFO test uses `os.mkfifo` at 177.
- Task PRD requires shell peers to have meaningful fixture evidence and preservation of existing Windows compatibility.

## Completed checks and boundaries

A proposed resolution was constructed only in memory from fixed main: add both cache paths, add Unix unittest `-v`, keep every other step. YAML parsed successfully; both job names and the Unix OS matrix remained intact; each setup-python points to `requirements-dev.txt`; removed checker references were absent. All eight Windows patterns match files and the expansion contains 14 unique modules with no duplicate selection.

Machine-readable static evidence: `ci-structural-check.json` beside this report. This is structural validation, not a GitHub Actions run, Windows acceptance, or full suite pass. Existing code/test runtime evidence remains owned by the root agent's final gate.
