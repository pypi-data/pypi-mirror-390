"""Main entry point for Masto-Mailo-Inator.

This module provides the command-line interface for the application,
handling arguments parsing and dispatching commands to the appropriate modules.
"""

import argparse
import importlib.metadata

from .get import get
from .setup import setup

# Get version from pyproject.toml via package metadata
VERSION = importlib.metadata.version('masto-mailo-inator')

def main():
    """Entry point for the command-line interface.

    Parses command-line arguments and dispatches to the appropriate
    command handler function.
    """
    parser = argparse.ArgumentParser(prog='masto-mailo-inator', description='Toots in your mailbox')
    parser.add_argument('-V', '--version', action='version', version=VERSION)

    action_parser = parser.add_subparsers(dest="command", required=True, title="Command")
    action_parser.add_parser('get', description='Get toots to your mailbox')
    action_parser.add_parser('setup', description='Setup auth')

    args = parser.parse_args()

    if args.command == 'get':
        get()
    elif args.command == 'setup':
        setup()

if __name__ == '__main__':
    main()
