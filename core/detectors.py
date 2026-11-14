"""Conservative scenario detectors. Only information available at decision time is cited."""
import pandas as pd
import numpy as np
from .decisions import make,iso

TZ='Europe/Vienna'

def required(df,*cols):return not df.empty and set(cols).issubset(df.columns)
def ts(x):return pd.Timestamp(x)
def local(x):return ts(x).tz_convert(TZ)
def episodes(times,gap):
    times=sorted(set(pd.Timestamp(t) for t in times if pd.notna(t)))
    groups=[]
    for t in times:
        if not groups or t-groups[-1][-1]>pd.Timedelta(gap):groups.append([t])
        else:groups[-1].append(t)
    return groups

def recipient_bookings(bookings, room, at):
    """Resolve only a unique, known-at-decision-time confirmed arrival booking."""
    if not required(bookings, 'booking_id', 'room_id', 'created_utc', 'arrival_utc'):
        return []
    candidates = bookings[(bookings.room_id.astype(str) == str(room)) &
                          (bookings.created_utc <= at) &
                          (bookings.arrival_utc >= at)]
    if 'status' in candidates:
        candidates = candidates[candidates.status == 'confirmed']
    if candidates.empty: return []
    first = candidates.arrival_utc.min()
    nearest = candidates[candidates.arrival_utc == first]
    return [str(nearest.iloc[0].booking_id)] if len(nearest) == 1 else []

def detect_turnaround(data,sched):
    out=[];ev=data.events; bk=data['bookings'];gr=data['guest_requests']
    if not required(bk,'room_id','departure_utc','arrival_utc'):return out
    if 'status' in bk:bk=bk[bk.status=='confirmed']
    triggers=[]
    if required(ev,'type','timestamp_utc','room_id'):
        for r in ev[ev.type.isin(['checkout_early','checkin_early','arrival_waiting_room'])].itertuples():
            triggers.append((r.timestamp_utc,str(r.room_id),str(r.type),None))
    if required(gr,'timestamp_utc','room_id','request_type'):
        for r in gr[gr.request_type.astype(str).str.contains('early|check',case=False,na=False)].itertuples():
            triggers.append((r.timestamp_utc,str(r.room_id),'guest_request',r))
    # Scheduled same-day turnover conflicts can be assessed at departure time.
    for r in bk.itertuples():
        if pd.notna(r.departure_utc) and pd.notna(r.arrival_utc) and r.arrival_utc>=r.departure_utc and r.arrival_utc-r.departure_utc<pd.Timedelta('3h'):
            triggers.append((r.departure_utc,str(r.room_id),'tight_turnaround',None))
    done={}
    if required(ev,'type','room_id','timestamp_utc'):
        for room,g in ev[ev.type=='cleaning_completed'].groupby('room_id'):
            done[str(room)]=sorted(g.timestamp_utc.dropna())
    seen=set()
    used_completions=set()
    for t,room,typ,req in sorted(triggers,key=lambda x:x[0]):
        if pd.isna(t) or room in ('nan','None'):continue
        day=local(t).date();ep=f'TURN-{room}-{day}'
        if ep in seen:continue
        seen.add(ep)
        shift_start=pd.Timestamp(f'{day} 07:00',tz=TZ).tz_convert('UTC')
        shift_end=pd.Timestamp(f'{day} 15:30',tz=TZ).tz_convert('UTC')
        start=max(t,shift_start);end=min(start+pd.Timedelta('45min'),shift_end)
        resource=sched.reserve('cleaner',start,end,t) if start<end else None
        departures=bk[bk.departure_utc.dt.tz_convert(TZ).dt.date==day]
        evidence=[f'event_or_request:{typ}:{room}:{iso(t)}',f'bookings.csv:departures={len(departures)}']
        guest_ids=[str(getattr(req,'request_id'))] if req is not None and hasattr(req,'request_id') else []
        if resource:
            a=make(t,[room],'room_turnaround','schedule_cleaning','high','Prioritise room turnaround; cleaner reserved for a 45-minute slot.',evidence+[f'staff_roster.csv:resource={resource}'],ep,resource=resource,expected='Cleaning scheduled',verification='Confirm cleaning_completed and housekeeping clean before release.',guest_ids=guest_ids)
        else:
            a=make(t,[room],'room_turnaround','request_human_approval','high','No full cleaning slot available; request staff coordination, do not promise room readiness.',evidence,ep,approval=True,verification='Approved staff assignment and observed cleaning completion.',guest_ids=guest_ids)
        out.append(a)
        lang=str(getattr(req,'language','en')) if req is not None else 'en'
        due=getattr(req,'response_due_utc',None) if req is not None else None
        msg=f'PROPOSED ({lang}): Your room is not confirmed ready yet. We will update you once housekeeping verifies readiness.'
        if due is not None and pd.notna(due):msg+=f' Respond by {iso(due)}.'
        out.append(make(t,[room],'room_turnaround','notify_guest','medium',msg,evidence,ep,dependencies=[a['event_id']],guest_ids=guest_ids,recipient_booking_ids=recipient_bookings(bk,room,t),verification='Verify booking recipient and delivery; manual review if unresolved.'))
        # Never infer successful cleaning from a proposed action.
        next_arrival=bk[(bk.room_id==room)&(bk.arrival_utc>=t)].arrival_utc.min()
        for completion in done.get(room,[]):
            completion_key=(room,completion)
            if completion_key in used_completions:
                continue
            if completion>=t and (pd.isna(next_arrival) or completion<=next_arrival) and not ((bk.room_id.astype(str)==room) & (bk.departure_utc>completion) & (bk.departure_utc<=completion+pd.Timedelta('24h'))).any():
                used_completions.add(completion_key)
                out.append(make(completion,[room],'room_turnaround','release_room','medium','Cleaning completion observed; release is simulated and must pass housekeeping check.',[f'events.jsonl:cleaning_completed:{room}:{iso(completion)}'],ep,expected='Room released in mock executor',verification='Housekeeping state is clean and room is released.',dependencies=([a['event_id']] if resource else []),readiness_evidence={'room_id':room,'cleaning_completed_utc':iso(completion),'source':'events.jsonl','status':'candidate_requires_fresh_housekeeping_check'}))
                break
    return out

