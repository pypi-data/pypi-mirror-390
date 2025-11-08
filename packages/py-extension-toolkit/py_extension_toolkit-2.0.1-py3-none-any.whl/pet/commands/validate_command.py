"""Validate command for checking extension projects."""

import click
import json
from pathlib import Path


@click.command()
@click.option('--strict', is_flag=True, help='Enable strict validation')
def validate(strict):
    """Validate the current extension project."""
    
    errors = []
    warnings = []
    
    # Check plugin-manifest.json
    manifest_path = Path('plugin-manifest.json')
    if not manifest_path.exists():
        errors.append("plugin-manifest.json is missing")
        click.echo("❌ Validation failed!")
        return
    
    # Get project name from manifest for the validation message
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        project_name = manifest.get('name', 'extension')
        click.echo(f"🔍 Validating {project_name} project...")
    except:
        click.echo("🔍 Validating extension project...")
        manifest = {}
    
    # Re-read and validate manifest structure (we already read it above for the project name)
    if not manifest:  # If we couldn't read it above, try again with proper error handling
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:  # Added encoding
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in plugin-manifest.json: {e}")
            click.echo("❌ Validation failed!")
            return
        except UnicodeDecodeError as e:
            errors.append(f"Encoding error in plugin-manifest.json: {e}")
            click.echo("❌ Validation failed!")
            return
        except IOError as e:
            errors.append(f"Could not read plugin-manifest.json: {e}")
            click.echo("❌ Validation failed!")
            return
    
    # Validate required fields
    required_fields = ['name', 'version', 'type']
    for field in required_fields:
        if field not in manifest:
            errors.append(f"Required field '{field}' missing in plugin-manifest.json")
        elif not manifest[field]:  # Check for empty values
            errors.append(f"Required field '{field}' is empty in plugin-manifest.json")
    
    # Validate field types and values
    if 'name' in manifest and not isinstance(manifest['name'], str):
        errors.append("Field 'name' must be a string")
    
    if 'version' in manifest:
        if not isinstance(manifest['version'], str):
            errors.append("Field 'version' must be a string")
        # Basic semver validation
        elif not manifest['version'].replace('.', '').replace('-', '').replace('+', '').replace('_', '').replace('alpha', '').replace('beta', '').replace('rc', '').isalnum():
            warnings.append("Version format may not follow semantic versioning")
    
    if 'type' in manifest:
        valid_types = ['web', 'python', 'api', 'microservice', 'dashboard', 'connector', 'webhook', 'widget', 'service', 'cli']
        if manifest['type'] not in valid_types:
            warnings.append(f"Extension type '{manifest['type']}' is not a recognized type. Valid types: {', '.join(valid_types)}")
    
    # Check entry point
    entry_point = manifest.get('entry_point')
    if entry_point and not Path(entry_point).exists():
        errors.append(f"Entry point file not found: {entry_point}")
    elif not entry_point:
        warnings.append("No entry_point specified in plugin-manifest.json")
    
    # Validate plugin-plugin-manifest.json if it exists
    plugin_manifest_path = Path('plugin-plugin-manifest.json')
    if plugin_manifest_path.exists():
        try:
            with open(plugin_manifest_path, 'r', encoding='utf-8') as f:
                plugin_manifest = json.load(f)
            
            # Check for service field
            if 'service' not in plugin_manifest:
                warnings.append("plugin-plugin-manifest.json should specify a 'service' field")
            elif not plugin_manifest['service']:
                warnings.append("'service' field in plugin-plugin-manifest.json is empty")
            else:
                valid_services = ['CRM', 'Projects', 'Books', 'Invoice', 'Inventory', 'Desk', 'Analytics', 'Creator', 'Forms', 'Survey', 'Mail', 'Meeting', 'Connect', 'Flow', 'Sign', 'People', 'Recruit', 'Social', 'Campaigns', 'SalesIQ', 'PageSense', 'Sites', 'Commerce', 'Catalyst', 'Cliq', 'WorkDrive', 'Show', 'Learn', 'Sprints', 'BugTracker', 'Vault', 'One', 'Writer', 'Sheet', 'Show']
                if plugin_manifest['service'] not in valid_services:
                    warnings.append(f"Unknown service '{plugin_manifest['service']}' in plugin-plugin-manifest.json. Consider using a recognized Zoho service.")
                    
        except json.JSONDecodeError as e:
            warnings.append(f"Invalid JSON in plugin-plugin-manifest.json: {e}")
        except (IOError, UnicodeDecodeError) as e:
            warnings.append(f"Could not read plugin-plugin-manifest.json: {e}")
    
    # Type-specific validation
    extension_type = manifest.get('type', 'web')
    
    if extension_type == 'web':
        validate_web_extension(manifest, errors, warnings, strict)
    elif extension_type == 'python':
        validate_python_extension(manifest, errors, warnings, strict)
    
    # Report results
    if errors:
        click.echo("❌ Validation failed!")
        for error in errors:
            click.echo(f"  ❌ {error}")
    else:
        click.echo("✅ Validation passed!")
    
    if warnings:
        click.echo("⚠️ Warnings:")
        for warning in warnings:
            click.echo(f"  ⚠️ {warning}")
    
    return len(errors) == 0


