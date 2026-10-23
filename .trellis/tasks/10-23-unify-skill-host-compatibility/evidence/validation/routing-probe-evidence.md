# Skill 路由行为探针证据

- Task：`/Users/hogenxue/Projects/CodexTamplate/.trellis/tasks/10-23-unify-skill-host-compatibility`
- 记录时间（UTC）：`2026-10-23T15:52:08.929467+00:00`
- 性质：整理此前真实观察；本次不重跑探针或完整检查。
- 结果：七意图推演完成；隔离只读审查通过；四处已发现问题定向复核均通过，未发现原问题残留。
- 状态边界：原生宿主、应用加载、真实 Git index 流程和概率性模型回归均为 `not_run`。

## 方法与范围

读取 package 全局指导、manifest、相关 Skill 以及 Cursor/Claude/Trellis 原生入口，将其作为候选说明分析。七意图只做行为选择推演，未实际执行安装、拉取、归档或生产实现。唯一执行性探针是隔离 no-index Git diff 审查。修订后只复核此前问题及入口。

## 七意图结果

### 1. 审查当前未提交改动，只报告问题

- 主入口：code-review within one native trellis-check
- 首步：Resolve the user-requested diff and task boundary.；Read staged/unstaged changes, task-owned new files, PRD and applicable standards.
- 允许：Read source and requirements.；Run necessary focused checks without persistent changes.；Return Spec and Standards findings in chat.
- 不允许：Code/spec/task-record fixes；Task state changes；Commit/push/PR comments
- 停止条件：Findings and coverage limitations reported; unresolved scope is reported rather than guessed.
- 结果：Owner and read-only boundary were clear. Initial conflicting native clauses were identified and subsequently rechecked as resolved.
- 源码指针：`skills/code-review/SKILL.md:11-28`, `.cursor/skills/trellis-check/SKILL.md:10-26,84,119-121`, `.trellis/agents/check.md:23-45`

### 2. 需求已经确认，按现有PRD修复并运行相关检查

- 主入口：implement through native Trellis execution; one final trellis-check
- 首步：Resolve matching existing task and accepted PRD.；Read required design/plan/spec context and satisfy native start gate.；Follow configured inline/dispatch execution without duplicating an implement owner.
- 允许：In-scope implementation；Necessary existing task records；Focused tests and selected final checks
- 不允许：Unresolved scope expansion；Implicit commit/push/archive；Duplicated implementation/review workflow
- 停止条件：Authorized requirements and selected checks are complete; actual evidence and uncovered boundaries reported.
- 结果：Authorized implementation need not repeat an already-settled interview. Initial fixed lint/typecheck instructions were subsequently rechecked as resolved.
- 源码指针：`skills/implement/SKILL.md:11-26`, `.trellis/workflow.md:489-576`, `.cursor/agents/trellis-implement.md:75-99`, `.claude/agents/trellis-implement.md:76-100`, `.trellis/agents/implement.md:28-67`

### 3. $grill-me 先讨论这套方案，别写文件

- 主入口：explicit grill-me
- 首步：Use the explicitly invoked stateless skill.；Read discoverable facts and prior decisions before asking the current decision frontier.
- 允许：Conversation；Read-only fact lookup
- 不允许：File or Task writes；Spec creation；Implementation or tests；Git/publication
- 停止条件：No answerable decision frontier remains, or remaining branches require external evidence; summarize actual decisions and return control.
- 结果：Stateless and explicit-invocation boundaries are present in the body and invocation metadata. No host discovery runtime was tested.
- 源码指针：`skills/grill-me/SKILL.md:9-21`, `skills/grill-me/agents/openai.yaml:6`, `agents/AGENTS.global.md:43`

### 4. 复盘刚完成的安装，应用加载尚未验证

- 主入口：retro; native trellis-break-loop reuses the same analysis if invoked
- 首步：Resolve the relevant installation/task period.；Read recorded installation, preservation and verification evidence.；Separate observed outcome, hypothesis and unknown.
- 允许：Evidence-based retrospective in chat；Existing-record writes only when covered by documentation authorization
- 不允许：Claiming application reload from file checks；Reinstallation/restart/test rerun merely for retrospective；Task creation/status changes/archive/Git
- 停止条件：Material lessons have evidence or explicit uncertainty, and follow-ups are distinct from completed work.
- 结果：Application loading remains not_run; the retrospective does not silently complete it.
- 源码指针：`skills/retro/SKILL.md:8-29`, `.cursor/skills/trellis-break-loop/SKILL.md:8-23`, `.trellis/workflow.md:590-603`

### 5. 拉取最新代码，保留本地改动

