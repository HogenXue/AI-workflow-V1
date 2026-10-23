import hashlib,importlib.util,json,os,pathlib,subprocess,sys,unittest
root=pathlib.Path('/private/tmp/pwsh-validation-bye34yp3')
repo=pathlib.Path('/Users/hogenxue/Projects/CodexTamplate')
runtime=root/'runtime'; home=root/'isolated-home';home.mkdir(exist_ok=True)
python_bin=root/'python-bin';python_bin.mkdir(exist_ok=True)
for name in ('python','python3'):
 p=python_bin/name
 if not p.exists():p.symlink_to(sys.executable)
for key in ('CODEX_HOME','CURSOR_MCP_FILE','CLAUDE_MCP_FILE','MINIMAX_DATA_DIR','MAVIS_DATA_DIR','CODEBUDDY_CONFIG_DIR','TRELLIS_TASK_DIR','TRELLIS_SESSION_ID'):
 os.environ.pop(key,None)
os.environ.update(HOME=str(home),USERPROFILE=str(home),XDG_CONFIG_HOME=str(home/'.config'),XDG_CACHE_HOME=str(home/'.cache'),XDG_DATA_HOME=str(home/'.local/share'),DOTNET_CLI_HOME=str(home/'.dotnet'),POWERSHELL_TELEMETRY_OPTOUT='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PSModulePath=str(runtime/'Modules'))
import yaml
os.environ['PYTHONPATH']=str(pathlib.Path(yaml.__file__).parent.parent)
os.environ['PATH']=os.pathsep.join([str(runtime),str(python_bin),os.environ.get('PATH','')])
version=subprocess.run([str(runtime/'pwsh'),'-NoLogo','-NoProfile','-NonInteractive','-Command',"$PSVersionTable | ConvertTo-Json -Compress"],env=os.environ,cwd=root,capture_output=True,text=True,timeout=30)
(root/'runtime-version.json').write_text(version.stdout)
if version.returncode:raise SystemExit(version.stderr)
print('RUNTIME:',version.stdout.strip(),flush=True)
selection={
 'test_install_components_ps':['InstallComponentsPsTests'],
 'test_install_entry_ps':['InstallEntryPsTests'],
 'test_install_existing_hooks_ps':['ExistingHooksInteractiveTests'],
 'test_install_lib_ps':['InstallLibPsTests'],
 'test_install_merge_ps':['InstallMergePsSmokeTests'],
 'test_install_review_ps':['SourceAliasSafetyTests','GraphifyPsRecoveryTests'],
 'test_install_new_hosts':['PowerShellNewHostMergeTests'],
 'test_install_wizard':['PowerShellWizardTests'],
 'test_aihero_install':['AiheroInstallPsTests'],
 'test_host_preservation':['PowerShellHostPreservationTests'],
}
suite=unittest.TestSuite();fingerprints={}
for name,classes in selection.items():
 file=repo/'tests'/f'{name}.py';fingerprints[str(file.relative_to(repo))]=hashlib.sha256(file.read_bytes()).hexdigest()
 spec=importlib.util.spec_from_file_location(name,file);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 for classname in classes:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(mod,classname)))
file=repo/'tests/test_install_codex_hook_ps.py';spec=importlib.util.spec_from_file_location('test_install_codex_hook_ps',file);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
suite.addTest(mod.CodexContextHookTests('test_installed_windows_command_runs_without_bash'))
(root/'selected-tests.json').write_text(json.dumps({'selection':selection,'count':suite.countTestCases(),'source_sha256':fingerprints},indent=2)+'\n')
result=unittest.TextTestRunner(verbosity=2).run(suite)
summary={'total':result.testsRun,'passed':result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),'skipped':[(case.id(),reason) for case,reason in result.skipped],'failures':[(case.id(),tb) for case,tb in result.failures],'errors':[(case.id(),tb) for case,tb in result.errors],'successful':result.wasSuccessful()}
(root/'result.json').write_text(json.dumps(summary,indent=2)+'\n')
raise SystemExit(not result.wasSuccessful())
