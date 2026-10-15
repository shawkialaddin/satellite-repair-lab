# Fixture infrastructure pilot

No model was used. These are not AI repair results.

| Baseline | Load | Accepted | Harmful accepted | Deferred | Synthetic deadline misses |
| --- | --- | --- | --- | --- | --- |
| B1 | light | 2 | 1 | 0 | 0 |
| B1 | busy | 2 | 1 | 0 | 20 |
| B2 | light | 1 | 0 | 0 | 0 |
| B2 | busy | 1 | 0 | 0 | 20 |
| B3 | light | 1 | 0 | 0 | 0 |
| B3 | busy | 0 | 0 | 1 | 0 |

Timing differences follow the explicit surrogate policy and are not evidence of a scheduling innovation.
Full provenance, host timings, recovery outcomes, and limitations are in pilot.json.
