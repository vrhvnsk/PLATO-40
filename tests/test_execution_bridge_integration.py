"""End-to-end mock safety and lifecycle integration tests."""
import json
from pathlib import Path
from core.decisions import make
from core.safety import validate
from core.executor import execute
from core.execution_bridge import bridge, write_bridge_report
from run import run

T = '2026-01-01T12:00:00Z'


def decision(action, *, asset='R101', approval=False, consent=False, resource=None, dependencies=None, evidence=None):
    return make(T, [asset], 'room_turnaround', action, 'high', 'test',
                evidence or ['test:evidence'], 'EP-' + action,
                approval=approval, consent=consent, resource=resource,
                dependencies=dependencies)


def test_end_to_end_safety_gates_and_bridge(tmp_path):
    clean = decision('schedule_cleaning', resource='C1')
    release = decision('release_room', evidence=['cleaning_completed:R101'], dependencies=[clean['event_id']])
    guest = decision('notify_guest', dependencies=[release['event_id']])
    technician = decision('dispatch_technician', approval=True, consent=True, resource='TECH1')
    decisions = validate([clean, release, guest, technician])
    records = execute(decisions)
    by_id = {r['event_id']: r for r in records}
    assert by_id[clean['event_id']]['status'] == 'pending_resource'
    assert by_id[release['event_id']]['status'] == 'pending_dependency'
    assert by_id[guest['event_id']]['status'] == 'pending_dependency'
    assert by_id[technician['event_id']]['status'] == 'pending_approval_and_consent'
    lifecycle, audit = bridge(decisions, records)
    assert all(x['outcome_status'] == 'unknown' for x in lifecycle)
    assert all(not x['execution_confirmed'] for x in audit)
    report = write_bridge_report(tmp_path, decisions, records)
    assert report['outcome_counts'] == {'unknown': 4}


def test_simulated_completion_does_not_satisfy_dependency():
    clean = decision('schedule_cleaning', resource='C1')
    release = decision('release_room', evidence=['cleaning_completed:R101'], dependencies=[clean['event_id']])
    context = {'resource_confirmations': {clean['event_id']: 'C1'},
               'safety_confirmations': {release['event_id']: {'room_clean_verified': {'verified': True, 'assets': ['R101']}}}}
    results = execute([clean, release], context=context)
    assert next(x for x in results if x['event_id'] == clean['event_id'])['status'] == 'simulated_completed'
    assert next(x for x in results if x['event_id'] == release['event_id'])['status'] == 'pending_dependency'
    lifecycle, _ = bridge([clean, release], results)
    assert all(x['outcome_status'] == 'unknown' for x in lifecycle)


def test_wrong_asset_attestation_cannot_release_room():
    d = decision('release_room', evidence=['cleaning_completed:R101'])
    ctx = {'safety_confirmations': {d['event_id']: {'room_clean_verified': {'verified': True, 'assets': ['R102']}}}}
    assert execute([d], context=ctx)[0]['status'] == 'pending_verification'


def test_duplicate_and_resource_conflict():
    a = decision('schedule_cleaning', resource='C1', asset='R101')
    b = decision('schedule_cleaning', resource='C1', asset='R102')
    ctx = {'resource_confirmations': {a['event_id']: 'C1', b['event_id']: 'C1'}}
    results = execute([a, b, a], context=ctx)
    assert [r['status'] for r in results].count('simulated_completed') == 1
    assert [r['status'] for r in results].count('blocked') == 2


def test_quickstart_pipeline_and_bridge(tmp_path):
    root = Path(__file__).resolve().parents[1]
    decisions = run(root / 'data' / 'quickstart', tmp_path / 'decisions.jsonl')
    assert decisions
    log = [json.loads(x) for x in (tmp_path / 'execution_log.jsonl').read_text().splitlines()]
    assert len(log) == len(decisions)
    summary = json.loads((tmp_path / 'reports' / 'executor_bridge' / 'executor_bridge_summary.json').read_text())
    assert summary['outcome_counts'] == {'unknown': len(decisions)}
    assert 'simulated_completed' in summary['executor_statuses'] or 'pending_resource' in summary['executor_statuses']
