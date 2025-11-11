"""
    lager.auth.commands

    auth commands
"""

import time
import urllib.parse
import webbrowser
import json
import base64
import requests
import click
from . import (
    get_client_id, get_auth_url, get_audience,
    read_config_file, write_config_file,
)
from ..context import LagerContext

SCOPE = 'openid profile email read:gateway flash:duck offline_access'

def poll_for_token(device_code, interval):
    """
        Poll for an auth token for the specified device at the given interval
    """
    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code,
        'client_id': get_client_id(),
    }
    token_url = urllib.parse.urljoin(get_auth_url(), '/oauth/token')
    while True:
        resp = requests.post(token_url, data=data)
        if resp.status_code == 200:
            return resp.json()

        if resp.status_code >= 500:
            resp.raise_for_status()

        error = resp.json()['error']
        if error == 'authorization_pending':
            time.sleep(interval)
        elif error == 'expired_token':
            click.secho('Session timed out. Please run `lager login` again.', err=True, fg='red')
            click.get_current_context().exit(1)
        elif error == 'access_denied':
            click.secho('Access denied.', err=True, fg='red')
            click.get_current_context().exit(1)


@click.command()
@click.pass_context
def login(ctx):
    """
        Log in
    """
    has_browser = True
    try:
        webbrowser.get()
    except webbrowser.Error:
        has_browser = False

    data = {
        'audience': get_audience(),
        'scope': SCOPE,
        'client_id': get_client_id(),
    }
    code_url = urllib.parse.urljoin(get_auth_url(), '/oauth/device/code')
    response = requests.post(code_url, data=data)
    response.raise_for_status()

    code_response = response.json()
    uri = code_response['verification_uri_complete']
    user_code = code_response['user_code']
    if has_browser:
        click.echo('Please confirm the following code appears in your browser: ', nl=False)
        click.secho(user_code, fg='green')
        if click.confirm('Lager would like to open a browser window to confirm your login info'):
            webbrowser.open_new(uri)
        else:
            click.echo('Cancelled')
    else:
        click.echo('Please visit ', nl=False)
        click.secho(uri, fg='green', nl=False)
        click.echo(' in your browser')
        click.echo('And confirm your device token: ', nl=False)
        click.secho(user_code, fg='green')

    click.echo('Awaiting confirmation... (Could take up to 5 seconds after clicking "Confirm" in your browser)')
    payload = poll_for_token(code_response['device_code'], code_response['interval'])

    config = read_config_file()
    config['AUTH'] = {
        'token': payload['access_token'],
        'type': payload['token_type'],
        'refresh': payload['refresh_token'],
    }
    write_config_file(config)

    ctx = LagerContext(
        ctx=ctx,
        auth=config['AUTH'],
        defaults=None,
        debug=False,
        style=None
    )

    session = ctx.session
    url = 'cli/post-login'
    session.post(url)

    click.secho('Success! You\'re ready to use Lager!', fg='green')

@click.command()
def logout():
    """
        Log out
    """
    try:
        config = read_config_file()
    except FileNotFoundError:
        return

    if 'AUTH' in config:
        del config['AUTH']

    write_config_file(config)






# """
#     lager.auth.commands

#     auth commands - Updated to use Lager Auth Broker with multi-provider SSO support
# """

# import time
# import urllib.parse
# import webbrowser
# import requests
# import click
# from . import (
#     get_client_id, get_auth_url, get_audience,
#     read_config_file, write_config_file,
# )
# from ..context import LagerContext

# # Updated for Lager Auth Broker
# LAGER_AUTH_BROKER_URL = 'http://localhost:8000'

# def poll_for_token(device_code, interval):
#     """
#         Poll for an auth token for the specified device at the given interval
#         Updated to use Lager Auth Broker polling endpoint
#     """
#     data = {
#         'device_code': device_code,
#     }
#     token_url = f"{LAGER_AUTH_BROKER_URL}/v1/device/poll"

