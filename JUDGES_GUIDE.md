# PLATO-40 | Judges' guide

## Three-minute demo

1. Start the frontend with `cd frontend && npm ci && npm run dev`.
2. The control room initially reads `frontend/public/decisions.jsonl`, copied from the full development replay in `reports/full_dev/decisions.jsonl`.
3. Inspect **Overview** for decisions, episodes and approvals; **Incidents** for evidence, priority and proposed actions; **Timeline** for the 2026 sequence; **Approvals** for human-in-the-loop gates.
4. Demonstrate an alternate dataset by importing a `decisions.jsonl` or ZIP containing one.
5. Run `python run.py data/quickstart --out reports/demo/decisions.jsonl` to show reproducible backend decisions and generated verification artifacts.

## Scenarios and capabilities

- **S01: Perfect Checkout.** Cleaning-aware room turnaround, early check-in conflict, staffing and guest-notification proposals; no release before cleaning.
- **S02: Hidden Water Leak.** Water-consumption anomaly detection, meter/occupancy checks, conservative attribution and verification.
- **S03: Heating and Energy.** Comfort and heat-pump degradation signals, weather context and energy trade-offs.
- **S04: Maintenance.** Filter and sensor degradation, maintenance proposals, technician approval and data-quality handling.
- **S05: Weekend Surge.** Occupancy, housekeeping and logistics coordination; constrained by available staff and lead times.

The backend emits structured JSONL decisions with `episode_id`, `issue_type`, `priority`, `action`, evidence, confidence, approval/consent requirements and verification plans. **Priority is an urgency ranking, not a measured harm score.** Several decisions may belong to one episode; dashboard decision counts are not unique incident counts.

## Evidence to inspect

- `reports/full_dev/decisions.jsonl`: full development decision trail
- `reports/full_dev/FINAL_VALIDATION.json` and `reports/full_dev/assurance/`: recorded validation and assurance artifacts
- `reports/IMPACT_AND_LEARNING_EVIDENCE.json`: impact/learning analysis
- `reports/step5_quickstart/`: quickstart replay and mock execution/verification
- `tests/`: automated safety and regression cases

## Boundaries and limitations

All data is synthetic. This is a **decision-support and mock-execution prototype**, not a connected production building controller. Approval/consent toggles in the frontend are illustrative and do not authorize physical work. Guest messages are proposed, not sent. Operational outcomes and energy savings are not independently measured. Learning suggestions are evidence-based hypotheses, not proven causal improvements. Scenario coverage, especially sparse-data leak attribution and sensor-degradation cases, is limited by the available synthetic observations. A holdout run should be evaluated without tuning on holdout data.

The 2026 calendar is used for the supplied development dataset. Some timestamps may be near year boundaries; this does not imply the dataset covers 2027 operationally.

## Learning-loop demonstration

`insights.md` and `learning_candidates.json` contain **35 evidence-linked improvement hypotheses** derived from the bundled 6,290-decision development replay: 27 CLARA operational candidates and 8 PLATO design-review candidates. The generator aggregates by detected episode, issue class and recurring asset; each candidate includes episode/decision counts, sample episode IDs, asset references, observed months, median confidence, a proposed change and a validation test. These candidates are **not 35 learned parameter updates or confirmed improvements**. A closed-loop evaluation would independently label episodes, compare against a frozen baseline and validate on an untouched holdout.

## Reproducibility and submission caveats

The quickstart report has been regenerated using this code and contains **474** decisions (the old saved 482-decision report was stale). The 6,290-decision full-dev report is bundled, but a fresh full-dev replay has **not** been confirmed to finish and match it. No holdout input was provided, so no genuine `decisions_holdout.jsonl` is included. Before submission, obtain the organizer holdout, freeze code with a `pre-holdout` Git tag, run the holdout once, and place its genuine decision output at the root.

The approval UI is a **replay viewer**, not a connected actuator or approval service. The approvals page displays recorded mock-execution status and unmet requirements; clicking a simulated approval does not update that status.
