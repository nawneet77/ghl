#!/usr/bin/env python3
"""GoHighLevel MCP Server using FastMCP (Railway-ready version)"""

import asyncio
import sys
from typing import Optional

from fastmcp import FastMCP

from .api.client import GoHighLevelClient
from .services.oauth import OAuthService
from .services.setup import StandardModeSetup
from .utils.client_helpers import get_client_with_token_override

from .ghl_mcp.params import *  # noqa: F403, F401

from .ghl_mcp.tools.contacts import _register_contact_tools
from .ghl_mcp.tools.conversations import _register_conversation_tools
from .ghl_mcp.tools.opportunities import _register_opportunity_tools
from .ghl_mcp.tools.calendars import _register_calendar_tools
from .ghl_mcp.tools.forms import _register_form_tools


# Initialize FastMCP server
mcp: FastMCP = FastMCP("ghl-mcp-server")

oauth_service: Optional[OAuthService] = None
ghl_client: Optional[GoHighLevelClient] = None


def initialize_clients():
    global oauth_service, ghl_client
    oauth_service = OAuthService()
    ghl_client = GoHighLevelClient(oauth_service)


async def get_client(access_token: Optional[str] = None) -> GoHighLevelClient:
    return await get_client_with_token_override(oauth_service, ghl_client, access_token)


def register_all_tools():
    _register_contact_tools(mcp, get_client)
    _register_conversation_tools(mcp, get_client)
    _register_opportunity_tools(mcp, get_client, lambda: oauth_service)
    _register_calendar_tools(mcp, get_client)
    _register_form_tools(mcp, get_client)


def main():
    async def silent_check():
    import os
    print("\n🔍 DEBUG: Checking env vars")
    print("CLIENT_ID:", os.getenv("GHL_CLIENT_ID"))
    print("CLIENT_SECRET:", os.getenv("GHL_CLIENT_SECRET"))
    print("REDIRECT_URI:", os.getenv("GHL_REDIRECT_URI"))

    async with StandardModeSetup() as setup:
        auth_valid, message = setup.check_auth_status()
        if not auth_valid:
            print(f"\n❌ ERROR: {message}\nPlease verify .env variables.", file=sys.stderr)
            return False
        return True


    setup_result = asyncio.run(silent_check())
    if not setup_result:
        print("🛑 Exiting due to failed authentication.")
        sys.exit(1)

    initialize_clients()
    register_all_tools()
    print("🚀 MCP Server is running. Access it via your Railway domain.")
    mcp.run(transport ="http",host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