def detect_surge(data, sched, existing_decisions=()):
    """S05 planner: schedule only evidenced capacity; escalate uncovered rooms."""
    from .weekend_planner import plan_weekend
    return plan_weekend(data, sched, existing_decisions)

def detect_water(data):
    out=[];rw=data['room_water'];wm=data['water_main']
    if not required(rw,'room_id','timestamp_utc','meter_total_l'):return out
    rw=rw.sort_values(['room_id','timestamp_utc']).copy()



    # Detect sustained cumulative-meter noise rather than alerting
    # separately for every negative reading.

    rw = rw.sort_values(["room_id", "timestamp_utc"]).copy()
    rw["flow"] = rw.groupby("room_id")["meter_total_l"].diff()


    for room, g in rw.groupby("room_id"):
        g = g.sort_values("timestamp_utc").copy()

        negative = g["flow"] < -0.05

        # A noisy period has at least 3 negative readings in 2 hours.
        negative_count = (
            negative.astype(int)
            .rolling(window=8, min_periods=8)
            .sum()
        )
        noisy = negative_count >= 3

        # Merge noisy observations separated by up to 24 hours.
        noisy_times = g.loc[noisy, "timestamp_utc"].tolist()
        for grp in episodes(noisy_times, "24h"):
            start = grp[0]
            end = grp[-1]
            episode_id = f"METERNOISE-{room}-{iso(start)}"

            out.append(make(
                start,
                [room],
                "data_quality",
                "flag_anomaly",
                "medium",
                "Repeated decreases in cumulative water-meter readings "
                "indicate unreliable telemetry, not confirmed consumption "
                "or a confirmed meter replacement.",
                [
                    f"room_water.csv:{room}:negative_readings",
                    f"room_water.csv:{room}:period={iso(start)}..{iso(end)}"
                ],
                episode_id,
                verification="Check meter diagnostics and maintenance "
                             "records; confirm readings become monotonic."
            ))

            # Exclude the affected period from consumption calculations.
            affected = (
                (rw.room_id == room)
                & (rw.timestamp_utc >= start - pd.Timedelta("2h"))
                & (rw.timestamp_utc <= end)
            )
            rw.loc[affected, "flow"] = np.nan

        # Isolated negative readings are invalid but do not
        # automatically constitute a separate incident.
        isolated = (rw.room_id == room) & (rw.flow < 0)
        rw.loc[isolated, "flow"] = np.nan

    rw.loc[rw.flow > 300, "flow"] = np.nan


   
    rw['local_day']=rw.timestamp_utc.dt.tz_convert(TZ).dt.date
    rw['local_hour']=rw.timestamp_utc.dt.tz_convert(TZ).dt.hour
    nights=rw[rw.local_hour.isin([2,3,4])].groupby(['room_id','local_day']).flow.agg(['min','count']).reset_index()
    nights=nights[(nights['count']>=8)&(nights['min']>0.3)]
    for room,g in nights.groupby('room_id'):
        days=sorted(g.local_day)
        for i in range(1,len(days)):
            if (days[i]-days[i-1]).days!=1:continue
            # Only first day of each consecutive run emits one incident.
            if i>1 and (days[i-1]-days[i-2]).days==1:continue
            t=pd.Timestamp(f'{days[i]} 05:15',tz=TZ).tz_convert('UTC')
            ep=f'LEAK-{room}-{days[i-1]}'
            evidence=[f'room_water.csv:night_flow:{room}:{days[i-1]}',f'room_water.csv:night_flow:{room}:{days[i]}']
            a=make(t,[room],'water_leak','flag_anomaly','high','Persistent nonzero night-time water flow across two nights; investigate possible running toilet.',evidence,ep,verification='Check for flow returning to baseline after repair.')
            out.append(a)
            out.append(make(t,[room],'water_leak','request_inspection','high','Inspection may require entering an occupied room; obtain approval and guest consent first.',evidence,ep,approval=True,consent=True,dependencies=[a['event_id']],verification='Inspect meter/fixture; verify subsequent night flow.'))
    if not required(wm,'timestamp_utc','meter_total_l'):return out
    main=wm.sort_values('timestamp_utc').copy()
    main['flow']=main.meter_total_l.diff()
    main.loc[(main.flow<0)|(main.flow>2000),'flow']=np.nan
    # Require >=90% room-meter coverage at each timestamp, rather than filling missing as zero.
    nrooms=rw.room_id.nunique()
    room_at=rw.groupby('timestamp_utc').flow.agg(['sum','count'])
    room_at=room_at[room_at['count']>=max(1,int(np.ceil(0.9*nrooms)))]
    joined=main.set_index('timestamp_utc')[['flow']].join(room_at,how='inner',rsuffix='_rooms').dropna()
    joined['gap']=joined['flow']-joined['sum']
    joined=joined[joined.index.tz_convert(TZ).hour.isin([2,3,4])]
    # Shift baseline by one sample, no future information.
    baseline=joined.gap.rolling('14D',min_periods=20).median().shift(1)
    hits=joined[(joined.gap-baseline)>np.maximum(5,baseline.abs()*0.5)]
    for group in episodes(hits.index,'36h'):
        if len(group)<8:continue
        t=group[7];ep=f'MAINLEAK-{iso(group[0])}'
        evidence=[f'water_main.csv-room_water.csv:gap:{iso(x)}' for x in group[:8]]
        out.append(make(t,['WM_MAIN'],'water_leak','dispatch_technician','high','Sustained unexplained main-minus-room water usage with adequate meter coverage; inspect shared pipework.',evidence,ep,approval=True,verification='Recheck main-room gap after service.'))
    return out



