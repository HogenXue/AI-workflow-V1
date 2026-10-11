"""Emit native Trellis context without requiring a Bash/WSL runtime."""

import os
import subprocess
import sys
from pathlib import Path

cwd = Path.cwd()
for root in (cwd, *cwd.parents):
    context = root / '.trellis/scripts/get_context.py'
    if context.is_file():
        result = subprocess.run(
            [sys.executable, str(context)], cwd=root, stdin=subprocess.DEVNULL,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, check=False,
        )
        sys.exit(result.returncode)

print('No .trellis/ in this project; skip session context.')
