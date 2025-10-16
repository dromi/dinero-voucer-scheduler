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

VOUCHER_DATE="$(date +%Y-%m-01)"
DESCRIPTION="Danica Pension"
AMOUNT="2092.10"

python connect_dinero.py \
  --voucher-date "${VOUCHER_DATE}" \
  --description "${DESCRIPTION}" \
  --amount "${AMOUNT}"
