# PLATO-40 — CLARA Future
### Explainable, human-supervised hotel operations

**Proximata Hackathon 2026 · Rhomberg / PLATO × CLARA Future challenge**

PLATO-40 is an offline prototype for a **fictional 40-room self-check-in hotel**. Using a synthetic year of bookings, guest requests, building telemetry and operations data, it detects problems, recommends actions, checks resource and safety constraints, simulates execution, and prepares evidence-linked recommendations for future buildings.

> **Important:** This is a *synthetic replay and decision-support system*. It is not connected to real PLATO buildings, hotel booking systems, robots, equipment, guest messaging services or live operational APIs. No physical action is taken and no guest message is sent.

## What it does

| Stage | Demonstrated capability |
| --- | --- |
| **Observe** | Ingest synthetic occupancy, bookings, guest requests, access, water, HVAC, equipment, energy, logistics, staffing, work orders and weather data |
| **Understand** | Detect room-turnaround conflicts, suspected leaks, comfort/energy problems, equipment degradation, maintenance and weekend surges |
| **Decide** | Generate timestamped JSONL decisions with severity, evidence, dependencies, confidence and verification plans |
| **Coordinate** | Reserve available staff/robot slots and propose cleaning, inspection, maintenance and guest communications |
| **Act safely** | Enforce approval, consent and prerequisite safeguards; simulate execution instead of controlling equipment |
| **Verify** | Record replay observations and distinguish unverified outcomes from actual confirmation |
| **Learn** | Generate evidence-linked improvement *hypotheses* for CLARA operations and PLATO building design |
| **Communicate** | Show CLARA's multilingual guest-message drafts powered by an Adaption Labs–expanded dataset |

### Architecture

```text
Synthetic 2026 hotel data
         │
         ▼
   Data loader ──► Detectors and planners ──► Scheduling / resource reservations
                                              │
                                              ▼
                                     Decision safety checks
                                              │
                              ┌───────────────┼─────────────────┐
                              ▼               ▼                 ▼
                        decisions.jsonl   Mock execution    Verification
                              │               │                 │
                              └───────────────┼─────────────────┘
                                              ▼
                                  React Control Room dashboard
                                              │
                                              ▼
                              Evidence-backed learning hypotheses
```

Decisions and mock-execution statuses are **not** confirmations that work was performed.

## Scenario coverage

The prototype addresses the five cases defined in the [challenge brief](data/dev/CHALLENGE.md):

| Scenario | Example behavior |
| --- | --- |
| **S01 — Perfect Checkout** | Identify tight checkout-to-check-in windows, coordinate housekeeping, propose guest updates, avoid premature room release |
| **S02 — Hidden Water Leak** | Flag suspicious consumption while treating unreliable metering and uncertainty conservatively |
| **S03 — Heating & Energy** | Evaluate comfort and equipment signals with weather and tariff context; propose bounded responses |
| **S04 — Maintenance** | Detect equipment/sensor degradation, check work orders and staff availability, propose escalation |
| **S05 — Weekend Surge** | Coordinate cleaning and logistics against higher demand and capacity constraints |

The [`data/dev/README.md`](data/dev/README.md) documents the synthetic data sources, units and timestamp conventions. [`data/dev/DECISION_CONTRACT.md`](data/dev/DECISION_CONTRACT.md) defines the JSONL decision format.

## CLARA × Adaption Labs: multilingual guest communication

The integration adds a clearly labeled **CLARA Suggestion** card to the existing **Approvals** page. It does **not** create a chatbot or a guest portal.

1. An operational detector identifies an early-check-in / room-turnaround situation.
2. The backend looks up the guest's recorded language in `guest_requests.csv` when available.
3. [`core/guest_messages.py`](core/guest_messages.py) chooses a scenario/language template from [`data/adaption/guest_message_templates.csv`](data/adaption/guest_message_templates.csv).
4. A `notify_guest` decision records the suggested wording as **`PROPOSED (...; NOT SENT)`**.
5. The frontend displays the message in its **CLARA Suggestion** card for staff review, with a **Draft · Not sent** label.

