# PLATO-40 | Evidence-backed learning loop

> Synthetic replay only. Recommendations are testable hypotheses, not demonstrated learning gains, causal outcomes, measured savings, or verified physical defects.
> Episode counts reflect prototype detections, not independently labelled ground truth.

## Evidence summary

- Decisions: 474
- Distinct detected episodes: 317
- Traceable improvement candidates: 31
- Method: group decisions by episode and issue class, identify recurring assets, and require at least three distinct episodes for asset-specific and design-review candidates.

| Issue class | Decisions |
|---|---:|
| data_quality | 3 |
| energy_optimization | 18 |
| heating_comfort | 184 |
| heating_plant | 3 |
| logistics | 13 |
| occupancy_surge | 96 |
| room_turnaround | 154 |
| ventilation_maintenance | 1 |
| water_leak | 2 |

## CLARA improvement candidates

### CLARA-01 | Data Quality: rule and workflow review

- Evidence: 3 detected episodes, 3 decisions; basis: repeated episodes.
- Assets (up to five): AHU1, R403, HP1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-AHU1-filter_dp_pa-2026-01-16T22:30:00Z, METERNOISE-R403-2026-01-18T08:15:00Z, MISSING-HP1-supply_temp_c-2026-01-22T13:00:00Z.
- Candidate change: Improve sensor freshness checks and require quality gating before control decisions.
- Required validation: Inject sensor freezes and missingness; measure false alarms and fail-closed behavior.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-02 | Energy Optimization: rule and workflow review

- Evidence: 18 detected episodes, 18 decisions; basis: repeated episodes.
- Assets (up to five): HP1, PV1, BAT1.
- Months observed: 2026-01.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-05T12:00:00Z, BAT-PLAN-2026-01-06T12:00:00Z, BAT-PLAN-2026-01-07T12:00:00Z.
- Candidate change: Tune tariff/PV-aware proposals while retaining comfort and battery safety constraints.
- Required validation: Replay against a fixed no-optimisation baseline; report cost and comfort with uncertainty.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-03 | Recurrent energy optimization at BAT1

- Evidence: 18 detected episodes, 18 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): HP1, PV1, BAT1.
- Months observed: 2026-01.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-05T12:00:00Z, BAT-PLAN-2026-01-06T12:00:00Z, BAT-PLAN-2026-01-07T12:00:00Z.
- Candidate change: Investigate asset BAT1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for BAT1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-04 | Recurrent energy optimization at HP1

- Evidence: 18 detected episodes, 18 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): HP1, PV1, BAT1.
- Months observed: 2026-01.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-05T12:00:00Z, BAT-PLAN-2026-01-06T12:00:00Z, BAT-PLAN-2026-01-07T12:00:00Z.
- Candidate change: Investigate asset HP1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for HP1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-05 | Recurrent energy optimization at PV1

- Evidence: 18 detected episodes, 18 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): HP1, PV1, BAT1.
- Months observed: 2026-01.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-05T12:00:00Z, BAT-PLAN-2026-01-06T12:00:00Z, BAT-PLAN-2026-01-07T12:00:00Z.
- Candidate change: Investigate asset PV1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for PV1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-06 | Heating Comfort: rule and workflow review

- Evidence: 116 detected episodes, 184 decisions; basis: repeated episodes.
- Assets (up to five): R107, R108, R309, R101, R410.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R410-2026-01-05T00:45:00Z, COLD-R402-2026-01-05T01:45:00Z, COLD-R110-2026-01-06T14:00:00Z.
- Candidate change: Review sustained cold-room escalation and occupied-room comfort thresholds.
- Required validation: Inspect raw temperature trajectories and occupied-room false positives.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-07 | Recurrent heating comfort at R107

- Evidence: 6 detected episodes, 9 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R107.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R107-2026-01-07T14:00:00Z, COLD-R107-2026-01-07T21:15:00Z, COLD-R107-2026-01-09T00:00:00Z.
- Candidate change: Investigate asset R107 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R107 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-08 | Recurrent heating comfort at R108

- Evidence: 6 detected episodes, 10 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R108.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R108-2026-01-07T14:00:00Z, COLD-R108-2026-01-08T05:00:00Z, COLD-R108-2026-01-13T06:30:00Z.
- Candidate change: Investigate asset R108 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R108 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-09 | Recurrent heating comfort at R309

- Evidence: 6 detected episodes, 9 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R309.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R309-2026-01-13T14:00:00Z, COLD-R309-2026-01-14T07:45:00Z, COLD-R309-2026-01-16T03:00:00Z.
- Candidate change: Investigate asset R309 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R309 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-10 | Heating Plant: rule and workflow review

