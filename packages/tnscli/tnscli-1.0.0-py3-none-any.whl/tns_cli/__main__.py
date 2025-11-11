#!/usr/bin/env python3
"""
Allow running the CLI as a Python module:
    python -m tns_cli
"""

from .cli import cli

if __name__ == '__main__':
    cli()
