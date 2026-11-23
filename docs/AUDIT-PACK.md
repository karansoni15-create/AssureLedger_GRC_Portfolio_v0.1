# Pilot assurance working papers
All observations, roles and decisions below are simulated. No real audit was performed.

## Statement of Applicability approach
`data/scenario.json` is the source of truth and `reports/soa.csv` is the generated view. The SoA lists all 93 ISO/IEC 27001:2022 Annex A references; 19 have a recorded decision and 74 are marked `undecided`, so the engine reports the SoA as incomplete. Each decision records the identifier, a project objective, applicability, rationale, implementation and evidence. Organisation-specific controls can be added with `"source": "additional"`. Inclusion does not mean implementation, and implementation does not mean effectiveness. Clause 4–10 management-system requirements are assessed separately.

## Internal audit plan IA-01
Objective: test whether selected access, recovery and supplier decisions have sufficient support. Criteria: approved project procedures and selected ISO alignment objectives, subject to licensed-standard validation. Population: privileged identities, restore processes and high-risk SaaS suppliers. Period: October 2026 synthetic exercise. Auditor: simulated assurance lead, separate from action owners.

| Procedure | Proposed sample | Test | Limitation |
|---|---|---|---|
| Access review | All 12 pilot privileged accounts | Reconcile owners, necessity and authorization | Guests and emergency accounts excluded from fixture |
| Recovery | One representative restored support dataset | Compare integrity, duration and recovery point to agreed objectives | Old test does not establish current ability |
| Vendor review | One high-impact support vendor | Review processing, deletion, subprocessors and incident terms | No independent supplier assurance report supplied |
| Endpoint governance | One tenant policy snapshot | Compare quota to local policy; check coverage separately | Quota alone does not establish device compliance |

## Findings and corrective action
F01: configuration exceeds a local device threshold; assess operational impact before changing it. Root-cause hypothesis: baseline review not integrated into change management. Require approved change evidence and post-change test.

F02: closure was recorded using expired restoration evidence. Root-cause hypothesis: closure workflow lacks freshness validation. Reperform representative test, assess recovery objectives and obtain independent verification. The engine reports `closure_unverified` and overdue as of 10 October.

F03: supplier deletion and subprocessor assurances are incomplete. Root-cause hypothesis: renewal process lacks security checkpoints. Obtain evidence, document gaps and escalate the renewal decision. Do not invent vendor approval.

## Supplier assessment VR-01
Fictional supplier: SupportDesk Example. Service: support ticket processing. Inherent tier: high because of customer information and service dependency. Request data locations, subprocessors, access controls, incident notification terms, retention/deletion evidence, continuity test results and independent assurance scope. A certificate alone may not cover the supplied service. Proposed recommendation: conditional renewal only after accountable review of unresolved gaps; no approval has been granted.

## Management review MR-01 — draft decision brief
As of 10 October 2026. Six risks are registered: five are being modified (one critical, four high) and one moderate risk is retained under a current acceptance. Two control entries have current reviewed supporting evidence, but their shared access-review record does not cover every account population. All four obligations show a gap because no linked control yet has accepted evidence. The SoA has 19 of 93 decisions. No whole-ISMS compliance percentage is calculated.

Decisions requested: fund a representative restore exercise; assign endpoint exception ownership; require a supplier evidence checkpoint before renewal. Evaluate audit results, outstanding actions, stakeholder feedback, changes in context, resources and improvement opportunities. Record who decided, what was authorized, due date and follow-up evidence. These are requests for a simulated meeting, not fabricated management approvals.

## Obligations register OB-01
Each entry records source, a paraphrased requirement, applicability, the basis for that applicability, owner, linked SoA controls and review date. The engine reports `gap` when linked controls lack accepted evidence and `soa_conflict` when an obligation relies on a control the SoA does not include.

| ID | Source | Applicability | Basis |
|---|---|---|---|
| OB01 | Privacy Act 1988 (Cth), APP 11 | assumed | Turnover above $3 million assumed; confirm |
| OB02 | Privacy Act Part IIIC, Notifiable Data Breaches scheme | assumed | Follows OB01 |
| OB03 | Cyber Security Act 2024 (Cth), Part 3 ransomware payment reporting | assumed | Turnover threshold assumed; confirm |
| OB04 | Customer master services agreement | applicable | Fictional 48-hour notification clause |

Applicability is assumed for a fictional company and is not legal advice. Do not infer legal coverage from company size or location alone. The register supports a conversation with legal counsel; it does not replace it.
