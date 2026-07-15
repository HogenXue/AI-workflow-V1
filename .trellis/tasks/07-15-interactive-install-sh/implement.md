# Implement: Interactive multi-agent installer

## Checklist

1. [x] Templates: `trellis/codex/` + `trellis/cursor/`
2. [x] Shared helpers for project-root prompt (candidates + skip; no silent git default) — `scripts/install-lib.sh`
3. [x] `scripts/install-codex-merge.sh`
4. [x] `scripts/install-cursor-merge.sh` (never touch root `AGENTS.md`)
5. [x] Extend `scripts/install.sh` — interactive multi-agent + explicit project pick
6. [x] Tests in `tests/test_install_interactive.py`
7. [x] README note for interactive + project-root
8. [x] Unittest suite green for install tests

## Validation

```bash
python -m unittest tests.test_install tests.test_trellis_tools tests.test_install_interactive
bash scripts/install.sh </dev/null; echo $?   # expect 2
```

## Project-root UX (locked)

- TTY: list candidates including cwd git root as an **option**; require choice; allow typed path; allow skip
- Non-interactive project writes: require `--project-root`; else skip + message
