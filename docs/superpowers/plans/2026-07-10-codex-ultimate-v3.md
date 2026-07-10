# Codex Ultimate v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a maintainable source package that replaces the six standard Codex core-development Skills with Hogen's configurable, Chinese-first workflows.

**Architecture:** Keep global collaboration boundaries in a short root `AGENTS.md`; place one independently-triggered Skill in each `skills/<name>/` directory. A root YAML default plus a target-repository YAML override govern shared behavior; Python validates package structure and Bash performs transactional replacement installation.

**Tech Stack:** Markdown and YAML metadata, Python 3.10+ with PyYAML, Bash, Python `unittest`.

---

## File structure

```text
AGENTS.md
manifest.yaml
requirements-dev.txt
config/defaults.yaml
config/project-config.schema.yaml
skills/{memory,gitnexus,openspec,review,debugging,release}/
  SKILL.md
  agents/openai.yaml
  references/*.md
  templates/*.md
  examples/*.md
  scripts/validate.sh
scripts/validate-all-skills.py
scripts/install.sh
tests/test_validate_all_skills.py
tests/test_install.py
```

`scripts/validate-all-skills.py` is the only structural validator. Per-Skill `scripts/validate.sh` wrappers delegate to it with their own directory name, so all Skill validation behavior stays consistent while each Skill remains executable and extensible.

### Task 1: Create the test and dependency foundation

**Files:**
- Create: `requirements-dev.txt`
- Create: `tests/test_validate_all_skills.py`
- Create: `tests/test_install.py`

- [ ] **Step 1: Add the development dependency declaration**

Create `requirements-dev.txt`:

```text
PyYAML>=6.0,<7.0
```

- [ ] **Step 2: Add failing validator tests**

Create `tests/test_validate_all_skills.py` with tests that load `scripts/validate-all-skills.py` through `importlib.util.spec_from_file_location`, create temporary package fixtures, and assert these public functions exist and behave as follows:

```python
import importlib.util
from pathlib import Path

def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("validator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def create_complete_skill(root: Path, name: str) -> Path:
    skill = root / name
    for directory in ("agents", "references", "templates", "examples", "scripts"):
        (skill / directory).mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        f"---\\nname: {name}\\ndescription: test skill\\n---\\n[ref](references/guide.md)\\n",
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text("display_name: Test\\n", encoding="utf-8")
    (skill / "references" / "guide.md").write_text("guide\\n", encoding="utf-8")
    return skill

def test_validate_skill_accepts_complete_skill(tmp_path):
    assert validator.validate_skill(create_complete_skill(tmp_path, "review")) == []

def test_validate_skill_reports_missing_resource_directory(tmp_path):
    skill = create_complete_skill(tmp_path, "review")
    (skill / "examples").rmdir()
    assert "missing required directory: examples" in validator.validate_skill(skill)

def test_validate_yaml_reports_invalid_frontmatter(tmp_path):
    path = tmp_path / "SKILL.md"
    path.write_text("---\\nname: review: broken\\n---\\n", encoding="utf-8")
    assert "invalid YAML" in validator.load_skill_metadata(path)[1]
```

- [ ] **Step 3: Add failing installer tests**

Create `tests/test_install.py` using `tempfile.TemporaryDirectory()` and `subprocess.run()` to assert:

```python
import subprocess
from pathlib import Path

def run_install(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(ROOT / "scripts" / "install.sh"), *args, "--target", str(target), "--backup-dir", str(backup)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

def test_dry_run_does_not_modify_target():
    result = run_install("--dry-run")
    assert result.returncode == 0
    assert not (target / "review").exists()

def test_conflict_without_replace_preserves_existing_skill():
    (target / "review").mkdir()
    (target / "review" / "sentinel").write_text("keep", encoding="utf-8")
    result = run_install("--copy")
    assert result.returncode != 0
    assert (target / "review" / "sentinel").read_text(encoding="utf-8") == "keep"

def test_replace_backs_up_and_replaces_existing_skill():
    (target / "review").mkdir()
    (target / "review" / "sentinel").write_text("old", encoding="utf-8")
    result = run_install("--copy", "--replace")
    assert result.returncode == 0
    assert (target / "review" / "SKILL.md").exists()
    assert any(path.name.startswith("review.") for path in backup.iterdir())
```

