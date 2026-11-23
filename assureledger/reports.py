"""Report writers. Reports are derived outputs; the scenario remains the source of truth."""
import csv
from html import escape
import json
from pathlib import Path

# OWASP CSV injection guidance: neutralise cells that a spreadsheet could treat as a formula.
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

SOA_FIELDS = ["id", "theme", "topic", "applicability", "rationale", "implementation", "assurance", "evidence", "owner"]
RISK_FIELDS = ["id", "asset", "scenario", "owner", "likelihood", "impact", "inherent", "band", "treatment_option",
               "treatment", "controls", "treatment_status", "due", "treatment_overdue", "target", "residual",
               "acceptance_status"]


def _cell(value):
    if isinstance(value, list):
        value = "; ".join(str(v) for v in value)
    if value is None:
        return ""
    if isinstance(value, str) and value.startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def write_csv(path, rows, fields):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({f: _cell(row.get(f)) for f in fields})


def _e(value):
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    if value is None:
        value = "—"
    if isinstance(value, bool):
        value = "yes" if value else "no"
    return escape(str(value))


def _table(rows, fields, labels=None):
    labels = labels or {}
    head = "".join(f"<th>{_e(labels.get(f, f.replace('_', ' ')))}</th>" for f in fields)
    body = "".join("<tr>" + "".join(f"<td class='{_e(f)}' data-v='{_e(row.get(f))}'>{_e(row.get(f))}</td>"
                                    for f in fields) + "</tr>" for row in rows)
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def _heatmap(risks):
    cells = {}
    for r in risks:
        cells.setdefault((r["likelihood"], r["impact"]), []).append(r["id"])
    rows = ["<table class='heat' aria-label='Inherent risk heat map'><thead><tr><th>Likelihood \\ Impact</th>"
            + "".join(f"<th>{i}</th>" for i in range(1, 6)) + "</tr></thead><tbody>"]
    for likelihood in range(5, 0, -1):
        rows.append(f"<tr><th>{likelihood}</th>")
        for impact in range(1, 6):
            ids = ", ".join(cells.get((likelihood, impact), []))
            rows.append(f"<td class='b-{_band(likelihood * impact)}'>{_e(ids)}</td>")
        rows.append("</tr>")
    rows.append("</tbody></table>")
    return "".join(rows)


def _band(value):
    return "critical" if value >= 20 else "high" if value >= 12 else "moderate" if value >= 6 else "low"


def _cards(summary):
    s = summary
    cards = [
        ("Open issues (high)", s["issues_by_severity"].get("high", 0)),
        ("Critical / high risks", s["risks_by_band"].get("critical", 0) + s["risks_by_band"].get("high", 0)),
        ("Overdue treatments", s["treatments_overdue"]),
        ("SoA decisions", f"{s['soa_decided']} / {s['soa_rows']}"),
        ("Controls supported for review", s["soa_by_assurance"].get("supported_for_review", 0)),
        ("Findings overdue or unverified", s["findings_needing_attention"]),
    ]
    return "<div class='cards'>" + "".join(
        f"<div class='card'><div class='n'>{_e(v)}</div><div class='l'>{_e(k)}</div></div>" for k, v in cards) + "</div>"


CSS = """body{font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;background:#f4f6f8;color:#172b42;max-width:1240px;margin:0 auto;padding:32px 24px}
h1{font-size:36px;margin:4px 0}h2{margin-top:40px;border-bottom:2px solid #183b50;padding-bottom:4px}
table{border-collapse:collapse;background:#fff;width:100%;font-size:13.5px}th,td{padding:9px 10px;text-align:left;border-bottom:1px solid #dde3ea;vertical-align:top}
thead th{background:#183b50;color:#fff}.scroll{overflow-x:auto}
td.due,td.review_due,td.id,td.ref,td.band,td.severity{white-space:nowrap}
@media print{thead th{position:static}.cards{grid-template-columns:repeat(3,1fr)}}
aside{background:#fff6e0;padding:16px 20px;border-left:5px solid #b7791f;margin:20px 0}small,.muted{color:#52657b}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:20px 0}
.card{background:#fff;border:1px solid #dde3ea;border-radius:8px;padding:14px}.card .n{font-size:28px;font-weight:700}.card .l{color:#52657b;font-size:13px}
.heat{width:auto}.heat td{width:110px;height:44px;text-align:center;font-weight:600}.heat th{text-align:center}
.b-low{background:#e3f2e8}.b-moderate{background:#fff3c4}.b-high{background:#ffd8b5}.b-critical{background:#f7b9b9}
td.severity[data-v=high],td.band[data-v=critical]{color:#9b1c1c;font-weight:700}td.severity[data-v=medium],td.band[data-v=high]{color:#9a5b00;font-weight:600}
td.status[data-v=accepted],td.assurance[data-v=supported_for_review],td.coverage[data-v=supported_for_review],td.acceptance_status[data-v=valid]{color:#1f6f4a;font-weight:600}
footer{margin-top:48px;font-size:13px;color:#52657b}"""


