"""Simulate package managers; no real package install or network access is used."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("install_dependencies", ROOT / "scripts/lib/install_dependencies.py")
DEPS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DEPS)


class DependencyBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.bin = self.home / "npm" / ("" if os.name == "nt" else "bin")
        self.env_dir = self.home / ".agents/tools/graphify"
        self.env_bin = self.env_dir / ("Scripts" if os.name == "nt" else "bin")
        self.executables = {"node": "fake-node", "npm.cmd": "fake-npm", "npm": "fake-npm"}
        self.calls = []
        self.failure = ""
        self.node_version = "v22.20.0\n"
        self.npm_prefix = str(self.home / "npm") + "\n"
        self.hide_installed_cli = False
        self.prefix_recovers_tools = False
        for patcher in (patch.dict(os.environ, {"PATH": "original-path"}),
                        patch.object(DEPS.shutil, "which", side_effect=self.executables.get),
                        patch.object(DEPS.subprocess, "run", side_effect=self.run_command)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_command(self, argv, **kwargs):
        self.calls.append(argv)
        output = ""
        code = 0
        if argv == ["fake-node", "--version"]:
            output = self.node_version
        elif argv == ["fake-npm", "prefix", "--global"]:
            output = self.npm_prefix
            if self.prefix_recovers_tools:
                self.executables.update({"gitnexus": "recovered-gitnexus", "trellis": "recovered-trellis"})
        elif argv[0] == "fake-npm" and "install" in argv:
            if self.failure == "npm":
                code = 13
            elif not self.hide_installed_cli:
                tool = "gitnexus" if argv[-1].startswith("gitnexus") else "trellis"
                self.bin.mkdir(parents=True, exist_ok=True)
                target = self.bin / tool
                target.write_text("fake cli", encoding="utf-8")
                self.executables[tool] = str(target)
        elif argv[:3] == [sys.executable, "-m", "venv"]:
            self.env_bin.mkdir(parents=True)
            (self.env_dir / "pyvenv.cfg").write_text("home = fake\n", encoding="utf-8")
            (self.env_bin / ("python.exe" if os.name == "nt" else "python")).touch()
        elif argv[-4:] == ["-m", "pip", "install", "graphifyy"]:
            if self.failure == "pip":
                code = 17
            else:
                (self.env_bin / ("graphify.exe" if os.name == "nt" else "graphify")).touch()
        elif self.failure == "probe" and argv[0] == "existing-graphify":
            code = 19
        return subprocess.CompletedProcess(argv, code, stdout=output, stderr="")

    def keep_npm_tools(self) -> None:
        self.executables.update({"gitnexus": "existing-gitnexus", "trellis": "existing-trellis"})

    def test_dry_run_does_not_execute_commands_or_create_environment(self) -> None:
        DEPS.bootstrap(self.home, apply=False, path_file=self.home / "paths.txt")
        self.assertEqual(self.calls, [])
        self.assertFalse(self.env_dir.exists())
        self.assertFalse((self.home / "paths.txt").exists())

    def test_existing_tools_are_verified_without_installs(self) -> None:
        self.keep_npm_tools()
        self.executables["graphify"] = "existing-graphify"
        DEPS.bootstrap(self.home, apply=True)
        self.assertEqual(len(self.calls), 3)
        self.assertFalse(any("install" in call or "venv" in call for call in self.calls))

    def test_missing_tools_are_installed_and_paths_reported(self) -> None:
        path_file = self.home / "paths.txt"
        DEPS.bootstrap(self.home, apply=True, path_file=path_file)
        npm_installs = [call for call in self.calls if call[0] == "fake-npm" and "install" in call]
        self.assertEqual([call[-1] for call in npm_installs], ["gitnexus@latest", "@mindfoldhq/trellis@latest"])
        self.assertTrue(all("--global" in call and "--engine-strict" in call for call in npm_installs))
        self.assertTrue(any(call[-4:] == ["-m", "pip", "install", "graphifyy"] for call in self.calls))
        self.assertIn(str(self.env_bin), path_file.read_text(encoding="utf-8").splitlines())
        self.assertIn(str(self.bin), path_file.read_text(encoding="utf-8").splitlines())

    def test_missing_runtime_fails_before_any_install(self) -> None:
        self.executables.clear()
        with self.assertRaisesRegex(DEPS.InstallError, "Node.js/npm"):
            DEPS.bootstrap(self.home, apply=True)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.env_dir.exists())

    def test_failed_npm_stops_remaining_installs_and_preserves_exit_code(self) -> None:
        self.failure = "npm"
        with self.assertRaises(DEPS.InstallError) as failure:
            DEPS.bootstrap(self.home, apply=True)
        self.assertEqual(failure.exception.status, 13)
        self.assertFalse(self.env_dir.exists())
        self.assertFalse(any("@mindfoldhq/trellis@latest" in call for call in self.calls))

    def test_unsupported_node_fails_before_installing(self) -> None:
        self.node_version = "v16.20.0\n"
        with self.assertRaisesRegex(DEPS.InstallError, "Node.js 18"):
            DEPS.bootstrap(self.home, apply=True)
        self.assertFalse(any("install" in call for call in self.calls))
        self.assertFalse(self.env_dir.exists())

    def test_invalid_npm_prefix_fails_before_installing(self) -> None:
        self.npm_prefix = ""
        with self.assertRaisesRegex(DEPS.InstallError, "invalid global prefix"):
            DEPS.bootstrap(self.home, apply=True)
        self.assertFalse(any("install" in call for call in self.calls))

    def test_success_without_cli_is_not_reported_as_success(self) -> None:
        self.hide_installed_cli = True
        with self.assertRaisesRegex(DEPS.InstallError, "CLI is unavailable"):
            DEPS.bootstrap(self.home, apply=True)
        self.assertFalse(self.env_dir.exists())

    def test_failed_graphify_pip_preserves_exit_code_without_path_report(self) -> None:
        self.keep_npm_tools()
        self.failure = "pip"
        with self.assertRaises(DEPS.InstallError) as failure:
            DEPS.bootstrap(self.home, apply=True, path_file=self.home / "paths.txt")
        self.assertEqual(failure.exception.status, 17)
        self.assertFalse((self.home / "paths.txt").exists())

    def test_managed_graphify_is_reused_when_missing_from_path(self) -> None:
        self.keep_npm_tools()
        self.env_bin.mkdir(parents=True)
        (self.env_bin / ("graphify.exe" if os.name == "nt" else "graphify")).touch()
        DEPS.bootstrap(self.home, apply=True)
        self.assertFalse(any("install" in call or "venv" in call for call in self.calls))

    def test_arbitrary_managed_directory_is_not_overwritten(self) -> None:
        self.env_dir.mkdir(parents=True)
        sentinel = self.env_dir / "user-owned.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(DEPS.InstallError, "not a virtual environment"):
            DEPS.bootstrap(self.home, apply=True)
        self.assertEqual(self.calls, [])
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_broken_existing_tool_fails_without_installing_replacements(self) -> None:
        self.executables["graphify"] = "existing-graphify"
        self.failure = "probe"
        with self.assertRaises(DEPS.InstallError) as failure:
            DEPS.bootstrap(self.home, apply=True)
        self.assertEqual(failure.exception.status, 19)
        self.assertFalse(any("install" in call for call in self.calls))

    def test_npm_prefix_path_recovery_avoids_reinstallation(self) -> None:
        self.executables["graphify"] = "existing-graphify"
        self.prefix_recovers_tools = True
        DEPS.bootstrap(self.home, apply=True)
        self.assertFalse(any("install" in call for call in self.calls))


if __name__ == "__main__":
    unittest.main()
