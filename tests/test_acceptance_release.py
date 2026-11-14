from scripts.validate_release import temporal_split
from core.autonomy_lab import simulate

def test_episode_disjoint_split():
    rows = [{'episode_id': str(i//2), 'event_id':str(i), 'timestamp_utc':f'2026-01-{i//2+1:02}T00:00:00'} for i in range(20)]
    a,b=temporal_split(rows)
    assert len(a)+len(b)==20
    assert {x['episode_id'] for x in a}.isdisjoint({x['episode_id'] for x in b})

def test_replay_deterministic():
    rows=[{'event_id':str(i), 'action':'schedule_cleaning', 'timestamp_utc':'2026-01-01T00:00:00'} for i in range(5)]
    assert simulate(rows)==simulate(rows)

def test_no_real_outcomes_claimed():
    r=simulate([{'event_id':'one','action':'schedule_cleaning','timestamp_utc':'2026-01-01T00:00:00'}])
    assert all(not x['real_outcome_verified'] for x in r)
