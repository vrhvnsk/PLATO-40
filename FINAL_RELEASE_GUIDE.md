# PLATO-40 integrated autonomy lab release

## One-command reproducible pipeline

```bash
python -m pip install -r requirements.txt
python scripts/final_release.py --data data/quickstart --out-dir reports/final_release --seed 40
python -m pytest -q
```

If the organizers provide independent holdout telemetry, append `--holdout PATH_TO_HOLDOUT`. No holdout is bundled or fabricated.

## Added capabilities

- Multi-step **synthetic** planning with decision, resource, execution, verification and learning stages.
- Counterfactual comparison with explicit, illustrative utility scores and safety exclusions.
- Deterministic synthetic post-action outcomes, never presented as authenticated verification.
- Shared hourly capacity reservations for cleaners, technicians, heat pump and battery; conflicts defer tasks.
- Judge-facing explanations, scored alternatives and plan steps in the guided `/demo` page.
- Conservative learning promotion gate: no candidate promoted without independent evidence.
- Deterministic SHA-256 trace digest and seed-based replay.
- Optional independent holdout pipeline; explicitly reports when absent.
- Eight additional backend regression tests.
- Measured local Python replay throughput in `autonomy_report.json` (environment-dependent).

## Important limitations

This is a **demonstration of synthetic autonomy**, not a production autonomous controller. The utility model is illustrative and not empirically calibrated. The simulated success rate is not a measured improvement over the baseline. Resource capacity is hourly, not a fully time-expanded constraint solver. No live equipment, robot, messaging, approvals or telemetry APIs are connected. No real outcome-based learning or validated policy promotion is claimed. Browser end-to-end tests require a browser testing stack and have not been added. Frontend production build could not be verified in this environment because npm dependency installation timed out. The prebundled 6,290-decision replay is not claimed to be reproduced by the current detector pipeline. A true holdout requires organizer-supplied data.

## Frontend

```bash
cd frontend
npm ci
npm run build
npm run dev
```

The guided `/demo` route now shows alternative action scores, planning steps and synthetic outcomes for the original bundled decisions. It does not claim these are real-world outcomes.

## Additional acceptance coverage

`python scripts/validate_release.py` generates a **temporal, episode-disjoint internal holdout** from bundled decisions, an exact deterministic replay check, trace digest and replay throughput measurement. This is *not* an independent organizer holdout and cannot measure real-world effectiveness. Run `python -m pytest -q` for the extended regression suite.

A GitHub Actions workflow at `.github/workflows/acceptance.yml` runs backend acceptance, frontend production build and Chromium Playwright smoke tests. Browser tests are provided but have **not been run successfully in this environment** because npm dependencies cannot be installed. To run locally after installing dependencies: `cd frontend && npm ci && npm run build && npx playwright install chromium && npx playwright test`.

No authentic post-action telemetry, real actuator acknowledgements, independent holdout data or verified policy improvements were supplied. Therefore real-world closed-loop verification and outcome-based learning remain unvalidated; inventing successful results would be misleading.
