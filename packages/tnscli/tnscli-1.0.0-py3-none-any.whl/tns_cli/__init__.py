"""TNS CLI - TAO Name Service Command Line Interface"""

__version__ = "1.0.0"
__author__ = "TNS Team"

from .client import TNSClient
from .cli import cli

__all__ = ["TNSClient", "cli"]
