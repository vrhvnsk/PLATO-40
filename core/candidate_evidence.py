"""Retrospective, non-causal evidence matching for PLATO-40.

Never treats post-decision observations as execution confirmation.
All source records retain their timestamps and identifiers.
"""
from __future__ import annotations
import argparse
import bisect
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

def dt(x):
    if isinstance(x, datetime):
        return x.astimezone(timezone.utc) if x.tzinfo else None
    if not isinstance(x, str):
        return None
    try:
        v = datetime.fromisoformat(x.replace("Z", "+00:00"))
        return v.astimezone(timezone.utc) if v.tzinfo else None
    except ValueError:
        return None

def records_csv(path):
    if not path.exists():
        return
    with path.open(encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)

def load_index(data_dir, decisions):
    root = Path(data_dir)
    if not root.is_dir():
        raise FileNotFoundError(root)
    rooms = {str(a) for d in decisions for a in d.get("affected_assets", [])
             if isinstance(a, str) and a.startswith("R") and a[1:].isdigit()}
    assets = {str(a) for d in decisions for a in d.get("affected_assets", [])}
    events, temps, orders = defaultdict(list), defaultdict(list), defaultdict(list)
    p = root / "events.jsonl"
    if p.exists():
        with p.open(encoding="utf-8-sig") as f:
            for line in f:
                if not line.strip():
                    continue
                e = json.loads(line)
                room = str(e.get("room_id", ""))
                t = dt(e.get("timestamp_utc"))
                if room in rooms and t:
                    events[room].append((t, e))
    for e in records_csv(root / "room_telemetry.csv"):
        room = e.get("room_id", "")
        if room not in rooms:
            continue
        t = dt(e.get("timestamp_utc"))
        try:
            temp = float(e["temperature_c"])
        except (ValueError, TypeError, KeyError):
            continue
        if t:
            temps[room].append((t, temp))
    for e in records_csv(root / "work_orders.csv"):
        asset = str(e.get("asset_id", ""))
        t = dt(e.get("completed_utc"))
        if asset in assets and t and str(e.get("status", "")).lower() == "completed":
            orders[asset].append((t, e))
    for index in (events, temps, orders):
        for values in index.values():
            values.sort(key=lambda x: x[0])
    return events, temps, orders

def after(series, start, hours):
    """Strictly later observations, bounded by a scenario-specific horizon."""
    if not start or not series:
        return []
    times = [x[0] for x in series]
    i = bisect.bisect_right(times, start)
    stop = start + timedelta(hours=hours)
    j = bisect.bisect_right(times, stop)
    return series[i:j]

SUPPORTED_ACTIONS = {"schedule_cleaning", "release_room", "adjust_room_setpoint", "dispatch_technician", "request_inspection"}
SUPPORTED_ISSUES = {"heating_comfort", "energy_comfort_coordination"}


def before(series, start, hours):
    if not start or not series:
        return []
    times = [x[0] for x in series]
    i = bisect.bisect_left(times, start - timedelta(hours=hours))
    j = bisect.bisect_right(times, start)
    return series[i:j]


def match(decisions, data_dir):
    events, temps, orders = load_index(data_dir, decisions)
    output = []
    cleaning_uses = defaultdict(list)
    for d in decisions:
        did = d.get("event_id")
        start = dt(d.get("timestamp_utc"))
        action = str(d.get("action", ""))
        issue = str(d.get("issue_type", ""))
        assets = [str(a) for a in d.get("affected_assets", [])]
        matches = []
        eligible = action in SUPPORTED_ACTIONS or issue in SUPPORTED_ISSUES
        reason = None
        if not eligible:
            status = "not_evaluated"
            reason = "No observational matching rule for this action/issue"
        elif not start:
            status = "not_evaluated"
            reason = "Missing or invalid decision timestamp"
        elif not assets:
            status = "not_evaluated"
            reason = "No affected assets to match"
        else:
            if action in {"schedule_cleaning", "release_room"}:
                for room in assets:
                    if room not in events:
                        continue
                    for t, ev in after(events[room], start, 24):
                        if ev.get("type") == "cleaning_completed":
                            source_id = ev.get("event_id")
                            matches.append({"kind": "later_cleaning_completion", "asset": room,
                                            "timestamp_utc": t.isoformat(), "source": "events.jsonl",
                                            "source_id": source_id, "match_strength": "temporal_only"})
                            if source_id:
                                cleaning_uses[source_id].append(len(output))
                            break
            if issue in SUPPORTED_ISSUES:
                for room in assets:
                    series = temps.get(room, [])
                    baseline = before(series, start, 2)
                    if not baseline:
                        reason = reason or "No pre-decision temperature baseline"
                        continue
                    baseline_c = baseline[-1][1]
                    if baseline_c >= 20:
                        reason = reason or "Baseline not below comfort band; recovery cannot be demonstrated"
                        continue
                    for t, temp in after(series, start, 6):
                        if 20 <= temp <= 23:
                            matches.append({"kind": "later_temperature_recovery_candidate", "asset": room,
                                            "timestamp_utc": t.isoformat(), "source": "room_telemetry.csv",
                                            "baseline_c": baseline_c, "value_c": temp,
                                            "match_strength": "observed_transition"})
                            break
            if action in {"dispatch_technician", "request_inspection"}:
                for asset in assets:
                    for t, order in after(orders.get(asset, []), start, 168):
                        matches.append({"kind": "later_completed_work_order", "asset": asset,
                                        "timestamp_utc": t.isoformat(), "source": "work_orders.csv",
                                        "source_id": order.get("work_order_id"),
                                        "match_strength": "asset_only_unattributed"})
                        break
            status = "candidate_observation" if matches else "no_observation_found"
            if not matches:
                reason = reason or "No qualifying later observation in the configured window"
        output.append({
            "decision_id": did, "issue_type": issue, "action": action,
            "observational_status": status, "unmatched_reason": reason if not matches else None,
            "execution_confirmed": False, "outcome_attributable": False,
            "candidate_evidence": matches,
            "interpretation": ("Post-decision observation only; no execution identity or causality established"
                               if matches else reason)
        })
    for source_id, indexes in cleaning_uses.items():
        if len(indexes) > 1:
            for i in indexes:
                for m in output[i]["candidate_evidence"]:
                    if m.get("source_id") == source_id and m["kind"] == "later_cleaning_completion":
                        m["shared_by_decisions"] = len(indexes)
                        m["match_strength"] = "ambiguous_reused_event"
    return output

