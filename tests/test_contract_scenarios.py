import pytest
from core.decisions import make
from core.safety import validate
from core.executor import execute_decision
T='2026-01-01T10:00:00Z'
def d(action, **kwargs):
    return make(T,['R101'],'test',action,'medium','test',['sensor:1'],'episode',**kwargs)
def test_heating_target_required():
    with pytest.raises(ValueError,match='Setpoint'):validate([d('adjust_room_setpoint')])
    assert validate([d('adjust_room_setpoint',target_setpoint_c=21)])[0]['target_setpoint_c']==21
def test_energy_proposal_not_dispatchable():
    x=d('optimize_energy',proposal_only=True)
    assert validate([x])[0]['autonomy']=='proposal_only'
    assert execute_decision(x)['status']=='proposal_only_not_dispatched'
    with pytest.raises(ValueError,match='proposal-only'):validate([d('optimize_energy')])
def test_unresolved_guest_blocked():
    x=d('notify_guest');validate([x]);assert x['recipient_resolution']=='manual_review_required'
    assert execute_decision(x)['status']=='blocked'
def test_guest_booking_trace():
    assert execute_decision(d('notify_guest',recipient_booking_ids=['BK123']))['status']=='proposed_not_sent'
def test_release_needs_fresh_verification():
    x=d('release_room',readiness_evidence={'room_id':'R101','cleaning_completed_utc':T,'status':'candidate_requires_fresh_housekeeping_check'})
    x['evidence']=['events.jsonl:cleaning_completed:R101:'+T]
    validate([x]);assert execute_decision(x)['status']=='pending_verification'
