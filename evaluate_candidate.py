"""Run ONLY inside the documented disposable container for generated candidates."""
import json
import os
import tempfile
from pathlib import Path
import lab
if os.environ.get('SATLAB_CONTAINER') != '1':
    raise SystemExit('Use the documented container command; host execution is disabled.')
source = Path('/candidate/patch.c')
with tempfile.TemporaryDirectory() as temp:
    target = Path(temp) / 'parser'
    try:
        lab.build(source, target)
        development = lab.checks(target, lab.DEVELOPMENT)
        acceptance = lab.checks(target, lab.ACCEPTANCE)
        evaluation = lab.checks(target, lab.EVALUATION)
        result = {'candidate_sha256': lab.digest(source), 'build': True,
                  'development_pass': development, 'acceptance_pass': acceptance,
                  'held_out_pass': evaluation,
                  'decisions': {b: {load: lab.decision(development, acceptance, b, load)
                                   for load in ['light', 'busy']} for b in ['B1', 'B2', 'B3']},
                  'status': 'single_candidate_evaluation_not_general_repair_evidence'}
    except Exception as exc:
        result = {'build_or_execution_failed': True, 'error_type': type(exc).__name__}
Path('/output/candidate-result.json').write_text(json.dumps(result, indent=2) + '\n')
