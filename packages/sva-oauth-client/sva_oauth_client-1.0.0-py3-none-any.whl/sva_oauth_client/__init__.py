"""
SVA OAuth Client - A Django package for integrating SVA (Secure Vault Authentication) OAuth provider.

This package provides a complete solution for Django applications to authenticate users
via SVA OAuth and retrieve identity blocks data from the consent screen.
"""

__version__ = '1.0.0'
__author__ = 'SVA Team'

from .client import SVAOAuthClient
from .decorators import sva_oauth_required, sva_blocks_required
from .utils import get_blocks_data, get_userinfo

__all__ = [
    'SVAOAuthClient',
    'sva_oauth_required',
    'sva_blocks_required',
    'get_blocks_data',
    'get_userinfo',
]

