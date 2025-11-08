"""List workspace command for managing workspaces."""

import click
import json
import requests
from pathlib import Path
from .login_command import is_authenticated, get_session, get_auth_headers


@click.command('list-workspace')
def list_workspace():
    """List all workspaces and extensions."""
    
    click.echo("📋 Listing workspaces and extensions...")
    
    # List local extensions (directories with plugin-manifest.json)
    click.echo("\n🏠 Local Extensions:")
    local_extensions = find_local_extensions()
    
    if local_extensions:
        for ext_path, manifest in local_extensions:
            name = manifest.get('name', 'Unknown')
            version = manifest.get('version', 'Unknown')
            ext_type = manifest.get('type', 'web')
            click.echo(f"\t📦 {name} (v{version}) - {ext_type}")
            click.echo(f"\t\t📁 {ext_path}")
    else:
        click.echo("  ℹ️ No local extensions found")
    
    # List remote workspaces if authenticated
    if is_authenticated():
        click.echo("\n☁️ Remote Workspaces:")
        list_remote_workspaces()
    else:
        click.echo("\n☁️ Remote Workspaces:")
        click.echo("\t❌ Not authenticated. Run 'pet login' to see remote workspaces.")


def find_local_extensions(search_dir="."):
    """Find all local extension projects."""
    extensions = []
    search_path = Path(search_dir)
    
    # Search current directory and subdirectories
    for item in search_path.rglob("plugin-manifest.json"):
        try:
            with open(item, 'r', encoding='utf-8') as f:  # Added encoding for consistency
                manifest = json.load(f)
            extensions.append((item.parent, manifest))
        except (json.JSONDecodeError, IOError, UnicodeDecodeError):
            continue
    
    return extensions


def list_remote_workspaces():
    """List remote workspaces using real API."""
    session = get_session()
    
    click.echo(f"\t🌐 Server: https://id-api.aqaryone.com")
    click.echo(f"\t👤 User: {session['username']}")

    try:
        # Get authentication headers
        headers = get_auth_headers()
        
        # Make API call to get user's companies/workspaces
        api_url = 'https://id-api.aqaryone.com/api/v1/company/entity/user'
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            companies = response.json()
            
            if not companies:
                click.echo("  ℹ️ No workspaces found")
                return
            
            click.echo(f"\t📊 Found {len(companies)} workspace(s)")
            
            for company in companies:
                click.echo(f"\n\t📂 Workspace: {company['name']}")
                click.echo(f"\t\t🆔 ID: {company['id']}")
                click.echo(f"\t\t📧 Email: {company['email']}")
                click.echo(f"\t\t📞 Phone: {company['phone']}")
                click.echo(f"\t\t📍 Address: {company['address']}")

                # Note: Extensions would need a separate API endpoint
                # For now, show placeholder text
                click.echo(f"\t\t📦 Extensions: [API endpoint needed for extensions]")

        elif response.status_code == 401:
            click.echo("\t❌ Authentication failed. Please run 'pet login' again.")
        elif response.status_code == 403:
            click.echo("\t❌ Access forbidden. Check your permissions.")
        else:
            click.echo(f"\t❌ Failed to load workspaces: HTTP {response.status_code}")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    click.echo(f"\t\tError: {error_data['error']}")
            except:
                click.echo(f"\t\tResponse: {response.text[:200]}...")

    except requests.exceptions.Timeout:
        click.echo("\t❌ Request timed out. Please check your internet connection.")
    except requests.exceptions.ConnectionError:
        click.echo("\t❌ Could not connect to the server. Please check your internet connection.")
    except requests.exceptions.RequestException as e:
        click.echo(f"\t❌ Network error: {e}")
    except json.JSONDecodeError:
        click.echo("\t❌ Invalid response format from server.")
    except Exception as e:
        click.echo(f"\t❌ Error listing workspaces: {e}")