- Evidence: 3 detected episodes, 3 decisions; basis: repeated episodes.
- Assets (up to five): HP1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-07T21:30:00Z, HP1-COP-2026-01-14, HP1-LOCKOUT-2026-01-16T15:15:00Z.
- Candidate change: Review heat-pump degradation escalation and technician availability.
- Required validation: Cross-check plant telemetry, maintenance records, and benign weather-driven changes.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-11 | Recurrent heating plant at HP1

- Evidence: 3 detected episodes, 3 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): HP1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-07T21:30:00Z, HP1-COP-2026-01-14, HP1-LOCKOUT-2026-01-16T15:15:00Z.
- Candidate change: Investigate asset HP1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for HP1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-12 | Logistics: rule and workflow review

- Evidence: 13 detected episodes, 13 decisions; basis: repeated episodes.
- Assets (up to five): VEND1, WASTE_MAIN, WASTE_F3, WASTE_F2, WASTE_F1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_F3-fill_pct-2026-01-06T12:00:00Z, LOG-FORECAST-WASTE_F2-fill_pct-2026-01-07T11:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-07T14:00:00Z.
- Candidate change: Reassess inventory reorder points, delivery lead times, and resource assignment.
- Required validation: Measure stockout lead time and confirmed fulfillment against historical work orders.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-13 | Recurrent logistics at VEND1

- Evidence: 5 detected episodes, 5 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): VEND1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-VEND1-stock_snacks-2026-01-13T21:00:00Z, LOG-FORECAST-VEND1-stock_snacks-2026-01-17T21:00:00Z, LOG-FORECAST-VEND1-stock_snacks-2026-01-20T20:00:00Z.
- Candidate change: Investigate asset VEND1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for VEND1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-14 | Recurrent logistics at WASTE_MAIN

- Evidence: 4 detected episodes, 4 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): WASTE_MAIN.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-07T14:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-14T14:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-22T14:00:00Z.
- Candidate change: Investigate asset WASTE_MAIN before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for WASTE_MAIN and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-15 | Occupancy Surge: rule and workflow review

- Evidence: 96 detected episodes, 96 decisions; basis: repeated episodes.
- Assets (up to five): R409, R401, R310, R309, R306.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-06-R206, SURGE-2026-01-06-R401, SURGE-2026-01-06-R302.
- Candidate change: Adjust cleaning and logistics forecasts for occupancy surges.
- Required validation: Compare predicted versus actual arrivals, staffing load and late turnovers.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-16 | Recurrent occupancy surge at R409

- Evidence: 9 detected episodes, 9 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R409, R401, R310, R306, R304.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-15-R409, SURGE-2026-01-18-R409, SURGE-2026-01-19-R409.
- Candidate change: Investigate asset R409 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R409 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-17 | Recurrent occupancy surge at R310

- Evidence: 8 detected episodes, 8 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R310, R409, R306, R108, R209.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-06-R310, SURGE-2026-01-15-R310, SURGE-2026-01-19-R310.
- Candidate change: Investigate asset R310 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R310 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-18 | Recurrent occupancy surge at R401

- Evidence: 8 detected episodes, 8 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R401, R409, R304, R309, R407.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-06-R401, SURGE-2026-01-15-R401, SURGE-2026-01-19-R401.
- Candidate change: Investigate asset R401 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R401 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-19 | Room Turnaround: rule and workflow review

- Evidence: 66 detected episodes, 154 decisions; basis: repeated episodes.
- Assets (up to five): R308, R305, R209, R109, R407.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R308-2026-01-05, TURN-R201-2026-01-06, TURN-R308-2026-01-06.
- Candidate change: Recalibrate cleaning time estimates and shift-aware room assignment; preserve the release gate.
- Required validation: Compare promised check-in times, observed cleaning completions, and staffing conflicts.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-20 | Recurrent room turnaround at R209

- Evidence: 4 detected episodes, 9 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R209.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R209-2026-01-12, TURN-R209-2026-01-23, TURN-R209-2026-01-24.
- Candidate change: Investigate asset R209 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R209 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-21 | Recurrent room turnaround at R305

- Evidence: 4 detected episodes, 10 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R305.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R305-2026-01-09, TURN-R305-2026-01-10, TURN-R305-2026-01-17.
- Candidate change: Investigate asset R305 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R305 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-22 | Recurrent room turnaround at R308

- Evidence: 4 detected episodes, 10 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R308.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R308-2026-01-05, TURN-R308-2026-01-06, TURN-R308-2026-01-07.
- Candidate change: Investigate asset R308 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R308 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-23 | Ventilation Maintenance: rule and workflow review

