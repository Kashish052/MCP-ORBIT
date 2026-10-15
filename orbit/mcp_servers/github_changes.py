from mcp.server.fastmcp import FastMCP
from orbit.state import MOCK_COMMITS
mcp = FastMCP("orbit-github-changes")
@mcp.tool()
def get_recent_commits(limit: int = 10) -> list[dict]:
    """Return synthetic recent commits for the demo repository (not live GitHub data)."""
    return MOCK_COMMITS[:max(1, min(limit, 20))]
@mcp.tool()
def search_commits_by_tag(tag: str) -> list[dict]:
    """Search synthetic commit metadata by a risk tag such as configuration or performance."""
    needle = tag.lower().strip()
    return [c for c in MOCK_COMMITS if needle in [t.lower() for t in c["risk_tags"]]]
if __name__ == "__main__": mcp.run()
