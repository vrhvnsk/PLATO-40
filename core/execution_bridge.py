"""Read-only bridge from Tal's mock executor to conservative outcome verification.

Mock statuses are *not* physical execution or verification evidence.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from .outcome_verification import load_jsonl, verify_outcomes, write_report


def bridge(decisions, executor_log):
    """Return lifecycle and per-decision mock-executor audit records.

    Never translate simulated_completed into executed, verified, or approved.
    An executor result with an unknown ID or a duplicate is reported as a warning.
    """
    ids = {str(d['event_id']) for d in decisions}
    seen = set()
    audit = []
    for entry in executor_log:
        eid = str(entry.get('event_id', ''))
        issues = []
        if eid not in ids:
            issues.append('unknown_decision_id')
        if eid in seen:
            issues.append('duplicate_executor_record')
        seen.add(eid)
        status = str(entry.get('status', ''))
        if status == 'simulated_completed' and entry.get('simulated') is not True:
            issues.append('inconsistent_simulation_flag')
        if status in {'executed', 'verified', 'approved', 'simulated_execution'}:
            issues.append('untrusted_executor_status_not_promoted')
        audit.append({'decision_id': eid, 'executor_status': status,
                      'execution_confirmed': False, 'outcome_confirmed': False,
                      'warnings': issues})
    for missing in sorted(ids - seen):
        audit.append({'decision_id': missing, 'executor_status': 'missing_log',
                      'execution_confirmed': False, 'outcome_confirmed': False,
                      'warnings': ['missing_executor_record']})
    # The mock executor emits no authenticated real-world events. Do not invent any.
    lifecycle = verify_outcomes(decisions, execution_events=[], observations=[])
    return lifecycle, audit


def write_bridge_report(out_dir, decisions, executor_log):
    out_dir = Path(out_dir)
    lifecycle, audit = bridge(decisions, executor_log)
    metrics = write_report(out_dir, decisions, lifecycle)
    with (out_dir / 'executor_audit.jsonl').open('w', encoding='utf-8') as f:
        for item in audit:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    summary = {'executor_statuses': dict(Counter(x['executor_status'] for x in audit)),
               'bridge_warnings': dict(Counter(w for x in audit for w in x['warnings'])),
               'outcome_counts': metrics['outcome_counts'],
               'note': 'Mock execution is not real execution. No lifecycle outcome was inferred.'}
    (out_dir / 'executor_bridge_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument('decisions')
    p.add_argument('execution_log')
    p.add_argument('--out-dir', default='reports/bridge')
    args = p.parse_args()
    summary = write_bridge_report(args.out_dir, load_jsonl(args.decisions), load_jsonl(args.execution_log))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
