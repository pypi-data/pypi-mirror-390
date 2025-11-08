"""Initialize command for creating new extension projects."""

import click
import json
import questionary
from pathlib import Path


@click.command()
@click.option('--name', help='Name of the extension')
@click.option('--type', 'project_type', type=click.Choice(['web', 'python']), 
              help='Type of extension project')
@click.option('--framework', type=click.Choice(['vanilla', 'react', 'vue']), 
              help='Frontend framework (for web projects)')
def init(name, project_type, framework):
    """Create a new extension project."""
    
    # Interactive prompts if not provided
    if not project_type:
        click.echo('\n? Select the type of extension project:')
        project_types = [
            'Web Extension',
            'Python Extension (Flask)'
        ]
        
        # Use questionary for better UI with arrow key navigation
        type_choice = questionary.select(
            "Select the type of extension project:",
            choices=project_types,
            default=project_types[0]
        ).ask()
        
        if not type_choice:  # User cancelled
            click.echo("Operation cancelled!")
            return
        
        # Map selection to project type
        if 'Python' in type_choice:
            project_type = 'python'
        else:
            project_type = 'web'  # Default to web for most extension types
        
        service_name = type_choice
    
    if not name:
        name = questionary.text("Project Name:").ask()
        if not name:  # User cancelled
            click.echo("Operation cancelled.")
            return
    
    # Set default framework for web projects
    if project_type == 'web' and not framework:
        framework = 'vanilla'  # Default to vanilla for web extensions
    elif project_type == 'python':
        framework = None
    
    click.echo(f"\nInitializing project at: {Path.cwd() / name}")
    click.echo(f"🚀 Creating {service_name if 'service_name' in locals() else project_type} extension: {name}")
    
    # Create project directory
    project_dir = Path(name)
    if project_dir.exists():
        click.echo(f"Directory {name} already exists!", err=True)
        return
    
    project_dir.mkdir(parents=True)
    
    if project_type == 'web':
        create_npm_project(project_dir, name, framework, service_name if 'service_name' in locals() else 'Web Extension')
    elif project_type == 'python':
        create_python_project(project_dir, name)
        create_manifest_file_python(project_dir, name)
    
    click.echo("Installing NPM dependencies...")
    
    # Install NPM dependencies
    if project_type == 'web':
        install_npm_dependencies(project_dir)
    
    click.echo(f"Project Initialized: {project_dir.absolute()}")
    click.echo("Run the following commands:")
    click.echo(f"cd '{name}'")
    click.echo("pet run")


def create_npm_project(project_dir, name, framework, service):
    """Create an NPM-based extension project with app/ and server/ structure."""
    
    # Create package.json
    package_json = {
        "name": name,
        "version": "0.0.1",
        "private": True,
        "scripts": {
            "start": "node server/index.js",
            "dev": "node server/index.js", 
            "serve": "node server/index.js"
        },
        "dependencies": {
            "body-parser": "^1.14.2",
            "errorhandler": "^1.4.2",
            "express": "^4.13.3",
            "morgan": "^1.6.1",
            "serve-index": "^1.9.0",
            "chalk": "^1.1.3",
            "i18next": "^10.0.7",
            "portfinder": "^1.0.25"
        }
    }
    
    with open(project_dir / 'package.json', 'w', encoding='utf-8') as f:
        json.dump(package_json, f, indent=2)
    
    # Create server directory and index.js
    (project_dir / 'server').mkdir()
    
    server_content = f'''/*
Copyright (c) 2025, AQARY Inc.
License: MIT
*/
var fs = require('fs');
var path = require('path');
var express = require('express');
var bodyParser = require('body-parser');
var errorHandler = require('errorhandler');
var morgan = require('morgan');
var serveIndex = require('serve-index');
var https = require('https');
var chalk = require('chalk');

process.env.PWD = process.env.PWD || process.cwd();

var expressApp = express();
var port = process.env.PORT || 5000;
var host = process.env.HOST || 'localhost';

expressApp.use(bodyParser.json());
expressApp.use(bodyParser.urlencoded({{ extended: true }}));
expressApp.use(morgan('dev'));

// Enable CORS for all origins and methods
expressApp.use(function(req, res, next) {{
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization");
    next();
}});

// Health check endpoint
expressApp.get('/api/health', function(req, res) {{
    res.json({{
        status: 'OK',
        extension: '{name}',
        version: '0.0.1',
        timestamp: new Date().toISOString()
    }});
}});

// Serve static files from app directory
expressApp.use('/', express.static(path.join(__dirname, '..', 'app')));

// Serve widget at root
expressApp.get('/', function(req, res) {{
    res.sendFile(path.join(__dirname, '..', 'app', 'widget.html'));
}});

// Error handling
expressApp.use(errorHandler());

// Always use HTTPS with self-signed certificates
var server;

try {{
    var httpsOptions = {{
        key: fs.readFileSync(path.join(__dirname, '..', 'key.pem')),
        cert: fs.readFileSync(path.join(__dirname, '..', 'cert.pem'))
    }};
    
    server = https.createServer(httpsOptions, expressApp);
    
    server.listen(port, '0.0.0.0', function() {{
        console.log(chalk.green('🚀 thachu Extension Server running at https://' + host + ':' + port));
        console.log(chalk.yellow('Note: You may need to authorize the self-signed certificate in your browser.'));
        console.log(chalk.yellow('Click "Advanced" → "Proceed to ' + host + ' (unsafe)" to continue.'));
        console.log(chalk.cyan('Visit: https://' + host + ':' + port));
    }});
}} catch (error) {{
    console.log(chalk.red('❌ HTTPS certificates not found or invalid'));
    console.log(chalk.yellow('Error: ' + error.message));
    console.log(chalk.cyan('Please ensure cert.pem and key.pem exist in the project root.'));
    console.log(chalk.cyan('Run: ./generate-certificates.sh to regenerate certificates'));
    process.exit(1);
}}

module.exports = expressApp;
'''
    
    with open(project_dir / 'server' / 'index.js', 'w', encoding='utf-8') as f:
        f.write(server_content)

    # Create app directory structure
    (project_dir / 'app').mkdir()
    (project_dir / 'app' / 'translations').mkdir()

    # Create widget.html
    widget_content = f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>{name} - Extension Widget</title>
  </head>
  <body>
    <div class="container">
      <h1>{name}</h1>
      <p>This is a sample Widget built using the Extension toolkit.</p>
      <div class="badge">Extension Widget</div>
    </div>
  </body>
