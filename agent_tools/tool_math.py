import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

load_dotenv()

mcp = FastMCP("Math")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """
    Health check endpoint.
    Returns: A simple plain text response indicating server health.
    """
    return PlainTextResponse("OK")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers (supports int and float)"""
    return float(a) + float(b)


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers (supports int and float)"""
    return float(a) * float(b)


if __name__ == "__main__":
    port = int(os.getenv("MATH_HTTP_PORT", "8000"))
    mcp.run(transport="streamable-http", port=port, log_level="debug")
