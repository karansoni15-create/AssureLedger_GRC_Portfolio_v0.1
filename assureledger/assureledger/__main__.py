import argparse
import csv
from datetime import date
from html import escape
import json
from pathlib import Path
from .engine import assess, load, device_quota


def main():
    parser = argparse.ArgumentParser(description="AssureLedger synthetic ISMS assessment")
    parser.add_argument("--data", default="data/scenario.json")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--out", default="reports")
    args = parser.parse_args()
    data_path = Path(args.data)
    result = assess(load(data_path), data_path.parent, args.as_of)
    result["technical_check"] = {"device_quota": device_quota(load(data_path.parent / "evidence/device-policy.json")), "scope": "One synthetic configuration snapshot; manual mapping required"}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "assessment.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (out / "soa.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["id", "objective", "applicability", "rationale", "implementation", "owner", "assurance"]
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in result["controls"]:
            writer.writerow({k: ("'" + str(v) if str(v).startswith(("=", "+", "-", "@")) else v) for k, v in row.items()})
    def table(rows, fields):
        return "<table><thead><tr>" + "".join(f"<th>{escape(f.replace('_', ' '))}</th>" for f in fields) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{escape(str(row.get(f, '')))}</td>" for f in fields) + "</tr>" for row in rows) + "</tbody></table>"
    html = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AssureLedger | Management review</title><style>body{font:16px system-ui;background:#f2f5f8;color:#172b42;max-width:1200px;margin:40px auto;padding:24px}h1{font-size:42px}h2{margin-top:36px}table{border-collapse:collapse;background:white;width:100%;font-size:14px}th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd;vertical-align:top}th{background:#183b50;color:white}aside{background:#e3efe9;padding:20px;border-left:5px solid #28765d}.scroll{overflow:auto}small{color:#52657b}</style>"""
    html += f"<header><small>ASSURELEDGER / SYNTHETIC PORTFOLIO</small><h1>Risk &amp; evidence review</h1><p>{escape(result['organization'])} · {result['as_of']}</p></header>"
    html += "<aside>Demonstration only. Evidence support is not certification or verified control effectiveness. Target risk scores are forecasts, not achieved residual risk. The SoA below covers a pilot subset.</aside>"
    html += "<h2>Risk register</h2><div class='scroll'>" + table(result["risks"], ["id", "scenario", "owner", "inherent", "band", "target", "treatment", "due"]) + "</div>"
    html += "<h2>Control assurance</h2><div class='scroll'>" + table(result["controls"], ["id", "objective", "implementation", "assurance", "rationale"]) + "</div>"
    html += "<h2>Corrective actions</h2><div class='scroll'>" + table(result["findings"], ["id", "issue", "owner", "due", "effective_status", "overdue"]) + "</div>"
    html += "<h2>Evidence health</h2>" + table([{"id": k, "status": v} for k,v in result["evidence"].items()], ["id", "status"])
    html += "<p>Technical observation: device quota = " + result["technical_check"]["device_quota"] + ". This project uses a locally selected maximum of 20; ISO does not prescribe that value.</p></html>"
    (out / "management-review.html").write_text(html, encoding="utf-8")
    print(f"Created assessment.json, soa.csv and management-review.html in {out}")


if __name__ == "__main__":
    main()
