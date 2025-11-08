"""Pull command for downloading extensions."""

import click
from pathlib import Path
from .login_command import is_authenticated, get_session


@click.command()
@click.option('--extension', '-e', help='Name of the extension to pull')
@click.option('--version', '-v', help='Specific version to pull (default: latest)')
@click.option('--output', '-o', help='Output directory (default: extension name)')
def pull(extension, version, output):
    """Pull an extension from the server."""
    
    if not is_authenticated():
        click.echo("❌ Not authenticated. Please run 'pet login' first.", err=True)
        return
    
    session = get_session()
    
    # Interactive prompts if not provided
    if not extension:
        click.echo("\n📥 Pull Extension from Server")
        extension = click.prompt('📦 Extension name to pull')
    
    if not version:
        if click.confirm('🏷️ Do you want to specify a version? (default: latest)', default=False):
            version = click.prompt('Version')
        else:
            version = None
    
    # Set output directory
    if not output:
        suggested_output = extension
        if click.confirm(f'📁 Save to directory "{suggested_output}"?', default=True):
            output = suggested_output
        else:
            output = click.prompt('📁 Output directory name')
    
    output_path = Path(output)
    
    if output_path.exists():
        if not click.confirm(f"Directory '{output}' already exists. Continue?"):
            return
    
    click.echo(f"📥 Pulling extension: {extension}")
    if version:
        click.echo(f"🏷️ Version: {version}")
    else:
        click.echo(f"🏷️ Version: latest")
    
    click.echo(f"🌐 Server: {session['server']}")
    
    # In a real implementation, you would download from the actual server
    # For this demo, we'll simulate the download
    simulate_pull(extension, version, output_path, session)


def simulate_pull(extension, version, output_path, session):
    """Simulate pulling from server (demo implementation)."""
    click.echo("📤 Downloading extension...")
    
    # Simulate download progress
    import time
    for i in range(0, 101, 15):
        click.echo(f"\\r📊 Download progress: {i}%", nl=False)
        time.sleep(0.1)
    
    click.echo("\n📦 Extracting extension...")
    
    # Create a demo extension structure since we can't actually download
    create_demo_extension(output_path, extension, version or "1.0.0")
    
    click.echo("✅ Extension pulled successfully!")
    click.echo(f"📁 Location: {output_path.absolute()}")
    click.echo(f"🚀 Next steps:")
    click.echo(f"   cd {output_path}")
    click.echo(f"   pet run")
    
    # In real implementation, you would:
    # 1. Download the extension package from server
    # 2. Verify package integrity
    # 3. Extract to specified directory
    # 4. Handle authentication and errors
    
    '''
    Real implementation would look like:
    
    try:
        # Build download URL
        url_path = f'/api/extensions/{extension}/download'
        if version:
            url_path += f'?version={version}'
        
        headers = {'Authorization': f'Bearer {session["token"]}'}
        
        response = requests.get(
            f'{session["server"]}{url_path}',
            headers=headers,
            stream=True
        )
        
        if response.status_code == 200:
            # Download to temporary file
            temp_file = Path(f'{extension}.zip')
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Extract the package
            with zipfile.ZipFile(temp_file, 'r') as zf:
                zf.extractall(output_path)
            
            # Clean up
            temp_file.unlink()
            
            click.echo("✅ Extension pulled successfully!")
            
        elif response.status_code == 404:
            click.echo(f"❌ Extension '{extension}' not found.")
        else:
            click.echo(f"❌ Pull failed: {response.text}")
            
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {e}")
    except Exception as e:
        click.echo(f"❌ Error pulling extension: {e}")
    '''


def create_demo_extension(output_path, name, version):
    """Create a demo extension for simulation purposes."""
    import json
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create manifest
    manifest = {
        "name": name,
        "version": version,
        "description": f"Downloaded extension: {name}",
        "type": "web",
        "entry_point": "app/index.html"
    }
    
    with open(output_path / 'plugin-manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    # Create basic structure
    app_dir = output_path / 'app'
    app_dir.mkdir(exist_ok=True)
    
    # Create simple HTML file
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>{name}</title>
</head>
<body>
    <h1>Welcome to {name}</h1>
    <p>This extension was pulled from the server.</p>
    <p>Version: {version}</p>
</body>
</html>'''
    
    with open(app_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)