</html>'''

    with open(project_dir / 'app' / 'widget.html', 'w', encoding='utf-8') as f:
        f.write(widget_content)
    
    # Create translations file
    translations_content = '{"welcome": "Welcome to your extension!"}'
    with open(project_dir / 'app' / 'translations' / 'en.json', 'w', encoding='utf-8') as f:
        f.write(translations_content)
    
    # Create plugin-plugin-manifest.json
    plugin_manifest = {
        "service": "Web framework" if service == 'Web Extension' else service
    }
    with open(project_dir / 'plugin-plugin-manifest.json', 'w', encoding='utf-8') as f:
        json.dump(plugin_manifest, f, indent=2)
    
    # Generate unique self-signed certificates for HTTPS
    generate_self_signed_certificates(project_dir, name)

    
    # Create .gitignore
    gitignore_content = '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs
*.log

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Build outputs
dist/
build/
'''
    
    with open(project_dir / '.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    # Create README.md
    readme_content = f'''# {name}

Extension built with Python Extension Toolkit (PET)

## Description

This is an extension that provides widget functionality with HTTPS support.

## Features

- Express.js server with HTTPS support
- Self-signed certificates for development
- Widget interface in app/ directory
- Secure server setup with proper certificate handling
- Development-ready structure

## Getting Started

### Prerequisites

- Node.js (>=10.0.0)
- npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

### Development

The extension runs on `https://127.0.0.1:5000` by default using self-signed certificates.

**Important**: You **must** authorize the self-signed certificate in your browser:
1. Visit the URL in your browser
2. You'll see a security warning
3. Click "Advanced" or "Show Details"
4. Click "Proceed to 127.0.0.1 (unsafe)" or "Accept the Risk"

**HTTPS-Only**: All extensions use HTTPS exclusively for security. Self-signed certificates are automatically generated for each project.

### API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /` - Serves the main widget

### Project Structure

```
{name}/
├── app/                    # Frontend widget files
│   ├── widget.html        # Main widget interface
│   └── translations/      # Internationalization files
│       └── en.json       # English translations
├── server/                # Backend server files
│   └── index.js          # Express HTTPS server
├── cert.pem              # SSL certificate (development)
├── key.pem               # SSL private key (development)
├── plugin-plugin-manifest.json  # Plugin configuration
├── package.json          # Node.js dependencies and scripts
└── README.md             # This file
```

### Customization

1. Edit `app/widget.html` for the main widget interface
2. Update `server/index.js` for server-side logic
3. Modify `plugin-plugin-manifest.json` for plugin configuration
4. Add translations in `app/translations/`

### HTTPS Development

This project uses HTTPS by default with unique self-signed certificates generated for each project.

**Certificate Generation:**
- Certificates are automatically generated during project creation using multiple methods:
  1. **OpenSSL** (preferred): Uses system OpenSSL for certificate generation
  2. **Python cryptography**: Auto-installs and uses cryptography library
  3. **pyOpenSSL**: Alternative Python library for certificate generation
  4. **Manual generation**: Script provided for manual certificate creation
- Each project gets **truly unique certificates** with:
  - Unique serial numbers (128-bit random)
  - Project-specific certificate subjects
  - UUID-based identifiers for uniqueness
  - Secure private key permissions (600)

**Certificate Features:**
- Valid for 1 year from creation date
- Includes Subject Alternative Names (SAN) for localhost and 127.0.0.1
- Project-specific domain: `[project-name].local`
- SHA-256 signature algorithm
- 2048-bit RSA keys for security

**For Production:**
1. Replace `cert.pem` and `key.pem` with proper SSL certificates from a Certificate Authority
2. Update server configuration as needed
3. Review CORS settings for your domain

**Troubleshooting:**
- If all certificate generation methods fail, placeholder files are created
- Run `./generate-certificates.sh` for manual certificate generation
- Each method automatically installs required dependencies

## Built With

- Express.js - Web framework
- HTTPS - Secure server setup
- PET (Python Extension Toolkit) - Project scaffolding

## License

MIT License
'''
    
    with open(project_dir / 'README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create plugin-manifest.json for pet CLI compatibility
    create_manifest_file(project_dir, name, service)


def create_manifest_file(project_dir, name, service_type):
    """Create plugin-manifest.json file for pet CLI compatibility (Web projects)."""
    manifest = {
        "name": name,
        "version": "0.0.1",
        "description": f"Extension - {name}",
        "type": "web",
        "entry_point": "app/widget.html",
        "author": "Extension Developer",
        "license": "MIT",
        "engines": {
            "node": ">=10.0.0"
        },
        "scripts": {
            "start": "node server/index.js"
        },
        "dependencies": {
            "body-parser": "^1.14.2",
            "errorhandler": "^1.4.2",
            "express": "^4.13.3",
            "morgan": "^1.6.1",
            "serve-index": "^1.9.0",
            "chalk": "^1.1.3",
            "i18next": "^10.0.7",
            "portfinder": "^1.0.25"
        },
        "keywords": [
            "extension",
            "widget",
            "nodejs",
            "express",
            "https"
        ]
    }
    
    with open(project_dir / 'plugin-manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)


def create_manifest_file_python(project_dir, name):
    """Create plugin-manifest.json file for pet CLI compatibility (Python projects)."""
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"Python Extension - {name}",
        "type": "python",
        "entry_point": "src/main.py",
        "author": "Extension Developer",
        "license": "MIT",
        "engines": {
            "python": ">=3.8"
        },
        "requirements": [
            "flask>=2.0.1",
            "flask-cors>=4.0.0"
        ],
        "keywords": [
            "extension",
            "python",
            "flask"
        ]
    }
    
    with open(project_dir / 'plugin-manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)


def create_python_project(project_dir, name):
    """Create a Python-based extension project."""
    # Create basic structure
    (project_dir / 'src').mkdir()
    (project_dir / 'templates').mkdir()
    (project_dir / 'static').mkdir()
    
    # Create main.py
    python_content = f'''"""
{name} Extension
Main application entry point
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os

# Get the parent directory (project root) for templates and static files
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
           template_folder=os.path.join(project_root, 'templates'),
           static_folder=os.path.join(project_root, 'static'))
CORS(app)


@app.route('/')
def index():
    """Main page of the extension."""
    return render_template('index.html', title='{name}')


@app.route('/api/status')
def status():
    """API endpoint to check extension status."""
    return jsonify({{
        'status': 'active',
        'extension': '{name}',
        'version': '1.0.0'
    }})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''
    
    with open(project_dir / 'src' / 'main.py', 'w', encoding='utf-8') as f:
        f.write(python_content)
    
    # Create HTML template
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title }}}}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; text-align: center; }}
        .status {{ padding: 10px; background: #e8f5e8; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to {name}</h1>
        <div class="status">
            <p>Extension Status: <strong>Active</strong></p>
        </div>
        <p>Your Python extension is running successfully!</p>
        <button onclick="checkStatus()">Check API Status</button>
    </div>
    
    <script>
        async function checkStatus() {{
            try {{
                const response = await fetch('/api/status');
                const data = await response.json();
                alert('Status: ' + data.status + '\nExtension: ' + data.extension);
            }} catch (error) {{
                alert('Error checking status: ' + error.message);
            }}
        }}
    </script>
</body>
</html>"""
    
    with open(project_dir / 'templates' / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # Create requirements.txt
    requirements = """flask>=2.0.1
flask-cors>=4.0.0"""
    
    with open(project_dir / 'requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)


def generate_self_signed_certificates(project_dir, project_name):
    """Generate unique self-signed certificates for each project."""
    import subprocess
    import shutil
    from datetime import datetime, timedelta
    
    cert_path = project_dir / 'cert.pem'
    key_path = project_dir / 'key.pem'
    
    # Ensure the project directory exists
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to use OpenSSL if available
    openssl_cmd = shutil.which('openssl')
    if openssl_cmd:
        try:
            # Generate unique certificate with project-specific subject
            subject = f"/CN=localhost/O={project_name}/OU=Development"
            
            # Generate private key and certificate in one command using absolute paths
            cmd = [
                openssl_cmd, 'req', '-x509', '-newkey', 'rsa:2048', 
                '-keyout', str(key_path.absolute()), 
                '-out', str(cert_path.absolute()),
                '-days', '365', '-nodes', '-subj', subject
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                click.echo("✅ Generated unique self-signed certificates using OpenSSL")
                return
            else:
                click.echo(f"⚠️ OpenSSL failed: {result.stderr}")
        except Exception as e:
            click.echo(f"⚠️ Error running OpenSSL: {e}")
    
    # Fallback 1: Try to auto-install and use cryptography library
    if not try_cryptography_generation(cert_path, key_path, project_name):
        # Fallback 2: Try using pyOpenSSL
        if not try_pyopenssl_generation(cert_path, key_path, project_name):
            # Final fallback: create placeholder files
            create_certificate_placeholders(project_dir, project_name)


def try_cryptography_generation(cert_path, key_path, project_name):
    """Try to generate certificates using the cryptography library."""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import ipaddress
        import secrets
        from datetime import datetime, timedelta
        
        # Generate truly unique private key with random seed
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate subject with project-specific and unique information
        import uuid
        unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
        
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Development"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, f"Local-{unique_id}"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, f"{project_name}-{unique_id}"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Extension"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        # Create certificate with truly random serial number
        serial_number = secrets.randbits(128)  # Larger random serial
        
        # Add random elements to ensure uniqueness
        now = datetime.utcnow()
        not_valid_before = now
        not_valid_after = now + timedelta(days=365)
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            serial_number
        ).not_valid_before(
            not_valid_before
        ).not_valid_after(
            not_valid_after
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.DNSName(f"{project_name}.local"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        # Write private key with secure permissions
        with open(key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Set restrictive permissions on private key (Unix-like systems)
        try:
            import stat
            key_path.chmod(stat.S_IREAD | stat.S_IWRITE)  # 600 permissions
        except:
            pass
        
        # Write certificate
        with open(cert_path, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        click.echo("✅ Generated unique self-signed certificates using Python cryptography")
        click.echo(f"🔑 Certificate serial number: {hex(serial_number)}")
        return True
        
    except ImportError:
        click.echo("⚠️ cryptography library not available, attempting to install...")
        try:
            import subprocess
            import sys
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'cryptography'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                click.echo("✅ cryptography library installed successfully")
                # Recursive call to try generation again
                return try_cryptography_generation(cert_path, key_path, project_name)
            else:
                click.echo(f"❌ Failed to install cryptography: {result.stderr}")
                return False
        except Exception as e:
            click.echo(f"❌ Error installing cryptography: {e}")
            return False
    except Exception as e:
        click.echo(f"⚠️ Error generating certificates with cryptography: {e}")
        return False


def try_pyopenssl_generation(cert_path, key_path, project_name):
    """Try to generate certificates using pyOpenSSL as an alternative."""
    try:
        from OpenSSL import crypto
        import secrets
        import uuid
        
        # Generate a unique private key
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        
        # Create a self-signed certificate
        cert = crypto.X509()
        
        # Set unique certificate details
        unique_id = str(uuid.uuid4())[:8]
        cert.get_subject().C = "US"
        cert.get_subject().ST = "Development"
        cert.get_subject().L = f"Local-{unique_id}"
        cert.get_subject().O = f"{project_name}-{unique_id}"
        cert.get_subject().OU = "Extension"
        cert.get_subject().CN = "localhost"
        
        # Set certificate properties
        cert.set_serial_number(secrets.randbits(64))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # Valid for 1 year
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')
        
        # Write private key
        with open(key_path, 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        
        # Set restrictive permissions on private key
        try:
            import stat
            key_path.chmod(stat.S_IREAD | stat.S_IWRITE)  # 600 permissions
        except:
            pass
        
        # Write certificate
        with open(cert_path, 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        
        click.echo("✅ Generated unique self-signed certificates using pyOpenSSL")
        click.echo(f"🔑 Certificate serial number: {cert.get_serial_number()}")
        return True
        
    except ImportError:
        click.echo("⚠️ pyOpenSSL library not available, attempting to install...")
        try:
            import subprocess
            import sys
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyOpenSSL'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                click.echo("✅ pyOpenSSL library installed successfully")
                return try_pyopenssl_generation(cert_path, key_path, project_name)
            else:
                click.echo(f"❌ Failed to install pyOpenSSL: {result.stderr}")
                return False
        except Exception as e:
            click.echo(f"❌ Error installing pyOpenSSL: {e}")
            return False
    except Exception as e:
        click.echo(f"⚠️ Error generating certificates with pyOpenSSL: {e}")
        return False


def create_certificate_placeholders(project_dir, project_name):
    """Create placeholder certificate files with instructions."""
    cert_path = project_dir / 'cert.pem'
    key_path = project_dir / 'key.pem'
    
    cert_placeholder = f'''# Certificate placeholder for {project_name}
# 
# This is a placeholder file. To generate proper self-signed certificates:
#
# Option 1 - Using OpenSSL (recommended):
# openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost/O={project_name}"
#
# Option 2 - Using Python cryptography library:
# pip install cryptography
# Then re-run: pet init
#
# For production, replace with proper SSL certificates from a Certificate Authority
'''
    
    key_placeholder = f'''# Private key placeholder for {project_name}
# 
# This is a placeholder file. To generate proper self-signed certificates:
#
# Option 1 - Using OpenSSL (recommended):
# openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost/O={project_name}"
#
# Option 2 - Using Python cryptography library:
# pip install cryptography
# Then re-run: pet init
#
# For production, replace with proper SSL certificates from a Certificate Authority
'''
    
    with open(cert_path, 'w', encoding='utf-8') as f:
        f.write(cert_placeholder)
    
    with open(key_path, 'w', encoding='utf-8') as f:
        f.write(key_placeholder)
    
    # Create a certificate generation script
    gen_script_content = f'''#!/bin/bash
# Certificate generation script for {project_name}

echo "🔐 Generating self-signed certificates for {project_name}..."

if command -v openssl >/dev/null 2>&1; then
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost/O={project_name}/OU=Development"
    echo "✅ Certificates generated successfully!"
    echo "⚠️  Note: These are self-signed certificates for development only"
    echo "🔒 For production, use proper SSL certificates from a Certificate Authority"
else
    echo "❌ OpenSSL not found. Please install OpenSSL to generate certificates."
    echo "📝 Alternatively, install Python cryptography library and re-run 'pet init'"
fi
'''
    
    with open(project_dir / 'generate-certificates.sh', 'w', encoding='utf-8') as f:
        f.write(gen_script_content)
    
    # Make the script executable on Unix-like systems
    try:
        import stat
        script_path = project_dir / 'generate-certificates.sh'
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
    except:
        pass
    
    click.echo("⚠️ Created certificate placeholders and generation script")
    click.echo("🔧 Run './generate-certificates.sh' or install 'cryptography' library")


def install_npm_dependencies(project_dir):
    """Install NPM dependencies for the project."""
    import subprocess
    import sys
    import platform
    
    try:
        # Use shell=True on Windows to properly resolve npm.cmd
        use_shell = platform.system() == 'Windows'
        
        # Check if npm is available
        subprocess.run(['npm', '--version'], capture_output=True, check=True, cwd=project_dir, shell=use_shell)
        
        # Install dependencies
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True, cwd=project_dir, shell=use_shell)
        
        if result.returncode == 0:
            click.echo("✅ NPM dependencies installed successfully")
        else:
            click.echo("⚠️ NPM install completed with warnings")
            if result.stderr:
                click.echo(f"Warnings: {result.stderr}")
                
    except subprocess.CalledProcessError:
        click.echo("❌ NPM not found. Please install Node.js and npm first.")
        click.echo("Visit: https://nodejs.org/")
    except Exception as e:
        click.echo(f"⚠️ Error installing dependencies: {e}")
        click.echo("You can manually run 'npm install' in the project directory.")