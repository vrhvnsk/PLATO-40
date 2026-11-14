"""Final scenario acceptance: decision invariants, counterfactuals and full replay.

These tests establish specified contracts, not physical-world correctness.
"""
from collections import Counter
from pathlib import Path
import pytest
from core.executor import execute, execute_decision
from core.loader import Data
from core.scheduler import Scheduler
from core.detectors import detect_all
from core.safety import validate

ROOT = Path(__file__).resolve().parents[1]
NOW = '2026-11-13T10:00:00Z'

def decision(eid, action, **kwargs):
    return {'event_id':eid,'timestamp_utc':NOW,'affected_assets':['R101'],
            'action':action,**kwargs}

def trusted(eid, check, assets=('R101',), when='2026-11-13T09:55:00Z', source='housekeeping'):
    return {'trusted_safety_sources':['housekeeping'],
            'safety_confirmations':{eid:{check:{'verified':True,'assets':list(assets),
                                               'timestamp_utc':when,'source':source}}}}

@pytest.mark.parametrize('change',[
    {'occupied_rooms':['R101']},
    {'execution_time_utc':'2026-11-15T10:00:00Z'},
    {'execution_time_utc':'bad'},
    {'trusted_safety_sources':[]},
    {'safety_confirmations':{}},
])
def test_s01_release_fails_closed_when_context_changes(change):
    d=decision('release', 'release_room')
    ctx=trusted('release','room_clean_verified');ctx.update(change)
    assert execute_decision(d,ctx)['status']!='simulated_completed'

def test_s01_verified_release_and_wrong_room():
    d=decision('release','release_room')
    assert execute_decision(d,trusted('release','room_clean_verified'))['status']=='simulated_completed'
    assert execute_decision(d,trusted('release','room_clean_verified',('R102',)))['status']=='pending_verification'

def test_s01_guest_message_is_not_claimed_sent():
    assert execute_decision(decision('guest','notify_guest',recipient_booking_ids=['BK1']))['status']=='proposed_not_sent'
    assert execute_decision(decision('guest','notify_guest'))['status']=='blocked'

@pytest.mark.parametrize('action', ['request_inspection','dispatch_technician','schedule_cleaning','dispatch_robot'])
def test_s02_s04_s05_no_unassigned_resources(action):
    d=decision('resource',action,resource_id='STAFF1')
    assert execute_decision(d)['status']!='simulated_completed'
    ctx={'resource_confirmations':{'resource':'STAFF1'},'approvals':['resource']}
    assert execute_decision(d,ctx)['status']=='simulated_completed'
    ctx['resource_confirmations']={'different':'STAFF1'}
    assert execute_decision(d,ctx)['status']!='simulated_completed'

def test_s02_occupied_room_entry_requires_guest_consent():
    d=decision('inspection','request_inspection',resource_id='TECH1')
    ctx={'occupied_rooms':['R101'],'resource_confirmations':{'inspection':'TECH1'}}
    assert execute_decision(d,ctx)['status']=='pending_consent'
    ctx['consents']=['inspection']
    assert execute_decision(d,ctx)['status']=='simulated_completed'

def test_s03_heating_attestation_is_scoped_and_trusted():
    d=decision('heat','adjust_room_setpoint',target_setpoint_c=21)
    assert execute_decision(d)['status']=='pending_verification'
    assert execute_decision(d,trusted('heat','comfort_limits_verified'))['status']=='simulated_completed'
    assert execute_decision(d,trusted('heat','comfort_limits_verified',source='untrusted'))['status']=='pending_verification'

@pytest.mark.parametrize('setpoint', [19, 24, None, 'bad'])
def test_s03_invalid_heating_targets_rejected(setpoint):
    from core.decisions import make
    with pytest.raises((ValueError,TypeError)):
        d=make(NOW,['R101'],'heating_comfort','adjust_room_setpoint','medium','test',['sensor'],'episode',target_setpoint_c=setpoint)
        validate([d])

def test_energy_proposal_cannot_dispatch_even_with_attestation():
    d=decision('energy','optimize_energy',proposal_only=True)
    assert execute_decision(d,trusted('energy','energy_constraints_verified'))['status']=='proposal_only_not_dispatched'
    assert execute_decision(decision('energy2','optimize_energy',proposal_only=False))['status']=='blocked'

def test_s05_conflicting_staff_and_duplicate_event():
    ds=[decision('a','schedule_cleaning',resource_id='C1'),
        decision('b','schedule_cleaning',resource_id='C1'),
        decision('a','schedule_cleaning',resource_id='C1')]
    ctx={'resource_confirmations':{'a':'C1','b':'C1'}}
    assert [x['status'] for x in execute(ds,context=ctx)]==['simulated_completed','blocked','blocked']

def test_logistics_dependencies_cannot_be_satisfied_by_simulation():
    ds=[decision('a','schedule_cleaning',resource_id='C1'),
        decision('b','release_room',dependencies=['a'])]
    ctx={'resource_confirmations':{'a':'C1'},**trusted('b','room_clean_verified')}
    assert [x['status'] for x in execute(ds,context=ctx)]==['simulated_completed','pending_dependency']

def test_replay_all_scenarios_and_invariants():
    data=Data(ROOT/'data'/'quickstart')
    ds=validate(detect_all(data,Scheduler(data['staff_roster'])))
    assert len(ds)>0
    counts=Counter(d['issue_type'] for d in ds)
    for scenario in ('room_turnaround','water_leak','heating_comfort',
                     'occupancy_surge','energy_optimization','logistics'):
        assert counts[scenario]>0, f'missing {scenario}'
    assert counts['ventilation_maintenance']+counts['heating_plant']>0
    assert len({d['event_id'] for d in ds})==len(ds)
    for d in ds:
        if d['action']=='optimize_energy':
            assert d['proposal_only'] is True
            assert execute_decision(d)['status']=='proposal_only_not_dispatched'
        if d['action']=='release_room':
            assert execute_decision(d)['status']!='simulated_completed'
        if d['action']=='notify_guest':
            assert execute_decision(d)['status']!='simulated_completed'
    assert all(x['status']!='simulated_completed' for x in execute(ds) if x['action'] in ('release_room','optimize_energy','notify_guest'))
