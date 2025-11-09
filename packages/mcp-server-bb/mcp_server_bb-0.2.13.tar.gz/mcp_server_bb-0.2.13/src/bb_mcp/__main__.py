import atexit
import asyncio
import sys

from .bb_mcp import mcp, service
from .config import get_settings


def _close_service() -> None:
    try:
        asyncio.run(service.close())
    except RuntimeError:
        # Event loop already running – best effort close.
        pass


def main() -> None:
    settings = get_settings()
    print("BB_BASE_URL:", settings.bb_base_url)
    if not settings.bb_username or not settings.bb_password:
        print("BB_USERNAME and BB_PASSWORD must be set in environment variables.")
        sys.exit(1)
    print("Starting BB MCP server...")
    atexit.register(_close_service)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
