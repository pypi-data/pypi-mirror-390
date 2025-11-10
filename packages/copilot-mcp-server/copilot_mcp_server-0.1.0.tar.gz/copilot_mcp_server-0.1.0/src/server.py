from fastmcp import FastMCP
from src.tools.copilot_tool import register_copilot_tools

mcp = FastMCP(
    name="copilot-mcp-server",
    version="0.1.0",
)

def setup_server():
    """Setup and configure the MCP server with all tools."""
    register_copilot_tools(mcp)
    return mcp

server = setup_server()