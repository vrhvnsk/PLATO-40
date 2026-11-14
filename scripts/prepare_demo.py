"""Rebuild static judges' demo assets from actual saved decision records.

No verification success is invented. Historical telemetry is not modified by simulation.
"""
import json
from pathlib import Path
from collections import defaultdict
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core.executor import execute

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'frontend'/'public'

def main():
    rows=[json.loads(line) for line in (ROOT/'decisions.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    if len({r['event_id'] for r in rows})!=len(rows):
        raise ValueError('Duplicate decision event IDs')
    logs=execute(rows)
    PUBLIC.mkdir(exist_ok=True,parents=True)
    (PUBLIC/'decisions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    for dest in (ROOT/'execution_log.jsonl',PUBLIC/'execution_log.jsonl'):
        dest.write_text(''.join(json.dumps(r)+'\n' for r in logs),encoding='utf-8')
    # This is a disclosure of absent causal evidence, not an observed outcome.
    ver=[{'event_id':r['event_id'],'status':'not_verified','note':'No post-action confirmation available from historical replay. Simulated actions do not modify historical telemetry.'} for r in rows]
    (PUBLIC/'verification.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in ver),encoding='utf-8')
    by=defaultdict(list)
    for r in rows:by[r['issue_type']].append(r)
    cases=[]
    for issue in ['room_turnaround','water_leak','heating_comfort','heating_plant','logistics','energy_optimization','data_quality','occupancy_surge','ventilation_maintenance']:
        options=by[issue]
        if options:
            options.sort(key=lambda r:(not r.get('requires_human_approval'),-len(r.get('evidence',[])),r['timestamp_utc']))
            cases.append({'issue_type':issue,'event_id':options[0]['event_id']})
    (PUBLIC/'demo_cases.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
    (PUBLIC/'learning_candidates.json').write_bytes((ROOT/'learning_candidates.json').read_bytes())
    print(f'Demo: {len(rows)} decisions, {len(logs)} mock-execution records, {len(cases)} scenario categories')

if __name__=='__main__':main()
