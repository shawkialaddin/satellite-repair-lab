# Reproducibility

## Fixture pilot

From the repository root:

```bash
python3 --version
cc --version
python3 -m unittest discover -s tests -v
python3 lab.py --output /tmp/satellite-repair-pilot
```

The expected structural output is four handwritten candidates, 24 policy/load combinations, no model, three recovery scenarios, and a digest-mismatch rejection. Build times, validation times, and executable hashes may vary with the host and toolchain. The five tests verify current pipeline behavior; they do not assess AI repair performance.

Committed `results/pilot.*` are example host-generated fixture records. Running `lab.py` without `--output` replaces those files. Preserve each research run in a separate directory rather than overwriting prior evidence.

## Before recording a model experiment

Record repository commit, OS, architecture, CPU, RAM, compiler and Python versions, container image digest, and execution limits. Record model identity/revision, weight checksums, quantization, inference backend/version, context budget, seed, prompt, raw response, source/artifact hashes, and attempt duration. The current adapter records only a subset; additional logging must be implemented before the main study.

Verify network isolation independently of the inference CLI. Pre-provision all tools and weights. Prevent generator access to protected tests and evaluator feedback. Public repository tests cannot be assumed uncontaminated, so use independently prepared evaluation cases for strong held-out claims.

Freeze the protocol and report every attempted repair. Compare acceptance policies on identical generated candidates. Keep independent evaluator labels separate from acceptance decisions. Measure real memory, compute, and workload deadlines before making resource-bounded or spacecraft-performance claims. Energy must be measured or explicitly marked unmeasured.

The Docker base image and installed packages are currently unpinned, so the container definition is a development aid rather than an immutable experimental environment.
