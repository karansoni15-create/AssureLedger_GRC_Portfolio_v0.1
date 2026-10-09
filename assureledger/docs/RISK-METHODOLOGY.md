# Risk assessment and treatment method
Document: RM-01 | Draft exercise method; management approval not obtained

Use an asset → threat event → vulnerability/condition → business consequence narrative. Assess confidentiality, integrity and availability consequences. Record assumptions and scope rather than implying precision from a number.

## Scoring
| Score | Likelihood over next 12 months | Impact: highest material dimension |
|---|---|---|
| 1 | Exceptional given current exposure | Minor local inconvenience |
| 2 | Plausible but unusual | Recoverable team disruption |
| 3 | Credible event requiring active attention | Material customer or operational harm |
| 4 | Likely given exposure and control gaps | Major contractual, data or service harm |
| 5 | Expected or recurring without intervention | Severe sustained business harm |

Score = likelihood × impact. Bands: 1–5 low, 6–11 moderate, 12–19 high, 20–25 critical. This is an ordinal prioritization tool, not an actuarial estimate or ISO-mandated formula. A low-frequency catastrophic event can be under-ranked; escalate severe consequences regardless of multiplication.

## Treatment and acceptance
Choose reduce, avoid, share or retain; record rationale and accountable owner. For this pilot all five risks use reduction. High/critical risks require management review; moderate risks require an owner decision and dated review; low risks remain monitored. These proposed thresholds require organizational approval.

The JSON contains inherent and target scores. It intentionally contains no automatically claimed residual score. Target reductions are hypotheses until relevant controls are tested and the risk owner reassesses exposure. Acceptance needs a named authorized decision-maker, rationale, decision date, expiry, conditions and supporting evidence; the prototype does not implement authenticated acceptance.

## Worked example R03
Threat: loss of customer support data. Condition: expired restore-test evidence and untested representative recovery. Consequence: extended outage and customer harm. Initial 4 × 5 = 20 (critical). Proposed treatment: Operations performs representative restore and validates recovery objectives. Forecast 2 × 5 = 10 does not become achieved residual risk merely because a test is scheduled. The overdue action stays visible until fresh evidence and independent verification support closure.

## Review cadence
Review monthly, after incidents, supplier changes, scope changes and new evidence. Keep old assessments for trend and rationale. File-level Git history supports the synthetic exercise; a production service requires immutable history and access-controlled approvals.
