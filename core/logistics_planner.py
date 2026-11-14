"""Causal logistics forecast and robot capacity planning."""
import pandas as pd
from .decisions import make, iso


def plan_logistics(data, sched):
    lg = data['logistics']
    if lg.empty or not {'timestamp_utc','asset_id','metric','value'}.issubset(lg):
        return []
    out = []
    assets = {a['id']: a for a in data.building.get('building', {}).get('assets', [])}
    for (asset, metric), raw in lg.groupby(['asset_id','metric']):
        if asset not in assets: continue
        if metric not in ('fill_pct', 'stock_drinks', 'stock_snacks'): continue
        g = raw.sort_values('timestamp_utc').copy()
        g['value'] = pd.to_numeric(g.value, errors='coerce')
        g = g.dropna(subset=['value','timestamp_utc'])
        if len(g) < 7: continue
        last_alert = None
        for i in range(6, len(g)):
            now = g.iloc[i]
            at = now.timestamp_utc
            # Avoid repeated orders until a clearly observed reset/refill.
            if last_alert is not None:
                if asset.startswith('WASTE') and now.value < 20:
                    last_alert = None
                elif asset == 'VEND1' and now.value >= .85 * assets[asset]['capacity'][metric.replace('stock_','')]:
                    last_alert = None
                else:
                    continue
            hist = g.iloc[i-6:i+1]
            if hist.timestamp_utc.diff().dropna().gt(pd.Timedelta('90min')).any(): continue
            elapsed = (hist.timestamp_utc.iloc[-1] - hist.timestamp_utc.iloc[0]).total_seconds()/3600
            if elapsed <= 0: continue
            rate = (float(hist.value.iloc[-1]) - float(hist.value.iloc[0])) / elapsed
            if asset.startswith('WASTE'):
                if rate <= 0: continue
                limit = 90 if asset != 'WASTE_MAIN' else 85
                hours = (limit - now.value) / rate
                if (now.value < 45 or hours > 12) and now.value < limit: continue
                if asset == 'WASTE_MAIN':
                    action, priority = 'order_service', 'high'
                    reason = (f'Central waste fill {now.value:.1f}%, rising {rate:.2f} percentage points/hour; '
                              f'projected to reach {limit}% in {max(0,hours):.1f}h. '
                              'Extra pickup has approximately 24h lead time; request confirmation, not completion.')
                    resource = None
                else:
                    # Floor-bin transport requires a 20-minute robot slot.
                    start = at.ceil('30min')
                    resource = sched.reserve('robot', start, start + pd.Timedelta('20min'), at)
                    if resource:
                        action, priority = 'dispatch_robot', 'medium'
                        reason = (f'Floor bin {now.value:.1f}% full, rising {rate:.2f} pp/h; '
                                  f'projected to {limit}% in {max(0,hours):.1f}h. '
                                  f'Proposed 20-minute bin transfer at {iso(start)} by {resource}; no completion assumed.')
                    else:
                        action, priority = 'request_human_approval', 'medium'
                        reason = (f'Floor bin {now.value:.1f}% full and projected to {limit}% in '
                                  f'{max(0,hours):.1f}h; no verified robot slot now. Coordinate staff.')
            elif asset == 'VEND1':
                if rate >= 0: continue
                cap = assets[asset]['capacity'].get(metric.replace('stock_', ''))
                if not cap: continue
                threshold = 0.15 * cap
                hours = (now.value - threshold) / -rate
                if (hours > 30) and now.value > threshold: continue
                action, priority, resource = 'order_service', 'medium', None
                reason = (f'{metric} stock {now.value:.0f}/{cap}, declining {-rate:.2f} units/hour; '
                          f'projected to 15% in {max(0,hours):.1f}h. '
                          'Vendor restock has approximately 24h lead time; request confirmation.')
            else: continue
            ep = f'LOG-FORECAST-{asset}-{metric}-{iso(at)}'
            evidence = [f'logistics.csv:{asset}:{metric}:{iso(hist.timestamp_utc.iloc[0])}..{iso(at)}',
                        f'building.json:{asset}:capacity_or_service']
            if resource: evidence.append(f'staff_roster.csv:resource={resource}:slot={iso(start)}')
            out.append(make(at, [asset], 'logistics', action, priority, reason, evidence, ep,
                            approval=action == 'request_human_approval', resource=resource,
                            expected='Service/robot task proposed, not confirmed',
                            verification='Confirm service acceptance or robot completion; recheck fill/stock telemetry.'))
            last_alert = at
    return out
