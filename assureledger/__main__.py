import argparse
from datetime import date
from pathlib import Path
import sys

from . import __version__
from .engine import assess, device_quota, load
from .reports import write_all
from .schema import ScenarioError


def main(argv=None):
    parser = argparse.ArgumentParser(prog="assureledger", description="AssureLedger synthetic ISMS assessment")
    parser.add_argument("--data", default="data/scenario.json", help="scenario JSON (default: %(default)s)")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today(),
                        help="assessment date YYYY-MM-DD (default: today)")
    parser.add_argument("--out", default="reports", help="output directory (default: %(default)s)")
    parser.add_argument("--strict", action="store_true", help="exit with status 1 if any high-severity issue is found")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    data_path = Path(args.data)
    try:
        result = assess(load(data_path), data_path.parent, args.as_of)
        policy = data_path.parent / "evidence/device-policy.json"
        try:
            quota = device_quota(load(policy)) if policy.is_file() else "unknown"
        except ScenarioError:
            quota = "unknown"  # an unreadable optional snapshot is an unknown observation, not a failed run
    except FileNotFoundError as exc:
        print(f"Scenario error: file not found: {exc.filename}", file=sys.stderr)
        return 2
    except ScenarioError as exc:
        print(f"Scenario error: {exc}", file=sys.stderr)
        return 2
    result["technical_check"] = {"device_quota": quota,
                                 "scope": "One synthetic configuration snapshot; manual mapping required"}
    written = write_all(args.out, result)
    high = result["summary"]["issues_by_severity"].get("high", 0)
    print(f"Wrote {', '.join(written)} to {args.out}")
    print(f"SoA {result['summary']['soa_decided']}/{result['summary']['soa_rows']} decided; "
          f"{len(result['issues'])} issues ({high} high)")
    return 1 if args.strict and high else 0


if __name__ == "__main__":
    sys.exit(main())
