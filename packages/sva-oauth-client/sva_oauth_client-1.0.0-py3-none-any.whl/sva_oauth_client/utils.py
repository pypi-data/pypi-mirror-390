"""
Utility functions for SVA OAuth integration.
"""
from typing import Dict, Any, Optional
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from .client import SVAOAuthClient


def get_client_from_settings() -> SVAOAuthClient:
    """
    Create SVAOAuthClient instance from Django settings.
    
    Returns:
        Configured SVAOAuthClient instance
        
    Raises:
        AttributeError: If required settings are missing
    """
    return SVAOAuthClient(
        base_url=getattr(settings, 'SVA_OAUTH_BASE_URL', 'http://localhost:8000'),
        client_id=getattr(settings, 'SVA_OAUTH_CLIENT_ID', ''),
        client_secret=getattr(settings, 'SVA_OAUTH_CLIENT_SECRET', ''),
        redirect_uri=getattr(settings, 'SVA_OAUTH_REDIRECT_URI', ''),
        data_token_secret=getattr(settings, 'SVA_DATA_TOKEN_SECRET', ''),
        data_token_algorithm=getattr(settings, 'SVA_DATA_TOKEN_ALGORITHM', 'HS256'),
        scopes=getattr(settings, 'SVA_OAUTH_SCOPES', None)
    )


def get_blocks_data(session: SessionBase) -> Optional[Dict[str, Any]]:
    """
    Get blocks data from session.
    
    Args:
        session: Django session object
        
    Returns:
        Dictionary containing blocks data, or None if not available
    """
    data_token = session.get('sva_oauth_data_token')
    if not data_token:
        return None
    
    try:
        client = get_client_from_settings()
        return client.get_blocks_data(data_token)
    except Exception:
        return None


def get_userinfo(session: SessionBase) -> Optional[Dict[str, Any]]:
    """
    Get userinfo from session or fetch from OAuth provider.
    
    Args:
        session: Django session object
        
    Returns:
        Dictionary containing user information, or None if not available
    """
    # Try to get from session cache first
    userinfo = session.get('sva_oauth_userinfo')
    if userinfo:
        return userinfo
    
    # Fetch from OAuth provider
    access_token = session.get('sva_oauth_access_token')
    if not access_token:
        return None
    
    try:
        client = get_client_from_settings()
        userinfo = client.get_userinfo(access_token)
        # Cache in session
        session['sva_oauth_userinfo'] = userinfo
        return userinfo
    except Exception:
        return None


def get_access_token(session: SessionBase) -> Optional[str]:
    """
    Get access token from session.
    
    Args:
        session: Django session object
        
    Returns:
        Access token string, or None if not available
    """
    return session.get('sva_oauth_access_token')


def get_data_token(session: SessionBase) -> Optional[str]:
    """
    Get data token from session.
    
    Args:
        session: Django session object
        
    Returns:
        Data token string, or None if not available
    """
    return session.get('sva_oauth_data_token')


def is_authenticated(session: SessionBase) -> bool:
    """
    Check if user is authenticated with SVA OAuth.
    
    Args:
        session: Django session object
        
    Returns:
        True if authenticated, False otherwise
    """
    return bool(session.get('sva_oauth_access_token'))


def clear_oauth_session(session: SessionBase) -> None:
    """
    Clear all OAuth-related data from session.
    
    Args:
        session: Django session object
    """
    keys_to_remove = [
        'sva_oauth_access_token',
        'sva_oauth_refresh_token',
        'sva_oauth_data_token',
        'sva_oauth_userinfo',
        'sva_oauth_scope',
        'sva_oauth_code_verifier',
        'sva_oauth_state',
    ]
    for key in keys_to_remove:
        session.pop(key, None)

