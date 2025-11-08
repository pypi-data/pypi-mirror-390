"""
Command-line interface for Aristotle SDK.
"""

import argparse
import sys

from aristotlelib.cli.version import get_version
from aristotlelib.cli.prove_from_file import ProveFromFileAction

ALL_ACTIONS = (ProveFromFileAction,)


def main():
    """Main entry point for the Aristotle CLI."""
    parser = argparse.ArgumentParser(
        prog="aristotle",
        description="Aristotle SDK - Automated theorem proving for Lean",
        epilog="For more information, visit https://aristotle.harmonic.fun",
    )

    parser.add_argument(
        "--version", action="version", version=f"aristotlelib {get_version()}"
    )
    subparsers = parser.add_subparsers(dest="command")
    for action_cls in ALL_ACTIONS:
        action = action_cls(subparsers)
        action.add_arguments()

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
