from fastmcp import Context, FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
import json
import os
import tomllib
import sys
import mcp.types as mt

from .policy import CanopyPolicy

POLICY = None

class PolicyMiddleware(Middleware):
    def __init__(self, policy: CanopyPolicy):
        super().__init__()
        # Initialize any policy-related state here
        self.policy = policy

    async def on_message(self, context: MiddlewareContext, call_next):
        """Called for all MCP messages."""
        message = context.message

        if isinstance(message, mt.CallToolRequestParams):
            tool_name = message.name

            # Check if allowed
            if tool_name not in ["get_canopy_status", "set_canopy_flow"] and not self.policy.is_allowed(tool_name):
                raise Exception(f"Tool call to {tool_name} is not allowed by policy")

            print(f"Processing {context.method} from {context.source} - {tool_name}", file=sys.stderr)
        
        result = await call_next(context)
        
        print(f"Completed {context.method}",file=sys.stderr)
        return result


# Read config from ~/.canopy/mcp_config.json
config_path = os.path.expanduser("~/.canopy/mcp_config.json")
with open(config_path, "r") as f:
    mcp_config = json.load(f)

# Read policy from command line argument if provided
policy_path = sys.argv[1]
POLICY = CanopyPolicy(policy_path)

# Create a proxy to the configured server (auto-creates ProxyClient)
proxy = FastMCP.as_proxy(mcp_config, name="Config-Based Proxy")
proxy.add_middleware(PolicyMiddleware(POLICY))

@proxy.tool()
async def get_canopy_status(ctx: Context) -> dict:
    """Fetches the current configuration state of Canopy."""
    return {"path": POLICY.policy_path}


@proxy.tool()
async def set_canopy_flow(flow_name: str, ctx: Context) -> dict:
    """Sets the active flow name. Once set, this can not be changed for the session."""
    POLICY.set_picked_flow(flow_name)
    return {"status": "Updated successfully."}


# Run the proxy with stdio transport for local access
def main():
    print("\n=== Starting proxy server ===")
    print("Note: The proxy will start and wait for MCP client connections via stdio")
    print("Press Ctrl+C to stop")
    proxy.run()

if __name__ == "__main__":
    main()