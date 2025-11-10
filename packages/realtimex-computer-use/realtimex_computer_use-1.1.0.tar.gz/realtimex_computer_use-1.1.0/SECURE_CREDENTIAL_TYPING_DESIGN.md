# Secure Credential Typing Design

## Problem Statement

AI agents need to type credentials (usernames, passwords, API keys) during automated login workflows. Credential values must **never** appear in:
- LLM conversation history
- Tool responses or logs
- Any debugging output

Traditional approaches expose credentials to the agent, creating security vulnerabilities and compliance issues. A secure solution is required that enables login automation while maintaining zero credential exposure.

## Security Requirements

**Critical constraints:**
- Agents must complete login workflows without seeing credential values
- Credential values must never enter LLM context
- Audit trails must track credential usage without exposing values
- System must support multiple credential types (basic auth, API keys, headers)
- Error messages must not leak credential structure or values

**Rejected approaches:**
- **Agent-side credential handling**: Exposes values to LLM context
- **Masked credentials in prompts**: Still requires transmission to agent
- **Post-execution credential injection**: Breaks dynamic workflow handling

## Chosen Solution: Credential Reference System

### Architecture

```
Agent (sees only references)
           ↓
get_credentials() → Returns [{"id": "cred_123", "name": "gmail", "type": "basic_auth"}]
           ↓
Agent selects credential by name/ID
           ↓
type_credential_field(credential_id="cred_123", field_name="username")
           ↓
MCP Server → Credential Store → Fetch value → Type via PyAutoGUI
           ↓
Returns: {"status": "success", "message": "Typed credential field 'username'"}
```

**Key principle:** Agent orchestrates workflow using credential IDs; actual values stay server-side.

---

## Implementation

### Tool: `type_credential_field`

**Location:** `realtimex-computer-use` MCP server

```python
def type_credential_field(
    credential_id: str,
    field_name: str
) -> Dict[str, Any]:
    """Type a credential field value securely without exposing it in responses or logs."""
    try:
        # Fetch credential from secure store
        credential = get_credential(credential_id)  # Uses realtimex_toolkit

        # Extract requested field
        payload = credential["payload"]
        field_value = payload[field_name]

        # Type the value
        pyautogui.typewrite(field_value, interval=0.05)

        # Return success without exposing value
        return {
            "status": "success",
            "message": f"Typed credential field '{field_name}'",
            "credential_id": credential_id,
            "field": field_name
        }
    except CredentialError as e:
        return {"status": "error", "message": str(e)}
```

---

## Supported Credential Types

The system supports four credential types with specific field structures:

| Type | Payload Fields | Common Use Case | Example Fields |
|------|---------------|-----------------|----------------|
| `basic_auth` | `username`, `password` | Web logins | `type_credential_field(id, "username")` |
| `http_header` | `name`, `value` | API authentication | `type_credential_field(id, "value")` |
| `query_auth` | `name`, `value` | URL parameters | `type_credential_field(id, "value")` |

**Field discovery:** If wrong field name provided, error response includes `available_fields` list.

---

## Agent Workflow

### Complete Login Sequence

```python
# Step 1: Get available credentials (returns metadata only)
credentials = get_credentials()
# Returns: {
#   "credentials": [
#     {"id": "cred_123", "name": "gmail_account", "type": "basic_auth"}
#   ]
# }

# Step 2: Agent asks user which credential to use
# Agent: "Found credential: gmail_account. Use this for login?"

# Step 3: Navigate to username field
coords = calculate_screen_coordinates(0.260, 0.083)
move_mouse(coords["x"], coords["y"])
click_mouse()

# Step 4: Type username (value never exposed)
result = type_credential_field(
    credential_id="cred_123",
    field_name="username"
)
# Returns: {"status": "success", "message": "Typed credential field 'username'"}

# Step 5: Navigate to password field
coords = calculate_screen_coordinates(0.260, 0.150)
move_mouse(coords["x"], coords["y"])
click_mouse()

# Step 6: Type password (value never exposed)
result = type_credential_field(
    credential_id="cred_123",
    field_name="password"
)
# Returns: {"status": "success", "message": "Typed credential field 'password'"}

# Step 7: Submit form
press_key("enter")
```

---

## Security Benefits

✅ **Zero credential exposure to agent**
- Agent sees only credential IDs and names
- Values fetched and typed server-side

✅ **Clean conversation history**
- Logs show: `type_credential_field(credential_id="cred_123", field_name="username")`
- Never shows: `type_text("actual_password123")`

✅ **Audit trail without exposure**
- Track which credentials used
- Track usage timestamps
- Track success/failure rates
- All without logging actual values

✅ **Secure error handling**
- `CredentialError` provides context without leaking values
- Generic errors for unexpected failures
- Field availability hints for debugging

✅ **Flexible credential types**
- Single interface for all credential types
- Payload structure handled transparently
- Easy to extend for new credential types

---

## System Prompt Guidelines

### Secure Credential Usage

