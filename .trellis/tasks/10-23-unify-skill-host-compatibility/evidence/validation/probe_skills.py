"""Native discovery only: initialize, initialized, skills/list; no thread or turn."""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

parser = argparse.ArgumentParser()
parser.add_argument('--cwd', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--timeout', type=float, default=30)
args = parser.parse_args()
output = Path(args.output)
output.parent.mkdir(parents=True, exist_ok=True)
proc = subprocess.Popen(['codex', 'app-server', '--stdio'], stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                        cwd=args.cwd, env=os.environ.copy(), bufsize=1)
messages = queue.Queue()

def reader():
    for line in proc.stdout:
        try:
            messages.put(json.loads(line))
        except json.JSONDecodeError:
            pass
    messages.put(None)

threading.Thread(target=reader, daemon=True).start()

def send(message):
    proc.stdin.write(json.dumps(message) + '\n')
    proc.stdin.flush()

def response(identifier):
    deadline = time.monotonic() + args.timeout
    while True:
        item = messages.get(timeout=max(.01, deadline - time.monotonic()))
        if item is None:
            raise RuntimeError('app-server closed before response')
        if item.get('id') == identifier:
            if 'error' in item:
                raise RuntimeError('app-server returned RPC error code ' + str(item['error'].get('code')))
            return item['result']
        if time.monotonic() >= deadline:
            raise TimeoutError('app-server response timeout')

try:
    send({'id': 1, 'method': 'initialize', 'params': {
        'clientInfo': {'name': 'local_skill_discovery_audit', 'version': '1.0.0'},
        'capabilities': {'experimentalApi': False}}})
    initialized = response(1)
    send({'method': 'initialized'})
    send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(Path(args.cwd).resolve())], 'forceReload': True}})
    listing = response(2)
    result = {'method': 'skills/list', 'server': {k: initialized.get(k) for k in ('userAgent', 'platformFamily', 'platformOs', 'codexHome')},
              'data': [{'cwd': entry['cwd'], 'errors': entry['errors'],
                        'skills': [{k: skill.get(k) for k in ('name', 'path', 'enabled', 'scope', 'pluginId')}
                                   for skill in entry['skills']]}
                       for entry in listing['data']]}
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'output': str(output), 'cwd_count': len(result['data']),
                      'skills': sum(len(e['skills']) for e in result['data']),
                      'errors': sum(len(e['errors']) for e in result['data'])}))
finally:
    if proc.stdin:
        proc.stdin.close()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
