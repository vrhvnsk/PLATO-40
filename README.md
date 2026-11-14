# PLATO 4.0 | Evidence-driven hospitality operations

**Observe → Understand → Decide → Act → Verify → Learn**

PLATO 4.0 is a hackathon prototype for coordinating hotel and building operations across bookings, housekeeping, guest requests, water consumption, heating, energy, maintenance, staffing and logistics. Instead of producing isolated alerts, it uses operational context to propose prioritised decisions, enforce safety and resource constraints, and generate auditable evidence about mock execution and verification.

**Scope:** This is a replay-driven decision-support and *simulated* execution system. It does not control physical HVAC equipment, dispatch real robots, send real guest messages or approve real maintenance work. Counterfactual utilities and simulated outcomes are illustrative, not independently measured savings or success rates.

## Quick start: the required single-command pipeline

From the repository root, with Python 3.10+ and dependencies installed:

```bash
python -m pip install -r requirements.txt
```

**One command takes a dataset directory and writes `decisions.jsonl`:**

```bash
python run.py data/quickstart --out decisions.jsonl
```

To process another dataset (including an organizer-provided holdout):

```bash
python run.py /path/to/data_directory --out decisions.jsonl
```

`data_directory` is a positional argument; `--out` is optional and defaults to `decisions.jsonl` in the current working directory. The CLI runs ingestion, detection, constrained scheduling, safety validation and decision serialization without starting a frontend. By default it also creates `execution_log.jsonl`, `verification.jsonl`, `insights.md` and executor bridge reports beside the output file. Add `--no-extras` to produce only the decision file.

**Verified on this supplied archive:** `python run.py data/quickstart --out ... --no-extras` produced **474 decisions across 317 episodes**; `python run.py examples/synthetic_fixture --out ...` produced **6 decisions across 3 episodes**. `python -m pytest -q` passed **149 tests**. These are local checks, not an independent holdout evaluation.

### Output contract

`decisions.jsonl` is UTF-8 JSON Lines: one JSON object per line, not a JSON array. Records include fields such as `episode_id`, `issue_type`, `priority`, `action`, evidence, confidence, approval/consent requirements and verification plans. Several decisions can belong to one episode; decision count is not incident count. The exact serialized record is determined by `core/decisions.py` and the detectors.

Check the output with:

```bash
python -c "import json; p='decisions.jsonl'; rows=[json.loads(s) for s in open(p,encoding='utf-8') if s.strip()]; print(len(rows),'valid decisions')"
```

The pipeline expects the project dataset contract and corresponding input files, not an arbitrary directory of unrelated CSVs. Inspect `data/quickstart`, `data/dev`, `examples/synthetic_fixture` and `core/loader.py` for supported input structures.

## The operational problem

A hotel is not a collection of independent dashboards. An early check-in creates a housekeeping deadline; an occupied room constrains maintenance; weather affects heating demand; heat-pump degradation changes energy and comfort trade-offs; unexpected water use may be a leak or ordinary cleaning. Optimising each subsystem independently can create conflicting or unsafe actions.

PLATO correlates signals, considers benign explanations and unreliable data, prioritises feasible interventions, respects shared resources and human approval gates, and records what would need to be observed to confirm success.

## Pipeline architecture

```text
Building / bookings / access / telemetry / weather / tariff / staff / logistics
                                  |
                         core/loader.py
                                  |
                   core/detectors.py + planners
                                  |
                   core/scheduler.py (capacity)
                                  |
                     core/safety.py (gates)
                                  |
                        decisions.jsonl
                                  |
                   mock executor + verification
                                  |
                    insights + evidence reports
                                  |
                        dashboard / frontend
```

Core responsibilities:

- **Observe:** Load and correlate time-indexed operational datasets; distinguish missing or suspect observations from reliable measurements.
- **Understand:** Identify risk episodes with evidence, uncertainty, alternate explanations and data-quality caveats.
- **Decide:** Propose actions and priorities across rooms, guests, maintenance, energy and logistics, respecting staff capacity and operational deadlines.
- **Act:** Record permitted mock actions or requests for human approval. This is not a live actuator interface.
- **Verify:** Produce verification plans, retrospective checks and simulated outcome evidence where applicable. A simulated action is not proof of a real-world result.
- **Learn:** Aggregate traceable hypotheses and potential improvements. No real-world policy promotion or empirically proven learning gain is claimed.

The integrated autonomy lab additionally demonstrates multi-step synthetic planning, counterfactual alternatives, shared resource reservations, seeded replay and trace digests. See `FINAL_RELEASE_GUIDE.md`, `core/autonomy_lab.py` and `scripts/final_release.py`. These demonstrations are separate from the required `run.py` JSONL entry point.

## Scenarios

