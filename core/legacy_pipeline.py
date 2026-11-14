#!/usr/bin/env python3
"""PLATO-40 autonomous operations pipeline.
Usage: python run.py <data_dir> [--out decisions.jsonl]
Effects are SIMULATED (mock executor). Guest messages are PROPOSED, not delivered.
Data: PLATO-40 synthetic dataset, Proximata Hackathon '26 - Rhomberg track (CC BY 4.0)."""
import argparse, json, hashlib, sys
from pathlib import Path
import numpy as np
import pandas as pd

TZ = "Europe/Vienna"
COMFORT_MIN, COMFORT_MAX = 20.0, 23.0
D = []  # decisions

# ---------------- loading ----------------
def load(d, name):
    p = d / name
    if not p.exists():
        print(f"[warn] {name} missing", file=sys.stderr); return pd.DataFrame()
    df = pd.read_csv(p).drop_duplicates()
    for c in df.columns:
        if c.endswith("_utc"):
            df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
    return df

def load_events(d):
    p = d / "events.jsonl"
    if not p.exists(): return pd.DataFrame(columns=["event_id", "timestamp_utc", "type"])
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    ev = pd.DataFrame(rows)
    ev["timestamp_utc"] = pd.to_datetime(ev["timestamp_utc"], utc=True, errors="coerce")
    return ev

def iso(t): return pd.Timestamp(t).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
def local(t): return pd.Timestamp(t).tz_convert(TZ)

# ---------------- decision log ----------------
APPROVAL = {"dispatch_technician", "block_room", "reassign_room", "request_human_approval"}

def decide(t, assets, issue, action, priority, reason, evidence, episode, *, consent=False,
           approval=None, conf=0.7, outcome="", verify="", deps=(), guest_ids=(), resource=None):
    need = consent or action in APPROVAL or bool(approval)
    eid = "D-" + hashlib.sha1(f"{episode}|{action}|{','.join(assets)}|{iso(t)}".encode()).hexdigest()[:12]
    rec = {"event_id": eid, "timestamp_utc": iso(t), "affected_assets": list(assets),
           "issue_type": issue, "action": action, "priority": priority, "reason": reason,
           "requires_human_approval": need, "requires_guest_consent": bool(consent),
           "autonomy": "approval_and_consent" if consent else ("human_approval" if need else "autonomous"),
           "episode_id": episode, "evidence": [str(e) for e in evidence],
           "expected_outcome": ("SIMULATED: " + outcome) if outcome else "",
           "verification_plan": verify, "dependencies": list(deps),
           "guest_request_ids": list(guest_ids), "confidence": round(float(conf), 2)}
    if resource: rec["resource_id"] = resource
    D.append(rec); return eid

def group_episodes(ts, gap):
    ts = pd.Series(sorted(ts))
    return [g.tolist() for _, g in ts.groupby((ts.diff() > pd.Timedelta(gap)).cumsum())]

# ---------------- staff availability (only what was known at t) ----------------
class Roster:
    def __init__(self, r): self.r = r
    def available(self, role, start, end, known_at):
        r = self.r
        if r.empty: return []
        s = r[(r.role == role) & (r.start_utc < end) & (r.end_utc > start)]
        absent = s.status.isin(["sick", "vacation", "out_of_service"]) & (s.status_known_utc <= known_at)
        return sorted(s[~absent].resource_id.unique().tolist())

