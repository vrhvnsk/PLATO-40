from analysis.insights import build_learning_candidates, generate


def test_candidates_are_traceable_and_not_claimed_as_proven():
    rows = [dict(event_id=f'D{i}', episode_id=f'E{i}', issue_type='water_leak',
                 affected_assets=['R101'], timestamp_utc=f'2026-01-0{i}T00:00:00Z',
                 confidence=0.7) for i in range(1, 4)]
    candidates = build_learning_candidates(rows)
    assert any(c['audience'] == 'CLARA' and 'R101' in c['title'] for c in candidates)
    assert any(c['audience'] == 'PLATO' for c in candidates)
    assert all(c['status'] == 'hypothesis_not_validated' for c in candidates)
    assert all(c['sample_episode_ids'] for c in candidates)
    assert 'not demonstrated learning gains' in generate(rows, None)


def test_single_episode_does_not_create_recurrence_or_design_claim():
    rows = [dict(event_id='D1', episode_id='E1', issue_type='water_leak',
                 affected_assets=['R101'], timestamp_utc='2026-01-01T00:00:00Z')]
    candidates = build_learning_candidates(rows)
    assert len(candidates) == 1
    assert candidates[0]['audience'] == 'CLARA'
