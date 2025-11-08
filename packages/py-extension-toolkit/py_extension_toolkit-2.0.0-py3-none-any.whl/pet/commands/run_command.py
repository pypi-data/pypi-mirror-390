"""Run command for starting the development server."""

import click
import os
import json
import subprocess
import sys
import shutil
from pathlib import Path
from flask import Flask, send_from_directory, render_template_string
from flask_cors import CORS
import threading
import time
import webbrowser


@click.command()
@click.option('--port', help='Port to run the development server on')
@click.option('--host', help='Host to bind the server to')
@click.option('--open-browser/--no-browser', default=None, help='Open browser automatically')
def run(port, host, open_browser):
    """Start the development server for the extension."""
    
    # Check if we're in an extension project (Node.js or Python)
    if Path('package.json').exists():
        # Node.js project
        return run_nodejs_project(port, host, open_browser)
    elif Path('plugin-manifest.json').exists():
        # Python project
        return run_python_project(port, host, open_browser)
    else:
        click.echo("❌ No package.json or plugin-manifest.json found. Make sure you're in an extension project directory.", err=True)
        click.echo("💡 Use 'pet init' to create a new extension project.")
        return


def run_python_project(port, host, open_browser):
    """Run a Python-based extension project."""
    
    # Interactive configuration if not provided
    if not port:
        port = click.prompt('🌐 Server port', default=5000, type=int)
    else:
        port = int(port)  # Ensure port is an integer
    
    if not host:
        host = click.prompt('🖥️ Server host', default='127.0.0.1')
    
    if open_browser is None:
        open_browser = click.confirm('🌍 Open browser automatically?', default=True)
    
    # Load manifest
    try:
        with open('plugin-manifest.json', 'r') as f:
            manifest = json.load(f)
    except Exception as e:
        click.echo(f"❌ Error reading plugin-manifest.json: {e}", err=True)
        return
    
    extension_type = manifest.get('type', 'web')
    entry_point = manifest.get('entry_point', 'app/widget.html')
    
    # Check if this is a Node.js project
    package_json_path = Path('package.json')
    if package_json_path.exists():
        click.echo("🔍 Detected Node.js project")
        run_nodejs_extension(port, host, open_browser, manifest)
    elif extension_type == 'python':
        # Always use HTTPS
        protocol = 'https'
        click.echo(f"🚀 Starting Python development server for '{manifest['name']}'...")
        click.echo(f"🌐 Server: {protocol}://{host}:{port}")
        run_python_extension(entry_point, port, host, open_browser)
    else:
        # Always use HTTPS
        protocol = 'https'
        click.echo(f"🚀 Starting web development server for '{manifest['name']}'...")
        click.echo(f"🌐 Server: {protocol}://{host}:{port}")
        run_web_extension(entry_point, port, host, open_browser, manifest)


