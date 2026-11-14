from core.executor import execute_decision


def decision(action='release_room', **kw):
    return {'event_id': 'D1', 'timestamp_utc': '2026-11-13T10:00:00Z',
            'action': action, 'affected_assets': ['R101'], **kw}


def attestation(timestamp='2026-11-13T09:30:00Z', source='building_sensor'):
    return {'safety_confirmations': {'D1': {'room_clean_verified': {
        'verified': True, 'assets': ['R101'], 'timestamp_utc': timestamp,
        'source': source}}}, 'trusted_safety_sources': ['building_sensor']}


def test_fresh_allowlisted_attestation_allows_mock_release():
    assert execute_decision(decision(), attestation())['status'] == 'simulated_completed'


def test_untrusted_source_rejected():
    assert execute_decision(decision(), attestation(source='unknown'))['status'] == 'pending_verification'


def test_future_attestation_rejected():
    assert execute_decision(decision(), attestation(timestamp='2026-11-13T10:01:00Z'))['status'] == 'pending_verification'


def test_missing_timestamp_rejected():
    c = attestation()
    del c['safety_confirmations']['D1']['room_clean_verified']['timestamp_utc']
    assert execute_decision(decision(), c)['status'] == 'pending_verification'


def test_occupied_room_requires_consent_even_if_flag_false():
    d = decision('schedule_cleaning', resource_id='STAFF1', requires_guest_consent=False)
    c = {'occupied_rooms': ['R101'], 'resource_confirmations': {'D1': 'STAFF1'}}
    assert execute_decision(d, c)['status'] == 'pending_consent'


def test_occupied_room_with_consent_can_simulate():
    d = decision('schedule_cleaning', resource_id='STAFF1', requires_guest_consent=False)
    c = {'occupied_rooms': ['R101'], 'resource_confirmations': {'D1': 'STAFF1'}, 'consents': ['D1']}
    assert execute_decision(d, c)['status'] == 'simulated_completed'