- 主入口：focused native Git synchronization under existing authorization
- 首步：Inspect branch, configured remote, status, staging and untracked work.；Establish recoverable preservation and safe synchronization scope.
- 允许：Requested synchronization；Recoverable preservation/restoration of local work；Verification of sync and preservation
- 不允许：Implicit new development Task/interview/graph rebuild；Discarding local changes；Unapproved history rewrite or semantic conflict choices
- 停止条件：Synchronization and local-change preservation are evidenced; stop the dependent branch for an unresolved divergence or semantic decision.
- 结果：Workflow explicitly exempts focused Git sync from development-task creation. Fast-forward preference and recovery details are evaluator execution choices, not a claim that the candidate specifies a complete safe-pull algorithm. No Git sync was executed.
- 源码指针：`.trellis/workflow.md:152-157`, `agents/AGENTS.global.md:16-19,75`, `skills/resolving-merge-conflicts/SKILL.md:6-16`

### 6. 归档这个已完成任务（未授权 commit）

- 主入口：native finish-work
- 首步：Identify only the selected task.；Read acceptance evidence and blockers.；Confirm installed command options before execution.
- 允许：task.py archive <selected-task> --no-commit；Necessary add_session.py records with --no-commit；Archive, status, evidence and pointer verification
- 不允许：Implicit commit/push；Archiving incomplete or unrelated tasks；Assuming CLI no-commit default
- 停止条件：Selected task is archived with intact evidence and correct pointers; pending Git work reported. Unmet acceptance keeps the task active.
- 结果：Both native finish-work entrypoints explicitly supply --no-commit. The initial incorrect CLI-default wording was subsequently rechecked as resolved. No archive command was executed.
- 源码指针：`.cursor/commands/trellis-finish-work.md:3-42`, `.claude/commands/trellis/finish-work.md:3-42`, `.trellis/workflow.md:605-624`, `.trellis/scripts/task.py:453`, `.trellis/scripts/add_session.py:568-569,608`

### 7. 做一个临时演示确认交互（仓库没有 Trellis）

- 主入口：prototype using existing project workflow/locations
- 首步：State the bounded interaction/design question and observable verdict.；Use established project patterns and prototype locations.
- 允许：Disposable named demo；Memory/scratch data；Proportional run/state verification
- 不允许：Initializing Trellis merely for the skill；Production data or feature rollout；Implicit publish/commit/branch creation/destructive cleanup
- 停止条件：Observed verdict, remaining uncertainty and artifact/run pointer are reported; production adoption returns to an authorized implementation workflow.
- 结果：The candidate explicitly supports non-Trellis projects without introducing another task system. No prototype was built in this scenario evaluation.
- 源码指针：`skills/prototype/SKILL.md:9-17`, `agents/AGENTS.global.md:49`

## 隔离只读审查

- Fixture：`/var/folders/n2/clr4tz2x4571vm2nh8dmlkq80000gn/T/codextamplate-review-probe-364rrgua`
- 实际 diff 命令：`git --no-optional-locks diff --no-index -- baseline/src/pricing.py candidate/src/pricing.py`。返回 1 表示存在差异，不是工具异常。
- PRD 要求 `total_cents(125, 2) == 250`；候选把乘法改为加法，内存执行得到 127。报告一个 Spec P1，Standards 无发现，未应用修复。
- 前后 7 文件 SHA-256 比较全部一致；Task 状态、spec、无关笔记分别检查为 unchanged。初始逐文件摘要未单独保留；真实工具输出保存了比较结果。
- 未创建任何 Git refs/index。`fixture-result.json` 为实际结果转录；`fixture-driver.py` 为已执行 driver 的保存版本，本次没有执行。

## 四个残留冲突的定向复验

### F1. Channel check self-fixes without authorization and reviews incomplete task scope

- 初次证据：.trellis/agents/check.md:4,28,45 required direct mechanical self-fixes.；Initial lines 25 and 42 scoped only uncommitted diffs; missing new task-wide scope and separate Spec/Standards requirements.
- 可达入口：.cursor/skills/trellis-channel/references/workers.md:27,47-51 maps --agent check to .trellis/agents/check.md.；.cursor/skills/trellis-channel/references/workflows.md:58,81,85 invokes --agent check.；Claude channel reference copies were byte-equal during recheck.
- 复验：`passed`；.trellis/agents/check.md:25 includes task-owned earlier commits, staged/unstaged and new files.；Line 27 explicitly forbids read-only code/spec/task-record edits and conditions fixes on implementation authorization.；Lines 32-37 separate Spec/Standards, select necessary checks and gate documentation writes.；Line 45 leaves Git/task-state/archive decisions with supervising session under user authorization.
- 原问题残留：无。

### F2. Native check Spec Sync clause unconditionally says to update a spec

- 初次证据：Both .cursor and .claude/skills/trellis-check/SKILL.md:84 originally said If YES, update the relevant spec doc despite read-only protection elsewhere.
- 可达入口：Native trellis-check skill; the Cursor/Claude copies were byte-equal.
- 复验：`passed`；Both files:84 now require read-only review to propose updates only and permit application only under documentation authorization.；Lines 119-121 retain chat-only read-only reporting and authorized-fix boundaries.
- 原问题残留：无。

### F3. Implementation roles require fixed lint/typecheck and prefilled pass reports

