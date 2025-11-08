"""Command-line interface for TestIO MCP Server.

Provides CLI entry point with support for:
- Standard flags: --help, --version
- Credential loading: --env-file
- Config overrides: cache TTLs, logging, concurrency
- Signal handling: graceful shutdown on CTRL+C
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import NoReturn

from dotenv import load_dotenv


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown.

    Handles SIGINT (CTRL+C) and SIGTERM for clean exit.
    Uses os._exit() for immediate cleanup without thread issues.
    """

    def signal_handler(signum: int, frame: object) -> None:
        """Handle shutdown signals gracefully.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = signal.Signals(signum).name
        print(f"\n\nReceived {signal_name}, shutting down...", file=sys.stderr)
        # Use os._exit() instead of sys.exit() to avoid thread cleanup issues
        # Exit code 0 for normal shutdown, 130 for SIGINT (standard shell convention)
        exit_code = 130 if signum == signal.SIGINT else 0
        os._exit(exit_code)

    # Register handlers for SIGINT (CTRL+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def get_version() -> str:
    """Get package version from metadata.

    Returns:
        Version string (e.g., "0.1.0")
    """
    try:
        from importlib.metadata import version

        return version("testio-mcp")
    except Exception:
        return "unknown"


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser with all CLI flags.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="testio-mcp",
        description="TestIO MCP Server - AI-first API integration for TestIO Customer API",
        epilog="Credentials must be provided via environment variables or --env-file. "
        "See https://github.com/test-IO/customer-mcp for documentation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Standard flags
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"testio-mcp {get_version()}",
    )

    # Credential loading
    parser.add_argument(
        "--env-file",
        type=Path,
        metavar="PATH",
        help="Path to .env file with credentials (default: .env in current directory)",
    )

    # Cache TTL overrides
    cache_group = parser.add_argument_group("cache configuration")
    cache_group.add_argument(
        "--cache-ttl-products",
        type=int,
        metavar="SECONDS",
        help="Cache TTL for products in seconds (default: 3600)",
    )
    cache_group.add_argument(
        "--cache-ttl-tests",
        type=int,
        metavar="SECONDS",
        help="Cache TTL for test data in seconds (default: 300)",
    )
    cache_group.add_argument(
        "--cache-ttl-bugs",
        type=int,
        metavar="SECONDS",
        help="Cache TTL for bug data in seconds (default: 60)",
    )

    # Logging configuration
    logging_group = parser.add_argument_group("logging configuration")
    logging_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Log level (default: INFO)",
    )
    logging_group.add_argument(
        "--log-format",
        choices=["json", "text"],
        help="Log output format (default: json)",
    )

    # HTTP client configuration
    http_group = parser.add_argument_group("http client configuration")
    http_group.add_argument(
        "--max-concurrent-requests",
        type=int,
        metavar="N",
        help="Maximum concurrent API requests (default: 10, range: 1-50)",
    )
    http_group.add_argument(
        "--connection-pool-size",
        type=int,
        metavar="N",
        help="HTTP connection pool size (default: 20, range: 1-100)",
    )
    http_group.add_argument(
        "--http-timeout",
        type=float,
        metavar="SECONDS",
        help="HTTP request timeout in seconds (default: 30.0, range: 1-300)",
    )

    return parser


def load_env_file(env_file: Path | None) -> None:
    """Load environment variables from .env file.

    Args:
        env_file: Path to .env file, or None to use default (.env in current directory)

    Raises:
        SystemExit: If specified env_file doesn't exist
    """
    if env_file:
        if not env_file.exists():
            print(f"Error: --env-file '{env_file}' not found", file=sys.stderr)
            sys.exit(1)
        load_dotenv(env_file, override=True)
    else:
        # Load .env from current directory if exists (default behavior)
        load_dotenv(override=False)


def apply_config_overrides(args: argparse.Namespace) -> None:
    """Apply CLI config overrides to environment variables.

    Args:
        args: Parsed command-line arguments
    """
    # Cache TTL overrides
    if args.cache_ttl_products is not None:
        os.environ["CACHE_TTL_PRODUCTS"] = str(args.cache_ttl_products)
    if args.cache_ttl_tests is not None:
        os.environ["CACHE_TTL_TESTS"] = str(args.cache_ttl_tests)
    if args.cache_ttl_bugs is not None:
        os.environ["CACHE_TTL_BUGS"] = str(args.cache_ttl_bugs)

    # Logging overrides
    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level
    if args.log_format:
        os.environ["LOG_FORMAT"] = args.log_format

    # HTTP client overrides
    if args.max_concurrent_requests is not None:
        os.environ["MAX_CONCURRENT_API_REQUESTS"] = str(args.max_concurrent_requests)
    if args.connection_pool_size is not None:
        os.environ["CONNECTION_POOL_SIZE"] = str(args.connection_pool_size)
    if args.http_timeout is not None:
        os.environ["HTTP_TIMEOUT_SECONDS"] = str(args.http_timeout)


def main() -> NoReturn:
    """CLI entry point for TestIO MCP Server.

    Parses command-line arguments, loads environment configuration,
    sets up signal handlers, and starts the MCP server.
    """
    # Set up signal handlers for graceful shutdown
    setup_signal_handlers()

    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()

    # Load environment variables from .env file
    load_env_file(args.env_file)

    # Apply CLI config overrides
    apply_config_overrides(args)

    # Import server AFTER env setup (so Pydantic Settings picks up values)
    from testio_mcp.server import mcp

    # Start server (this blocks until shutdown)
    mcp.run()

    # Unreachable code (mcp.run() blocks forever)
    sys.exit(0)
