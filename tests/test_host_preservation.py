"""Host installers preserve unrelated configuration and never write during preview."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOST_OVERRIDES = ('CODEX_HOME', 'CURSOR_MCP_FILE', 'CLAUDE_MCP_FILE', 'MINIMAX_DATA_DIR',
                  'MAVIS_DATA_DIR', 'CODEBUDDY_CONFIG_DIR', 'TRELLIS_TASK_DIR', 'TRELLIS_SESSION_ID')


class HostPreservationMixin:
    suffix = '.sh'
    shell = 'bash'

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='host preserve ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home'
        self.home.mkdir()
        self.env = {k: v for k, v in os.environ.items() if k not in HOST_OVERRIDES}
        self.env.update(HOME=str(self.home), USERPROFILE=str(self.home), PYTHONDONTWRITEBYTECODE='1')
        self.project = self.root / 'project'
        self.project.mkdir()

    def run_install(self, host, *args):
        command = [self.shell]
        if self.suffix == '.ps1':
            command += ['-NoLogo', '-NoProfile', '-File']
        command += [str(ROOT / f'scripts/install-{host}{self.suffix}'), *map(str, args)]
        return subprocess.run(command, cwd=self.project, env=self.env, capture_output=True, text=True)

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_five_host_previews_create_no_directories(self):
        for host in ('codex', 'cursor', 'claude', 'minimax', 'workbuddy'):
            with self.subTest(host=host):
                result = self.run_install(host + '-merge', '--dry-run', '--mcp-keep')
                self.assert_ok(result)
                self.assertEqual(list(self.home.iterdir()), [], result.stdout)
        result = self.run_install('agents', '--dry-run')
        self.assert_ok(result)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_agents_preserve_disabled_hooks_and_report_effective_override(self):
        codex = self.home / '.codex'
        codex.mkdir()
        before = b'# personal\n[features]\nhooks = false\n[other]\nvalue = "keep"\n'
        config = codex / 'config.toml'
        config.write_bytes(before)
        override = codex / 'AGENTS.override.md'
        override.write_text('Personal override\n')
        result = self.run_install('agents', '--apply')
        self.assert_ok(result)
        self.assertEqual(config.read_bytes(), before)
        self.assertEqual(override.read_text(), 'Personal override\n')
        self.assertIn('effective global instruction file', result.stdout)
        self.assertIn('remains shadowed', result.stdout)
        self.assertEqual((codex / 'AGENTS.md').read_bytes(), (ROOT / 'agents/AGENTS.global.md').read_bytes())

    def test_agents_do_not_create_config_to_enable_hooks(self):
        self.assert_ok(self.run_install('agents', '--apply'))
        self.assertFalse((self.home / '.codex/config.toml').exists())

    def test_codex_merge_keeps_foreign_handlers_inside_managed_group(self):
        codex = self.home / '.codex'
        hooks = codex / 'hooks'
        hooks.mkdir(parents=True)
        (hooks / 'foreign.py').write_bytes(b'# keep foreign bytes\n')
        foreign = {'type': 'command', 'command': 'echo foreign', 'timeout': 7}
        group = {'matcher': 'resume', 'userMetadata': True, 'hooks': [
            {'type': 'command', 'command': 'bash old-managed.sh', 'statusMessage': 'Trellis/Codex session context'},
            foreign,
        ]}
        keep_event = [{'hooks': [{'type': 'command', 'command': 'echo stop'}]}]
        original = {'description': 'personal', 'hooks': {'SessionStart': [group], 'Stop': keep_event}}
        (codex / 'hooks.json').write_text(json.dumps(original))
        for _ in range(2):
            result = self.run_install('codex-merge', '--apply', '--mcp-keep', '--replace')
            self.assert_ok(result)
            self.assertIn('does not grant native hook trust', result.stdout)
        current = json.loads((codex / 'hooks.json').read_text())
        self.assertEqual(current['description'], 'personal')
        self.assertEqual(current['hooks']['Stop'], keep_event)
        self.assertEqual(current['hooks']['SessionStart'][0], {**group, 'hooks': [foreign]})
        self.assertEqual(len(current['hooks']['SessionStart']), 2)
        self.assertEqual((hooks / 'foreign.py').read_bytes(), b'# keep foreign bytes\n')
        self.assertTrue((hooks / 'session-start.py').is_file())
        self.assertTrue((hooks / 'session-start.sh').is_file())

    def test_cursor_merge_keeps_foreign_hooks_and_scripts(self):
        cursor = self.project / '.cursor'
        hooks = cursor / 'hooks'
        hooks.mkdir(parents=True)
        (hooks / 'foreign.py').write_text('personal\n')
        template = json.loads((ROOT / 'trellis/cursor/hooks.json').read_text())
        foreign = {'command': 'echo personal', 'timeout': 9}
        template['hooks']['sessionStart'].append(foreign)
        template['hooks']['stop'] = [{'command': 'echo finished'}]
        template['extra'] = {'personal': True}
        (cursor / 'hooks.json').write_text(json.dumps(template))
        (cursor / 'rules').mkdir()
        (cursor / 'rules/foreign.mdc').write_text('keep\n')
        for _ in range(2):
            self.assert_ok(self.run_install('cursor-merge', '--apply', '--mcp-keep', '--replace',
                                            '--project-root', self.project))
        current = json.loads((cursor / 'hooks.json').read_text())
        self.assertEqual(current['hooks']['stop'], template['hooks']['stop'])
        self.assertEqual(current['extra'], {'personal': True})
        self.assertIn(foreign, current['hooks']['sessionStart'])
        self.assertEqual(len(current['hooks']['sessionStart']), 2)
        self.assertEqual((hooks / 'foreign.py').read_text(), 'personal\n')
        self.assertEqual((cursor / 'rules/foreign.mdc').read_text(), 'keep\n')

    def test_unknown_public_script_is_not_overwritten_and_mcp_rolls_back(self):
        codex = self.home / '.codex'
        hooks = codex / 'hooks'
        hooks.mkdir(parents=True)
        script = hooks / 'session-start.py'
        script.write_text('print("personal script")\n')
        config = codex / 'config.toml'
        config.write_bytes(b'[features]\nhooks = false\n')
        result = self.run_install('codex-merge', '--apply', '--mcp-keep', '--replace')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unrecognized or customized hook script preserved', result.stderr)
        self.assertEqual(script.read_text(), 'print("personal script")\n')
        self.assertEqual(config.read_bytes(), b'[features]\nhooks = false\n')
        self.assertFalse((codex / 'hooks.json').exists())

    def test_invalid_hook_config_rolls_back_mcp(self):
        codex = self.home / '.codex'
        codex.mkdir()
        original = b'{"hooks":{"SessionStart":false}}\n'
        (codex / 'hooks.json').write_bytes(original)
        config = codex / 'config.toml'
        config.write_bytes(b'[features]\nhooks = false\n')
        result = self.run_install('codex-merge', '--apply', '--mcp-keep', '--replace')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((codex / 'hooks.json').read_bytes(), original)
        self.assertEqual(config.read_bytes(), b'[features]\nhooks = false\n')


@unittest.skipUnless(shutil.which('bash'), 'Bash not available')
class BashHostPreservationTests(HostPreservationMixin, unittest.TestCase):
    pass


@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell runtime not available')
class PowerShellHostPreservationTests(HostPreservationMixin, unittest.TestCase):
    shell = 'pwsh'
    suffix = '.ps1'


class HookOwnershipTests(unittest.TestCase):
    def test_known_previous_package_asset_upgrades_but_user_edits_are_preserved(self):
        with tempfile.TemporaryDirectory(prefix='hook ownership ') as temp:
            root = Path(temp)
            templates = root / 'templates'
            shutil.copytree(ROOT / 'trellis/codex', templates)
            target = root / 'host/hooks.json'
            command = [sys.executable, str(ROOT / 'scripts/lib/merge_host_hooks.py'),
                       '--host', 'codex', '--templates', str(templates), '--target', str(target)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            next_source = b'print("new package version")\n'
            (templates / 'hooks/session-start.py').write_bytes(next_source)
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            installed = target.parent / 'hooks/session-start.py'
            self.assertEqual(installed.read_bytes(), next_source)
            installed.write_bytes(b'print("personal edit")\n')
            config_before = target.read_bytes()
            third = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(third.returncode, 0)
            self.assertEqual(installed.read_bytes(), b'print("personal edit")\n')
            self.assertEqual(target.read_bytes(), config_before)


@unittest.skipUnless(shutil.which('bash'), 'Bash not available')
class ContextHookParityTests(unittest.TestCase):
    def test_bash_delegates_sibling_python_from_nested_cwd_and_keeps_error(self):
        with tempfile.TemporaryDirectory(prefix='nested hook ') as temp:
            root = Path(temp)
            hooks = root / 'installed hooks'
            hooks.mkdir()
            for name in ('session-start.sh', 'session-start.py'):
                shutil.copy2(ROOT / 'trellis/codex/hooks' / name, hooks / name)
            repo = root / 'repo'
            nested = repo / 'src/sub'
            nested.mkdir(parents=True)
            context = repo / '.trellis/scripts/get_context.py'
            context.parent.mkdir(parents=True)
            context.write_text('import sys\nprint("nested context")\nsys.exit(7)\n')
            results = [subprocess.run(cmd, cwd=nested, capture_output=True, text=True)
                       for cmd in ([sys.executable, str(hooks / 'session-start.py')],
                                   ['bash', str(hooks / 'session-start.sh')])]
            for result in results:
                self.assertEqual(result.returncode, 7)
                self.assertEqual(result.stdout, 'nested context\n')


if __name__ == '__main__':
    unittest.main()
