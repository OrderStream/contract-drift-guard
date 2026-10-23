"""
Command line interface for contract-drift-guard.
"""

import argparse
import sys
import json
from pathlib import Path
from contract_drift_guard.core import TSParser, ContractComparator
from contract_drift_guard.monetization import LicenseManager

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="contract-drift-guard",
        description="CI gate diffing backend runtime payload schemas against frontend TypeScript definitions"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # check command
    check_parser = subparsers.add_parser("check", help="Diff backend JSON payload against TypeScript definition")
    check_parser.add_argument("--backend-payload", required=True, help="Path to backend payload JSON file")
    check_parser.add_argument("--frontend-types", required=True, help="Path to frontend TypeScript definition file (.ts)")
    check_parser.add_argument("--type-name", required=True, help="TypeScript interface or type name to validate against")
    check_parser.add_argument("--fail-on-extra", action="store_true", default=False, help="Fail on extra unmodeled fields")
    check_parser.add_argument("--license-key", default=None, help="OrderStream license key")

    # license / donate command
    subparsers.add_parser("license", help="View license tier and zero-fee crypto donation wallets")

    args = parser.parse_args(argv)

    if not args.command or args.command == "license":
        print(LicenseManager.get_banner("contract-drift-guard"))
        tier = LicenseManager.get_tier(getattr(args, "license_key", None))
        print(f"Active Tier: {tier['name']} ({tier['tier']})")
        print(f"Features: {', '.join(tier['features'])}")
        print(LicenseManager.get_remediation_footer())
        return 0

    if args.command == "check":
        print(LicenseManager.get_banner("contract-drift-guard"))
        payload_path = Path(args.backend_payload)
        types_path = Path(args.frontend_types)

        if not payload_path.exists():
            print(f"Error: Backend payload file not found: {payload_path}")
            return 1
        if not types_path.exists():
            print(f"Error: Frontend types file not found: {types_path}")
            return 1

        payload_data = json.loads(payload_path.read_text(encoding="utf-8"))
        ts_types = TSParser.parse_typescript(types_path.read_text(encoding="utf-8"))

        if args.type_name not in ts_types:
            print(f"Error: TypeScript type/interface '{args.type_name}' not found in {types_path}.")
            print(f"Available types: {', '.join(ts_types.keys())}")
            return 1

        ts_def = ts_types[args.type_name]
        violations = ContractComparator.compare(payload_data, ts_def)

        print(ContractComparator.generate_markdown(violations, args.type_name))
        print(LicenseManager.get_remediation_footer())

        has_critical = any(v.severity == "CRITICAL" for v in violations)
        has_extra = any(v.kind == "EXTRA_FIELD" for v in violations)

        if has_critical or (args.fail_on_extra and has_extra):
            print("\n❌ [CONTRACT-DRIFT-GUARD] FAILED: Contract schema drift detected!")
            return 1

        print("\n✅ [CONTRACT-DRIFT-GUARD] PASSED: Backend payload satisfies TypeScript contract.")
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(main())