#     while True:
#         resp = requests.post(token_url, json=data)

#         if resp.status_code == 200:
#             result = resp.json()
#             # Check if authentication is complete
#             if result['status'] == 'approved':
#                 return result
#             elif result['status'] == 'pending':
#                 time.sleep(interval)
#                 continue
#             elif result['status'] == 'expired':
#                 click.secho('Session timed out. Please run `lager login` again.', err=True, fg='red')
#                 click.get_current_context().exit(1)
#             elif result['status'] == 'denied':
#                 click.secho('Access denied.', err=True, fg='red')
#                 click.get_current_context().exit(1)

#         # Handle all client and server errors (4xx and 5xx)
#         if resp.status_code >= 400:
#             try:
#                 error_detail = resp.json().get('detail', 'Authentication failed')
#                 # For device code errors, raise a special exception to handle cleanly
#                 if 'Invalid device code' in error_detail:
#                     raise DeviceCodeError(error_detail)
#                 click.secho(error_detail, err=True, fg='red')
#                 click.get_current_context().exit(1)
#             except DeviceCodeError:
#                 raise  # Re-raise to be caught by caller
#             except:
#                 click.secho(f'Authentication failed with status {resp.status_code}', err=True, fg='red')
#                 click.get_current_context().exit(1)

#         # If we get here, it's an unexpected response - sleep and retry
#         time.sleep(interval)


# class DeviceCodeError(Exception):
#     """Custom exception for device code validation errors"""
#     pass


# @click.command()
# @click.option('--device-code', help='Device code from SSO tile (internal use)')
# @click.option('--email', help='Email address for direct login (fallback)')
# @click.pass_context
# def login(ctx, device_code, email):
#     """
#         Log in using Lager Auth Broker with multi-provider SSO support
        
#         Primary usage (SSO):
#         lager login --device-code ABC123    # From clicking identity provider tile
        
#         Fallback usage:
#         lager login --email user@company.com  # Direct login
#         lager login                           # Interactive mode
#     """

#     # SSO Flow: Device code provided from identity provider tile click
#     if device_code:
#         click.echo('Authenticating with SSO session...')
#         try:
#             payload = poll_for_token(device_code, 5)

#             # Save tokens to config
#             config = read_config_file()
#             config['AUTH'] = {
#                 'token': payload['access_token'],
#                 'type': payload['token_type'],
#                 'refresh': payload['refresh_token'],
#             }
#             write_config_file(config)

#             # Initialize LagerContext with new auth
#             ctx = LagerContext(
#                 ctx=ctx,
#                 auth=config['AUTH'],
#                 defaults=None,
#                 debug=False,
#                 style=None
#             )

#             # Post-login hook (if your API supports it)
#             try:
#                 session = ctx.session
#                 url = 'cli/post-login'
#                 session.post(url)
#             except:
#                 # Ignore if post-login endpoint doesn't exist
#                 pass

#             click.secho('Success! You\'re ready to use Lager!', fg='green')
#             return

#         except DeviceCodeError as e:
#             # Clean output for invalid device code - just show the server message
#             click.secho(str(e), err=True, fg='red')
#             click.get_current_context().exit(1)
#         except Exception as e:
#             click.secho(f'SSO authentication failed: {str(e)}', err=True, fg='red')
#             click.secho('Try using your company\'s SSO dashboard (Okta, Entra ID, or OneLogin) to start authentication.', err=True, fg='yellow')
#             click.get_current_context().exit(1)

#     # Fallback Flow: Direct email-based login (for development/testing)
#     has_browser = True
#     try:
#         webbrowser.get()
#     except webbrowser.Error:
#         has_browser = False

#     # Get email interactively if not provided
#     if not email:
#         email = click.prompt('Enter your email address', type=str)

#     click.echo(f'Looking up tenant for: {email}')

