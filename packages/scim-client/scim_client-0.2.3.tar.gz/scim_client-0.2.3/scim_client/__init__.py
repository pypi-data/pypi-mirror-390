"""Top-level package for scim_client."""

__author__ = """Mitratech Development Team"""
__email__ = "devs@mitratech.com"

from ._version import __version_info__, __version__
from .scim_client import SCIMClient
from .response import SCIMResponse
from .resources import User, UserSearch, UserMeta, UserEmail, UserName
