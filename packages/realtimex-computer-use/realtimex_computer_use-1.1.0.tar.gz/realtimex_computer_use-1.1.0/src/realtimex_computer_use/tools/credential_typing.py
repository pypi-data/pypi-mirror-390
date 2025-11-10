"""Secure credential typing tools for automated login workflows."""

from typing import Any, Dict

import pyautogui
from pydantic import Field
from realtimex_toolkit import get_credential
from realtimex_toolkit.exceptions import CredentialError


def type_credential_field(
    credential_id: str = Field(description="ID of the credential to use"),
    field_name: str = Field(
        description="Field name to type. Common fields: 'username', 'password' (basic_auth); 'name', 'value' (http_header, query_auth)"
    ),
) -> Dict[str, Any]:
    """Type a credential field value securely without exposing it in responses or logs."""
    try:
        # Retrieve credential using secure toolkit
        credential = get_credential(credential_id)

        # Extract payload containing field values
        payload = credential.get("payload")
        if not payload:
            return {"status": "error", "message": "Credential has no payload"}

        # Get the requested field value
        field_value = payload.get(field_name)
        if field_value is None:
            available_fields = list(payload.keys())
            return {
                "status": "error",
                "message": f"Field '{field_name}' not found in credential",
                "available_fields": available_fields,
            }

        # Type the value using PyAutoGUI
        pyautogui.typewrite(field_value, interval=0.05)

        # Return success without exposing the actual value
        return {
            "status": "success",
            "message": f"Typed credential field '{field_name}'",
            "credential_id": credential_id,
            "credential_name": credential.get("name"),
            "field": field_name,
        }

    except CredentialError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to type credential field: {type(e).__name__}",
        }
