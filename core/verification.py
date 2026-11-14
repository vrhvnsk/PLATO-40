"""Replay evidence is not proof that a simulated intervention caused an outcome."""
import pandas as pd

def verify(decisions,data):
    ev=data.events
    out=[]
    for d in decisions:
        result={'event_id':d['event_id'],'status':'not_verified','note':'No post-action verification available; simulated actions do not alter historical data.'}
        if d['action']=='release_room':
            result.update(status='observed_prerequisite',note='Cleaning completion was observed in replay; no physical action performed.')
        elif d['issue_type']=='heating_comfort' and not data['room_telemetry'].empty:
            t=data['room_telemetry']; cutoff=pd.Timestamp(d['timestamp_utc'])
            if {'room_id','timestamp_utc','temperature_c'}.issubset(t.columns):
                q=t[(t.room_id==d['affected_assets'][0])&(t.timestamp_utc>cutoff)&(t.timestamp_utc<=cutoff+pd.Timedelta('2h'))]
                if len(q) and pd.to_numeric(q.temperature_c,errors='coerce').ge(20).any():
                    result.update(status='observed_recovery',note='Temperature recovered in replay; causation by simulated action is not established.')
        out.append(result)
    return out
