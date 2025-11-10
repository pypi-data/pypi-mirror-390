#!/usr/bin/env python3
"""
CLI for chuk-acp-agent.

Provides commands for scaffolding and running agents.
"""

import argparse
import sys
from pathlib import Path


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="chuk-acp-agent",
        description="Opinionated agent kit for building ACP agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Version command
    subparsers.add_parser("version", help="Show version information")

    # Help command
    subparsers.add_parser("help", help="Show this help message")

    # Client command (interactive mode with MCP config)
    client_parser = subparsers.add_parser("client", help="Run interactive agent with MCP tools")
    client_parser.add_argument(
        "--mcp-config-file",
        type=str,
        help="Path to MCP configuration JSON file",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "version":
        print_version()
    elif args.command == "help":
        parser.print_help()
    elif args.command == "client":
        run_client(args.mcp_config_file)
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


def print_version() -> None:
    """Print version information."""
    from chuk_acp_agent import __version__

    print(f"chuk-acp-agent {__version__}")


def run_client(mcp_config_file: str | None) -> None:
    """
    Run interactive agent client.

    Args:
        mcp_config_file: Optional path to MCP config file
    """
    from chuk_acp_agent.agent.interactive import InteractiveAgent

    # Create interactive agent
    agent = InteractiveAgent()

    # Load MCP config if provided
    if mcp_config_file:
        config_path = Path(mcp_config_file)
        if not config_path.exists():
            print(f"Error: MCP config file not found: {mcp_config_file}", file=sys.stderr)
            sys.exit(1)

        try:
            agent.load_mcp_config(config_path)
            print(f"Loaded MCP config from: {mcp_config_file}")
        except Exception as e:
            print(f"Error loading MCP config: {e}", file=sys.stderr)
            sys.exit(1)

    # Run the agent
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error running agent: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
