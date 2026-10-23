from pathlib import Path
import hashlib, json, subprocess, tempfile
root=Path(tempfile.mkdtemp(prefix='codextamplate-review-probe-'))
files={
 'baseline/src/pricing.py':'def total_cents(unit_cents, quantity):\n    return unit_cents * quantity\n',
 'candidate/src/pricing.py':'def total_cents(unit_cents, quantity):\n    return unit_cents + quantity\n',
 'candidate/.trellis/tasks/review-only/prd.md':'# Price calculation\nAcceptance: total_cents(125, 2) must return 250.\nRequested mode: review current uncommitted diff; only report issues.\n',
 'candidate/.trellis/tasks/review-only/task.json':'{"id":"review-only","status":"in_progress"}\n',
 'candidate/.trellis/spec/python.md':'# Python conventions\nUse snake_case. Represent prices as integer cents.\n',
 'candidate/.trellis/.current-task':'.trellis/tasks/review-only\n',
 'candidate/unrelated-notes.md':'Existing user note: do not edit.\n'
}
for name,content in files.items():
 p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
def snapshot():
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}
before=snapshot()
# Review reads the defined requirement/standards, then examines the known current diff.
prd=(root/'candidate/.trellis/tasks/review-only/prd.md').read_text()
standards=(root/'candidate/.trellis/spec/python.md').read_text()
diff=subprocess.run(['git','--no-optional-locks','diff','--no-index','--','baseline/src/pricing.py','candidate/src/pricing.py'],cwd=root,capture_output=True,text=True)
namespace={}
exec(compile((root/'candidate/src/pricing.py').read_text(),'candidate/src/pricing.py','exec'),namespace)
observed=namespace['total_cents'](125,2)
after=snapshot()
print(json.dumps({'fixture':str(root),'fixture_type':'isolated git --no-index diff; no Git refs or index created','diff_exit':diff.returncode,'diff':diff.stdout,'spec_finding':{'file':'candidate/src/pricing.py','line':2,'expected':250,'observed':observed,'severity':'P1','fix_applied':False},'standards_findings':[],'reviewed_files':len(before),'preservation':{'all_file_hashes_unchanged':before==after,'task_state_unchanged':before['candidate/.trellis/tasks/review-only/task.json']==after['candidate/.trellis/tasks/review-only/task.json'],'spec_unchanged':before['candidate/.trellis/spec/python.md']==after['candidate/.trellis/spec/python.md'],'unrelated_unchanged':before['candidate/unrelated-notes.md']==after['candidate/unrelated-notes.md']},'limitations':['No native host invocation','No staged/unstaged/untracked Git index coverage','Behavioral exercise by evaluator, not probabilistic model regression']} ,ensure_ascii=False,indent=2))
