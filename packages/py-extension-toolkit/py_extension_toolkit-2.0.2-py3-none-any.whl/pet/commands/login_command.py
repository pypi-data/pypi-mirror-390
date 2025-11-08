"""Login command for authentication."""

import click
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta


@click.command()
@click.option('--server', help='Extension server URL')
@click.option('--username', help='Your username')
@click.option('--password', help='Your password')
def login(server, username, password):
    """Login to the extension server."""
    
    # Use defaults if not provided
    click.echo("🔐 Logging in to Aqary Identity Service.")
    if not server:
        server = 'https://id.aqaryint.com'
    
    if not username:
        username = click.prompt('👤 Username')
    
    if not password:
        password = click.prompt('🔑 Password', hide_input=True)
    
    click.echo(f"🔐 Logging in to {server}...")
    
    try:
        # Make authentication request to the API
        auth_url = 'https://id-api.aqaryone.com/api/v1/login'
        
        payload = {
            'username': username,
            'password': password
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(auth_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Successful authentication
            result = response.json()['result']
            
            # Extract tokens and user info
            access_token = result['access_token']
            refresh_token = result['refresh_token']
            expires_in = result['expires_in']
            user_info = result['user']
            role_info = result['role']

            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Create session directory
            session_dir = Path.home() / '.pet'
            session_dir.mkdir(exist_ok=True)
            
            # Store session info
            session_data = {
                'server': server,
                'username': username,
                'authenticated': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': expires_at.isoformat(),
                'expires_in': expires_in,
                'user': user_info,
                'role': role_info
            }
            
            session_file = session_dir / 'session.json'
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            
            click.echo("✅ Login successful!")
            click.echo(f"Welcome, {user_info['first_name']} {user_info['last_name']}!")
            click.echo(f"🏢 Role: {role_info['role_name']}")
            click.echo(f"📝 Session saved to: {session_file}")
            click.echo(f"⏰ Token expires in {expires_in // 3600} hours")
            
        elif response.status_code == 400:
            # Authentication failed
            error_data = response.json()
            click.echo(f"❌ Authentication failed: {error_data.get('error', 'Invalid credentials')}", err=True)
            return False
            
        else:
            # Other error
            click.echo(f"❌ Login failed with status code {response.status_code}", err=True)
            try:
                error_data = response.json()
                click.echo(f"Error: {error_data}", err=True)
            except:
                click.echo(f"Response: {response.text}", err=True)
            return False
            
    except requests.exceptions.Timeout:
        click.echo("❌ Login request timed out. Please check your internet connection.", err=True)
        return False
    except requests.exceptions.ConnectionError:
        click.echo("❌ Could not connect to authentication server. Please check your internet connection.", err=True)
        return False
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ Network error during login: {e}", err=True)
        return False
    except json.JSONDecodeError:
        click.echo("❌ Invalid response from authentication server.", err=True)
        return False
    except Exception as e:
        click.echo(f"❌ Unexpected error during login: {e}", err=True)
        return False
        
    return True


def get_session():
    """Get current session information."""
    session_file = Path.home() / '.pet' / 'session.json'
    
    if not session_file.exists():
        return None
    
    try:
        with open(session_file, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def is_authenticated():
    """Check if user is authenticated and token is valid."""
    session = get_session()
    if not session or not session.get('authenticated', False):
        return False
    
    # Check if token has expired
    expires_at = session.get('expires_at')
    if expires_at:
        try:
            expiry_time = datetime.fromisoformat(expires_at)
            if datetime.now() >= expiry_time:
                click.echo("⚠️ Your session has expired. Please run 'pet login' again.")
                return False
        except ValueError:
            # Invalid date format, consider expired
            return False
    
    return True


def get_access_token():
    """Get the current access token."""
    session = get_session()
    if session and is_authenticated():
        return session.get('access_token')
    return None


def get_auth_headers():
    """Get headers with authorization token for API requests."""
    token = get_access_token()
    if token:
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    return {'Content-Type': 'application/json'}


def refresh_token():
    """Refresh the access token using refresh token."""
    session = get_session()
    if not session or not session.get('refresh_token'):
        return False
    
    try:
        # This would be the refresh endpoint - adjust URL as needed
        refresh_url = 'https://id-api.aqaryone.com/api/v1/refresh'
        
        headers = {
            'Authorization': f'Bearer {session["refresh_token"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(refresh_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            # Update session with new tokens
            session['access_token'] = result['result']['access_token']
            session['expires_in'] = result['result']['expires_in']
            
            expires_at = datetime.now() + timedelta(seconds=result['result']['expires_in'])
            session['expires_at'] = expires_at.isoformat()
            
            # Save updated session
            session_file = Path.home() / '.pet' / 'session.json'
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2)
            
            return True
    except Exception:
        pass
    
    return False


@click.command()
def logout():
    """Logout from the extension server."""
    session_file = Path.home() / '.pet' / 'session.json'
    
    if session_file.exists():
        session = get_session()
        if session:
            username = session.get('username', 'User')
            session_file.unlink()
            click.echo(f"✅ Sorry to see you go, {username}! You have been logged out.")
            click.echo(f"🗑️ Session cleared from: {session_file}")
        else:
            session_file.unlink()
            click.echo("✅ Session cleared.")
    else:
        click.echo("ℹ️ No active session found.")


def clear_session():
    """Clear the current session (internal helper)."""
    session_file = Path.home() / '.pet' / 'session.json'
    if session_file.exists():
        session_file.unlink()
        return True
    return False