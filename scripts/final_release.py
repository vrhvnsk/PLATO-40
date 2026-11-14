"""One-command reproducible synthetic replay and autonomy evaluation."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run import run
from core.autonomy_lab import run_lab


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', default='data/quickstart')
    p.add_argument('--out-dir', default='reports/final_release')
    p.add_argument('--seed', type=int, default=40)
    p.add_argument('--holdout', default=None, help='Independent organizer holdout directory, if provided')
    a = p.parse_args()
    dest = Path(a.out_dir)
    dest.mkdir(parents=True, exist_ok=True)
    run(a.data, dest / 'decisions.jsonl')
    result = {'development': run_lab(dest / 'decisions.jsonl', dest, a.seed)}
    if a.holdout:
        hdir = dest / 'holdout'; hdir.mkdir(exist_ok=True)
        run(a.holdout, hdir / 'decisions_holdout.jsonl')
        result['holdout'] = run_lab(hdir / 'decisions_holdout.jsonl', hdir, a.seed)
    else:
        result['holdout'] = {'status': 'not_run', 'reason': 'Independent holdout data not supplied'}
    (dest / 'release_manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
