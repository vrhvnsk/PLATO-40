"""Adversarial safety gates. Tests distinguish enforced guarantees from open risks."""
import pytest
from core.executor import execute, execute_decision
from core.safety import validate

BASE = dict(event_id='ADV-1', timestamp_utc='2026-11-13T10:00:00Z',
            affected_assets=['R101'], issue_type='occupancy_surge',
            action='release_room', priority='high', reason='adversarial',
            requires_human_approval=False, evidence=['cleaning_completed:E1'])

def decision(**updates):
    return {**BASE, **updates}

def attestation(eid='ADV-1', room='R101', check='room_clean_verified'):
    return {'safety_confirmations': {eid: {check: {'verified': True, 'assets': [room]}}}}

def test_dirty_room_without_attestation_blocked():
    assert execute_decision(decision(), {})['status'] == 'pending_verification'

def test_wrong_room_attestation_blocked():
    assert execute_decision(decision(), attestation(room='R102'))['status'] == 'pending_verification'

def test_global_clean_boolean_does_not_authorize():
    assert execute_decision(decision(), {'room_clean_verified': True})['status'] == 'pending_verification'

def test_wrong_decision_attestation_blocked():
    assert execute_decision(decision(), attestation(eid='ADV-OTHER'))['status'] == 'pending_verification'

def test_approval_cannot_be_borrowed_from_another_decision():
    d=decision(action='block_room', requires_human_approval=True)
    assert execute_decision(d, {'approvals':['ADV-OTHER']})['status']=='pending_approval'

def test_consent_cannot_be_borrowed():
    d=decision(action='schedule_cleaning', requires_guest_consent=True,
               requires_human_approval=True, resource_id='STAFF1')
    r=execute_decision(d, {'approvals':['ADV-1'], 'consents':['ADV-OTHER'],
                            'resource_confirmations':{'ADV-1':'STAFF1'}})
    assert r['status']=='pending_consent'

def test_missing_dependency_even_if_simulated_prior_action():
    clean=decision(event_id='CLEAN',action='schedule_cleaning',resource_id='STAFF1')
    release=decision(event_id='RELEASE',dependencies=['CLEAN'])
    context={'resource_confirmations':{'CLEAN':'STAFF1'},
             'safety_confirmations':{'RELEASE':{'room_clean_verified':{'verified':True,'assets':['R101']}}}}
    result=execute([clean,release],context=context)
    assert next(x for x in result if x['event_id']=='RELEASE')['status']=='pending_dependency'

def test_duplicate_event_id_blocked():
    results=execute([decision(),decision()],context=attestation())
    assert any(r['status']=='blocked' and 'duplicate_event_id' in r['missing_requirements'] for r in results)

def test_same_resource_double_booking_blocked():
    a=decision(action='schedule_cleaning',event_id='A',resource_id='STAFF1')
    b=decision(action='schedule_cleaning',event_id='B',resource_id='STAFF1')
    res=execute([a,b],context={'resource_confirmations':{'A':'STAFF1','B':'STAFF1'}})
    assert res[0]['status']=='simulated_completed'
    assert res[1]['status']=='blocked'

def test_unsafe_setpoint_rejected_by_validator():
    with pytest.raises(ValueError,match='Setpoint'):
        validate([decision(action='adjust_room_setpoint',target_setpoint_c=29)])

def test_room_release_without_cleaning_evidence_rejected_by_validator():
    with pytest.raises(ValueError,match='cleaning evidence'):
        validate([decision(evidence=[])])

def test_missing_approval_flag_rejected_by_validator():
    with pytest.raises(ValueError,match='approval'):
        validate([decision(action='block_room')])

def test_persistent_replay_ledger_blocks_second_batch():
    ledger=set()
    d=decision(action='flag_anomaly')
    assert execute([d],context={'execution_ledger':ledger})[0]['status']=='logged_only'
    assert execute([d],context={'execution_ledger':ledger})[0]['status']=='blocked'

def test_occupied_room_requires_consent_even_if_flag_falsified():
    d=decision(action='schedule_cleaning',resource_id='STAFF1',requires_guest_consent=False)
    r=execute_decision(d,{'occupied_rooms':['R101'],'resource_confirmations':{'ADV-1':'STAFF1'}})
    assert r['status']!='simulated_completed'

def test_stale_attestation_cannot_release_room():
    ctx=attestation()
    ctx['safety_confirmations']['ADV-1']['room_clean_verified']['timestamp_utc']='2020-01-01T00:00:00Z'
    assert execute_decision(decision(),ctx)['status']!='simulated_completed'