**Adaption contribution:** We used Adaption Labs to expand **10 original guest-communication examples into 60 template records** covering **10 scenarios × 6 languages**: English, German, French, Italian, Spanish and Dutch. The resulting CSV is integrated directly into the backend; it is an exported artifact, not a runtime request to Adaption. This is **an Adaption-generated offline dataset**, not a live Adaption inference API or a trained online chatbot.

**Current scope:** The room-turnaround detector invokes the `early_checkin` template. The other translated scenarios exist in the dataset and selector but are **not all connected to their own detectors**. The selector falls back to English if a scenario-language combination is absent. No message is delivered, and delivery confirmation is not implemented.

## Quick start

### Backend

Run from the repository root with **Python 3.10+**:

```bash
python3 -m pip install -r requirements.txt

# Quickstart synthetic replay
python3 run.py data/quickstart --out reports/local_quickstart/decisions.jsonl

# Full development replay (larger dataset)
python3 run.py data/dev --out reports/local_dev/decisions.jsonl

# Backend regression tests
python3 -m pytest -q
```

Each standard run writes `decisions.jsonl`, `execution_log.jsonl`, `verification.jsonl`, `insights.md`, and additional execution-bridge evidence beside the output path. Use `--no-extras` if only the decision file is required.

You can test the multilingual selector directly:

```bash
python3 -c "from core.guest_messages import propose_guest_message; print(propose_guest_message('de')); print(propose_guest_message('fr'))"
```

### Frontend

The frontend uses React, TanStack Router and Vite. Use **Node.js 24+** for best compatibility with the currently pinned build dependencies:

```bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite (typically **http://localhost:8080**).

| Page | What you can review |
| --- | --- |
| **Overview** | Operational replay counts, pending reviews and recent events |
| **Records** | Timeline of decisions |
| **Incidents** | Incident evidence, priority and proposed actions |
| **Approvals** | Action proposals, mock-execution status, human oversight and CLARA multilingual drafts |

The retired **Live demo** page is not in the navigation. The `/demo` route file still exists but is not part of the current guided user flow.

The frontend initially loads `frontend/public/decisions.jsonl`. On Overview you can use **Reload URL** or import a backend ZIP/JSONL. UI approval and consent checkboxes are **local simulations**, not calls to the backend executor. When importing a new decision file, the UI deliberately clears its saved execution mapping to avoid mismatched evidence.

### Optional evaluation tools

```bash
# Deterministic synthetic planning and release artifacts
python3 scripts/final_release.py --data data/quickstart --out-dir reports/local_release --seed 40

# Episode-disjoint temporal split and replay-determinism checks
python3 scripts/validate_release.py --decisions decisions.jsonl --out reports/local_acceptance
```

These report **synthetic assumptions and deterministic replays**, not experimentally measured improvements or live building outcomes.

## Data and output contract

The primary backend output is newline-delimited UTF-8 JSON. Each decision includes an `event_id`, `timestamp_utc`, `affected_assets`, `issue_type`, `action`, `priority`, `reason`, `requires_human_approval`, plus optional evidence, dependencies, resource ID, consent and verification fields.

A guest-notification decision may include a reason beginning with `PROPOSED (de; NOT SENT):` followed by the Adaption-generated German draft. Internal response deadlines may be appended for staff workflow purposes; they should not be presented as part of the guest-facing message.

The full required and recommended decision fields are reproduced below, so reviewers can follow the output without opening a second guide.

## Safety, verification and limits

- High-impact actions require appropriate **human approval**, and occupied-room actions can require **guest consent**.
- Scheduling checks capacity; room release depends on separate cleaning/readiness evidence.
- Missing prerequisites can block or defer proposed execution. Mock execution **never actuates** HVAC, dispatches a real robot or contacts a guest.
- Historical observations and simulated outcomes are not causal proof of recovery or savings.
- Learning artifacts describe **testable operational/design hypotheses** rather than validated self-improvement.
- This system consumes booking records and can propose responses to arrivals, but does **not** modify live bookings or process cancellations through a connected reservation API.

## Reproducibility and submission notes

The Git tag [`pre-holdout`](https://github.com/vrhvnsk/plato40/tree/pre-holdout) freezes the original baseline at commit **`2fb5114`**. Subsequent commits add Adaption-powered guest communication and its frontend display without moving the tag.

**Do not conflate saved replays:** Older bundled development artifacts refer to **6,290 decisions**, while the locally regenerated multilingual development replay produced **6,146 decisions across 4,250 episodes**. The difference has not been fully reconciled. Likewise, the refreshed `frontend/public/decisions.jsonl` should not automatically be assumed to match older stored execution, verification or learning artifacts.

A file called `decisions_holdout.jsonl` exists in the repository, but its provenance has **not been independently verified** in this documentation. Its filename alone is not proof of an untouched, organizer-supplied holdout run. The temporal split created by `scripts/validate_release.py` is explicitly an **internal synthetic holdout**, not the organizer's independent data.

**Observed local checks:** **149 Python tests passed** on the integrated backend, and the frontend production build completed. A local frontend test run showed **15 passing and 6 failing tests** involving incident selection / incident-summary UI; these have not been established as CLARA regressions. Do not represent the full frontend test suite as passing.

The project is a **hackathon prototype**, not a validated autonomous controller. No authenticated post-action outcomes, measured energy savings, real delivery acknowledgements, real-world guest consent or proven automatic policy updates are claimed.

## Repository map

```text
core/                    Detectors, planners, scheduler, safety, executor,
                         verification, learning, CLARA message templates
