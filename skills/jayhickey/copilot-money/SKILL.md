---
name: copilot-money
description: Query Copilot Money personal finance data (accounts, transactions, net worth, holdings, asset allocation) and refresh bank connections. Use when the user asks about finances, account balances, recent transactions, net worth, investment allocation, or wants to sync/refresh bank data.
---

# Copilot Money CLI

CLI for querying [Copilot Money](https://copilot.money) personal finance data. Auto-authenticates using tokens from browser storage.

> **Note:** This is an unofficial tool and is not affiliated with Copilot Money.

## Installation

```bash
pip install copilot-money-cli
```

Then run commands directly with `copilot ...`

## Commands

### Refresh bank connections
```bash
copilot refresh                     # Refresh all connections
copilot refresh <connection_id>     # Refresh specific connection
copilot refresh --json              # Output as JSON
```

### List accounts
```bash
copilot accounts                    # All accounts with balances
copilot accounts --type CREDIT      # Filter by type
copilot accounts --json             # Output as JSON
```

### Transactions
```bash
copilot transactions                # Recent transactions (default 20)
copilot transactions --count 50     # Specify count
copilot transactions --json
```

### Net worth
```bash
copilot networth                    # Assets, liabilities, net worth summary
copilot networth --json
```

### Holdings
```bash
copilot holdings                    # Grouped by security type (default)
copilot holdings --group account    # Grouped by account
copilot holdings --group symbol     # Grouped by symbol
copilot holdings --group none       # Flat list
copilot holdings --type ETF         # Filter by security type
copilot holdings --json
```

### Asset allocation
```bash
copilot allocation                  # Stocks/bonds breakdown with US/Intl split
copilot allocation --json
```

### Config/auth
```bash
copilot config show                 # Show current config and token status
copilot config init                 # Auto-detect token from browsers
copilot config init --source chrome # From specific browser (arc|chrome|safari|firefox)
copilot config init --source manual # Manual token entry
copilot config refresh              # Refresh auth token
copilot config clear                # Delete saved config
```

## Account Types

- `DEPOSITORY` — Checking/savings accounts
- `CREDIT` — Credit cards
- `INVESTMENT` — Brokerage, 401k, IRA, crypto
- `LOAN` — Mortgages, student loans
- `REAL_ESTATE` — Property values
- `OTHER` — Misc accounts

## Security Types (for holdings)

- `EQUITY` — Individual stocks
- `ETF` — Exchange-traded funds
- `MUTUAL_FUND` — Mutual funds
- `CRYPTO` — Cryptocurrency
- `BOND` — Bonds
- `CASH` — Money market / cash
- `OTHER` — Other securities

## Requirements

- Python 3.10+
- macOS (for browser token auto-detection; manual token entry works anywhere)
- User must be logged into [Copilot Money](https://copilot.money) in a supported browser

## Notes

- Config stored at `~/.config/copilot-money/config.json`
- Auth tokens auto-detected from browser IndexedDB (Arc, Chrome, Safari, Firefox)
- All browser token extraction happens locally — no data sent externally except to Copilot Money's API
- Target date funds are auto-split into US stocks, intl stocks, and bonds
- If auth fails, log into Copilot Money in a browser or use `copilot config init --source manual`
