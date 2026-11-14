"""Small synthetic fixture, independently created for tests; NOT official challenge data."""
from pathlib import Path
import json
import pandas as pd
p=Path(__file__).parent/'synthetic_fixture';p.mkdir(exist_ok=True)
base=pd.Timestamp('2026-01-06T00:00:00Z')
def write(name,rows):pd.DataFrame(rows).to_csv(p/(name+'.csv'),index=False)
write('bookings',[{'room_id':'R101','arrival_utc':str(base-pd.Timedelta('1d')),'departure_utc':str(base+pd.Timedelta('12h')),'status':'confirmed'}, {'room_id':'R101','arrival_utc':str(base+pd.Timedelta('14h')),'departure_utc':str(base+pd.Timedelta('3d')),'status':'confirmed'}])
write('staff_roster',[{'resource_id':'C1','role':'cleaner','start_utc':str(base+pd.Timedelta('7h')),'end_utc':str(base+pd.Timedelta('16h')),'status':'available','status_known_utc':str(base-pd.Timedelta('1d'))},{'resource_id':'BOT1','role':'robot','start_utc':str(base),'end_utc':str(base+pd.Timedelta('1d')),'status':'available','status_known_utc':str(base-pd.Timedelta('1d'))}])
write('guest_requests',[{'request_id':'Q1','timestamp_utc':str(base+pd.Timedelta('11h')),'room_id':'R101','request_type':'early_checkin','language':'de','response_due_utc':str(base+pd.Timedelta('12h'))}])
rows=[]
for i in range(96):
    t=base+pd.Timedelta(minutes=15*i)
    rows.append({'room_id':'R101','timestamp_utc':str(t),'temperature_c':19 if i<8 else 21,'window_open':0})
write('room_telemetry',rows)
water=[]
for i in range(96*3):
    t=base-pd.Timedelta('2d')+pd.Timedelta(minutes=15*i)
    water.append({'room_id':'R101','timestamp_utc':str(t),'meter_total_l':100+i*0.5})
write('room_water',water)
write('water_main',[{'timestamp_utc':r['timestamp_utc'],'meter_total_l':200+i*0.7} for i,r in enumerate(water)])
write('logistics',[{'asset_id':'WASTE_F1','metric':'fill_pct','timestamp_utc':str(base+pd.Timedelta('10h')),'value':95}])
(p/'events.jsonl').write_text('\n'.join(json.dumps(x) for x in [{'event_id':'E1','type':'checkout_early','room_id':'R101','timestamp_utc':str(base+pd.Timedelta('10h'))},{'event_id':'E2','type':'cleaning_completed','room_id':'R101','timestamp_utc':str(base+pd.Timedelta('13h'))}])+'\n')
(p/'building.json').write_text(json.dumps({'name':'Fixture only','rooms':[{'id':'R101','floor':1}]}))
(p/'manifest.json').write_text(json.dumps({'profile':'fixture','note':'Not an official PLATO-40 dataset'}))
print(p)
