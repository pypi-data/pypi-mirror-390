"""Credential management tools for retrieving configured authentication credentials."""

import os
from typing import Dict, Any
import httpx


def get_credentials() -> Dict[str, Any]:
    """Get available credentials for authentication from the configured credential server."""
    credential_server_url = os.getenv("CREDENTIAL_SERVER_URL", "http://localhost:3001")

    try:
        api_url = f"{credential_server_url.rstrip('/')}/api/v1/credentials"
        response = httpx.get(api_url, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict) or not data.get("status"):
            return {"status": "error", "message": "Invalid response from server"}

        # Extract only essential fields
        credentials_data = data.get("credentials", [])
        credentials = [
            {
                "name": cred.get("name"),
                "type": cred.get("type"),
                "id": cred.get("id"),
            }
            for cred in credentials_data
        ]

        return {
            "status": "success",
            "message": f"Found {len(credentials)} credential(s)",
            "credentials": credentials,
        }

    except httpx.TimeoutException:
        return {"status": "error", "message": "Connection timeout"}
    except httpx.HTTPStatusError as e:
        return {"status": "error", "message": f"HTTP {e.response.status_code}"}
    except httpx.RequestError:
        return {"status": "error", "message": "Connection failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
