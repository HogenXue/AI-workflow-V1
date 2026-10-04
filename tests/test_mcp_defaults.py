"""Default MCP endpoints and explicit URL overrides for every supported host."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://www.59005046.xyz:8102/mcp"
HOSTS = ("codex", "cursor", "claude", "minimax", "workbuddy")


class McpDefaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def merge(self, host: str, *args: str, input_text: str = "") -> tuple[subprocess.CompletedProcess[str], Path]:
        target = self.root / (host + (".toml" if host == "codex" else ".json"))
        fragments = ROOT / "trellis" / host / "mcp"
        if host != "codex":
            fragments /= "servers.json"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/lib/merge_host_mcp.py"),
             "--host", host, "--target", str(target), "--fragments", str(fragments), *args],
            input=input_text, text=True, capture_output=True, timeout=10,
        )
        return result, target

    def read_urls(self, host: str, path: Path) -> dict[str, str]:
        if host != "codex":
            return {name: entry["url"] for name, entry in json.loads(path.read_text())["mcpServers"].items() if "url" in entry}
        return dict(re.findall(r'\[mcp_servers\.(\w+)\]\s*\nurl = "([^"]+)"', path.read_text()))

    def test_templates_have_both_confirmed_default_urls(self) -> None:
        for host in HOSTS:
            with self.subTest(host=host):
                if host == "codex":
                    for server in ("mem0", "recallium"):
                        text = (ROOT / "trellis/codex/mcp" / f"{server}.toml").read_text()
                        self.assertIn(f'url = "{DEFAULT_URL}"', text)
                else:
                    servers = json.loads((ROOT / "trellis" / host / "mcp/servers.json").read_text())
                    self.assertEqual(servers["mem0"]["url"], DEFAULT_URL)
                    self.assertEqual(servers["recallium"]["url"], DEFAULT_URL)

    def test_install_without_override_uses_both_defaults(self) -> None:
        for host in HOSTS:
            with self.subTest(host=host):
                result, target = self.merge(host, "--policy", "keep")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(self.read_urls(host, target), {"mem0": DEFAULT_URL, "recallium": DEFAULT_URL})

    def test_explicit_override_changes_only_mem0(self) -> None:
        for host in HOSTS:
            with self.subTest(host=host):
                custom = "https://custom.example/memory"
                result, target = self.merge(host, "--policy", "keep", "--mem0-url", custom)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(self.read_urls(host, target), {"mem0": custom, "recallium": DEFAULT_URL})

    def seed_custom(self, host: str) -> dict[str, str]:
        urls = {"mem0": "https://old.example/mem0", "recallium": "https://old.example/recallium"}
        target = self.root / (host + (".toml" if host == "codex" else ".json"))
        if host == "codex":
            target.write_text("\n".join(f'[mcp_servers.{name}]\nurl = "{url}"\n' for name, url in urls.items()))
        else:
            target.write_text(json.dumps({"mcpServers": {name: {"url": url} for name, url in urls.items()}}))
        return urls

    def test_interactive_enter_keeps_existing_urls(self) -> None:
        for host in HOSTS:
            with self.subTest(host=host):
                urls = self.seed_custom(host)
                result, target = self.merge(host, "--policy", "overwrite", "--interactive", input_text="\n\n")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(self.read_urls(host, target), urls)

    def test_interactive_replace_uses_default_without_extra_url_prompt(self) -> None:
        for host in HOSTS:
            with self.subTest(host=host):
                self.seed_custom(host)
                result, target = self.merge(host, "--policy", "keep", "--interactive", input_text="y\ny\n")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(self.read_urls(host, target), {"mem0": DEFAULT_URL, "recallium": DEFAULT_URL})
                self.assertNotIn("replacement URL must not be empty", result.stderr)
