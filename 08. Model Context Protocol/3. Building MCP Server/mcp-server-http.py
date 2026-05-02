from fastmcp import FastMCP

mcp = FastMCP("My HTTP MCP Server")

@mcp.tool
def get_weather(location: str) -> str:
    """Get weather for location."""
    return f"It is sunny in {location}."

if __name__ == "__main__":
    # Start an HTTP server on port 8000
    # You can use http or streamable-http transport for this
    # Run the server using command: "python mcp-server-http.py"
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)