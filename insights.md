# PLATO-40 | Evidence-backed learning loop

> Synthetic replay only. Recommendations are testable hypotheses, not demonstrated learning gains, causal outcomes, measured savings, or verified physical defects.
> Episode counts reflect prototype detections, not independently labelled ground truth.

## Evidence summary

- Decisions: 6219
- Distinct detected episodes: 4288
- Traceable improvement candidates: 35
- Method: group decisions by episode and issue class, identify recurring assets, and require at least three distinct episodes for asset-specific and design-review candidates.

| Issue class | Decisions |
|---|---:|
| data_quality | 12 |
| energy_optimization | 303 |
| heating_comfort | 1678 |
| heating_plant | 10 |
| logistics | 277 |
| occupancy_surge | 1744 |
| room_turnaround | 2188 |
| ventilation_maintenance | 2 |
| water_leak | 5 |

## CLARA improvement candidates

### CLARA-01 | Data Quality: rule and workflow review

- Evidence: 12 detected episodes, 12 decisions; basis: repeated episodes.
- Assets (up to five): AHU1, HP1, R407, R110.
- Months observed: 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-HP1-heat_output_kw-2026-02-24T20:45:00Z, MISSING-AHU1-airflow_m3h-2026-03-28T03:15:00Z, MISSING-HP1-heat_output_kw-2026-03-31T06:15:00Z.
- Candidate change: Improve sensor freshness checks and require quality gating before control decisions.
- Required validation: Inject sensor freezes and missingness; measure false alarms and fail-closed behavior.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-02 | Recurrent data quality at AHU1

- Evidence: 6 detected episodes, 6 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): AHU1.
- Months observed: 2026-03, 2026-04, 2026-05, 2026-07, 2026-10, 2026-11.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-AHU1-airflow_m3h-2026-03-28T03:15:00Z, MISSING-AHU1-filter_dp_pa-2026-04-23T07:30:00Z, MISSING-AHU1-airflow_m3h-2026-05-13T06:00:00Z.
- Candidate change: Investigate asset AHU1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for AHU1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-03 | Recurrent data quality at HP1

- Evidence: 4 detected episodes, 4 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): HP1.
- Months observed: 2026-02, 2026-03, 2026-06, 2026-07.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-HP1-heat_output_kw-2026-02-24T20:45:00Z, MISSING-HP1-heat_output_kw-2026-03-31T06:15:00Z, MISSING-HP1-supply_temp_c-2026-06-10T07:00:00Z.
- Candidate change: Investigate asset HP1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for HP1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-04 | Energy Optimization: rule and workflow review

- Evidence: 303 detected episodes, 303 decisions; basis: repeated episodes.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Tune tariff/PV-aware proposals while retaining comfort and battery safety constraints.
- Required validation: Replay against a fixed no-optimisation baseline; report cost and comfort with uncertainty.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-05 | Recurrent energy optimization at BAT1

- Evidence: 303 detected episodes, 303 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Investigate asset BAT1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for BAT1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-06 | Recurrent energy optimization at HP1

- Evidence: 303 detected episodes, 303 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Investigate asset HP1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for HP1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-07 | Recurrent energy optimization at PV1

- Evidence: 303 detected episodes, 303 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Investigate asset PV1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for PV1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-08 | Heating Comfort: rule and workflow review

- Evidence: 1028 detected episodes, 1678 decisions; basis: repeated episodes.
- Assets (up to five): R107, R108, R106, R110, R102.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R304-2026-01-01T01:15:00Z, COLD-R108-2026-01-01T01:15:00Z, COLD-R408-2026-01-02T08:45:00Z.
- Candidate change: Review sustained cold-room escalation and occupied-room comfort thresholds.
- Required validation: Inspect raw temperature trajectories and occupied-room false positives.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-09 | Recurrent heating comfort at R107

- Evidence: 61 detected episodes, 101 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R107.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R107-2026-01-05T14:00:00Z, COLD-R107-2026-01-19T14:00:00Z, COLD-R107-2026-01-20T08:15:00Z.
- Candidate change: Investigate asset R107 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R107 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-10 | Recurrent heating comfort at R108

- Evidence: 52 detected episodes, 89 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R108.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R108-2026-01-01T01:15:00Z, COLD-R108-2026-01-04T07:15:00Z, COLD-R108-2026-01-08T07:15:00Z.
- Candidate change: Investigate asset R108 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R108 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-11 | Recurrent heating comfort at R106

- Evidence: 47 detected episodes, 73 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R106.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R106-2026-01-05T14:00:00Z, COLD-R106-2026-01-06T07:00:00Z, COLD-R106-2026-01-16T14:00:00Z.
- Candidate change: Investigate asset R106 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R106 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-12 | Heating Plant: rule and workflow review