def detect_comfort(data):
    out = []
    tel = data["room_telemetry"]
    bk = data["bookings"]

    if not required(tel, "room_id", "timestamp_utc", "temperature_c"):
        return out
    if not required(bk, "room_id", "arrival_utc", "departure_utc"):
        return out

    if "status" in bk.columns:
        bk = bk[bk.status == "confirmed"]

    tel = tel.sort_values(["room_id", "timestamp_utc"]).copy()
    tel["temperature_c"] = pd.to_numeric(
        tel.temperature_c, errors="coerce"
    )
    tel.loc[
        ~tel.temperature_c.between(0, 40), "temperature_c"
    ] = np.nan

    for room, g in tel.groupby("room_id"):
        stays = bk[bk.room_id == room]
        if stays.empty:
            continue

        occ = pd.Series(False, index=g.index)
        for b in stays.itertuples():
            occ |= (
                (g.timestamp_utc >= b.arrival_utc)
                & (g.timestamp_utc < b.departure_utc)
            )

        window = (
            g.window_open != 1
            if "window_open" in g.columns
            else pd.Series(True, index=g.index)
        )

        eligible = occ & window & g.temperature_c.notna()
        g = g.loc[eligible].copy()

        if g.empty:
            continue

        # One active incident per room until recovery.
        active = False
        cold_start = None
        last_cold = None
        adjustment_time = None
        adjustment_id = None
        episode_id = None
        escalated = False

        for r in g.itertuples():
            t = r.timestamp_utc
            temp = r.temperature_c

            # Missing intervals must not prove sustained discomfort.
            if last_cold is not None and (
                t - last_cold > pd.Timedelta("20min")
            ):
                cold_start = None
                if not active:
                    last_cold = None

            # Recovery requires a clear temperature margin.
            if temp >= 20.5:
                active = False
                cold_start = None
                last_cold = None
                adjustment_time = None
                adjustment_id = None
                episode_id = None
                escalated = False
                continue

            if temp >= 20:
                # Do not start a new incident for a borderline reading.
                cold_start = None
                last_cold = None
                continue

            if cold_start is None and not active:
                cold_start = t

            last_cold = t

            # First action after at least 60 minutes of cold readings.
            if not active:
                if t - cold_start < pd.Timedelta("60min"):
                    continue

                episode_id = f"COLD-{room}-{iso(cold_start)}"
                evidence = [
                    f"room_telemetry.csv:{room}:{iso(cold_start)}:temperature<20",
                    f"room_telemetry.csv:{room}:{iso(t)}:temperature<20",
                ]

                action = make(
                    t,
                    [room],
                    "heating_comfort",
                    "adjust_room_setpoint",
                    "high",
                    "Occupied room below 20 C for at least 60 minutes.",
                    evidence,
                    episode_id,
                    expected="Setpoint adjustment in mock executor",
                    verification="Check temperature recovery within 2 hours.", target_setpoint_c=21.0
                )

                out.append(action)
                adjustment_time = t
                adjustment_id = action["event_id"]
                active = True
                continue

            # Escalate only when cold telemetry continuously supports it.
            if (
                active
                and not escalated
                and temp < 20
                and t - adjustment_time >= pd.Timedelta("2h")
            ):
                start = t - pd.Timedelta("2h")
                recent = g.loc[
                    (g.timestamp_utc >= start)
                    & (g.timestamp_utc <= t)
                ]
                sustained = (
                    len(recent) >= 2
                    and recent.timestamp_utc.iloc[0] <= start
                    and recent.temperature_c.lt(20).all()
                    and recent.timestamp_utc.diff().dropna()
                        .le(pd.Timedelta("20min")).all()
                )
                if sustained:
                    out.append(make(
                        t,
                        [room],
                        "heating_comfort",
                        "request_human_approval",
                        "high",
                        "Room remained below 20 C across two hours of "
                        "continuous observations; investigate heating performance.",
                        [f"room_telemetry.csv:{room}:{iso(t)}:temperature<20"],
                        episode_id,
                        approval=True,
                        dependencies=[adjustment_id],
                        verification="Inspect heating system and confirm recovery."
                    ))
                    escalated = True

    return out




