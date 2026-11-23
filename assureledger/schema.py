"""Scenario validation.

Every rule here exists because a broken record would produce a misleading
assurance conclusion. Errors are raised as ScenarioError so the CLI can report
them cleanly instead of printing a Python traceback.
"""
from datetime import date

SCHEMA_VERSION = "0.2"
COLLECTIONS = ("assets", "risks", "controls", "evidence", "findings", "obligations")
APPLICABILITY = ("included", "excluded", "undecided")
IMPLEMENTATION = ("planned", "partial", "implemented", "not_applicable")
EVIDENCE_REVIEW = ("accepted", "pending", "rejected")
FINDING_STATUS = ("open", "in_progress", "closed")
# ISO/IEC 27005:2022 treatment options.
TREATMENT_OPTIONS = ("modify", "retain", "avoid", "share")
TREATMENT_STATUS = ("not_started", "in_progress", "complete")
ACCEPTANCE_STATUS = ("not_requested", "accepted", "rejected")
OBLIGATION_APPLICABILITY = ("applicable", "assumed_applicable", "not_applicable")


class ScenarioError(ValueError):
    """Raised when the scenario cannot support a trustworthy assessment."""


def _where(collection, item):
    if "[" in collection:  # already a full path such as risks[R01].acceptance
        return collection
    ident = item.get("id", "?") if isinstance(item, dict) else "?"
    return f"{collection}[{ident}]"


def _require(item, fields, collection):
    missing = [f for f in fields if f not in item]
    if missing:
        raise ScenarioError(f"{_where(collection, item)} is missing: {', '.join(missing)}")


def _text(item, field, collection, *, required=True):
    value = item.get(field)
    if not isinstance(value, str):
        raise ScenarioError(f"{_where(collection, item)}.{field} must be text")
    if required and not value.strip():
        raise ScenarioError(f"{_where(collection, item)}.{field} must not be empty")
    return value


def _ids(item, field, collection):
    value = item.get(field)
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ScenarioError(f"{_where(collection, item)}.{field} must be a list of identifiers")
    if len(value) != len(set(value)):
        raise ScenarioError(f"{_where(collection, item)}.{field} contains duplicates")
    return value


def _date(item, field, collection, *, optional=False):
    value = item.get(field)
    if optional and value is None:
        return None
    if not isinstance(value, str):
        raise ScenarioError(f"{_where(collection, item)}.{field} must be an ISO date (YYYY-MM-DD)")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ScenarioError(f"{_where(collection, item)}.{field} is not a valid date: {value!r}") from exc


def _choice(item, field, options, collection):
    if item.get(field) not in options:
        raise ScenarioError(f"{_where(collection, item)}.{field} must be one of: {', '.join(options)}")


def _ordinal(item, field, collection, *, optional=False):
    value = item.get(field)
    if optional and value is None:
        return None
    if type(value) is not int or not 1 <= value <= 5:
        raise ScenarioError(f"{_where(collection, item)}.{field} must be an integer from 1 to 5")
    return value


