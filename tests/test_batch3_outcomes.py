from core.outcome_verification import verify_outcomes, evaluate

D = {'event_id': 'D1', 'timestamp_utc': '2026-01-01T00:00:00Z',
     'action': 'request_human_approval', 'requires_human_approval': True,
     'verification_plan': 'Check result', 'evidence': ['sensor:1']}


def test_unobserved_is_unknown():
    r = verify_outcomes([D])[0]
    assert r['lifecycle_status'] == 'awaiting_approval'
    assert r['outcome_status'] == 'unknown'


def test_approval_and_execution_without_outcome():
    events = [
        {'decision_id': 'D1', 'status': 'approved', 'timestamp_utc': '2026-01-01T01:00:00Z'},
        {'decision_id': 'D1', 'status': 'executed', 'timestamp_utc': '2026-01-01T02:00:00Z', 'evidence_ref': 'job:2'},
    ]
    r = verify_outcomes([D], events)[0]
    assert r['lifecycle_status'] == 'executed'
    assert r['outcome_status'] == 'unknown'


def test_attributable_observation():
    events = [
        {'decision_id': 'D1', 'status': 'approved', 'timestamp_utc': '2026-01-01T01:00:00Z'},
        {'decision_id': 'D1', 'status': 'executed', 'timestamp_utc': '2026-01-01T02:00:00Z', 'evidence_ref': 'job:2'},
    ]
    obs = [{'decision_id': 'D1', 'timestamp_utc': '2026-01-01T03:00:00Z', 'outcome': 'success', 'evidence_ref': 'inspection:3'}]
    assert verify_outcomes([D], events, obs)[0]['outcome_status'] == 'confirmed_success'


def test_unlinked_observation_is_not_proof():
    obs = [{'timestamp_utc': '2026-01-01T03:00:00Z', 'outcome': 'success', 'evidence_ref': 'sensor:3'}]
    assert verify_outcomes([D], observations=obs)[0]['outcome_status'] == 'unknown'


def test_unapproved_execution_not_accepted():
    ev = [{'decision_id': 'D1', 'status': 'executed', 'timestamp_utc': '2026-01-01T02:00:00Z', 'evidence_ref': 'job:2'}]
    r = verify_outcomes([D], ev)[0]
    assert r['outcome_status'] == 'unknown'
    assert 'execution_without_valid_approval' in r['warnings']


def test_predecision_observation_not_proof():
    ev = [
        {'decision_id': 'D1', 'status': 'approved', 'timestamp_utc': '2026-01-01T01:00:00Z'},
        {'decision_id': 'D1', 'status': 'executed', 'timestamp_utc': '2026-01-01T02:00:00Z', 'evidence_ref': 'job:2'},
    ]
    obs = [{'decision_id': 'D1', 'timestamp_utc': '2026-01-01T01:30:00Z', 'outcome': 'success', 'evidence_ref': 'sensor:3'}]
    r = verify_outcomes([D], ev, obs)[0]
    assert r['outcome_status'] == 'unknown'


def test_metrics():
    results = verify_outcomes([D])
    metrics = evaluate([D], results)
    assert metrics['verification_plan_coverage'] == 1
    assert metrics['outcome_counts']['unknown'] == 1
