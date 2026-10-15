import tempfile
import unittest
from pathlib import Path
import lab


class AcceptanceTests(unittest.TestCase):
    def test_exhaustion_overrides_success(self):
        self.assertEqual(lab.decision(True, True, 'B3', 'light', True), 'terminate')

    def test_failure_is_not_deferred(self):
        self.assertEqual(lab.decision(True, False, 'B3', 'busy'), 'reject')

    def test_busy_valid_patch_is_deferred(self):
        self.assertEqual(lab.decision(True, True, 'B3', 'busy'), 'defer')

    def test_suites_disjoint(self):
        sets = [{tuple(args) for args, _ in suite} for suite in
                [lab.DEVELOPMENT, lab.ACCEPTANCE, lab.EVALUATION]]
        self.assertFalse(sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2])

    def test_end_to_end_rejects_partial_and_preserves_recovery(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            lab.run(Path(directory))
            r = json.loads((Path(directory) / 'pilot.json').read_text())
        partial = [x for x in r['rows'] if x['candidate'] == 'partial']
        self.assertTrue(all(x['decision'] == 'accept' for x in partial if x['baseline'] == 'B1'))
        self.assertTrue(all(x['decision'] == 'reject' for x in partial if x['baseline'] == 'B2'))
        self.assertTrue(all(x['original_restored_or_preserved'] for x in r['recovery'] if x['fault']))
        self.assertEqual(r['digest_mismatch_check'], 'artifact_mismatch')
        self.assertIsNone(r['model_used'])


if __name__ == '__main__':
    unittest.main()
