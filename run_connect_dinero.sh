#!/usr/bin/env bash
# Simple helper that exports Dinero credentials and runs the verification script.
#
# Replace the placeholder values below with your actual Dinero credentials
# before executing the script. Alternatively, you can set the environment
# variables externally and comment out or remove the export statements.

set -euo pipefail

export DINERO_CLIENT_ID="replace-with-client-id"
export DINERO_CLIENT_SECRET="replace-with-client-secret"
export DINERO_API_KEY="replace-with-api-key"
export DINERO_ORG_ID="replace-with-organization-id"

VOUCHER_DATE=${DINERO_VOUCHER_DATE:-}
DESCRIPTION=${DINERO_VOUCHER_DESCRIPTION:-}
AMOUNT=${DINERO_VOUCHER_AMOUNT:-}

if [[ -z "${VOUCHER_DATE}" || -z "${DESCRIPTION}" || -z "${AMOUNT}" ]]; then
  cat <<'EOF'
Missing Dinero manual voucher details.
Please set the following environment variables before running the script:
  DINERO_VOUCHER_DATE        ISO date (YYYY-MM-DD)
  DINERO_VOUCHER_DESCRIPTION Description for the voucher line
  DINERO_VOUCHER_AMOUNT      Amount for the voucher line

Alternatively, edit run_connect_dinero.sh to hard-code these values.
EOF
  exit 1
fi

python connect_dinero.py \
  --voucher-date "${VOUCHER_DATE}" \
  --description "${DESCRIPTION}" \
  --amount "${AMOUNT}"
