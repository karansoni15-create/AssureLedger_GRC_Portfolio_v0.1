# AssureLedger

**Trace a technical observation to a business risk, an accountable owner and an auditable decision.**

An ISO/IEC 27001:2022-oriented GRC portfolio by Karan Soni, developed with AI assistance. Version 0.1 is a tested, offline Python workbench using a fictional Australian SaaS company. It extends the *idea* behind Karan's AutoAudit contributions into governance workflows. No Hardhat code or private organizational data is reused.

## Start in two minutes
Requires Python 3.11+ (CI also verifies Python 3.14); no runtime dependencies, credentials, cloud subscription or paid platform.

```sh
python -m unittest discover -s tests -v
python -m assureledger --as-of 2026-10-10
```

For an editable local install, run `python -m pip install --editable .`. The optional device-policy snapshot is reported as `unknown` when it is absent; the evidence records referenced by the scenario remain required and are validated before assessment.

Open `reports/management-review.html` locally. On Windows, run `start reports\management-review.html`. Review the machine-readable `reports/assessment.json` and spreadsheet-friendly `reports/soa.csv`. Run commands from this repository root. Omit `--as-of` to evaluate freshness on the current local date.

## What the release demonstrates
- Five linked business risks, three information assets, twelve pilot control decisions.
- Four synthetic evidence records with checksums, scope, review and expiry.
- Three corrective actions, including an intentionally invalid closure.
- Technical device-quota observation with explicit `pass`, `fail`, `unknown` semantics.
- Deterministic JSON, CSV and escaped HTML reports; GitHub Actions test matrix.
- Scope, methodology, supplier assessment, internal audit and management-review working papers.

The demo deliberately contains gaps. The quota snapshot fails the selected threshold; restore evidence is expired; the engine reopens assurance attention on an unverified closure. A green dashboard would conceal the most useful GRC learning.

## Read the case study
1. [Research and design decisions](docs/RESEARCH.md)
2. [ISMS scope and responsibilities](docs/ISMS-SCOPE.md)
3. [Risk methodology](docs/RISK-METHODOLOGY.md)
4. [Audit and management-review pack](docs/AUDIT-PACK.md)
5. [Architecture and limitations](docs/ARCHITECTURE.md)
6. [Delivery roadmap](docs/ROADMAP.md)
7. [Recruiter demonstration](docs/DEMO.md)
8. [GitHub connection and publication](docs/GITHUB.md)

## Honest boundary
This is an industry-informed portfolio MVP, not production software or an ISO-certified ISMS. The pilot SoA is **not the complete Annex A review**. Objectives are original project paraphrases, not licensed ISO control text. Full implementation requires access to the licensed standard, review of all applicable requirements, organizational decisions and independent assurance. No percentage in this project means ISO compliance. Evidence acceptance is a simulated human decision; hashes detect changed bytes but cannot prove authenticity.

## Contribution
Change a fixture, add a test explaining the assurance consequence, run the test suite and regenerate reports. Use a branch and pull request. See SECURITY.md before adding evidence. Roadmap work must be labelled planned until implemented and verified.
