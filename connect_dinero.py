"""Utility script to verify connectivity with the Dinero API.

The script relies on the following environment variables being present:

- DINERO_CLIENT_ID
- DINERO_CLIENT_SECRET
- DINERO_API_KEY
- DINERO_ORG_ID

Running the script will attempt to fetch an OAuth access token and then
perform a lightweight request against the Dinero API to verify that the
credentials are valid.  The response is printed to stdout so that the
caller can confirm the integration is working.
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

import requests

TOKEN_URL = "https://authz.dinero.dk/dineroapi/oauth/token"
API_BASE_URL = "https://api.dinero.dk/v1"


class MissingEnvironmentVariable(RuntimeError):
    """Raised when one of the required environment variables is missing."""


@dataclass
class DineroCredentials:
    client_id: str
    client_secret: str
    api_key: str
    organization_id: str

    @classmethod
    def from_env(cls) -> "DineroCredentials":
        def require_env(name: str) -> str:
            value = os.environ.get(name)
            if not value:
                raise MissingEnvironmentVariable(
                    f"Missing required environment variable: {name}"
                )
            return value

        return cls(
            client_id=require_env("DINERO_CLIENT_ID"),
            client_secret=require_env("DINERO_CLIENT_SECRET"),
            api_key=require_env("DINERO_API_KEY"),
            organization_id=require_env("DINERO_ORG_ID"),
        )


def fetch_access_token(credentials: DineroCredentials) -> str:
    """Fetch an OAuth access token from Dinero."""

    encoded = base64.b64encode(
        f"{credentials.client_id}:{credentials.client_secret}".encode("utf-8")
    ).decode("ascii")

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "password",
            "scope": "read write",
            "username": credentials.api_key,
            "password": credentials.api_key,
        },
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:  # pragma: no cover - convenience for users
        raise RuntimeError(
            "Failed to obtain an access token from Dinero."
        ) from exc

    payload: Dict[str, Any] = response.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(
            "Dinero token response did not include an access token."
        )

    return token


def fetch_organization_details(credentials: DineroCredentials, token: str) -> Dict[str, Any]:
    """Retrieve organization details to verify the connection."""

    url = f"{API_BASE_URL}/organizations"
    response = requests.get(
        url,
        params={"fields": "id,name,isPro"},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": credentials.api_key,
        },
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:  # pragma: no cover - convenience for users
        raise RuntimeError(
            "Failed to fetch organization details from Dinero."
        ) from exc

    organizations = response.json()
    if not isinstance(organizations, list):
        raise RuntimeError("Unexpected response while listing Dinero organizations.")

    wanted_id = credentials.organization_id.lower()
    for organization in organizations:
        org_id = str(organization.get("Id") or organization.get("id") or "").lower()
        if org_id == wanted_id:
            return organization

    raise RuntimeError(
        "The provided organization ID was not returned by Dinero. "
        "Ensure the API key belongs to the specified organization."
    )


def create_manual_voucher(
    credentials: DineroCredentials,
    token: str,
    *,
    voucher_date: str,
    description: str,
    amount: float,
) -> Dict[str, Any]:
    """Create a manual voucher to verify write permissions."""

    url = f"{API_BASE_URL}/{credentials.organization_id}/vouchers/manuel"
    payload = {
        "voucherDate": voucher_date,
        "lines": [
            {
                "description": description,
                "accountNumber": 55000,
                "balancingAccountNumber": 60140,
                "amount": amount,
                "accountVatCode": None,
                "balancingAccountVatCode": None,
            }
        ],
    }

    response = requests.post(
        url,
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": credentials.api_key,
        },
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:  # pragma: no cover - convenience for users
        raise RuntimeError("Failed to create a manual voucher in Dinero.") from exc

    return response.json()


def book_manual_voucher(
    credentials: DineroCredentials,
    token: str,
    voucher_guid: str,
    timestamp: str,
) -> Optional[Dict[str, Any]]:
    """Book a previously created manual voucher."""

    url = (
        f"{API_BASE_URL}/{credentials.organization_id}/vouchers/manuel/"
        f"{voucher_guid}/book"
    )

    response = requests.post(
        url,
        json={"timestamp": timestamp},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": credentials.api_key,
        },
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:  # pragma: no cover - convenience for users
        raise RuntimeError("Failed to book the manual voucher in Dinero.") from exc

    if not response.content:
        return None

    return response.json()


def parse_arguments(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify Dinero connectivity, create a manual voucher, and book it "
            "afterwards."
        )
    )
    parser.add_argument(
        "--voucher-date",
        required=True,
        help="ISO formatted date (YYYY-MM-DD) to use for the manual voucher.",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Description for the manual voucher line.",
    )
    parser.add_argument(
        "--amount",
        type=float,
        required=True,
        help="Amount to post on the manual voucher line.",
    )
    return parser.parse_args(argv)


def main() -> int:
    try:
        args = parse_arguments(sys.argv[1:])
        try:
            voucher_date = date.fromisoformat(args.voucher_date).isoformat()
        except ValueError as exc:
            raise RuntimeError(
                "--voucher-date must be a valid ISO formatted date (YYYY-MM-DD)."
            ) from exc

        credentials = DineroCredentials.from_env()
        token = fetch_access_token(credentials)
        organization = fetch_organization_details(credentials, token)
        voucher = create_manual_voucher(
            credentials,
            token,
            voucher_date=voucher_date,
            description=args.description,
            amount=args.amount,
        )
        voucher_guid = (
            voucher.get("guid")
            or voucher.get("Guid")
            or voucher.get("voucherGuid")
            or voucher.get("VoucherGuid")
        )
        if not voucher_guid:
            raise RuntimeError("Dinero response did not include a voucher GUID to book.")
        timestamp = (
            voucher.get("timestamp")
            or voucher.get("Timestamp")
            or voucher.get("timeStamp")
            or voucher.get("TimeStamp")
        )
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise RuntimeError(
                "Dinero response did not include a timestamp required to book the voucher."
            )
        book_manual_voucher(credentials, token, voucher_guid, timestamp)
    except MissingEnvironmentVariable as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - top level error reporting
        print(f"Error while verifying Dinero connection: {exc}", file=sys.stderr)
        return 1

    org_name = organization.get("Name") or organization.get("name") or "<unknown>"
    voucher_number = voucher.get("voucherNumber") or voucher.get("VoucherNumber")
    print(
        f"Successfully connected to Dinero organization '{org_name}' "
        f"(ID: {credentials.organization_id})."
    )
    if voucher_number is not None:
        print(f"Created manual voucher number {voucher_number}.")
    else:
        print("Created manual voucher.")
    print(f"Booked manual voucher with GUID {voucher_guid}.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
