from core.executor import execute, execute_decision


def decision(eid, action, assets=None, **kwargs):
    return {'event_id': eid, 'action': action, 'timestamp_utc': '2026-01-01T12:00:00Z',
            'affected_assets': assets or ['R101'], **kwargs}


def attest(eid, check, assets):
    return {'safety_confirmations': {eid: {check: {'verified': True, 'assets': assets}}}}


def test_global_clean_flag_cannot_release_room():
    d = decision('r1', 'release_room')
    assert execute_decision(d, {'room_clean_verified': True})['status'] == 'pending_verification'


def test_wrong_room_and_wrong_decision_attestations_rejected():
    d = decision('r1', 'release_room')
    assert execute_decision(d, attest('r1', 'room_clean_verified', ['R102']))['status'] == 'pending_verification'
    assert execute_decision(d, attest('r2', 'room_clean_verified', ['R101']))['status'] == 'pending_verification'
    assert execute_decision(d, attest('r1', 'room_clean_verified', ['R101']))['status'] == 'pending_verification'


def test_legacy_execute_cannot_bypass_safety():
    assert execute([decision('r1', 'release_room')])[0]['status'] == 'pending_verification'
    assert execute([decision('r1', 'release_room')], context={'room_clean_verified': True})[0]['status'] == 'pending_verification'


def test_global_resource_flag_cannot_assign_staff():
    d = decision('c1', 'schedule_cleaning', resource_id='C1')
    assert execute_decision(d, {'resource_available': True})['status'] == 'pending_resource'


def test_duplicate_and_resource_conflict():
    a = decision('c1', 'schedule_cleaning', resource_id='C1')
    b = decision('c2', 'schedule_cleaning', resource_id='C1')
    c = {'resource_confirmations': {'c1': 'C1', 'c2': 'C1'}}
    statuses = [r['status'] for r in execute([a, b, a], context=c)]
    assert statuses == ['simulated_completed', 'blocked', 'blocked']


def test_mock_completion_does_not_satisfy_dependency():
    a = decision('a', 'schedule_cleaning', resource_id='C1')
    b = decision('b', 'release_room', dependencies=['a'])
    c = {'resource_confirmations': {'a': 'C1'}, **attest('b', 'room_clean_verified', ['R101'])}
    statuses = [r['status'] for r in execute([a, b], context=c)]
    assert statuses == ['simulated_completed', 'pending_dependency']


def test_persistent_ledger_blocks_replay():
    ledger = set()
    c = {'execution_ledger': ledger}
    d = decision('a', 'flag_anomaly')
    assert execute([d], context=c)[0]['status'] == 'logged_only'
    assert execute([d], context=c)[0]['status'] == 'blocked'


def test_approval_is_decision_specific():
    d = decision('a', 'dispatch_technician', resource_id='T1')
    assert execute_decision(d, {'approvals': ['other'], 'resource_confirmations': {'a': 'T1'}})['status'] == 'pending_approval'
