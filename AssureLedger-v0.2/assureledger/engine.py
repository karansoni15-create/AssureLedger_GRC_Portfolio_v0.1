"""Deterministic assurance assessment.

No network calls, no certification score. Every conclusion is derived from the
scenario, the evidence files and an explicit assessment date, so the same
inputs always give the same reports.
"""
from datetime import date
from importlib import resources
from pathlib import Path
import hashlib
import json

from .schema import ScenarioError, validate

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScenarioError(f"{path} is not valid JSON: {exc}") from exc


def load_catalog():
    text = resources.files("assureledger").joinpath("annex_a_2022.json").read_text(encoding="utf-8")
    return json.loads(text)["controls"]


def score(likelihood, impact):
    if any(type(n) is not int or not 1 <= n <= 5 for n in (likelihood, impact)):
        raise ValueError("Likelihood and impact must be integers from 1 to 5")
    return likelihood * impact


def band(value):
    return "critical" if value >= 20 else "high" if value >= 12 else "moderate" if value >= 6 else "low"


def device_quota(payload, maximum=20):
    """Project-specific technical check; not an ISO-mandated numeric limit."""
    value = payload.get("userDeviceQuota") if isinstance(payload, dict) else None
    if type(value) is not int or value < 0:
        return "unknown"
    return "pass" if value <= maximum else "fail"


def evidence_status(evidence, root, as_of):
    root = Path(root).resolve()
    path = (root / evidence["path"]).resolve()
    if not path.is_relative_to(root):
        return "unsafe_path"
    if not path.is_file():
        return "missing"
    if hashlib.sha256(path.read_bytes()).hexdigest() != evidence["sha256"].lower():
        return "integrity_failed"
    collected, expires = date.fromisoformat(evidence["collected"]), date.fromisoformat(evidence["expires"])
    if expires < collected or collected > as_of:
        return "invalid_date"
    if evidence["review"] == "rejected":
        return "rejected"
    if expires < as_of:
        return "expired"
    if evidence["review"] != "accepted":
        return "pending_review"
    return "accepted"


def control_assurance(control, evidence):
    if control["applicability"] in ("excluded", "undecided"):
        return control["applicability"]
    if control["implementation"] != "implemented":
        return "implementation_gap"
    if not control["evidence"] or any(evidence[e] != "accepted" for e in control["evidence"]):
        return "evidence_gap"
    return "supported_for_review"


def acceptance_status(risk, criteria, as_of):
    """Is a recorded residual-risk acceptance usable on the assessment date?"""
    acceptance = risk["acceptance"]
    if acceptance["status"] != "accepted":
        return acceptance["status"]
    if risk["residual_likelihood"] is None:
        return "missing_residual"
    residual = score(risk["residual_likelihood"], risk["residual_impact"])
    decided_on = date.fromisoformat(acceptance["decided_on"])
    if decided_on > as_of:
        return "invalid_date"
    if date.fromisoformat(acceptance["expires"]) < as_of:
        return "expired"
    by = acceptance["decided_by"]
    if by == risk["owner"] and residual <= criteria["owner_acceptance_max"]:
        return "valid"
    if by == criteria["management_role"] and residual <= criteria["management_acceptance_max"]:
        return "valid"
    return "exceeds_authority"


def _issue(issues, severity, kind, ref, message):
    issues.append({"severity": severity, "type": kind, "ref": ref, "message": message})