# ---------------- S01 / S05 turnaround ----------------
def turnaround(bk, ev, gr, ros, tel):
    bk = bk[bk.status == "confirmed"]
    hk_clean = {}
    if not ev.empty and "cleaning_completed" in set(ev.type):
        cc = ev[ev.type == "cleaning_completed"]
        for r, g in cc.groupby("room_id"): hk_clean[r] = g.timestamp_utc.sort_values().tolist()
    triggers = []
    if not ev.empty:
        for typ in ("checkout_early", "checkin_early", "arrival_waiting_room", "checkin_after_wait"):
            for x in ev[ev.type == typ].itertuples():
                triggers.append((x.timestamp_utc, getattr(x, "room_id", None), typ, None))
    if not gr.empty:
        early = gr[gr.request_type.astype(str).str.contains("early|check", case=False, na=False)]
        for x in early.itertuples():
            triggers.append((x.timestamp_utc, x.room_id, "guest_request", x))
    seen = set()
    for t, room, typ, req in sorted(triggers, key=lambda z: z[0]):
        if not isinstance(room, str) or not room.startswith("R"): continue
        day = local(t).date(); ep = f"EP-TURN-{room}-{day}"
        if (ep, typ) in seen: continue
        seen.add((ep, typ))
        lt = local(t)
        shift_s = lt.normalize() + pd.Timedelta(hours=7); shift_e = lt.normalize() + pd.Timedelta(hours=15, minutes=30)
        cleaners = ros.available("cleaner", shift_s.tz_convert("UTC"), shift_e.tz_convert("UTC"), t)
        deps_today = bk[bk.departure_utc.dt.tz_convert(TZ).dt.date == day]
        load = len(deps_today)
        cap = len(cleaners) * 12  # assumption: ~12 rooms per cleaner shift, document in README
        ev_ = [f"events.jsonl:{typ}:{room}:{iso(t)}", f"staff_roster.csv:cleaners_available={len(cleaners)}",
               f"bookings.csv:departures_on_{day}={load}"]
        gid = [req.request_id] if req is not None else []
        if req is not None: ev_.append(f"guest_requests.csv:{req.request_id}")
        if cleaners:
            prio = "high" if load > cap else "medium"
            c1 = decide(t, [room], "room_turnaround", "schedule_cleaning", prio,
                        f"Prioritise {room} in today's cleaning queue ({typ}); {len(cleaners)} cleaners available for {load} departures.",
                        ev_, ep, resource=cleaners[0], conf=0.8, outcome=f"{room} cleaned before arrival",
                        verify="housekeeping_state=clean and cleaning_completed event; only then release_room.")
        else:
            c1 = decide(t, [room], "room_turnaround", "request_human_approval", "high",
                        "No cleaner available (absences known at this time); call on-call housekeeper ONCALL_1 for the evening or reassign room.",
                        ev_, ep, conf=0.75, verify="Approval recorded; cleaning_completed before arrival.")
        if load > cap and cleaners:
            decide(t, [room], "occupancy_surge", "request_human_approval", "high",
                   f"Departures ({load}) exceed estimated capacity ({cap}); request ONCALL_1 evening shift. Robots clean floors only, cannot release rooms.",
                   ev_, ep, conf=0.65, deps=[c1])
            robots = ros.available("robot", shift_s.tz_convert("UTC"), shift_e.tz_convert("UTC"), t)
            if robots:
                decide(t, [f"WASTE_F{room[1]}"], "occupancy_surge", "dispatch_robot", "medium",
                       "Robot takes corridor floor cleaning and bin transport to free cleaner time.",
                       ev_, ep, resource=robots[0], conf=0.7, outcome="cleaner time freed for rooms")
        lang = getattr(req, "language", "en") if req is not None else "en"
        due = getattr(req, "response_due_utc", None) if req is not None else None
        decide(t, [room], "room_turnaround", "notify_guest", "medium",
               f"PROPOSED message ({lang}): realistic ready time after cleaning is confirmed; not a delivery receipt."
               + (f" Respond before {iso(due)}." if due is not None and pd.notna(due) else ""),
               ev_, ep, conf=0.7, deps=[c1], guest_ids=gid)
        done = [c for c in hk_clean.get(room, []) if c >= t]
        if done:
            decide(done[0], [room], "room_turnaround", "release_room", "medium",
                   "Release only after cleaning_completed was observed.",
                   [f"events.jsonl:cleaning_completed:{room}:{iso(done[0])}"], ep, conf=0.9, deps=[c1])

