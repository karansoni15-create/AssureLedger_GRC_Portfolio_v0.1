# Research brief and project selection
Research date: 10 October 2026 (Australia/Sydney). Sources below are public primary sources, reviewed for project design. Job descriptions are qualitative examples, not a statistically representative demand study or a claim of internship eligibility.

## Decision
Build a risk-to-evidence assurance workbench for a fictional SaaS business using M365 and Azure. Focus on analyst work: define scope, assess exposure, select treatment, record applicability, evaluate evidence, report exceptions and verify corrective action. Keep the first release offline so a recruiter can reproduce it without tenant permissions.

## Evidence behind the decision
| Primary source | Finding used | Design consequence |
|---|---|---|
| [ISO overview](https://www.iso.org/standard/27001) | ISO/IEC 27001:2022 concerns an organizational ISMS and risk management | Include scope and management decisions, not just technical checks |
| [ISO amendment](https://www.iso.org/standard/88435.html) | A 2024 climate-action amendment accompanies the 2022 edition | Include a climate-relevance determination in the context assessment |
| [ASD assessment process](https://www.cyber.gov.au/publication/essential-eight-assessment-process-guide) | Credible evidence and assessment judgment matter | Track scope, freshness and quality; do not equate a screenshot with proven effectiveness |
| [Kinetic GRC Analyst](https://www.livehire.com/careers/wearekinetic/job/K79K3/U25A2H1NUK/grc-analyst) | Risk registers, policies, vendor assurance and reporting feature in a Melbourne role | Include supplier working paper and remediation ownership |
| [Audinate Senior GRC Analyst](https://jobs.lever.co/audinate/e88c36e7-d7d9-4da6-a91b-6679b9b59005) | Risk assessment, audit preparation and maintaining a GRC platform are explicit responsibilities | Make the decision trail demonstrable; this is a senior skills benchmark, not an entry-level vacancy recommendation |
| [NIST SP 1301](https://csrc.nist.gov/pubs/sp/1301/final) | Current/target profiles support prioritization and stakeholder communication | Separate observed evidence from intended future posture |
| [Microsoft Graph policy resource](https://learn.microsoft.com/graph/api/resources/deviceregistrationpolicy) | `userDeviceQuota` describes the device registration quota | Add a small offline technical observation that can later support a reviewed evidence record |

## Why this is stronger than a checklist
An employer can ask why a control is selected, who accepts exposure, whether evidence covers the relevant population and whether a finding is truly closed. This project exposes those questions. The twelve-control pilot is deliberately narrow enough to understand and defend. It must not be sold as a complete ISO implementation.

## Alternatives considered
- Policy-only pack: accessible, but limited proof of practical assurance and data traceability.
- Another cloud configuration scanner: fits previous experience, but contributes less new GRC breadth.
- Full enterprise SaaS platform: substantial auth, tenancy and operational work distracts from an initial credible case study.
- Selected: structured working papers plus a small reproducible evidence engine; expand after analyst review.

## Interpretation limits
Mappings from a device configuration to A.8.1 or A.5.23 are project judgments about supporting evidence, not official equivalence. The locally chosen device limit of 20 is not an ISO requirement. Essential Eight and ISO have different purposes; this release does not calculate Essential Eight maturity or assert framework equivalence. Legal applicability requires separate qualified review. Access to the licensed ISO standard remains necessary to validate full clause and Annex A coverage; copyrighted standard text is not reproduced.
