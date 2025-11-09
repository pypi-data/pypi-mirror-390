# GitHub Repository Setup Guide for MACT

**Purpose:** Deploy MACT codebase to GitHub for production deployment and end-user access  
**Last Updated:** November 8, 2025

---

## 📋 Table of Contents
1. [Repository Creation](#1-repository-creation)
2. [Pushing Code to GitHub](#2-pushing-code-to-github)
3. [Release Management](#3-release-management)
4. [Repository Configuration](#4-repository-configuration)
5. [End-User Access](#5-end-user-access)
6. [Pulling on DigitalOcean Droplet](#6-pulling-on-digitalocean-droplet)

---

## 1. Repository Creation

### 1.1 Create New Repository on GitHub

1. **Navigate to:** https://github.com/new
2. **Fill in details:**
   - **Repository name:** `M-ACT`
   - **Description:** `Mirrored Active Collaborative Tunnel - A Git-driven collaborative development platform with room-based URL mirroring`
   - **Visibility:** 
     - ✅ **Public** (recommended for open-source project)
     - OR Private (if you prefer restricted access)
   - **Initialize:**
     - ❌ Do NOT add README (we already have one)
     - ❌ Do NOT add .gitignore (already exists)
     - ❌ Do NOT add license (already exists)

3. **Click:** "Create repository"

### 1.2 Note Your Repository URL

After creation, you'll see:
```
https://github.com/int33k/M-ACT.git
```

Save this URL - you'll need it shortly.

---

## 2. Pushing Code to GitHub

### 2.1 Verify Current Repository Status

```bash
cd /home/int33k/Desktop/M-ACT

# Check git status
git status

# Should show clean working tree
# If you have uncommitted changes, commit them first:
git add .
git commit -m "Prepare for production deployment"
```

### 2.2 Add GitHub Remote

```bash
# Add GitHub as remote origin (replace int33k)
git remote add origin https://github.com/int33k/M-ACT.git

# Verify remote
git remote -v
# Should show:
# origin  https://github.com/int33k/M-ACT.git (fetch)
# origin  https://github.com/int33k/M-ACT.git (push)
```

**If you already have a remote named "origin":**
```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/int33k/M-ACT.git
```

### 2.3 Push to GitHub

```bash
# Ensure you're on main branch
git branch -M main

# Push all code
git push -u origin main

# Enter your GitHub credentials if prompted
# Or use Personal Access Token (PAT) if 2FA is enabled
```

### 2.4 Push Tags (if any)

```bash
# List existing tags
git tag

# Push all tags
git push origin --tags
```

### 2.5 Verify Push

1. Go to: https://github.com/int33k/M-ACT
2. Verify all files are present:
   - ✅ backend/
   - ✅ cli/
   - ✅ proxy/
   - ✅ tests/
   - ✅ .docs/
   - ✅ deployment/
   - ✅ README.md
   - ✅ requirements.txt

---

## 3. Release Management

### 3.1 Create First Release

```bash
cd /home/int33k/Desktop/M-ACT

# Create version tag
git tag -a v1.0.0 -m "MACT v1.0.0 - Production Ready Release"

# Push tag to GitHub
git push origin v1.0.0
```

### 3.2 Create GitHub Release

1. **Navigate to:** https://github.com/int33k/M-ACT/releases
2. **Click:** "Draft a new release"
3. **Fill in:**

**Tag version:** `v1.0.0`

**Release title:** `MACT v1.0.0 - Production Ready`

**Description:**
```markdown
# 🚀 MACT v1.0.0 - Production Ready

First stable production release of **MACT (Mirrored Active Collaborative Tunnel)** - A Git-driven collaborative development platform.

## ✨ Features

### Core Functionality
- **Room-based collaboration** - Multiple developers share one persistent URL
- **Git-driven switching** - Latest commit author becomes active developer
- **Live mirroring** - Room URL auto-proxies to active developer's localhost
- **Zero-config tunnels** - One CLI command sets up everything
- **Real-time dashboard** - WebSocket-powered status updates

### Architecture
- Python/Flask REST API for coordination
- Starlette/ASGI proxy with subdomain routing
- FRP (Fast Reverse Proxy) for tunneling
- CLI for room management and automation

### Security
- Input validation on all endpoints
- Bearer token authentication for admin routes
- XSS prevention with HTML sanitization
- Rate limiting and security headers

## 📊 Test Coverage
✅ **36 tests passing** across all components:
- Backend: 13 tests
- Proxy: 8 tests
- CLI: 7 tests
- FRP Manager: 5 tests
- Integration: 3 tests

## 🚀 Quick Start

### For End Users (Install CLI)
```bash
# Clone and setup
git clone https://github.com/int33k/M-ACT.git ~/mact-cli
cd ~/mact-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize
python -m cli.cli init --name your-name

# Create room (from your project directory)
cd ~/your-project
python -m cli.cli create --project my-app --subdomain dev-yourname --local-port 3000
```

### For Administrators (Production Deployment)
See [PRODUCTION_DEPLOYMENT_GUIDE.md](.docs/PRODUCTION_DEPLOYMENT_GUIDE.md)

## 📚 Documentation
- [Project Context & Architecture](.docs/PROJECT_CONTEXT.md)
- [Production Deployment Guide](.docs/PRODUCTION_DEPLOYMENT_GUIDE.md)
- [CLI Documentation](cli/README.md)
- [API Reference](backend/README.md)
- [Security Model](.docs/SECURITY_THREAT_MODEL.md)

## 🛠️ Technology Stack
- **Backend:** Python 3.12 + Flask
- **Proxy:** Starlette/ASGI + uvicorn
- **Tunneling:** frp v0.65.0 (vendored)
- **Testing:** pytest
- **Deployment:** systemd + nginx + Let's Encrypt

## 📦 Production Deployment
- **Domain:** m-act.live (with wildcard SSL)
- **Platform:** DigitalOcean (Ubuntu 22.04)
- **Services:** systemd with auto-restart
- **SSL:** Let's Encrypt wildcard certificate
- **Monitoring:** DigitalOcean + system logs

## 🐛 Known Issues
None - this is a stable production release.

## 🤝 Contributing
This is an academic research project. For contributions or issues, please open an issue on GitHub.

## 📄 License
MIT License - See LICENSE file for details.

---

**Domain:** https://m-act.live  
**Deployment Status:** Production Ready ✅  
**Test Status:** All 36 tests passing ✅  
**Security:** Production hardened ✅
```

4. **Click:** "Publish release"

### 3.3 Future Releases

For subsequent releases:
```bash
# Make changes, commit, and create new tag
git tag -a v1.1.0 -m "MACT v1.1.0 - Feature update"
git push origin v1.1.0

# Create release on GitHub with changelog
```

---

## 4. Repository Configuration

### 4.1 Update Repository Settings

**Navigate to:** https://github.com/int33k/M-ACT/settings

#### General
- **Description:** `Mirrored Active Collaborative Tunnel - Git-driven collaborative development`
- **Website:** `https://m-act.live`
- **Topics:** Add tags:
  - `collaboration`
  - `tunneling`
  - `git`
  - `flask`
  - `real-time`
  - `reverse-proxy`
  - `frp`
  - `websocket`

#### Features
- ✅ **Issues** (enable for bug reports)
- ✅ **Discussions** (enable for community)
- ❌ **Projects** (optional)
- ❌ **Wiki** (we have .docs/)

### 4.2 Add README Badges (Optional)

Edit `README.md` to add status badges at the top:

```markdown
# MACT (Mirrored Active Collaborative Tunnel)

[![Tests](https://img.shields.io/badge/tests-36%20passing-brightgreen)](https://github.com/int33k/M-ACT/actions)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Domain](https://img.shields.io/badge/domain-m--act.live-orange)](https://m-act.live)
```

### 4.3 Add GitHub Actions (Optional)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-22.04
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --tb=short
```

Commit and push:
```bash
git add .github/workflows/tests.yml
git commit -m "Add GitHub Actions CI"
git push origin main
```

### 4.4 Create Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.12]
- MACT version: [e.g., v1.0.0]

**Logs**
Paste relevant logs here.
```

---

## 5. End-User Access

### 5.1 Clone Instructions for Users

Users can access your code with:

```bash
# HTTPS (easier)
git clone https://github.com/int33k/M-ACT.git

# SSH (if they have SSH keys)
git clone git@github.com:int33k/M-ACT.git
```

### 5.2 Installation Script URL

Direct installation via curl:

```bash
# One-line install (create this script)
curl -fsSL https://raw.githubusercontent.com/int33k/M-ACT/main/scripts/install-cli.sh | bash
```

### 5.3 Create Install Script

Create `scripts/install-cli.sh`:

```bash
#!/bin/bash
# MACT CLI Quick Installer
set -e

INSTALL_DIR="$HOME/mact-cli"
REPO_URL="https://github.com/int33k/M-ACT.git"

echo "=================================================="
echo "   MACT CLI Installer"
echo "=================================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Clone repository
echo "📦 Cloning MACT repository..."
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory $INSTALL_DIR already exists. Updating..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create config directory
mkdir -p ~/.mact

# Create alias helper
SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [ -n "$SHELL_RC" ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Add this to your $SHELL_RC for easy access:"
    echo ""
    echo "  alias mact='cd $INSTALL_DIR && source .venv/bin/activate && python -m cli.cli'"
    echo ""
    echo "Or run commands directly:"
    echo "  cd $INSTALL_DIR"
    echo "  source .venv/bin/activate"
    echo "  python -m cli.cli init --name your-name"
fi
```

Commit and push:
```bash
chmod +x scripts/install-cli.sh
git add scripts/install-cli.sh
git commit -m "Add CLI installation script"
git push origin main
```

---

## 6. Pulling on DigitalOcean Droplet

### 6.1 SSH into Droplet

```bash
ssh root@YOUR_DROPLET_IP
# or
ssh deploy@YOUR_DROPLET_IP
```

### 6.2 Initial Clone on Server

```bash
# Switch to appropriate user
sudo su - deploy

# Clone to production directory
cd /opt
sudo mkdir -p mact
sudo chown deploy:deploy mact
cd mact

# Clone from GitHub
git clone https://github.com/int33k/M-ACT.git .

# Verify
ls -la
```

### 6.3 Setup on Server

```bash
cd /opt/mact

# Create Python environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pytest tests/ -q
```

### 6.4 Pulling Updates

When you push updates to GitHub:

```bash
# On server
cd /opt/mact
git pull origin main

# Update dependencies if requirements changed
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -q

# Restart services
sudo systemctl restart mact-backend mact-proxy
```

### 6.5 Automated Deployment Script

The project includes `deployment/scripts/deploy.sh` which:
1. Creates backup
2. Pulls latest code
3. Updates dependencies
4. Runs tests
5. Restarts services
6. Performs health checks

**Usage:**
```bash
cd /opt/mact
sudo ./deployment/scripts/deploy.sh
```

---

## 📋 Checklist

### Pre-Push Checklist
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Documentation updated
- [ ] Secrets removed from code (use env files)
- [ ] .gitignore configured properly
- [ ] README.md updated with production info

### GitHub Setup Checklist
- [ ] Repository created on GitHub
- [ ] Code pushed to main branch
- [ ] Release v1.0.0 created
- [ ] Repository description and topics added
- [ ] README includes production deployment info
- [ ] Installation script created and tested

### Server Setup Checklist
- [ ] Code cloned to /opt/mact
- [ ] Dependencies installed
- [ ] Tests passing on server
- [ ] Services configured and running
- [ ] Deploy script tested

---

## 🔐 Security Notes

### Don't Commit These Files
The `.gitignore` already excludes:
- `*.env` (environment files with secrets)
- `__pycache__/`
- `.venv/`
- `logs/`
- `*.log`
- `.DS_Store`

### Use Environment Variables
Store secrets in:
- `/opt/mact/deployment/mact-backend.env`
- `/opt/mact/deployment/mact-proxy.env`
- `/opt/mact/deployment/mact-frps.env`

**Never commit these files to GitHub!**

### Generate Secure Tokens
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📞 Support

**Issues:** https://github.com/int33k/M-ACT/issues  
**Discussions:** https://github.com/int33k/M-ACT/discussions  
**Documentation:** https://github.com/int33k/M-ACT/tree/main/.docs

---

**Status:** Ready for GitHub deployment ✅  
**Repository:** https://github.com/int33k/M-ACT  
**Production:** https://m-act.live