#     # Start device authorization flow with Lager Auth Broker
#     device_url = f"{LAGER_AUTH_BROKER_URL}/v1/device/start"
#     data = {'email': email}

#     try:
#         response = requests.post(device_url, json=data)
#         response.raise_for_status()
#     except requests.exceptions.HTTPError as e:
#         if response.status_code == 400:
#             error_detail = response.json().get('detail', 'Unknown error')
#             if 'Unable to determine tenant' in error_detail:
#                 click.secho(f'{error_detail}', err=True, fg='red')
#                 click.secho('Make sure your email domain is configured for Lager authentication.', err=True, fg='yellow')
#                 click.secho('Or try using your company\'s SSO dashboard instead.', err=True, fg='yellow')
#                 click.get_current_context().exit(1)
#         click.secho(f'Authentication service error: {str(e)}', err=True, fg='red')
#         click.get_current_context().exit(1)
#     except Exception as e:
#         click.secho(f'Network error: {str(e)}', err=True, fg='red')
#         click.secho('Make sure the Lager auth service is running.', err=True, fg='yellow')
#         click.get_current_context().exit(1)

#     device_response = response.json()
#     verify_url = device_response['verify_url']
#     user_code = device_response['user_code']

#     if has_browser:
#         click.echo('Please confirm the following code appears in your browser: ', nl=False)
#         click.secho(user_code, fg='green')
#         if click.confirm('Open browser to complete authentication?'):
#             webbrowser.open_new(verify_url)
#         else:
#             click.echo('Cancelled')
#     else:
#         click.echo('Please visit ', nl=False)
#         click.secho(verify_url, fg='green', nl=False)
#         click.echo(' in your browser')
#         click.echo('And confirm your device token: ', nl=False)
#         click.secho(user_code, fg='green')

#     click.echo('Awaiting confirmation... (Could take up to 5 seconds after clicking "Continue with SSO")')
#     payload = poll_for_token(device_response['device_code'], device_response['poll_interval'])

#     # Save tokens to config
#     config = read_config_file()
#     config['AUTH'] = {
#         'token': payload['access_token'],
#         'type': payload['token_type'],
#         'refresh': payload['refresh_token'],
#     }
#     write_config_file(config)

#     # Initialize LagerContext with new auth
#     ctx = LagerContext(
#         ctx=ctx,
#         auth=config['AUTH'],
#         defaults=None,
#         debug=False,
#         style=None
#     )

#     # Post-login hook (if your API supports it)
#     try:
#         session = ctx.session
#         url = 'cli/post-login'
#         session.post(url)
#     except:
#         # Ignore if post-login endpoint doesn't exist
#         pass

#     click.secho('Success! You\'re ready to use Lager!', fg='green')


# @click.command()
# def logout():
#     """
#         Log out - revoke refresh token if possible
#     """
#     try:
#         config = read_config_file()
#     except FileNotFoundError:
#         click.secho('You are not currently logged in.', fg='yellow')
#         return

#     # Check if actually logged in
#     if 'AUTH' not in config or not config['AUTH'].get('refresh'):
#         click.secho('You are not currently logged in.', fg='yellow')
#         return

#     # Optionally revoke the refresh token
#     try:
#         revoke_data = {
#             'token': config['AUTH']['refresh'],
#             'token_type_hint': 'refresh_token'
#         }
#         revoke_url = f"{LAGER_AUTH_BROKER_URL}/v1/revoke"
#         response = requests.post(revoke_url, json=revoke_data, timeout=5)
#         # Only log revocation errors if it's a client error (4xx), not server errors (5xx)
#         if 400 <= response.status_code < 500:
#             click.secho(f'Warning: Token revocation failed (server returned {response.status_code})', err=True, fg='yellow')
#     except requests.exceptions.RequestException:
#         # Ignore network/timeout errors - still log out locally
#         pass

#     # Remove auth from config
#     del config['AUTH']
#     write_config_file(config)
#     click.secho('Successfully logged out.', fg='green')