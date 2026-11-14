"""Conservative impact and learning verification: proposals never count as realized savings."""
from __future__ import annotations
import re
from collections import Counter
from .outcome_verification import verify_outcomes

BENEFIT = re.compile(r'estimated gross tariff benefit\s+EUR\s+([0-9]+(?:\.[0-9]+)?)', re.I)

def summarize_impact(decisions, execution_events=None, observations=None, learning=None):
    decisions = list(decisions)
    lifecycle = verify_outcomes(decisions, execution_events or [], observations or [])
    status = {row['decision_id']: row for row in lifecycle}
    energy = [d for d in decisions if d.get('action') == 'optimize_energy']
    estimates = []
    for d in energy:
        match = BENEFIT.search(str(d.get('reason', '')))
        if match:
            estimates.append(float(match.group(1)))
    recommendations = (learning or {}).get('recommendations', [])
    verified = [r for r in recommendations if r.get('status') == 'verified' and
                r.get('validation_evidence_refs') and r.get('measured_outcome') is not None]
    return {
        'decisions': len(decisions),
        'issue_counts': dict(sorted(Counter(d.get('issue_type') for d in decisions).items())),
        'energy': {
            'proposals': len(energy),
            'proposals_with_gross_estimate': len(estimates),
            'sum_of_individual_gross_estimates_eur': round(sum(estimates), 2),
            'estimated_savings_eur': None,
            'realized_savings_eur': None,
            'reason': 'Individual gross opportunities may overlap, and none is a verified, executed dispatch. Sum is NOT a portfolio savings estimate.',
        },
        'operations': {
            'cleaning_proposals': sum(d.get('action') == 'schedule_cleaning' for d in decisions),
            'guest_notification_proposals': sum(d.get('action') == 'notify_guest' for d in decisions),
            'maintenance_proposals': sum(d.get('issue_type') in {'heating_plant','ventilation_maintenance'} for d in decisions),
            'confirmed_executions': sum(bool(row['evidence_refs']) and row['lifecycle_status'] in {'executed','verified'} for row in lifecycle),
            'confirmed_successes': sum(row['outcome_status'] == 'confirmed_success' for row in lifecycle),
            'confirmed_failures': sum(row['outcome_status'] == 'confirmed_failure' for row in lifecycle),
            'labor_hours_saved': None,
            'deadlines_improved': None,
        },
        'learning': {
            'recommendations': len(recommendations),
            'verified_recommendations': len(verified),
            'unverified_recommendations': len(recommendations) - len(verified),
            'verification_policy': 'Requires explicit validation evidence references and a measured outcome; descriptive recommendations remain hypotheses.',
        },
        'lifecycle_warnings': dict(sorted(Counter(w for row in lifecycle for w in row['warnings']).items())),
    }
