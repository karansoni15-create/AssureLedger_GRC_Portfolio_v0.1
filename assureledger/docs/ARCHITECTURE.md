# Architecture and engineering decisions

```mermaid
flowchart TD
    A["Synthetic records and evidence"] --> B["Schema and relationship validation"]
    B --> C["Evidence integrity and freshness"]
    C --> D["Control and finding assessment"]
    D --> E["JSON, CSV and HTML reports"]
```

Python standard library was selected for reproducible offline use and low setup cost. Structured JSON makes assumptions inspectable in Git. Reports are derived outputs, never the source of truth. Dates are evaluated against an explicit assessment date. SHA-256 identifies changed evidence bytes; it is not a signature or provenance guarantee.

## Data relationships
Asset → risk → selected controls → evidence. Findings link one risk and one control plus closure evidence. Duplicate identifiers and broken references are rejected. A future database should enforce the same relationships transactionally.

## Technical adapter
The v0.1 device check reads an explicitly synthetic Microsoft Graph-shaped JSON file. Missing, invalid or negative quota gives `unknown`; zero means no permitted registrations and passes the maximum-only check, but needs usability review. A result remains a technical observation; it cannot automatically mark an ISO control effective. The release does not directly integrate with AutoAudit or Graph.

## Release limits
Reviewers and owners are labels, not authenticated identities. Evidence quality and relevance require manual judgment. The engine cannot tell whether a document truthfully describes an effective control. There is no live connector, database, multi-user API, signed audit log, production RBAC, full standard coverage or deployed web application. Reports are static local HTML. Inputs are trusted local project files; malformed structures may produce Python errors.

## Production gates
Before real organizational data: threat model; authenticated roles and separation of duties; migrations and transactional storage; evidence ACLs and retention; signed/versioned provenance; tenant isolation; secure upload limits and malware handling; backup/restore testing; security review; operational monitoring and incident response. A checksum-only registry must never be represented as immutable audit storage.