- [ ] **Step 4: Run the tests and verify the expected initial failure**

Run: `python3 -m pip install -r requirements-dev.txt && python3 -m unittest discover -s tests -v`

Expected: FAIL because `scripts/validate-all-skills.py` and `scripts/install.sh` do not yet exist.

### Task 2: Add package identity, shared configuration, and global guidance

**Files:**
- Create: `AGENTS.md`
- Create: `manifest.yaml`
- Create: `config/defaults.yaml`
- Create: `config/project-config.schema.yaml`

- [ ] **Step 1: Write the root AGENTS.md within the 30-line budget**

Include the concrete rules: Chinese replies; state uncertainty; satisfy the request with the smallest change; do not refactor unrelated code; describe plan/assumptions/trade-offs/verification for complex work; do not claim unrun tests, deployment, restart, commit, or tool results; document interface contract changes; report changes, verification, results, and remaining work; load applicable installed Skills; honor nearest project instructions over package defaults.

- [ ] **Step 2: Create the package manifest**

Write `manifest.yaml`:

```yaml
version: 3.0.0
skills:
  - memory
  - gitnexus
  - openspec
  - review
  - debugging
  - release
default_install_mode: link
requires:
  python: ">=3.10"
  python_packages:
    - PyYAML
```

- [ ] **Step 3: Create defaults and the override schema**

Write `config/defaults.yaml`:

```yaml
language: zh-CN
change_policy:
  minimal_change: true
  preserve_dirty_worktree: true
  require_impact_analysis_before_symbol_edit: false
verification:
  report_unexecuted_steps: true
  require_spec_for_complex_change: true
tools:
  missing_tool_policy: report-and-degrade
```

Write `config/project-config.schema.yaml` with the allowed top-level mapping keys `language`, `change_policy`, `verification`, and `tools`, each containing the exact leaf keys from `defaults.yaml` and scalar types `string` or `boolean`.

- [ ] **Step 4: Add and run a layout test**

Add `test_manifest_lists_exactly_six_standard_skill_names` to `tests/test_validate_all_skills.py`:

```python
metadata = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
assert metadata["skills"] == ["memory", "gitnexus", "openspec", "review", "debugging", "release"]
```

Run: `python3 -m unittest tests.test_validate_all_skills -v`

Expected: FAIL only on unimplemented validator imports; manifest assertion passes.

### Task 3: Implement memory and gitnexus Skills

**Files:**
- Create: `skills/memory/{SKILL.md,agents/openai.yaml,references/memory-backends.md,templates/decision.md,examples/record-decision.md,scripts/validate.sh}`
- Create: `skills/gitnexus/{SKILL.md,agents/openai.yaml,references/impact-and-worktree.md,templates/impact-report.md,examples/assess-symbol-change.md,scripts/validate.sh}`

- [ ] **Step 1: Create both six-directory Skill layouts**

For each directory create `agents`, `references`, `templates`, `examples`, and `scripts`. Each `scripts/validate.sh` must be executable and contain:

```bash
#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
python3 "$repo_root/scripts/validate-all-skills.py" --skill "$(basename "$(dirname "$0")")"
```

- [ ] **Step 2: Write trigger metadata and short workflows**

Use these frontmatter values:

```yaml
name: memory
description: "Retrieve and record durable project context, decisions, learned constraints, and completed outcomes. Use for prior-work questions, architecture decisions, handoffs, and preserving important conclusions."
```

```yaml
name: gitnexus
description: "Analyze code relationships, change impact, worktrees, commit scope, and release branches. Use before changing symbols, reviewing blast radius, working with Git worktrees, or validating affected flows before a commit."
```

Each body first loads shared configuration, then checks tool availability, follows its workflow, and explicitly reports missing capabilities. Reference the corresponding `references/*.md` by relative path.

- [ ] **Step 3: Add concrete reusable resources**

