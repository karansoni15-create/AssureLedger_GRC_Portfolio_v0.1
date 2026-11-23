# Validation record

## v0.2.0 — 23 November 2026 (Australia/Sydney)
Executed in a Linux build environment before the pull request was opened.

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -v` on Python 3.11, 3.12 and 3.13 | 57 tests passed on each |
| `python -m assureledger --as-of 2026-10-10` | Four reports generated; SoA 19/93 decided; 7 issues (1 high) |
| Committed reports regenerated and compared byte-for-byte | Identical (enforced by `test_committed_reports_are_reproducible`) |
| `pip install .` into a clean virtual environment, then `assureledger --version` and a run from another directory | Passed; the Annex A catalogue ships as package data |
| `management-review.html` rendered in headless Chrome and inspected | All sections visible; layout fixed after a first pass hid one risk row inside a scroll box |
| `--strict` on the demo scenario | Exit code 1, as intended (F02 closure is unverified) |

Covered by tests: scoring bands; Annex A catalogue completeness (93 = 37 + 8 + 14 + 34); type, enum, date and reference validation with clean exit code 2; SoA coverage and conflicts; ISO/IEC 27005 treatment options; overdue treatment; acceptance authority, expiry and missing residual; obligation coverage and review dates; evidence integrity, path traversal, expiry, rejection and pending review; independent closure; CSV injection (including tab and carriage return); HTML escaping; optional and unreadable device snapshot.

Not yet verified: the GitHub Actions run itself (including the Windows and Python 3.14 jobs) until the pull request triggers it; correctness of SoA topic labels against the licensed standard; legal applicability of the obligations.

No production deployment, real-tenant assessment, legal review or ISO certification review has taken place.

## v0.1.0 — 10 October 2026
16 tests passed locally; reports generated. The GitHub Actions workflow had not run, and later turned out never to have run because it was committed inside a sub-folder.
