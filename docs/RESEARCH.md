# Research brief and design decisions
Original research: 10 October 2026. Refreshed: 23 November 2026 (Australia/Sydney) for v0.2.

Job advertisements are qualitative examples of what employers ask for, not a representative demand study and not a claim about eligibility for any role.

## Decision
Build a risk-to-evidence assurance workbench for a fictional SaaS business that uses Microsoft 365 and Azure. Focus on analyst work: define scope, assess exposure, choose a treatment, record applicability, judge evidence, track obligations, report exceptions and verify corrective action. Keep it offline so a recruiter can reproduce it without tenant permissions.

## What employers ask for (November 2026 refresh)
Melbourne GRC advertisements reviewed for v0.2 repeat the same responsibilities:

- maintaining a risk register and tracking treatment plans and remediation;
- ISO 27001 audit readiness and supporting an ISMS;
- third-party and supplier risk assessments;
- monitoring compliance with ISO 27001 alongside ASD frameworks (the Essential Eight and the ISM), and tracking regulatory obligations such as the Privacy Act and SOCI.

**Design consequence:** v0.2 adds a structured treatment plan, residual-risk acceptance, an obligations register and spreadsheet-friendly outputs. These are the artefacts a junior analyst is asked to maintain.

## Standards and regulatory findings
| Source | Finding | Design consequence |
|---|---|---|
| ISO/IEC 27001:2022 clause 6.1.3 (as described by ISO-focused training and auditor sources; licensed text not reproduced) | The SoA must contain the necessary controls, why each is included, whether it is implemented, and why any Annex A control is excluded. Risk owners approve the treatment plan and accept residual risk. | The SoA now has a row for all 93 Annex A references with explicit "undecided" status. Risks carry a structured acceptance record checked against authority limits. |
| ISO/IEC 27005:2022 | Treatment options are modification, retention, avoidance and sharing | `treatment_option` uses these four values. A retained risk must have a valid acceptance. |
| [ISO amendment 2024](https://www.iso.org/standard/88435.html) | Climate change must be considered when determining relevant issues and interested-party needs | Kept in the ISMS scope working paper |
| [ASD Essentials (published 15 October 2026)](https://www.cyber.gov.au/essentials) | ASD has evolved the Essential Eight into the ASD Essentials series. *Essentials for enterprise IT* is the direct successor, with separate chapters for cloud and operational technology. | No Essential Eight maturity score is calculated. A mapping to *Essentials for enterprise IT* is on the roadmap, to be done only after reading the chapter and ASD's transition guide. Many organisations will still be reporting against the Essential Eight during the transition. |
| [OAIC: Notifiable Data Breaches scheme](https://www.oaic.gov.au/privacy/notifiable-data-breaches) | Organisations covered by the Privacy Act (generally turnover above $3 million, with exceptions) must assess a suspected eligible data breach within 30 days and notify where required | Obligations OB01–OB02, marked `assumed_applicable` with the turnover assumption stated |
| [Cyber Security Act 2024 (Cth), Part 3](https://www.cyber.gov.au/ransomware-payment-and-cyber-extortion-payment-reporting) | Since 30 May 2025, reporting business entities must report a ransomware or cyber extortion payment to ASD within 72 hours | Obligation OB03, linked to authority contacts and incident planning |
| [NIST SP 1301](https://csrc.nist.gov/pubs/sp/1301/final) | Current and target profiles support prioritisation and communication | Target scores are kept separate from owner-assessed residual scores |
| [Microsoft Graph device registration policy](https://learn.microsoft.com/graph/api/resources/deviceregistrationpolicy) | `userDeviceQuota` describes the device registration limit | Offline technical observation that can later become reviewed evidence |

## Why this is stronger than a checklist
An interviewer can ask why a control is included, who may accept a residual risk, whether evidence covers the relevant population, whether a finding is really closed, and which law makes a control necessary. The project gives a traceable answer to each question, and the code enforces the rules instead of only describing them.

## Alternatives considered
- Policy-only document pack: easy to produce, but proves little about practical assurance.
- Another cloud configuration scanner: fits earlier technical experience but adds little GRC breadth.
- Full multi-user GRC platform: authentication, tenancy and operations work would crowd out the analysis.
- **Selected:** structured working papers plus a small, tested, reproducible engine, expanded only after analyst review.

## Interpretation limits
Mapping a device setting to A.8.1 or A.5.23 is a project judgement about supporting evidence, not an official equivalence. The device limit of 20 is a project choice, not an ISO requirement. Obligation applicability is assumed for a fictional company and is not legal advice. Full clause and Annex A validation needs access to the licensed standard.