| Scenario | Operational conflict | Expected safe response |
|---|---|---|
| **S01: Perfect Checkout** | Early departure, early check-in and tight cleaning capacity | Prioritise feasible cleaning; never release an uncleaned room; propose realistic guest communication |
| **S02: Hidden Water Leak** | Abnormal water use with occupancy, housekeeping and meter ambiguity | Cross-check context and reliability; investigate or escalate with uncertainty |
| **S03: Heating and Energy** | Comfort, heat-pump degradation, weather and energy costs | Evaluate constrained comfort/energy interventions and approval gates |
| **S04: Maintenance** | Filter/sensor degradation and maintenance work | Detect equipment issues, handle bad sensor evidence, schedule or escalate technician work |
| **S05: Weekend Surge** | Occupancy, housekeeping, staffing and supply pressure | Coordinate shared capacity, lead times, room readiness and guest deadlines |

The scenarios are synthetic replay cases, not evidence of deployment at a live property. Coverage depends on available input observations.

## Safety and autonomy

PLATO distinguishes a proposed decision from an authorised or completed action. Human approval and guest consent requirements must not be bypassed. Room readiness, resource availability and other hard constraints take precedence over speed or nominal optimisation. Priority is an urgency ranking, not a calibrated harm estimate. Frontend approval and consent toggles are **illustrative UI controls**, not backend authorisation or physical execution.

## Outputs and evidence

| Artifact | Meaning |
|---|---|
| `decisions.jsonl` | Primary required decisions, one JSON object per line |
| `execution_log.jsonl` | Mock execution statuses and constraints |
| `verification.jsonl` | Verification plans/results from replay evidence |
| `insights.md` | Evidence-based insights and hypotheses |
| `reports/executor_bridge/` | Executor bridge/audit material beside the output directory |
| `learning_candidates.json` | Bundled learning candidates, not proven improvements |
| `reports/full_dev/` | Saved full development replay and assurance evidence |

The bundled root `decisions.jsonl` contains **6,290 saved development decisions**. This historical artifact has **not** been confirmed to be exactly reproducible by the current detector code. Do not treat it as an independently reproduced or holdout result. The quickstart replay *was* regenerated with the current code (474 decisions).

## Dashboard and guided demo

The React/Vite frontend is a replay viewer for incidents, evidence, timeline, priorities, approvals and decision/action trails:

```bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite. It initially reads `frontend/public/decisions.jsonl` (the bundled full-development replay). Import a newly generated JSONL or backend ZIP to inspect a different run; generating a new backend file does **not** automatically replace the frontend's bundled file. The guided `/demo` route shows planning steps, alternative action scores and **synthetic** outcomes. The optional Python dashboard can be launched with `streamlit run dashboard/app.py`.

The frontend production build and browser end-to-end tests were **not independently verified in this review**. A GitHub Actions acceptance workflow and Playwright tests are included; see `FINAL_RELEASE_GUIDE.md`.

## Tests and reproducibility

```bash
python -m pytest -q
```

This supplied archive passed **149/149** backend tests in the review environment. For the additional release workflow:

```bash
python scripts/final_release.py --data data/quickstart --out-dir reports/final_release --seed 40
python scripts/validate_release.py
```

The internal temporal, episode-disjoint holdout generated by the validation script is **not** an independent organizer holdout. For an actual organizer holdout, freeze code before inspection, run the documented CLI on the supplied directory, and retain its genuine `decisions.jsonl` separately. Never rename development or internally generated data as organizer holdout.

## Repository map

- `run.py`: documented single-command pipeline entry point
- `core/`: loading, detection, scheduling, safety, decisions, execution simulation, verification, evidence, learning and planning
- `analysis/`: insight generation and audit helpers
- `data/`: bundled quickstart and development datasets
- `examples/`: synthetic fixture and generator
- `frontend/`: interactive control-room replay and guided demo
- `dashboard/`: optional Streamlit interface
- `scripts/`: demo preparation, release and acceptance utilities
- `tests/`: regression, scenario, safety and acceptance tests
- `reports/`: saved replay, assurance, impact and release evidence
- `JUDGES_GUIDE.md`: judge-facing walkthrough and caveats
- `DEMO_SCRIPT.md`: timed presentation walkthrough
- `FINAL_RELEASE_GUIDE.md`: autonomy lab, acceptance and release details

## Evaluation and limitations

The hackathon evaluation weights are technical implementation **35**, autonomous operation and impact **30**, learning loop and vision **15**, and demo/presentation **20** points.

What the current project demonstrates: a functioning command-line decision pipeline on bundled quickstart and fixture data, automated backend regression coverage, evidence-oriented decisions, mock execution, safety gating and an interactive replay UI.

What it does **not** establish: independent organizer-holdout performance; verified physical actions, robot dispatch, guest communication or actuator acknowledgements; measured energy savings; calibrated causal counterfactuals; real-world closed-loop learning; or production-grade safety certification. The full-development replay's exact reproducibility remains unconfirmed. Frontend browser/build verification remains separate from the backend tests.

## Vision

PLATO's long-term architecture is a coordinated operations layer connecting property-management systems, building telemetry, staff workflows, authorised agents and robots, and human oversight. Its core principle is simple: **an operational system should explain the evidence behind a decision, respect the constraints around it, and distinguish attempted actions from verified outcomes.**
