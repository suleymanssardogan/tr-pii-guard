"""MCP server exposing tr-pii-guard's detection/redaction as tools any MCP
client (Claude, other agents) can call directly.

Needs the `mcp` extra: pip install tr-pii-guard[mcp]
Run with: python -m tr_pii_guard.mcp_server  (or the `tr-pii-guard-mcp` script)
"""

from .redactor import hash_pii, redact, restore


def _get_server():
    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError as exc:
        raise ImportError(
            "MCP server için ek bağımlılıklar gerekli: pip install tr-pii-guard[mcp]"
        ) from exc

    server = MCPServer("tr-pii-guard")

    @server.tool()
    def redact_text(text: str, use_ner: bool = False) -> dict:
        """Mask Turkish PII (TC no, IBAN, phone, email, optionally names/locations)
        in `text`. Returns {"masked_text": ..., "mapping": ...}; pass the mapping
        back into restore_text to recover the original."""
        masked_text, mapping = redact(text, use_ner=use_ner)
        return {"masked_text": masked_text, "mapping": mapping}

    @server.tool()
    def restore_text(masked_text: str, mapping: dict) -> str:
        """Reverse redact_text: replace placeholders with their original values."""
        return restore(masked_text, mapping)

    @server.tool()
    def hash_pii_text(text: str, salt: str = "") -> str:
        """Irreversibly pseudonymize PII in `text` with a salted hash instead of
        a restorable placeholder -- the original value can never be recovered."""
        return hash_pii(text, salt=salt)

    return server


def main() -> None:
    _get_server().run()


if __name__ == "__main__":
    main()