# ---------------- S02 water ----------------
def water(rw, wm, wo, tel):
    if rw.empty: return
    rw = rw.sort_values(["room_id", "timestamp_utc"]).copy()
    rw["flow"] = rw.groupby("room_id").meter_total_l.diff()
    resets = rw[rw.flow < 0]
    for x in resets.itertuples():
        decide(x.timestamp_utc, [x.room_id], "data_quality", "flag_anomaly", "low",
               "Cumulative meter decreased (meter exchange/restart); excluded from consumption.",
               [f"room_water.csv:{x.room_id}:{iso(x.timestamp_utc)}"], f"EP-WMRESET-{x.room_id}-{local(x.timestamp_utc).date()}", conf=0.9)
    rw.loc[(rw.flow < 0) | (rw.flow > 300), "flow"] = np.nan
    lt = rw.timestamp_utc.dt.tz_convert(TZ)
    night = rw[lt.dt.hour.between(2, 4)].copy()
    night["date"] = lt[night.index].dt.date
    floor = night.groupby(["room_id", "date"]).flow.min().dropna()
    floor = floor[floor > 0.3].reset_index()
    for room, g in floor.groupby("room_id"):
        dates = pd.to_datetime(g.date)
        runs = (dates.diff().dt.days != 1).cumsum()
        for _, run in g.groupby(runs.values):
            if len(run) < 2: continue
            d0 = run.date.iloc[0]; t = pd.Timestamp(run.date.iloc[1]).tz_localize(TZ) + pd.Timedelta(hours=6)
            ep = f"EP-LEAK-{room}-{d0}"
            ev = [f"room_water.csv:{room}:{d}T02:00..05:00local:min_flow={v:.2f}l/15min" for d, v in zip(run.date, run.flow)]
            f1 = decide(t, [room], "water_leak", "flag_anomaly", "high",
                        f"Continuous night flow in {room} on {len(run)} consecutive nights (running-toilet pattern), not guest/cleaning use.",
                        ev, ep, conf=min(0.95, 0.55 + 0.1 * len(run)))
            decide(t, [room], "water_leak", "request_inspection", "high",
                   "Inspect WC fill valve/flush; entering an occupied room needs approval and guest consent (not granted).",
                   ev, ep, consent=True, deps=[f1], verify="Night minimum flow returns to ~0 after repair; else escalate to dispatch_technician.")
    if wm.empty: return
    m = wm.sort_values("timestamp_utc").set_index("timestamp_utc").meter_total_l.diff()
    m[(m < 0) | (m > 2000)] = np.nan
    mh = m.resample("1h").sum(min_count=1)
    rh = rw.set_index("timestamp_utc").flow.resample("1h").sum(min_count=30)
    gap = (mh - rh).dropna()
    gn = gap[gap.index.tz_convert(TZ).hour.isin([2, 3, 4])]
    base = gn.rolling("14D", min_periods=20).median().shift(1)
    mad = (gn - base).abs().rolling("14D", min_periods=20).median().shift(1)
    hit = gn[(gn - base) > np.maximum(5, 4 * mad)]
    days = pd.Series(hit.index.tz_convert(TZ).date).value_counts()
    bad_days = sorted(d for d, n in days.items() if n >= 2)
    for grp in group_episodes([pd.Timestamp(d) for d in bad_days], "2D"):
        if len(grp) < 2: continue
        t = grp[1].tz_localize(TZ) + pd.Timedelta(hours=6)
        ep = f"EP-MAINLEAK-{grp[0].date()}"
        ev = [f"water_main.csv-room_water.csv:night_gap_above_baseline:{d.date()}" for d in grp]
        decide(t, ["WM_MAIN"], "water_leak", "flag_anomaly", "critical",
               "Main meter exceeds sum of room meters at night above 14-day baseline on consecutive nights: leak in common pipework/areas.",
               ev, ep, conf=0.7)
        decide(t, ["WM_MAIN"], "water_leak", "dispatch_technician", "critical",
               "Inspect common pipework, technical room and irrigation; water shutoff only with approval.",
               ev, ep, conf=0.7, verify="Night gap returns to baseline.")

