"""
AppID Manager Client SDK

A Python SDK for managing AppID resources with support for concurrent access and product isolation.
"""

from .client import AppIdClient

__version__ = "1.0.0"
__author__ = "ouyangrunli"
__email__ = "ouyangrunli@agora.com"

__all__ = [
    "AppIdClient"
]