analysis/                Evidence analysis and insight generation
data/quickstart/         Small synthetic scenario dataset
data/dev/                Full synthetic dataset, challenge brief and contracts
data/adaption/           Adaption-expanded multilingual guest templates
frontend/                Control-room dashboard (React / Vite)
dashboard/               Optional Streamlit dashboard
scripts/                 Release, demo and acceptance utilities
tests/                   Backend regression and acceptance tests
reports/                 Historical replay, audit and evidence artifacts
decisions.jsonl           Bundled development replay decisions
decisions_holdout.jsonl   Named holdout artifact; verify provenance before use
```

## Complete input-data reference

The challenge provides two independent synthetic runs with the same layout. **Quickstart** covers 21 January days; **dev** covers 365 days of 2026. Do **not concatenate them**.

| Input file | Main contents | Critical interpretation |
| --- | --- | --- |
| `building.json` | Forty rooms, assets, sensor IDs, capacities, operating constraints | Comfort band for occupied rooms; room and robot capabilities |
| `manifest.json` | Dataset profile, timing, units, limitations | Verify which synthetic run is being replayed |
| `bookings.csv` | Booking ID, room, creation, booked arrival/departure, status | A confirmed booking is **not** evidence of a ready room; cancelled records exist |
| `access_log.csv` | Door/credential access attempts and result | Granted entry does not necessarily imply departure or room vacancy |
| `events.jsonl` | Check-in/out, housekeeping, logistics, BMS alarms | Alarms can be delayed, incomplete or false; cleaning events are separate from planned tasks |
| `room_telemetry.csv` | Temperature, setpoint, humidity, CO₂, presence, window, housekeeping state | Fifteen-minute samples; zero motion is not proof of vacancy |
| `room_water.csv`, `water_main.csv` | Cumulative litres | Consumption requires differencing; meter resets/exchanges can mimic leaks |
| `energy.csv` | HVAC, total load, PV, battery, grid flows | Positive battery discharge / negative battery charge |
| `weather.csv`, `weather_forecast.csv` | Measurements and forecasts | Use only forecasts issued by decision time |
| `tariff.csv` | Hourly day-ahead EUR/kWh | Respect publication timestamps to prevent future information leakage |
| `equipment.csv` | Heat-pump `HP1` and ventilation `AHU1` readings | No ground-truth equipment fault labels |
| `logistics.csv` | Bin fill levels, central waste container, vending stock | Fill percentages may be capped; restock/pickup lead times matter |
| `staff_roster.csv` | Cleaners, technicians, robots, shift status and known-at time | Absences must be respected; no invented capacity |
| `work_orders.csv` | Preventive/corrective work and completion history | A scheduled work order is not proof of repair |
| `guest_requests.csv` | Request, room, booking, language, requested service, due time, consent requirement | Consent **required** is not consent **granted**; a request is not an outgoing message |

**Time:** UTC ISO 8601 (`...Z`) in source outputs; operations use `Europe/Vienna`. Telemetry is generally at 15-minute resolution. Known-at timestamps such as `created_utc`, `issued_utc`, `published_utc` and `status_known_utc` matter: a historical replay must not use observations unavailable at the time of the decision. An empty value means **missing**, not zero.

## Decision format and audit trail

One UTF-8 JSON object per line in `decisions.jsonl` (or `decisions_holdout.jsonl` for genuine holdout input). The formal contract is reproduced here:

| Field | Required | Interpretation |
| --- | --- | --- |
| `event_id` | Yes | Unique decision identifier |
| `timestamp_utc` | Yes | Decision time, ISO 8601 UTC |
| `affected_assets` | Yes | Non-empty array of affected room, asset or resource IDs |
| `issue_type` | Yes | Operational issue classification |
| `action` | Yes | Proposed or mock-executed action |
| `priority` | Yes | `critical`, `high`, `medium` or `low` |
| `reason` | Yes | Human-readable justification or proposed-message draft |
| `requires_human_approval` | Yes | Whether approval is mandatory |
| `autonomy` | Recommended | `autonomous`, `human_approval`, `approval_and_consent`; proposal-only may also be used |
| `episode_id` | Recommended | Groups related decisions into one operational episode |
| `evidence` | Recommended | Traceable source-data references |
| `confidence` | Recommended | Numeric heuristic score, **not** a calibrated probability |
| `expected_outcome` | Recommended | Expected or explicitly simulated effect |
| `verification_plan` | Recommended | Signals to look for, or reason to escalate |
| `dependencies` | Recommended | Other decision IDs / required preconditions |
| `guest_request_ids` | Optional | References to affected guest requests |
| `recipient_booking_ids` | Optional | Possible booking recipients, if resolved |
| `requires_guest_consent` | Optional | Whether additional consent is needed |
| `resource_id` | Optional | Scheduled staff or robot identifier |

**Action vocabulary:** `schedule_cleaning`, `dispatch_robot`, `adjust_room_setpoint`, `optimize_energy`, `block_room`, `release_room`, `reassign_room`, `request_inspection`, `dispatch_technician`, `order_service`, `notify_guest`, `flag_anomaly`, `defer_action`, `request_human_approval`. Additional implementation-specific actions may occur; inspect the corresponding decision and tests.

**Example** (illustrative fields and IDs, not extracted from a historical event):

```json
{
  "event_id": "D-example-001",
  "timestamp_utc": "2026-01-02T10:39:45Z",
  "affected_assets": ["R202"],
  "issue_type": "room_turnaround",
  "action": "notify_guest",
  "priority": "medium",
  "reason": "PROPOSED (de; NOT SENT): Ihr Zimmer wird noch vorbereitet.",
  "requires_human_approval": false,
  "requires_guest_consent": false,
  "autonomy": "autonomous",
  "episode_id": "TURN-R202-2026-01-02",
  "evidence": ["event_or_request:guest_request:R202:2026-01-02T10:39:45Z"],
  "dependencies": ["D-example-cleaning"],
  "verification_plan": "Verify booking recipient and delivery; manual review if unresolved."
}
```

`event_id` counts **decisions**, not unique incidents. Several decisions can share an `episode_id`. Separate artifacts have different evidentiary weight:

- **`decisions.jsonl`**: what the engine proposed and why.
- **`execution_log.jsonl`**: what the **mock executor** allowed, deferred, blocked, or simulated. It does not record real actions.
- **`verification.jsonl`**: observations/verification status available to the replay; no causal proof of success from an unmodified archive.
- **`insights.md`**: operational and design recommendations, with uncertainty.
- **`learning_candidates.json`**: structured candidate hypotheses, not learned policy parameters.
- **`autonomy_trace.jsonl` / `autonomy_report.json`** (when prepared): deterministic *synthetic* action alternatives, plan stages, scenario outcomes and audit information.

### Autonomy and execution safeguards

| Autonomy tier | Examples | Enforcement / representation |
| --- | --- | --- |
| Autonomous **within limits** | Housekeeping scheduling, robot task proposals, anomaly logging, bounded comfort/energy planning, guest drafts | Still subject to resource availability, dependencies, safety constraints, and mock-only execution |
| Human approval | Technician/contractor dispatch, room blocking or guest reassignment, cost-sensitive actions | `requires_human_approval = true`; without a trusted confirmation, remain pending |
| Human approval **plus guest consent** | Entry into occupied rooms or sensitive safety interventions | Both gates must be satisfied; needing consent must never be mistaken for possessing it |

The mock executor is deliberately conservative. With missing prerequisites it reports statuses such as `pending_dependency`, `pending_approval`, `pending_consent`, `pending_resource`, `pending_verification`, `blocked` or `logged_only`. For guest messages it may return `proposed_not_sent`; energy planning may be `proposal_only_not_dispatched`. A `simulated_completed` result means **simulated processing**, not verified physical completion. Resource reservations should not be double-booked or assumed to complete a task.

**Caution about the browser UI:** toggling an approval in the frontend changes local display state, not a real or trusted executor approval. It does not send a translated guest message. Recorded mock-execution entries may remain pending even after a user clicks a visual approval.

### Learning and feedback: CLARA → PLATO

The challenge asks for two different kinds of feedback:

1. **CLARA operations:** candidates for cleaning scheduling, leak detection, equipment monitoring, energy setpoints, alarm tuning, maintenance prioritisation and guest-service processes.
2. **PLATO design:** candidate changes in sensor coverage, maintenance access, system sizing, waste/logistics layout, resilience and other future-building design trade-offs.

The bundled reports include **35 evidence-linked hypotheses** (27 operations-focused and 8 design-review candidates) associated with the historical development replay. Each hypothesis should be treated as something to **test**, not as a validated saving or trained/automatically deployed improvement. Evidence links, sample episodes, time coverage, uncertain inputs and a proposed verification test matter more than the hypothesis count.

A production learning loop would need verified outcomes, comparable baselines, independently labelled episodes, guardrails, offline/online evaluation, review and safe rollout. None of those are represented as already proven in this synthetic replay.

## Reproducible evaluation and frozen holdout

The event replay is designed to be run from a single documented entry point:

```bash
python3 run.py PATH_TO_DATASET_DIRECTORY --out PATH_TO_OUTPUT/decisions.jsonl
```

For example:

```bash
python3 run.py data/quickstart --out reports/local_quickstart/decisions.jsonl
python3 run.py data/dev --out reports/local_dev/decisions.jsonl
```

For **a genuine organizer-supplied unseen holdout**, use that separate directory and preserve the result:

```bash
python3 run.py /path/to/organizer-holdout --out decisions_holdout.jsonl
```

Use the input's own `manifest.json` to identify the run. Do not relabel `data/dev`, a synthetic temporal split or an empty file as unseen holdout evidence.

The `pre-holdout` tag is the frozen baseline. In the current repository it points to commit `2fb511419fe19237986ae8c1040268c492990810`. The subsequent integration commits include:

- `7043343`: offline Adaption-expanded multilingual CLARA selector and templates.
- `9026deb`: refreshed bundled frontend decision data.
- `1fed8f8`: visible CLARA card on Approvals.
- Later changes: hide the retired Live demo from navigation and remove its Overview shortcut.

**Post-tag-change explanation:** These later changes improve guest-draft wording, display and navigation. The frontend decision bundle was regenerated as part of the multilingual work, resulting in a different record count. Therefore the newer replay should **not** be described as identical to the frozen baseline, nor should unexplained differences be attributed solely to translation. The historical root replay and refreshed frontend replay must be assessed as distinct artifacts.

### What we tested — and what remains unverified

| Check | Recorded result / caveat |
| --- | --- |
| Python backend tests | **149 passed** in the team's local integrated run (deprecation warnings remain) |
| React frontend production build | **Succeeded locally** after `npm ci` |
| Frontend component tests | **15 passed, 6 failed**, in incident-state/summary tests during the recorded local run |
| Multilingual backend quickstart | **474 decisions / 317 episodes**, including 85 `notify_guest` decisions in the tested run |
| Full development replay with CLARA change | **6,146 decisions / 4,250 episodes** in the recorded local run |
| Earlier bundled development artifact | **6,290 decisions**, from a different saved run; not equivalent to the refreshed file |
| CLARA dashboard display | Verified locally showing a German **CLARA Suggestion** card and **Draft · Not sent** status |
| Independent organizer holdout | **Not independently verified here**; do not infer validity from file presence |
| Physical execution, delivery, causation, measured savings | **Not performed / not evidenced** |

These are *observations from the team’s test session*, not claims that tests have been rerun after every later change. Continuous integration is defined in `.github/workflows/acceptance.yml`, but local observations and CI status must not be conflated. The frontend unit failures should be resolved separately from the CLARA card if time allows.

### Reviewer verification checklist

1. Run `python3 -m pytest -q` to inspect backend regression results.
2. Run `python3 run.py data/quickstart --out reports/local_quickstart/decisions.jsonl`.
3. Inspect `decisions.jsonl`, `execution_log.jsonl`, `verification.jsonl` and `insights.md` in that output directory.
4. Check that sensitive actions require approval/consent; missing prerequisites do not silently become real actions.
5. Open the four dashboard pages, find `notify_guest`, and verify that CLARA labels its text **Draft · Not sent**.
6. Compare the tagged baseline against later commits and examine any genuine holdout artifact separately.
7. Distinguish replay observations, simulated results, hypothesis evidence and measured/verified outcomes.

## Target architecture: how this would become a real building system

The challenge’s longer-term vision requires integrations that are deliberately outside this offline prototype. A production roadmap would introduce:

```text
Reservations / PMS ─┐
BMS + IoT sensors ──┤
Access + housekeeping├──► Event bus + identity + data-quality layer
Tariffs / weather ──┤                         │
Robots + work orders┘                         ▼
                                 CLARA policies + planners
                                             │
                                 Safety / privacy / approvals
                                             │
                      ┌──────────────────────┼───────────────────┐
                      ▼                      ▼                   ▼
               Building APIs          Work-order / robot    Guest messaging
                      │                      │                   │
                      └──────────────────────┼───────────────────┘
                                             ▼
                                   Verified acknowledgements
                                             │
                                   Outcome monitoring / A-B tests
                                             │
                                  Controlled CLARA policy updates
                                             │
                               Evidence for future PLATO design
