import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "config" / "effective_config.py"


class EffectiveConfigCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.package = self.root / "package"
        self.project = self.root / "project"
        (self.package / "config").mkdir(parents=True)
        self.project.mkdir()
        (self.package / "config" / "defaults.yaml").write_text(
            "language: zh-CN\n"
            "change_policy:\n"
            "  minimal_change: true\n"
            "  preserve_dirty_worktree: true\n",
            encoding="utf-8",
        )
        (self.package / "config" / "project-config.schema.yaml").write_text(
            "type: mapping\n"
            "allowed_keys:\n"
            "  language:\n"
            "    type: string\n"
            "  change_policy:\n"
            "    type: mapping\n"
            "    allowed_keys:\n"
            "      minimal_change:\n"
            "        type: boolean\n"
            "      preserve_dirty_worktree:\n"
            "        type: boolean\n",
            encoding="utf-8",
        )

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--package-root",
                str(self.package),
                "--project-root",
                str(self.project),
                *args,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_outputs_merged_configuration_as_stable_json(self) -> None:
        (self.project / "hogen-codex.yaml").write_text(
            "change_policy:\n  minimal_change: false\n",
            encoding="utf-8",
        )

        result = self.run_cli()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "language": "zh-CN",
                "change_policy": {
                    "minimal_change": False,
                    "preserve_dirty_worktree": True,
                },
            },
        )
        self.assertTrue(result.stdout.endswith("\n"))

    def test_get_outputs_one_dotted_configuration_value(self) -> None:
        (self.project / "hogen-codex.yaml").write_text(
            "change_policy:\n  minimal_change: false\n",
            encoding="utf-8",
        )

        result = self.run_cli("--get", "change_policy.minimal_change")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "false\n")

    def test_unknown_dotted_key_fails_loudly(self) -> None:
        result = self.run_cli("--get", "change_policy.unknown")

        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown configuration key", result.stderr)

    def test_consumer_registry_must_cover_every_schema_leaf(self) -> None:
        (self.package / "config" / "consumers.yaml").write_text(
            "consumers:\n"
            "  language: [agents]\n"
            "  change_policy.minimal_change: [karpathy-guidelines-zh]\n",
            encoding="utf-8",
        )

        result = self.run_cli("--validate-consumers")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "missing configuration consumer: change_policy.preserve_dirty_worktree",
            result.stderr,
        )

    def test_package_consumer_registry_is_complete(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "--validate-consumers"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_pyyaml_has_actionable_runtime_error(self) -> None:
        result = subprocess.run(
            [sys.executable, "-S", str(CLI)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("PyYAML is required", result.stderr)
        self.assertIn("pip install -r requirements-dev.txt", result.stderr)


if __name__ == "__main__":
    unittest.main()
