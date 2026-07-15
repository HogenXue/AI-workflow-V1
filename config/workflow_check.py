#!/usr/bin/env python3
"""Run read-only Trellis gates and repository quality checks."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from config.effective_config import load_effective_config  # noqa: E402


CHECKBOX = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$", re.M)
PLACEHOLDER = re.compile(r"\b(?:TBD|TODO)\b", re.I)
SECTION_ALIASES = {
    "goal": {"goal", "目标"},
    "requirements": {"requirements", "需求", "要求"},
    "acceptance_criteria": {"acceptance criteria", "验收标准", "验收条件"},
}
VOLATILE_PREFIXES = (".gitnexus/", ".trellis/.runtime/")


def _issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError as error:
        return None, f"无法读取 {path}: {error}"
    except json.JSONDecodeError as error:
        return None, f"JSON 无效 {path}: {error}"


def _resolve_task(project_root: Path, task: str) -> tuple[Path | None, list[dict[str, str]]]:
    candidate = Path(task)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError:
        return None, [_issue("task_outside_project", "任务目录必须位于项目根目录内")]
    if not candidate.is_dir():
        return None, [_issue("missing_task", f"任务目录不存在：{candidate}")]
    return candidate, []


def _markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            heading = match.group(1).strip().casefold()
            current = None
            for name, aliases in SECTION_ALIASES.items():
                if heading in aliases:
                    current = name
                    sections.setdefault(name, [])
                    break
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _placeholder_section(section: str | None) -> bool:
    if not section:
        return True
    meaningful = re.sub(r"^[\s*-]+", "", section).strip(" .")
    return not meaningful or bool(PLACEHOLDER.search(section))


def _task_status(task_dir: Path) -> tuple[str | None, list[dict[str, str]]]:
    data, error = _load_json(task_dir / "task.json")
    if error:
        return None, [_issue("invalid_task_json", error)]
    if not isinstance(data, dict) or not isinstance(data.get("status"), str):
        return None, [_issue("missing_task_status", "task.json 缺少字符串 status")]
    return data["status"], []


def _prd_sections(task_dir: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    path = task_dir / "prd.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return {}, [_issue("missing_prd", f"无法读取 prd.md：{error}")]
    return _markdown_sections(text), []


def _context_issues(project_root: Path, task_dir: Path) -> list[dict[str, str]]:
    manifests = [task_dir / "implement.jsonl", task_dir / "check.jsonl"]
    if not any(path.exists() for path in manifests):
        return []

    issues: list[dict[str, str]] = []
    for path in manifests:
        action = path.stem
        entries: list[dict[str, Any]] = []
        if path.is_file():
            try:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if not line.strip():
                        continue
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError as error:
                        issues.append(
                            _issue(
                                f"invalid_{action}_context",
                                f"{path.name}:{number} JSON 无效：{error}",
                            )
                        )
                        continue
                    if isinstance(item, dict) and item.get("file"):
                        entries.append(item)
            except OSError as error:
                issues.append(_issue(f"invalid_{action}_context", f"无法读取 {path.name}：{error}"))
        if not entries:
            issues.append(
                _issue(
                    f"uncurated_{action}_context",
                    f"{path.name} 必须包含真实的 spec/research 上下文条目",
                )
            )
            continue
        for entry in entries:
            relative = str(entry["file"])
            reason = entry.get("reason")
            allowed = relative.startswith(".trellis/spec/") or "/research/" in relative
            target = (project_root / relative).resolve()
            try:
                target.relative_to(project_root)
            except ValueError:
                allowed = False
            if not allowed or not target.is_file() or not isinstance(reason, str) or not reason.strip():
                issues.append(
                    _issue(
                        f"invalid_{action}_context_entry",
                        f"{path.name} 条目必须指向现有 spec/research 文件并说明原因：{relative}",
                    )
                )
    return issues


def readiness(
    project_root: Path,
    task_dir: Path,
    config: dict[str, Any],
    complex_task: bool,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    status, status_issues = _task_status(task_dir)
    issues.extend(status_issues)
    if status is not None and status != "planning":
        issues.append(_issue("wrong_task_status", f"readiness 要求 planning，当前为 {status}"))

    sections, prd_issues = _prd_sections(task_dir)
    issues.extend(prd_issues)
    for name, code, label in (
        ("goal", "placeholder_goal", "Goal/目标"),
        ("requirements", "placeholder_requirements", "Requirements/需求"),
        (
            "acceptance_criteria",
            "placeholder_acceptance_criteria",
            "Acceptance Criteria/验收标准",
        ),
    ):
        if _placeholder_section(sections.get(name)):
            issues.append(_issue(code, f"PRD {label} 缺失或仍是占位内容"))
    acceptance = sections.get("acceptance_criteria", "")
    if acceptance and not CHECKBOX.search(acceptance):
        issues.append(_issue("missing_acceptance_checkboxes", "验收标准必须包含复选框"))

    require_spec = bool(
        config.get("verification", {}).get("require_spec_for_complex_change", True)
    )
    if complex_task and require_spec:
        if not (task_dir / "design.md").is_file():
            issues.append(_issue("missing_design", "复杂任务缺少 design.md"))
        if not (task_dir / "implement.md").is_file():
            issues.append(_issue("missing_implement", "复杂任务缺少 implement.md"))
    issues.extend(_context_issues(project_root, task_dir))
    return {"command": "readiness", "ok": not issues, "issues": issues}


def _git_output(project_root: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        text=text,
        capture_output=True,
        check=False,
    )


def git_head(project_root: Path) -> str:
    result = _git_output(project_root, "rev-parse", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else "UNBORN"


def worktree_fingerprint(project_root: Path, evidence_path: Path | None = None) -> str:
    """Hash tracked and unignored untracked files without mutating the worktree."""

    result = _git_output(
        project_root,
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
        text=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())

    excluded: str | None = None
    if evidence_path is not None:
        try:
            excluded = evidence_path.resolve().relative_to(project_root).as_posix()
        except ValueError:
            excluded = None
    paths = sorted(
        path.decode("utf-8", errors="surrogateescape")
        for path in result.stdout.split(b"\0")
        if path
    )
    digest = hashlib.sha256()
    for relative in paths:
        normalized = Path(relative).as_posix()
        if normalized == excluded or any(normalized.startswith(prefix) for prefix in VOLATILE_PREFIXES):
            continue
        path = project_root / relative
        digest.update(normalized.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")
        if path.is_symlink():
            digest.update(b"L\0")
            digest.update(path.readlink().as_posix().encode("utf-8", errors="surrogateescape"))
        elif path.is_file():
            digest.update(b"F\0")
            digest.update(path.read_bytes())
        else:
            digest.update(b"MISSING\0")
        digest.update(b"\0")
    return digest.hexdigest()


def _run_command(name: str, command: str, project_root: Path) -> dict[str, Any]:
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=project_root,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": name,
        "command": command,
        "status": "passed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def _run_argv(name: str, argv: list[str], project_root: Path) -> dict[str, Any]:
    started = time.monotonic()
    result = subprocess.run(
        argv,
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": name,
        "command": " ".join(argv),
        "status": "passed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def _python_syntax_check(project_root: Path) -> dict[str, Any]:
    started = time.monotonic()
    roots = [project_root / name for name in ("config", "scripts", "tests", "trellis")]
    files = sorted(path for root in roots if root.is_dir() for path in root.rglob("*.py"))
    errors: list[str] = []
    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeError) as error:
            errors.append(f"{path.relative_to(project_root)}: {error}")
    return {
        "name": "python-syntax",
        "command": "AST parse config scripts tests trellis",
        "status": "passed" if not errors else "failed",
        "exit_code": 0 if not errors else 1,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "stdout": f"checked {len(files)} Python files\n",
        "stderr": "\n".join(errors),
    }


def _shell_syntax_check(project_root: Path) -> dict[str, Any]:
    started = time.monotonic()
    roots = [project_root / "scripts", project_root / "trellis"]
    files = sorted(path for root in roots if root.is_dir() for path in root.rglob("*.sh"))
    errors: list[str] = []
    for path in files:
        result = subprocess.run(
            ["bash", "-n", str(path)], text=True, capture_output=True, check=False
        )
        if result.returncode:
            errors.append(f"{path.relative_to(project_root)}: {result.stderr.strip()}")
    return {
        "name": "bash-syntax",
        "command": "bash -n scripts/**/*.sh trellis/**/*.sh",
        "status": "passed" if not errors else "failed",
        "exit_code": 0 if not errors else 1,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "stdout": f"checked {len(files)} shell files\n",
        "stderr": "\n".join(errors),
    }


def _default_quality_checks(project_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    checks: list[dict[str, Any]] = []
    skipped: list[str] = []
    validator = project_root / "scripts" / "validate-all-skills.py"
    if validator.is_file():
        checks.append(_run_argv("skill-validation", [sys.executable, str(validator)], project_root))
    else:
        skipped.append("skill-validation：缺少 scripts/validate-all-skills.py")
    if (project_root / "tests").is_dir():
        checks.append(
            _run_argv(
                "unit-tests",
                [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                project_root,
            )
        )
    else:
        skipped.append("unit-tests：缺少 tests 目录")
    checks.append(_shell_syntax_check(project_root))
    checks.append(_python_syntax_check(project_root))
    checks.append(_run_argv("git-diff-check", ["git", "diff", "--check"], project_root))
    return checks, skipped


def quality(
    project_root: Path,
    task_dir: Path | None,
    config: dict[str, Any],
    injected_checks: list[str],
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    checks: list[dict[str, Any]] = []
    skipped: list[str] = []
    if injected_checks:
        for item in injected_checks:
            if "=" not in item:
                issues.append(_issue("invalid_check", f"检查参数必须为 名称=命令：{item}"))
                continue
            name, command = item.split("=", 1)
            if not name.strip() or not command.strip():
                issues.append(_issue("invalid_check", f"检查参数必须为 名称=命令：{item}"))
                continue
            checks.append(_run_command(name.strip(), command.strip(), project_root))
    else:
        is_ai_workflow_package = (
            (project_root / "manifest.yaml").is_file()
            and (project_root / "skills").is_dir()
            and (project_root / "scripts" / "validate-all-skills.py").is_file()
        )
        if is_ai_workflow_package:
            checks, skipped = _default_quality_checks(project_root)
        else:
            issues.append(
                _issue(
                    "missing_quality_profile",
                    "非 AI-workflow 包项目必须使用 --check 名称=命令 显式提供必要质量检查",
                )
            )

    for check in checks:
        if check["status"] != "passed":
            issues.append(_issue("quality_check_failed", f"质量检查失败：{check['name']}"))
    if not checks and not any(issue["code"] == "missing_quality_profile" for issue in issues):
        issues.append(_issue("no_quality_checks", "没有可执行的质量检查"))

    result: dict[str, Any] = {
        "command": "quality",
        "ok": not issues,
        "issues": issues,
        "checks": checks,
    }
    report_skipped = bool(config.get("verification", {}).get("report_unexecuted_steps", True))
    if report_skipped:
        result["skipped"] = skipped

    if not issues and task_dir is not None:
        evidence_path = task_dir / "verification.json"
        evidence_checks = [
            {
                key: check[key]
                for key in ("name", "command", "status", "exit_code", "duration_ms")
            }
            for check in checks
        ]
        evidence = {
            "schema_version": 1,
            "status": "passed",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "git_head": git_head(project_root),
            "worktree_fingerprint": worktree_fingerprint(project_root, evidence_path),
            "checks": evidence_checks,
        }
        temporary = evidence_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(evidence_path)
        result["evidence"] = str(evidence_path.relative_to(project_root))
    return result


def completion(project_root: Path, task_dir: Path) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    status, status_issues = _task_status(task_dir)
    issues.extend(status_issues)
    if status is not None and status != "in_progress":
        issues.append(_issue("wrong_task_status", f"completion 要求 in_progress，当前为 {status}"))

    sections, prd_issues = _prd_sections(task_dir)
    issues.extend(prd_issues)
    boxes = CHECKBOX.findall(sections.get("acceptance_criteria", ""))
    if not boxes:
        issues.append(_issue("missing_acceptance_checkboxes", "验收标准必须包含复选框"))
    elif any(mark == " " for mark, _ in boxes):
        issues.append(_issue("unchecked_acceptance_criteria", "仍有未勾选的验收标准"))

    evidence_path = task_dir / "verification.json"
    evidence, evidence_error = _load_json(evidence_path)
    if evidence_error:
        issues.append(_issue("missing_verification", evidence_error))
    elif not isinstance(evidence, dict):
        issues.append(_issue("invalid_verification", "质量证据必须是 JSON 对象"))
    else:
        checks = evidence.get("checks")
        valid_checks = (
            isinstance(checks, list)
            and bool(checks)
            and all(
                isinstance(check, dict)
                and isinstance(check.get("name"), str)
                and check.get("status") == "passed"
                and check.get("exit_code") == 0
                for check in checks
            )
        )
        if evidence.get("schema_version") != 1 or evidence.get("status") != "passed" or not valid_checks:
            issues.append(
                _issue(
                    "invalid_verification",
                    "质量证据 schema、passed 状态或检查记录无效",
                )
            )
        else:
            if evidence.get("git_head") != git_head(project_root):
                issues.append(_issue("stale_head", "质量证据对应的 Git HEAD 已过期"))
            current_fingerprint = worktree_fingerprint(project_root, evidence_path)
            if evidence.get("worktree_fingerprint") != current_fingerprint:
                issues.append(_issue("stale_worktree", "质量证据对应的工作区已经变化"))
    return {"command": "completion", "ok": not issues, "issues": issues}


def _print_result(result: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    prefix = "OK" if result.get("ok") else "ERROR"
    print(f"{prefix}: {result.get('command')}")
    for issue in result.get("issues", []):
        print(f"  - [{issue['code']}] {issue['message']}")
    for check in result.get("checks", []):
        print(f"  - {check['status'].upper()}: {check['name']}")
    for skipped in result.get("skipped", []):
        print(f"  - SKIP: {skipped}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, default=PACKAGE_ROOT)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("text", "json"), default="text")
    subparsers = parser.add_subparsers(dest="command", required=True)

    readiness_parser = subparsers.add_parser("readiness")
    readiness_parser.add_argument("--task", required=True)
    readiness_parser.add_argument("--complex", action="store_true")

    quality_parser = subparsers.add_parser("quality")
    quality_parser.add_argument("--task")
    quality_parser.add_argument("--check", action="append", default=[])

    completion_parser = subparsers.add_parser("completion")
    completion_parser.add_argument("--task", required=True)
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    package_root = args.package_root.resolve()
    config, config_errors = load_effective_config(package_root, project_root)
    if config_errors:
        result = {
            "command": args.command,
            "ok": False,
            "issues": [
                _issue("invalid_effective_config", f"{path}: {error}")
                for path, error in config_errors
            ],
        }
        _print_result(result, args.format)
        return 1
    assert config is not None

    task_dir: Path | None = None
    if getattr(args, "task", None):
        task_dir, task_issues = _resolve_task(project_root, args.task)
        if task_issues:
            result = {"command": args.command, "ok": False, "issues": task_issues}
            _print_result(result, args.format)
            return 1

    if args.command == "readiness":
        assert task_dir is not None
        result = readiness(project_root, task_dir, config, args.complex)
    elif args.command == "quality":
        result = quality(project_root, task_dir, config, args.check)
    else:
        assert task_dir is not None
        result = completion(project_root, task_dir)
    _print_result(result, args.format)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