# ---------------- S03 comfort ----------------
def occupied_mask(tel, bk, ev):
    bk = bk[bk.status == "confirmed"]
    occ = pd.Series(False, index=tel.index)
    for x in bk.itertuples():
        m = (tel.room_id == x.room_id) & (tel.timestamp_utc >= x.arrival_utc) & (tel.timestamp_utc < x.departure_utc)
        occ |= m
    return occ

def comfort(tel, bk, ev, ros):
    if tel.empty: return
    tel = tel.copy()
    tel.loc[(tel.temperature_c < 0) | (tel.temperature_c > 40), "temperature_c"] = np.nan
    tel["occ"] = occupied_mask(tel, bk, ev)
    cold = tel[tel.occ & (tel.temperature_c < COMFORT_MIN) & (tel.window_open != 1)]
    for room, g in cold.groupby("room_id"):
        for ep_ts in group_episodes(g.timestamp_utc, "45min"):
            if len(ep_ts) < 4: continue  # 1 h sustained
            t = ep_ts[3]; ep = f"EP-COLD-{room}-{iso(ep_ts[0])}"
            gg = g[g.timestamp_utc.isin(ep_ts)]
            ev_ = [f"room_telemetry.csv:{room}:{iso(ep_ts[0])}..{iso(ep_ts[-1])}:min_temp={gg.temperature_c.min():.1f}C",
                   "bookings.csv:occupied"]
            a = decide(t, [room], "heating_comfort", "adjust_room_setpoint", "high",
                       f"Occupied {room} below comfort band ({COMFORT_MIN} C) for >=1h, window closed. Comfort over cost.",
                       ev_, ep, conf=0.8, outcome="room back within 20-23 C",
                       verify="temperature_c >= 20 within 2 h; otherwise check HP1 and escalate.")
            if len(ep_ts) >= 12:
                tech = ros.available("technician", t, t + pd.Timedelta("8h"), t)
                decide(t + pd.Timedelta("2h"), [room, "HP1"], "heating_comfort", "dispatch_technician", "high",
                       "Still cold after setpoint action: plant or room-valve fault likely." + ("" if tech else " In-house technician unavailable: external contractor."),
                       ev_, ep, conf=0.7, deps=[a], resource=tech[0] if tech else None)

