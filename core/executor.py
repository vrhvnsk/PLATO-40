"""Fail-closed mock executor. No physical actuation or guest delivery.

Approvals, consent, resource assignments and safety attestations are bound to
individual decision IDs. Context is an external, trusted input, not evidence
that the decision itself succeeded.
"""

from .decisions import APPROVAL_ACTIONS
from datetime import datetime, timezone

RESOURCE_ACTIONS = {'schedule_cleaning', 'dispatch_robot', 'dispatch_technician', 'request_inspection'}
SAFETY_CHECKS = {
    'release_room': 'room_clean_verified',
    'adjust_room_setpoint': 'comfort_limits_verified',
    'optimize_energy': 'energy_constraints_verified',
}
ROOM_ENTRY_ACTIONS = {'schedule_cleaning', 'dispatch_robot', 'request_inspection', 'dispatch_technician'}
MAX_ATTESTATION_AGE_SECONDS = 24 * 3600


def _utc(value):
    try:
        dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return dt.astimezone(timezone.utc) if dt.tzinfo else None
    except (TypeError, ValueError, OverflowError):
        return None


def _trusted_attestation(record, decision, context):
    if not isinstance(record, dict):
        return False
    source = record.get('source')
    if not source or source not in set(context.get('trusted_safety_sources') or []):
        return False
    observed = _utc(record.get('timestamp_utc'))
    decision_time = _utc(decision.get('timestamp_utc'))
    if observed is None or decision_time is None:
        return False
    execution_time = _utc(context.get('execution_time_utc')) if 'execution_time_utc' in context else decision_time
    if execution_time is None:
        return False
    age = (execution_time - observed).total_seconds()
    return 0 <= age <= MAX_ATTESTATION_AGE_SECONDS and observed <= decision_time


def _occupied_room_consent_required(decision, context):
    if decision.get('action') not in ROOM_ENTRY_ACTIONS:
        return False
    assets = set(map(str, decision.get('affected_assets') or []))
    occupied = set(map(str, context.get('occupied_rooms') or []))
    return bool(assets & occupied)

NON_EXECUTING = {'notify_guest': 'proposed_not_sent',
                 'flag_anomaly': 'logged_only',
                 'defer_action': 'logged_only',
                 'request_human_approval': 'logged_only',
                 'optimize_energy': 'proposal_only_not_dispatched'}


def _scoped_confirmation(decision, context, check):
    """Only decision-specific attestations with matching assets are accepted.

    Format: safety_confirmations[event_id][check] = {'assets': [...], 'verified': True}
    This deliberately rejects legacy global booleans.
    """
    record = context.get('safety_confirmations', {}).get(decision['event_id'], {}).get(check)
    if not isinstance(record, dict) or record.get('verified') is not True:
        return False
    assets = set(map(str, decision.get('affected_assets') or []))
    return (bool(assets) and assets.issubset(set(map(str, record.get('assets') or [])))
            and _trusted_attestation(record, decision, context))