- Evidence: 1 detected episodes, 1 decisions; basis: repeated episodes.
- Assets (up to five): AHU1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: FILTER-2026-01-15.
- Candidate change: Review ventilation inspection cadence and filter-change triggers.
- Required validation: Verify against measured pressure drop, work orders, and post-maintenance readings.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-24 | Water Leak: rule and workflow review

- Evidence: 1 detected episodes, 2 decisions; basis: repeated episodes.
- Assets (up to five): R305.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: LEAK-R305-2026-01-20.
- Candidate change: Review overnight flow and meter reconciliation thresholds; isolate missing or unreliable submeters.
- Required validation: Manually label sampled alerts and benign high-use periods; compare precision and missed leaks.
- Status: **hypothesis only; not implemented or independently validated**.


## PLATO improvement candidates

### PLATO-01 | Data Quality: design review candidate

- Evidence: 3 detected episodes, 3 decisions; basis: repeated episodes.
- Assets (up to five): AHU1, R403, HP1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-AHU1-filter_dp_pa-2026-01-16T22:30:00Z, METERNOISE-R403-2026-01-18T08:15:00Z, MISSING-HP1-supply_temp_c-2026-01-22T13:00:00Z.
- Candidate change: Review sensor redundancy and maintainability in future specifications.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-02 | Energy Optimization: design review candidate

- Evidence: 18 detected episodes, 18 decisions; basis: repeated episodes.
- Assets (up to five): HP1, PV1, BAT1.
- Months observed: 2026-01.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-05T12:00:00Z, BAT-PLAN-2026-01-06T12:00:00Z, BAT-PLAN-2026-01-07T12:00:00Z.
- Candidate change: Evaluate future storage/PV sizing only after measured counterfactual benefits.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-03 | Heating Comfort: design review candidate

- Evidence: 116 detected episodes, 184 decisions; basis: repeated episodes.
- Assets (up to five): R107, R108, R309, R101, R410.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R410-2026-01-05T00:45:00Z, COLD-R402-2026-01-05T01:45:00Z, COLD-R110-2026-01-06T14:00:00Z.
- Candidate change: Review zoning, envelope and controllability for repeatedly uncomfortable rooms.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-04 | Heating Plant: design review candidate

- Evidence: 3 detected episodes, 3 decisions; basis: repeated episodes.
- Assets (up to five): HP1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-07T21:30:00Z, HP1-COP-2026-01-14, HP1-LOCKOUT-2026-01-16T15:15:00Z.
- Candidate change: Review service access and instrumentation for repeatedly degraded equipment.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-05 | Logistics: design review candidate

- Evidence: 13 detected episodes, 13 decisions; basis: repeated episodes.
- Assets (up to five): VEND1, WASTE_MAIN, WASTE_F3, WASTE_F2, WASTE_F1.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_F3-fill_pct-2026-01-06T12:00:00Z, LOG-FORECAST-WASTE_F2-fill_pct-2026-01-07T11:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-07T14:00:00Z.
- Candidate change: Review delivery access, storage capacity and robot-compatible paths.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-06 | Occupancy Surge: design review candidate

- Evidence: 96 detected episodes, 96 decisions; basis: repeated episodes.
- Assets (up to five): R409, R401, R310, R309, R306.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-06-R206, SURGE-2026-01-06-R401, SURGE-2026-01-06-R302.
- Candidate change: Review service-capacity assumptions under peak occupancy.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-07 | Room Turnaround: design review candidate

- Evidence: 66 detected episodes, 154 decisions; basis: repeated episodes.
- Assets (up to five): R308, R305, R209, R109, R407.
- Months observed: 2026-01.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R308-2026-01-05, TURN-R201-2026-01-06, TURN-R308-2026-01-06.
- Candidate change: Evaluate housekeeping staging, room access and circulation bottlenecks.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

## Closed-loop evaluation protocol

1. Capture each candidate with its evidence, decision IDs and affected assets.
2. Label a stratified sample of true incidents and benign look-alikes independently.
3. Change one rule or workflow on development data; record the version and expected trade-off.
4. Compare the baseline and candidate on a frozen evaluation split using precision, recall, missed critical incidents, approval load and resource conflicts.
5. Promote only after human safety review and an unchanged holdout evaluation. Do not tune on holdout.

## Target architecture

BMS/PMS/telemetry adapters -> quality-controlled event store -> detectors -> shared scheduler and safety policy -> approval/consent interface -> mock executor -> independent verification -> traceable CLARA rule proposals and PLATO design reviews.

## Limitations

- Simulated actions do not change the historical replay; post-action causality cannot be established.
- No live building, measured cost reduction, confirmed physical incident labels or independently verified design outcomes.
- Multiple candidates can derive from the same episodes; candidate count is not a learning-rate metric.
- Holdout must remain untouched until the final frozen evaluation.
