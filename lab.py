"""Synthetic acceptance pilot. No model repair success is claimed."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Frozen, disjoint sets. Public for reproducibility; never claim unseen-to-model status.
DEVELOPMENT = [(["1", "0", "10"], "OK:1"), (["3", "0", "10"], "REJECT")]
ACCEPTANCE = [(["2", "1", "10", "20"], "OK:2"),
              (["0", "2"], "OK:0"), (["2", "1", "10"], "REJECT"),
              (["1", "9", "10"], "REJECT")]
EVALUATION = [(["3", "3", "1", "2", "255"], "OK:3"),
              (["0", "8"], "REJECT"), (["1", "0", "256"], "REJECT"),
              (["1x", "0", "1"], "REJECT"), (["-1", "0"], "REJECT"),
              (["33", "0"] + ["1"] * 33, "REJECT")]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(source, target):
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", str(source),
                    "-o", str(target)], check=True, capture_output=True, timeout=20)


def checks(executable, cases):
    outcomes = []
    for args, expected in cases:
        try:
            r = subprocess.run([str(executable), *args], capture_output=True,
                               text=True, timeout=1)
            ok = r.returncode == 0 and r.stdout.strip() == expected
        except subprocess.TimeoutExpired:
            ok = False
        outcomes.append(ok)
    return all(outcomes)


def decision(development_ok, protected_ok, baseline, mission_load, exhausted=False):
    if exhausted:
        return "terminate"
    if not development_ok:
        return "reject"
    if baseline != "B1" and not protected_ok:
        return "reject"
    if baseline == "B3" and mission_load == "busy":
        return "defer"
    return "accept"


def timing_surrogate(baseline, load, ticks=100):
    """Discrete deterministic accounting, NOT measured OS or spacecraft timing.
    Each slot has 10 units; mission demand is 4 (light) or 9 (busy).
    Validation demand is 3 units in first 20 slots. B3 defers busy work.
    """
    mission = 4 if load == "light" else 9
    misses = 0
    for tick in range(ticks):
        repair = 3 if tick < 20 else 0
        if baseline == "B0" or (baseline == "B3" and load == "busy"):
            repair = 0
        misses += int(mission + repair > 10)
    return {"synthetic_deadline_misses": misses, "slots": ticks,
            "measurement_kind": "deterministic_timing_surrogate"}


def activate(candidate, tested_digest, active, recovery, fault=None):
    if digest(candidate) != tested_digest:
        return "artifact_mismatch"
    previous = active.read_bytes()
    recovery.write_bytes(previous)
    staged = active.with_suffix(".staged")
    staged.write_bytes(candidate.read_bytes())
    staged.chmod(0o700)
    if fault == "interrupt":
        staged.unlink()
        return "interrupted_preserved"
    staged.replace(active)
    if fault == "health_failure" or not checks(active, ACCEPTANCE):
        active.write_bytes(recovery.read_bytes())
        active.chmod(0o700)
        return "rolled_back"
    return "activated"


def rate(numerator, denominator):
    return None if denominator == 0 else numerator / denominator


def summarize(rows):
    output = []
    for baseline in ["B1", "B2", "B3"]:
        for load in ["light", "busy"]:
            group = [r for r in rows if r["baseline"] == baseline and r["load"] == load]
            accepted = [r for r in group if r["decision"] == "accept"]
            valid = [r for r in group if r["held_out_valid"]]
            rejected_valid = sum(r["decision"] == "reject" for r in valid)
            harmful = sum(not r["held_out_valid"] for r in accepted)
            output.append({"baseline": baseline, "load": load,
                           "cases": len(group), "accepted": len(accepted),
                           "harmful_accepted": harmful,
                           "erroneous_acceptance_rate": rate(harmful, len(accepted)),
                           "valid_patch_rejection_rate": rate(rejected_valid, len(valid)),
                           "valid_activated_yield": rate(sum(r["held_out_valid"] for r in accepted), len(group)),
                           "deferred": sum(r["decision"] == "defer" for r in group),
                           **timing_surrogate(baseline, load)})
    return output


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    rows, recovery_checks = [], []
    with tempfile.TemporaryDirectory() as directory:
        workspace = Path(directory)
        vulnerable = workspace / "vulnerable"
        build(ROOT / "candidates/vulnerable.c", vulnerable)
        for name in ["vulnerable", "partial", "fixed", "reject_all"]:
            executable = workspace / name
            start = time.perf_counter()
            build(ROOT / f"candidates/{name}.c", executable)
            build_seconds = time.perf_counter() - start
            start = time.perf_counter()
            dev = checks(executable, DEVELOPMENT)
            protected = checks(executable, ACCEPTANCE)
            validation_seconds = time.perf_counter() - start
            # Evaluation never feeds candidate generation or acceptance decisions.
            evaluated = checks(executable, EVALUATION)
            for baseline in ["B1", "B2", "B3"]:
                for load in ["light", "busy"]:
                    d = decision(dev, protected, baseline, load)
                    rows.append({"candidate": name, "provenance": "handwritten_fixture",
                                 "source_sha256": digest(ROOT / f"candidates/{name}.c"),
                                 "artifact_sha256": digest(executable),
                                 "baseline": baseline, "load": load, "decision": d,
                                 "development_pass": dev, "acceptance_pass": protected,
                                 "held_out_valid": evaluated, "host_build_seconds": build_seconds,
                                 "host_validation_seconds": validation_seconds})
        active, recovery = workspace / "active", workspace / "recovery"
        for fault in [None, "interrupt", "health_failure"]:
            shutil.copy2(vulnerable, active)
            original = digest(active)
            status = activate(workspace / "fixed", digest(workspace / "fixed"), active, recovery, fault)
            preserved = digest(active) == original
            recovery_checks.append({"fault": fault, "status": status,
                                    "original_restored_or_preserved": preserved})
        mismatch = activate(workspace / "fixed", "wrong-digest", active, recovery)
        assert mismatch == "artifact_mismatch"
    report = {"status": "fixture_infrastructure_pilot_not_ai_repair_results",
              "model_used": None, "case_count": 4,
              "limits": ["handwritten candidates", "synthetic timing", "no hardware power measurements",
                         "trusted fixture execution on host; not a security sandbox",
                         "public evaluation cases are not contamination-proof"],
              "rows": rows, "summary": summarize(rows), "recovery": recovery_checks,
              "digest_mismatch_check": mismatch,
              "no_repair_timing": [timing_surrogate("B0", load) for load in ["light", "busy"]]}
    (output / "pilot.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Fixture infrastructure pilot", "", "No model was used. These are not AI repair results.", "",
             "| Baseline | Load | Accepted | Harmful accepted | Deferred | Synthetic deadline misses |",
             "| --- | --- | --- | --- | --- | --- |"]
    for s in report["summary"]:
        lines.append(f'| {s["baseline"]} | {s["load"]} | {s["accepted"]} | {s["harmful_accepted"]} | {s["deferred"]} | {s["synthetic_deadline_misses"]} |')
    lines += ["", "Timing differences follow the explicit surrogate policy and are not evidence of a scheduling innovation.",
              "Full provenance, host timings, recovery outcomes, and limitations are in pilot.json."]
    (output / "pilot.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"output": str(output), "fixture_runs": len(rows), "model_used": None,
                      "recovery": recovery_checks}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    run(parser.parse_args().output)
