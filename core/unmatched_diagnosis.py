"""Explain observational gaps without treating mock execution as real execution."""
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path
from .candidate_evidence import match
from .executor import execute

def diagnose(decisions, data_dir):
    candidates = match(decisions, data_dir)
    executions = {r['event_id']: r for r in execute(decisions)}
    groups = defaultdict(Counter)
    examples = defaultdict(list)
    rows = []
    for d, c in zip(decisions, candidates):
        status = c['observational_status']
        reason = c.get('unmatched_reason') or 'candidate_found'
        execution = executions.get(d.get('event_id'), {})
        mock_status = execution.get('status', 'missing_executor_record')
        # Classifications are mutually exclusive and are not claims of causality.
        if status == 'not_evaluated':
            category = 'unsupported_or_insufficient_rule'
        elif status == 'candidate_observation':
            category = 'temporal_candidate_only'
        elif mock_status.startswith('pending_') or mock_status == 'blocked':
            category = 'mock_executor_gate_unmet'
        elif mock_status in {'proposed_not_sent', 'logged_only'}:
            category = 'non_executing_mock_action'
        else:
            category = 'no_qualifying_observation'
        row = {'decision_id': d.get('event_id'), 'action': d.get('action'),
               'issue_type': d.get('issue_type'), 'observational_status': status,
               'unmatched_reason': reason, 'mock_executor_status': mock_status,
               'diagnosis': category, 'real_execution_confirmed': False}
        rows.append(row)
        groups[category][d.get('action')] += 1
        if len(examples[category]) < 5: examples[category].append(row)
    return rows, {'total': len(rows), 'diagnosis_counts': dict(Counter(r['diagnosis'] for r in rows)),
                  'mock_executor_status_counts': dict(Counter(r['mock_executor_status'] for r in rows)),
                  'unmatched_reasons': dict(Counter(r['unmatched_reason'] for r in rows if r['observational_status'] == 'no_observation_found')),
                  'by_action': {k:dict(v) for k,v in groups.items()}, 'examples': dict(examples),
                  'disclaimer': 'Mock executor gates are not evidence of actual execution; candidate observations are not causal outcomes.'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('decisions'); ap.add_argument('--data-dir',required=True); ap.add_argument('--out-dir',default='reports/diagnosis')
    a=ap.parse_args(); out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    decisions=[json.loads(s) for s in Path(a.decisions).read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    rows, summary=diagnose(decisions,a.data_dir)
    (out/'unmatched_diagnosis.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (out/'diagnosis_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary['diagnosis_counts'],indent=2))
if __name__=='__main__': main()
