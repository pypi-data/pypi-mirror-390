from typing import Optional
import json
from fastmcp import FastMCP
from src.services.client import karini_client


def register_copilot_tools(mcp: FastMCP):
    """Register all copilot-related tools with the MCP server."""
    
    @mcp.tool()
    async def ask_karini_copilot(
        question: str
    ) -> str:
        """Ask a question to the Karini copilot."""
        if not karini_client:
            return json.dumps({
                "error": "Copilot not configured. Please set KARINI_COPILOT_ID and KARINI_API_KEY"
            })
        
        try:
            response = await karini_client.ask_copilot(
                question=question,
                suggest_followup_questions=False,
            )
            return response
        except Exception as e:
            return json.dumps({
                "error": f"Failed to ask copilot: {str(e)}"
            })