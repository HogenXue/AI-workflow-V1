# Grill Me 与 Trellis 集成实施计划

## Goal

交付一个通过仓库安装器分发、能在 Trellis planning 中自动接管需求访谈并将结论沉淀到现有 task PRD 的 `grill-me` fork。

## Architecture

Skill package 提供访谈与 PRD handoff 协议；全局 AGENTS 模板只负责在恰当的 Trellis 请求上路由到该 Skill；manifest 让现有安装器分发它。Trellis task 仍保存所有正式 planning artifacts，并继续控制 `task.py start`。

## Tech Stack

Markdown、YAML、Bash、Python `unittest`、现有 `scripts/validate-all-skills.py`。

## Global Constraints

- 不覆盖或回退当前工作区已有的 README、`scripts/install-agents.sh`、`tests/test_trellis_tools.py`、`trellis/README.zh-CN.md` 改动。
- 新 Skill 必须通过仓库 Skill validator，并遵守完整 bundled Skill 目录契约。
- 不向真实 `~/.codex` 写入；所有安装验证使用临时目录。
- 不在全局模板中创建第二套 Task、PRD、Design 或 Spec；Trellis 是唯一持久化工作流。

## Superseding workflow boundary

The detailed steps below were revised after the user confirmed the final ownership model. This section overrides any conflicting earlier wording:

- Grill Me is optional and auto-routes only complex or unclear requirements.
- OpenSpec owns the canonical behavior Spec: requirements, scenarios, and acceptance. In a Trellis project it does not maintain a task list.
- Trellis owns the task-level PRD/plan, status, and Journal. Its PRD/plan references the OpenSpec Spec and must not duplicate behavior content.
- TDD owns the test-first implementation loop. GitNexus is cross-cutting: impact analysis happens before edits and Git-scope validation happens before a commit.

---

### Task 1: 建立可自动调用的 Grill Me Skill 包

**Files:**
- Create: `skills/grill-me/SKILL.md`
- Create: `skills/grill-me/agents/openai.yaml`
- Create: `skills/grill-me/references/trellis-handoff.md`
- Create: `skills/grill-me/templates/prd-requirements.md`
- Create: `skills/grill-me/examples/new-feature-session.md`
- Create: `skills/grill-me/scripts/validate.sh`
- Modify: `tests/test_validate_all_skills.py`

**Interfaces:**
- Consumes: current task path from Trellis and the standard bundled-Skill validation contract.
- Produces: `$grill-me` with implicit invocation enabled; a predictable PRD handoff template and a single-skill validation command.

- [ ] Add a failing `BundledSkillContractTests.test_grill_me_enables_implicit_invocation_and_trellis_handoff` test that loads `skills/grill-me/SKILL.md` and `agents/openai.yaml`, asserts the frontmatter name is `grill-me`, asserts `disable-model-invocation` is absent, asserts `policy.allow_implicit_invocation is True`, and checks the Skill references `prd.md`, `task.py start`, and `trellis-brainstorm`.
- [ ] Run `python3 -m unittest tests.test_validate_all_skills.BundledSkillContractTests.test_grill_me_enables_implicit_invocation_and_trellis_handoff -v`; expect failure because the new Skill does not exist.
- [ ] Create the six required package artifacts. The main Skill must state the exact sequence: confirm task creation; create or resolve the planning task; ask one question; inspect repository facts first; write every resolved answer to `prd.md`; summarize Scope, Non-goals, Acceptance criteria, and Open items; request user confirmation; use `trellis-brainstorm` only when Open items remain; do not call `task.py start` before confirmation.
- [ ] Run `python3 scripts/validate-all-skills.py --skill grill-me` and the focused unittest again; expect both to pass.

### Task 2: Register and distribute the Skill

**Files:**
- Modify: `manifest.yaml`
- Modify: `tests/test_install.py`

**Interfaces:**
- Consumes: `manifest.yaml` skill list, which `scripts/install-skills.sh` parses as indented names.
- Produces: `grill-me` included by every existing copy/link installation mode without changing installer behavior.

