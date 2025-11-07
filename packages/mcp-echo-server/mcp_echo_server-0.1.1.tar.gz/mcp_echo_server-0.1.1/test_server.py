"""Test script to verify the MCP server works."""

import asyncio
import json
from mcp.client.stdio import StdioServerParameters, stdio_client


async def test_echo_tool():
    """Test the echo tool."""
    import sys

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_test.server"],
        env=None,
    )

    async with stdio_client(server_params) as (read, write):
        from mcp.client.session import ClientSession

        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools_result.tools]}")

            # Call the echo tool
            result = await session.call_tool("echo", {"message": "Hello, MCP!"})
            print(f"Echo result: {result.content[0].text}")

            assert result.content[0].text == "Echo: Hello, MCP!"
            print("✓ Test passed!")


if __name__ == "__main__":
    asyncio.run(test_echo_tool())