def report(decisions, rows, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "candidate_evidence.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    counts = dict(sorted(Counter(r["observational_status"] for r in rows).items()))
    by_kind = dict(sorted(Counter(m["kind"] for r in rows for m in r["candidate_evidence"]).items()))
    by_action = {}
    for action in sorted({r.get("action", "") for r in rows}):
        subset = [r for r in rows if r.get("action", "") == action]
        by_action[action] = dict(sorted(Counter(r["observational_status"] for r in subset).items()))
    reasons = dict(sorted(Counter(r.get("unmatched_reason") for r in rows if r.get("unmatched_reason")).items()))
    match_strengths = dict(sorted(Counter(m.get("match_strength", "unknown") for r in rows
                                          for m in r.get("candidate_evidence", [])).items()))
    metrics = {"decisions": len(decisions), "status_by_action": by_action,
               "unmatched_reasons": reasons, "match_strengths": match_strengths, "observational_status_counts": counts,
               "candidate_evidence_by_kind": by_kind,
               "confirmed_executions": 0, "attributed_outcomes": 0,
               "note": "Candidates are temporal associations, not proof of execution or success."}
    (out / "candidate_evaluation.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    lines = ["# PLATO-40: Retrospective candidate evidence", "",
             f"Decisions assessed: **{len(decisions)}**", "", "## Observational status", ""]
    lines.extend(f"- `{k}`: {v}" for k,v in counts.items())
    lines += ["", "## Candidate evidence by kind", ""]
    lines.extend(f"- `{k}`: {v}" for k,v in by_kind.items())
    lines += ["", "## Why observations are unmatched", ""]
    lines.extend(f"- `{k}`: {v}" for k, v in reasons.items())
    lines += ["", "## Match quality", ""]
    lines.extend(f"- `{k}`: {v}" for k, v in match_strengths.items())
    lines += ["", "## Status by action", ""]
    lines.extend(f"- `{k}`: {v}" for k, v in by_action.items())
    lines += ["", "## Interpretation", "",
              "Observations are matched only when they occur strictly after the decision.",
              "`not_evaluated` means no implemented matching rule or insufficient decision metadata.",
              "`no_observation_found` means an eligible rule found no qualifying observation.",
              "Reused cleaning events and asset-only work orders are explicitly flagged as ambiguous.",
              "Heating recovery requires a below-band pre-decision baseline and a later in-band reading.",
              "These matches do **not** prove that a proposed action was approved, executed, or caused the observation.",
              "The existing Batch 3 lifecycle report remains authoritative for execution-linked outcomes.", ""]
    (out / "REPORT_CANDIDATES.md").write_text("\n".join(lines), encoding="utf-8")
    return metrics

def main():
    p = argparse.ArgumentParser()
    p.add_argument("decisions")
    p.add_argument("--data-dir", required=True)
    p.add_argument("--out-dir", default="reports/dev")
    args = p.parse_args()
    with open(args.decisions, encoding="utf-8-sig") as f:
        decisions = [json.loads(line) for line in f if line.strip()]
    rows = match(decisions, args.data_dir)
    metrics = report(decisions, rows, args.out_dir)
    print(f"Candidate evidence: {metrics['observational_status_counts']}; report in {args.out_dir}")

if __name__ == "__main__":
    main()
