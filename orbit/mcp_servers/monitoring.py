from mcp.server.fastmcp import FastMCP
from orbit.state import read_state
mcp = FastMCP("orbit-monitoring")
@mcp.tool()
def get_service_metrics() -> dict:
    """Return current local demo-service metrics and health state."""
    state = read_state()
    return {key: state[key] for key in ("service","error_rate","p95_latency_ms",
        "database_pool_usage_pct","health","active_fault","last_deployment")}
if __name__ == "__main__": mcp.run()