def write_html(path, result):
    s = result["summary"]
    decided = [row for row in result["soa"] if row["applicability"] != "undecided"]
    criteria = result["risk_criteria"]
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>AssureLedger | Management review</title>",
        f"<style>{CSS}</style></head><body>",
        f"<header><small>ASSURELEDGER · SYNTHETIC PORTFOLIO · SCHEMA {_e(result['schema_version'])}</small>",
        f"<h1>Risk &amp; assurance review</h1><p>{_e(result['organization'])} · assessed as of {_e(result['as_of'])}</p></header>",
        "<aside>Demonstration with fictional data. Evidence marked <em>supported for review</em> is not proof of control "
        "effectiveness and nothing here is an ISO certification opinion. Target scores are forecasts; residual scores are "
        "recorded only where a risk owner has reassessed the risk.</aside>",
        "<h2>Executive summary</h2>", _cards(s),
        "<h2>Issues requiring attention</h2>",
        _table(result["issues"], ["severity", "type", "ref", "message"]) if result["issues"] else "<p>No issues.</p>",
        "<h2>Inherent risk heat map</h2>", _heatmap(result["risks"]),
        f"<p class='muted'>Acceptance authority: risk owner up to residual {criteria['owner_acceptance_max']}; "
        f"{_e(criteria['management_role'])} up to {criteria['management_acceptance_max']}; above that, treat or escalate.</p>",
        "<h2>Risk register and treatment plan</h2>",
        _table(result["risks"], ["id", "scenario", "owner", "inherent", "band", "treatment_option", "treatment",
                                 "controls", "treatment_status", "due", "treatment_overdue", "target", "residual",
                                 "acceptance_status"]),
        f"<h2>Statement of Applicability — {s['soa_decided']} of {s['soa_rows']} decided</h2>",
        "<p class='muted'>Only decided rows are shown. The full SoA, including every undecided Annex A reference, is in "
        "<code>soa.csv</code>. Topic labels are project paraphrases, not ISO control text.</p>",
        _table(decided, ["id", "topic", "applicability", "implementation", "assurance", "evidence", "rationale"]),
        "<h2>Obligations register</h2>",
        _table(result["obligations"], ["id", "source", "summary", "applicability", "basis", "owner", "controls",
                                       "coverage", "review_due"]),
        "<h2>Corrective actions</h2>",
        _table(result["findings"], ["id", "issue", "risk", "control", "owner", "due", "status", "effective_status",
                                    "overdue"], {"status": "recorded status"}),
        "<h2>Evidence health</h2>",
        _table(result["evidence_register"], ["id", "path", "quality", "collected", "expires", "review", "reviewer", "status"]),
        f"<p>Technical observation: device registration quota = <strong>{_e(result['technical_check']['device_quota'])}</strong>. "
        "The threshold of 20 is a project choice; ISO/IEC 27001 does not prescribe it.</p>",
        "<footer>Generated by AssureLedger from data/scenario.json. Regenerate rather than edit this file.</footer>",
        "</body></html>\n",
    ]
    Path(path).write_text("".join(parts), encoding="utf-8", newline="\n")


def write_all(out, result):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "assessment.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    write_csv(out / "soa.csv", result["soa"], SOA_FIELDS)
    write_csv(out / "risk-register.csv", result["risks"], RISK_FIELDS)
    write_html(out / "management-review.html", result)
    return ["assessment.json", "soa.csv", "risk-register.csv", "management-review.html"]
