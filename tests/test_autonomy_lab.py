from core.autonomy_lab import simulate, evaluation, compare_policy


def d(eid, action='schedule_cleaning', **kw):
    return dict(event_id=eid, timestamp_utc='2026-01-01T10:00:00Z', action=action,
                priority='high', confidence=.9, **kw)


def test_determinism():
    ds = [d('a'), d('b')]
    assert simulate(ds) == simulate(list(reversed(ds)))


def test_resource_conflict():
    result = simulate([d('a'), d('b')], capacity={'cleaner': 1})
    assert [r['status'] for r in result] == ['simulated_action_completed', 'deferred_resource_conflict']


def test_human_gate():
    result = simulate([d('a', requires_human_approval=True)])
    assert result[0]['status'] == 'awaiting_human_approval'
    assert not result[0]['real_execution_confirmed']


def test_consent_gate():
    result = simulate([d('a', requires_guest_consent=True)])
    assert result[0]['status'] == 'awaiting_human_approval'


def test_no_promotion():
    rows = simulate([d('a')])
    assert compare_policy(rows)['promoted_candidates'] == 0
    assert evaluation(rows)['real_executions_verified'] == 0


def test_zero_capacity():
    assert simulate([d('a')], capacity={'cleaner': 0})[0]['status'] == 'deferred_resource_conflict'


def test_unsafe_action_not_autonomous():
    r = simulate([d('a', action='release_room')])[0]
    assert r['chosen_action'] == 'request_human_approval'


def test_no_mutation():
    ds = [d('a')]
    original = repr(ds)
    simulate(ds)
    assert repr(ds) == original
