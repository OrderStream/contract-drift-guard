# contract-drift-guard 📋✨

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-Passing-brightgreen.svg)]()
[![OrderStream Polar](https://img.shields.io/badge/Polar-OrderStream-blue.svg)](https://polar.sh/orderstream)
[![Stellar XLM/USDC](https://img.shields.io/badge/Stellar-USDC%2FXLM-black.svg)](#direct-web3-wallet-monetization)
[![Base USDC](https://img.shields.io/badge/Base-USDC-0052FF.svg)](#direct-web3-wallet-monetization)

CI gate that extracts runtime payload schemas during backend test execution and diffs them against frontend TypeScript definitions to catch API schema drifts before release.

---

## 💥 The Friction & Dollar Cost
API contracts inevitably drift between frontend and backend teams:
- Backend refactors an endpoint: `user_id` is renamed to `userId`, a mandatory field is removed, or a field returns `null` instead of an object.
- Backend CI tests pass 100% (since backend tests only test backend).
- The change ships to production, causing `TypeError: Cannot read properties of undefined` and crashing client single-page apps.

**contract-drift-guard** bridges the boundary in CI:
- Compares real serialized backend test fixtures or OpenAPI specs against frontend TypeScript interfaces.
- Flags missing fields, nullability violations, and scalar type mismatches.
- Emits markdown diff tables directly into GitHub Actions summaries.

---

## 🚀 Quick Start

### Installation
```bash
pip install contract-drift-guard
```

### CLI Usage
```bash
# Compare recorded backend response with frontend TypeScript interface
contract-drift-guard check \
  --backend-payload ./fixtures/user_response.json \
  --frontend-types ./frontend/src/types/user.ts \
  --type-name "UserProfile"

# Strict mode: fail if backend returns unmodeled extra fields
contract-drift-guard check \
  --backend-payload ./fixtures/user_response.json \
  --frontend-types ./frontend/src/types/user.ts \
  --type-name "UserProfile" \
  --fail-on-extra

# Check license & zero-fee wallet payment details
contract-drift-guard license
```

---

## 🤖 GitHub Action Integration

```yaml
- name: Contract Drift Guard CI
  uses: OrderStream/contract-drift-guard@v1
  with:
    backend_payload: "tests/fixtures/account_response.json"
    frontend_types: "frontend/types/account.ts"
    type_name: "AccountData"
    fail_on_extra: false
```

---

## 💰 Direct Web3 Wallet Monetization & Polar Integration

Support this project or purchase enterprise OpenAPI live streaming with **0 platform fees**:

- **Polar Subscription & Sponsorship:** [https://polar.sh/orderstream](https://polar.sh/orderstream)
- **Stellar Network (Native XLM / USDC):**
  - Public Key: `GABFQIK63R2NETJM7T673EAMZN4RJLLGP3OFUEJU5ZVTGWUKULZJNL6`
  - Memo (Required): `400566831`
- **EVM (Base / Arbitrum / Ethereum USDT & USDC):**
  - Address: `0x5de2b62434754bfd39ef350a3a867ed3eced5074`
