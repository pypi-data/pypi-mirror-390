from realtimex_toolkit import get_credential

credential_1 = get_credential("test_http_header_auth")
print("[HTTP Header Auth Credential]", credential_1["payload"])

credential_2 = get_credential("test_query_auth")
print("[Query Auth Credential]", credential_2["payload"])

credential_3 = get_credential("test_basic_auth")
print("[Basic Auth Credential]", credential_3["payload"])

credential_4 = get_credential("test_http_header_auth")
print("[HTTP Header Auth Payload]", credential_4["payload"])

