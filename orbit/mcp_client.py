from __future__ import annotations
import json, sys
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT = Path(__file__).resolve().parents[1]
SERVER_MODULES = {"monitoring":"orbit.mcp_servers.monitoring","logs":"orbit.mcp_servers.logs",
                  "github":"orbit.mcp_servers.github_changes"}
def _decode_result(result):
    if getattr(result, "isError", False): raise RuntimeError(f"MCP tool returned an error: {result.content}")
    pieces = []
    for item in getattr(result, "content", []):
        if getattr(item, "text", None):
            try: pieces.append(json.loads(item.text))
            except json.JSONDecodeError: pieces.append(item.text)
    return pieces[0] if len(pieces) == 1 else pieces
async def call_mcp_tool(server: str, tool_name: str, arguments: dict | None = None):
    """Launch one local MCP server over stdio, call a tool, then close it."""
    if server not in SERVER_MODULES: raise ValueError(f"Unknown MCP server: {server}")
    params = StdioServerParameters(command=sys.executable, args=["-m", SERVER_MODULES[server]],
                                  cwd=str(ROOT), env=None)
    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        return _decode_result(await session.call_tool(tool_name, arguments or {}))
async def gather_incident_evidence() -> dict:
    """Gather evidence through the three local MCP server processes."""
    return {
        "metrics": await call_mcp_tool("monitoring","get_service_metrics"),
        "logs": await call_mcp_tool("logs","search_error_logs",{"limit":50}),
        "commits": await call_mcp_tool("github","get_recent_commits",{"limit":10}),
    }
