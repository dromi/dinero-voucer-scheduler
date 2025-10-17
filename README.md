# Dinero Voucher Scheduler

This project ships a CLI utility (`connect_dinero.py`) that validates Dinero API credentials, creates a manual voucher, and books it to confirm write access. A companion script (`run_connect_dinero.sh`) demonstrates how to supply credentials and execute the workflow in one step using `uv run`.

## Requirements

- Python 3.12+
- Dinero account credentials with API access
- Network connectivity to `authz.dinero.dk` and `api.dinero.dk`

The script depends on `requests`; install via `pip install -r requirements.txt` or `uv pip sync uv.lock` for the locked versions.

## Required Environment Variables

Set the following before running the CLI:

- `DINERO_CLIENT_ID`: OAuth client ID from Dinero.
- `DINERO_CLIENT_SECRET`: OAuth client secret paired with the client ID.
- `DINERO_API_KEY`: Personal integration API key; used as username/password in the token request.
- `DINERO_ORG_ID`: Organization GUID the voucher should be created under.

## Running the Verifier

Activate your environment and invoke the script with voucher details:

```bash
python connect_dinero.py \
  --voucher-date 2024-01-01 \
  --description "Sample voucher" \
  --amount 1250.00
```

Command arguments:

- `--voucher-date`: ISO date for the manual voucher (YYYY-MM-DD). Validated before sending.
- `--description`: Line description to appear on the voucher.
- `--amount`: Amount posted on the voucher line. Positive values are automatically negated so the voucher balances correctly.

The script performs three checks:
1. Exchanges the client credentials and API key for an access token.
2. Confirms the provided organization exists and matches `DINERO_ORG_ID`.
3. Creates a manual voucher and books it immediately, printing the voucher number and GUID on success.

Errors are written to stderr with actionable messages (missing env vars, HTTP failures, invalid input).

## Using `run_connect_dinero.sh`

`run_connect_dinero.sh` is an example wrapper that exports placeholder credentials, sets default voucher arguments, and executes `connect_dinero.py` via `uv run`. Update the exports and voucher metadata before use, or comment out the exports if credentials are already in the environment:

```bash
chmod +x run_connect_dinero.sh
./run_connect_dinero.sh
```

The helper script enables `set -euo pipefail`, so any missing variables or failing commands abort immediately. Adjust the `VOUCHER_DATE`, `DESCRIPTION`, and `AMOUNT` variables to suit your validation scenario.

## Operational Notes

- The Dinero manual voucher endpoint used (`/v1/{orgId}/vouchers/manuel`) requires write permissions. Ensure the credentials you supply have the appropriate scope.
- Do not commit real credential values. Store secrets outside the repository or load them via your shell profile or secret manager.
- Successful runs produce output similar to:

```
Successfully connected to Dinero organization 'Example Org' (ID: 401390).
Created manual voucher number 123.
Booked manual voucher with GUID 00000000-0000-0000-0000-000000000000.
```

If this workflow becomes part of automation, consider rotating the test voucher data and cleaning up any artifacts in Dinero as needed.
