"""Fail closed on violations of challenge autonomy constraints."""
from .decisions import APPROVAL_ACTIONS


def validate(decisions):
    seen=set()
    for d in decisions:
        for key in ('event_id','timestamp_utc','affected_assets','issue_type','action','priority','reason','requires_human_approval'):
            if key not in d:raise ValueError(f'Missing decision field {key}')
        if d['event_id'] in seen:raise ValueError('Duplicate decision ID')
        seen.add(d['event_id'])
        if d.get('requires_guest_consent') and not d['requires_human_approval']:
            raise ValueError('Consent requires human approval')
        if d['action'] in APPROVAL_ACTIONS and not d['requires_human_approval']:
            raise ValueError('Unsafe action without approval')
        if d['action']=='release_room' and not any('cleaning_completed' in e for e in d.get('evidence',[])):
            raise ValueError('Room release without cleaning evidence')
        if d['action']=='adjust_room_setpoint':
            target=d.get('target_setpoint_c')
            if isinstance(target,bool) or not isinstance(target,(int,float)) or not 20<=target<=23:
                raise ValueError('Setpoint missing or unsafe')
        if d['action']=='optimize_energy' and (d.get('proposal_only') is not True or d.get('autonomy')!='proposal_only'):
            raise ValueError('Battery optimization must be proposal-only')
        if d['action']=='notify_guest' and not (d.get('recipient_booking_ids') or d.get('guest_request_ids')):
            # Missing recipient is a review condition, not permission to send.
            d['recipient_resolution']='manual_review_required'
        if d['action']=='release_room':
            ev=d.get('readiness_evidence') or {}
            if (ev.get('room_id') not in d['affected_assets'] or not ev.get('cleaning_completed_utc')
                    or ev.get('status')!='candidate_requires_fresh_housekeeping_check'):
                d['readiness_resolution']='manual_review_required'
    return sorted(decisions,key=lambda x:(x['timestamp_utc'],x['event_id']))
