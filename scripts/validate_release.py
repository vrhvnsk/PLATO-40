"""Offline acceptance checks: replay determinism, leakage-safe temporal evaluation, archive hygiene."""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.autonomy_lab import read_jsonl, simulate, evaluation, write_jsonl


def temporal_split(rows, fraction=0.2):
    """Split by episode when possible to prevent the same episode crossing partitions."""
    groups = {}
    for i, row in enumerate(rows):
        key = str(row.get('episode_id') or row.get('event_id') or f'row-{i}')
        groups.setdefault(key, []).append(row)
    ordered = sorted(groups.items(), key=lambda kv: (min(str(r.get('timestamp_utc', '')) for r in kv[1]), kv[0]))
    cut = max(1, min(len(ordered)-1, int(len(ordered)*(1-fraction)))) if len(ordered)>1 else len(ordered)
    return [r for _, group in ordered[:cut] for r in group], [r for _, group in ordered[cut:] for r in group]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--decisions', default='decisions.jsonl')
    p.add_argument('--out', default='reports/acceptance')
    p.add_argument('--seed', type=int, default=40)
    args = p.parse_args()
    path = ROOT / args.decisions
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    decisions = read_jsonl(path)
    train, holdout = temporal_split(decisions)
    start = time.perf_counter()
    a = simulate(holdout, args.seed)
    duration = time.perf_counter()-start
    b = simulate(holdout, args.seed)
    assert a == b, 'Non-deterministic replay'
    assert not ({str(x.get('episode_id') or x.get('event_id')) for x in train} & {str(x.get('episode_id') or x.get('event_id')) for x in holdout}), 'Episode leakage'
    write_jsonl(out / 'decisions_internal_holdout.jsonl', holdout)
    write_jsonl(out / 'autonomy_internal_holdout.jsonl', a)
    digest = hashlib.sha256((out/'autonomy_internal_holdout.jsonl').read_bytes()).hexdigest()
    report = {'source': str(path), 'train_rows': len(train), 'internal_holdout_rows': len(holdout),
              'holdout_provenance': 'Temporal split of bundled data, NOT independent organizer holdout',
              'episode_disjoint': True, 'replay_deterministic': True, 'trace_sha256': digest,
              'holdout_evaluation': evaluation(a), 'holdout_replay_seconds': round(duration,4),
              'holdout_decisions_per_second': round(len(a)/duration,2) if duration else None,
              'outcome_learning_validated': False,
              'reason': 'Bundled decisions have no authenticated post-action outcomes or counterfactual ground truth'}
    (out/'acceptance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