- Evidence: 10 detected episodes, 10 decisions; basis: repeated episodes.
- Assets (up to five): HP1.
- Months observed: 2026-01, 2026-02, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-26T12:00:00Z, HP1-COP-2026-01-26, HP1-LOCKOUT-2026-02-15T21:00:00Z.
- Candidate change: Review heat-pump degradation escalation and technician availability.
- Required validation: Cross-check plant telemetry, maintenance records, and benign weather-driven changes.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-13 | Recurrent heating plant at HP1

- Evidence: 10 detected episodes, 10 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): HP1.
- Months observed: 2026-01, 2026-02, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-26T12:00:00Z, HP1-COP-2026-01-26, HP1-LOCKOUT-2026-02-15T21:00:00Z.
- Candidate change: Investigate asset HP1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for HP1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-14 | Logistics: rule and workflow review

- Evidence: 277 detected episodes, 277 decisions; basis: repeated episodes.
- Assets (up to five): VEND1, WASTE_MAIN, WASTE_F1, WASTE_F2, WASTE_F3.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-VEND1-stock_snacks-2026-01-01T22:00:00Z, LOG-FORECAST-WASTE_F2-fill_pct-2026-01-02T12:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-02T14:00:00Z.
- Candidate change: Reassess inventory reorder points, delivery lead times, and resource assignment.
- Required validation: Measure stockout lead time and confirmed fulfillment against historical work orders.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-15 | Recurrent logistics at VEND1

- Evidence: 148 detected episodes, 148 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): VEND1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-VEND1-stock_snacks-2026-01-01T22:00:00Z, LOG-FORECAST-VEND1-stock_snacks-2026-01-06T22:00:00Z, LOG-FORECAST-VEND1-stock_snacks-2026-01-17T20:00:00Z.
- Candidate change: Investigate asset VEND1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for VEND1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-16 | Recurrent logistics at WASTE_MAIN

- Evidence: 75 detected episodes, 75 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): WASTE_MAIN.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-02T14:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-19T14:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-29T14:00:00Z.
- Candidate change: Investigate asset WASTE_MAIN before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for WASTE_MAIN and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-17 | Recurrent logistics at WASTE_F1

- Evidence: 16 detected episodes, 16 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): WASTE_F1.
- Months observed: 2026-01, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_F1-fill_pct-2026-01-20T10:00:00Z, LOG-FORECAST-WASTE_F1-fill_pct-2026-04-03T10:00:00Z, LOG-FORECAST-WASTE_F1-fill_pct-2026-04-11T11:00:00Z.
- Candidate change: Investigate asset WASTE_F1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for WASTE_F1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-18 | Occupancy Surge: rule and workflow review

- Evidence: 1744 detected episodes, 1744 decisions; basis: repeated episodes.
- Assets (up to five): R407, R403, R101, R408, R207.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12, 2027-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-02-R104, SURGE-2026-01-02-R201, SURGE-2026-01-02-R206.
- Candidate change: Adjust cleaning and logistics forecasts for occupancy surges.
- Required validation: Compare predicted versus actual arrivals, staffing load and late turnovers.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-19 | Recurrent occupancy surge at R407

- Evidence: 60 detected episodes, 60 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R407, R408, R405, R308, R410.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12, 2027-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-02-R407, SURGE-2026-01-16-R407, SURGE-2026-01-18-R407.
- Candidate change: Investigate asset R407 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R407 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-20 | Recurrent occupancy surge at R403

- Evidence: 58 detected episodes, 58 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R403, R401, R309, R109, R201.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-31-R403, SURGE-2026-02-07-R403, SURGE-2026-02-23-R403.
- Candidate change: Investigate asset R403 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R403 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-21 | Recurrent occupancy surge at R101

- Evidence: 56 detected episodes, 56 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R101, R309, R109, R402, R306.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-12-R101, SURGE-2026-01-19-R101, SURGE-2026-01-20-R101.
- Candidate change: Investigate asset R101 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R101 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-22 | Room Turnaround: rule and workflow review

- Evidence: 909 detected episodes, 2188 decisions; basis: repeated episodes.
- Assets (up to five): R309, R106, R110, R209, R408.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R101-2026-01-02, TURN-R303-2026-01-02, TURN-R303-2026-01-03.
- Candidate change: Recalibrate cleaning time estimates and shift-aware room assignment; preserve the release gate.
- Required validation: Compare promised check-in times, observed cleaning completions, and staffing conflicts.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-23 | Recurrent room turnaround at R309

- Evidence: 34 detected episodes, 81 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R309.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R309-2026-01-09, TURN-R309-2026-01-10, TURN-R309-2026-01-28.
- Candidate change: Investigate asset R309 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R309 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-24 | Recurrent room turnaround at R106

- Evidence: 31 detected episodes, 75 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R106.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R106-2026-01-19, TURN-R106-2026-01-29, TURN-R106-2026-02-09.
- Candidate change: Investigate asset R106 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R106 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-25 | Recurrent room turnaround at R110

