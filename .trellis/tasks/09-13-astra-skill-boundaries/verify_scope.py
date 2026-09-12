"""Read-only verification of the approved rule changes and installed copies."""
import json,re,sys,unittest,subprocess
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[3]
TASK=Path(__file__).resolve().parent
EGM_RULES=Path('/Users/hogenxue/Projects/EGM/AGENTS-egm.md')
meta=json.loads((TASK/'changed-files.json').read_text())
for filename in meta['files']:
 p=Path(filename);s=p.read_text()
 assert s.strip(),filename
 assert (Path(meta['backup'])/filename.lstrip('/')).is_file(),filename
 if p.name=='SKILL.md':
  data=yaml.safe_load(s.split('---',2)[1]);assert data.get('name') and data.get('description'),filename
 assert all(line==line.rstrip() for line in s.splitlines()),filename
 assert s.endswith('\n'),filename
pairs=[(ROOT/'AGENTS.global.md',Path.home()/'.codex/AGENTS.md')]
for rel in ['grill-with-docs/SKILL.md','grill-with-docs/references/trellis-boundary.md','diagnosing-bugs/SKILL.md']:
 pairs.append((ROOT/'skills'/rel,Path.home()/'.agents/skills'/rel))
for a,b in pairs:assert a.read_bytes()==b.read_bytes(),str(a)
workflow=(ROOT/'.trellis/workflow.md').read_text()
starts=re.findall(r'^\[workflow-state:([^\]]+)\]$',workflow,re.M)
ends=re.findall(r'^\[/workflow-state:([^\]]+)\]$',workflow,re.M)
assert starts==ends and len(starts)==len(set(starts)), 'workflow breadcrumb structure'
assert 'Load `trellis-brainstorm`; stay in planning.' not in workflow
assert 'Simple conversation or small task: ask only' not in workflow
assert 'Complex task: ask whether' not in workflow
assert 'commit, and wrap up' not in workflow
super=Path.home()/'.agents/skills/superpowers'
assert '1% chance' not in (super/'using-superpowers/SKILL.md').read_text()
assert '<HARD-GATE>' not in (super/'brainstorming/SKILL.md').read_text()
assert 'in this message' not in (super/'verification-before-completion/SKILL.md').read_text()
assert '## Mode routing' in (Path.home()/'.codex/skills/graphify/SKILL.md').read_text()
assert '不要求 OpenSpec CLI' in (Path.home()/'.codex/skills/openspec/SKILL.md').read_text()
assert '无未决项时记录可继续' in (ROOT/'skills/grill-with-docs/SKILL.md').read_text()
assert 'No red-capable command, no Phase 2' not in (ROOT/'skills/diagnosing-bugs/SKILL.md').read_text()
assert 'only when the current task requires graph evidence' in (ROOT/'AGENTS.md').read_text()
assert 'NEVER rename symbols' not in (ROOT/'AGENTS.md').read_text()
assert '实现稳定后，按当前 Task 要求使用项目原生 `trellis-check`' in (ROOT/'AGENTS.md').read_text()
assert '纯咨询不建 Task' in (ROOT/'AGENTS.project.md').read_text()
assert '以下变化本身不要求扩大验证' in (ROOT/'AGENTS.global.md').read_text()
assert EGM_RULES.read_bytes() == (ROOT/'AGENTS-egm.md').read_bytes()
egm=EGM_RULES.read_text()
for phrase in ('主动使用 `$grill-with-docs` 审查需求完整性','## 数据库交付','Gitee `origin`','可用命令清单，不是默认必跑清单'):
 assert phrase in egm
sys.path.insert(0,str(ROOT/'tests'))
from test_grill_with_docs_trellis_route import GrillWithDocsTrellisRouteTests
names=['test_global_template_routes_simple_and_complex_trellis_work','test_global_template_keeps_capability_boundaries_explicit','test_project_override_resolves_native_trellis_skill_aliases','test_repository_dogfoods_the_codex_phase_override']
result=unittest.TextTestRunner().run(unittest.TestSuite(GrillWithDocsTrellisRouteTests(n) for n in names))
assert result.wasSuccessful()
paths=[str(Path(p).relative_to(ROOT)) for p in meta['files'] if Path(p).is_relative_to(ROOT)]
subprocess.run(['git','diff','--check','--',*paths],cwd=ROOT,check=True)
print(f'PASS: {len(meta["files"])} changed files, backups, YAML, 4 install sync pairs, project workflow boundaries, EGM template sync and 4 existing template tests')
