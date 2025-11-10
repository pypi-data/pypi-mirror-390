import os
import logging
import argparse
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from starlette.middleware.cors import CORSMiddleware

from . import (
    account,
    trading,
    market,
    config,
)

_LOGGER = logging.getLogger(__name__)


verifier = StaticTokenVerifier(tokens={
    config.MCP_AUTH_TOKEN: {
        "client_id": "mcp",
        "scopes": [],
    }
})
mcp = FastMCP(name="mcp-okx", version="0.1.0", auth=verifier)
account.add_tools(mcp)
trading.add_tools(mcp)
market.add_tools(mcp)


def main():
    mode = os.getenv("TRANSPORT")
    port = int(os.getenv("PORT", 0)) or 80
    parser = argparse.ArgumentParser(description="OKX MCP Server")
    parser.add_argument("--http", action="store_true", help="Use streamable HTTP mode instead of stdio")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=port, help=f"Port to listen on (default: {port})")

    args = parser.parse_args()
    if args.http or mode == "http":
        app = mcp.http_app()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id", "mcp-protocol-version"],
            max_age=86400,
        )
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()

if __name__ == "__main__":
    main()
