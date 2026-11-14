"""Conservative verification ledger. No future observations are used at decision time.

Only explicit event confirmations qualify as observed completion. The ledger is
an offline retrospective, not a causal online controller.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import timedelta
from .assurance import parse_time
import pandas as pd

CONFIRMATIONS = {
    'release_room': {'cleaning_completed'},
    'schedule_cleaning': {'cleaning_completed'},
}


def verify(decisions: list[dict], events: list[dict] | None = None) -> dict:
    observations = defaultdict(list)
    if events is None:
        events = []
    if isinstance(events, pd.DataFrame):
        events = events.to_dict('records')
    for ev in events:
        typ = str(ev.get('type', ''))
        room = str(ev.get('room_id', ''))
        at = parse_time(ev.get('timestamp_utc'))
        if typ and room and at:
            observations[(room, typ)].append(at)
    for times in observations.values():
        times.sort()
    rows = []
    for d in decisions:
        action = d.get('action')
        at = parse_time(d.get('timestamp_utc'))
        assets = d.get('affected_assets') or []
        status = 'unverified'
        basis = 'No explicit execution or outcome confirmation supplied'
        if action == 'release_room' and any('cleaning_completed' in str(e) for e in d.get('evidence', [])):
            status = 'observed_prerequisite_only'
            basis = 'Cleaning completion referenced, but room-release confirmation is absent'
        elif action == 'schedule_cleaning' and at and len(assets) == 1:
            # Matching only by room and a 24-hour window is suggestive, not proof
            # that this particular scheduled job was executed.
            later = [t for t in observations.get((str(assets[0]), 'cleaning_completed'), [])
                     if at <= t <= at + timedelta(hours=24)]
            if later:
                status = 'candidate_observation'
                basis = 'Later cleaning completion for room; job identity not established'
        rows.append({'event_id': d.get('event_id'), 'action': action, 'status': status, 'basis': basis})
    return {'methodology': 'Retrospective evidence matching; no claim of causality or autonomous execution.',
            'entries': rows,
            'status_counts': {s: sum(x['status'] == s for x in rows) for s in sorted({x['status'] for x in rows})}}
