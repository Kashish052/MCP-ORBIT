from mcp.server.fastmcp import FastMCP
from orbit.state import read_logs
mcp = FastMCP("orbit-logs")
@mcp.tool()
def search_error_logs(limit: int = 50) -> list[dict]:
    """Search recent local demo logs, prioritizing error and warning records."""
    return [row for row in read_logs(limit) if row.get("level") in {"ERROR","WARNING"}][-limit:]
@mcp.tool()
def get_recent_logs(limit: int = 30) -> list[dict]:
    """Return recent local demo logs for incident context."""
    return read_logs(limit)
if __name__ == "__main__": mcp.run()