def execute_decision(decision, context=None):
    context = context or {}
    eid = decision['event_id']
    action = decision['action']
    approval = bool(decision.get('requires_human_approval') or action in APPROVAL_ACTIONS)
    consent = bool(decision.get('requires_guest_consent') or _occupied_room_consent_required(decision, context))
    dependencies = decision.get('dependencies') or []
    completed = set(context.get('completed_actions') or [])
    missing = [f'dependency:{dep}' for dep in dependencies if dep not in completed]
    if approval and eid not in (context.get('approvals') or []):
        missing.append('human_approval')
    if consent and eid not in (context.get('consents') or []):
        missing.append('guest_consent')

    resource_id = decision.get('resource_id')
    if action in RESOURCE_ACTIONS:
        confirmations = context.get('resource_confirmations') or {}
        if not resource_id or confirmations.get(eid) != resource_id:
            missing.append('resource_availability')

    if action == 'release_room' and set(map(str, decision.get('affected_assets') or [])) & set(map(str, context.get('occupied_rooms') or [])):
        missing.append('room_occupied')
    if action == 'optimize_energy' and decision.get('proposal_only') is not True:
        missing.append('proposal_only_contract')
    if action == 'notify_guest' and not (decision.get('recipient_booking_ids') or decision.get('guest_request_ids')):
        missing.append('recipient_unresolved')
    check = SAFETY_CHECKS.get(action) if action != 'optimize_energy' else None
    if check and not _scoped_confirmation(decision, context, check):
        missing.append(check)

    if any(m.startswith('dependency:') for m in missing):
        status = 'pending_dependency'
    elif 'room_occupied' in missing or 'proposal_only_contract' in missing or 'recipient_unresolved' in missing:
        status = 'blocked'
    elif 'human_approval' in missing and 'guest_consent' in missing:
        status = 'pending_approval_and_consent'
    elif 'human_approval' in missing:
        status = 'pending_approval'
    elif 'guest_consent' in missing:
        status = 'pending_consent'
    elif 'resource_availability' in missing:
        status = 'pending_resource'
    elif check and check in missing:
        status = 'pending_verification'
    else:
        status = NON_EXECUTING.get(action, 'simulated_completed')

    return {
        'event_id': eid, 'action': action, 'status': status,
        'reason': {
            'simulated_completed': 'Mock processing only; real-world outcome unverified',
            'pending_dependency': 'Prerequisite not confirmed',
            'pending_approval': 'Human approval required',
            'pending_consent': 'Guest consent required',
            'pending_approval_and_consent': 'Human approval and guest consent required',
            'pending_resource': 'Decision-specific resource confirmation required',
            'pending_verification': 'Decision- and asset-specific safety attestation required',
            'proposed_not_sent': 'Guest message not sent',
            'proposal_only_not_dispatched': 'Planning output only; no battery dispatch',
            'logged_only': 'Recorded only',
        }.get(status, 'Execution blocked'),
        'missing_requirements': missing,
        'simulated': status == 'simulated_completed',
        'resource_id': resource_id,
        'duration_minutes': context.get('duration_minutes'),
        'verification': {'status': 'not_verified', 'details': decision.get('verification_plan', '')},
    }


def execute(decisions, approvals=None, consents=None, context=None):
    """All callers use the same safety path, including legacy execute(decisions).

    A caller may pass a persistent execution_ledger set in context to prevent
    replay across calls. In-memory duplicate and resource-conflict checks are
    always applied within this batch. No unverified action becomes a dependency.
    """
    context = dict(context or {})
    if approvals is not None:
        context['approvals'] = approvals
    if consents is not None:
        context['consents'] = consents
    seen = set(context.get('execution_ledger') or [])
    completed = set(context.get('completed_actions') or [])
    busy_resources = set(context.get('busy_resources') or [])
    results = []
    for decision in sorted(decisions, key=lambda d: (str(d.get('timestamp_utc', '')), str(d['event_id']))):
        eid = decision['event_id']
        rid = decision.get('resource_id')
        if eid in seen:
            result = {'event_id': eid, 'action': decision['action'], 'status': 'blocked',
                      'reason': 'Duplicate or replayed event_id', 'missing_requirements': ['duplicate_event_id'],
                      'simulated': False}
        elif decision['action'] in RESOURCE_ACTIONS and rid and rid in busy_resources:
            result = {'event_id': eid, 'action': decision['action'], 'status': 'blocked',
                      'reason': 'Resource already reserved in this batch',
                      'missing_requirements': ['resource_conflict'], 'simulated': False}
        else:
            result = execute_decision(decision, {**context, 'completed_actions': completed})
            # Mock processing is not evidence of real completion. Explicitly
            # verified dependencies must arrive through completed_actions.
            if result['status'] == 'simulated_completed' and decision['action'] in RESOURCE_ACTIONS:
                busy_resources.add(rid)
        seen.add(eid)
        results.append(result)
    if isinstance(context.get('execution_ledger'), set):
        context['execution_ledger'].update(seen)
    if isinstance(context.get('busy_resources'), set):
        context['busy_resources'].update(busy_resources)
    return results