def run_nodejs_extension(port, host, open_browser, manifest):
    """Run a Node.js/Express-based extension."""
    
    # Check if Node.js is available
    # Prefer using shutil.which so we can detect node.exe/node on Windows and WSL
    node_exe = shutil.which('node') or shutil.which('node.exe')
    if not node_exe:
        click.echo("❌ Node.js not found. Please install Node.js first.", err=True)
        click.echo("Visit: https://nodejs.org/")
        return
    
    # Check if npm dependencies are installed
    if not Path('node_modules').exists():
        click.echo("📦 Installing NPM dependencies...")
        # Find npm executable (npm, npm.cmd, npm.exe)
        npm_cmd = shutil.which('npm') or shutil.which('npm.cmd') or shutil.which('npm.exe')
        if not npm_cmd:
            click.echo("❌ NPM not found. Please install Node.js and npm first.")
            return
        try:
            result = subprocess.run([npm_cmd, 'install'], capture_output=True, text=True)
            if result.returncode != 0:
                click.echo("❌ Failed to install dependencies")
                click.echo(result.stderr)
                return
        except subprocess.CalledProcessError:
            click.echo("❌ Failed to install dependencies via npm")
            return
    
    # Check if port is in use
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        click.echo(f"❌ {port} port is already in use")
        return
    
    click.echo(f"🚀 Starting Node.js server for '{manifest['name']}'...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PORT'] = str(port)
    env['HOST'] = host
    env['NODE_ENV'] = 'development'
    
    if open_browser:
        # Open browser after a short delay
        def open_browser_delayed():
            time.sleep(3)  # Give server more time to start
            # Always use HTTPS
            protocol = 'https'
            
            def is_wsl():
                try:
                    with open('/proc/version', 'r') as f:
                        return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
                except:
                    return False
            
            server_url = f'{protocol}://{host}:{port}'
            if is_wsl():
                try:
                    subprocess.run(['cmd.exe', '/c', 'start', server_url], capture_output=True, timeout=5)
                except:
                    click.echo(f"💡 WSL detected: Please manually open {server_url} in your browser")
            else:
                try:
                    webbrowser.open(server_url)
                except:
                    click.echo(f"💡 Could not auto-open browser. Please open {server_url} manually")
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    try:
        # Always use HTTPS
        protocol = 'https'
        
        # Start the Node.js server
        click.echo(f"Pet running at {protocol}://{host}:{port}")
        click.echo(f"🔒 HTTPS server with self-signed certificates")
        click.echo(f"Note: Click 'Advanced' → 'Proceed to {host} (unsafe)' in your browser to authorize the certificate.")
        
        # Prefer npm_cmd found earlier if present, fall back to 'npm'
        npm_cmd = shutil.which('npm') or shutil.which('npm.cmd') or shutil.which('npm.exe') or 'npm'
        subprocess.run([npm_cmd, 'start'], env=env, cwd=os.getcwd())
    except KeyboardInterrupt:
        click.echo("\n🛑 Development server stopped.")
    except Exception as e:
        click.echo(f"❌ Error starting server: {e}")


def run_python_extension(entry_point, port, host, open_browser):
    """Run a Python-based extension."""
    if not Path(entry_point).exists():
        click.echo(f"❌ Entry point file not found: {entry_point}", err=True)
        return
    
    # Install requirements if requirements.txt exists
    if Path('requirements.txt').exists():
        click.echo("📦 Installing requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      capture_output=True)
    
    # Set environment variables
    env = os.environ.copy()
    env['FLASK_APP'] = entry_point
    env['FLASK_ENV'] = 'development'
    env['FLASK_RUN_PORT'] = str(port)
    env['FLASK_RUN_HOST'] = host
    
    if open_browser:
        # Open browser after a short delay using WSL-aware method
        def open_browser_delayed():
            time.sleep(2)
            # Always use HTTPS
            protocol = 'https'
            url = f'{protocol}://{host}:{port}'
            
            # WSL detection and browser opening
            def is_wsl():
                try:
                    return 'WSL' in os.environ.get('WSL_DISTRO_NAME', '') or \
                           'wsl' in os.uname().release.lower() or \
                           'microsoft' in os.uname().release.lower()
                except:
                    return False
            
            try:
                if is_wsl():
                    # Use cmd.exe to open browser in WSL
                    subprocess.run(['cmd.exe', '/c', 'start', url], check=True)
                else:
                    # Use standard webbrowser for non-WSL environments
                    import webbrowser
                    webbrowser.open(url)
            except Exception as e:
                click.echo(f"⚠️ Could not open browser automatically: {e}")
                click.echo(f"🌐 Please open {url} manually in your browser")
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    click.echo("🔧 Starting Python Flask server...")
    
    # Run the Python application
    try:
        subprocess.run([sys.executable, entry_point], env=env, cwd=os.getcwd())
    except KeyboardInterrupt:
        click.echo("\n🛑 Development server stopped.")


def run_web_extension(entry_point, port, host, open_browser, manifest):
    """Run a web-based extension with a simple file server."""
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/')
    def index():
        """Serve the main entry point."""
        try:
            if Path(entry_point).exists():
                return send_from_directory('.', entry_point)
            else:
                return render_template_string(get_default_page(manifest)), 404
        except Exception as e:
            return f"Error serving file: {e}", 500
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        """Serve static files."""
        try:
            return send_from_directory('.', filename)
        except Exception as e:
            return f"File not found: {filename}", 404
    
    @app.route('/api/manifest')
    def get_manifest():
        """Serve the plugin-manifest.json for development tools."""
        return manifest
    
    if open_browser:
        # Determine protocol based on host
        protocol = 'http' if host in ['localhost', '127.0.0.1', '0.0.0.0'] or host.startswith('192.168.') or host.startswith('10.') or host.startswith('172.') else 'https'
        server_url = f"{protocol}://{host}:{port}"
        
        def is_wsl():
            """Check if running in Windows Subsystem for Linux."""
            try:
                with open('/proc/version', 'r') as f:
                    return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
            except:
                return False
        
        # Open browser after a short delay
        def open_browser_delayed():
            time.sleep(1)
            if is_wsl():
                # In WSL, try to open browser in Windows
                try:
                    subprocess.run(['cmd.exe', '/c', 'start', server_url], capture_output=True, timeout=5)
                except:
                    click.echo(f"💡 WSL detected: Please manually open {server_url} in your browser")
            else:
                try:
                    webbrowser.open(server_url)
                except:
                    click.echo(f"💡 Could not auto-open browser. Please open {server_url} manually")
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    click.echo("🔧 Starting development server...")
    
    try:
        app.run(host=host, port=port, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        click.echo("\n🛑 Development server terminated!!.")


def get_default_page(manifest):
    """Return a default page when entry point is not found."""
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{manifest.get("name", "Extension")} - Development</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .error {{ color: #d32f2f; }}
        .info {{ color: #1976d2; }}
        code {{ 
            background: #f5f5f5; 
            padding: 2px 6px; 
            border-radius: 3px; 
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 {manifest.get("name", "Extension")} Development Server</h1>
        <p class="error">⚠️ Entry point file not found: <code>{manifest.get("entry_point", "app/widget.html")}</code></p>
        <p class="info">The development server is running, but your entry point file is missing.</p>
        <hr>
        <h3>Extension Info:</h3>
        <p><strong>Name:</strong> {manifest.get("name", "N/A")}</p>
        <p><strong>Version:</strong> {manifest.get("version", "N/A")}</p>
        <p><strong>Type:</strong> {manifest.get("type", "web")}</p>
        <p><strong>Description:</strong> {manifest.get("description", "N/A")}</p>
    </div>
</body>
</html>
    '''


def run_nodejs_project(port, host, open_browser):
    """Run a Node.js-based extension project."""
    
    # Interactive configuration if not provided
    if not port:
        port = click.prompt('🌐 Server port', default=5000, type=int)
    else:
        port = int(port)  # Ensure port is an integer
    
    if not host:
        host = click.prompt('🖥️ Server host', default='127.0.0.1')
    
    if open_browser is None:
        open_browser = click.confirm('🌍 Open browser automatically?', default=True)
    
    # Load package.json
    try:
        with open('package.json', 'r') as f:
            package_json = json.load(f)
    except Exception as e:
        click.echo(f"❌ Error reading package.json: {e}", err=True)
        return
    
    project_name = package_json.get('name', 'Extension')
    
    # Always use HTTPS
    protocol = 'https'
    server_url = f"{protocol}://{host}:{port}"
    
    click.echo(f"🚀 Starting development server for '{project_name}'...")
    click.echo(f"📋 Type: Node.js Extension")
    click.echo(f"🌐 Server: {server_url}")
    
    # Check for existing port usage (like zet does)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    if result == 0:
        click.echo(f"{port} port is already in use")
        return
    sock.close()
    
    # Set environment variables for Node.js
    env = os.environ.copy()
    env['PORT'] = str(port)
    env['HOST'] = host
    
    def is_wsl():
        """Check if running in Windows Subsystem for Linux."""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
        except:
            return False
    
    if open_browser:
        # Open browser after a short delay
        def open_browser_delayed():
            time.sleep(3)  # Give server more time to start
            if is_wsl():
                # In WSL, try to open browser in Windows
                try:
                    subprocess.run(['cmd.exe', '/c', 'start', server_url], 
                                 capture_output=True, timeout=5)
                except:
                    click.echo(f"💡 WSL detected: Please manually open {server_url} in your browser")
            else:
                try:
                    webbrowser.open(server_url)
                except:
                    click.echo(f"💡 Could not auto-open browser. Please open {server_url} manually")
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    click.echo("🔧 Starting Node.js server...")
    click.echo(f"Pet running at {server_url}")
    if protocol == 'https':
        click.echo(f"Note: Please enable the host ({server_url}) in a new tab and authorize the connection by clicking Advanced->Proceed to {host} (unsafe).")
    
    try:
        # Run npm start or node server/index.js (updated for new structure)
        if 'scripts' in package_json and 'start' in package_json['scripts']:
            npm_cmd = shutil.which('npm') or shutil.which('npm.cmd') or shutil.which('npm.exe') or 'npm'
            subprocess.run([npm_cmd, 'start'], env=env, cwd=os.getcwd())
        else:
            # Try server/index.js first (new structure), then fallback to server.js
            node_exe = shutil.which('node') or shutil.which('node.exe') or 'node'
            if Path('server/index.js').exists():
                subprocess.run([node_exe, 'server/index.js'], env=env, cwd=os.getcwd())
            elif Path('server.js').exists():
                subprocess.run([node_exe, 'server.js'], env=env, cwd=os.getcwd())
            else:
                click.echo("❌ No server file found (server/index.js or server.js)")
                return

    except FileNotFoundError:
        click.echo("❌ Node.js or npm not found. Please install Node.js and npm.")
        click.echo("💡 Visit https://nodejs.org/ to download and install Node.js")

    except KeyboardInterrupt:
        click.echo("\n🛑 Development server terminated!!")