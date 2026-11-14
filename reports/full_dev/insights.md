# PLATO-40 | Evidence-backed learning loop

> Synthetic replay only. Recommendations are testable hypotheses, not demonstrated learning gains, causal outcomes, measured savings, or verified physical defects.
> Episode counts reflect prototype detections, not independently labelled ground truth.

## Evidence summary

- Decisions: 6290
- Distinct detected episodes: 4250
- Traceable improvement candidates: 35
- Method: group decisions by episode and issue class, identify recurring assets, and require at least three distinct episodes for asset-specific and design-review candidates.

| Issue class | Decisions |
|---|---:|
| data_quality | 12 |
| energy_optimization | 306 |
| heating_comfort | 1824 |
| heating_plant | 5 |
| logistics | 274 |
| occupancy_surge | 1656 |
| room_turnaround | 2206 |
| ventilation_maintenance | 2 |
| water_leak | 5 |

## CLARA improvement candidates

### CLARA-01 | Data Quality: rule and workflow review

- Evidence: 12 detected episodes, 12 decisions; basis: repeated episodes.
- Assets (up to five): AHU1, HP1, R105, R405.
- Months observed: 2026-02, 2026-03, 2026-07, 2026-08, 2026-10, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-AHU1-filter_dp_pa-2026-02-02T16:00:00Z, MISSING-AHU1-airflow_m3h-2026-03-02T00:30:00Z, MISSING-HP1-supply_temp_c-2026-03-24T15:00:00Z.
- Candidate change: Improve sensor freshness checks and require quality gating before control decisions.
- Required validation: Inject sensor freezes and missingness; measure false alarms and fail-closed behavior.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-02 | Recurrent data quality at AHU1

- Evidence: 7 detected episodes, 7 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): AHU1.
- Months observed: 2026-02, 2026-03, 2026-07, 2026-08, 2026-10.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-AHU1-filter_dp_pa-2026-02-02T16:00:00Z, MISSING-AHU1-airflow_m3h-2026-03-02T00:30:00Z, MISSING-AHU1-filter_dp_pa-2026-07-21T06:15:00Z.
- Candidate change: Investigate asset AHU1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for AHU1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-03 | Recurrent data quality at HP1

- Evidence: 3 detected episodes, 3 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): HP1.
- Months observed: 2026-03, 2026-07, 2026-10.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-HP1-supply_temp_c-2026-03-24T15:00:00Z, MISSING-HP1-heat_output_kw-2026-07-10T12:00:00Z, MISSING-HP1-supply_temp_c-2026-10-05T10:00:00Z.
- Candidate change: Investigate asset HP1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for HP1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-04 | Energy Optimization: rule and workflow review

- Evidence: 306 detected episodes, 306 decisions; basis: repeated episodes.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Tune tariff/PV-aware proposals while retaining comfort and battery safety constraints.
- Required validation: Replay against a fixed no-optimisation baseline; report cost and comfort with uncertainty.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-05 | Recurrent energy optimization at BAT1

- Evidence: 306 detected episodes, 306 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Investigate asset BAT1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for BAT1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-06 | Recurrent energy optimization at HP1

- Evidence: 306 detected episodes, 306 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Investigate asset HP1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for HP1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-07 | Recurrent energy optimization at PV1

- Evidence: 306 detected episodes, 306 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Investigate asset PV1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for PV1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-08 | Heating Comfort: rule and workflow review

- Evidence: 1140 detected episodes, 1824 decisions; basis: repeated episodes.
- Assets (up to five): R106, R107, R109, R105, R110.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R310-2026-01-01T00:00:00Z, COLD-R102-2026-01-01T00:00:00Z, COLD-R107-2026-01-01T00:00:00Z.
- Candidate change: Review sustained cold-room escalation and occupied-room comfort thresholds.
- Required validation: Inspect raw temperature trajectories and occupied-room false positives.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-09 | Recurrent heating comfort at R106

