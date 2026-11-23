from copy import deepcopy
from datetime import date
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from assureledger.engine import (acceptance_status, assess, band, device_quota, evidence_status, load,
                                 load_catalog, score)
from assureledger.reports import _cell
from assureledger.schema import ScenarioError, validate

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AS_OF = date(2026, 10, 10)
CATALOG = load_catalog()
CATALOG_IDS = {c["id"] for c in CATALOG}


def by_id(rows, ident):
    return next(row for row in rows if row["id"] == ident)


def run_cli(*args):
    return subprocess.run([sys.executable, "-m", "assureledger", *args], cwd=ROOT, capture_output=True, text=True)


class Base(unittest.TestCase):
    def setUp(self):
        self.data = load(DATA / "scenario.json")

    def assess(self, as_of=AS_OF):
        return assess(self.data, DATA, as_of, CATALOG)

    def assert_invalid(self, fragment=None):
        with self.assertRaises(ScenarioError) as ctx:
            validate(self.data, CATALOG_IDS)
        if fragment:
            self.assertIn(fragment, str(ctx.exception))

    def issue_types(self, result):
        return {(i["type"], i["ref"]) for i in result["issues"]}


class CatalogTests(unittest.TestCase):
    def test_catalog_has_all_93_annex_a_controls(self):
        self.assertEqual(len(CATALOG), 93)
        self.assertEqual(len(CATALOG_IDS), 93)
        themes = {}
        for c in CATALOG:
            themes[c["theme"]] = themes.get(c["theme"], 0) + 1
        self.assertEqual(themes, {"organisational": 37, "people": 8, "physical": 14, "technological": 34})


class ScoringTests(unittest.TestCase):
    def test_risk_boundaries(self):
        self.assertEqual(score(4, 5), 20)
        for value, expected in [(5, "low"), (6, "moderate"), (11, "moderate"), (12, "high"), (19, "high"), (20, "critical")]:
            self.assertEqual(band(value), expected)

    def test_invalid_scores(self):
        for value in (True, 0, 6, "4", 2.5, None):
            with self.assertRaises(ValueError):
                score(value, 4)

    def test_quota_boundary_and_unknown(self):
        for value, expected in [(0, "pass"), (20, "pass"), (21, "fail"), (None, "unknown"), (True, "unknown"),
                                (-1, "unknown"), ("20", "unknown")]:
            self.assertEqual(device_quota({"userDeviceQuota": value}), expected)
        self.assertEqual(device_quota([]), "unknown")


class ValidationTests(Base):
    def test_shipped_scenario_is_valid(self):
        validate(self.data, CATALOG_IDS)

    def test_schema_version_required(self):
        self.data["schema_version"] = "0.1"
        self.assert_invalid("schema_version")

    def test_broken_reference_rejected(self):
        self.data["risks"][0]["controls"] = ["A.5.1"]  # real Annex A id but no SoA decision
        self.assert_invalid("no SoA decision")

    def test_unknown_control_identifier_rejected(self):
        self.data["controls"][0]["id"] = "A.9.99"
        self.assert_invalid("not an ISO/IEC 27001:2022 Annex A identifier")

    def test_additional_control_allowed_when_marked(self):
        extra = deepcopy(self.data["controls"][0])
        extra.update(id="HC-01", source="additional", objective="Customer-specific escrow arrangement")
        self.data["controls"].append(extra)
        validate(self.data, CATALOG_IDS)
        result = self.assess()
        self.assertEqual(by_id(result["soa"], "HC-01")["theme"], "additional")
        self.assertEqual(len(result["soa"]), 94)

    def test_duplicate_identifier_rejected(self):
        self.data["risks"].append(deepcopy(self.data["risks"][0]))
        self.assert_invalid("Duplicate")

    def test_wrong_types_give_clean_errors(self):
        cases = [("assets", "owner", 7), ("risks", "owner", None), ("risks", "likelihood", "4"),
                 ("controls", "evidence", "E02"), ("findings", "verified_by", 3)]
        for collection, field, value in cases:
            with self.subTest(collection=collection, field=field):
                self.setUp()
                self.data[collection][0][field] = value
                self.assert_invalid()

    def test_malformed_evidence_metadata_rejected(self):
        self.data["evidence"][0]["sha256"] = "not-a-digest"
        self.assert_invalid("sha256")

    def test_missing_required_field_rejected(self):
        del self.data["risks"][0]["owner"]
        self.assert_invalid("missing: owner")

    def test_invalid_date_rejected(self):
        self.data["risks"][0]["due"] = "30/10/2026"
        self.assert_invalid("not a valid date")

    def test_evidence_expiry_before_collection_rejected(self):
        self.data["evidence"][0].update(expires="2026-01-01", collected="2026-02-01")
        self.assert_invalid("expiry")

    def test_exclusion_requires_reason(self):
        by_id(self.data["controls"], "A.7.2")["rationale"] = ""
        self.assert_invalid("rationale")

    def test_excluded_control_cannot_claim_implementation(self):
        by_id(self.data["controls"], "A.7.2")["implementation"] = "partial"
        self.assert_invalid("not_applicable")

    def test_reviewed_evidence_requires_reviewer(self):
        self.data["evidence"][1]["reviewer"] = ""
        self.assert_invalid("reviewer")

    def test_included_control_cannot_be_not_applicable(self):
        by_id(self.data["controls"], "A.5.9")["implementation"] = "not_applicable"
        self.assert_invalid("cannot be not_applicable")

    def test_partial_residual_rejected(self):
        self.data["risks"][0]["residual_likelihood"] = 2
        self.assert_invalid("residual")

    def test_modify_treatment_requires_controls(self):
        self.data["risks"][0]["controls"] = []
        self.assert_invalid("selects no controls")

    def test_treatment_option_must_be_iso_27005_option(self):
        self.data["risks"][0]["treatment_option"] = "reduce"
        self.assert_invalid("treatment_option")

    def test_accepted_risk_requires_decision_record(self):
        by_id(self.data["risks"], "R06")["acceptance"]["decided_by"] = ""
        self.assert_invalid("decided_by")

    def test_owner_limit_cannot_exceed_management_limit(self):
        self.data["risk_criteria"]["owner_acceptance_max"] = 20
        self.assert_invalid("owner limit")


