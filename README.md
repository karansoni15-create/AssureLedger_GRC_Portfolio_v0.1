# AssureLedger

[![assurance-tests](https://github.com/karansoni15-create/AssureLedger_GRC_Portfolio_v0.1/actions/workflows/ci.yml/badge.svg)](https://github.com/karansoni15-create/AssureLedger_GRC_Portfolio_v0.1/actions/workflows/ci.yml)

**Trace a technical observation to a business risk, an accountable owner, an applicability decision and an auditable conclusion.**

AssureLedger is an ISO/IEC 27001:2022-oriented GRC portfolio project by Karan Soni, developed with AI assistance. It is an offline, tested Python workbench that runs an information security risk and assurance cycle for **HarbourCloud Services**, a fictional 45-person Australian SaaS company. No real organisation's data is used.

It answers the questions a GRC analyst, internal auditor or certification auditor actually asks:

| Question | Where the answer comes from |
|---|---|
| Which risks matter, who owns them and how are they being treated? | Risk register and treatment plan (ISO/IEC 27005 options: modify, retain, avoid, share) |
| Has anyone with the right authority accepted the residual risk, and is that decision still current? | Acceptance checks against documented authority limits and expiry dates |
| Has every Annex A control been considered, and is every inclusion and exclusion justified? | 93-row Statement of Applicability with coverage reporting |
| Does the evidence actually support the control right now? | Evidence integrity (SHA-256), freshness, review and scope checks |
| Is a "closed" finding really closed? | Closure requires current accepted evidence and a verifier independent of the owner |
| Which Australian obligations apply, and are the controls behind them supported? | Obligations register: Privacy Act APP 11, Notifiable Data Breaches scheme, Cyber Security Act 2024 ransomware payment reporting, customer contract |

## Run it in two minutes
Requires Python 3.11 or later. There are no third-party runtime dependencies, credentials or cloud subscriptions.

```sh
python -m unittest discover -s tests -v
python -m assureledger --as-of 2026-10-10
```

Optional: `python -m pip install .` then run `assureledger --as-of 2026-10-10`. Add `--strict` to exit with status 1 when any high-severity issue is found, so the assessment can act as a CI gate.

Outputs in `reports/`:

| File | Audience |
|---|---|
| `management-review.html` | Management review: executive summary, issues, heat map, register, SoA, obligations, actions, evidence |
| `soa.csv` | Statement of Applicability, all 93 Annex A references |
| `risk-register.csv` | Risk register and treatment plan for spreadsheet users |
| `assessment.json` | Machine-readable result for other tools |

On Windows, open the report with `start reports\management-review.html`.

## What the 10 October 2026 assessment shows
The demo deliberately contains gaps, because a green dashboard would hide the most useful GRC learning.

- **SoA 19 of 93 decided.** The remaining 74 Annex A references are listed as undecided and the tool refuses to call the SoA complete.
- **Finding F02 reopened.** It was recorded as closed using restore evidence that had expired, so the engine reports `closure_unverified`.
- **One critical risk (R03)** with an untested restore. Its target score is a forecast, not an achieved residual.
- **One retained risk (R06)** with a valid acceptance. The residual score of 9 is above the owner's limit of 8, so the decision is recorded by the (simulated) managing director.
- **Four obligations show a gap**, because none of their linked controls yet has accepted, current evidence.
- **Device quota check fails** a project-selected threshold. It is a technical observation, not an ISO verdict.

## Repository map
```
assureledger/      engine.py (assessment), schema.py (validation), reports.py, annex_a_2022.json (93 references)
data/              scenario.json (source of truth) and synthetic evidence files
docs/              working papers and case study
reports/           generated outputs, verified byte-for-byte by the test suite
tests/             57 unit and end-to-end tests
```

## Read the case study
1. [Research and design decisions](docs/RESEARCH.md)
2. [ISMS scope and responsibilities](docs/ISMS-SCOPE.md)
3. [Risk methodology and acceptance criteria](docs/RISK-METHODOLOGY.md)
4. [Audit, obligations and management-review pack](docs/AUDIT-PACK.md)
5. [Architecture and limitations](docs/ARCHITECTURE.md)
6. [Delivery roadmap](docs/ROADMAP.md)
7. [Recruiter demonstration and interview preparation](docs/DEMO.md)
8. [Validation record](docs/VALIDATION.md) and [changelog](CHANGELOG.md)

## Honest boundary
This is an industry-informed portfolio project, not production software or a certified ISMS. The SoA is **not** complete: 74 references have no decision yet. Topic labels and objectives are original paraphrases, not licensed ISO text. Obligation applicability is **assumed** for the exercise and would need legal confirmation. No percentage in this project means ISO compliance. Owners, reviewers and approvers are simulated labels, not authenticated people. SHA-256 hashes detect changed bytes but cannot prove who created a file or whether it is true.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Read [SECURITY.md](SECURITY.md) before adding any evidence.
