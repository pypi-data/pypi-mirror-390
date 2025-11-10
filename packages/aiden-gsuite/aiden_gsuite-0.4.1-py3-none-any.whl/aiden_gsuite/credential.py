MCP_AGENT = "mcp-gsuite/1.0.0"

CREDENTIAL_ARG = "__credential__"

class Credential:
    def __init__(self, params: dict):
        credential_params = params.get(CREDENTIAL_ARG)
        if not credential_params:
            raise RuntimeError(f"Missing required argument: {CREDENTIAL_ARG}")
        self.account = credential_params.get("account")
        self.token = credential_params.get("token")