class EvidenceTests(Base):
    def test_hash_change_detected(self):
        e = deepcopy(self.data["evidence"][1]); e["sha256"] = "0" * 64
        self.assertEqual(evidence_status(e, DATA, AS_OF), "integrity_failed")

    def test_path_traversal_rejected(self):
        e = deepcopy(self.data["evidence"][1]); e["path"] = "../README.md"
        self.assertEqual(evidence_status(e, DATA, AS_OF), "unsafe_path")

    def test_missing_evidence(self):
        e = deepcopy(self.data["evidence"][1]); e["path"] = "evidence/absent.txt"
        self.assertEqual(evidence_status(e, DATA, AS_OF), "missing")

    def test_expiry_boundary_and_future_collection(self):
        e = deepcopy(self.data["evidence"][1]); e["expires"] = AS_OF.isoformat()
        self.assertEqual(evidence_status(e, DATA, AS_OF), "accepted")
        e["collected"] = "2026-10-11"
        self.assertEqual(evidence_status(e, DATA, AS_OF), "invalid_date")

    def test_pending_review(self):
        self.assertEqual(evidence_status(self.data["evidence"][0], DATA, AS_OF), "pending_review")

    def test_rejected_evidence_is_reported_as_rejected(self):
        # v0.1 bug: rejected evidence was reported as pending_review.
        e = deepcopy(self.data["evidence"][1]); e["review"] = "rejected"
        self.assertEqual(evidence_status(e, DATA, AS_OF), "rejected")

    def test_uppercase_digest_still_matches(self):
        e = deepcopy(self.data["evidence"][1]); e["sha256"] = e["sha256"].upper()
        self.assertEqual(evidence_status(e, DATA, AS_OF), "accepted")