def validate_web_extension(manifest, errors, warnings, strict):
    """Validate web extension specific requirements."""
    entry_point = manifest.get('entry_point', 'app/widget.html')  # Updated for new structure
    
    if not Path(entry_point).exists():
        errors.append(f"Web entry point not found: {entry_point}")
    
    # Check for package.json (Node.js projects need this)
    if not Path('package.json').exists():
        warnings.append("package.json not found - Node.js projects should have this file")
    
    # Check for server/index.js (Express server in new structure)
    if not Path('server/index.js').exists():
        if not Path('server.js').exists():  # Fallback to old structure
            warnings.append("server/index.js or server.js not found - Express projects should have a server file")
        else:
            warnings.append("Consider moving server.js to server/index.js for better organization")
    
    # Check for plugin-plugin-manifest.json (new requirement)
    if not Path('plugin-plugin-manifest.json').exists():
        warnings.append("plugin-plugin-manifest.json not found - extensions should specify the target service")
    
    # Check for app directory structure (new project structure)
    app_dir = Path('app')
    if not app_dir.exists():
        warnings.append("app directory not found - extensions should have an app directory")
    else:
        # Check for widget.html in app directory
        if not (app_dir / 'widget.html').exists():
            warnings.append("app/widget.html not found - main widget file is missing")
        
        # Check for translations directory
        translations_dir = app_dir / 'translations'
        if not translations_dir.exists():
            warnings.append("app/translations directory not found")
        elif not list(translations_dir.glob('*.json')):
            warnings.append("No translation files found in app/translations")
    
    # Check for server directory structure
    server_dir = Path('server')
    if not server_dir.exists():
        warnings.append("server directory not found - extensions should have a server directory")
    
    # Check for HTTPS certificates
    if not Path('cert.pem').exists():
        warnings.append("cert.pem not found - HTTPS certificate missing")
    if not Path('key.pem').exists():
        warnings.append("key.pem not found - HTTPS private key missing")
    
    # Check certificate generation script
    if Path('generate-cert.sh').exists():
        # Check if certificates are placeholder files
        try:
            with open('cert.pem', 'r', encoding='utf-8') as f:
                cert_content = f.read()
            if 'placeholder' in cert_content.lower() or 'BEGIN CERTIFICATE' not in cert_content:
                warnings.append("Certificate appears to be a placeholder - run 'bash generate-cert.sh' to generate proper certificates")
        except:
            pass
    
    # Check Node.js dependencies if package.json exists
    package_json_path = Path('package.json')
    if package_json_path.exists():
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # Check for required dependencies (updated for new structure)
            dependencies = package_data.get('dependencies', {})
            required_deps = ['express', 'body-parser', 'morgan']
            recommended_deps = ['errorhandler', 'serve-index', 'chalk']
            
            for dep in required_deps:
                if dep not in dependencies:
                    warnings.append(f"Missing required dependency: {dep}")
            
            for dep in recommended_deps:
                if dep not in dependencies:
                    warnings.append(f"Missing recommended dependency: {dep}")
            
            # Check start script
            scripts = package_data.get('scripts', {})
            if 'start' not in scripts:
                warnings.append("Missing 'start' script in package.json")
            elif scripts['start'] != 'node server/index.js':
                if scripts['start'] != 'node server.js':  # Accept old structure
                    warnings.append("Start script should be 'node server/index.js' for new project structure")
                    
        except (json.JSONDecodeError, IOError):
            warnings.append("Could not read package.json file")


def validate_python_extension(manifest, errors, warnings, strict):
    """Validate Python extension specific requirements."""
    entry_point = manifest.get('entry_point', 'src/main.py')
    
    if not Path(entry_point).exists():
        errors.append(f"Python entry point not found: {entry_point}")
    
    # Check for requirements.txt
    if not Path('requirements.txt').exists():
        warnings.append("requirements.txt not found")
    
    # Check Python syntax if strict mode
    if strict and Path(entry_point).exists():
        try:
            with open(entry_point, 'r', encoding='utf-8') as f:  # Added encoding
                code = f.read()
            compile(code, entry_point, 'exec')
        except SyntaxError as e:
            errors.append(f"Syntax error in {entry_point}: {e}")
        except UnicodeDecodeError as e:
            errors.append(f"Encoding error in {entry_point}: {e}")
        except IOError as e:
            errors.append(f"Could not read {entry_point}: {e}")
    
    # Check for src directory structure
    src_dir = Path('src')
    if not src_dir.exists():
        warnings.append("src directory not found")
    
    # Check for templates directory if Flask is used
    requirements_file = Path('requirements.txt')
    if requirements_file.exists():
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:  # Added encoding and error handling
                requirements = f.read()
                if 'flask' in requirements.lower():
                    if not Path('templates').exists():
                        warnings.append("Flask detected but templates directory not found")
                    if not Path('static').exists():
                        warnings.append("Flask detected but static directory not found")
        except (IOError, UnicodeDecodeError) as e:
            warnings.append(f"Could not read requirements.txt: {e}")
    
    # Check for __init__.py in src directory
    if src_dir.exists() and not (src_dir / '__init__.py').exists():
        warnings.append("src/__init__.py not found - Python packages should have this file")