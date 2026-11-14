"""Read-only PLATO-40 contract and scenario coverage audit.
Run: python plato40_final_audit.py decisions_dev.jsonl
"""
import collections, json, sys, math
from pathlib import Path

def main(path):
    ds=[json.loads(s) for s in Path(path).read_text(encoding="utf-8").splitlines() if s.strip()]
    counts=collections.Counter((d.get("issue_type"),d.get("action")) for d in ds)
    findings=[]
    def flag(d,level,reason):
        findings.append({"event_id":d.get("event_id"),"issue_type":d.get("issue_type"),"action":d.get("action"),"severity":level,"reason":reason})
    required={"event_id","timestamp_utc","affected_assets","issue_type","action","priority","reason","requires_human_approval"}
    seen=set()
    for d in ds:
        for key in required-set(d): flag(d,"BLOCKER",f"missing required field: {key}")
        eid=d.get("event_id")
        if eid in seen:flag(d,"BLOCKER","duplicate decision ID")
        seen.add(eid)
        a=d.get("action")
        if a=="adjust_room_setpoint":
            t=d.get("target_setpoint_c")
            if isinstance(t,bool) or not isinstance(t,(int,float)) or not math.isfinite(t) or not 20<=t<=23:
                flag(d,"BLOCKER","missing, nonfinite or out-of-range setpoint")
        if a=="optimize_energy":
            if d.get("proposal_only") is not True or d.get("autonomy")!="proposal_only":
                flag(d,"BLOCKER","battery proposal not marked proposal_only")
        if a=="notify_guest":
            if not (d.get("recipient_booking_ids") or d.get("guest_request_ids")):
                if d.get("recipient_resolution")!="manual_review_required":
                    flag(d,"BLOCKER","unresolved recipient not marked manual review")
                else: flag(d,"REVIEW","guest recipient unresolved; must not send")
        if a=="release_room":
            evidence=d.get("evidence") or []
            if not any("cleaning_completed" in str(e) for e in evidence):
                flag(d,"BLOCKER","release missing cleaning-completion evidence")
            readiness=d.get("readiness_evidence") or {}
            if readiness.get("room_id") not in (d.get("affected_assets") or []) or not readiness.get("cleaning_completed_utc"):
                flag(d,"REVIEW","room readiness evidence missing/incomplete")
            if readiness.get("status")=="candidate_requires_fresh_housekeeping_check":
                flag(d,"REVIEW","fresh housekeeping attestation still required")
        if a in {"dispatch_technician","block_room","reassign_room","request_human_approval","order_service"} and not d.get("requires_human_approval"):
            flag(d,"BLOCKER","mandatory approval missing")
        if d.get("requires_guest_consent") and not d.get("requires_human_approval"):
            flag(d,"BLOCKER","guest consent without human approval")
    scenarios={
        "S01 room turnaround":{"room_turnaround"},
        "S02 water leak":{"water_leak"},
        "S03 heating":{"heating_comfort","heating_plant"},
        "S04 maintenance":{"ventilation_maintenance","heating_plant"},
        "S05 occupancy surge":{"occupancy_surge"},
        "Energy":{"energy_optimization"},
        "Logistics":{"logistics"},
    }
    print("Decisions:",len(ds),"Unique episodes:",len({d.get("episode_id") for d in ds}))
    print("\nScenario coverage (presence only, not correctness):")
    for name,issues in scenarios.items():
        n=sum(v for (issue,action),v in counts.items() if issue in issues)
        print(f"  {name}: {n} decisions", "COVERED" if n else "MISSING")
    print("\nAction distribution:")
    for (issue,action),n in sorted(counts.items()):print(f"  {issue}/{action}: {n}")
    by=collections.Counter(f["severity"] for f in findings)
    print("\nAudit findings:",dict(by))
    for f in findings[:20]:print(" ",f)
    report={"decisions":len(ds),"scenarios":{name:sum(v for (issue,action),v in counts.items() if issue in issues) for name,issues in scenarios.items()},
            "action_counts":{f"{i}/{a}":n for (i,a),n in sorted(counts.items())},"finding_counts":dict(by),"findings":findings,
            "limitations":["Read-only decision-contract checks; not execution safety certification",
                           "Presence of scenario actions does not prove correct scenario behavior",
                           "Cleaning readiness and recipient authentication require source-data and runtime validation",
                           "No real execution or verified outcomes inferred"]}
    Path("FINAL_AUDIT.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("\nWrote FINAL_AUDIT.json")
    return 1 if by["BLOCKER"] else 0
if __name__=="__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else "decisions_dev.jsonl"))
