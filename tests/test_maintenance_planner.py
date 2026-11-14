import pandas as pd
from types import SimpleNamespace
from core.maintenance_planner import plan_maintenance
from core.scheduler import Scheduler
from core.decisions import make

T = pd.Timestamp('2026-01-12T09:00:00Z')

def data(orders=None):
    return {'work_orders': pd.DataFrame(orders or [], columns=['work_order_id','asset_id','created_utc','completed_utc','status'])}

def alert(asset='AHU1', issue='ventilation_maintenance'):
    return make(T,[asset],issue,'request_human_approval','high','Measured degradation',['equipment.csv:measured'],f'CASE-{asset}',approval=True)

def roster(status='scheduled', resource='TECH_1'):
    return pd.DataFrame([dict(resource_id=resource,role='technician',start_utc=T,end_utc=T+pd.Timedelta('8h'),status=status,status_known_utc=T-pd.Timedelta('1h'))])

def test_real_technician_slot_requires_approval():
    x=plan_maintenance(data(),Scheduler(roster()),[alert()])[0]
    assert x['action']=='dispatch_technician' and x['requires_human_approval']
    assert x['resource_id']=='TECH_1' and '09:00:00Z' in x['reason']

def test_absent_technician_is_not_allocated():
    s=Scheduler(pd.concat([roster(),roster('sick')],ignore_index=True))
    x=plan_maintenance(data(),s,[alert()])[0]
    assert x['action']=='request_human_approval' and 'resource_id' not in x

def test_no_technician_is_not_invented():
    x=plan_maintenance(data(),Scheduler(pd.DataFrame()),[alert()])[0]
    assert x['action']=='request_human_approval' and 'external' in x['reason']

def test_known_open_work_order_prevents_duplicate_dispatch():
    order=['WO1','AHU1',T-pd.Timedelta('1h'),pd.NaT,'open']
    x=plan_maintenance(data([order]),Scheduler(roster()),[alert()])[0]
    assert x['action']=='flag_anomaly' and 'work_orders.csv:WO1' in x['evidence']

def test_future_work_order_is_not_used_early():
    order=['WO1','AHU1',T+pd.Timedelta('1h'),pd.NaT,'open']
    x=plan_maintenance(data([order]),Scheduler(roster()),[alert()])[0]
    assert x['action']=='dispatch_technician'

def test_completed_later_is_open_at_decision_time():
    order=['WO1','AHU1',T-pd.Timedelta('1h'),T+pd.Timedelta('1h'),'completed']
    x=plan_maintenance(data([order]),Scheduler(roster()),[alert()])[0]
    assert x['action']=='flag_anomaly'

def test_data_quality_alert_not_converted_to_service():
    a=make(T,['AHU1'],'data_quality','flag_anomaly','medium','Frozen sensor',['equipment.csv:missing'],'GAP')
    assert plan_maintenance(data(),Scheduler(roster()),[a])==[a]

def test_two_assets_do_not_double_book_technician():
    s=Scheduler(roster())
    out=plan_maintenance(data(),s,[alert('AHU1'),alert('HP1','heating_plant')])
    assert len(out)==2 and len(s.reservations)==2
    assert s.reservations[0][2] <= s.reservations[1][1]