class AssessmentTests(Base):
    def test_soa_covers_every_annex_a_control(self):
        result = self.assess()
        self.assertEqual([r["id"] for r in result["soa"]], [c["id"] for c in CATALOG])
        self.assertEqual(result["summary"]["soa_decided"], len(self.data["controls"]))
        self.assertIn(("soa_incomplete", "SoA"), self.issue_types(result))

    def test_complete_soa_removes_incomplete_issue(self):
        decided = {c["id"] for c in self.data["controls"]}
        for ref in CATALOG:
            if ref["id"] not in decided:
                self.data["controls"].append({"id": ref["id"], "objective": ref["topic"], "applicability": "excluded",
                                              "implementation": "not_applicable", "rationale": "Test exclusion",
                                              "evidence": [], "owner": "tester"})
        self.assertNotIn(("soa_incomplete", "SoA"), self.issue_types(self.assess()))

    def test_expired_evidence_invalidates_closure(self):
        result = self.assess()
        self.assertEqual(result["evidence"]["E03"], "expired")
        f02 = by_id(result["findings"], "F02")
        self.assertEqual(f02["effective_status"], "closure_unverified")
        self.assertTrue(f02["overdue"])
        self.assertIn(("closure_unverified", "F02"), self.issue_types(result))

    def test_valid_closure_requires_independent_verifier(self):
        f = self.data["findings"][0]
        f.update(status="closed", closure_evidence=["E02"], verified_by=f["owner"])
        self.assertEqual(by_id(self.assess()["findings"], "F01")["effective_status"], "closure_unverified")
        f["verified_by"] = "independent reviewer"
        self.assertEqual(by_id(self.assess()["findings"], "F01")["effective_status"], "closed")

    def test_implemented_without_evidence_is_gap(self):
        by_id(self.data["controls"], "A.5.15")["evidence"] = []
        self.assertEqual(by_id(self.assess()["soa"], "A.5.15")["assurance"], "evidence_gap")

    def test_risk_relying_on_excluded_control_is_flagged(self):
        by_id(self.data["risks"], "R01")["controls"].append("A.7.2")
        result = self.assess()
        self.assertEqual(by_id(result["risks"], "R01")["soa_conflicts"], ["A.7.2"])
        self.assertIn(("soa_conflict", "R01"), self.issue_types(result))

    def test_overdue_treatment_flagged_and_complete_is_not(self):
        result = self.assess(date(2026, 11, 23))
        self.assertTrue(by_id(result["risks"], "R03")["treatment_overdue"])
        self.assertFalse(by_id(result["risks"], "R06")["treatment_overdue"])
        severity = {i["ref"]: i["severity"] for i in result["issues"] if i["type"] == "treatment_overdue"}
        self.assertEqual(severity["R03"], "high")  # critical inherent risk

    def test_obligation_coverage(self):
        result = self.assess()
        self.assertEqual(by_id(result["obligations"], "OB01")["coverage"], "gap")
        by_id(self.data["obligations"], "OB01")["controls"] = ["A.5.15"]
        self.assertEqual(by_id(self.assess()["obligations"], "OB01")["coverage"], "supported_for_review")
        by_id(self.data["obligations"], "OB01")["controls"] = ["A.7.2"]
        self.assertEqual(by_id(self.assess()["obligations"], "OB01")["coverage"], "soa_conflict")
        by_id(self.data["obligations"], "OB01")["applicability"] = "not_applicable"
        self.assertEqual(by_id(self.assess()["obligations"], "OB01")["coverage"], "not_applicable")

    def test_obligation_review_overdue(self):
        result = self.assess(date(2026, 12, 16))
        self.assertTrue(by_id(result["obligations"], "OB04")["review_overdue"])

    def test_issues_sorted_high_first(self):
        severities = [i["severity"] for i in self.assess()["issues"]]
        self.assertEqual(severities, sorted(severities, key={"high": 0, "medium": 1, "low": 2}.get))

    def test_assessment_is_deterministic(self):
        self.assertEqual(self.assess(), self.assess())


class AcceptanceTests(Base):
    def risk(self, **changes):
        r = deepcopy(by_id(self.data["risks"], "R06"))
        r.update(changes)
        return r

    def test_management_acceptance_within_authority_is_valid(self):
        self.assertEqual(acceptance_status(self.risk(), self.data["risk_criteria"], AS_OF), "valid")

    def test_owner_cannot_accept_above_owner_limit(self):
        r = self.risk(); r["acceptance"]["decided_by"] = r["owner"]  # residual 9 > owner limit 8
        self.assertEqual(acceptance_status(r, self.data["risk_criteria"], AS_OF), "exceeds_authority")

    def test_owner_can_accept_within_owner_limit(self):
        r = self.risk(residual_likelihood=2, residual_impact=4); r["acceptance"]["decided_by"] = r["owner"]
        self.assertEqual(acceptance_status(r, self.data["risk_criteria"], AS_OF), "valid")

    def test_nobody_can_accept_above_management_limit(self):
        r = self.risk(residual_likelihood=4, residual_impact=4)
        self.assertEqual(acceptance_status(r, self.data["risk_criteria"], AS_OF), "exceeds_authority")

    def test_expired_acceptance(self):
        self.assertEqual(acceptance_status(self.risk(), self.data["risk_criteria"], date(2027, 4, 1)), "expired")

    def test_acceptance_without_residual(self):
        r = self.risk(residual_likelihood=None, residual_impact=None)
        self.assertEqual(acceptance_status(r, self.data["risk_criteria"], AS_OF), "missing_residual")

    def test_rejected_acceptance_on_modified_risk_is_not_an_issue(self):
        by_id(self.data["risks"], "R01")["acceptance"].update(
            status="rejected", decided_by="IT lead", decided_on="2026-10-02", rationale="Treat instead")
        result = self.assess()
        self.assertEqual(by_id(result["risks"], "R01")["acceptance_status"], "rejected")
        self.assertFalse(any(i["ref"] == "R01" for i in result["issues"]))

    def test_retained_risk_without_valid_acceptance_is_high_issue(self):
        by_id(self.data["risks"], "R06")["acceptance"]["decided_by"] = "IT lead"
        types = self.issue_types(self.assess())
        self.assertIn(("retained_without_acceptance", "R06"), types)
        self.assertIn(("acceptance_exceeds_authority", "R06"), types)


