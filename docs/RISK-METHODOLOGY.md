# Risk assessment, treatment and acceptance method
Document: RM-01 | Version 0.2 | Draft exercise method; management approval simulated

Describe each risk as asset → threat event → vulnerability or condition → business consequence. Assess confidentiality, integrity and availability consequences. Record assumptions and scope rather than implying precision from a number.

## Scoring
| Score | Likelihood over next 12 months | Impact: highest material dimension |
|---|---|---|
| 1 | Exceptional given current exposure | Minor local inconvenience |
| 2 | Plausible but unusual | Recoverable team disruption |
| 3 | Credible event requiring active attention | Material customer or operational harm |
| 4 | Likely given exposure and control gaps | Major contractual, data or service harm |
| 5 | Expected or recurring without intervention | Severe sustained business harm |

Score = likelihood × impact. Bands: 1–5 low, 6–11 moderate, 12–19 high, 20–25 critical. This is an ordinal prioritisation tool, not an actuarial estimate or an ISO-mandated formula. A low-frequency catastrophic event can be under-ranked by multiplication; escalate severe consequences regardless of the product.

## Three different scores
| Score | Meaning | Who sets it |
|---|---|---|
| Inherent | Exposure with current controls as assessed | Analyst with risk owner |
| Target | The exposure the treatment plan aims for. A forecast only. | Risk owner when approving the plan |
| Residual | Exposure after treatment, reassessed on evidence | Risk owner after testing; `null` until then |

The engine never copies the target into the residual. A residual score appears only when someone records a reassessment.

## Treatment options (ISO/IEC 27005:2022)
`modify` (change likelihood or impact with controls), `retain` (accept as is), `avoid` (stop the activity) or `share` (for example insurance or contract). A `modify` treatment must select at least one control, and every selected control must be **included** in the SoA; otherwise the engine raises a `soa_conflict` issue. A `retain` treatment must have a valid acceptance.

## Acceptance criteria and authority (simulated)
| Residual score | Who may accept |
|---|---|
| 1–8 | The named risk owner |
| 9–15 | The managing director (simulated role) |
| 16–25 | Nobody: treat further or escalate to the board |

An acceptance record needs the decision maker, date, expiry and rationale. The engine reports `exceeds_authority`, `expired`, `missing_residual` or `invalid_date` when a recorded acceptance cannot be relied on. These limits are values in `risk_criteria` and require real organisational approval before use.

## Worked example R03 (critical, modify)
Threat: loss of customer support data. Condition: expired restore-test evidence and no representative recovery test. Consequence: extended outage and customer harm. Inherent 4 × 5 = 20 (critical). Treatment: Operations runs a representative restore and validates recovery objectives. Target 2 × 5 = 10 is a forecast. No residual is recorded until fresh evidence exists. Finding F02 stays visible as `closure_unverified` until then.

## Worked example R06 (moderate, retain)
Key-person dependency on one tenant administrator. Inherent and residual 3 × 3 = 9. The IT lead's limit is 8, so the decision to retain for two quarters is recorded by the managing director, expiring 31 March 2027. If the IT lead had signed it, the engine would report `exceeds_authority` and a high-severity issue.

## Review cadence
Review monthly, after incidents, supplier changes, scope changes and new evidence. Treatment past its due date is flagged automatically, and high-severity if the inherent risk is high or critical. Git history provides the change trail for this synthetic exercise; a production service needs immutable history and access-controlled approvals.
