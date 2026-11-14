"""Traceable, hypothesis-only feedback from replay decisions.

Recommendations are candidate interventions, not fitted model parameters or
validated real-world improvements. Each item includes reproducible evidence.
"""
from collections import Counter, defaultdict
from statistics import median


def build_learning_candidates(decisions):
    episodes = defaultdict(list)
    for d in decisions:
        episodes[str(d.get('episode_id') or d['event_id'])].append(d)
    groups = defaultdict(list)
    for eid, rows in episodes.items():
        groups[rows[0]['issue_type']].append((eid, rows))

    candidates = []
    def add(audience, category, title, episode_rows, suggestion, validation, basis='repeated episodes'):
        if not episode_rows:
            return
        all_rows = [d for _, rs in episode_rows for d in rs]
        assets = Counter(a for _, rs in episode_rows for a in set(a for d in rs for a in d.get('affected_assets', [])))
        months = sorted({d.get('timestamp_utc', '')[:7] for d in all_rows if d.get('timestamp_utc')})
        confidences = [d['confidence'] for d in all_rows if isinstance(d.get('confidence'), (float, int))]
        candidates.append({
            'audience': audience, 'category': category, 'title': title,
            'episode_count': len(episode_rows), 'decision_count': len(all_rows),
            'assets': [a for a, _ in assets.most_common(5)],
            'months': months, 'median_confidence': round(median(confidences), 3) if confidences else None,
            'sample_episode_ids': [eid for eid, _ in episode_rows[:3]],
            'suggestion': suggestion, 'validation': validation, 'basis': basis,
            'status': 'hypothesis_not_validated',
        })

    plans = {
        'water_leak': ('Review overnight flow and meter reconciliation thresholds; isolate missing or unreliable submeters.', 'Manually label sampled alerts and benign high-use periods; compare precision and missed leaks.'),
        'room_turnaround': ('Recalibrate cleaning time estimates and shift-aware room assignment; preserve the release gate.', 'Compare promised check-in times, observed cleaning completions, and staffing conflicts.'),
        'heating_comfort': ('Review sustained cold-room escalation and occupied-room comfort thresholds.', 'Inspect raw temperature trajectories and occupied-room false positives.'),
        'heating_plant': ('Review heat-pump degradation escalation and technician availability.', 'Cross-check plant telemetry, maintenance records, and benign weather-driven changes.'),
        'energy_optimization': ('Tune tariff/PV-aware proposals while retaining comfort and battery safety constraints.', 'Replay against a fixed no-optimisation baseline; report cost and comfort with uncertainty.'),
        'logistics': ('Reassess inventory reorder points, delivery lead times, and resource assignment.', 'Measure stockout lead time and confirmed fulfillment against historical work orders.'),
        'occupancy_surge': ('Adjust cleaning and logistics forecasts for occupancy surges.', 'Compare predicted versus actual arrivals, staffing load and late turnovers.'),
        'data_quality': ('Improve sensor freshness checks and require quality gating before control decisions.', 'Inject sensor freezes and missingness; measure false alarms and fail-closed behavior.'),
        'ventilation_maintenance': ('Review ventilation inspection cadence and filter-change triggers.', 'Verify against measured pressure drop, work orders, and post-maintenance readings.'),
    }
    for issue, episode_rows in sorted(groups.items()):
        suggestion, validation = plans.get(issue, ('Review decision thresholds and routing for this issue class.', 'Independently label sampled episodes and evaluate false positives.'))
        add('CLARA', issue, f'{issue.replace("_", " ").title()}: rule and workflow review', episode_rows, suggestion, validation)
        # A targeted hypothesis is only warranted for repeated affected assets.
        by_asset = defaultdict(list)
        for eid, rows in episode_rows:
            for asset in set(a for d in rows for a in d.get('affected_assets', [])):
                by_asset[asset].append((eid, rows))
        for asset, rows in sorted(by_asset.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:3]:
            if len(rows) >= 3:
                add('CLARA', issue, f'Recurrent {issue.replace("_", " ")} at {asset}', rows,
                    f'Investigate asset {asset} before changing global thresholds; consider a targeted inspection or calibration.',
                    f'Confirm independent occurrences for {asset} and compare with peer assets and maintenance history.',
                    'at least three distinct detected episodes at the same asset')
        # Design feedback must remain a review hypothesis, never a construction directive.
        if len(episode_rows) >= 3:
            design = {
                'water_leak': 'Evaluate branch-level metering and service access where independently confirmed gaps recur.',
                'heating_comfort': 'Review zoning, envelope and controllability for repeatedly uncomfortable rooms.',
                'heating_plant': 'Review service access and instrumentation for repeatedly degraded equipment.',
                'room_turnaround': 'Evaluate housekeeping staging, room access and circulation bottlenecks.',
                'logistics': 'Review delivery access, storage capacity and robot-compatible paths.',
                'energy_optimization': 'Evaluate future storage/PV sizing only after measured counterfactual benefits.',
                'data_quality': 'Review sensor redundancy and maintainability in future specifications.',
                'occupancy_surge': 'Review service-capacity assumptions under peak occupancy.',
                'ventilation_maintenance': 'Review AHU filter accessibility and sensor instrumentation.',
            }.get(issue, 'Review whether verified recurring issues justify design changes.')
            add('PLATO', issue, f'{issue.replace("_", " ").title()}: design review candidate', episode_rows,
                design, 'Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.')
    return candidates


