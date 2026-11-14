"""S02/S04 counterfactuals and evidence-bounded impact claims."""
import pandas as pd
from core.detectors import detect_water, detect_equipment
from core.impact_evidence import summarize_impact

T = pd.date_range('2026-01-01T00:00:00Z', periods=4*24*7, freq='15min')

def water(flow, *, reset=False):
    readings = [i*flow for i in range(len(T))]
    if reset:
        readings[20] = readings[19] - 2
    return {'room_water': pd.DataFrame({'room_id':'R101','timestamp_utc':T,'meter_total_l':readings}),
            'water_main':pd.DataFrame({'timestamp_utc':T,'meter_total_l':readings})}

def equipment(values, metric='filter_dp_pa', asset='AHU1'):
    return {'equipment':pd.DataFrame({'timestamp_utc':T[:len(values)],'asset_id':asset,
                                     'metric':metric,'value':values}), 'weather':pd.DataFrame()}

def test_s02_zero_flow_no_false_leak():
    assert not [d for d in detect_water(water(0)) if d['issue_type']=='water_leak']

def test_s02_sustained_night_flow_triggers_inspection_and_consent():
    ds=detect_water(water(1))
    inspections=[d for d in ds if d['action']=='request_inspection']
    assert inspections and all(d['requires_guest_consent'] and d['requires_human_approval'] for d in inspections)

def test_s02_single_reset_does_not_imply_confirmed_leak():
    ds=detect_water(water(0,reset=True))
    assert not [d for d in ds if d['issue_type']=='water_leak']

def test_s04_healthy_filter_no_maintenance():
    ds=detect_equipment(equipment([100 + (i%5) for i in range(len(T))]))
    assert not [d for d in ds if d['issue_type']=='ventilation_maintenance']

def test_s04_two_day_pressure_rise_requires_approval():
    values=[100 if i < 4*24*4 else 170 for i in range(len(T))]
    ds=detect_equipment(equipment(values))
    matches=[d for d in ds if d['issue_type']=='ventilation_maintenance']
    assert matches and all(d['requires_human_approval'] for d in matches)

def test_s04_single_day_spike_does_not_trigger_maintenance():
    values=[170 if 4*24*4 <= i < 4*24*5 else 100 for i in range(len(T))]
    assert not [d for d in detect_equipment(equipment(values)) if d['issue_type']=='ventilation_maintenance']

def test_s04_single_lockout_escalates_without_auto_restart():
    ds=detect_equipment(equipment(['running']*10+['lockout']+['running']*10,'status','HP1'))
    assert any(d['issue_type']=='heating_plant' and d['requires_human_approval'] for d in ds)
    assert not any(d['action']=='restart_heat_pump' for d in ds)

def test_impact_proposals_are_not_measured_savings():
    d={'event_id':'a','timestamp_utc':'2026-01-01T00:00:00Z','action':'optimize_energy',
       'reason':'estimated gross tariff benefit EUR 5.20', 'issue_type':'energy_optimization'}
    result=summarize_impact([d])
    assert result['energy']['sum_of_individual_gross_estimates_eur']==5.2
    assert result['energy']['realized_savings_eur'] is None
    assert result['energy']['estimated_savings_eur'] is None
    assert result['operations']['confirmed_successes']==0

def test_learning_cannot_self_certify_without_measurement():
    result=summarize_impact([],learning={'recommendations':[
        {'status':'verified'}, {'status':'verified','validation_evidence_refs':['inspection:1'],'measured_outcome':3},
        {'status':'proposed_not_verified','validation_evidence_refs':['inspection:2'],'measured_outcome':4}]})
    assert result['learning']['verified_recommendations']==1
    assert result['learning']['unverified_recommendations']==2
