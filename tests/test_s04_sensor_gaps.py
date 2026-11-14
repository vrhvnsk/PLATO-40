"""Regression test for sustained equipment sensor gaps in S04."""

import pandas as pd

from core.detectors import detect_equipment


def test_s04_flags_each_gap_at_the_eighth_missing_reading():
    timestamps = pd.date_range('2026-01-16T00:00:00Z', periods=42, freq='15min')
    missing_slots = {*range(1, 8), *range(9, 20), *range(21, 32), *range(33, 42)}
    equipment = pd.DataFrame([
        (timestamp, 'AHU1', 'filter_dp_pa', None if slot in missing_slots else 100 + slot)
        for slot, timestamp in enumerate(timestamps)
        if slot != 26  # Break continuity between two short runs.
    ] + [
        (timestamp, 'HP1', 'status', 'running') for timestamp in timestamps
    ], columns=['timestamp_utc', 'asset_id', 'metric', 'value'])

    decisions = detect_equipment({
        'equipment': equipment.sample(frac=1, random_state=4),
        'weather': pd.DataFrame(),
    })

    assert [decision['timestamp_utc'] for decision in decisions] == [
        '2026-01-16T04:00:00Z',
        '2026-01-16T10:00:00Z',
    ]
    for decision, start in zip(decisions, ('04:00', '10:00')):
        assert decision['affected_assets'] == ['AHU1']
        assert decision['issue_type'] == 'data_quality'
        assert decision['action'] == 'flag_anomaly'
        assert decision['requires_human_approval'] is False
        assert decision['evidence'][-1] == (
            f'equipment.csv:AHU1:filter_dp_pa:2026-01-16T{start}:00Z'
        )
