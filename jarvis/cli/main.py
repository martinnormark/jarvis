"""
Command-line interface for Jarvis.

Provides a clean entry point for running the voice assistant.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from ..core.assistant import JarvisAssistant
from ..core.config import Config


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description="Jarvis - Voice Assistant with Interruptible Audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  jarvis                    # Run with default settings
  jarvis --env .env.local   # Use specific environment file
  jarvis --help             # Show this help message
        """,
    )

    parser.add_argument(
        "--env",
        type=str,
        default=".env.local",
        help="Path to environment file (default: .env.local)",
    )

    parser.add_argument("--version", action="version", version="Jarvis 0.1.0")

    args = parser.parse_args(argv)

    try:
        # Load configuration
        config = Config.from_env(args.env)

        # Run assistant
        with JarvisAssistant(config) as assistant:
            conversation_id = assistant.run()

        if conversation_id:
            print(f"✓ Assistant completed successfully")
            return 0
        else:
            print("✗ Assistant terminated")
            return 1

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
