"""Deterministic assurance assessment. No network calls or certification score."""
from datetime import date
from pathlib import Path
import hashlib
import json


def _require_fields(item, fields, collection):
    missing = [field for field in fields if field not in item]
    if missing:
        raise ValueError(f"{collection} item is missing: {', '.join(missing)}")


def score(likelihood, impact):
    if any(type(n) is not int or not 1 <= n <= 5 for n in (likelihood, impact)):
        raise ValueError("Likelihood and impact must be integers from 1 to 5")
    return likelihood * impact


def band(value):
    return "critical" if value >= 20 else "high" if value >= 12 else "moderate" if value >= 6 else "low"


def device_quota(payload, maximum=20):
    """Project-specific technical check; not an ISO-mandated numeric limit."""
    value = payload.get("userDeviceQuota")
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
    if hashlib.sha256(path.read_bytes()).hexdigest() != evidence["sha256"]:
        return "integrity_failed"
    collected, expires = date.fromisoformat(evidence["collected"]), date.fromisoformat(evidence["expires"])
    if expires < collected or collected > as_of:
        return "invalid_date"
    if expires < as_of:
        return "expired"
    if evidence["review"] != "accepted":
        return "pending_review"
    return "accepted"


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("Scenario must be a JSON object")
    for collection in ("assets", "risks", "controls", "evidence", "findings"):
        if not isinstance(data.get(collection), list):
            raise ValueError(f"{collection} must be a list")
    for collection in ("assets", "risks", "controls", "evidence", "findings"):
        ids = []
        for item in data[collection]:
            if not isinstance(item, dict):
                raise ValueError(f"{collection} items must be objects")
            _require_fields(item, ("id",), collection)
            ids.append(item["id"])
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate identifiers in {collection}")
    assets = {a["id"] for a in data["assets"]}
    risks = {r["id"] for r in data["risks"]}
    controls = {c["id"] for c in data["controls"]}
    evidence = {e["id"] for e in data["evidence"]}
    for asset in data["assets"]:
        _require_fields(asset, ("name", "owner", "classification"), "assets")
        if not asset["owner"].strip():
            raise ValueError("Asset requires an owner")
    for risk in data["risks"]:
        _require_fields(risk, ("asset", "owner", "likelihood", "impact", "target_likelihood", "target_impact", "controls", "due"), "risks")
        if risk["asset"] not in assets or not risk["owner"].strip():
            raise ValueError("Risk requires an existing asset and owner")
        score(risk["likelihood"], risk["impact"])
        score(risk["target_likelihood"], risk["target_impact"])
        if not set(risk["controls"]) <= controls:
            raise ValueError("Unknown risk control")
        date.fromisoformat(risk["due"])
    for control in data["controls"]:
        _require_fields(control, ("applicability", "implementation", "rationale", "evidence"), "controls")
        if control["applicability"] not in ("included", "excluded", "undecided"):
            raise ValueError("Invalid applicability")
        if control["implementation"] not in ("planned", "partial", "implemented", "not_applicable"):
            raise ValueError("Invalid implementation")
        if control["applicability"] != "undecided" and not control["rationale"].strip():
            raise ValueError("Applicability decisions require a rationale")
        if not set(control["evidence"]) <= evidence:
            raise ValueError("Unknown evidence reference")
    for item in data["evidence"]:
        _require_fields(item, ("path", "sha256", "collected", "expires", "review", "reviewer"), "evidence")
        if not isinstance(item["sha256"], str) or len(item["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in item["sha256"].lower()):
            raise ValueError("Evidence sha256 must be a 64-character hexadecimal digest")
        collected = date.fromisoformat(item["collected"])
        expires = date.fromisoformat(item["expires"])
        if expires < collected:
            raise ValueError("Evidence expiry cannot precede collection")
        if item["review"] not in ("accepted", "pending", "rejected"):
            raise ValueError("Invalid evidence review")
        if item["review"] == "accepted" and not item["reviewer"].strip():
            raise ValueError("Accepted evidence requires a reviewer")
    for finding in data["findings"]:
        _require_fields(finding, ("risk", "control", "status", "closure_evidence", "verified_by", "owner", "due"), "findings")
        if finding["risk"] not in risks or finding["control"] not in controls:
            raise ValueError("Unknown finding relationship")
        if finding["status"] not in ("open", "in_progress", "closed"):
            raise ValueError("Invalid finding status")
        if not set(finding["closure_evidence"]) <= evidence:
            raise ValueError("Unknown closure evidence")
        date.fromisoformat(finding["due"])


def assess(data, root, as_of):
    validate(data)
    evidence = {e["id"]: evidence_status(e, root, as_of) for e in data["evidence"]}
    controls = []
    for c in data["controls"]:
        if c["applicability"] == "excluded":
            status = "excluded"
        elif c["applicability"] == "undecided":
            status = "undecided"
        elif c["implementation"] != "implemented":
            status = "implementation_gap"
        elif not c["evidence"] or any(evidence[e] != "accepted" for e in c["evidence"]):
            status = "evidence_gap"
        else:
            status = "supported_for_review"
        controls.append({**c, "assurance": status})
    risks = [{**r, "inherent": score(r["likelihood"], r["impact"]),
              "target": score(r["target_likelihood"], r["target_impact"]),
              "band": band(score(r["likelihood"], r["impact"]))} for r in data["risks"]]
    findings = []
    for f in data["findings"]:
        valid_closure = bool(f["closure_evidence"]) and all(evidence[e] == "accepted" for e in f["closure_evidence"]) and bool(f["verified_by"].strip()) and f["verified_by"] != f["owner"]
        effective = "closure_unverified" if f["status"] == "closed" and not valid_closure else f["status"]
        findings.append({**f, "effective_status": effective, "overdue": effective != "closed" and date.fromisoformat(f["due"]) < as_of})
    return {"organization": data["organization"], "as_of": as_of.isoformat(),
            "synthetic": True, "evidence": evidence, "controls": controls,
            "risks": risks, "findings": findings}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
