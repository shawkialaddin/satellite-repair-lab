# Research roadmap

## Completed infrastructure

- [x] Synthetic C parser and four handwritten patch fixtures.
- [x] Development, acceptance, and evaluator suites.
- [x] Acceptance/rejection/deferral policies and recovery checks.
- [x] Structured fixture reports and five passing unit/integration tests.

## Next experiment

- [x] Record two local Qwen models, exact GGUF revisions/checksums, and inference configuration.
- [ ] Verify the model adapter and disposable container evaluator end to end.
- [x] Run generation with network syscall denial and reproduce compilation/validation with network-filtered replay.
- [ ] Separate generator access from acceptance and evaluator files.
- [x] Record all 34 bounded model attempts, including build failures and incorrect outputs.
- [x] Measure a separate host CPU-contention workload (inference excluded).

## Evidence required for the paper

- [ ] Verify related work and define a precise, defensible contribution.
- [ ] Freeze benchmark, acceptance rules, baselines, and analysis before the main run.
- [ ] Add independently curated vulnerabilities and repeated runs.
- [ ] Implement enforced resource budgets and independent acceptance isolation.
- [ ] Select a documented hardware target and measure mission-workload interference.
- [ ] Compare the same generator with simpler acceptance policies using paired candidates.
- [ ] Measure harmful acceptance, repair success, rejection, deferral, and recovery outcomes.
- [ ] Analyze uncertainty and document threats to validity and benchmark leakage.
- [ ] Archive code and experimental records, then prepare a venue-specific manuscript.

The manuscript is maintained separately during preparation. No submission, acceptance, novelty, or flight-readiness claim is made by this roadmap.
