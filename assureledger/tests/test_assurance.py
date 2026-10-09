from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from assureledger.engine import assess, band, device_quota, evidence_status, load, score, validate

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 10, 10)


class AssuranceTests(unittest.TestCase):
    def setUp(self):
        self.data = load(ROOT / 'data/scenario.json')

    def test_risk_boundaries(self):
        self.assertEqual(score(4, 5), 20)
        for value, expected in [(5,'low'),(6,'moderate'),(11,'moderate'),(12,'high'),(19,'high'),(20,'critical')]:
            self.assertEqual(band(value), expected)

    def test_invalid_scores(self):
        for value in (True, 0, 6, '4', 2.5):
            with self.assertRaises(ValueError):
                score(value, 4)

    def test_quota_boundary_and_unknown(self):
        for value, expected in [(0,'pass'),(20,'pass'),(21,'fail'),(None,'unknown'),(True,'unknown'),(-1,'unknown'),('20','unknown')]:
            self.assertEqual(device_quota({'userDeviceQuota':value}),expected)

    def test_broken_reference_rejected(self):
        self.data['risks'][0]['controls'] = ['missing']
        with self.assertRaises(ValueError): validate(self.data)

    def test_duplicate_identifier_rejected(self):
        self.data['risks'].append(deepcopy(self.data['risks'][0]))
        with self.assertRaises(ValueError): validate(self.data)

    def test_malformed_evidence_metadata_rejected(self):
        self.data['evidence'][0]['sha256'] = 'not-a-digest'
        with self.assertRaises(ValueError): validate(self.data)

    def test_missing_required_field_rejected(self):
        del self.data['risks'][0]['owner']
        with self.assertRaises(ValueError): validate(self.data)

    def test_evidence_expiry_before_collection_rejected(self):
        self.data['evidence'][0]['expires'] = '2026-01-01'
        self.data['evidence'][0]['collected'] = '2026-02-01'
        with self.assertRaises(ValueError): validate(self.data)

    def test_exclusion_requires_reason(self):
        self.data['controls'][6]['rationale'] = ''
        with self.assertRaises(ValueError): validate(self.data)

    def test_review_requires_reviewer(self):
        self.data['evidence'][1]['reviewer'] = ''
        with self.assertRaises(ValueError): validate(self.data)

    def test_expired_evidence_invalidates_closure(self):
        result = assess(self.data, ROOT/'data', AS_OF)
        self.assertEqual(result['evidence']['E03'], 'expired')
        self.assertEqual(result['findings'][1]['effective_status'], 'closure_unverified')
        self.assertTrue(result['findings'][1]['overdue'])

    def test_valid_closure_requires_independent_verifier(self):
        f = self.data['findings'][0]
        f.update(status='closed',closure_evidence=['E02'],verified_by=f['owner'])
        self.assertEqual(assess(self.data,ROOT/'data',AS_OF)['findings'][0]['effective_status'],'closure_unverified')
        f['verified_by'] = 'independent reviewer'
        self.assertEqual(assess(self.data,ROOT/'data',AS_OF)['findings'][0]['effective_status'],'closed')

    def test_implemented_without_evidence_is_gap(self):
        self.data['controls'][1]['evidence'] = []
        self.assertEqual(assess(self.data,ROOT/'data',AS_OF)['controls'][1]['assurance'],'evidence_gap')

    def test_hash_change_detected(self):
        e = deepcopy(self.data['evidence'][1]); e['sha256'] = '0'*64
        self.assertEqual(evidence_status(e,ROOT/'data',AS_OF),'integrity_failed')

    def test_path_traversal_rejected(self):
        e = deepcopy(self.data['evidence'][1]); e['path'] = '../README.md'
        self.assertEqual(evidence_status(e,ROOT/'data',AS_OF),'unsafe_path')

    def test_missing_evidence(self):
        e = deepcopy(self.data['evidence'][1]); e['path'] = 'evidence/absent.txt'
        self.assertEqual(evidence_status(e,ROOT/'data',AS_OF),'missing')

    def test_expiry_boundary_and_future_collection(self):
        e = deepcopy(self.data['evidence'][1]); e['expires'] = AS_OF.isoformat()
        self.assertEqual(evidence_status(e,ROOT/'data',AS_OF),'accepted')
        e['collected'] = '2026-10-11'
        self.assertEqual(evidence_status(e,ROOT/'data',AS_OF),'invalid_date')

    def test_pending_review(self):
        self.assertEqual(evidence_status(self.data['evidence'][0],ROOT/'data',AS_OF),'pending_review')

    def test_cli_reports_and_output_escaping(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            self.data['organization'] = '<script>alert(1)</script>'
            self.data['controls'][0]['objective'] = '=1+1'
            source = tmp/'scenario.json'
            source.write_text(json.dumps(self.data))
            (tmp/'evidence').mkdir()
            (tmp/'evidence/device-policy.json').write_text('{"userDeviceQuota":50}')
            result = subprocess.run([sys.executable,'-m','assureledger','--data',str(source),'--as-of','2026-10-10','--out',str(tmp/'out')],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            html = (tmp/'out/management-review.html').read_text()
            self.assertNotIn('<script>',html)
            self.assertIn('&lt;script&gt;',html)
            self.assertIn("'=1+1",(tmp/'out/soa.csv').read_text())
            report = load(tmp/'out/assessment.json')
            self.assertEqual(report['as_of'],'2026-10-10')
            self.assertEqual(report['technical_check']['device_quota'],'fail')

    def test_cli_missing_optional_device_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp/'scenario.json'
            source.write_text(json.dumps(self.data))
            (tmp/'evidence').mkdir()
            result = subprocess.run([sys.executable,'-m','assureledger','--data',str(source),'--as-of','2026-10-10','--out',str(tmp/'out')],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(load(tmp/'out/assessment.json')['technical_check']['device_quota'],'unknown')


if __name__ == '__main__':
    unittest.main()
