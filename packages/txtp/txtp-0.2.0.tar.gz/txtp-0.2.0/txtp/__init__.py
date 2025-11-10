"""TXTP - Text Transfer Protocol
A simple package to send or serve fixed text over TCP sockets
with a minimal custom protocol header.
"""

__version__ = "0.1.0"

from .core import start_server, send_request