Make `templates/decision.md` contain headings `Context`, `Decision`, `Alternatives`, `Consequences`, and `Verification`. Make `templates/impact-report.md` contain headings `Target`, `Direct callers`, `Affected flows`, `Risk`, and `Evidence`. Examples must show a Chinese user request, which workflow runs, and a concise Chinese final report.

### Task 4: Implement openspec and review Skills

**Files:**
- Create: `skills/openspec/{SKILL.md,agents/openai.yaml,references/change-classification.md,templates/change-spec.md,examples/design-api-change.md,scripts/validate.sh}`
- Create: `skills/review/{SKILL.md,agents/openai.yaml,references/review-severity.md,templates/review-report.md,examples/review-pull-request.md,scripts/validate.sh}`

- [ ] **Step 1: Create both layouts and their executable wrappers**

Create the five directories for each Skill. In both `scripts/validate.sh` files, write:

```bash
#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
python3 "$repo_root/scripts/validate-all-skills.py" --skill "$(basename "$(dirname "$0")")"
```

- [ ] **Step 2: Write exact metadata**

```yaml
name: openspec
description: "Create and maintain requirements, technical designs, RFCs, API contracts, database contracts, and implementation tasks for medium or large changes. Use before architecture-heavy, cross-module, data-model, or interface changes."
```

```yaml
name: review
description: "Review code changes for correctness, security, compatibility, maintainability, performance, and regression risk. Use for pull-request review, pre-merge review, release review, or a focused review of changed files."
```

- [ ] **Step 3: Add resources with fixed output structures**

`change-spec.md` must use headings `Problem`, `Scope`, `Acceptance criteria`, `Design`, `Risks`, and `Verification`. `review-report.md` must use `Findings` followed by `Severity`, `Evidence`, `Impact`, and `Recommendation`. Reference material must define when a change needs a spec and how P0–P3 findings are reported.

### Task 5: Implement debugging and release Skills

**Files:**
- Create: `skills/debugging/{SKILL.md,agents/openai.yaml,references/evidence-loop.md,templates/debug-report.md,examples/fix-runtime-error.md,scripts/validate.sh}`
- Create: `skills/release/{SKILL.md,agents/openai.yaml,references/release-gates.md,templates/release-checklist.md,examples/prepare-release.md,scripts/validate.sh}`

- [ ] **Step 1: Create both layouts and their executable wrappers**

Create the five directories for each Skill. In both `scripts/validate.sh` files, write:

```bash
#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
python3 "$repo_root/scripts/validate-all-skills.py" --skill "$(basename "$(dirname "$0")")"
```

- [ ] **Step 2: Write exact metadata**

```yaml
name: debugging
description: "Investigate bugs, crashes, test failures, and unexpected behavior through reproduction, evidence collection, root-cause isolation, minimal repair, and verification. Use whenever diagnosing or fixing a defect."
```

```yaml
name: release
description: "Plan, verify, execute, and report releases with versioning, change notes, rollback readiness, and post-release checks. Use for release preparation, deployment, rollout, rollback, or release-status verification."
```

- [ ] **Step 3: Add resources with fixed evidence gates**

`debug-report.md` must contain `Reproduction`, `Observed evidence`, `Root cause`, `Minimal fix`, `Verification`, and `Unverified`. `release-checklist.md` must contain `Scope`, `Pre-release checks`, `Rollback`, `Execution record`, `Post-release checks`, and `Outstanding risks`. The examples must demonstrate Chinese reporting that distinguishes completed and unexecuted operations.

### Task 6: Implement the package validator

**Files:**
- Create: `scripts/validate-all-skills.py`
- Modify: `tests/test_validate_all_skills.py`

- [ ] **Step 1: Implement the tested public functions**

Implement `load_yaml(path)`, `load_skill_metadata(path)`, `validate_skill(skill_path)`, `validate_config(path)`, and `main(argv)`. `load_skill_metadata` must isolate the first `---` frontmatter block, use `yaml.safe_load`, require only scalar `name` and `description`, and return `(metadata, error_text)`. `validate_skill` must require all six resource paths and verify every Markdown relative link resolves inside its Skill directory.

- [ ] **Step 2: Implement command behavior**