- Evidence: 55 detected episodes, 90 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R106.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R106-2026-01-05T14:00:00Z, COLD-R106-2026-01-12T08:15:00Z, COLD-R106-2026-01-15T07:15:00Z.
- Candidate change: Investigate asset R106 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R106 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-10 | Recurrent heating comfort at R107

- Evidence: 54 detected episodes, 88 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R107.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R107-2026-01-01T00:00:00Z, COLD-R107-2026-01-02T08:45:00Z, COLD-R107-2026-01-10T14:00:00Z.
- Candidate change: Investigate asset R107 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R107 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-11 | Recurrent heating comfort at R109

- Evidence: 51 detected episodes, 78 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R109.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R109-2026-01-06T14:00:00Z, COLD-R109-2026-01-09T08:30:00Z, COLD-R109-2026-01-12T14:00:00Z.
- Candidate change: Investigate asset R109 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R109 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-12 | Heating Plant: rule and workflow review

- Evidence: 5 detected episodes, 5 decisions; basis: repeated episodes.
- Assets (up to five): HP1.
- Months observed: 2026-01, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-25T06:30:00Z, HP1-LOCKOUT-2026-11-23T02:45:00Z, HP1-LOCKOUT-2026-12-06T07:45:00Z.
- Candidate change: Review heat-pump degradation escalation and technician availability.
- Required validation: Cross-check plant telemetry, maintenance records, and benign weather-driven changes.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-13 | Recurrent heating plant at HP1

- Evidence: 5 detected episodes, 5 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): HP1.
- Months observed: 2026-01, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-25T06:30:00Z, HP1-LOCKOUT-2026-11-23T02:45:00Z, HP1-LOCKOUT-2026-12-06T07:45:00Z.
- Candidate change: Investigate asset HP1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for HP1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-14 | Logistics: rule and workflow review

- Evidence: 274 detected episodes, 274 decisions; basis: repeated episodes.
- Assets (up to five): VEND1, WASTE_MAIN, WASTE_F1, WASTE_F2, WASTE_F3.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_F2-fill_pct-2026-01-02T13:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-03T14:00:00Z, LOG-FORECAST-VEND1-stock_snacks-2026-01-04T22:00:00Z.
- Candidate change: Reassess inventory reorder points, delivery lead times, and resource assignment.
- Required validation: Measure stockout lead time and confirmed fulfillment against historical work orders.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-15 | Recurrent logistics at VEND1

- Evidence: 156 detected episodes, 156 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): VEND1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-VEND1-stock_snacks-2026-01-04T22:00:00Z, LOG-FORECAST-VEND1-stock_snacks-2026-01-10T22:00:00Z, LOG-FORECAST-VEND1-stock_snacks-2026-01-16T21:00:00Z.
- Candidate change: Investigate asset VEND1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for VEND1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-16 | Recurrent logistics at WASTE_MAIN

- Evidence: 66 detected episodes, 66 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): WASTE_MAIN.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-03T14:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-09T14:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-18T14:00:00Z.
- Candidate change: Investigate asset WASTE_MAIN before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for WASTE_MAIN and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-17 | Recurrent logistics at WASTE_F1

- Evidence: 16 detected episodes, 16 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): WASTE_F1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-09, 2026-10.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_F1-fill_pct-2026-01-09T11:00:00Z, LOG-FORECAST-WASTE_F1-fill_pct-2026-01-18T11:00:00Z, LOG-FORECAST-WASTE_F1-fill_pct-2026-02-18T13:00:00Z.
- Candidate change: Investigate asset WASTE_F1 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for WASTE_F1 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-18 | Occupancy Surge: rule and workflow review

- Evidence: 1656 detected episodes, 1656 decisions; basis: repeated episodes.
- Assets (up to five): R409, R404, R408, R304, R407.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12, 2027-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-02, SURGE-2026-01-02-R104, SURGE-2026-01-02-R201.
- Candidate change: Adjust cleaning and logistics forecasts for occupancy surges.
- Required validation: Compare predicted versus actual arrivals, staffing load and late turnovers.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-19 | Recurrent occupancy surge at R409

