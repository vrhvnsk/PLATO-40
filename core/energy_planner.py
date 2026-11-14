"""Causal, conservative battery arbitrage proposals for PLATO-40."""
import pandas as pd
import numpy as np
from bisect import insort
from statistics import median
from .decisions import make, iso

def plan_energy(data):
    tariff, energy, forecast = data['tariff'], data['energy'], data['weather_forecast']
    assets = {a['id']: a for a in data.building.get('building', {}).get('assets', [])}
    bat = assets.get('BAT1', {})
    required = {'usable_kwh', 'max_charge_kw', 'max_discharge_kw', 'soc_bounds_kwh', 'round_trip_efficiency'}
    if not required.issubset(bat) or tariff.empty or energy.empty or forecast.empty:
        return []
    bounds = bat['soc_bounds_kwh']
    eff = float(bat['round_trip_efficiency']) ** 0.5
    if not (0 < eff <= 1): return []
    t = tariff.copy()
    t['price_eur_kwh'] = pd.to_numeric(t.price_eur_kwh, errors='coerce')
    e = energy.sort_values('timestamp_utc')
    out = []
    # Index once. Repeated full-table scans made long development replays quadratic.
    e = e.dropna(subset=['timestamp_utc'])
    valid_soc = e[e.battery_soc_kwh.notna()].sort_values('timestamp_utc')
    soc_times = valid_soc.timestamp_utc.to_numpy(dtype='datetime64[ns]')
    fc = forecast.dropna(subset=['issued_utc', 'target_utc']).sort_values('issued_utc')
    forecast_groups = {target: group for target, group in fc.groupby('target_utc')}
    historical_pv = e[['timestamp_utc', 'pv_kw']].dropna().copy()
    historical_pv['hour'] = historical_pv.timestamp_utc.dt.hour
    historical_pv = historical_pv.sort_values('timestamp_utc')
    pv_samples = list(historical_pv.itertuples(index=False))
    pv_pos = 0
    pv_by_hour = {h: [] for h in range(24)}
    for published, group in t.groupby('published_utc', sort=True):
        if pd.isna(published): continue
        future = group[(group.timestamp_utc > published) & group.price_eur_kwh.notna()].sort_values('timestamp_utc')
        # Require full, strictly hourly day-ahead price coverage.
        if len(future) < 20: continue
        hourly = future.drop_duplicates('timestamp_utc').set_index('timestamp_utc')
        hourly = hourly[hourly.index <= published + pd.Timedelta('36h')]
        if len(hourly) < 20: continue
        soc_pos = np.searchsorted(soc_times, published.to_datetime64(), side='right') - 1
        if soc_pos < 0: continue
        soc_row = valid_soc.iloc[soc_pos]
        if published - soc_row.timestamp_utc > pd.Timedelta('2h'): continue
        soc = float(soc_row.battery_soc_kwh)
        if not bounds[0] <= soc <= bounds[1]: continue
        # Use the latest forecast issued by decision time, never realized future weather.
        wx_rows = []
        for target in hourly.index:
            fg = forecast_groups.get(target)
            if fg is None: continue
            ft = fg.issued_utc.to_numpy(dtype='datetime64[ns]')
            idx = np.searchsorted(ft, published.to_datetime64(), side='right') - 1
            if idx >= 0: wx_rows.append(fg.iloc[idx])
        if not wx_rows: continue
        wx = pd.DataFrame(wx_rows)
        if len(wx) < 18: continue
        # No PV forecast exists in this dataset. Historical same-hour PV is
        # a proxy only; never claim it is a day-ahead forecast.
        while pv_pos < len(pv_samples) and pv_samples[pv_pos].timestamp_utc <= published:
            sample = pv_samples[pv_pos]
            insort(pv_by_hour[int(sample.hour)], float(sample.pv_kw))
            pv_pos += 1
        pv_proxy = {h: median(v) for h, v in pv_by_hour.items() if v}
        # Only plan battery arbitrage, never reduce heating to save money.
        cheap = hourly.sort_values('price_eur_kwh')
        expensive = hourly.sort_values('price_eur_kwh', ascending=False)
        best = None
        wx_by_target = wx.set_index('target_utc')['outdoor_c_forecast'].to_dict()
        for charge_at, charge_row in cheap.iterrows():
            for discharge_at, discharge_row in expensive.iterrows():
                if discharge_at <= charge_at: continue
                if charge_at not in wx_by_target or discharge_at not in wx_by_target: continue
                # Forecast-aware conservative guard: do not charge from the
                # grid during extreme cold, when heating demand is uncertain.
                temp = float(wx_by_target[charge_at])
                if temp < -8: continue
                # Charge energy cannot exceed storage headroom; discharge
                # limited by the corresponding stored energy and SOC floor.
                charge_kwh = min(float(bat['max_charge_kw']), (float(bounds[1]) - soc) / eff)
                discharge_kwh = min(float(bat['max_discharge_kw']), charge_kwh * eff * eff)
                if charge_kwh <= 0 or discharge_kwh <= 0: continue
                # Require positive net benefit after efficiency losses.
                savings = discharge_kwh * float(discharge_row.price_eur_kwh) - charge_kwh * float(charge_row.price_eur_kwh)
                if savings <= 0.5: continue
                candidate = (savings, charge_at, discharge_at, charge_kwh, discharge_kwh, temp)
                if best is None or candidate[0] > best[0]: best = candidate
        if best is None: continue
        savings, charge_at, discharge_at, charge_kwh, discharge_kwh, temp = best
        pv = pv_proxy.get(charge_at.hour, np.nan)
        pv_text = f'Historical same-hour PV median {pv:.1f} kW (not a forecast).' if pd.notna(pv) else 'No PV proxy available.'
        ep = f'BAT-PLAN-{iso(published)}'
        out.append(make(published, ['BAT1', 'PV1', 'HP1'], 'energy_optimization', 'optimize_energy', 'low',
            f'SIMULATED battery-only proposal: charge {charge_kwh:.1f} kWh at {iso(charge_at)}, '
            f'discharge {discharge_kwh:.1f} kWh at {iso(discharge_at)}; estimated gross tariff benefit '
            f'EUR {savings:.2f} before wear and fees. Weather forecast at charge {temp:.1f} C. '
            f'{pv_text} Heating setpoints and occupied comfort remain unchanged. '
            'Requires revalidation of SOC, forecast and comfort before execution.',
            [f'tariff.csv:published={iso(published)}:charge={iso(charge_at)}:discharge={iso(discharge_at)}',
             f'energy.csv:BAT1:soc:{iso(soc_row.timestamp_utc)}',
             f'weather_forecast.csv:issued<={iso(published)}',
             'building.json:BAT1:limits'],
            ep, expected=f'Battery dispatch proposal, not executed; gross tariff benefit EUR {savings:.2f}',
            verification='Before each slot recheck SOC, battery power limits, grid import limits and room temperatures; abort on constraint violation.',
            confidence=0.55,proposal_only=True))
    return out