def detect_equipment(data):
    """Causal S04 detection: statuses, AHU filter pressure and HP COP."""
    out = []
    eq, weather = data['equipment'], data['weather']
    if not required(eq, 'timestamp_utc', 'asset_id', 'metric', 'value'):
        return out
    eq = eq.copy().sort_values('timestamp_utc')
    eq['numeric_value'] = pd.to_numeric(eq.value, errors='coerce')

    # Count consecutive explicitly missing readings at the equipment cadence.
    cadence = pd.Timedelta(minutes=15)
    for (asset, metric), readings in eq.groupby(['asset_id', 'metric']):
        readings = readings.dropna(subset=['timestamp_utc'])
        missing = readings.value.isna().groupby(readings.timestamp_utc).all()
        boundaries = (~missing) | missing.index.to_series().diff().ne(cadence)
        consecutive = missing.groupby(boundaries.cumsum()).cumsum()
        for t in missing.index[missing & consecutive.eq(8)]:
            start = t - 7 * cadence
            out.append(make(
                t, [asset], 'data_quality', 'flag_anomaly', 'medium',
                f'{asset}.{metric} has eight consecutive missing 15-minute readings; check sensor telemetry.',
                [f'equipment.csv:{asset}:{metric}:{iso(start)}',
                 f'equipment.csv:{asset}:{metric}:{iso(t)}'],
                f'MISSING-{asset}-{metric}-{iso(start)}',
                verification='Confirm the sensor resumes reporting valid readings.',
            ))

    # Fault status is categorical, not a number. Group adjacent lockouts.
    statuses = eq[(eq.asset_id == 'HP1') & (eq.metric == 'status')].copy()
    lockouts = statuses[statuses.value.astype(str).str.contains('lockout', case=False, na=False)]
    # Treat closely recurring lockouts as one unresolved controller incident.
    # Grouping affects alert deduplication, not the initial detection time.
    for grp in episodes(lockouts.timestamp_utc, '48h'):
        t = grp[0]
        out.append(make(t, ['HP1'], 'heating_plant', 'request_human_approval',
                        'high', 'Heat-pump controller reports a lockout; request technician assessment before restarting.',
                        [f'equipment.csv:HP1:status:{iso(t)}'], f'HP1-LOCKOUT-{iso(t)}',
                        approval=True, verification='Review controller fault log and confirm safe restart.'))

    # Detect frozen numeric telemetry; do not misclassify textual statuses.
    for (asset, metric), g in eq[eq.metric != 'status'].groupby(['asset_id', 'metric']):
        g = g.sort_values('timestamp_utc')
        changes = g.numeric_value.ne(g.numeric_value.shift()) | g.numeric_value.isna()
        for _, run in g.groupby(changes.cumsum()):
            if len(run) < 2 or run.timestamp_utc.iloc[-1] - run.timestamp_utc.iloc[0] < pd.Timedelta('6h'):
                continue
            t = run.timestamp_utc.iloc[0] + pd.Timedelta('6h')
            out.append(make(t, [asset], 'data_quality', 'flag_anomaly', 'medium',
                            f'{asset}.{metric} frozen for at least 6 hours; check sensor.',
                            [f'equipment.csv:{asset}:{metric}:{iso(run.timestamp_utc.iloc[0])}'],
                            f'FROZEN-{asset}-{metric}-{iso(run.timestamp_utc.iloc[0])}',
                            verification='Confirm readings resume.'))

    w = eq.pivot_table(index='timestamp_utc', columns=['asset_id', 'metric'],
                       values='numeric_value', aggfunc='median').sort_index()
    if ('AHU1', 'filter_dp_pa') in w.columns:
        s = w[('AHU1', 'filter_dp_pa')].resample('1D').median()
        # Reference is exclusively from earlier completed days.
        base = s.rolling(7, min_periods=3).median().shift(1)
        high = (s > base * 1.30) & (s > base + 25)
        # Emit once per unresolved high-pressure episode. Missing measurements
        # do not constitute recovery. Two measured recovery days (< 110% of
        # baseline) are needed to close an episode; decisions use completed days.
        pending = None
        active = False
        recovery_days = 0
        for day, value in s.items():
            reference = base.loc[day]
            if pd.isna(value) or pd.isna(reference):
                continue
            is_high = bool(high.loc[day])
            if active:
                if value <= reference * 1.10:
                    recovery_days += 1
                    if recovery_days >= 2:
                        active = False
                        pending = None
                        recovery_days = 0
                else:
                    recovery_days = 0
                continue
            if is_high:
                if pending is None:
                    pending = day
                elif (day - pending) <= pd.Timedelta('48h'):
                    t = day + pd.Timedelta('1D')
                    out.append(make(t, ['AHU1'], 'ventilation_maintenance',
                                    'request_human_approval', 'medium',
                                    'Filter pressure elevated on two measured days relative to earlier baseline; inspect filter and airflow.',
                                    [f'equipment.csv:AHU1:filter_dp_pa:{pending.date()}',
                                     f'equipment.csv:AHU1:filter_dp_pa:{day.date()}'],
                                    f'FILTER-{pending.date()}', approval=True,
                                    verification='Confirm filter condition and post-service pressure/airflow.'))
                    active = True
                    pending = None
                else:
                    pending = day
            else:
                pending = None

    if {('HP1', 'heat_output_kw'), ('HP1', 'electric_kw')}.issubset(w.columns):
        h = pd.DataFrame({'q': w[('HP1', 'heat_output_kw')],
                          'e': w[('HP1', 'electric_kw')]})
        h = h[(h.e > 0.5) & (h.q > 0)].copy()
        h['cop'] = h.q / h.e
        # Daily medians; baseline uses previous days only and avoids the
        # current-day lookahead present in an unshifted rolling statistic.
        daily = h.cop.resample('1D').median()
        ref = daily.rolling(7, min_periods=5).median().shift(1)
        low = (daily < ref * 0.75) & (daily < 2.1)
        for grp in episodes(daily.index[low.fillna(False)], '36h'):
            if len(grp) < 2:
                continue
            t = grp[1] + pd.Timedelta('1D')
            out.append(make(t, ['HP1'], 'heating_plant',
                            'request_human_approval', 'high',
                            'Heat-pump daily COP substantially below prior-day baseline; weather and operating mode require technician review.',
                            [f'equipment.csv:HP1:COP:{x.date()}' for x in grp[:2]],
                            f'HP1-COP-{grp[0].date()}', approval=True,
                            verification='Compare weather-matched COP and check fault logs before maintenance.'))
    return out

def detect_equipment_planned(data, sched):
    from .maintenance_planner import plan_maintenance
    return plan_maintenance(data, sched, detect_equipment(data))

def detect_energy(data):
    from .energy_planner import plan_energy
    return plan_energy(data)


def detect_logistics(data, sched):
    from .logistics_planner import plan_logistics
    return plan_logistics(data, sched)

def detect_all(data,sched):
    out=[]
    for detector in (lambda:detect_turnaround(data,sched),lambda:detect_surge(data,sched,out),lambda:detect_water(data),lambda:detect_comfort(data),lambda:detect_equipment_planned(data,sched),lambda:detect_energy(data),lambda:detect_logistics(data,sched)):
        out.extend(detector())
    return out

