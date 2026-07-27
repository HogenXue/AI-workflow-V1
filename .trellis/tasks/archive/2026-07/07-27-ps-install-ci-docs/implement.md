# Implement: ps-install-ci-docs

1. [x] Add `tests/test_install_*_ps.py` modules covering parent AC-P3 scenarios (lib/entry/components/merge).
2. [x] Update `.github/workflows/ci.yml` for Windows + pwsh + PS tests.
3. [x] Update README + `.trellis/spec/scripts/*`.
4. [x] Quality check: local `test_install_*_ps.py` green; unix `quality` job unchanged (full unittest discover; PS classes skip without pwsh).

Depends: entry complete for green path.

