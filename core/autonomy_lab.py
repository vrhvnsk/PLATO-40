"""Deterministic, synthetic, safety-gated PLATO planning and outcome laboratory.

Never operates real equipment or sends communications. Counterfactual scores and
outcomes are scenario assumptions, not measured building performance.
"""
from __future__ import annotations
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

RISK = {'request_human_approval', 'isolate_water_supply', 'relocate_guest', 'release_room'}
PRIORITY = {'critical': 0, 'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
RESOURCES = {'schedule_cleaning': 'cleaner', 'dispatch_maintenance': 'technician',
             'inspect_leak': 'technician', 'adjust_room_setpoint': 'heat_pump',
             'optimize_energy': 'battery'}


def stable_unit(*parts):
    digest = hashlib.sha256('|'.join(map(str, parts)).encode()).digest()
    return int.from_bytes(digest[:8], 'big') / (2**64)


def alternatives(decision):
    action = str(decision.get('action', ''))
    options = [action, 'monitor_and_verify', 'request_human_approval']
    return list(dict.fromkeys(options))


def score_option(decision, action, seed=40):
    """Illustrative utility with hard safety exclusions, not calibrated costs."""
    approval = bool(decision.get('requires_human_approval'))
    consent = bool(decision.get('requires_guest_consent'))
    if (approval or consent or action in RISK) and action != 'request_human_approval':
        return {'action': action, 'eligible': False, 'score': None,
                'reason': 'Approval/consent or high-impact action requires a human gate'}
    if action == 'request_human_approval':
        utility = 48 if approval or consent else 22
    elif action == 'monitor_and_verify':
        utility = 30 if decision.get('confidence', 1) < 0.6 else 18
    else:
        utility = 65 + 10 * stable_unit(seed, decision.get('event_id'), action)
    return {'action': action, 'eligible': True, 'score': round(utility, 3),
            'reason': 'Synthetic utility: response benefit, conservatism and action eligibility'}


def simulate(decisions, seed=40, capacity=None):
    """Plan across episodes, reserve resources and simulate post-action checks.

    No approvals are fabricated. Safety-gated actions are queued for a human.
    """
    capacity = dict(capacity or {'cleaner': 2, 'technician': 1, 'heat_pump': 3, 'battery': 1})
    if any(not isinstance(v, int) or v < 0 for v in capacity.values()):
        raise ValueError('capacities must be non-negative integers')
    reservations = {}
    output = []
    order = sorted(decisions, key=lambda d: (str(d.get('timestamp_utc', '')),
                  PRIORITY.get(str(d.get('priority', '')).lower(), 4), str(d.get('event_id', ''))))
    for d in order:
        event = str(d.get('event_id', ''))
        opts = [score_option(d, a, seed) for a in alternatives(d)]
        eligible = [o for o in opts if o['eligible']]
        chosen = max(eligible, key=lambda o: (o['score'], o['action']))
        resource = RESOURCES.get(chosen['action'])
        slot = str(d.get('timestamp_utc', ''))[:13]
        key = (slot, resource)
        conflict = resource is not None and reservations.get(key, 0) >= capacity.get(resource, 0)
        gated = chosen['action'] == 'request_human_approval'
        steps = [{'step': 'detect', 'status': 'observed_in_input'},
                 {'step': 'evaluate_alternatives', 'status': 'simulated'},
                 {'step': 'check_safety_and_resources', 'status': 'simulated'}]
        if conflict:
            status = 'deferred_resource_conflict'
            steps.append({'step': 'replan', 'status': 'queued_for_next_slot'})
        elif gated:
            status = 'awaiting_human_approval'
            steps.append({'step': 'human_approval', 'status': 'pending'})
        else:
            status = 'simulated_action_completed'
            if resource:
                reservations[key] = reservations.get(key, 0) + 1
            steps.append({'step': 'execute', 'status': 'synthetic_only'})
        # Explicitly synthetic feedback; deterministic by seed and event ID.
        success = status == 'simulated_action_completed' and stable_unit(seed, event, 'outcome') >= 0.2
        if status == 'simulated_action_completed':
            steps.append({'step': 'verify', 'status': 'synthetic_pass' if success else 'synthetic_fail'})
        output.append({'event_id': event, 'episode_id': d.get('episode_id'),
                       'issue_type': d.get('issue_type'), 'original_action': d.get('action'),
                       'chosen_action': chosen['action'], 'alternatives': opts,
                       'decision_explanation': chosen['reason'], 'resource': resource,
                       'resource_slot': slot if resource else None, 'status': status,
                       'synthetic_outcome': 'pass' if success else ('fail' if status == 'simulated_action_completed' else 'not_observed'),
                       'steps': steps, 'real_execution_confirmed': False,
                       'real_outcome_verified': False,
                       'learning_signal': 'synthetic_positive' if success else ('synthetic_negative' if status == 'simulated_action_completed' else 'insufficient_evidence')})
    return output


def evaluation(records):
    statuses = Counter(r['status'] for r in records)
    completed = statuses['simulated_action_completed']
    successes = sum(r['synthetic_outcome'] == 'pass' for r in records)
    return {'count': len(records), 'statuses': dict(sorted(statuses.items())),
            'synthetic_successes': successes, 'synthetic_completions': completed,
            'synthetic_success_rate': round(successes / completed, 5) if completed else None,
            'real_executions_verified': 0, 'real_improvement_claimed': False,
            'limitations': ['Synthetic deterministic outcomes are not independent evidence',
                            'No real actuation, approvals, guest messages or real-world feedback']}


def compare_policy(records):
    """Conservative promotion gate: never promote on synthetic outcomes alone."""
    positives = sum(r['learning_signal'] == 'synthetic_positive' for r in records)
    return {'candidates_supported_by_synthetic_feedback': positives,
            'promoted_candidates': 0, 'promotion_allowed': False,
            'reason': 'Requires independent holdout evidence and authenticated operational outcomes'}


def read_jsonl(path):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows):
    Path(path).write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows), encoding='utf-8')


def run_lab(decisions_path, out_dir, seed=40, capacity=None):
    dest = Path(out_dir); dest.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    decisions = read_jsonl(decisions_path)
    rows = simulate(decisions, seed, capacity)
    elapsed = time.perf_counter() - t0
    write_jsonl(dest / 'autonomy_trace.jsonl', rows)
    report = {'seed': seed, 'source': str(decisions_path), 'evaluation': evaluation(rows),
              'learning': compare_policy(rows), 'performance': {
                  'elapsed_seconds': round(elapsed, 4),
                  'decisions_per_second': round(len(rows) / elapsed, 2) if elapsed else None},
              'reproducibility': {'deterministic_outputs': True,
                  'trace_sha256': hashlib.sha256((dest / 'autonomy_trace.jsonl').read_bytes()).hexdigest()}}
    (dest / 'autonomy_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report
