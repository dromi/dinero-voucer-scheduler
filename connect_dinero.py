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

import base64
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict

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

    url = f"{API_BASE_URL}/{credentials.organization_id}/organization"
    response = requests.get(
        url,
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

    return response.json()


def main() -> int:
    try:
        credentials = DineroCredentials.from_env()
        token = fetch_access_token(credentials)
        organization = fetch_organization_details(credentials, token)
    except MissingEnvironmentVariable as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - top level error reporting
        print(f"Error while verifying Dinero connection: {exc}", file=sys.stderr)
        return 1

    org_name = organization.get("Name") or organization.get("name") or "<unknown>"
    print(
        f"Successfully connected to Dinero organization '{org_name}' "
        f"(ID: {credentials.organization_id})."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
