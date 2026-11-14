"""Independent Batch 2 regression tests; no proprietary dataset required."""
from datetime import datetime
from core.assurance import audit
from core.learning import feedback
from core.retrospective_verification import verify


def decision(eid, action='schedule_cleaning', issue='occupancy_surge', **kwargs):
    return {'event_id': eid, 'timestamp_utc': '2026-01-01T08:00:00Z',
            'episode_id': eid, 'issue_type': issue, 'action': action,
            'affected_assets': ['R101'], 'evidence': ['staff_roster.csv:resource=C1:slot=2026-01-01T08:00:00Z'],
            'verification_plan': 'Observe completion', 'requires_human_approval': False,
            'dependencies': [], **kwargs}


def test_missing_dependencies_and_future_dependency():
    first = decision('a')
    second = decision('b')
    second['dependencies'] = ['a', 'missing']
    first['timestamp_utc'] = '2026-01-02T08:00:00Z'
    codes = [f['code'] for f in audit([first, second])['findings']]
    assert 'missing_dependency' in codes and 'future_dependency' in codes


def test_room_release_requires_observed_completion():
    result = audit([decision('a', action='release_room')])
    assert 'release_without_completion_evidence' in result['finding_counts']


def test_approval_gate_is_required():
    result = audit([decision('a', action='order_service')])
    assert 'missing_approval_gate' in result['finding_counts']


def test_duplicate_episode_action_is_reported():
    x, y = decision('a'), decision('b')
    y['episode_id'] = x['episode_id']
    assert 'repeated_episode_action' in audit([x, y])['finding_counts']


def test_same_resource_start_is_only_warning():
    findings = audit([decision('a'), decision('b')])['findings']
    assert any(f['code'] == 'same_resource_start' and f['severity'] == 'warning' for f in findings)


def test_feedback_has_no_fake_impact():
    decisions = [decision('a')]
    result = feedback(decisions, audit(decisions))
    assert result['recommendations']
    assert all(r['impact_estimate'] is None and r['status'] == 'proposed_not_verified'
               for r in result['recommendations'])


def test_later_cleaning_is_not_treated_as_confirmed_job():
    result = verify([decision('a')], [{'type': 'cleaning_completed', 'room_id': 'R101',
                                      'timestamp_utc': '2026-01-01T09:00:00Z'}])
    assert result['entries'][0]['status'] == 'candidate_observation'


def test_future_observation_not_matched():
    result = verify([decision('a')], [{'type': 'cleaning_completed', 'room_id': 'R101',
                                      'timestamp_utc': '2026-01-03T09:00:00Z'}])
    assert result['entries'][0]['status'] == 'unverified'


def test_no_mutation():
    x = decision('a')
    original = repr(x)
    audit([x]); feedback([x], audit([x])); verify([x])
    assert repr(x) == original
