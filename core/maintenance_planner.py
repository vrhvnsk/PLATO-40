"""S04: time-aware maintenance triage, using observed faults and real roster capacity."""
import pandas as pd
from .decisions import make, iso

DURATION = pd.Timedelta('90min')
HORIZON = pd.Timedelta('48h')
STEP = pd.Timedelta('30min')

def _known_orders(orders, asset, at):
    if orders.empty or not {'asset_id','created_utc','status'}.issubset(orders):
        return orders.iloc[0:0]
    created = pd.to_datetime(orders.created_utc, utc=True, errors='coerce')
    rows = orders[(orders.asset_id.astype(str) == str(asset)) & (created <= at)].copy()
    # A work order completed after the decision time was still open then.
    if 'completed_utc' in rows:
        completed = pd.to_datetime(rows.completed_utc, utc=True, errors='coerce')
        rows = rows[completed.isna() | (completed > at)]
    if 'status' in rows:
        rows = rows[~rows.status.astype(str).str.lower().isin(['cancelled','canceled'])]
    return rows

def _find_slot(sched, at):
    # A slot is never assumed available: scheduler validates the entire interval.
    start = pd.Timestamp(at).ceil('30min')
    stop = at + HORIZON
    while start + DURATION <= stop:
        if sched.available('technician', start, start + DURATION, at):
            rid = sched.reserve('technician', start, start + DURATION, at)
            if rid:
                return rid, start
        start += STEP
    return None, None

def plan_maintenance(data, sched, detected):
    """Upgrade existing S04 alerts into feasible service proposals.

    Does not claim work is completed, does not create fictional technicians,
    and never treats a sensor-data-quality alert as equipment degradation.
    """
    orders = data['work_orders']
    result = []
    for original in sorted(detected, key=lambda x: (x['timestamp_utc'], x['event_id'])):
        issue = original['issue_type']
        if issue not in {'heating_plant','ventilation_maintenance'}:
            result.append(original)
            continue
        at = pd.Timestamp(original['timestamp_utc'])
        asset = original['affected_assets'][0]
        ep = original['episode_id']
        evidence = list(original['evidence'])
        known = _known_orders(orders, asset, at)
        if not known.empty:
            refs = [f"work_orders.csv:{x}" for x in known.work_order_id.astype(str)] if 'work_order_id' in known else ['work_orders.csv:open_order']
            result.append(make(at, [asset], issue, 'flag_anomaly', original['priority'],
                'Maintenance concern already has a known open work order; monitor its progress rather than dispatch twice.',
                evidence + refs, ep, verification='Verify existing work order completion and post-service telemetry.'))
            continue
        rid, slot = _find_slot(sched, at)
        if rid:
            result.append(make(at, [asset], issue, 'dispatch_technician', original['priority'],
                f'Proposed 90-minute inspection at {iso(slot)} by {rid}; human approval required before dispatch. No repair is assumed.',
                evidence + [f'staff_roster.csv:resource={rid}:slot={iso(slot)}'], ep,
                approval=True, resource=rid, expected='Technician inspection proposed, not yet executed',
                verification='Approve assignment, confirm technician attendance, inspect equipment and compare post-service measurements.'))
        else:
            result.append(make(at, [asset], issue, 'request_human_approval', original['priority'],
                'No verified 90-minute technician slot in the next 48 hours; request on-call/external HVAC service approval. No external availability is assumed.',
                evidence + ['staff_roster.csv:no_confirmed_technician_slot_within_48h'], ep,
                approval=True, verification='Confirm external availability, accepted work order and post-service measurements.'))
    return result