- Evidence: 61 detected episodes, 61 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R409, R407, R406, R306, R408.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-02, SURGE-2026-01-02-R409, SURGE-2026-01-16-R409.
- Candidate change: Investigate asset R409 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R409 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-20 | Recurrent occupancy surge at R404

- Evidence: 57 detected episodes, 57 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R404, R304, R409, R306, R401.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-14-R404, SURGE-2026-02-04-R404, SURGE-2026-02-05-R404.
- Candidate change: Investigate asset R404 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R404 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-21 | Recurrent occupancy surge at R408

- Evidence: 53 detected episodes, 53 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R408, R409, R406, R407, R309.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-26-R408, SURGE-2026-02-04-R408, SURGE-2026-02-25-R408.
- Candidate change: Investigate asset R408 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R408 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-22 | Room Turnaround: rule and workflow review

- Evidence: 852 detected episodes, 2206 decisions; basis: repeated episodes.
- Assets (up to five): R102, R208, R204, R402, R103.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R202-2026-01-02, TURN-R405-2026-01-04, TURN-R103-2026-01-05.
- Candidate change: Recalibrate cleaning time estimates and shift-aware room assignment; preserve the release gate.
- Required validation: Compare promised check-in times, observed cleaning completions, and staffing conflicts.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-23 | Recurrent room turnaround at R102

- Evidence: 30 detected episodes, 76 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R102.
- Months observed: 2026-01, 2026-03, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R102-2026-01-10, TURN-R102-2026-01-12, TURN-R102-2026-03-07.
- Candidate change: Investigate asset R102 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R102 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-24 | Recurrent room turnaround at R204

- Evidence: 29 detected episodes, 77 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R204.
- Months observed: 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R204-2026-02-02, TURN-R204-2026-02-06, TURN-R204-2026-02-24.
- Candidate change: Investigate asset R204 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R204 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-25 | Recurrent room turnaround at R208

- Evidence: 29 detected episodes, 71 decisions; basis: at least three distinct detected episodes at the same asset.
- Assets (up to five): R208.
- Months observed: 2026-01, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R208-2026-01-19, TURN-R208-2026-01-25, TURN-R208-2026-03-04.
- Candidate change: Investigate asset R208 before changing global thresholds; consider a targeted inspection or calibration.
- Required validation: Confirm independent occurrences for R208 and compare with peer assets and maintenance history.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-26 | Ventilation Maintenance: rule and workflow review

- Evidence: 2 detected episodes, 2 decisions; basis: repeated episodes.
- Assets (up to five): AHU1.
- Months observed: 2026-07, 2026-10.
- Median decision confidence: 0.7.
- Example episode IDs: FILTER-2026-07-19, FILTER-2026-10-16.
- Candidate change: Review ventilation inspection cadence and filter-change triggers.
- Required validation: Verify against measured pressure drop, work orders, and post-maintenance readings.
- Status: **hypothesis only; not implemented or independently validated**.

### CLARA-27 | Water Leak: rule and workflow review

- Evidence: 3 detected episodes, 5 decisions; basis: repeated episodes.
- Assets (up to five): R403, WM_MAIN, R208.
- Months observed: 2026-06, 2026-07, 2026-11.
- Median decision confidence: 0.7.
- Example episode IDs: LEAK-R403-2026-06-21, MAINLEAK-2026-07-11T00:00:00Z, LEAK-R208-2026-11-11.
- Candidate change: Review overnight flow and meter reconciliation thresholds; isolate missing or unreliable submeters.
- Required validation: Manually label sampled alerts and benign high-use periods; compare precision and missed leaks.
- Status: **hypothesis only; not implemented or independently validated**.


## PLATO improvement candidates

### PLATO-01 | Data Quality: design review candidate

