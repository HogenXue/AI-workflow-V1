import importlib.util,os,pathlib,unittest,yaml
c=pathlib.Path('/private/tmp/skill-preflight-fix-0jv82wqf');repo=pathlib.Path('/Users/hogenxue/Projects/CodexTamplate')
if not (c/'config').exists():(c/'config').symlink_to(repo/'config',target_is_directory=True)
os.environ.update(PYTHONPATH=str(pathlib.Path(yaml.__file__).parent.parent),PYTHONDONTWRITEBYTECODE='1',PATH='/private/tmp/pwsh-validation-bye34yp3/runtime:/private/tmp/pwsh-validation-bye34yp3/python-bin:'+os.environ['PATH'])
home=c/'isolated-home';home.mkdir(exist_ok=True)
os.environ.update(HOME=str(home),USERPROFILE=str(home),XDG_CONFIG_HOME=str(home/'.config'),XDG_CACHE_HOME=str(home/'.cache'),XDG_DATA_HOME=str(home/'.local/share'),DOTNET_CLI_HOME=str(home/'.dotnet'),POWERSHELL_TELEMETRY_OPTOUT='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',PSModulePath='/private/tmp/pwsh-validation-bye34yp3/runtime/Modules')
for k in ('CURSOR_MCP_FILE','CLAUDE_MCP_FILE','MINIMAX_DATA_DIR','MAVIS_DATA_DIR','CODEBUDDY_CONFIG_DIR','CODEX_HOME'):os.environ.pop(k,None)
suite=unittest.TestSuite()
def load(name):
 s=importlib.util.spec_from_file_location(name,c/'tests'/f'{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('test_install')
for name in ('test_skills_conflict_requires_replace_and_preserves_existing_file','test_other_root_pruning_is_explicit_and_backed_up','test_default_component_backups_share_agents_root'):
 suite.addTest(m.ComponentInstallTests(name))
m=load('test_aihero_install')
for cls in (m.AiheroInstallBashTests,m.AiheroInstallPsTests):
 for name in ('test_preview_preserves_old_restored_skills_and_does_not_prune_them','test_upgrade_replaces_restored_skills_with_backups_and_prunes_only_legacy'):
  suite.addTest(cls(name))
r=unittest.TextTestRunner(verbosity=2).run(suite);raise SystemExit(not r.wasSuccessful())
