import pandas as pd
from core.scheduler import Scheduler
from core.weekend_planner import plan_weekend

UTC = 'UTC'
def time(s): return pd.Timestamp(s, tz=UTC)

class Data:
    def __init__(self, bookings):
        self.tables = {'bookings': pd.DataFrame(bookings)}
    def __getitem__(self, name): return self.tables[name]

def booking(room, dep, arr):
    return {'room_id': room, 'departure_utc': time(dep), 'arrival_utc': time(arr),
            'created_utc': time('2026-01-09 08:00'), 'status': 'confirmed'}

def roster(status='available', end='2026-01-10 16:00'):
    return pd.DataFrame([{'resource_id':'C1','role':'cleaner','start_utc':time('2026-01-10 07:00'),
                          'end_utc':time(end),'status':status,'status_known_utc':time('2026-01-09 08:00')}])

def actions(ds, action): return [d for d in ds if d['action']==action]

def test_two_turnovers_are_scheduled_without_double_booking():
    data=Data([booking('R1','2026-01-10 08:00','2026-01-10 11:00'),
               booking('R2','2026-01-10 08:00','2026-01-10 11:00')])
    sched=Scheduler(roster())
    ds=plan_weekend(data,sched)
    assert len(actions(ds,'schedule_cleaning'))==2
    assert not actions(ds,'request_human_approval')
    assert len(sched.reservations)==2
    (a,sa,ea),(b,sb,eb)=sched.reservations
    assert a==b=='C1' and (ea<=sb or eb<=sa)

def test_sick_cleaner_and_robot_cannot_create_capacity():
    r=roster(status='sick')
    r=pd.concat([r,pd.DataFrame([{'resource_id':'BOT1','role':'robot',
        'start_utc':time('2026-01-10 00:00'),'end_utc':time('2026-01-11 00:00'),
        'status':'available','status_known_utc':time('2026-01-09 08:00')}])],ignore_index=True)
    ds=plan_weekend(Data([booking('R1','2026-01-10 08:00','2026-01-10 09:00')]),Scheduler(r))
    assert not actions(ds,'schedule_cleaning')
    assert len(actions(ds,'request_human_approval'))==1
    assert len(actions(ds,'notify_guest'))==1
    assert actions(ds,'request_human_approval')[0]['requires_human_approval']

def test_existing_turnaround_cleaning_is_not_rescheduled():
    b=booking('R1','2026-01-10 08:00','2026-01-10 11:00')
    existing=[{'issue_type':'room_turnaround','action':'schedule_cleaning','episode_id':'TURN-R1-2026-01-10'}]
    ds=plan_weekend(Data([b]),Scheduler(roster()),existing)
    assert ds==[]

def test_late_booking_is_not_known_in_morning():
    b=booking('R1','2026-01-10 08:00','2026-01-10 11:00')
    b['created_utc']=time('2026-01-10 10:00')
    assert plan_weekend(Data([b]),Scheduler(roster()))==[]

def test_no_room_turnover_if_arrival_precedes_departure():
    b=booking('R1','2026-01-10 12:00','2026-01-10 09:00')
    assert plan_weekend(Data([b]),Scheduler(roster()))==[]

def test_no_slot_before_arrival_escalates():
    b=booking('R1','2026-01-10 08:00','2026-01-10 08:30')
    ds=plan_weekend(Data([b]),Scheduler(roster()))
    assert not actions(ds,'schedule_cleaning')
    assert len(actions(ds,'request_human_approval'))==1
    msg=actions(ds,'notify_guest')[0]
    assert msg['dependencies']==[actions(ds,'request_human_approval')[0]['event_id']]
