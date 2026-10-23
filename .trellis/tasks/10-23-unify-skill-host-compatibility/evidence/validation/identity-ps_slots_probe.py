import json,os,pathlib,subprocess,tempfile,yaml
candidate=pathlib.Path('/private/tmp/skill-preflight-fix-0jv82wqf');runtime=pathlib.Path('/private/tmp/pwsh-validation-bye34yp3/runtime');python_bin=pathlib.Path('/private/tmp/pwsh-validation-bye34yp3/python-bin');results=[]
contents=[None,'malformed old document\n','---\nname: code-review\n---\nno description\n','---\nname: independent-report\ndescription: Keep capability.\n---\nprivate\n','---\nname: code-review\ndescription: Existing managed review.\n---\nold\n']
for action in ('replace','prune'):
 for index,content in enumerate(contents):
  with tempfile.TemporaryDirectory(prefix='ps identity slot ') as tmp:
   home=pathlib.Path(tmp);target=home/'.agents/skills';slot=(home/'.codex/skills/code-review') if action=='prune' else target/'code-review';slot.mkdir(parents=True);sentinel=slot/'sentinel';sentinel.write_text('keep')
   if content is not None:(slot/'SKILL.md').write_text(content)
   env={k:v for k,v in os.environ.items() if k not in ('CURSOR_MCP_FILE','CLAUDE_MCP_FILE','MINIMAX_DATA_DIR','MAVIS_DATA_DIR','CODEBUDDY_CONFIG_DIR')};env.update(HOME=str(home),USERPROFILE=str(home),CODEX_HOME=str(home/'.codex'),XDG_CONFIG_HOME=str(home/'.config'),XDG_CACHE_HOME=str(home/'.cache'),XDG_DATA_HOME=str(home/'.local/share'),DOTNET_CLI_HOME=str(home/'.dotnet'),POWERSHELL_TELEMETRY_OPTOUT='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(pathlib.Path(yaml.__file__).parent.parent),PSModulePath=str(runtime/'Modules'),PATH=os.pathsep.join([str(runtime),str(python_bin),os.environ['PATH']]))
   args=[str(runtime/'pwsh'),'-NoProfile','-File',str(candidate/'scripts/install-skills.ps1'),'--copy','--replace','--target',str(target)]
   if action=='prune':args.append('--prune-other-root')
   result=subprocess.run(args,env=env,cwd=home,text=True,capture_output=True,timeout=30)
   allowed=index==4
   assert (result.returncode==0)==allowed,(action,index,result.stdout,result.stderr)
   if not allowed:
    assert f'refusing to {action}' in result.stderr
    assert sentinel.read_text()=='keep'
    assert not (target/'memory').exists()
    assert list(home.rglob('*.bak'))==[]
   else:
    assert not sentinel.exists()
    assert (target/'code-review/SKILL.md').is_file()
   results.append({'action':action,'case':index,'expected_allowed':allowed,'exit':result.returncode,'passed':True})
print(json.dumps(results,indent=2))
