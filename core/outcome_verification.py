"""Conservative, read-only decision lifecycle and outcome evidence evaluation.

No execution is inferred from proposals, and unrelated telemetry is not credited
as an effect of a decision. Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TERMINAL = {'verified', 'failed'}
EXECUTION_STATES = {'approved', 'rejected', 'executed', 'failed', 'verified'}


def timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
    except ValueError:
        return None


def load_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open(encoding='utf-8-sig') as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_records(path: str | Path | None) -> list[dict]:
    if path is None:
        return []
    p = Path(path)
    if p.suffix.lower() == '.csv':
        with p.open(encoding='utf-8-sig', newline='') as handle:
            return list(csv.DictReader(handle))
    if p.suffix.lower() == '.jsonl':
        return load_jsonl(p)
    raise ValueError('Supported input formats: .csv and .jsonl')


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _truth(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.strip().lower() in {'true', '1', 'yes'})


def verify_outcomes(decisions: list[dict], execution_events: list[dict] | None = None,
                    observations: list[dict] | None = None) -> list[dict]:
    """Return one lifecycle record per decision.

    Execution event contract: decision_id (or event_id), status, timestamp_utc,
    evidence_ref. Valid statuses: approved, rejected, executed, failed, verified.
    'verified' requires an explicit evidence_ref and prior 'executed' event.
    'failed' indicates a recorded failure, not necessarily execution.

    Observation contract: decision_id, timestamp_utc, evidence_ref, outcome
    ('success' or 'failure'). Observations without decision_id are intentionally
    not linked. A successful observation needs an executed event before it can
    verify the decision; a failure observation is recorded as a failed outcome
    only when execution is established.
    """
    by_id = defaultdict(list)
    for ev in execution_events or []:
        key = ev.get('decision_id') or ev.get('event_id')
        if key:
            by_id[str(key)].append(ev)
    obs_by_id = defaultdict(list)
    for obs in observations or []:
        if obs.get('decision_id'):
            obs_by_id[str(obs['decision_id'])].append(obs)
    results = []
    for d in decisions:
        did = d.get('event_id')
        start = timestamp(d.get('timestamp_utc'))
        relevant = sorted(by_id.get(str(did), []), key=lambda e: timestamp(e.get('timestamp_utc')) or datetime.max.replace(tzinfo=timezone.utc))
        state = 'awaiting_approval' if _truth(d.get('requires_human_approval')) else 'proposed'
        executed_at = None
        evidence = []
        warnings = []
        rejected = False
        for ev in relevant:
            status = str(ev.get('status', '')).strip().lower()
            at = timestamp(ev.get('timestamp_utc'))
            ref = ev.get('evidence_ref')
            if status not in EXECUTION_STATES or at is None or (start and at < start):
                warnings.append('invalid_or_predecision_execution_event')
                continue
            if status == 'approved':
                if not rejected and state in {'awaiting_approval', 'proposed'}:
                    state = 'approved'
            elif status == 'rejected':
                if executed_at is None:
                    state = 'rejected'
                    rejected = True
            elif status == 'executed':
                if rejected or (_truth(d.get('requires_human_approval')) and state != 'approved' and executed_at is None):
                    warnings.append('execution_without_valid_approval')
                elif _nonempty(ref):
                    state = 'executed'
                    executed_at = at
                    evidence.append(str(ref))
                else:
                    warnings.append('execution_missing_evidence_ref')
            elif status == 'verified':
                if executed_at and at >= executed_at and _nonempty(ref):
                    state = 'verified'
                    evidence.append(str(ref))
                else:
                    warnings.append('verification_without_execution_evidence')
            elif status == 'failed':
                if _nonempty(ref):
                    state = 'failed'
                    evidence.append(str(ref))
                else:
                    warnings.append('failure_missing_evidence_ref')
        for obs in sorted(obs_by_id.get(str(did), []), key=lambda e: timestamp(e.get('timestamp_utc')) or datetime.max.replace(tzinfo=timezone.utc)):
            at = timestamp(obs.get('timestamp_utc'))
            outcome = str(obs.get('outcome', '')).lower()
            ref = obs.get('evidence_ref')
            if outcome not in {'success', 'failure'} or not at or not _nonempty(ref):
                warnings.append('invalid_outcome_observation')
                continue
            if executed_at is None or at < executed_at:
                warnings.append('observation_not_attributable_to_executed_decision')
                continue
            if outcome == 'failure':
                state = 'failed'
                evidence.append(str(ref))
            elif state != 'failed':
                state = 'verified'
                evidence.append(str(ref))
        results.append({
            'decision_id': did, 'episode_id': d.get('episode_id'),
            'issue_type': d.get('issue_type'), 'action': d.get('action'),
            'lifecycle_status': state,
            'outcome_status': ('confirmed_success' if state == 'verified' else
                               'confirmed_failure' if state == 'failed' else 'unknown'),
            'verification_plan_present': _nonempty(d.get('verification_plan')),
            'evidence_refs': list(dict.fromkeys(evidence)),
            'warnings': list(dict.fromkeys(warnings)),
        })
    return results


def evaluate(decisions: list[dict], lifecycle: list[dict]) -> dict:
    statuses = Counter(x['lifecycle_status'] for x in lifecycle)
    outcomes = Counter(x['outcome_status'] for x in lifecycle)
    warnings = Counter(w for x in lifecycle for w in x['warnings'])
    return {
        'decision_count': len(decisions),
        'lifecycle_counts': dict(sorted(statuses.items())),
        'outcome_counts': dict(sorted(outcomes.items())),
        'warning_counts': dict(sorted(warnings.items())),
        'verification_plan_coverage': sum(_nonempty(d.get('verification_plan')) for d in decisions),
        'evidence_reference_coverage': sum(bool(d.get('evidence')) for d in decisions),
        'approval_gate_coverage': sum(_truth(d.get('requires_human_approval')) for d in decisions if d.get('action') in {'request_human_approval', 'dispatch_technician', 'order_service'}),
        'approval_gated_decisions': sum(d.get('action') in {'request_human_approval', 'dispatch_technician', 'order_service'} for d in decisions),
        'note': 'Unknown means no attributable observed outcome. Static coverage is not proof of physical execution or effectiveness.',
    }


def write_report(out_dir: Path, decisions: list[dict], lifecycle: list[dict]) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = evaluate(decisions, lifecycle)
    with (out_dir / 'lifecycle.jsonl').open('w', encoding='utf-8') as f:
        for row in lifecycle:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    (out_dir / 'evaluation.json').write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding='utf-8')
    lines = ['# PLATO-40 Batch 3: Outcome verification', '',
             f"Decisions: **{metrics['decision_count']}**", '', '## Lifecycle statuses', '']
    lines += [f'- `{k}`: {v}' for k, v in metrics['lifecycle_counts'].items()]
    lines += ['', '## Outcome statuses', '']
    lines += [f'- `{k}`: {v}' for k, v in metrics['outcome_counts'].items()]
    lines += ['', '## Coverage', '',
              f"- Verification plans: {metrics['verification_plan_coverage']} / {len(decisions)}",
              f"- Decision evidence references: {metrics['evidence_reference_coverage']} / {len(decisions)}",
              f"- Approval gates on gated action types: {metrics['approval_gate_coverage']} / {metrics['approval_gated_decisions']}",
              '', '## Warnings', '']
    lines += [f'- `{k}`: {v}' for k, v in metrics['warning_counts'].items()] or ['- None']
    lines += ['', '## Interpretation', '', metrics['note'],
              'Execution and outcome evidence must explicitly reference the decision ID. Unlinked sensor readings cannot establish causation.', '']
    (out_dir / 'REPORT_BATCH3.md').write_text('\n'.join(lines), encoding='utf-8')
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description='Conservative outcome verification for PLATO-40')
    parser.add_argument('decisions', help='Decisions JSONL file')
    parser.add_argument('--execution-events', help='Optional CSV or JSONL of explicit execution events')
    parser.add_argument('--observations', help='Optional CSV or JSONL of decision-linked outcomes')
    parser.add_argument('--out-dir', default='reports/batch3')
    args = parser.parse_args()
    decisions = load_jsonl(args.decisions)
    lifecycle = verify_outcomes(decisions, load_records(args.execution_events), load_records(args.observations))
    metrics = write_report(Path(args.out_dir), decisions, lifecycle)
    print(f"Batch 3: {len(decisions)} decisions; outcomes {metrics['outcome_counts']}; reports in {args.out_dir}")


if __name__ == '__main__':
    main()
