"""Protect artifact verification from accepting corrupt or escaped evidence."""
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest


class ReproductionTests(unittest.TestCase):
    def module(self):
        try:
            return importlib.import_module('scripts.reproduce')
        except ModuleNotFoundError:
            self.fail('Offline reproduction helper is not implemented')

    def test_changed_numeric_result_is_rejected(self):
        compare=self.module().assert_equivalent
        compare({'rate':[0.5,None]}, {'rate':[0.5+1e-12,None]})
        with self.assertRaises(ValueError):
            compare({'rate':[0.5,None]}, {'rate':[0.6,None]})
        with self.assertRaises(ValueError):
            compare({'rate':None}, {'rate':0})

    def test_nonfinite_and_boolean_substitution_are_rejected(self):
        compare=self.module().assert_equivalent
        for value in (float('nan'),float('inf'),True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                compare(1.0,value)

    def test_evidence_corruption_is_rejected(self):
        module=self.module()
        with tempfile.TemporaryDirectory(dir='work') as name:
            root=Path(name)
            (root/'case.json').write_bytes(b'original')
            (root/'manifest.json').write_text(json.dumps({'files':[{'path':'case.json','sha256':hashlib.sha256(b'original').hexdigest()}]}))
            self.assertEqual(module.verify_evidence(root),1)
            (root/'case.json').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                module.verify_evidence(root)

    def test_manifest_cannot_escape_its_directory(self):
        child=self.module().safe_child
        for name in ('../outside','/outside','C:/outside','a/../../outside','a\\..\\outside'):
            with self.subTest(name=name),self.assertRaises(ValueError):
                child(Path('work').resolve(),name)

    def test_existing_destination_is_preserved(self):
        prepare=self.module().prepare_workspace
        with tempfile.TemporaryDirectory(dir='work') as name:
            destination=Path(name)
            sentinel=destination/'keep.txt'
            sentinel.write_text('keep')
            with self.assertRaises(FileExistsError):
                prepare(Path('.').resolve(),destination)
            self.assertEqual(sentinel.read_text(),'keep')


if __name__=='__main__':
    unittest.main()