# ---------------- HP1 / AHU1 ----------------
def equipment(eq, weather, ros, wo):
    if eq.empty: return
    eq = eq.copy(); eq["v"] = pd.to_numeric(eq.value, errors="coerce")
    # data quality: gaps and frozen values
    for (a, m), g in eq[eq.metric != "status"].groupby(["asset_id", "metric"]):
        s = g.set_index("timestamp_utc").v.sort_index()
        frozen = s.diff().eq(0).astype(int).groupby(s.diff().ne(0).cumsum()).transform("sum")
        for name, mask in (("missing", s.isna()), ("frozen", frozen >= 24)):
            ts = s.index[mask]
            for grp in group_episodes(ts, "2h"):
                if len(grp) < 8: continue
                decide(grp[0] + pd.Timedelta("2h"), [a], "data_quality", "flag_anomaly", "medium",
                       f"{a}.{m} {name} for {len(grp)} steps: data issue, NOT evidence of plant degradation.",
                       [f"equipment.csv:{a}:{m}:{iso(grp[0])}..{iso(grp[-1])}"], f"EP-DQ-{a}-{m}-{iso(grp[0])}", conf=0.9,
                       verify="Readings resume; check gateway; do not dispatch on this alone.")
    w = eq.pivot_table(index="timestamp_utc", columns=["asset_id", "metric"], values="v")
    # AHU1 filter
    if ("AHU1", "filter_dp_pa") in w:
        dp = w[("AHU1", "filter_dp_pa")].resample("1D").median().dropna()
        base = dp.rolling(30, min_periods=10).quantile(0.25).shift(1)
        high = dp[(dp > base * 1.3) & (dp > base + 40)]
        for grp in group_episodes(high.index, "3D"):
            if len(grp) < 3: continue
            t = grp[2] + pd.Timedelta("8h"); ep = f"EP-FILTER-{grp[0].date()}"
            tech = ros.available("technician", t, t + pd.Timedelta("3D"), t)
            ev_ = [f"equipment.csv:AHU1:filter_dp_pa:{grp[0].date()}..{grp[-1].date()}:{dp[grp[-1]]:.0f}Pa vs base {base[grp[-1]]:.0f}Pa"]
            if tech:
                decide(t, ["AHU1"], "ventilation_maintenance", "dispatch_technician", "medium",
                       "Sustained filter pressure rise over 3+ days: replace filter.", ev_, ep, resource=tech[0], conf=0.8,
                       verify="filter_dp_pa back to baseline after replacement; airflow restored.")
            else:
                decide(t, ["AHU1"], "ventilation_maintenance", "order_service", "medium",
                       "Filter degradation and in-house technician unavailable (roster): order external contractor.",
                       ev_, ep, approval=True, conf=0.75, verify="Work order completed; dp back to baseline.")
    # HP1 efficiency vs outdoor temperature
    if ("HP1", "heat_output_kw") in w and ("HP1", "electric_kw") in w and not weather.empty:
        h = pd.DataFrame({"q": w[("HP1", "heat_output_kw")], "e": w[("HP1", "electric_kw")]}).dropna()
        h = h[h.e > 0.5]
        out = weather.set_index("timestamp_utc").iloc[:, 0] if "outdoor_temp_c" not in weather else weather.set_index("timestamp_utc").outdoor_temp_c
        h = h.join(out.rename("tout"), how="inner").dropna()
        h["cop"] = h.q / h.e; h["bin"] = (h.tout // 3) * 3
        h["ref"] = h.groupby("bin").cop.transform(lambda s: s.rolling(96 * 14, min_periods=96).median().shift(96))
        daily = (h.cop / h.ref).resample("1D").median().dropna()
        low = daily[daily < 0.75]
        for grp in group_episodes(low.index, "2D"):
            if len(grp) < 2: continue
            t = grp[1] + pd.Timedelta("8h"); ep = f"EP-HP1-{grp[0].date()}"
            decide(t, ["HP1"], "heating_plant", "dispatch_technician", "high",
                   "HP1 efficiency >25% below its own baseline at same outdoor temperature for 2+ days.",
                   [f"equipment.csv:HP1:cop_ratio={daily[g]:.2f}:{g.date()}" for g in grp], ep, conf=0.7,
                   verify="COP ratio back above 0.9; occupied rooms within comfort band.")

# ---------------- energy plan (only published info) ----------------
def energy_plan(tf, fc):
    if tf.empty: return
    tf = tf.copy(); tf["day"] = tf.timestamp_utc.dt.tz_convert(TZ).dt.date
    for day, g in tf.groupby("day"):
        pub = g.published_utc.max()
        if pd.isna(pub) or len(g) < 20: continue
        cheap = g.nsmallest(4, "price_eur_kwh"); dear = g.nlargest(4, "price_eur_kwh")
        spread = dear.price_eur_kwh.mean() - cheap.price_eur_kwh.mean()
        if spread < 0.05: continue  # no action when spread is small (avoid spam)
        cold = ""
        if not fc.empty:
            f = fc[(fc.issued_utc <= pub)]
            if not f.empty:
                f = f[f.issued_utc == f.issued_utc.max()]
                tcol = [c for c in f.columns if "temp" in c]
                if tcol: cold = f" Forecast min {f[tcol[0]].min():.0f} C."
        decide(pub, ["HP1", "BAT1"], "energy_optimization", "optimize_energy", "low",
               f"Pre-heat/charge battery in cheapest hours, reduce load in dearest hours, staying in 20-23 C for occupied rooms.{cold}",
               [f"tariff.csv:{day}:cheap={','.join(iso(x) for x in cheap.timestamp_utc)}",
                f"tariff.csv:{day}:spread={spread:.3f}EUR/kWh:published={iso(pub)}"],
               f"EP-ENERGY-{day}", conf=0.6, outcome="lower energy cost (estimate only, not measured)",
               verify="No occupied room leaves comfort band; otherwise revert.")

# ---------------- logistics ----------------
def logistics(lg):
    if lg.empty: return
    for (a, m), g in lg.groupby(["asset_id", "metric"]):
        s = g.set_index("timestamp_utc").value.astype(float).sort_index().dropna()
        if a == "WASTE_MAIN" or a.startswith("WASTE_F"):
            thr = 85 if a == "WASTE_MAIN" else 90
            hits = s.index[s >= thr]
            act, issue = ("order_service", "logistics") if a == "WASTE_MAIN" else ("dispatch_robot", "logistics")
        elif a == "VEND1":
            hits = s.index[s <= 0.15 * s.rolling("14D").max()]
            act, issue = "order_service", "logistics"
        else: continue
        for grp in group_episodes(hits, "24h"):
            t = grp[0]
            decide(t, [a], issue, act, "medium",
                   f"{a} {m}={s[t]:.0f}: order extra pickup/restock (~24h lead)" if act == "order_service" else f"{a} nearly full: robot carries bin to WASTE_MAIN",
                   [f"logistics.csv:{a}:{m}:{iso(t)}"], f"EP-LOG-{a}-{m}-{iso(t)}", conf=0.75,
                   outcome="no overflow/stock-out", verify="Level drops after service; no waste_bin_full/vending_out_of_stock event.")

# ---------------- safety validator ----------------
def validate(ros_df):
    out, ids = [], set()
    for x in sorted(D, key=lambda r: r["timestamp_utc"]):
        if x["event_id"] in ids: continue
        if x["requires_guest_consent"]: assert x["requires_human_approval"]
        if x["action"] in APPROVAL: assert x["requires_human_approval"]
        if x["action"] == "release_room": assert any("cleaning_completed" in e for e in x["evidence"])
        assert x["affected_assets"] and x["priority"] in ("critical", "high", "medium", "low")
        ids.add(x["event_id"]); out.append(x)
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("data_dir"); ap.add_argument("--out", default="decisions.jsonl")
    a = ap.parse_args(); d = Path(a.data_dir)
    bk, rs, gr = load(d, "bookings.csv"), load(d, "staff_roster.csv"), load(d, "guest_requests.csv")
    tel, rw, wm = load(d, "room_telemetry.csv"), load(d, "room_water.csv"), load(d, "water_main.csv")
    eq, wx, fc, tf = load(d, "equipment.csv"), load(d, "weather.csv"), load(d, "weather_forecast.csv"), load(d, "tariff.csv")
    lg, wo, ev = load(d, "logistics.csv"), load(d, "work_orders.csv"), load_events(d)
    ros = Roster(rs)
    steps = [("turnaround", lambda: turnaround(bk, ev, gr, ros, tel)), ("water", lambda: water(rw, wm, wo, tel)),
             ("comfort", lambda: comfort(tel, bk, ev, ros)), ("equipment", lambda: equipment(eq, wx, ros, wo)),
             ("energy", lambda: energy_plan(tf, fc)), ("logistics", lambda: logistics(lg))]
    for name, fn in steps:
        try: fn(); print(f"[ok] {name}", file=sys.stderr)
        except Exception as e: print(f"[warn] {name} failed: {e!r}", file=sys.stderr)
    out = validate(rs)
    with open(a.out, "w", encoding="utf-8") as f:
        for x in out: f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"wrote {len(out)} decisions, {len({x['episode_id'] for x in out})} episodes -> {a.out}")

if __name__ == "__main__":
    main()