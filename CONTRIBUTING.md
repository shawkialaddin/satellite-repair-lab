# Contributing

This is an early research testbed. Contributions that strengthen reproducibility, independent evaluation, and measured resource constraints are welcome.

## Before changing an experiment

Open an issue describing the research question, proposed change, and expected evidence. Keep benchmark expansion separate from acceptance-policy tuning. Record fixture provenance and third-party licenses. Do not use evaluation outcomes to tune a repair generator while describing those cases as held out.

## Local checks

Use Python 3.10+ and a C11 compiler named `cc`:

```bash
python3 -m unittest discover -s tests -v
python3 lab.py --output /tmp/satellite-repair-pilot
```

Include the command, environment, failures, and relevant output in your pull request. Tests run included trusted fixtures on the host. Generated C belongs in the disposable evaluator described in `docs/EXPERIMENT.md`.

## Reporting results

State whether candidates were handwritten or model-generated. Distinguish synthetic timing from measurements. Report rejected, deferred, failed, and timed-out attempts, with denominators. Do not claim general security from passing a finite test suite. Do not commit model weights, credentials, or private data.

## Contributions and authorship

Contributions are submitted under the repository's Apache 2.0 license. Code contribution does not automatically establish paper authorship; discuss research contributions and authorship with the maintainer before publication.
