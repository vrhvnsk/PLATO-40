"""Decision contract and deterministic IDs."""
import hashlib
import pandas as pd

PRIORITIES={'critical','high','medium','low'}
APPROVAL_ACTIONS={'dispatch_technician','block_room','reassign_room','request_human_approval','order_service'}

def iso(t):
    x=pd.Timestamp(t)
    return (x.tz_localize('UTC') if x.tzinfo is None else x.tz_convert('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')

def make(t, assets, issue, action, priority, reason, evidence, episode, *, approval=False, consent=False, confidence=0.7, expected='', verification='', dependencies=None, guest_ids=None, resource=None, target_setpoint_c=None, recipient_booking_ids=None, proposal_only=False, readiness_evidence=None):
    if priority not in PRIORITIES: raise ValueError(f'Invalid priority {priority}')
    assets=[str(a) for a in assets if pd.notna(a)]
    if not assets: raise ValueError('Decision must have affected_assets')
    need_approval=bool(approval or consent or action in APPROVAL_ACTIONS)
    eid='D-'+hashlib.sha256(f'{episode}|{action}|{",".join(assets)}|{iso(t)}'.encode()).hexdigest()[:16]
    out={'event_id':eid,'timestamp_utc':iso(t),'affected_assets':assets,'issue_type':issue,
         'action':action,'priority':priority,'reason':reason,
         'requires_human_approval':need_approval,'requires_guest_consent':bool(consent),
         'autonomy':'approval_and_consent' if consent else ('human_approval' if need_approval else 'autonomous'),
         'episode_id':str(episode),'evidence':[str(x) for x in evidence],
         'confidence':round(float(confidence),2),
         'expected_outcome':'SIMULATED: '+expected if expected else '',
         'verification_plan':verification,'dependencies':dependencies or [],
         'guest_request_ids':guest_ids or []}
    if target_setpoint_c is not None: out['target_setpoint_c']=float(target_setpoint_c)
    if recipient_booking_ids is not None: out['recipient_booking_ids']=list(recipient_booking_ids)
    if proposal_only: out['proposal_only']=True; out['autonomy']='proposal_only'
    if readiness_evidence is not None: out['readiness_evidence']=readiness_evidence
    if resource:out['resource_id']=str(resource)
    return out
