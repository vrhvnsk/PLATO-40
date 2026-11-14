"""S05: conservative capacity planning from confirmed, known room turnovers.

Robots are never counted as room-cleaning capacity: their ability to clean rooms
is not established by the staff roster. No on-call staff is presumed available.
"""
import pandas as pd
from .decisions import make, iso

TZ = 'Europe/Vienna'
DURATION = pd.Timedelta('45min')


def _ready(df, *cols):
    return not df.empty and set(cols).issubset(df.columns)


def plan_weekend(data, sched, existing_decisions=()):
    bookings = data['bookings']
    if not _ready(bookings, 'room_id', 'arrival_utc', 'departure_utc', 'created_utc'):
        return []
    bookings = bookings.copy()
    if 'status' in bookings:
        bookings = bookings[bookings.status == 'confirmed']
    bookings = bookings.dropna(subset=['room_id', 'arrival_utc', 'departure_utc', 'created_utc'])
    if bookings.empty:
        return []

    # Existing turnaround decisions may already reserve a cleaner. Don't
    # silently assign another one to the same room/day.
    handled = set()
    for d in existing_decisions:
        if d.get('issue_type') != 'room_turnaround':
            continue
        if d.get('action') != 'schedule_cleaning':
            continue
        ep = str(d.get('episode_id', ''))
        if ep.startswith('TURN-'):
            handled.add(ep[5:])

    days = sorted(set(bookings.departure_utc.dt.tz_convert(TZ).dt.date))
    decisions = []
    for day in days:
        # A day plan is made at 08:00 local; only bookings created by then count.
        t = pd.Timestamp(f'{day} 08:00', tz=TZ).tz_convert('UTC')
        known = bookings[bookings.created_utc <= t]
        departures = known[known.departure_utc.dt.tz_convert(TZ).dt.date == day]
        arrivals = known[known.arrival_utc.dt.tz_convert(TZ).dt.date == day]
        if departures.empty or arrivals.empty:
            continue
        tasks = []
        for room in sorted(set(departures.room_id.astype(str)) & set(arrivals.room_id.astype(str))):
            # Actual turnover: a departure precedes a later arrival on same day.
            deps = departures[departures.room_id.astype(str) == room].departure_utc
            arrs = arrivals[arrivals.room_id.astype(str) == room].arrival_utc
            valid = [(dep, arr) for dep in deps for arr in arrs if dep <= arr]
            if not valid:
                continue
            dep, arr = min(valid, key=lambda p: (p[1], p[0]))
            if f'{room}-{day}' in handled:
                continue
            tasks.append((arr, dep, room))
        if not tasks:
            continue

        # Earliest arrivals first. Search real 15-minute slots covered by a
        # complete known cleaner shift. Existing reservations are respected.
        uncovered = []
        assigned = []
        for arrival, departure, room in sorted(tasks):
            start = max(t, departure)
            end_limit = arrival
            assignment = None
            slot = start
            while slot + DURATION <= end_limit:
                rid = sched.reserve('cleaner', slot, slot + DURATION, t)
                if rid is not None:
                    assignment = (rid, slot)
                    break
                slot += pd.Timedelta('15min')
            if assignment is None:
                uncovered.append((room, departure, arrival))
                continue
            rid, slot = assignment
            evidence = [f'bookings.csv:turnover:{room}:departure={iso(departure)}:arrival={iso(arrival)}',
                        f'staff_roster.csv:cleaner={rid}:slot={iso(slot)}']
            d = make(t, [room], 'occupancy_surge', 'schedule_cleaning', 'high',
                     f'Plan a 45-minute cleaner slot beginning {iso(slot)} before confirmed arrival {iso(arrival)}.',
                     evidence, f'SURGE-{day}-{room}', resource=rid,
                     expected='Cleaning scheduled, not yet completed',
                     verification='Check cleaning_completed and housekeeping readiness before releasing room.')
            decisions.append(d)
            assigned.append(room)

        if uncovered:
            evidence = [f'bookings.csv:known_turnovers={len(tasks)}:day={day}',
                        f'planner:assigned={len(assigned)}:uncovered={len(uncovered)}',
                        'staff_roster.csv:no_eligible_unreserved_cleaner_slot_for_uncovered_tasks']
            rooms = [room for room, _, _ in uncovered]
            approval = make(t, rooms, 'occupancy_surge', 'request_human_approval', 'high',
                            'Confirmed turnovers have no verified cleaner slot before arrival. Request on-call staffing or manual reprioritisation; no additional capacity assumed.',
                            evidence, f'SURGE-{day}', approval=True,
                            verification='Confirm actual on-call acceptance, staffing and completed cleaning.')
            decisions.append(approval)
            # Warn only about genuinely uncovered rooms, never promise readiness.
            for room, dep, arr in uncovered:
                decisions.append(make(t, [room], 'occupancy_surge', 'notify_guest', 'medium',
                                      'PROPOSED: Room readiness is not yet confirmed. We will update you after housekeeping verification.',
                                      [f'bookings.csv:turnover:{room}:departure={iso(dep)}:arrival={iso(arr)}'],
                                      f'SURGE-{day}-{room}', dependencies=[approval['event_id']],
                                      recipient_booking_ids=recipient_bookings_for_surge(data['bookings'], room, t), verification='Confirm recipient and message delivery; do not promise a ready room.'))
    return decisions


def recipient_bookings_for_surge(bookings, room, at):
    from .detectors import recipient_bookings
    return recipient_bookings(bookings, room, at)