- Evidence: 12 detected episodes, 12 decisions; basis: repeated episodes.
- Assets (up to five): AHU1, HP1, R105, R405.
- Months observed: 2026-02, 2026-03, 2026-07, 2026-08, 2026-10, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: MISSING-AHU1-filter_dp_pa-2026-02-02T16:00:00Z, MISSING-AHU1-airflow_m3h-2026-03-02T00:30:00Z, MISSING-HP1-supply_temp_c-2026-03-24T15:00:00Z.
- Candidate change: Review sensor redundancy and maintainability in future specifications.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-02 | Energy Optimization: design review candidate

- Evidence: 306 detected episodes, 306 decisions; basis: repeated episodes.
- Assets (up to five): BAT1, PV1, HP1.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.55.
- Example episode IDs: BAT-PLAN-2026-01-01T12:00:00Z, BAT-PLAN-2026-01-02T12:00:00Z, BAT-PLAN-2026-01-03T12:00:00Z.
- Candidate change: Evaluate future storage/PV sizing only after measured counterfactual benefits.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-03 | Heating Comfort: design review candidate

- Evidence: 1140 detected episodes, 1824 decisions; basis: repeated episodes.
- Assets (up to five): R106, R107, R109, R105, R110.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: COLD-R310-2026-01-01T00:00:00Z, COLD-R102-2026-01-01T00:00:00Z, COLD-R107-2026-01-01T00:00:00Z.
- Candidate change: Review zoning, envelope and controllability for repeatedly uncomfortable rooms.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-04 | Heating Plant: design review candidate

- Evidence: 5 detected episodes, 5 decisions; basis: repeated episodes.
- Assets (up to five): HP1.
- Months observed: 2026-01, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: HP1-LOCKOUT-2026-01-25T06:30:00Z, HP1-LOCKOUT-2026-11-23T02:45:00Z, HP1-LOCKOUT-2026-12-06T07:45:00Z.
- Candidate change: Review service access and instrumentation for repeatedly degraded equipment.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-05 | Logistics: design review candidate

- Evidence: 274 detected episodes, 274 decisions; basis: repeated episodes.
- Assets (up to five): VEND1, WASTE_MAIN, WASTE_F1, WASTE_F2, WASTE_F3.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: LOG-FORECAST-WASTE_F2-fill_pct-2026-01-02T13:00:00Z, LOG-FORECAST-WASTE_MAIN-fill_pct-2026-01-03T14:00:00Z, LOG-FORECAST-VEND1-stock_snacks-2026-01-04T22:00:00Z.
- Candidate change: Review delivery access, storage capacity and robot-compatible paths.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-06 | Occupancy Surge: design review candidate

- Evidence: 1656 detected episodes, 1656 decisions; basis: repeated episodes.
- Assets (up to five): R409, R404, R408, R304, R407.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12, 2027-01.
- Median decision confidence: 0.7.
- Example episode IDs: SURGE-2026-01-02, SURGE-2026-01-02-R104, SURGE-2026-01-02-R201.
- Candidate change: Review service-capacity assumptions under peak occupancy.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-07 | Room Turnaround: design review candidate

- Evidence: 852 detected episodes, 2206 decisions; basis: repeated episodes.
- Assets (up to five): R102, R208, R204, R402, R103.
- Months observed: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09, 2026-10, 2026-11, 2026-12.
- Median decision confidence: 0.7.
- Example episode IDs: TURN-R202-2026-01-02, TURN-R405-2026-01-04, TURN-R103-2026-01-05.
- Candidate change: Evaluate housekeeping staging, room access and circulation bottlenecks.
- Required validation: Require site validation, lifecycle-cost comparison, and engineering sign-off before design changes.
- Status: **hypothesis only; not implemented or independently validated**.

### PLATO-08 | Water Leak: design review candidate

- Evidence: 3 detected episodes, 5 decisions; basis: repeated episodes.
- Assets (up to five): R403, WM_MAIN, R208.
- Months observed: 2026-06, 2026-07, 2026-11.
- Median decision confidence: 0.7.
- Example episode IDs: LEAK-R403-2026-06-21, MAINLEAK-2026-07-11T00:00:00Z, LEAK-R208-2026-11-11.
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
