from collections import Counter
from pathlib import Path
from core.loader import Data
from core.scheduler import Scheduler
from core.detectors import detect_energy, detect_logistics
from core.safety import validate


def fixture():
    return Data(Path(__file__).parents[1] / 'data' / 'quickstart')


def test_energy_proposals_are_causal_and_non_actuating():
    data = fixture()
    decisions = validate(detect_energy(data))
    assert decisions
    assert all(x['action'] == 'optimize_energy' for x in decisions)
    assert all('Heating setpoints and occupied comfort remain unchanged' in x['reason'] for x in decisions)
    assert all(('not a forecast' in x['reason'] or 'No PV proxy available' in x['reason']) for x in decisions)
    assert all('tariff.csv:' in ' '.join(x['evidence']) for x in decisions)


def test_logistics_resource_and_evidence():
    data = fixture()
    sched = Scheduler(data['staff_roster'])
    decisions = validate(detect_logistics(data, sched))
    assert decisions
    assert any(x['action'] == 'dispatch_robot' for x in decisions)
    assert any(x['action'] == 'order_service' for x in decisions)
    assert all('logistics.csv:' in ' '.join(x['evidence']) for x in decisions)
    assert all(x.get('resource_id') for x in decisions if x['action'] == 'dispatch_robot')
    assert all(x['requires_human_approval'] for x in decisions if x['action'] == 'order_service')
