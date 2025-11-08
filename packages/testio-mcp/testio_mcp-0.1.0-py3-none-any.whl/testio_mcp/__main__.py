"""Entry point for running TestIO MCP server as a module.

This allows running the server with: python -m testio_mcp
Or via CLI entry point: testio-mcp (after pip install)
"""

from testio_mcp.server import mcp


def main() -> None:
    """CLI entry point for the TestIO MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
