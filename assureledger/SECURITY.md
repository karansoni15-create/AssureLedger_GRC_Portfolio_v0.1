# Security and data handling
This release is an offline single-user demonstration. Use only synthetic data in a public repository. Never commit tenant exports, access tokens, customer evidence, contracts or personal details. Fixtures are explicitly synthetic. There is no live cloud connector.

Evidence paths are constrained to the dataset directory; HTML output is escaped and CSV cells with formula prefixes are neutralized. Symlinks escaping the evidence root are rejected. These protections do not replace access control on the local filesystem.

Local editors can modify evidence, metadata, hashes and reviewer names together. The system is not tamper-proof and does not authenticate reviewers. Concurrent use, role-based approvals, encrypted storage, retention enforcement and signed audit logs remain production gates. For a real deployment, store evidence outside Git in controlled storage with versioning, least privilege, retention and independently protected logs.

Report software defects through a private maintainer channel once a repository is established. Do not post sensitive evidence in public issues.