- [ ] Update `tests/test_install.py` so the `SKILLS` tuple includes `grill-me`; add assertions that a skills dry-run reports `copy grill-me` and a copy install creates `grill-me/SKILL.md`.
- [ ] Run the affected `ComponentInstallTests` cases; expect failure while `manifest.yaml` lacks `grill-me`.
- [ ] Add `  - grill-me` to `manifest.yaml` immediately after existing workflow skills, keeping `default_install_mode: copy` unchanged.
- [ ] Run `python3 -m unittest tests.test_install.ComponentInstallTests -v`; expect success.
- [ ] Run `bash scripts/install.sh skills --dry-run --target "$(mktemp -d)/skills"`; expect one `DRY-RUN` line for `grill-me` and no writes to the user’s Codex home.

### Task 3: Add the Trellis-aware global route and user documentation

**Files:**
- Modify: `trellis/AGENTS.global.md`
- Modify: `README.md`
- Modify: `skills/openspec/SKILL.md`
- Test: `tests/test_trellis_tools.py` or a new focused template-content test if avoiding unrelated dirty sections is safer

**Interfaces:**
- Consumes: the global template copied by `scripts/install-agents.sh` and the workflow state rules defined by Trellis projects.
- Produces: a precise automatic route that hands new/large/unclear Trellis requests to `$grill-me` after task consent and preserves Trellis ownership for all official artifacts.

- [ ] Add a failing template-content assertion for the exact order `task creation consent`, `$grill-me`, `prd.md`, `trellis-brainstorm`, and `task.py start` without changing existing tests related to hooks.
- [ ] Run that focused test and confirm it fails because the template does not yet route through Grill Me.
- [ ] Insert a concise `grill-me` bullet under the existing Trellis workflow routing section: it applies only to new features, larger refactors, or unclear requirements; it requires task creation consent first; it uses Grill Me as the only initial interview; it persists and summarizes PRD data; it skips `trellis-brainstorm` unless open items remain; and it preserves the explicit confirmation gate before start.
- [ ] Add a Trellis-aware OpenSpec rule: OpenSpec owns requirements, scenarios, and acceptance, but must not create a second task list when Trellis owns task-level PRD/plan and Journal.
- [ ] Update only the unaffected Skills list and installation documentation portions of `README.md` to name `grill-me`, explain its Trellis handoff role, and show the existing `skills --copy --replace` command. Preserve the user’s current hooks-related edits verbatim.
- [ ] Re-run the template test and `python3 -m unittest tests.test_trellis_tools -v`; expect success.

### Task 4: Full verification and planning handoff

**Files:**
- Verify: `skills/grill-me/**`, `manifest.yaml`, `trellis/AGENTS.global.md`, `README.md`, `tests/test_install.py`, `tests/test_trellis_tools.py`, `tests/test_validate_all_skills.py`

**Interfaces:**
- Consumes: all artifacts produced in Tasks 1–3.
- Produces: verified package behavior ready for a user-approved `task.py start` and normal Trellis implementation flow.

- [ ] Run `python3 scripts/validate-all-skills.py` after ensuring PyYAML is available; expect `OK: grill-me` together with every existing manifest Skill.
- [ ] Run `python3 -m unittest tests.test_install tests.test_trellis_tools tests.test_validate_all_skills -v`; expect all tests to pass.
- [ ] Run `bash -n scripts/install-skills.sh scripts/install-agents.sh scripts/install.sh` and `bash scripts/install.sh skills --dry-run --target "$(mktemp -d)/skills"`; expect zero syntax errors and a dry-run listing including `grill-me`.
- [ ] Inspect `git diff --check` and `git diff -- <task-owned files>`; confirm no whitespace errors and no unintended changes to the user’s pre-existing dirty hunks.
- [ ] Present the verification results and the commit plan to the user; do not start or commit without the separate approvals required by the Trellis workflow and project Git rules.

## Spec-update decision

This task creates a package-distribution and global-routing convention rather than a frontend or backend coding convention. The durable rule is therefore stored in `trellis/AGENTS.global.md` and the `grill-me` Skill itself; no `.trellis/spec/` update is applicable.
