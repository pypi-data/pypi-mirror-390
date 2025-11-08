"""
Decorators for SVA OAuth integration.
"""
from functools import wraps
from typing import Callable, Any
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from .utils import is_authenticated, get_blocks_data


def sva_oauth_required(view_func: Callable) -> Callable:
    """
    Decorator to require SVA OAuth authentication.
    
    Redirects to login if user is not authenticated.
    
    Usage:
        @sva_oauth_required
        def my_view(request):
            # User is authenticated with SVA OAuth
            blocks_data = get_blocks_data(request.session)
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_authenticated(request.session):
            login_url = getattr(settings, 'SVA_OAUTH_LOGIN_URL', '/oauth/login/')
            messages.info(request, 'Please sign in with SVA to continue.')
            return redirect(login_url)
        return view_func(request, *args, **kwargs)
    return wrapper


def sva_blocks_required(*required_blocks: str):
    """
    Decorator to require specific identity blocks.
    
    Args:
        *required_blocks: Block names that must be present
        
    Usage:
        @sva_blocks_required('email', 'name', 'phone')
        def my_view(request):
            # User has approved email, name, and phone blocks
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not is_authenticated(request.session):
                login_url = getattr(settings, 'SVA_OAUTH_LOGIN_URL', '/oauth/login/')
                messages.info(request, 'Please sign in with SVA to continue.')
                return redirect(login_url)
            
            blocks_data = get_blocks_data(request.session)
            if not blocks_data:
                messages.error(request, 'No blocks data available. Please sign in again.')
                login_url = getattr(settings, 'SVA_OAUTH_LOGIN_URL', '/oauth/login/')
                return redirect(login_url)
            
            missing_blocks = [block for block in required_blocks if block not in blocks_data]
            if missing_blocks:
                messages.error(
                    request,
                    f'Missing required blocks: {", ".join(missing_blocks)}. '
                    'Please sign in again and approve all requested blocks.'
                )
                login_url = getattr(settings, 'SVA_OAUTH_LOGIN_URL', '/oauth/login/')
                return redirect(login_url)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

