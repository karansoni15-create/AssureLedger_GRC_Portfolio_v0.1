# Changelog

## 0.2.0 — 23 November 2026
### Added
- Statement of Applicability covering all 93 ISO/IEC 27001:2022 Annex A references (paraphrased topic labels), with "undecided" rows and an `soa_incomplete` issue until every reference has a decision. Organisation-specific controls supported with `"source": "additional"`.
- Structured risk treatment: ISO/IEC 27005 options (`modify`, `retain`, `avoid`, `share`), treatment status, overdue detection, owner-assessed residual score.
- Residual-risk acceptance with authority limits (`risk_criteria`), expiry and decision records; new retained risk R06.
- Australian obligations register: Privacy Act APP 11, Notifiable Data Breaches scheme, Cyber Security Act 2024 ransomware payment reporting, and a synthetic customer contract clause, with coverage checks.
- Seven further SoA decisions (A.5.5, A.5.24, A.5.26, A.5.31, A.5.34, A.5.37, A.8.5) supporting the obligations and R06.
- Prioritised issue list and summary; HTML executive summary, heat map, obligations and evidence register; `risk-register.csv`.
- `--strict` (exit 1 on high-severity issues), `--version` and an `assureledger` console command.
- Windows CI job, Dependabot for GitHub Actions, report artefact upload, `.gitattributes`.
### Fixed
- Project was nested in a sub-folder, so GitHub never ran the CI workflow and showed no README.
- Rejected evidence was reported as `pending_review`.
- CSV formula guard did not cover cells starting with tab or carriage return.
- Malformed input crashed with a traceback; now exits 2 with a `Scenario error` message.
- Reports written on Windows used CRLF line endings and differed from Linux output.
- Risks could rely on controls that the SoA excluded without any warning.
### Changed
- Scenario `schema_version` "0.2" is required. Free-text risk `acceptance` replaced by a structured record.
- Package split into `schema.py`, `engine.py` and `reports.py`.
- Removed stale `docs/GITHUB.md`.

## 0.1.0 — 10 October 2026
- Initial offline pilot: five risks, twelve control decisions, four evidence records, three findings, JSON/CSV/HTML reports.
