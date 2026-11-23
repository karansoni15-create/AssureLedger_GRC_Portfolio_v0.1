# Contributing

1. Create a branch. Never commit directly to `main`.
2. Change `data/scenario.json` or the code. Use synthetic data only (see [SECURITY.md](SECURITY.md)).
3. Add a test that explains the assurance consequence of the change, for example "an acceptance signed by the wrong person must not be valid".
4. Run the tests and regenerate the reports:
   ```sh
   python -m unittest discover -s tests -v
   python -m assureledger --as-of 2026-10-10
   ```
   The test suite fails if the committed reports are stale.
5. If you edit an evidence file, update its `sha256` in the scenario on purpose and say why in the pull request. A silent hash change is exactly what the tool is built to catch.
6. Open a pull request describing the decision you made and its rationale. Roadmap items stay labelled "planned" until implemented and tested.
