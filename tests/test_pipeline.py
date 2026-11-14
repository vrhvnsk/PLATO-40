import json
import pandas as pd
import pytest
from core.decisions import make
from core.safety import validate
from core.executor import execute
from core.scheduler import Scheduler
from run import run
from pathlib import Path

def test_contract_and_approval():
    d=make('2026-01-01T12:00:00Z',['R101'],'water_leak','request_inspection','high','Leak suspected',['meter'], 'EP1',consent=True)
    assert d['requires_human_approval'] and d['requires_guest_consent']
    assert execute([d])[0]['status']=='pending_approval_and_consent'
    assert execute([d],approvals=[d['event_id']])[0]['status']=='pending_consent'
    assert execute([d],approvals=[d['event_id']],consents=[d['event_id']])[0]['status']=='pending_resource'

def test_release_requires_cleaning():
    d=make('2026-01-01T12:00:00Z',['R101'],'room_turnaround','release_room','medium','Ready',['booking'], 'EP1')
    with pytest.raises(ValueError):validate([d])

def test_scheduler_no_double_booking():
    r=pd.DataFrame([{'role':'cleaner','resource_id':'C1','start_utc':pd.Timestamp('2026-01-01T08:00Z'),'end_utc':pd.Timestamp('2026-01-01T16:00Z'),'status':'available','status_known_utc':pd.Timestamp('2025-12-31T00:00Z')}])
    s=Scheduler(r)
    assert s.reserve('cleaner','2026-01-01T09:00Z','2026-01-01T10:00Z','2026-01-01T09:00Z')=='C1'
    assert s.reserve('cleaner','2026-01-01T09:30Z','2026-01-01T10:30Z','2026-01-01T09:30Z') is None

def test_fixture_end_to_end(tmp_path):
    root=Path(__file__).parents[1]
    decisions=run(root/'examples'/'synthetic_fixture',tmp_path/'decisions.jsonl')
    assert decisions
    assert (tmp_path/'insights.md').exists()
    assert (tmp_path/'execution_log.jsonl').exists()
    assert all('event_id' in d for d in decisions)