- 初次证据：.cursor/agents/trellis-implement.md:77 and .claude/agents/trellis-implement.md:78 required project lint and typecheck; report examples prefilled Passed.；.trellis/agents/implement.md:28,43 required lint/typecheck on changed scope.
- 可达入口：.trellis/workflow.md:497-499,511-513,525-527 dispatches native implement roles.；Channel workers.md:47-51 maps --agent implement to .trellis/agents/implement.md.
- 复验：`passed`；Cursor:77 and Claude:78 now require task-selected proportionate checks, allow sufficient documentation structural checks, reuse valid evidence, report actual commands/results/limits.；Cursor:98-99 and Claude:99-100 no longer prefill Passed.；Channel implement:28,43 and report:66-67 use selected checks and actual results/uncovered reasons.
- 原问题残留：无。

### F4. Workflow inaccurately describes --no-commit as script default

- 初次证据：.trellis/workflow.md:618 originally said archive and journal scripts use --no-commit by default.；.trellis/scripts/add_session.py:608 actually passes auto_commit=not args.no_commit.；task.py:453 defines --no-commit as an explicit store_true flag.
- 可达入口：Both finish-work command files:20,33 explicitly pass --no-commit.
- 复验：`passed`；workflow.md:618 now states that scripts can auto-commit by default and callers must pass --no-commit unless exact resulting changes are covered by Git authorization.；Finish-work entrypoints retain explicit flags and installed-version capability checking.；Script source still matches the corrected description.
- 原问题残留：无。

## 真实命令与结果

以下是相关命令子集；完整结构化条目见 JSON。没有将未执行的 native 命令写成已执行。

### initial_read

```text
nl -ba skills/implement/SKILL.md; nl -ba skills/grill-me/SKILL.md; nl -ba skills/retro/SKILL.md; nl -ba skills/prototype/SKILL.md
```

Read actual skill bodies; exit 0.

### initial_read

```text
nl -ba .cursor/skills/trellis-check/SKILL.md; nl -ba .cursor/agents/trellis-check.md; nl -ba .cursor/commands/trellis-finish-work.md
```

Read native review and finish instructions; exit 0.

### fixture_review

```text
git --no-optional-locks diff --no-index -- baseline/src/pricing.py candidate/src/pricing.py
```

Exit 1, expected for a detected no-index difference; multiplication was changed to addition.

### fixture_review

```text
exec(compile(candidate_source, "candidate/src/pricing.py", "exec"), namespace); observed = namespace["total_cents"](125, 2)
```

Observed 127 versus PRD expected 250; no pycache or file output from this execution.

### fixture_review

```text
before = snapshot(); ...read-only diff/review...; after = snapshot(); before == after
```

True for all 7 files; task/spec/unrelated-note preservation each separately true. Per-file initial hashes were not printed or retained; the recorded tool result retained the comparison outcomes.

### targeted_recheck

```text
nl -ba .trellis/agents/check.md; nl -ba .trellis/agents/implement.md; nl -ba .cursor/agents/trellis-implement.md | sed -n '1,110p'; nl -ba .claude/agents/trellis-implement.md | sed -n '1,112p'
```

Exit 0. Read changed role bodies and confirmed F1/F3 fixes.

### targeted_recheck

```text
nl -ba .cursor/skills/trellis-check/SKILL.md | sed -n '76,88p;115,124p'; nl -ba .claude/skills/trellis-check/SKILL.md | sed -n '76,88p;115,124p'; nl -ba .trellis/workflow.md | sed -n '605,624p'; nl -ba .cursor/skills/trellis-channel/references/workers.md | sed -n '23,30p;44,54p;89,99p'; nl -ba .cursor/skills/trellis-channel/references/workflows.md | sed -n '45,90p'
```

Exit 0. Read changed Spec Sync/CLI-default clauses and actual channel routes.

### targeted_recheck

```text
rg -n "no-commit|auto_commit=not|auto_commit: bool" .cursor/commands/trellis-finish-work.md .claude/commands/trellis/finish-work.md .trellis/scripts/add_session.py .trellis/scripts/task.py
```

Exit 0. Confirmed explicit finish-work flags and matching script behavior.

## 未覆盖边界

- Metadata/body presence and text consistency do not prove runtime behavior.
- Fixture review was evaluator-guided and synthetic; it was not a native host invocation or isolated autonomous model run.
- No real pull, archive, implementation, explicit-Grill session, installation, or interaction prototype was executed for the seven scenarios.
- Initial file hashes were compared in process but not retained individually; retained results state equality.
- No repository/HOME/task-state/Git refs or index modifications were performed by this evaluator; only isolated temporary fixture/evidence files were created.

## 保存工件

- `routing-probe-evidence.json`：结构化全记录。
- `fixture-result.json`：已有实际工具结果转录。
- `fixture-driver.py`：此前执行 driver 的保存版本，不是本次重跑。
- 本文：供任务记录引用的说明。
