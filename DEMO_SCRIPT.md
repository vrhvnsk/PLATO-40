# PLATO-40 | Judges' demonstration (5–7 minutes)

## Setup

From the repository root, run `python -m pytest -q` and `python scripts/prepare_demo.py`. From `frontend/`, run `npm ci` and `npm run dev` (install Node.js 22 LTS if the native Rolldown binding fails on Windows). Open the URL printed by Vite, then choose **Live demo** in the sidebar. The static demo is populated from the bundled 6,290 decisions, not synthetic UI examples.

## Walkthrough

1. **Observe (45 sec).** Show the number of decisions and episodes, then choose **Water leak** or **Room turnaround**. Identify the timestamp, assets, and raw evidence references. The evidence strings are references into the source data, not independently reloaded telemetry charts.
2. **Understand (45 sec).** Explain the detector's reason and confidence, then discuss data quality and benign look-alikes. Do not imply confidence is a calibrated probability unless demonstrated.
3. **Decide and coordinate (60 sec).** Point out action, priority, resource dependencies, human approval, guest consent and room readiness. Switch to an approval-requiring scenario. Explain that the interface is read-only replay; approval toggles are local demonstrations.
4. **Mock execute (60 sec).** Show the actual fail-closed executor record and any missing safeguards. `pending_*`, `blocked`, `proposal_only_*` and `logged_only` are not successful physical executions. No guest messages are actually delivered.
5. **Verify (45 sec).** Show the verification plan and the `not_verified` state. Explain that post-action causation cannot be demonstrated from historical telemetry when the mock executor does not change it. The standalone pipeline can generate replay-observation statuses, but those are not causal proof.
6. **Learn (60 sec).** Show a related CLARA rule proposal and PLATO design hypothesis, if one matches the case. The 35 candidates are evidence-based hypotheses, not 35 proven improvements. Discuss how A/B replay or sensor validation would test them.
7. **Close (30 sec).** Mention 138 backend tests passing, no physical actuation, full-year reproduction not independently established, and holdout requiring organizer data.

## Reproducibility and submission

- Quickstart: `python run.py data/quickstart --out reports/demo/decisions.jsonl` (the current code previously produced 474 decisions; verify in your environment).
- Full development: `python run.py data/dev --out reports/reproduced_dev/decisions.jsonl`; compare counts and IDs to `decisions.jsonl`. A full fresh run is **not** claimed as verified here.
- Holdout: freeze code and create the `pre-holdout` Git tag **before** receiving/running organizer holdout. Run it with the same entry point and place the genuine output in `decisions_holdout.jsonl`.
- The 2026 frontend archive is a replay view. Replacing its decision file with an unrelated run invalidates the bundled executor and learning evidence; regenerate with `python scripts/prepare_demo.py` for the saved root-level dataset.
