"""Native MiniMax Code / WorkBuddy merge contracts, using isolated user homes."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NewHostMergeHarness:
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.env = dict(os.environ, HOME=str(self.home))
        for key in ("MINIMAX_DATA_DIR", "MAVIS_DATA_DIR", "CODEBUDDY_CONFIG_DIR"):
            self.env.pop(key, None)

    def run_merge(self, host: str, *args: str) -> subprocess.CompletedProcess[str]:
        argv = ([shutil.which("bash")] if self.ext == "sh" else
                [shutil.which("pwsh"), "-NoProfile", "-File"])
        return subprocess.run(
            [*argv, str(ROOT / "scripts" / f"install.{self.ext}"), f"{host}-merge", *args],
            env=self.env, cwd=self.root, text=True, capture_output=True, timeout=30,
        )

    def target(self, host: str) -> Path:
        return self.home / (".minimax/mcp.json" if host == "minimax" else ".codebuddy/.mcp.json")

    def test_native_transport_and_host_isolation(self) -> None:
        for host in ("minimax", "workbuddy"):
            with self.subTest(host=host):
                result = self.run_merge(host, "--mcp-keep", "--mem0-url", "https://memory.example/mcp")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                servers = json.loads(self.target(host).read_text())["mcpServers"]
                self.assertEqual(servers["gitnexus"]["type"], "stdio")
                self.assertEqual(servers["recallium"]["type"], "http")
                self.assertEqual(servers["mem0"]["url"], "https://memory.example/mcp")
                self.assertEqual(servers["mem0"]["type"], "http")
                self.assertTrue(all("transport" not in value for value in servers.values()))
        for path in (".codex", ".claude", ".cursor", ".agents"):
            self.assertFalse((self.home / path).exists())
        self.assertFalse((self.root / ".codebuddy").exists())

    def test_keep_and_overwrite_preserve_other_keys_and_exact_backup(self) -> None:
        for host in ("minimax", "workbuddy"):
            with self.subTest(host=host):
                target = self.target(host)
                target.parent.mkdir()
                original = '{"other":true,"mcpServers":{"custom":{"command":"custom"},"recallium":{"url":"https://old.example/mcp","headers":{"X-Test":"kept"}}}}\n'
                target.write_text(original)
                result = self.run_merge(host, "--mcp-keep")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                data = json.loads(target.read_text())
                self.assertEqual(data["mcpServers"]["recallium"]["headers"], {"X-Test": "kept"})
                self.assertTrue(data["other"])
                self.assertEqual(data["mcpServers"]["custom"], {"command": "custom"})
                backups = list((target.parent / ".ai-workflow-backups").glob("*.bak"))
                self.assertEqual(len(backups), 1)
                self.assertEqual(backups[0].read_text(), original)
                result = self.run_merge(host, "--mcp-overwrite")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                data = json.loads(target.read_text())
                self.assertNotEqual(data["mcpServers"]["recallium"]["url"], "https://old.example/mcp")
                self.assertTrue(data["other"])
                self.assertIn("custom", data["mcpServers"])
                self.assertEqual(len(list((target.parent / ".ai-workflow-backups").glob("*.bak"))), 2)

    def test_preview_creates_no_directories_and_preserves_existing_file(self) -> None:
        for host in ("minimax", "workbuddy"):
            with self.subTest(host=host):
                result = self.run_merge(host, "--dry-run", "--mcp-keep")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertIn("DRY-RUN:", result.stdout)
                self.assertFalse(self.target(host).parent.exists())
                target = self.target(host)
                target.parent.mkdir()
                original = '{"keep":"exact"}\n'
                target.write_text(original)
                result = self.run_merge(host, "--dry-run", "--mcp-keep")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(target.read_text(), original)
                self.assertFalse((target.parent / ".ai-workflow-backups").exists())

    def test_conflict_and_invalid_inputs_do_not_overwrite(self) -> None:
        for host in ("minimax", "workbuddy"):
            target = self.target(host)
            target.parent.mkdir()
            for original in ('not-json', '[]', '{"mcpServers":[]}', '{"mcpServers":{"gitnexus":{"command":"custom"}}}'):
                with self.subTest(host=host, original=original):
                    target.write_text(original)
                    result = self.run_merge(host)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertEqual(target.read_text(), original)
            target.write_text('{"user":"kept"}')
            result = self.run_merge(host, "--mcp-overwrite", "--mem0-url", "http://public.example/mcp")
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual(target.read_text(), '{"user":"kept"}')

    def test_directory_targets_and_package_fragment_are_rejected(self) -> None:
        for host in ("minimax", "workbuddy"):
            with self.subTest(host=host):
                directory = self.root / host
                directory.mkdir()
                result = self.run_merge(host, "--mcp-file", str(directory))
                self.assertNotEqual(result.returncode, 0, result.stdout)
                fragment = ROOT / "trellis" / host / "mcp" / "servers.json"
                self.assertTrue(fragment.is_file())
                original = fragment.read_bytes()
                result = self.run_merge(host, "--mcp-file", str(fragment), "--mcp-overwrite")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(fragment.read_bytes(), original)

    def test_home_overrides_and_explicit_mcp_file(self) -> None:
        for host, env_key in (("minimax", "MINIMAX_DATA_DIR"), ("workbuddy", "CODEBUDDY_CONFIG_DIR")):
            with self.subTest(host=host):
                custom = self.root / (host + " custom")
                self.env[env_key] = str(custom)
                result = self.run_merge(host, "--mcp-keep")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                name = "mcp.json" if host == "minimax" else ".mcp.json"
                self.assertTrue((custom / name).is_file())
                explicit = self.root / (host + "-explicit.json")
                result = self.run_merge(host, f"--{host}-home", str(self.root / "other"),
                                        "--mcp-file", str(explicit), "--mcp-keep")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertTrue(explicit.is_file())
                self.assertFalse(self.target(host).exists())

    def test_workbuddy_legacy_precedence_and_minimax_nested_file(self) -> None:
        legacy = self.home / ".codebuddy.json"
        legacy.write_text('{"legacy":"kept"}')
        result = self.run_merge("workbuddy", "--mcp-keep")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(legacy.read_text())["legacy"])
        self.assertFalse(self.target("workbuddy").exists())
        old = self.home / ".codebuddy/mcp.json"
        old.write_text('{"old":"kept"}')
        legacy_before = legacy.read_bytes()
        result = self.run_merge("workbuddy", "--mcp-keep")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(old.read_text())["old"])
        self.assertEqual(legacy.read_bytes(), legacy_before)
        preferred = self.target("workbuddy")
        preferred.write_text('{"preferred":true}')
        old_before = old.read_bytes()
        result = self.run_merge("workbuddy", "--mcp-keep")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(preferred.read_text())["preferred"])
        self.assertEqual(old.read_bytes(), old_before)
        nested = self.home / ".minimax/mcp/mcp.json"
        nested.parent.mkdir(parents=True)
        nested.write_text('{"nested":true}')
        result = self.run_merge("minimax", "--mcp-keep")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(nested.read_text())["nested"])
        self.assertFalse(self.target("minimax").exists())

    def test_invalid_options_and_backup_failure_stop_without_writes(self) -> None:
        for host in ("minimax", "workbuddy"):
            for args in (("--mcp-file",), ("--dry-run", "--apply"), (f"--{host}-home", "--mcp-keep")):
                with self.subTest(host=host, args=args):
                    result = self.run_merge(host, *args)
                    self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                    self.assertFalse(self.target(host).parent.exists())
            target = self.target(host)
            target.parent.mkdir()
            target.write_text('{"keep":true}')
            blocked = self.root / (host + "-blocked")
            blocked.write_text("not a directory")
            result = self.run_merge(host, "--mcp-overwrite", "--backup-dir", str(blocked / "backup"))
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertEqual(target.read_text(), '{"keep":true}')

    def test_symlink_targets_are_rejected_without_touching_referent(self) -> None:
        for host in ("minimax", "workbuddy"):
            with self.subTest(host=host):
                target = self.target(host)
                target.parent.mkdir()
                referent = self.root / (host + "-referent.json")
                referent.write_text('{"user":true}')
                try:
                    target.symlink_to(referent)
                except OSError as error:
                    self.skipTest(f"Symlinks unavailable: {error}")
                result = self.run_merge(host, "--mcp-overwrite")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertTrue(target.is_symlink())
                self.assertEqual(referent.read_text(), '{"user":true}')

    def test_real_profile_installs_skills_defaults_and_rules_in_temporary_home(self) -> None:
        entry = ROOT / "scripts" / f"install.{self.ext}"
        source = entry.read_text()
        if self.ext == "sh":
            source = source.split("if (($# == 0)); then", 1)[0]
            source = source.replace(
                'script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"',
                'script_dir=' + shlex.quote(str(ROOT / "scripts")),
                1,
            )
            source += "\ninstall_lib_prompt_yn() { return 1; }\ninstall_profile_minimax ''\ninstall_profile_workbuddy ''\n"
            argv = [shutil.which("bash")]
        else:
            source = source.split("# --- entry ---", 1)[0]
            scripts = str(ROOT / "scripts").replace("'", "''")
            source = f"$script:profileScripts = '{scripts}'\n" + source.replace("$PSScriptRoot", "$script:profileScripts")
            source += "\nfunction Test-InstallLibStdinTty { return $false }\nInstall-ProfileMinimax\nInstall-ProfileWorkBuddy\n"
            argv = [shutil.which("pwsh"), "-NoProfile", "-File"]
        harness = self.root / f"real-profiles.{self.ext}"
        harness.write_text(source)
        minimax = self.home / ".minimax"
        minimax.mkdir()
        (minimax / "config.yaml").write_text("provider: preserved\n")
        workbuddy = self.home / ".codebuddy"
        workbuddy.mkdir()
        (workbuddy / "settings.json").write_text('{"permissions":"preserved"}')
        result = subprocess.run([*argv, str(harness)], env=self.env, cwd=self.root,
                                text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        for parent, document in ((minimax, "AGENTS.md"), (workbuddy, "CODEBUDDY.md")):
            self.assertEqual((parent / document).read_bytes(), (ROOT / "agents/AGENTS.global.md").read_bytes())
            self.assertEqual(len(list((parent / "skills").glob("*/SKILL.md"))), 7)
            self.assertTrue((parent / "config/defaults.yaml").is_file())
            self.assertFalse((parent / "config.toml").exists())
            self.assertFalse((parent / "hooks.json").exists())
        self.assertEqual((minimax / "config.yaml").read_text(), "provider: preserved\n")
        self.assertEqual((workbuddy / "settings.json").read_text(), '{"permissions":"preserved"}')
        self.assertTrue(self.target("minimax").is_file())
        self.assertTrue(self.target("workbuddy").is_file())
        for name in (".codex", ".cursor", ".claude", ".agents", ".codebuddy", ".minimax"):
            self.assertFalse((self.root / name).exists())


@unittest.skipUnless(shutil.which("bash"), "Bash required")
class BashNewHostMergeTests(NewHostMergeHarness, unittest.TestCase):
    ext = "sh"


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7+ required")
class PowerShellNewHostMergeTests(NewHostMergeHarness, unittest.TestCase):
    ext = "ps1"
