"""
Unit and integration tests for contract-drift-guard.
"""

import json
import pytest
from pathlib import Path
from contract_drift_guard.core import TSParser, ContractComparator
from contract_drift_guard.monetization import LicenseManager
from contract_drift_guard.cli import main

def test_license_manager():
    comm = LicenseManager.get_tier(None)
    assert comm["tier"] == "community"

    ent = LicenseManager.get_tier("ord_ent_drift_guard")
    assert ent["tier"] == "enterprise"

    banner = LicenseManager.get_banner("contract-drift-guard")
    assert "GABFQIK63R2NETJM7T673EAMZN4RJLLGP3OFUEJU5ZVTGWUKULZJNL6" in banner

def test_ts_parser():
    ts_code = """
export interface UserProfile {
    id: string;
    username: string;
    age?: number;
    email: string | null;
    tags: string[];
}
"""
    types = TSParser.parse_typescript(ts_code)
    assert "UserProfile" in types
    profile = types["UserProfile"]

    assert profile.fields["id"].expected_type == "string"
    assert profile.fields["id"].optional is False

    assert profile.fields["age"].expected_type == "number"
    assert profile.fields["age"].optional is True

    assert profile.fields["email"].nullable is True
    assert profile.fields["tags"].expected_type == "array"

def test_ts_parser_nested_braces():
    nested_code = """
    export interface ComplexAccount {
        accountId: string;
        settings: {
            theme: string;
            notifications: boolean;
        };
        isVerified: boolean;
    }
    """
    types = TSParser.parse_typescript(nested_code)
    assert "ComplexAccount" in types
    acc = types["ComplexAccount"]
    assert "accountId" in acc.fields
    assert "settings" in acc.fields
    assert acc.fields["settings"].expected_type == "object"
    # Crucial assertion: isVerified after nested closing brace must be found!
    assert "isVerified" in acc.fields
    assert acc.fields["isVerified"].expected_type == "boolean"

def test_contract_comparator_detects_drift():
    ts_code = """
interface Product {
    id: string;
    price: number;
    description: string;
}
"""
    types = TSParser.parse_typescript(ts_code)
    product_type = types["Product"]

    # 1. Missing description, price is string instead of number
    payload = {
        "id": "prod_123",
        "price": "99.99",
        "extra_field": True
    }

    violations = ContractComparator.compare(payload, product_type)
    kinds = [v.kind for v in violations]

    assert "MISSING_FIELD" in kinds  # description is missing
    assert "TYPE_MISMATCH" in kinds   # price is string
    assert "EXTRA_FIELD" in kinds     # extra_field

def test_contract_comparator_clean_match():
    ts_code = """
interface Product {
    id: string;
    price: number;
    in_stock: boolean;
}
"""
    types = TSParser.parse_typescript(ts_code)
    payload = {
        "id": "prod_123",
        "price": 99.99,
        "in_stock": True
    }
    violations = ContractComparator.compare(payload, types["Product"])
    assert len(violations) == 0

def test_cli_execution(tmp_path):
    ts_file = tmp_path / "types.ts"
    ts_file.write_text("interface Item { id: string; }\n", encoding="utf-8")

    json_file = tmp_path / "payload.json"
    json_file.write_text('{"id": "123"}', encoding="utf-8")

    exit_code = main([
        "check",
        "--backend-payload", str(json_file),
        "--frontend-types", str(ts_file),
        "--type-name", "Item"
    ])
    assert exit_code == 0

    exit_lic = main(["license"])
    assert exit_lic == 0

    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
