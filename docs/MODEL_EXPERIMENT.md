# Local model experiment

The `experiments/` directory adds a separate synthetic-predicate benchmark. It does not replace or reinterpret the original four parser fixtures.

Three tasks cover a length/opcode predicate, overflow-safe capacity checking, and permission-bitmask/authorization validation. All receive unsigned 32-bit arguments through a trusted C harness. Reference implementations are handwritten controls, not model repairs. Evaluator case counts are 116, 398, and 186 respectively; inputs are disjoint from development and acceptance suites.

## Dependencies

Linux x86-64 with a static C toolchain, Python 3.12, and libseccomp 2.5.5 were used in the recorded run. Inference used a CPU build of `llama-cpp-python==0.3.16`, with two inference threads. The optional inference dependency is absent from the fixture-only quick start.

```bash
python3 -m venv .venv
. .venv/bin/activate
CC=gcc CXX=g++ CMAKE_BUILD_PARALLEL_LEVEL=2 CMAKE_ARGS='-DGGML_OPENMP=OFF -DGGML_NATIVE=OFF' pip install -r requirements-model.txt
```

Provision the exact model GGUF and a sibling `model.json` matching the recorded protocol before disconnecting. Official model repositories:

- https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF
- https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF

Record repository revision, filename, byte size, and SHA-256 in `model.json`. Full recorded identifiers are in each experiment's `protocol.json`. Downloading weights is preparation, not part of disconnected repair execution. No model weights are stored in this repository.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 python3 experiments/run_model_pilot.py \
  --model /absolute/path/to/model.gguf --python "$VIRTUAL_ENV/bin/python" \
  --output /absolute/path/to/new-run
python3 experiments/mission_pilot.py --output /absolute/path/to/mission-run.json
python3 -m unittest discover -s tests -v
```

The first command refuses to reuse an existing protocol directory in the updated runner. Reproduce in a fresh output directory. Exact historical runner source is retained in the recorded experiment snapshots where present.

## Boundaries and limitations

Network creation and connection syscalls are denied in the inference child using seccomp, with a socket-denial self-test. Children inherit the filter. Model generation is limited to two attempts per task/seed, 384 output tokens, a 2048-token context, 90 CPU seconds and 120 wall seconds per invocation, and a 3 GiB virtual-address limit. These are host limits, not flight-computer specifications.

Generated C is statically linked. Its runtime profile defaults to EPERM and permits a small syscall set without file opens, sockets, process creation, or file mutation. Execution has a 128 MiB address limit, one CPU second, and a wall timeout. The profile still permits initial `execve` and several metadata syscalls; it is not a formal isolation proof. Kernel compromise and malicious toolchains are outside scope.

The compiler runs on the host. A function-only input contract rejects preprocessing directives and selected unsupported constructs, but this is not a hardened compiler sandbox. Generated source must be reviewed or compilation moved into a disposable hardened environment before accepting arbitrary hostile sources. The current study establishes no hostile-generator containment guarantee.

The trusted inference worker receives prompts, not tools for reading the repository. Acceptance/evaluator files are absent from the prompt. They are not protected by separate filesystem privileges in this host, and public test contamination remains possible. Acceptance/evaluation feedback is not given to generation; only development failures are returned.

The mission test measures real CPU/wall time for an artificial periodic task and an artificial validation workload pinned to one logical CPU. It does not include inference, real patch validation, spacecraft dynamics, a real-time scheduler, or flight hardware. Its phase-aware deferral uses a known load schedule and is not a novel scheduling result.
