"""Execute Codex context hooks and the installed Windows command (Windows CI)."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / 'trellis/codex/hooks/session-start.py'


class CodexContextHookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex hook ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.nested = self.project / 'nested'
        self.nested.mkdir(parents=True)

    def context(self, source):
        scripts = self.project / '.trellis/scripts'
        scripts.mkdir(parents=True)
        (scripts / 'get_context.py').write_text(source, encoding='utf-8')

    def run_hook(self):
        return subprocess.run([sys.executable, str(HOOK)], cwd=self.nested,
                              input='{"hook_event_name":"SessionStart"}',
                              text=True, capture_output=True, check=False)

    def test_no_trellis_is_successful_skip(self):
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('No .trellis/', result.stdout)

    def test_nested_context_uses_native_python_and_project_root(self):
        self.context("from pathlib import Path\nprint('CONTEXT_OK:' + Path.cwd().name)\n")
        result = self.run_hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CONTEXT_OK:project', result.stdout)

    def test_context_failure_is_not_hidden(self):
        self.context("import sys\nprint('context failed', file=sys.stderr)\nsys.exit(7)\n")
        result = self.run_hook()
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertIn('context failed', result.stderr)

    @unittest.skipUnless(os.name == 'nt' and shutil.which('pwsh'), 'Windows PowerShell required')
    def test_installed_windows_command_runs_without_bash(self):
        codex = self.root / 'home with spaces' / '.codex'
        env = {**os.environ, 'HOME': str(codex.parent), 'CODEX_HOME': str(codex),
               'PYTHONIOENCODING': 'utf-8'}
        self.context("from pathlib import Path\nprint('CONTEXT_OK:' + Path.cwd().name)\n")
        result = subprocess.run([
            shutil.which('pwsh'), '-NoProfile', '-File',
            str(ROOT / 'scripts/install-codex-merge.ps1'), '--apply', '--mcp-keep',
            '--codex-home', str(codex), '--skip-project'], env=env, cwd=self.project,
            text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads((codex / 'hooks.json').read_text(encoding='utf-8'))
        command = data['hooks']['SessionStart'][0]['hooks'][0]['commandWindows']
        self.assertNotIn('bash', command.lower())
        result = subprocess.run([shutil.which('pwsh'), '-NoProfile', '-Command', command],
                                cwd=self.nested, env=env, input='{}', text=True,
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('CONTEXT_OK:project', result.stdout)


if __name__ == '__main__':
    unittest.main()
