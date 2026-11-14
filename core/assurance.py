"""Deterministic, read-only decision-contract and coordination audit.

This module never changes decisions, allocates resources, or claims execution.
Its findings distinguish proven inconsistencies from missing evidence.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        t = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return t.astimezone(timezone.utc) if t.tzinfo else None
    except ValueError:
        return None


def finding(code: str, severity: str, event_ids: list[str], detail: str) -> dict:
    return {'code': code, 'severity': severity, 'event_ids': event_ids, 'detail': detail}


def audit(decisions: list[dict]) -> dict:
    findings: list[dict] = []
    by_id: dict[str, dict] = {}
    counts = Counter()
    intervals = defaultdict(list)
    episode_actions = defaultdict(list)
    for i, d in enumerate(decisions):
        eid = d.get('event_id')
        if not isinstance(eid, str) or not eid:
            findings.append(finding('missing_event_id', 'error', [], f'Record {i} lacks event_id'))
            continue
        if eid in by_id:
            findings.append(finding('duplicate_event_id', 'error', [eid], 'Repeated event_id'))
        else:
            by_id[eid] = d
        action = d.get('action', '')
        issue = d.get('issue_type', '')
        counts[(issue, action)] += 1
        episode_actions[(d.get('episode_id'), action)].append(eid)
        if parse_time(d.get('timestamp_utc')) is None:
            findings.append(finding('invalid_timestamp', 'error', [eid], 'Timestamp missing timezone or invalid'))
        if not d.get('evidence'):
            findings.append(finding('missing_evidence', 'warning', [eid], 'No supporting evidence references'))
        if not str(d.get('verification_plan') or '').strip():
            findings.append(finding('missing_verification', 'warning', [eid], 'No verification criterion'))
        if action in {'request_human_approval', 'dispatch_technician', 'order_service'} and not d.get('requires_human_approval'):
            findings.append(finding('missing_approval_gate', 'error', [eid], f'{action} lacks approval gate'))
        # A proposal alone is not proof that cleaning occurred or that a room is safe to release.
        if action == 'release_room' and not any('cleaning_completed' in str(e) for e in d.get('evidence', [])):
            findings.append(finding('release_without_completion_evidence', 'error', [eid], 'No observed cleaning completion cited'))
        # Only parse explicit reservation evidence, not timestamps guessed from reason text.
        for e in d.get('evidence', []):
            if not isinstance(e, str) or 'resource=' not in e or ':slot=' not in e:
                continue
            resource = e.split('resource=', 1)[1].split(':', 1)[0]
            start_text = e.split(':slot=', 1)[1].split(':duration=', 1)[0]
            start = parse_time(start_text)
            if resource and start:
                intervals[resource].append((start, eid, action))
    for (episode, action), ids in episode_actions.items():
        if episode is not None and len(ids) > 1:
            findings.append(finding('repeated_episode_action', 'warning', ids[:10], f'{len(ids)} occurrences for {episode} / {action}'))
    for eid, d in by_id.items():
        now = parse_time(d.get('timestamp_utc'))
        for dep in d.get('dependencies', []) or []:
            if dep not in by_id:
                findings.append(finding('missing_dependency', 'error', [eid], f'Dependency {dep} absent from replay'))
            elif now and (prev := parse_time(by_id[dep].get('timestamp_utc'))) and prev > now:
                findings.append(finding('future_dependency', 'error', [eid, dep], 'Dependency occurs after dependent action'))
    # Same resource and identical start is suspicious, but durations are not present
    # in the decision contract: do not pretend to prove interval overlap.
    for resource, reservations in intervals.items():
        starts = defaultdict(list)
        for start, eid, _ in reservations:
            starts[start].append(eid)
        for start, ids in starts.items():
            if len(ids) > 1:
                findings.append(finding('same_resource_start', 'warning', ids[:10],
                                        f'{resource}: {len(ids)} reservations at {start.isoformat()}; check scheduler intervals'))
    findings.sort(key=lambda f: (f['code'], f['event_ids'], f['detail']))
    return {
        'decision_count': len(decisions),
        'unique_event_ids': len(by_id),
        'episode_count': len({d.get('episode_id') for d in decisions if d.get('episode_id')}),
        'counts': [{'issue_type': k[0], 'action': k[1], 'count': v} for k, v in sorted(counts.items())],
        'findings': findings,
        'finding_counts': dict(sorted(Counter(f['code'] for f in findings).items())),
        'interpretation': 'Read-only static audit. Warnings are review candidates, not confirmed operational failures.'
    }
