"""Native MCP syntax regression tests; every write stays in a temporary directory."""
from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/lib/merge_host_mcp.py"
OLD_URL = "https://old.example/mcp"
NEW_URL = "https://new.example/mcp"


class NativeMcpFormatsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="native mcp ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "config.toml"
        self.fragments = self.root / "fragments"
        self.fragments.mkdir()
        (self.fragments / "mem0.toml").write_text(
            f'[mcp_servers.mem0]\nurl = "{NEW_URL}"\n', encoding="utf-8"
        )

    def merge(self, *, host="codex", policy="keep", extra=()):
        fragments = self.fragments if host == "codex" else self.fragments / "servers.json"
        return subprocess.run(
            [sys.executable, str(HELPER), "--host", host, "--target", str(self.target),
             "--fragments", str(fragments), "--policy", policy, *extra],
            cwd=self.root, text=True, capture_output=True, timeout=15, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipIf(tomllib is None, "tomllib or tomli required for TOML assertions")
    def test_keep_recognizes_native_toml_representations_without_changing_bytes(self):
        forms = (
            f'[mcp_servers.mem0] # personal endpoint\nurl = "{OLD_URL}"\n',
            f'[mcp_servers."mem0"]\nurl = "{OLD_URL}"\n',
            f"  [ mcp_servers . 'mem0' ] # quoted key\nurl = '{OLD_URL}'\n",
            f'mcp_servers.mem0.url = "{OLD_URL}"\n',
            f'[mcp_servers]\nmem0 = {{ url = "{OLD_URL}" }}\n',
            f'mcp_servers = {{ mem0 = {{ url = "{OLD_URL}" }} }}\n',
            '[mcp_servers.mem0.http_headers]\nX-Test = "kept"\n',
        )
        for original in forms:
            with self.subTest(original=original):
                before = original.replace("\n", "\r\n").encode()
                self.target.write_bytes(before)
                self.assert_success(self.merge())
                self.assertEqual(self.target.read_bytes(), before)

    @unittest.skipIf(tomllib is None, "tomllib or tomli required for TOML assertions")
    def test_overwrite_native_tables_dotted_and_server_inline_preserves_other_data(self):
        forms = (
            f'[mcp_servers.mem0] # personal endpoint\nurl = "{OLD_URL}"\n',
            f'[mcp_servers."mem0"]\nurl = "{OLD_URL}"\n',
            f"  [ mcp_servers . 'mem0' ]\nurl = '{OLD_URL}'\n",
            f'mcp_servers.mem0.url = "{OLD_URL}"\n',
            f'[mcp_servers]\nmem0 = {{ url = "{OLD_URL}" }}\n',
            f'[mcp_servers.mem0]\nurl = "{OLD_URL}"',
        )
        for form in forms:
            with self.subTest(form=form):
                original = ('model = "keep-model"\n# preserve this note\n' + form + '\n'
                            '[mcp_servers.mem0.http_headers]\nAuthorization = "fixture-only"\n'
                            '[mcp_servers.custom]\ncommand = "custom-tool"\n')
                # Inline server tables are closed; do not append a child table to them.
                if "mem0 = {" in form:
                    original = ('model = "keep-model"\n# preserve this note\n' + form + '\n'
                                '[mcp_servers.custom]\ncommand = "custom-tool"\n')
                before = tomllib.loads(original)
                self.target.write_text(original, encoding="utf-8")
                self.assert_success(self.merge(policy="overwrite"))
                expected = before
                expected["mcp_servers"]["mem0"]["url"] = NEW_URL
                actual = self.target.read_text(encoding="utf-8")
                self.assertEqual(tomllib.loads(actual), expected)
                self.assertIn('# preserve this note\n', actual)
                self.assertIn('[mcp_servers.custom]\ncommand = "custom-tool"\n', actual)

    @unittest.skipIf(tomllib is None, "tomllib or tomli required for TOML assertions")
    def test_multiline_strings_containing_fake_headers_are_preserved(self):
        original = ('note = """\n[mcp_servers.mem0]\nurl = "fake"\n"""\n'
                    f'[mcp_servers.mem0]\nurl = "{OLD_URL}"\n'
                    'message = \'\'\'\n[not.a.real.table]\n\'\'\'\n'
                    'timeout = 42\n')
        self.target.write_text(original, encoding="utf-8")
        self.assert_success(self.merge(policy="overwrite"))
        expected = tomllib.loads(original)
        expected['mcp_servers']['mem0']['url'] = NEW_URL
        self.assertEqual(tomllib.loads(self.target.read_text()), expected)

    def test_closed_inline_parent_rejects_overwrite_without_mutation(self):
        original = f'mcp_servers = {{ mem0 = {{ url = "{OLD_URL}" }}, custom = {{ command = "keep" }} }}\n'
        self.target.write_text(original, encoding="utf-8")
        result = self.merge(policy="overwrite")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('inline', result.stderr.lower())
        self.assertEqual(self.target.read_text(), original)

    def test_closed_inline_parent_rejects_add_without_mutation(self):
        original = 'mcp_servers = { custom = { command = "keep" } }\n'
        self.target.write_text(original, encoding="utf-8")
        result = self.merge()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.target.read_text(), original)

    def test_invalid_toml_or_mcp_shape_is_rejected_before_mutation(self):
        for original in ('broken = [\n', 'mcp_servers = "not a table"\n',
                         '[mcp_servers]\nmem0 = "not a server object"\n'):
            with self.subTest(original=original):
                self.target.write_text(original, encoding="utf-8")
                result = self.merge(policy="overwrite")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(self.target.read_text(), original)

    def test_later_invalid_fragment_does_not_publish_earlier_changes(self):
        original = 'model = "kept"\n'
        self.target.write_text(original)
        (self.fragments / 'gitnexus.toml').write_text('[mcp_servers.gitnexus]\ncommand = "ok"\n')
        (self.fragments / 'mem0.toml').write_text('[mcp_servers.mem0]\nurl = "https://new.example"\nbroken = [\n')
        result = self.merge()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.target.read_text(), original)

    def test_atomic_update_preserves_private_mode_and_existing_temp_sentinel(self):
        self.target.write_text('model = "kept"\n')
        self.target.chmod(0o600)
        sentinel = self.target.with_suffix('.toml.tmp')
        sentinel.write_text('unrelated temporary file')
        self.assert_success(self.merge())
        if os.name != 'nt':
            self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)
        self.assertEqual(sentinel.read_text(), 'unrelated temporary file')

    def test_unavailable_toml_parser_fails_explicitly_before_write(self):
        spec = importlib.util.spec_from_file_location("native_mcp_helper", HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.target.write_text('model = "kept"\n')
        with patch.object(module, "tomllib", None):
            with self.assertRaisesRegex(ValueError, "Python 3.11.*tomli"):
                module.merge_codex_toml(self.target, self.fragments, 'keep', None, False, False)
        self.assertEqual(self.target.read_text(), 'model = "kept"\n')

    def test_failed_atomic_publish_preserves_original_and_removes_private_staging(self):
        spec = importlib.util.spec_from_file_location("native_mcp_helper", HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.target.write_text('model = "kept"\n')
        with patch.object(module.Path, "replace", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError):
                module.merge_codex_toml(self.target, self.fragments, 'keep', None, False, False)
        self.assertEqual(self.target.read_text(), 'model = "kept"\n')
        self.assertEqual(list(self.root.glob('.*.tmp')), [])

    def seed_json(self, text):
        self.target = self.root / '.mcp.json'
        self.target.write_text(text, encoding='utf-8')
        (self.fragments / 'servers.json').write_text(
            json.dumps({'mem0': {'type': 'http', 'url': NEW_URL}}), encoding='utf-8')

    def test_workbuddy_jsonc_keep_is_byte_exact(self):
        original = ('\ufeff{\r\n  // local setting\r\n  "note": "https://host/path//literal/*data*/",\r\n'
                    '  "mcpServers": {"mem0": {"type": "http", "url": "' + OLD_URL + '",},},\r\n}\r\n')
        self.seed_json(original)
        before = self.target.read_bytes()
        self.assert_success(self.merge(host='workbuddy'))
        self.assertEqual(self.target.read_bytes(), before)

    def test_workbuddy_jsonc_update_preserves_other_values_and_server_fields(self):
        original = ('{/* block */ "note":"escaped \\\" // still string",'
                    '"path":"C:\\\\tools\\\\x", "mcpServers":{'
                    '"custom":{"command":"keep/*literal*/",},'
                    '"mem0":{"url":"' + OLD_URL + '","headers":{"X-Key":"fixture"},},},}')
        self.seed_json(original)
        self.assert_success(self.merge(host='workbuddy', policy='overwrite'))
        data = json.loads(self.target.read_text())
        self.assertEqual(data['note'], 'escaped " // still string')
        self.assertEqual(data['path'], 'C:\\tools\\x')
        self.assertEqual(data['mcpServers']['custom'], {'command':'keep/*literal*/'})
        self.assertEqual(data['mcpServers']['mem0'], {'type':'http','url':NEW_URL,'headers':{'X-Key':'fixture'}})

    def test_workbuddy_jsonc_add_preserves_existing_servers(self):
        self.seed_json('{"mcpServers": {"custom":{"command":"keep"},},/* end */}')
        self.assert_success(self.merge(host='workbuddy'))
        self.assertEqual(json.loads(self.target.read_text())['mcpServers']['custom'], {'command':'keep'})

    def test_invalid_jsonc_does_not_mutate(self):
        for original in ('{"mcpServers":{}} /* unterminated', '{"mcpServers":{},,}',
                         '{"mcpServers":{},"mcpServers":{}}', '{"mcpServers":[]}'):
            with self.subTest(original=original):
                self.seed_json(original)
                result = self.merge(host='workbuddy',policy='overwrite')
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(self.target.read_text(), original)

    def test_other_hosts_retain_strict_json_contract(self):
        original = '{"mcpServers":{}, // comment\n}'
        for host in ('cursor','claude','minimax'):
            with self.subTest(host=host):
                self.seed_json(original)
                result = self.merge(host=host)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.target.read_text(),original)


if __name__ == '__main__':
    unittest.main()