def generate(decisions, data):
    counts = Counter(d['issue_type'] for d in decisions)
    candidates = build_learning_candidates(decisions)
    distinct = len(set(d.get('episode_id') or d['event_id'] for d in decisions))
    lines = [
        '# PLATO-40 | Evidence-backed learning loop', '',
        '> Synthetic replay only. Recommendations are testable hypotheses, not demonstrated learning gains, causal outcomes, measured savings, or verified physical defects.',
        '> Episode counts reflect prototype detections, not independently labelled ground truth.', '',
        '## Evidence summary', '',
        f'- Decisions: {len(decisions)}', f'- Distinct detected episodes: {distinct}',
        f'- Traceable improvement candidates: {len(candidates)}',
        '- Method: group decisions by episode and issue class, identify recurring assets, and require at least three distinct episodes for asset-specific and design-review candidates.', '',
        '| Issue class | Decisions |', '|---|---:|',
    ]
    lines.extend(f'| {k} | {v} |' for k, v in sorted(counts.items()))
    for audience in ('CLARA', 'PLATO'):
        lines += ['', f'## {audience} improvement candidates', '']
        subset = [c for c in candidates if c['audience'] == audience]
        if not subset:
            lines.append('No candidates supported by the available replay.')
        for i, c in enumerate(subset, 1):
            lines += [
                f'### {audience}-{i:02d} | {c["title"]}', '',
                f'- Evidence: {c["episode_count"]} detected episodes, {c["decision_count"]} decisions; basis: {c["basis"]}.',
                f'- Assets (up to five): {", ".join(c["assets"]) or "not specified"}.',
                f'- Months observed: {", ".join(c["months"]) or "not specified"}.',
                f'- Median decision confidence: {c["median_confidence"] if c["median_confidence"] is not None else "unavailable"}.',
                f'- Example episode IDs: {", ".join(c["sample_episode_ids"])}.',
                f'- Candidate change: {c["suggestion"]}',
                f'- Required validation: {c["validation"]}',
                '- Status: **hypothesis only; not implemented or independently validated**.', '',
            ]
    lines += [
        '## Closed-loop evaluation protocol', '',
        '1. Capture each candidate with its evidence, decision IDs and affected assets.',
        '2. Label a stratified sample of true incidents and benign look-alikes independently.',
        '3. Change one rule or workflow on development data; record the version and expected trade-off.',
        '4. Compare the baseline and candidate on a frozen evaluation split using precision, recall, missed critical incidents, approval load and resource conflicts.',
        '5. Promote only after human safety review and an unchanged holdout evaluation. Do not tune on holdout.', '',
        '## Target architecture', '',
        'BMS/PMS/telemetry adapters -> quality-controlled event store -> detectors -> shared scheduler and safety policy -> approval/consent interface -> mock executor -> independent verification -> traceable CLARA rule proposals and PLATO design reviews.', '',
        '## Limitations', '',
        '- Simulated actions do not change the historical replay; post-action causality cannot be established.',
        '- No live building, measured cost reduction, confirmed physical incident labels or independently verified design outcomes.',
        '- Multiple candidates can derive from the same episodes; candidate count is not a learning-rate metric.',
        '- Holdout must remain untouched until the final frozen evaluation.', '',
    ]
    return '\n'.join(lines)
