"""
Django views for SVA OAuth integration.
"""
from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_http_methods
from .client import SVAOAuthClient, SVATokenError, SVAAuthorizationError
from .utils import get_client_from_settings, clear_oauth_session


@require_http_methods(["GET"])
def oauth_login(request):
    """
    Initiate OAuth flow by redirecting to SVA authorization endpoint.
    
    URL: /oauth/login/
    """
    try:
        client = get_client_from_settings()
        
        # Generate state and code verifier
        state = request.session.get('sva_oauth_state')
        code_verifier = request.session.get('sva_oauth_code_verifier')
        
        # Generate authorization URL
        auth_url, code_verifier = client.get_authorization_url(
            state=state,
            code_verifier=code_verifier
        )
        
        # Store in session
        request.session['sva_oauth_code_verifier'] = code_verifier
        request.session['sva_oauth_state'] = auth_url.split('state=')[1].split('&')[0] if 'state=' in auth_url else None
        
        return redirect(auth_url)
        
    except Exception as e:
        messages.error(request, f'Failed to initiate OAuth flow: {str(e)}')
        return redirect(getattr(settings, 'SVA_OAUTH_ERROR_REDIRECT', '/'))


@require_http_methods(["GET"])
def oauth_callback(request):
    """
    Handle OAuth callback and exchange authorization code for tokens.
    
    URL: /oauth/callback/
    """
    error = request.GET.get('error')
    if error:
        error_description = request.GET.get('error_description', error)
        messages.error(request, f'OAuth error: {error_description}')
        return redirect(getattr(settings, 'SVA_OAUTH_ERROR_REDIRECT', '/'))
    
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code:
        messages.error(request, 'No authorization code received')
        return redirect(getattr(settings, 'SVA_OAUTH_ERROR_REDIRECT', '/'))
    
    # Verify state
    expected_state = request.session.get('sva_oauth_state')
    if state and expected_state and state != expected_state:
        messages.error(request, 'Invalid state parameter. Possible CSRF attack.')
        return redirect(getattr(settings, 'SVA_OAUTH_ERROR_REDIRECT', '/'))
    
    # Get code_verifier from session
    code_verifier = request.session.get('sva_oauth_code_verifier')
    if not code_verifier:
        messages.error(request, 'Missing code verifier. Please try again.')
        return redirect(getattr(settings, 'SVA_OAUTH_LOGIN_URL', '/oauth/login/'))
    
    try:
        client = get_client_from_settings()
        
        # Exchange code for tokens
        token_response = client.exchange_code_for_tokens(
            code=code,
            code_verifier=code_verifier,
            state=state
        )
        
        # Store tokens in session
        request.session['sva_oauth_access_token'] = token_response.get('access_token')
        request.session['sva_oauth_refresh_token'] = token_response.get('refresh_token')
        request.session['sva_oauth_data_token'] = token_response.get('data_token', '')
        request.session['sva_oauth_scope'] = token_response.get('scope', '')
        
        # Clean up session
        request.session.pop('sva_oauth_code_verifier', None)
        request.session.pop('sva_oauth_state', None)
        
        messages.success(request, 'Successfully authenticated with SVA!')
        
        # Redirect to success URL
        success_url = getattr(settings, 'SVA_OAUTH_SUCCESS_REDIRECT', '/')
        return redirect(success_url)
        
    except SVATokenError as e:
        messages.error(request, f'Failed to exchange token: {str(e)}')
        return redirect(getattr(settings, 'SVA_OAUTH_ERROR_REDIRECT', '/'))
    except Exception as e:
        messages.error(request, f'Unexpected error: {str(e)}')
        return redirect(getattr(settings, 'SVA_OAUTH_ERROR_REDIRECT', '/'))


@require_http_methods(["GET", "POST"])
def oauth_logout(request):
    """
    Logout and clear OAuth session data.
    
    URL: /oauth/logout/
    """
    clear_oauth_session(request.session)
    messages.success(request, 'Successfully logged out.')
    
    logout_redirect = getattr(settings, 'SVA_OAUTH_LOGOUT_REDIRECT', '/')
    return redirect(logout_redirect)