**IMPORTANT:** Never ask users for credentials directly. Always use the credential system.

**Login Workflow Pattern:**

1. **Discovery Phase:**
   ```
   Call get_credentials() to list available credentials
   Present options to user for selection
   ```

2. **Navigation Phase:**
   ```
   Navigate to login form
   Click on username/email field
   ```

3. **Username Entry:**
   ```
   Call type_credential_field(credential_id, "username")
   Wait for field to be populated
   ```

4. **Password Navigation:**
   ```
   Navigate to password field (Tab key or click)
   ```

5. **Password Entry:**
   ```
   Call type_credential_field(credential_id, "password")
   Wait for field to be populated
   ```

6. **Submit:**
   ```
   Press Enter or click login button
   Wait for login to complete
   ```

**Security Rules:**

- ❌ NEVER ask user to type credentials manually
- ❌ NEVER use `type_text()` for sensitive data
- ✅ ALWAYS use `type_credential_field()` for credentials
- ✅ ALWAYS verify credential was typed before proceeding
- ✅ Handle errors gracefully and inform user of issues

**Example Prompt Snippet:**

```markdown
## Credential Handling

When logging into websites or services:

1. Use get_credentials() to find available credentials
2. Ask user which credential to use (by name)
3. Use type_credential_field() to type username
4. Use type_credential_field() to type password
5. Submit the login form

NEVER ask users to manually type passwords or API keys.
All credential values are handled securely by the system.
```

---

## Error Handling

### Common Error Scenarios

**1. Credential Not Found:**
```json
{
  "status": "error",
  "message": "Credential error (id=cred_invalid, details={...})"
}
```
**Resolution:** Verify credential ID exists, check credential server connection

**2. Field Not Found:**
```json
{
  "status": "error",
  "message": "Field 'email' not found in credential",
  "available_fields": ["username", "password"]
}
```
**Resolution:** Use correct field name from available_fields list

**3. Decryption Failure:**
```json
{
  "status": "error",
  "message": "Credential error (id=cred_123, details={...})"
}
```
**Resolution:** Check encryption keys, credential server configuration

**4. PyAutoGUI Failure:**
```json
{
  "status": "error",
  "message": "Failed to type credential field: FailSafeException"
}
```
**Resolution:** Mouse in corner (failsafe triggered), move mouse and retry

---

## Configuration

**Required Environment Variables:**

```bash
# Credential server URL (used by get_credentials)
CREDENTIAL_SERVER_URL=http://localhost:3001

# Encryption keys (handled by realtimex_toolkit)
# Set via toolkit configuration
```

**Dependencies:**

```toml
dependencies = [
    "realtimex-toolkit>=1.2.0",  # Secure credential retrieval
    "pyautogui>=0.9.54",          # Typing automation
]
```

---

## Integration Points

### With Other Tools

**Required tool combination:**

```
get_credentials()              # Discover credentials
   ↓
calculate_screen_coordinates() # Find input fields
   ↓
move_mouse() + click_mouse()   # Navigate to field
   ↓
type_credential_field()        # Type credential securely
   ↓
press_key("enter")             # Submit form
```

**Tool chain for complete login:**

```
Browser Control → Coordinate Calculation → Mouse Control → Credential Typing → Keyboard Control
```

---

## Testing Checklist

### Functional Tests
- [ ] Type basic_auth username field
- [ ] Type basic_auth password field
- [ ] Type http_header value field
- [ ] Type query_auth value field
- [ ] Handle missing credential ID
- [ ] Handle invalid field name
- [ ] Return available_fields on field error
- [ ] Verify no credential values in responses

### Security Tests
- [ ] Confirm values never in tool responses
- [ ] Confirm values never in error messages
- [ ] Confirm values never in logs
- [ ] Verify CredentialError messages are safe
- [ ] Test audit trail doesn't expose values

### Integration Tests
- [ ] Complete Gmail login workflow
- [ ] Complete API authentication workflow
- [ ] Handle multi-field credentials
- [ ] Test with PyAutoGUI MCP server integration

---

## Future Enhancements

**Phase 2 - Enhanced Credential Management:**
- Credential validation before typing
- Multi-factor authentication support
- Session management and token refresh
- Credential expiration handling

**Phase 3 - Advanced Security:**
- Biometric authentication integration
- Hardware token support (YubiKey)
- Role-based credential access control
- Credential rotation automation

**Phase 4 - UX Improvements:**
- Visual feedback during credential typing
- Retry logic for failed authentications
- Automatic form field detection
- Smart credential matching by URL

---

## References

- **Related MCP Server:** `realtimex-computer-use` (current package)
- **Credential Library:** `realtimex-toolkit>=1.2.0`
- **PyAutoGUI Documentation:** https://pyautogui.readthedocs.io/
- **Related Design:** `COORDINATE_SCALING_DESIGN.md` (for field navigation)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
**Author:** RTA
**Status:** Implemented - Ready for System Prompt Integration