class ReportTests(Base):
    def test_csv_formula_prefixes_neutralised(self):
        for value in ("=1+1", "+cmd", "-2", "@SUM(A1)", "\tHIDDEN", "\rX"):
            self.assertTrue(_cell(value).startswith("'"), repr(value))
        self.assertEqual(_cell("plain"), "plain")
        self.assertEqual(_cell(["E01", "E02"]), "E01; E02")

    def test_cli_reports_and_output_escaping(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            self.data["organization"] = "<script>alert(1)</script>"
            by_id(self.data["controls"], "A.5.9")["rationale"] = "=1+1"
            (tmp / "scenario.json").write_text(json.dumps(self.data))
            (tmp / "evidence").mkdir()
            (tmp / "evidence/device-policy.json").write_text('{"userDeviceQuota":50}')
            result = run_cli("--data", str(tmp / "scenario.json"), "--as-of", "2026-10-10", "--out", str(tmp / "out"))
            self.assertEqual(result.returncode, 0, result.stderr)
            html = (tmp / "out/management-review.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>", html)
            self.assertIn("&lt;script&gt;", html)
            with (tmp / "out/soa.csv").open(encoding="utf-8", newline="") as stream:
                rows = {r["id"]: r for r in csv.DictReader(stream)}
            self.assertEqual(len(rows), 93)
            self.assertEqual(rows["A.5.9"]["rationale"], "'=1+1")
            self.assertTrue((tmp / "out/risk-register.csv").is_file())
            report = load(tmp / "out/assessment.json")
            self.assertEqual(report["as_of"], "2026-10-10")
            self.assertEqual(report["technical_check"]["device_quota"], "fail")

    def test_cli_missing_optional_device_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "scenario.json").write_text(json.dumps(self.data))
            (tmp / "evidence").mkdir()
            result = run_cli("--data", str(tmp / "scenario.json"), "--as-of", "2026-10-10", "--out", str(tmp / "out"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(load(tmp / "out/assessment.json")["technical_check"]["device_quota"], "unknown")

    def test_cli_invalid_scenario_exits_2_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            del self.data["risks"][0]["owner"]
            (tmp / "scenario.json").write_text(json.dumps(self.data))
            result = run_cli("--data", str(tmp / "scenario.json"), "--out", str(tmp / "out"))
            self.assertEqual(result.returncode, 2)
            self.assertIn("Scenario error", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            (tmp / "scenario.json").write_text("{not json")
            self.assertEqual(run_cli("--data", str(tmp / "scenario.json"), "--out", str(tmp / "out")).returncode, 2)

    def test_cli_unreadable_device_snapshot_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "scenario.json").write_text(json.dumps(self.data))
            (tmp / "evidence").mkdir()
            (tmp / "evidence/device-policy.json").write_text("{broken")
            result = run_cli("--data", str(tmp / "scenario.json"), "--as-of", "2026-10-10", "--out", str(tmp / "out"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(load(tmp / "out/assessment.json")["technical_check"]["device_quota"], "unknown")

    def test_cli_strict_mode_fails_on_high_issues(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("--as-of", "2026-10-10", "--out", tmp, "--strict")
            self.assertEqual(result.returncode, 1)  # F02 closure is unverified

    def test_committed_reports_are_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run_cli("--as-of", "2026-10-10", "--out", tmp).returncode, 0)
            for name in ("assessment.json", "soa.csv", "risk-register.csv", "management-review.html"):
                with self.subTest(report=name):
                    self.assertEqual((Path(tmp) / name).read_bytes(), (ROOT / "reports" / name).read_bytes(),
                                     f"reports/{name} is stale: run python -m assureledger --as-of 2026-10-10")


if __name__ == "__main__":
    unittest.main()