Support `--skill NAME`, `--root PATH`, and `--project-root PATH`. `--root` identifies the package root; `--project-root` identifies the optional external `hogen-codex.yaml` and defaults to the package root. Without `--skill`, read `manifest.yaml`, validate all listed skills, load defaults and schema from the package root, then validate and merge the project override, print `OK: <name>` for every valid Skill, and exit 0. With errors, print `ERROR: <path>: <reason>` for each and exit 1.

- [ ] **Step 3: Extend tests for broken links and invalid configuration**

Add:

```python
def test_validate_skill_reports_broken_relative_link(tmp_path):
    skill = create_complete_skill(tmp_path, "review")
    (skill / "SKILL.md").write_text("---\\nname: review\\ndescription: review code\\n---\\n[missing](references/nope.md)", encoding="utf-8")
    assert "broken relative reference: references/nope.md" in validator.validate_skill(skill)
```

- [ ] **Step 4: Run all validator tests**

Run: `python3 -m unittest tests.test_validate_all_skills -v`

Expected: PASS.

### Task 7: Implement controlled replacement installation

**Files:**
- Create: `scripts/install.sh`
- Modify: `tests/test_install.py`

- [ ] **Step 1: Implement strict argument parsing**

Accept `--dry-run`, `--link`, `--copy`, `--replace`, `--target PATH`, and `--backup-dir PATH`. Reject missing values, both `--link` and `--copy`, and unrecognized flags with exit 2. Default to `--dry-run --link`, `--target "${CODEX_HOME:-$HOME/.codex}/skills"`, and `--backup-dir "$target/.codex-ultimate-v3-backups"`.

- [ ] **Step 2: Implement preflight and backup transaction**

Read the six names from `manifest.yaml`; verify each source directory exists; identify conflicts before mutating anything. If conflicts exist without `--replace`, print them and exit 1. With `--replace`, move every conflict to `$backup_dir/<UTC timestamp>/<skill>` before creating links or copies. On any failed creation, remove newly created targets and move all backups back to their original names before exiting nonzero.

- [ ] **Step 3: Implement output contract**

Dry-run prints `DRY-RUN: <mode> <skill> -> <target>/<skill>` for all six Skills and exits 0 without writes. Successful mutation prints `INSTALLED: <skill>` per skill and then `BACKUP: <path>` when replacement created a backup. Never delete backup directories automatically.

- [ ] **Step 4: Run installer tests**

Run: `python3 -m unittest tests.test_install -v`

Expected: PASS for dry-run, conflict preservation, copy replacement backup, and argument rejection.

### Task 8: Verify the package as an installable source artifact

**Files:**
- Modify: `docs/superpowers/specs/2026-07-10-codex-ultimate-v3-design.md`
- Modify: `docs/superpowers/specs/2026-07-10-codex-ultimate-v3-requirements.md`

- [ ] **Step 1: Run structural validation**

Run: `python3 scripts/validate-all-skills.py`

Expected: six `OK:` lines, then exit 0.

- [ ] **Step 2: Run the complete regression suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: PASS with no skipped safety tests.

- [ ] **Step 3: Run an isolated installer dry-run**

Run: `tmpdir="$(mktemp -d)"; bash scripts/install.sh --dry-run --copy --target "$tmpdir/skills"; test ! -e "$tmpdir/skills/review"`

Expected: six `DRY-RUN:` lines and no created target Skill.

- [ ] **Step 4: Record final verification only after commands actually pass**

Append a dated verification note to the design document listing the exact commands and their actual results. Do not claim a Git commit because the current workspace has no `.git` directory; do not initialize one implicitly.

## Spec coverage review

- Requirements 1–3: Tasks 2–5 create global guidance and six complete Skill layouts.
- Requirement 4: Tasks 2 and 6 define and validate default/project configuration.
- Requirement 5: Tasks 3–5 require explicit availability and degradation rules.
- Requirements 6–7: Task 7 tests dry-run, conflict refusal, backup, replacement, and rollback behavior.
- Requirement 8: Tasks 1 and 6 implement and test the validator; Task 8 runs the full package check.

No Git commit task is included because this workspace is not a Git repository and the approved scope forbids implicit repository initialization.
