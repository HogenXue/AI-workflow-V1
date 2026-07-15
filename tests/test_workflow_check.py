import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "config" / "workflow_check.py"


class WorkflowCheckE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.project = Path(self.temp_dir.name) / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        subprocess.run(
            ["git", "config", "user.email", "workflow-check@example.test"],
            cwd=self.project,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Workflow Check"],
            cwd=self.project,
            check=True,
        )
        (self.project / "README.md").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.project, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.project, check=True)
        self.task = self.project / ".trellis" / "tasks" / "07-16-check"
        self.task.mkdir(parents=True)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--project-root",
                str(self.project),
                "--format",
                "json",
                *args,
            ],
            cwd=self.project,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def write_task(
        self,
        *,
        status: str = "planning",
        checked: bool = False,
        artifacts: bool = True,
        context: str = "curated",
    ) -> None:
        (self.task / "task.json").write_text(
            json.dumps({"status": status, "name": "check"}) + "\n",
            encoding="utf-8",
        )
        mark = "x" if checked else " "
        (self.task / "prd.md").write_text(
            "# Check\n\n"
            "## Goal\n\n可验证目标。\n\n"
            "## Requirements\n\n- 提供确定性门禁。\n\n"
            "## Acceptance Criteria\n\n"
            f"- [{mark}] 门禁返回可判定结果。\n",
            encoding="utf-8",
        )
        if artifacts:
            (self.task / "design.md").write_text("# 设计\n\n共享检查器。\n", encoding="utf-8")
            (self.task / "implement.md").write_text("# 计划\n\n- [ ] 实现。\n", encoding="utf-8")
        if context == "none":
            return
        if context == "seed":
            row = json.dumps({"_example": "seed"}) + "\n"
        else:
            spec = self.project / ".trellis" / "spec" / "scripts" / "index.md"
            spec.parent.mkdir(parents=True, exist_ok=True)
            spec.write_text("# Script spec\n", encoding="utf-8")
            row = json.dumps(
                {
                    "file": ".trellis/spec/scripts/index.md",
                    "reason": "测试上下文",
                },
                ensure_ascii=False,
            ) + "\n"
        (self.task / "implement.jsonl").write_text(row, encoding="utf-8")
        (self.task / "check.jsonl").write_text(row, encoding="utf-8")

    def task_argument(self) -> str:
        return str(self.task.relative_to(self.project))

    def test_readiness_reports_all_missing_complex_task_evidence_without_state_change(self) -> None:
        (self.task / "task.json").write_text(
            json.dumps({"status": "planning"}) + "\n", encoding="utf-8"
        )
        (self.task / "prd.md").write_text(
            "# Check\n\n## Goal\n\nTBD.\n\n## Requirements\n\n- TBD\n\n"
            "## Acceptance Criteria\n\n- [ ] TBD\n",
            encoding="utf-8",
        )
        seed = json.dumps({"_example": "seed"}) + "\n"
        (self.task / "implement.jsonl").write_text(seed, encoding="utf-8")
        (self.task / "check.jsonl").write_text(seed, encoding="utf-8")
        before = (self.task / "task.json").read_text(encoding="utf-8")

        result = self.run_cli("readiness", "--task", self.task_argument(), "--complex")

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        codes = {item["code"] for item in payload["issues"]}
        self.assertTrue(
            {
                "placeholder_goal",
                "placeholder_requirements",
                "placeholder_acceptance_criteria",
                "missing_design",
                "missing_implement",
                "uncurated_implement_context",
                "uncurated_check_context",
            }.issubset(codes)
        )
        self.assertEqual((self.task / "task.json").read_text(encoding="utf-8"), before)

    def test_readiness_passes_for_complete_complex_task(self) -> None:
        self.write_task()

        result = self.run_cli("readiness", "--task", self.task_argument(), "--complex")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_effective_config_can_disable_complex_artifact_requirement(self) -> None:
        self.write_task(artifacts=False, context="none")
        (self.project / "hogen-codex.yaml").write_text(
            "verification:\n  require_spec_for_complex_change: false\n",
            encoding="utf-8",
        )

        result = self.run_cli("readiness", "--task", self.task_argument(), "--complex")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_quality_without_task_is_side_effect_free(self) -> None:
        self.write_task(status="in_progress", checked=True)

        result = self.run_cli("quality", "--check", "smoke=true")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertFalse((self.task / "verification.json").exists())

    def test_non_package_project_requires_explicit_quality_checks(self) -> None:
        self.write_task(status="in_progress", checked=True)

        result = self.run_cli("quality", "--task", self.task_argument())

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "missing_quality_profile",
            {item["code"] for item in json.loads(result.stdout)["issues"]},
        )
        self.assertFalse((self.task / "verification.json").exists())

    def test_quality_and_completion_bind_fresh_evidence_without_changing_status(self) -> None:
        self.write_task(status="in_progress", checked=True)
        before = (self.task / "task.json").read_text(encoding="utf-8")

        quality = self.run_cli(
            "quality",
            "--task",
            self.task_argument(),
            "--check",
            "smoke=true",
        )

        self.assertEqual(quality.returncode, 0, quality.stderr + quality.stdout)
        evidence = json.loads((self.task / "verification.json").read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"], "passed")
        self.assertIn("worktree_fingerprint", evidence)
        self.assertEqual((self.task / "task.json").read_text(encoding="utf-8"), before)

        completion = self.run_cli("completion", "--task", self.task_argument())
        self.assertEqual(completion.returncode, 0, completion.stderr + completion.stdout)
        self.assertEqual((self.task / "task.json").read_text(encoding="utf-8"), before)

        (self.project / "changed-after-quality.txt").write_text("stale\n", encoding="utf-8")
        stale = self.run_cli("completion", "--task", self.task_argument())
        self.assertEqual(stale.returncode, 1)
        self.assertIn("stale_worktree", {item["code"] for item in json.loads(stale.stdout)["issues"]})

        (self.project / "changed-after-quality.txt").unlink()
        (self.project / "README.md").write_text("tracked change\n", encoding="utf-8")
        tracked_stale = self.run_cli("completion", "--task", self.task_argument())
        self.assertEqual(tracked_stale.returncode, 1)
        self.assertIn(
            "stale_worktree",
            {item["code"] for item in json.loads(tracked_stale.stdout)["issues"]},
        )

    def test_completion_rejects_unchecked_acceptance_criteria(self) -> None:
        self.write_task(status="in_progress", checked=False)
        quality = self.run_cli(
            "quality",
            "--task",
            self.task_argument(),
            "--check",
            "smoke=true",
        )
        self.assertEqual(quality.returncode, 0, quality.stderr + quality.stdout)

        result = self.run_cli("completion", "--task", self.task_argument())

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "unchecked_acceptance_criteria",
            {item["code"] for item in json.loads(result.stdout)["issues"]},
        )

    def test_completion_rejects_structurally_invalid_verification(self) -> None:
        self.write_task(status="in_progress", checked=True)
        quality = self.run_cli(
            "quality",
            "--task",
            self.task_argument(),
            "--check",
            "smoke=true",
        )
        self.assertEqual(quality.returncode, 0, quality.stderr + quality.stdout)
        evidence_path = self.task / "verification.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence["checks"] = []
        evidence_path.write_text(json.dumps(evidence) + "\n", encoding="utf-8")

        result = self.run_cli("completion", "--task", self.task_argument())

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "invalid_verification",
            {item["code"] for item in json.loads(result.stdout)["issues"]},
        )

    def test_full_planning_to_completion_lifecycle(self) -> None:
        self.write_task(status="planning", checked=False)
        ready = self.run_cli("readiness", "--task", self.task_argument(), "--complex")
        self.assertEqual(ready.returncode, 0, ready.stderr + ready.stdout)

        self.write_task(status="in_progress", checked=True)
        quality = self.run_cli(
            "quality",
            "--task",
            self.task_argument(),
            "--check",
            "smoke=true",
        )
        self.assertEqual(quality.returncode, 0, quality.stderr + quality.stdout)

        completed = self.run_cli("completion", "--task", self.task_argument())
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()
