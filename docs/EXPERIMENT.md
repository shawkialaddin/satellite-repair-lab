# Experiment details

## Experiment design

Synthetic application arguments: declared payload length, opcode, then payload bytes. Valid length is 0..32 and must equal actual count; opcode is 0..3; bytes are unsigned decimal 0..255. There is no CCSDS protocol implementation. The vulnerable fixture deliberately omits logical validation without intentionally causing out-of-bounds host reads.

- B0: no-repair timing reference.
- B1: development-test-only acceptance.
- B2: protected acceptance suite plus development tests.
- B3: B2 plus deferral under a synthetic busy mission state.

Four handcrafted candidates: original, incomplete length fix, complete reference fix, reject-everything regression. Separate development, acceptance, and evaluator input sets support the test pipeline. All are public and are not genuinely secret from a model with repository access. The real study must isolate evaluator files and freeze policy/cases before generation.

B3 avoids synthetic timing misses by definition of the surrogate policy. That is a plumbing check, not a discovered scheduling benefit. Resource termination is unit-tested, not implemented as complete process-tree budget enforcement. This Python host pilot is not the protected production supervisor described in the paper.

## Generate a real candidate

Provision a local model CLI and weights first. The CLI must accept a prompt on stdin and return only C source on stdout. This adapter makes no network request itself but does not constrain what the CLI can do. Disable networking independently and record the environment for a genuine offline claim.

```bash
python3 generate_candidate.py --command-json '["/absolute/path/to/local-inference-cli"]' --output generated/patch.c
```

This performs one generation attempt; it is not an iterative autonomous repair loop. It does not execute the candidate. Record model revision, weight checksum, quantization, seed, prompt and generation cost. Never commit private credentials or model weights accidentally.

## Evaluate generated C in a disposable container

Requires Docker. Build the image while online, then execute with networking disabled. Do not mount secrets, the Docker socket, or writable project source. Container isolation is an experimental boundary, not a formal security guarantee. Image digest and toolchain versions must be pinned for the main study.

```bash
docker build -t satellite-repair-evaluator .
mkdir -p generated evaluation-output
chmod 777 evaluation-output
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 256m --cpus 1 --tmpfs /tmp:rw,exec,nosuid,size=64m -v "$PWD/generated:/candidate:ro" -v "$PWD/evaluation-output:/output:rw" satellite-repair-evaluator
```

The evaluation image contains test suites; the generation environment must not receive its filesystem or evaluator feedback. Restrict output directory permissions again after the run as appropriate. Compilation/process failures are recorded as failures. The disposable container should be destroyed after evaluation. This path is unverified here because Docker is unavailable.

## Recovery scope

Activation tests operate on disposable executable files. A staged binary is verified by digest and replaces the active file; interruption preserves the original; injected health failure restores it. No live spacecraft process or persistent state migration is implemented. The original may remain vulnerable after rollback, so availability recovery does not mean security restoration.

## Next evidence gates

1. Run and log the local model path with genuine network isolation.
2. Implement bounded iterative repair without revealing protected/evaluator tests.
3. Integrate process isolation and measured resource enforcement.
4. Replace synthetic timing with measured periodic workloads on a documented target.
5. Expand to independently curated defects and repeated model runs.
6. Select venue, freeze protocol, analyze results, and revise manuscript claims.

