"""Regression tests for PLATO-40 detector incident safety and deduplication."""
import pandas as pd
from core.detectors import detect_turnaround, detect_comfort, detect_equipment


def utc(value):
    return pd.Timestamp(value, tz='UTC')


class FakeData(dict):
    @property
    def events(self):
        return self.get('events', pd.DataFrame())


class NoCleaner:
    def reserve(self, *args, **kwargs):
        return None


def test_cleaning_completion_cannot_release_two_turnarounds():
    events = pd.DataFrame([
        {'type': 'checkout_early', 'room_id': 'R308', 'timestamp_utc': utc('2026-01-05 08:00')},
        {'type': 'checkout_early', 'room_id': 'R308', 'timestamp_utc': utc('2026-01-06 08:00')},
        {'type': 'cleaning_completed', 'room_id': 'R308', 'timestamp_utc': utc('2026-01-07 10:00')},
    ])
    bookings = pd.DataFrame([{
        'room_id': 'R308', 'departure_utc': utc('2026-01-10 09:00'),
        'arrival_utc': utc('2026-01-11 15:00'), 'status': 'confirmed'
    }])
    data = FakeData(events=events, bookings=bookings, guest_requests=pd.DataFrame())
    decisions = detect_turnaround(data, NoCleaner())
    releases = [d for d in decisions if d['action'] == 'release_room']
    assert len(releases) == 1, releases
    assert releases[0]['evidence'] == [
        'events.jsonl:cleaning_completed:R308:2026-01-07T10:00:00Z'
    ]
    assert not releases[0]['dependencies']  # No unapproved staffing dependency


def comfort_data(times):
    telemetry = pd.DataFrame([{
        'room_id': 'R101', 'timestamp_utc': utc(t),
        'temperature_c': 19.0, 'window_open': 0
    } for t in times])
    bookings = pd.DataFrame([{
        'room_id': 'R101', 'arrival_utc': utc('2026-01-05 00:00'),
        'departure_utc': utc('2026-01-06 00:00'), 'status': 'confirmed'
    }])
    return FakeData(room_telemetry=telemetry, bookings=bookings)


def test_telemetry_gap_does_not_justify_heating_escalation():
    # One hour of readings starts an incident; a long gap follows.
    times = [f'2026-01-05 {h:02d}:{m:02d}' for h, m in
             [(8, 0), (8, 15), (8, 30), (8, 45), (9, 0),
              (11, 15), (11, 30), (11, 45)]]
    decisions = detect_comfort(comfort_data(times))
    assert sum(d['action'] == 'adjust_room_setpoint' for d in decisions) == 1
    assert not any(d['action'] == 'request_human_approval' for d in decisions)


def test_continuous_cold_telemetry_can_escalate_once():
    times = pd.date_range('2026-01-05 08:00', '2026-01-05 11:30', freq='15min', tz='UTC')
    telemetry = pd.DataFrame({
        'room_id': ['R101'] * len(times), 'timestamp_utc': times,
        'temperature_c': [19.0] * len(times), 'window_open': [0] * len(times)
    })
    data = comfort_data([])
    data['room_telemetry'] = telemetry
    decisions = detect_comfort(data)
    adjustments = [d for d in decisions if d['action'] == 'adjust_room_setpoint']
    escalations = [d for d in decisions if d['action'] == 'request_human_approval']
    assert len(adjustments) == 1
    assert len(escalations) == 1
    assert escalations[0]['dependencies'] == [adjustments[0]['event_id']]


def equipment_data(rows):
    return FakeData(equipment=pd.DataFrame(rows), weather=pd.DataFrame())


def test_nearby_heat_pump_lockouts_are_one_incident():
    times = ['2026-01-05 09:00', '2026-01-05 22:00',
             '2026-01-06 10:00', '2026-01-10 09:00']
    rows = [{'timestamp_utc': utc(t), 'asset_id': 'HP1',
             'metric': 'status', 'value': 'lockout_high_pressure'} for t in times]
    decisions = detect_equipment(equipment_data(rows))
    lockouts = [d for d in decisions if d['episode_id'].startswith('HP1-LOCKOUT-')]
    assert len(lockouts) == 2
    assert [d['timestamp_utc'] for d in lockouts] == [
        '2026-01-05T09:00:00Z', '2026-01-10T09:00:00Z'
    ]
    assert all(d['requires_human_approval'] for d in lockouts)


def test_missing_ahu_readings_do_not_reset_unresolved_incident():
    # Baseline, high pressure for two days, a missing-data interval,
    # then high pressure again without any measured recovery.
    readings = [
        ('2026-01-01', 100), ('2026-01-02', 100),
        ('2026-01-03', 100), ('2026-01-04', 100),
        ('2026-01-05', 160), ('2026-01-06', 170),
        ('2026-01-10', 240), ('2026-01-11', 250),
    ]
    rows = [{'timestamp_utc': utc(day), 'asset_id': 'AHU1',
             'metric': 'filter_dp_pa', 'value': value} for day, value in readings]
    decisions = detect_equipment(equipment_data(rows))
    filter_alerts = [d for d in decisions if d['issue_type'] == 'ventilation_maintenance']
    assert len(filter_alerts) == 1, filter_alerts
    assert filter_alerts[0]['timestamp_utc'] == '2026-01-07T00:00:00Z'