def assess(data, root, as_of, catalog=None):
    catalog = load_catalog() if catalog is None else catalog
    catalog_ids = {c["id"] for c in catalog}
    validate(data, catalog_ids)
    criteria = data["risk_criteria"]
    issues = []

    evidence = {e["id"]: evidence_status(e, root, as_of) for e in data["evidence"]}
    for ident, status in evidence.items():
        if status in ("integrity_failed", "unsafe_path", "missing", "invalid_date"):
            _issue(issues, "high", "evidence_" + status, ident, f"Evidence {ident} cannot be relied on: {status}")
        elif status in ("expired", "rejected"):
            _issue(issues, "medium", "evidence_" + status, ident, f"Evidence {ident} is {status}")

    controls = [{**c, "assurance": control_assurance(c, evidence)} for c in data["controls"]]
    by_control = {c["id"]: c for c in controls}

    # Statement of Applicability: one row for every Annex A control plus any additional controls.
    soa = []
    for ref in catalog:
        decided = by_control.get(ref["id"])
        if decided:
            soa.append({**decided, "theme": ref["theme"], "topic": ref["topic"], "source": "annex_a"})
        else:
            soa.append({"id": ref["id"], "theme": ref["theme"], "topic": ref["topic"], "source": "annex_a",
                        "objective": "", "applicability": "undecided", "implementation": "", "rationale": "",
                        "evidence": [], "owner": "", "assurance": "undecided"})
    soa += [{**c, "theme": "additional", "topic": c["objective"]} for c in controls if c["id"] not in catalog_ids]
    undecided = sum(1 for row in soa if row["applicability"] == "undecided")
    if undecided:
        _issue(issues, "medium", "soa_incomplete", "SoA",
               f"{undecided} of {len(soa)} controls have no applicability decision; the SoA is not complete")

    risks = []
    for r in data["risks"]:
        inherent = score(r["likelihood"], r["impact"])
        residual = None if r["residual_likelihood"] is None else score(r["residual_likelihood"], r["residual_impact"])
        accepted = acceptance_status(r, criteria, as_of)
        overdue = r["treatment_status"] != "complete" and date.fromisoformat(r["due"]) < as_of
        conflicts = [c for c in r["controls"] if by_control[c]["applicability"] != "included"]
        risks.append({**r, "inherent": inherent, "band": band(inherent),
                      "target": score(r["target_likelihood"], r["target_impact"]),
                      "residual": residual, "acceptance_status": accepted,
                      "treatment_overdue": overdue, "soa_conflicts": conflicts})
        if conflicts:
            _issue(issues, "high", "soa_conflict", r["id"],
                   f"Risk {r['id']} relies on {', '.join(conflicts)}, which the SoA does not include")
        if overdue:
            _issue(issues, "high" if inherent >= 12 else "medium", "treatment_overdue", r["id"],
                   f"Treatment for {r['id']} was due {r['due']} and is {r['treatment_status']}")
        if accepted in ("expired", "exceeds_authority", "missing_residual", "invalid_date"):
            _issue(issues, "high", "acceptance_" + accepted, r["id"],
                   f"Residual-risk acceptance for {r['id']} is not usable: {accepted}")
        if r["treatment_option"] == "retain" and accepted != "valid":
            _issue(issues, "high", "retained_without_acceptance", r["id"],
                   f"Risk {r['id']} is retained without a valid acceptance decision")

    findings = []
    for f in data["findings"]:
        valid_closure = (bool(f["closure_evidence"]) and all(evidence[e] == "accepted" for e in f["closure_evidence"])
                         and bool(f["verified_by"].strip()) and f["verified_by"] != f["owner"])
        effective = "closure_unverified" if f["status"] == "closed" and not valid_closure else f["status"]
        overdue = effective != "closed" and date.fromisoformat(f["due"]) < as_of
        findings.append({**f, "effective_status": effective, "overdue": overdue})
        if effective == "closure_unverified":
            _issue(issues, "high", "closure_unverified", f["id"],
                   f"Finding {f['id']} is recorded as closed without current, independently verified evidence")
        elif overdue:
            _issue(issues, "medium", "finding_overdue", f["id"], f"Finding {f['id']} was due {f['due']}")

    obligations = []
    for o in data["obligations"]:
        linked = [by_control[c] for c in o["controls"]]
        if o["applicability"] == "not_applicable":
            coverage = "not_applicable"
        elif any(c["applicability"] != "included" for c in linked):
            coverage = "soa_conflict"
        elif linked and all(c["assurance"] == "supported_for_review" for c in linked):
            coverage = "supported_for_review"
        else:
            coverage = "gap"
        review_overdue = date.fromisoformat(o["review_due"]) < as_of
        obligations.append({**o, "coverage": coverage, "review_overdue": review_overdue})
        if coverage == "soa_conflict":
            _issue(issues, "high", "obligation_soa_conflict", o["id"],
                   f"Obligation {o['id']} relies on a control the SoA does not include")
        elif coverage == "gap":
            _issue(issues, "medium", "obligation_gap", o["id"],
                   f"Obligation {o['id']} ({o['source']}) has linked controls without supporting evidence")
        if review_overdue:
            _issue(issues, "medium", "obligation_review_overdue", o["id"], f"Obligation {o['id']} review was due {o['review_due']}")

    issues.sort(key=lambda i: (SEVERITY_ORDER[i["severity"]], i["type"], i["ref"]))

    def count(rows, key):
        out = {}
        for row in rows:
            out[row[key]] = out.get(row[key], 0) + 1
        return dict(sorted(out.items()))

    summary = {
        "risks_by_band": count(risks, "band"),
        "treatments_overdue": sum(r["treatment_overdue"] for r in risks),
        "soa_rows": len(soa),
        "soa_decided": len(soa) - undecided,
        "soa_by_assurance": count(soa, "assurance"),
        "evidence_by_status": count([{"s": s} for s in evidence.values()], "s"),
        "findings_by_status": count(findings, "effective_status"),
        "findings_overdue": sum(f["overdue"] for f in findings),
        "findings_needing_attention": sum(f["overdue"] or f["effective_status"] == "closure_unverified" for f in findings),
        "obligations_by_coverage": count(obligations, "coverage"),
        "issues_by_severity": count(issues, "severity"),
    }
    return {"organization": data["organization"], "as_of": as_of.isoformat(), "synthetic": True,
            "schema_version": data["schema_version"], "risk_criteria": criteria, "summary": summary,
            "issues": issues, "evidence": evidence, "controls": controls, "soa": soa, "risks": risks,
            "findings": findings, "obligations": obligations,
            "evidence_register": [{"id": e["id"], "path": e["path"], "quality": e.get("quality", ""),
                                   "collected": e["collected"], "expires": e["expires"], "review": e["review"],
                                   "reviewer": e["reviewer"], "status": evidence[e["id"]]} for e in data["evidence"]]}
