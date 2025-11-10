# Copilot MCP Server

MCP (Model Context Protocol) server for integrating copilots with Claude Desktop and other MCP clients.

## Features

- 🤖 **Chat with Copilots** - Interactive conversations with copilots
- 🔍 **Query Copilots** - Send queries with optional context
- 🔌 **Easy Integration** - Works seamlessly with Claude Desktop

## Installation

### Via pip (after publishing to PyPI)

```bash
pip install copilot-mcp-server
```

### Via uvx (recommended for Claude Desktop)

```bash
uvx copilot-mcp-server
```

## Configuration

### Option 1: Environment Variables in Claude Desktop Config

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following:

```json
{
  "mcpServers": {
    "copilot-mcp-server": {
      "command": "uvx",
      "args": ["copilot-mcp-server@latest"],
      "env": {
        "KARINI_API_BASE": "https://api.karini.ai",
        "KARINI_COPILOT_ID": "your-copilot-id",
        "KARINI_API_KEY": "your-api-key"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `KARINI_API_BASE` | Yes | Base URL for Karini API |
| `KARINI_COPILOT_ID` | Yes | Your copilot's unique identifier |
| `KARINI_API_KEY` | Yes | API key for authentication |
| `KARINI_COPILOT_ORIGIN` | Yes | Origin URL for CORS |

## Available Tools

### `ask_karini_copilot`

Ask a question to your Karini copilot and get a response.

**Parameters:**
- `question` (string, required): The question to ask the copilot
