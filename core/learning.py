"""Evidence-bounded Level 3 recommendations, not invented savings estimates."""
from __future__ import annotations
from collections import Counter, defaultdict
from .assurance import parse_time


def feedback(decisions: list[dict], assurance: dict) -> dict:
    actions = Counter((d.get('issue_type'), d.get('action')) for d in decisions)
    by_asset = defaultdict(Counter)
    for d in decisions:
        for asset in d.get('affected_assets', []) or []:
            by_asset[str(asset)][(d.get('issue_type'), d.get('action'))] += 1
    recs = []

    def add(owner, title, observation, recommendation, validation, refs, confidence='medium'):
        recs.append({'owner': owner, 'title': title, 'observation': observation,
                     'recommendation': recommendation, 'validation_required': validation,
                     'supporting_event_ids': refs[:8], 'confidence': confidence,
                     'impact_estimate': None, 'status': 'proposed_not_verified'})

    def examples(issue, action, asset=None):
        return [d['event_id'] for d in decisions if d.get('issue_type') == issue and d.get('action') == action
                and (asset is None or asset in (d.get('affected_assets') or [])) and d.get('event_id')][:8]

    n = actions[('heating_comfort', 'request_human_approval')]
    if n:
        add('CLARA', 'Review persistent cold-room escalations',
            f'{n} heating-comfort approval requests recorded in replay.',
            'Review room-level recovery windows and escalation timing before changing setpoint or alert thresholds.',
            'Compare occupied-room temperature trajectories before/after simulated adjustments; verify 20–23 C band and approval latency.',
            examples('heating_comfort', 'request_human_approval'))
    n = actions[('occupancy_surge', 'schedule_cleaning')]
    if n:
        add('CLARA', 'Evaluate weekend cleaning capacity',
            f'{n} occupancy-surge cleaning proposals recorded.',
            'Compare arrival deadlines against verified cleaner/robot reservations and recorded completion; review shift staffing for peak days.',
            'Measure missed deadlines and staff utilization from roster plus completion events, not proposal counts.',
            examples('occupancy_surge', 'schedule_cleaning'))
    n = sum(v for (issue, action), v in actions.items() if issue == 'logistics' and action in {'order_service', 'request_human_approval'})
    if n:
        add('CLARA', 'Track outstanding vendor requests',
            f'{n} logistics vendor-order or escalation decisions recorded.',
            'Maintain pending/accepted/fulfilled service state and suppress unnecessary repeat proposals until telemetry or vendor confirmation changes state.',
            'Join service acknowledgements with later stock/fill readings and calculate confirmed lead times.',
            examples('logistics', 'order_service') + examples('logistics', 'request_human_approval'))
    n = actions[('energy_comfort_coordination', 'request_human_approval')]
    if n:
        add('CLARA', 'Protect comfort during energy optimization',
            f'{n} coordinated comfort/energy approval requests recorded.',
            'Keep heating reductions gated during observed cold-room or plant-risk episodes; review forecast freshness and actual comfort recovery.',
            'Replay the proposed dispatch with constraints and compare to a no-action baseline before claiming cost savings.',
            examples('energy_comfort_coordination', 'request_human_approval'))
    if actions[('ventilation_maintenance', 'flag_anomaly')] or actions[('heating_plant', 'dispatch_technician')]:
        refs = examples('ventilation_maintenance', 'flag_anomaly') + examples('heating_plant', 'dispatch_technician')
        add('PLATO', 'Investigate plant maintainability and sensor redundancy',
            'Replay includes ventilation/plant maintenance signals; failure causality is not established.',
            'Assess accessible service points, differential-pressure sensing and fault telemetry in the next building design.',
            'Validate against confirmed work orders, inspection results and equipment fault logs before specifying hardware changes.', refs, 'low')
    if actions[('water_leak', 'request_inspection')] or actions[('water_leak', 'dispatch_technician')]:
        refs = examples('water_leak', 'request_inspection') + examples('water_leak', 'dispatch_technician')
        add('PLATO', 'Evaluate water-meter observability',
            'Replay includes suspected water leaks requiring investigation.',
            'Study whether room and main meters plus diagnostic telemetry adequately distinguish leaks from meter artifacts.',
            'Cross-check meter gaps against confirmed repairs and known occupancy; do not infer leak rate or savings from alerts.', refs, 'low')
    if assurance['finding_counts']:
        add('CLARA', 'Resolve decision assurance findings',
            f"Static audit identified {len(assurance['findings'])} findings across {len(assurance['finding_counts'])} categories.",
            'Triage errors before autonomous execution; investigate warnings with original scheduler and replay inputs.',
            'Re-run assurance after corrections and verify no new error-class findings.',
            [eid for f in assurance['findings'][:8] for eid in f['event_ids']][:8])
    top = sorted(((sum(c.values()), asset) for asset, c in by_asset.items()), reverse=True)[:10]
    return {
        'methodology': 'Descriptive, deterministic, post-replay analysis of emitted decisions. No counterfactual or physical outcome is inferred.',
        'data_limitations': ['Decisions are proposals or mock actions, not proof of physical execution.',
                             'Counts do not establish false-positive rates without labeled ground truth.',
                             'No measured cost, CO2, water, or labor savings are asserted.',
                             'Design recommendations are hypotheses pending equipment and work-order validation.'],
        'top_assets_by_decisions': [{'asset': asset, 'decisions': n} for n, asset in top],
        'recommendations': recs
    }
