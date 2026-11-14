from core.executor import execute_decision, execute


def release():
    return {'event_id':'RELEASE1','timestamp_utc':'2026-11-13T10:00:00Z',
            'action':'release_room','affected_assets':['R101']}


def trusted():
    return {'trusted_safety_sources':['housekeeping'],
            'safety_confirmations':{'RELEASE1':{'room_clean_verified':{
                'verified':True,'assets':['R101'], 'source':'housekeeping',
                'timestamp_utc':'2026-11-13T09:55:00Z'}}}}


def test_valid_clean_empty_room_mock_release():
    assert execute_decision(release(),trusted())['status']=='simulated_completed'


def test_occupied_room_never_released_even_with_attestation():
    ctx=trusted();ctx['occupied_rooms']=['R101']
    result=execute_decision(release(),ctx)
    assert result['status']=='blocked'
    assert 'room_occupied' in result['missing_requirements']


def test_attestation_stale_at_execution_time():
    ctx=trusted();ctx['execution_time_utc']='2026-11-15T10:00:00Z'
    assert execute_decision(release(),ctx)['status']=='pending_verification'


def test_attestation_fresh_at_execution_time():
    ctx=trusted();ctx['execution_time_utc']='2026-11-13T10:02:00Z'
    assert execute_decision(release(),ctx)['status']=='simulated_completed'


def test_future_execution_clock_rejected():
    ctx=trusted();ctx['execution_time_utc']='invalid'
    assert execute_decision(release(),ctx)['status']=='pending_verification'


def test_duplicate_release_cannot_replay():
    ctx=trusted()
    assert [r['status'] for r in execute([release(),release()],context=ctx)]==['simulated_completed','blocked']
