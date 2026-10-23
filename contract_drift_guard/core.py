"""
Schema drift comparator diffing backend runtime payloads against frontend TypeScript definitions.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

@dataclass
class TSField:
    name: str
    expected_type: str  # string, number, boolean, array, object, any
    optional: bool
    nullable: bool

@dataclass
class TSTypeDef:
    name: str
    fields: Dict[str, TSField]

@dataclass
class DriftViolation:
    field_name: str
    kind: str  # MISSING_FIELD, TYPE_MISMATCH, NULLABILITY_VIOLATION, EXTRA_FIELD
    severity: str  # CRITICAL, HIGH, INFO
    message: str
    expected: str
    actual: str

class TSParser:
    @staticmethod
    def parse_typescript(content: str) -> Dict[str, TSTypeDef]:
        type_defs: Dict[str, TSTypeDef] = {}
        # Match interface Name { ... } or type Name = { ... } with balanced braces
        pattern = re.compile(r"\b(?:interface|type)\s+([a-zA-Z0-9_$]+)(?:<[^>]*>)?(?:\s+extends\s+[^{]+)?(?:\s*=\s*)?\s*\{")
        blocks: List[Tuple[str, str]] = []

        for match in pattern.finditer(content):
            name = match.group(1)
            start_idx = match.end()
            depth = 1
            i = start_idx
            while i < len(content) and depth > 0:
                if content[i] == '{':
                    depth += 1
                elif content[i] == '}':
                    depth -= 1
                i += 1
            if depth == 0:
                body = content[start_idx:i-1]
                blocks.append((name, body))
        
        for name, body in blocks:
            fields: Dict[str, TSField] = {}
            nested_depth = 0
            for line in body.splitlines():
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                open_braces = line.count("{")
                close_braces = line.count("}")

                if nested_depth == 0:
                    match = re.search(r"^([a-zA-Z0-9_$]+)(\?)?:\s*([^;,\n]+)?", line)
                    if match:
                        fname = match.group(1)
                        optional = bool(match.group(2))
                        raw_type = (match.group(3) or "").strip()
                        nullable = "null" in raw_type or "undefined" in raw_type
                        
                        # Normalize type
                        norm_type = "any"
                        if "{" in line or "Record" in raw_type or "object" in raw_type:
                            norm_type = "object"
                        elif "[]" in raw_type or "Array" in raw_type:
                            norm_type = "array"
                        elif "string" in raw_type:
                            norm_type = "string"
                        elif "number" in raw_type:
                            norm_type = "number"
                        elif "boolean" in raw_type:
                            norm_type = "boolean"
                        
                        fields[fname] = TSField(
                            name=fname,
                            expected_type=norm_type,
                            optional=optional,
                            nullable=nullable
                        )
                nested_depth += (open_braces - close_braces)
            type_defs[name] = TSTypeDef(name=name, fields=fields)

        return type_defs

class ContractComparator:
    @staticmethod
    def infer_type(val: Any) -> str:
        if val is None:
            return "null"
        elif isinstance(val, bool):
            return "boolean"
        elif isinstance(val, (int, float)):
            return "number"
        elif isinstance(val, str):
            return "string"
        elif isinstance(val, list):
            return "array"
        elif isinstance(val, dict):
            return "object"
        return "any"

    @classmethod
    def compare(cls, payload: Dict[str, Any], ts_type: TSTypeDef) -> List[DriftViolation]:
        violations: List[DriftViolation] = []

        # 1. Check all required TS fields exist in backend payload
        for fname, ts_field in ts_type.fields.items():
            if fname not in payload:
                if not ts_field.optional:
                    violations.append(DriftViolation(
                        field_name=fname,
                        kind="MISSING_FIELD",
                        severity="CRITICAL",
                        message=f"Required frontend field '{fname}' is missing from backend runtime response.",
                        expected=f"{ts_field.expected_type} (required)",
                        actual="undefined"
                    ))
            else:
                val = payload[fname]
                val_type = cls.infer_type(val)
                
                # Check nullability
                if val is None and not (ts_field.nullable or ts_field.optional):
                    violations.append(DriftViolation(
                        field_name=fname,
                        kind="NULLABILITY_VIOLATION",
                        severity="CRITICAL",
                        message=f"Field '{fname}' returned null, but TypeScript definition does not permit null.",
                        expected=ts_field.expected_type,
                        actual="null"
                    ))
                # Check type compatibility
                elif val is not None and ts_field.expected_type != "any" and val_type != ts_field.expected_type:
                    violations.append(DriftViolation(
                        field_name=fname,
                        kind="TYPE_MISMATCH",
                        severity="CRITICAL",
                        message=f"Field '{fname}' returned type '{val_type}', but frontend expects '{ts_field.expected_type}'.",
                        expected=ts_field.expected_type,
                        actual=val_type
                    ))

        # 2. Check for extra unmodeled fields
        for key, val in payload.items():
            if key not in ts_type.fields:
                violations.append(DriftViolation(
                    field_name=key,
                    kind="EXTRA_FIELD",
                    severity="INFO",
                    message=f"Backend returned unmodeled payload field '{key}'.",
                    expected="not in TS interface",
                    actual=cls.infer_type(val)
                ))

        return violations

    @staticmethod
    def generate_markdown(violations: List[DriftViolation], contract_name: str) -> str:
        if not violations:
            return f"### ✅ Contract Drift Guard: 100% Schema Parity for `{contract_name}`\n\nNo breaking drift detected."

        criticals = [v for v in violations if v.severity == "CRITICAL"]
        status = "🚨 BREAKING SCHEMA DRIFT" if criticals else "⚠️ SCHEMA DRIFT DETECTED"

        md = [
            f"### {status} in `{contract_name}`",
            "",
            "| Severity | Field | Issue | Frontend Expected | Backend Returned |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]
        for v in violations:
            md.append(f"| `{v.severity}` | `{v.field_name}` | {v.message} | `{v.expected}` | `{v.actual}` |")

        md.append("")
        md.append("---")
        md.append("> **Zero-Downtime Contract Parity by OrderStream**")
        return "\n".join(md)
