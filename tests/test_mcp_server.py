import asyncio
import json
import sys

import pytest

pytest.importorskip("mcp")

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

VALID_TC_NO = "10000000146"


async def _run_session():
    params = StdioServerParameters(command=sys.executable, args=["-m", "tr_pii_guard.mcp_server"])
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()

        tools = await session.list_tools()
        tool_names = {t.name for t in tools.tools}

        redact_result = await session.call_tool("redact_text", {"text": f"TC no {VALID_TC_NO}."})
        payload = json.loads(redact_result.content[0].text)

        restore_result = await session.call_tool(
            "restore_text",
            {"masked_text": payload["masked_text"], "mapping": payload["mapping"]},
        )
        restored = restore_result.content[0].text

        hash_result = await session.call_tool(
            "hash_pii_text", {"text": f"TC no {VALID_TC_NO}.", "salt": "test-tuz"}
        )
        hashed = hash_result.content[0].text

        return tool_names, payload, restored, hashed


def test_mcp_server_tools_round_trip():
    tool_names, payload, restored, hashed = asyncio.run(_run_session())

    assert tool_names == {"redact_text", "restore_text", "hash_pii_text"}
    assert VALID_TC_NO not in payload["masked_text"]
    assert restored == f"TC no {VALID_TC_NO}."
    assert VALID_TC_NO not in hashed
