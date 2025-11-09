"""
AutoSubtitle Python Client Library

Official Python client library for AutoSubtitle.net API.
"""

from .client import AutoSubtitleClient
from .errors import AutoSubtitleError

__version__ = "1.0.0"
__all__ = ["AutoSubtitleClient", "AutoSubtitleError"]

