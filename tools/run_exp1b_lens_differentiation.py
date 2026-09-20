#!/usr/bin/env python3
from __future__ import annotations
import hashlib, itertools, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research_core.models import EvidenceRecord, PracticeRequest, RoutingLevel
from research_core.service import prioritize_followups
FIXTURE_PATH = ROOT / "examples/paper/experiments/exp1b/fixtures.json"
OUT_DIR = ROOT / "examples/paper/experiments/exp1b/results"

def build_request(d):
    return PracticeRequest(
        categories=list(d["categories"]),
        parent_distribution=dict(d["parent_distribution"]),
        evidence=[EvidenceRecord(**x) for x in d["evidence"]],
        permitted_categories=list(d["permitted_categories"]),
        kappa_company=float(d["kappa_company"]),
        temporal_decay_rate_per_day=float(d["temporal_decay_rate_per_day"]),
        routing_levels=[RoutingLevel(**x) for x in d["routing_levels"]],
        routing_gamma=float(d["routing_gamma"]), support_tau=float(d["support_tau"]),
        abstention_threshold=float(d["abstention_threshold"]),
    )
def chash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def tv(a,b):
    keys=sorted(set(a)|set(b))
    return 0.5*sum(abs(float(a.get(k,0))-float(b.get(k,0))) for k in keys)

def main():
    data=json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    rows=[]
    for f in data["fixtures"]:
        result=prioritize_followups(build_request(f["request"]))
        rows.append({
            "case_id":f["case_id"],"study":f["study"],"control_type":f["control_type"],
            "source_company":f.get("source_company"),"source_company_lens_id":f.get("source_company_lens_id"),
            "source_role":f.get("source_role"),"source_role_lens_id":f.get("source_role_lens_id"),
            "result":result,"sha256":chash(result),
        })
    groups={
        "company_positive_swe":[x for x in rows if x["case_id"].startswith("E1B-C1-")],
        "company_negative_retail":[x for x in rows if x["case_id"].startswith("E1B-N1-")],
        "role_positive":[x for x in rows if x["case_id"].startswith("E1B-R1-")],
    }
    comparisons={}
    for name,items in groups.items():
        pairs=[]
        for a,b in itertools.combinations(items,2):
            da=a["result"].get("diagnostic_distribution",{})
            db=b["result"].get("diagnostic_distribution",{})
            pairs.append({"a":a["case_id"],"b":b["case_id"],"tv":round(tv(da,db),12),
                          "exact_result_equal":a["result"]==b["result"],
                          "same_top_category":a["result"].get("top_category")==b["result"].get("top_category")})
        comparisons[name]=pairs
    failures=[]
    for p in comparisons["company_positive_swe"]:
        if p["tv"]<=0: failures.append(f"positive company control zero TV: {p['a']} vs {p['b']}")
    for p in comparisons["company_negative_retail"]:
        if p["tv"]!=0 or not p["exact_result_equal"]:
            failures.append(f"negative company control differs: {p['a']} vs {p['b']}")
    role_items=groups["role_positive"]
    if len({chash(x["result"].get("diagnostic_distribution",{})) for x in role_items}) != len(role_items):
        failures.append("role positive control did not produce five distinct distributions")
    if len({x["result"].get("top_category") for x in role_items}) < 2:
        failures.append("role positive control produced fewer than two distinct top categories")
    expected={
        "E1B-C1-amazon-swe":"ownership_execution",
        "E1B-C1-google-swe":"analytical_problem_solving",
        "E1B-C1-jpmorgan-swe":"analytical_problem_solving",
        "E1B-R1-swe":"analytical_problem_solving",
        "E1B-R1-data":"analytical_problem_solving",
        "E1B-R1-retail":"impact_results",
        "E1B-R1-risk":"analytical_problem_solving",
        "E1B-R1-consult":"structured_thinking",
    }
    byid={x["case_id"]:x for x in rows}
    for cid,exp in expected.items():
        act=byid[cid]["result"].get("top_category")
        if act!=exp: failures.append(f"{cid}: expected {exp}, got {act}")
    out={"protocol_version":data["protocol_version"],"experiment_base_commit":data["experiment_base_commit"],
         "fixture_count":len(rows),"results":rows,"comparisons":comparisons,"failures":failures,"passed":not failures}
    OUT_DIR.mkdir(parents=True,exist_ok=True)
    jp=OUT_DIR/"exp1b_results.json"; cp=OUT_DIR/"exp1b_results.csv"
    jp.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    lines=["case_id,study,control_type,source_company,source_role,mode,top_category,data_support,effective_evidence_mass,uncertainty_entropy,sha256"]
    for row in rows:
        r=row["result"]
        lines.append(",".join(map(str,[row["case_id"],row["study"],row["control_type"],row.get("source_company") or "",
            row.get("source_role") or "",r.get("mode") or "",r.get("top_category") or "",
            r.get("data_support",""),r.get("effective_evidence_mass",""),r.get("uncertainty_entropy",""),row["sha256"]])))
    cp.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"exp1b_cases={len(rows)} failures={len(failures)}")
    print("results_json_sha256="+hashlib.sha256(jp.read_bytes()).hexdigest())
    print("results_csv_sha256="+hashlib.sha256(cp.read_bytes()).hexdigest())
    if failures:
        for f in failures: print("FAIL:",f)
        return 1
    print("EXPERIMENT_1B_PASS")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
