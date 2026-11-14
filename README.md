# PLATO-40 | Autonomous building operations prototype

Hackathon demo using synthetic building telemetry and operational data. The system detects anomalies, prioritizes decisions, schedules constrained resources, records approval/consent requirements, and generates verification and learning evidence. **It does not control real building equipment or send real guest messages.**

## Run the demo

**Backend (Python 3.10+):**

```bash
python -m pip install -r requirements.txt
python run.py data/quickstart --out reports/demo/decisions.jsonl
python run.py data/dev --out reports/demo_dev/decisions.jsonl
python -m pytest -q
```

Each run writes a decision log plus mock execution, verification and insights in its output folder. `reports/full_dev/` includes the submitted full development replay and its validation/assurance evidence.

**Frontend (Node.js + npm):**

```bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite. The frontend loads the **2026 full development decision log** from `frontend/public/decisions.jsonl` by default. To inspect another run, use **Import backend ZIP or JSONL** in the dashboard, or copy the generated `decisions.jsonl` into `frontend/public/decisions.jsonl` and reload. Imported approvals and consent toggles are **UI simulations**, not executed actions.

**Optional Python dashboard:** `streamlit run dashboard/app.py`.

## Repository layout

- `core/`: detection, scheduling, safety, execution simulation, verification and learning
- `analysis/`: evidence and audit utilities
- `data/`: synthetic quickstart and development datasets with their contracts
- `frontend/`: interactive control-room replay
- `dashboard/`: optional Streamlit viewer
- `reports/full_dev/`: full development run, evidence and validation
- `reports/step5_quickstart/`: quickstart regression outputs
- `tests/`: backend regression and acceptance suite
- `examples/`: reproducible synthetic fixture generator

See `JUDGES_GUIDE.md` for scenario coverage, evaluation evidence and limitations. See `DEMO_SCRIPT.md` for the timed guided walkthrough. The frontend sidebar includes a **Live demo** page. Rebuild its evidence assets with `python scripts/prepare_demo.py`.

## Submission artifacts and reproducibility status

- `decisions.jsonl`: 6,290 **bundled development replay** decisions, identical to `reports/full_dev/decisions.jsonl`. This is not claimed to be independently reproduced with the current code.
- `insights.md` and `learning_candidates.json`: 35 traceable **hypotheses**, generated from the bundled development decisions. These are not 35 verified improvements or measured learning gains.
- `reports/step5_quickstart/decisions.jsonl`: regenerated with the current code (474 decisions). Use `python run.py data/quickstart --out reports/step5_quickstart/decisions.jsonl` to reproduce it.
- `decisions_holdout.jsonl`: **not included** because no organizer holdout dataset was supplied. Do not rename development data as holdout. Run the frozen pipeline against the organizer holdout data and place its genuine output at repository root before submission.
- `pre-holdout` Git tag: **must be created in your Git repository before running holdout**; a ZIP cannot create or verify Git history.

The frontend shows saved mock-execution status and missing safety requirements from `frontend/public/execution_log.jsonl`. Approval/consent toggles are **illustrative only** and never trigger a backend call. Importing another decisions file clears the saved execution statuses to avoid mismatched evidence.
