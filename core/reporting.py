"""Usage: python -m core.reporting decisions_dev.jsonl --out-dir reports/dev [--events data/dev/events.jsonl]"""
import argparse
import json
from pathlib import Path
from .assurance import audit
from .learning import feedback
from .retrospective_verification import verify


def read_jsonl(path):
    with Path(path).open(encoding='utf-8-sig') as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f'{path}:{line_number}: {exc}') from exc
            if not isinstance(item, dict):
                raise ValueError(f'{path}:{line_number}: expected JSON object')
            yield item


def main():
    parser = argparse.ArgumentParser(description='PLATO-40 Batch 2 read-only audit and feedback')
    parser.add_argument('decisions', type=Path)
    parser.add_argument('--events', type=Path, help='Optional observed events.jsonl for retrospective verification')
    parser.add_argument('--out-dir', type=Path, default=Path('reports/dev'))
    parser.add_argument('--strict', action='store_true', help='Exit nonzero if any error-severity findings')
    args = parser.parse_args()
    decisions = list(read_jsonl(args.decisions))
    assurance = audit(decisions)
    learning = feedback(decisions, assurance)
    verification = verify(decisions, list(read_jsonl(args.events)) if args.events else None)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, obj in [('assurance', assurance), ('feedback', learning), ('verification', verification)]:
        (args.out_dir / f'{name}.json').write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = [
        '# PLATO-40 Batch 2: replay assurance and learning', '',
        f"Decisions: **{assurance['decision_count']}**; episodes: **{assurance['episode_count']}**; unique event IDs: **{assurance['unique_event_ids']}**.",
        f"Audit findings: **{len(assurance['findings'])}**, including **{sum(f['severity']=='error' for f in assurance['findings'])} errors**.",
        '', '## Findings by type', '',
    ]
    lines += [f'- `{code}`: {n}' for code, n in assurance['finding_counts'].items()] or ['- No static audit findings']
    lines += ['', '## CLARA / PLATO recommendations', '']
    for r in learning['recommendations']:
        lines += [f"### {r['owner']}: {r['title']}", '', r['observation'], '',
                  f"**Proposal:** {r['recommendation']}", '',
                  f"**Validation:** {r['validation_required']}", '']
    lines += ['## Evidence limitations', ''] + [f'- {s}' for s in learning['data_limitations']]
    (args.out_dir / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"Batch 2: {len(decisions)} decisions, {len(assurance['findings'])} findings, {len(learning['recommendations'])} recommendations")
    print(f'Reports written to {args.out_dir}')
    if args.strict and any(f['severity'] == 'error' for f in assurance['findings']):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
