from pathlib import Path
import os,sys,subprocess,tempfile
import yaml
repo=Path('/Users/hogenxue/Projects/CodexTamplate');audit=Path(__file__).parent
pattern=sys.argv[1] if len(sys.argv)>1 else 'test_*.py'
with tempfile.TemporaryDirectory(prefix='fixture-home-',dir=audit) as td:
 home=Path(td);env=dict(os.environ)
 for key in ['CODEX_HOME','CURSOR_MCP_FILE','CLAUDE_MCP_FILE','MINIMAX_DATA_DIR','MAVIS_DATA_DIR','CODEBUDDY_CONFIG_DIR','XDG_STATE_HOME']:
  env.pop(key,None)
 env.update(HOME=str(home),USERPROFILE=str(home),XDG_CONFIG_HOME=str(home/'.config'),XDG_CACHE_HOME=str(home/'.cache'),XDG_DATA_HOME=str(home/'.local/share'),DOTNET_CLI_HOME=str(home/'.dotnet'),PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(Path(yaml.__file__).parent.parent),POWERSHELL_TELEMETRY_OPTOUT='1',DOTNET_CLI_TELEMETRY_OPTOUT='1')
 runtime_file=audit/'pwsh-path.txt'
 if runtime_file.exists():
  runtime=Path(runtime_file.read_text().strip()).parent;shim=home/'bin';shim.mkdir()
  for name in ['python','python3']:(shim/name).symlink_to(sys.executable)
  env.update(PATH=str(shim)+os.pathsep+str(runtime)+os.pathsep+env['PATH'],PSModulePath=str(runtime/'Modules'))
 p=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p',pattern,'-v'],cwd=repo,env=env)
 raise SystemExit(p.returncode)
