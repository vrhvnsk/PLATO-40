#!/usr/bin/env python3
"""Run: python run.py DATA_DIR --out decisions.jsonl"""
import argparse,json
from pathlib import Path
from core.loader import Data
from core.scheduler import Scheduler
from core.detectors import detect_all
from core.safety import validate
from core.executor import execute
from core.verification import verify
from core.execution_bridge import write_bridge_report
from analysis.insights import generate

def run(data_dir,out='decisions.jsonl',extras=True):
    data=Data(data_dir)
    decisions=validate(detect_all(data,Scheduler(data['staff_roster'])))
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(''.join(json.dumps(d,ensure_ascii=False,default=str)+'\n' for d in decisions),encoding='utf-8')
    if extras:
        execution_records=execute(decisions)
        (out.parent/'execution_log.jsonl').write_text(''.join(json.dumps(d)+'\n' for d in execution_records),encoding='utf-8')
        write_bridge_report(out.parent/'reports'/'executor_bridge', decisions, execution_records)
        (out.parent/'verification.jsonl').write_text(''.join(json.dumps(d)+'\n' for d in verify(decisions,data)),encoding='utf-8')
        (out.parent/'insights.md').write_text(generate(decisions,data),encoding='utf-8')
    print(f'Wrote {len(decisions)} decisions / {len(set(d["episode_id"] for d in decisions))} episodes -> {out}')
    return decisions

if __name__=='__main__':
    p=argparse.ArgumentParser(description='PLATO-40 synthetic building operations replay')
    p.add_argument('data_dir');p.add_argument('--out',default='decisions.jsonl')
    p.add_argument('--no-extras',action='store_true')
    a=p.parse_args();run(a.data_dir,a.out,not a.no_extras)
