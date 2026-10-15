# Preliminary host study: local generation and separate acceptance

Recorded 16 October 2026 (Riyadh). These exploratory runs are reproducible host evidence, not a flight evaluation or a general repair-reliability estimate.

## Model trials

Each model used three synthetic tasks and seeds 11, 22, and 33, for nine task/seed trials. A trial stopped at its first development-passing candidate or after two generation attempts. Attempt two used seed+1. The historical `seed` field records that actual inference seed; the base trial seed is also encoded in the attempt ID. Development feedback alone was returned to the model. Acceptance and evaluator outcomes were not used to produce retries.

| Model, Q4_K_M | Trials | Attempts | Built/evaluated | Evaluator-valid trials | Distinct raw function outputs |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-Coder 0.5B Instruct | 9 | 18 | 11 | 0 | 4 |
| Qwen2.5-Coder 1.5B Instruct | 9 | 16 | 16 | 2 | 8 |

The 1.5B model repaired the length predicate in one seed trial and the authorization predicate in one seed trial. Neither model repaired the overflow task. Reference implementations passed the complete evaluator sets. The 0.5B experiment was run first; adding 1.5B after its failures was an exploratory choice, not a preregistered comparison. Separate informal prompt diagnostics were not included as benchmark trials.

The tasks share a tiny function-level harness, and all were constructed by the same development process. They are not independently curated real-world defects. Repeated seeds, attempts, and identical outputs must not be counted as independent vulnerabilities. Strong semantic specifications in the prompt further limit generalization.

## Acceptance outcome

B1 accepted zero 0.5B candidates and two 1.5B candidates. B2 accepted exactly the same candidates. All accepted candidates passed the evaluator. B3-light matched B2; B3-busy deferred the same two eligible candidates by its defined policy.

**No benefit from the extra acceptance suite was observed in these model runs.** Erroneous acceptance for 0.5B is undefined because its acceptance denominator is zero. For 1.5B, zero of two accepted candidates failed the evaluator, which provides very little evidence about reliability. No confidence or superiority claim is justified. The original handwritten parser fixtures remain separate controls for showing how a partial fix can pass a weaker gate.

## Host resource observations

| Model | Median inference invocation wall time | Range | Peak inference RSS range |
| --- | ---: | ---: | ---: |
| 0.5B | 3.006 s | 2.095-4.759 s | 609.30-610.93 MiB |
| 1.5B | 6.333 s | 5.340-8.090 s | 1813.20-1815.58 MiB |

Wall time covers worker startup, model loading, and generation; it excludes subsequent compilation and evaluator execution. RSS is per-process `ru_maxrss` on Linux, not address-space allocation or whole-system memory. Two CPU inference threads, 2048-token context, and a 384-output-token limit were used. Whole-system energy was not measured. Exact model hashes and settings are recorded in each protocol.

Inference children denied networking with seccomp. A subsequent replay denied network syscalls in the parent, compiler, and candidate descendants. All 34 saved candidates reproduced their development, acceptance, and evaluator pass/fail outcomes. See the per-model `offline-replay.json` files. Compiler filesystem isolation was not established.

## Separate host workload experiment

A periodic synthetic mission task and an artificial validation task shared one logical CPU. Period: 20 ms. Mission CPU demand: 14 ms for 30 jobs, then 5 ms for 30 jobs. Validation: 20 jobs using 8 ms CPU with 12 ms sleep after each job. B2 started validation immediately. B3 delayed validation until 0.6 s, when the known workload demand dropped. Trial order was shuffled with seed 20261016.

| Policy | Misses in each repeat (60 jobs each) | Validation finished after release |
| --- | --- | --- |
| B0, no validation | 0, 0, 0 | Not applicable |
| B2, immediate validation | 27, 26, 27 | 0.517-0.526 s |
| B3, deferred validation | 0, 0, 0 | 1.007-1.010 s |

These are measured host wall/CPU times, unlike the original deterministic timing surrogate. However, the workload is artificial, deferral uses known phase timing, and the test excludes inference and actual patch-validation execution. The result demonstrates a contention/latency trade-off in this setup. It does not demonstrate a new scheduler, real mission protection, or end-to-end improvement.

## Controls and remaining evidence

Nine automated tests pass locally, including blocked network/file-open/process-creation probes, runaway termination, disjoint case sets, reference controls, and original recovery checks. The tests do not prove kernel confinement, patch correctness, or mission safety.

A full empirical study still requires flight-software or independently sourced application defects, a stronger baseline, a protected supervisor with a hardened build environment, integrated generation/validation/mission measurements, and a documented target-device budget. The current study is best framed as preliminary feasibility and limitations evidence.