- Evidence: 29 detected episodes, 69 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R110.
- Months observed: 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R110-2026-03-23, TURN-R110-2026-03-26, TURN-R110-2026-03-27.
- Candidate change: Investigate asset R110 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R110 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-26 | Ventilation Maintenance: rule and workflow review

- Evidence: 2 detected episodes, 2 decisions; basis: repeated episodes.
- Assets (up to five): AHU1.
- Months observed: 2026-07, 2026-10.
- Median decision confidence: 0.7.
- Example episode IDs: FILTER-2026-07-26, FILTER-2026-10-09.
- Candidate change: Review ventilation inspection cadence and filter-change triggers.
- Required validation: Verify against measured pressure drop, work orders, and post-maintenance readings.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-27 | Water Leak: rule and workflow review

- Evidence: 3 detected episodes, 5 decisions; basis: repeated episodes.
- Assets (up to five): R107, WM_MAIN, R209.
- Months observed: 2026-06, 2026-07, 2026-10.
- Median decision confidence: 0.7.
- Example episode IDs: LEAK-R107-2026-06-16, MAINLEAK-2026-07-13T02:15:00Z, LEAK-R209-2026-10-30.
- Candidate change: Review overnight flow and meter reconciliation thresholds; isolate missing or unreliable submeters.
- Required validation: Manually label sampled alerts and benign high-use periods; compare precision and missed leaks.
- Status: **hypothesis only; not implemented or independently validated**.


## PLATO improvement candidates

### PLATO-01 | Data Quality: design review candidate

- Evidence: 12 detected episodes, 12 decisions; basis: repeated episodes.
- Assets (up to five): AHU1, HP1, R407, R110.
- Months observed: 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-HP1-heat_output_kw-2026-02-24T20:45:00Z, MISSING-AHU1-airflow_m3h-2026-03-28T03:15:00Z, MISSING-HP1-heat_output_kw-2026-03-31T06:15:00Z.
- Candidate change: Review sensor redundancy and maintainability in future specifications.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-02 | Energy Optimization: design review candidate

- Evidence: 303 detected episodes, 303 decisions; basis: repeated episodes.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Evaluate future storage/PV sizing only after measured counterfactual benefits.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-03 | Heating Comfort: design review candidate

- Evidence: 1028 detected episodes, 1678 decisions; basis: repeated episodes.
- Assets (up to five): R107, R108, R106, R110, R102.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R304-2026-01-01T01:15:00Z, COLD-R108-2026-01-01T01:15:00Z, COLD-R408-2026-01-02T08:45:00Z.
- Candidate change: Review zoning, envelope and controllability for repeatedly uncomfortable rooms.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-04 | Heating Plant: design review candidate

- Evidence: 10 detected episodes, 10 decisions; basis: repeated episodes.
- Assets (up to five): HP1.
- Months observed: 2026-01, 2026-02, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-26T12:00:00Z, HP1-COP-2026-01-26, HP1-LOCKOUT-2026-02-15T21:00:00Z.
- Candidate change: Review service access and instrumentation for repeatedly degraded equipment.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-05 | Logistics: design review candidate

- Evidence: 277 detected episodes, 277 decisions; basis: repeated episodes.
- Assets (up to five): VEND1, WASTE_MAIN, WASTE_F1, WASTE_F2, WASTE_F3.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-VEND1-stock_snacks-2026-01-01T22:00:00Z, LOG-FORECAST-WASTE_F2-fill_pct-2026-01-02T12:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-02T14:00:00Z.
- Candidate change: Review delivery access, storage capacity and robot-compatible paths.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-06 | Occupancy Surge: design review candidate

- Evidence: 1744 detected episodes, 1744 decisions; basis: repeated episodes.
- Assets (up to five): R407, R403, R101, R408, R207.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12, 2027-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-02-R104, SURGE-2026-01-02-R201, SURGE-2026-01-02-R206.
- Candidate change: Review service-capacity assumptions under peak occupancy.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-07 | Room Turnaround: design review candidate

- Evidence: 909 detected episodes, 2188 decisions; basis: repeated episodes.
- Assets (up to five): R309, R106, R110, R209, R408.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R101-2026-01-02, TURN-R303-2026-01-02, TURN-R303-2026-01-03.
- Candidate change: Evaluate housekeeping staging, room access and circulation bottlenecks.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-08 | Water Leak: design review candidate

- Evidence: 3 detected episodes, 5 decisions; basis: repeated episodes.
- Assets (up to five): R107, WM_MAIN, R209.
- Months observed: 2026-06, 2026-07, 2026-10.
- Median decision confidence: 0.7.
- Example episode IDs: LEAK-R107-2026-06-16, MAINLEAK-2026-07-13T02:15:00Z, LEAK-R209-2026-10-30.
- Candidate change: Evaluate branch-level metering and service access where independently confirmed gaps recur.
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