def validate(data, catalog_ids):
    """Validate structure, types and cross-references. Returns None or raises ScenarioError."""
    if not isinstance(data, dict):
        raise ScenarioError("Scenario must be a JSON object")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ScenarioError(f"schema_version must be {SCHEMA_VERSION!r}")
    if not isinstance(data.get("organization"), str) or not data["organization"].strip():
        raise ScenarioError("organization must be non-empty text")

    criteria = data.get("risk_criteria")
    if not isinstance(criteria, dict):
        raise ScenarioError("risk_criteria must be an object")
    for field in ("owner_acceptance_max", "management_acceptance_max"):
        if type(criteria.get(field)) is not int or not 1 <= criteria[field] <= 25:
            raise ScenarioError(f"risk_criteria.{field} must be an integer from 1 to 25")
    if criteria["owner_acceptance_max"] > criteria["management_acceptance_max"]:
        raise ScenarioError("risk_criteria: owner limit cannot exceed management limit")
    _text(criteria, "management_role", "risk_criteria")

    for collection in COLLECTIONS:
        if not isinstance(data.get(collection), list):
            raise ScenarioError(f"{collection} must be a list")
        seen = set()
        for item in data[collection]:
            if not isinstance(item, dict):
                raise ScenarioError(f"{collection} items must be objects")
            _require(item, ("id",), collection)
            ident = _text(item, "id", collection)
            if ident in seen:
                raise ScenarioError(f"Duplicate identifier {ident!r} in {collection}")
            seen.add(ident)

    assets = {a["id"] for a in data["assets"]}
    risks = {r["id"] for r in data["risks"]}
    controls = {c["id"] for c in data["controls"]}
    evidence = {e["id"] for e in data["evidence"]}

    for asset in data["assets"]:
        _require(asset, ("name", "owner", "classification"), "assets")
        for field in ("name", "owner", "classification"):
            _text(asset, field, "assets")

    for control in data["controls"]:
        _require(control, ("objective", "applicability", "implementation", "rationale", "evidence", "owner"), "controls")
        if control["id"] not in catalog_ids and control.get("source") != "additional":
            raise ScenarioError(
                f"controls[{control['id']}] is not an ISO/IEC 27001:2022 Annex A identifier; "
                "mark organisation-specific controls with \"source\": \"additional\"")
        _text(control, "objective", "controls")
        _text(control, "owner", "controls")
        _choice(control, "applicability", APPLICABILITY, "controls")
        _choice(control, "implementation", IMPLEMENTATION, "controls")
        _text(control, "rationale", "controls", required=control["applicability"] != "undecided")
        if control["applicability"] == "excluded" and control["implementation"] != "not_applicable":
            raise ScenarioError(f"controls[{control['id']}] is excluded, so implementation must be not_applicable")
        if control["applicability"] == "included" and control["implementation"] == "not_applicable":
            raise ScenarioError(f"controls[{control['id']}] is included, so implementation cannot be not_applicable")
        if not set(_ids(control, "evidence", "controls")) <= evidence:
            raise ScenarioError(f"controls[{control['id']}] references unknown evidence")

    for item in data["evidence"]:
        _require(item, ("path", "sha256", "collected", "expires", "review", "reviewer"), "evidence")
        _text(item, "path", "evidence")
        digest = _text(item, "sha256", "evidence")
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest.lower()):
            raise ScenarioError(f"evidence[{item['id']}].sha256 must be a 64-character hexadecimal digest")
        if _date(item, "expires", "evidence") < _date(item, "collected", "evidence"):
            raise ScenarioError(f"evidence[{item['id']}] expiry cannot precede collection")
        _choice(item, "review", EVIDENCE_REVIEW, "evidence")
        _text(item, "reviewer", "evidence", required=item["review"] != "pending")

    for risk in data["risks"]:
        _require(risk, ("asset", "scenario", "owner", "likelihood", "impact", "target_likelihood",
                        "target_impact", "controls", "treatment", "treatment_option",
                        "treatment_status", "due", "residual_likelihood", "residual_impact",
                        "acceptance"), "risks")
        if risk["asset"] not in assets:
            raise ScenarioError(f"risks[{risk['id']}] references unknown asset {risk['asset']!r}")
        for field in ("scenario", "owner", "treatment"):
            _text(risk, field, "risks")
        for field in ("likelihood", "impact", "target_likelihood", "target_impact"):
            _ordinal(risk, field, "risks")
        residual = [_ordinal(risk, f, "risks", optional=True) for f in ("residual_likelihood", "residual_impact")]
        if (residual[0] is None) != (residual[1] is None):
            raise ScenarioError(f"risks[{risk['id']}] needs both residual values or neither")
        _choice(risk, "treatment_option", TREATMENT_OPTIONS, "risks")
        _choice(risk, "treatment_status", TREATMENT_STATUS, "risks")
        if not set(_ids(risk, "controls", "risks")) <= controls:
            raise ScenarioError(f"risks[{risk['id']}] references a control with no SoA decision")
        if risk["treatment_option"] == "modify" and not risk["controls"]:
            raise ScenarioError(f"risks[{risk['id']}] modifies the risk but selects no controls")
        _date(risk, "due", "risks")
        acceptance = risk["acceptance"]
        if not isinstance(acceptance, dict):
            raise ScenarioError(f"risks[{risk['id']}].acceptance must be an object")
        where = f"risks[{risk['id']}].acceptance"
        _require(acceptance, ("status", "decided_by", "decided_on", "expires", "rationale"), where)
        _choice(acceptance, "status", ACCEPTANCE_STATUS, where)
        decided = acceptance["status"] != "not_requested"
        _text(acceptance, "decided_by", where, required=decided)
        _text(acceptance, "rationale", where, required=decided)
        decided_on = _date(acceptance, "decided_on", where, optional=not decided)
        expires = _date(acceptance, "expires", where, optional=acceptance["status"] != "accepted")
        if decided_on and expires and expires < decided_on:
            raise ScenarioError(f"{where} expiry cannot precede the decision")

    for finding in data["findings"]:
        _require(finding, ("risk", "control", "issue", "status", "closure_evidence", "verified_by", "owner", "due"), "findings")
        if finding["risk"] not in risks or finding["control"] not in controls:
            raise ScenarioError(f"findings[{finding['id']}] references an unknown risk or control")
        _text(finding, "issue", "findings")
        _text(finding, "owner", "findings")
        _text(finding, "verified_by", "findings", required=False)
        _choice(finding, "status", FINDING_STATUS, "findings")
        if not set(_ids(finding, "closure_evidence", "findings")) <= evidence:
            raise ScenarioError(f"findings[{finding['id']}] references unknown closure evidence")
        _date(finding, "due", "findings")

    for obligation in data["obligations"]:
        _require(obligation, ("source", "summary", "applicability", "basis", "owner", "controls", "review_due"), "obligations")
        for field in ("source", "summary", "basis", "owner"):
            _text(obligation, field, "obligations")
        _choice(obligation, "applicability", OBLIGATION_APPLICABILITY, "obligations")
        if not set(_ids(obligation, "controls", "obligations")) <= controls:
            raise ScenarioError(f"obligations[{obligation['id']}] references a control with no SoA decision")
        _date(obligation, "review_due", "obligations")
