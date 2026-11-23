# Delivery roadmap
Updated 23 November 2026. Dates are proposed milestones, not commitments or scheduled automation.

## Done
| Date | Release | Evidence |
|---|---|---|
| 10 October 2026 | v0.1 offline pilot and working papers | First public commit |
| 23 November 2026 | v0.2 industry upgrade: 93-row SoA, treatment options, acceptance authority, obligations register, issue list, CI that actually runs, reproducibility check | 57 tests; see [VALIDATION.md](VALIDATION.md) and [CHANGELOG](../CHANGELOG.md) |

## Next
| Target | Deliverable | Acceptance evidence |
|---|---|---|
| 7 December 2026 | Karan reviews every risk, score and SoA decision and records his own rationale in a pull request | Can explain R03, R06, F02 and OB02 without notes |
| 21 December 2026 | Decide the remaining 74 Annex A references using the licensed standard (university library access) | `soa_incomplete` issue disappears; every exclusion justified |
| 18 January 2027 | Map selected controls to *ASD Essentials for enterprise IT* after reading the chapter and ASD's transition guide | Mapping labelled as project judgement; no maturity or effectiveness claim |
| 1 February 2027 | Supplier assessment and internal audit cycle as data (sampling, findings, retest) | Audit records validated like findings; verified retest closes a finding |
| February 2027 | Portfolio release with a recorded 8-minute demonstration | Reproducible setup; limitations reviewed |
| February–March 2027 | Internship and graduate applications | Link project to role requirements; explain work-rights eligibility accurately |

## Backlog
- **P1:** decision history (who changed a score and why); evidence metadata schema with scope and population; clause 4–10 requirement tracker.
- **P2:** read-only connector to an authorised lab tenant or sanitised AutoAudit export, after a threat model.
- **P3:** database, API and authenticated UI only after an explicit threat model; AI supplier risk extension (do not claim ISO/IEC 42001 coverage from an ISO 27001 mapping).

## Definition of done for a feature
A business need, an observable decision consequence, tests for incorrect or missing evidence, documented limitations, reproducible reports and no sensitive data in the repository. Approvals in fixtures are labelled simulated; the code must never generate an approval.