```

For a real deployment this also needs role-based access control, auditable consent, secure credentials, vendor API reliability, rollback, escalation, human override, privacy review, independent safety validation and calibrated operational evaluation.

## Limitations, provenance and licensing

**Not implemented / not claimed:** real booking modifications or cancellation handling through a reservation API; live robot control; real HVAC or battery dispatch; outbound guest emails/SMS; true guest portal; authenticated approval/consent workflows; measured energy savings; causal performance gains; or a deployed adaptive learning model.

The challenge defines PLATO-40 as a fictional building. The data is synthetic and published by the challenge under **CC BY 4.0**; attribution: “PLATO-40 synthetic dataset, Proximata Hackathon ’26 – Rhomberg track.” The repository contains an MIT `LICENSE` for team code. PLATO and CLARA are Rhomberg product names used only for identifying the challenge context; this project is not a representation of their real operating systems.

**Submission artifacts at repository root:** `README.md`, `LICENSE`, `.env.example`, `decisions.jsonl`, `decisions_holdout.jsonl` (if a genuine independent holdout has been run and validated), `insights.md`, plus the `pre-holdout` Git tag. Never commit API tokens, private guest data or deployment secrets.

**Competition evaluation areas:** technical implementation (35/100), autonomous operation and impact (30/100), learning loop and vision (15/100), and demo/presentation (20/100). The README is documentation of implemented capabilities, not a substitute for actual tests, video and required deliverables.

---

**PLATO-40 · CLARA Future — Explainable building operations, safe simulated action, and traceable lessons for what comes next.**
