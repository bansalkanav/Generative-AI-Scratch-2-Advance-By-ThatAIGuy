from fastmcp import FastMCP

mcp = FastMCP("My STDIO MCP Server")

@mcp.tool
def multiply(a: int, b: int) -> int:
    """This tool takes two integers and returns the product"""
    return a * b

@mcp.tool
def add(a: int, b: int) -> int:
    """This tool takes two integers and returns the addition"""
    return a + b

if __name__ == "__main__":
    mcp.run()         # by default this uses "stdio" transport