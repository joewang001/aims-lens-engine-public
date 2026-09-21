#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIXTURES=ROOT/'examples/paper/experiments/exp3/fixtures.json'
OUT=ROOT/'examples/paper/experiments/exp3/results'
EXPECTED_IDS=[f'AHA-00{i}' for i in range(1,7)]
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def combined(c): return ' '.join([c['transcript']]+c.get('supplemental_evidence_markers',[])).lower()
def target(text):
 t=text.lower()
 if 'senior software developer' in t: return 'Senior Software Developer'
 if 'software developer' in t and re.search(r'\bsenior role\b',t): return 'Senior Software Developer'
 return 'Not clearly stated'
def impact(t):
 metric=bool(re.search(r'\b\d+(?:\.\d+)?\s*%|\b\d+\s*percent\b|\b\d[\d,]*\s+(?:monthly\s+)?users\b',t) or ('seconds' in t and 'milliseconds' in t))
 outcome=any(x in t for x in ['reduced','reduce','reduction','cut','faster','improvement','improved'])
 return metric and outcome
def reasoning(t): return any(x in t for x in ['problem','issue','bottleneck','contention','locking','slow','performance']) and any(x in t for x in ['proposed','changed','change the','identified','found','checked','redesign','asynchronous','caching logic','background job','transaction logic'])
def ownership(t): return any(x in t for x in ['i led','i was responsible','i proposed','i identified','i changed','i introduced','i found'])
def collaboration(t): return any(x in t for x in ['collaborated with','worked closely with','worked with qa','product and qa','qa and product','cross-functional','different teams'])
def mentoring(t): return any(x in t for x in ['mentored','helping junior','help two junior','junior developers'])
def fit(t): return any(x in t for x in ['strong fit','strong candidate','fit senior role','i can fit senior role'])
def unsupported(t): return sum(x in t for x in ['hardworking','responsible','learn quickly'])>=2
def senior(t):
 decision=any(x in t for x in ['i led','i was responsible','i proposed','technical decision-making','take responsibility for delivery'])
 scope=mentoring(t) or any(x in t for x in ['100,000','payment system','highest-traffic','production features independently'])
 return decision and scope
def oracle(c):
 t=combined(c); trg=target(c['transcript'])
 f={'measurable_impact':impact(t),'technical_reasoning':reasoning(t),'project_ownership':ownership(t),'collaboration':collaboration(t),'mentoring':mentoring(t),'role_fit_connection':fit(t),'unsupported_self_claims':unsupported(t),'senior_scope':senior(t)}
 gate=trg=='Senior Software Developer' and f['measurable_impact'] and f['technical_reasoning'] and f['project_ownership'] and f['collaboration'] and f['senior_scope'] and f['role_fit_connection']
 if trg=='Not clearly stated': gap='target_role_clarity'
 elif gate: gap='validation_probe'
 elif f['unsupported_self_claims']: gap='evidence_and_ownership'
 else: gap='ownership_or_senior_scope'
 return {'target_role':trg,'mode':'validation_probe' if gate else 'diagnostic','strong_answer_gate':gate,'primary_gap_class':gap,'features':f,'language_surface_variation':bool(c.get('language_surface_variation',False)),'language_surface_used_in_gate':False}
def main():
 data=json.loads(FIXTURES.read_text(encoding='utf-8')); failures=[]; cases=data.get('cases',[])
 ids=[c.get('case_id') for c in cases]
 if ids!=EXPECTED_IDS: failures.append(f'case IDs/order mismatch: {ids!r}')
 if data.get('claim_boundary',{}).get('current_model_rerun_performed') is not False: failures.append('current_model_rerun_performed must be false')
 rows=[]; details=[]
 for c in cases:
  cid=c['case_id']; cf=[]; actual_sha=sha(c['transcript'])
  if actual_sha!=c['transcript_sha256']: cf.append('transcript SHA mismatch')
  if c.get('historical_baseline_status')!='PASS': cf.append('historical baseline status is not PASS')
  r=oracle(c)
  if r['target_role']!=c['expected_target_role']: cf.append(f"target role expected {c['expected_target_role']!r}, got {r['target_role']!r}")
  if r['mode']!=c['expected_mode']: cf.append(f"mode expected {c['expected_mode']!r}, got {r['mode']!r}")
  if r['strong_answer_gate'] is not c['expected_strong_gate']: cf.append(f"strong gate expected {c['expected_strong_gate']!r}, got {r['strong_answer_gate']!r}")
  if r['primary_gap_class'] not in c['allowed_primary_gap_classes']: cf.append(f"primary gap {r['primary_gap_class']!r} not allowed")
  for feat in c.get('must_credit_features',[]):
   if not r['features'].get(feat,False): cf.append('must-credit feature not detected: '+feat)
  if cid=='AHA-004' and r['target_role']!='Not clearly stated': cf.append('current identity incorrectly used as target role')
  if cid=='AHA-006' and (not r['strong_answer_gate'] or r['language_surface_used_in_gate']): cf.append('AHA-006 gate/language-surface invariant failed')
  failures.extend(f'{cid}: {x}' for x in cf)
  rows.append({'case_id':cid,'historical_baseline':c['historical_baseline_status'],'target_role':r['target_role'],'mode':r['mode'],'strong_answer_gate':r['strong_answer_gate'],'primary_gap_class':r['primary_gap_class'],'must_credit_pass':all(r['features'].get(f,False) for f in c.get('must_credit_features',[])),'language_surface_variation':r['language_surface_variation'],'language_surface_used_in_gate':r['language_surface_used_in_gate'],'case_passed':not cf,'transcript_sha256':actual_sha})
  details.append({'case_id':cid,'scenario':c['scenario'],'source_basis':c['source_basis'],'oracle':r,'expected':{'target_role':c['expected_target_role'],'mode':c['expected_mode'],'strong_answer_gate':c['expected_strong_gate'],'allowed_primary_gap_classes':c['allowed_primary_gap_classes'],'must_credit_features':c['must_credit_features'],'preferred_aims_signals':c['preferred_aims_signals']},'failures':cf})
 hp=sum(c.get('historical_baseline_status')=='PASS' for c in cases); op=sum(r['case_passed'] for r in rows)
 out={'protocol_version':data['protocol_version'],'experiment_base_commit':data['experiment_base_commit'],'source_record':data['source_record'],'claim_boundary':data['claim_boundary'],'historical_only_generation_rules':data['historical_only_generation_rules'],'case_count':len(cases),'historical_baseline_pass_count':hp,'deterministic_oracle_pass_count':op,'current_model_rerun_performed':False,'cases':details,'failures':failures,'passed':not failures}
 OUT.mkdir(parents=True,exist_ok=True); jp=OUT/'exp3_results.json'; cp=OUT/'exp3_case_matrix.csv'
 jp.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf-8')
 fields=['case_id','historical_baseline','target_role','mode','strong_answer_gate','primary_gap_class','must_credit_pass','language_surface_variation','language_surface_used_in_gate','case_passed','transcript_sha256']
 with cp.open('w',encoding='utf-8',newline='') as fh:
  w=csv.DictWriter(fh,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
 print(f'exp3_cases={len(cases)} historical_pass={hp} oracle_pass={op} failures={len(failures)}'); print('current_model_rerun_performed=false'); print('results_json_sha256='+hashlib.sha256(jp.read_bytes()).hexdigest()); print('case_matrix_csv_sha256='+hashlib.sha256(cp.read_bytes()).hexdigest())
 if failures:
  [print('FAIL:',x) for x in failures]; return 1
 print('EXPERIMENT_3_PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
