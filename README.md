# contract-drift-guard 📋✨

[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-v1.0.0-orange?logo=githubactions)](https://github.com/OrderStream/contract-drift-guard)

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

---

## 💳 Enterprise Pricing Matrix & Licensing

| Tier | Price | Repositories | Core Capabilities |
| :--- | :--- | :--- | :--- |
| **Community Free** | **** | Unlimited | Standalone CLI runner and single-repo GitHub Action |
| **Starter Suite** | ** / mo** | Up to 10 Repos | Automated CI PR gates, 500 CI runs/mo, standard email support |
| **Team Platform** | **,499 / mo** | Up to 50 Repos | Full 10-tool OrderStream suite, flaky test quarantine deterministic replay, zero-downtime shadow DB migration guard, 24/7 telemetry alarms |
| **Enterprise Platform** | **,999 / mo** | Unlimited | Multi-repo speculative merge engine, zero-downtime migration orchestrator, WASM sandbox gate, dedicated 24/7 cloud keeper, custom SLA |
| **M&A IP & Security Audit** | **,000 one-time** | Whole Organization | Comprehensive copyleft AST fuzzy fingerprint audit, snippet license sheriff certification, formal invariant verification, and executive forensic IP Cleanliness Certificate |

## 💰 Direct Web3 Wallet Monetization & Polar Integration

Support this project or purchase enterprise OpenAPI live streaming with **0 platform fees**:

- **Polar Subscription & Sponsorship:** [https://polar.sh/orderstream](https://polar.sh/orderstream)
- **Stellar Network (Native XLM / USDC):**
  - Public Key: `GABFQIK63R2NETJM7T673EAMZN4RJLLGP3OFUEJU5ZVTGWUKULZJNL6`
  - Memo (Required): `400566831`
- **EVM (Base / Arbitrum / Ethereum USDT & USDC):**
  - Address: `0x5de2b62434754bfd39ef350a3a867ed3eced5074`
