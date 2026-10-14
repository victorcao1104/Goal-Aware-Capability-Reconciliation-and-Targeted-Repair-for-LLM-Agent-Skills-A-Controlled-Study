import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from research_v5 import run
from research_v5.core import mechanism_controls

class ReviewTests(unittest.TestCase):
    def test_distinct_infrastructure_failures_never_overwrite(self):
        scratch=run.ROOT/'work';scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as d:
            with patch.object(run,'ROOT',Path(d)):
                run.record_infrastructure_failure('key1','fp1',ValueError('do not publish me'))
                run.record_infrastructure_failure('key2','fp2',OSError('do not publish me'))
            files=list(Path(d).rglob('*.json'))
            self.assertEqual(len(files),2)
            self.assertNotIn('do not publish me',''.join(p.read_text() for p in files))
    def test_recorded_controls_show_limit_and_legitimate_expansion(self):
        c=mechanism_controls()
        self.assertEqual(c['unauthorized_expansion']['execution']['unauthorized'],0)
        self.assertEqual(c['unchanged_bad_initial']['execution']['unauthorized'],2)
        self.assertEqual(c['repaired_initial']['execution']['unauthorized'],0)
        self.assertEqual(c['trusted_harness_expansion']['effective_excess'],[])
        self.assertTrue(c['trusted_harness_expansion']['extra_effects_complete'])
if __name__=='__main__':unittest.main()
