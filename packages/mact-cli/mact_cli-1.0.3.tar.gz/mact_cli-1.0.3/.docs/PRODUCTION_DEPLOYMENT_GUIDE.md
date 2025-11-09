# MACT Production Deployment Guide
**Target Domain:** m-act.live  
**Platform:** DigitalOcean Droplet (Ubuntu 22.04 LTS)  
**Last Updated:** November 8, 2025

---

## 📋 Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [GitHub Repository Setup](#github-repository-setup)
3. [DigitalOcean Droplet Setup](#digitalocean-droplet-setup)
4. [DNS Configuration](#dns-configuration)
5. [Server Initial Setup](#server-initial-setup)
6. [MACT Installation](#mact-installation)
7. [SSL Certificate Setup](#ssl-certificate-setup)
8. [Service Configuration](#service-configuration)
9. [Starting Services](#starting-services)
10. [Verification & Testing](#verification--testing)
11. [Client Setup for End Users](#client-setup-for-end-users)
12. [Monitoring & Maintenance](#monitoring--maintenance)
13. [Troubleshooting](#troubleshooting)

---

## 1. Pre-Deployment Checklist

### Required Resources
- ✅ **Domain:** m-act.live (registered on name.com)
- ✅ **Server:** DigitalOcean Droplet (Ubuntu 22.04, min 2GB RAM, 2 vCPUs)
- ✅ **GitHub Account:** For hosting the repository
- ✅ **Email Address:** For SSL certificate notifications
- ✅ **SSH Key:** For secure server access

### Local Prerequisites
```bash
# Verify your local setup is working
cd /home/int33k/Desktop/M-ACT

# Run all tests
pytest tests/ -v

# Verify all 36 tests pass
# ✓ 13 backend tests
# ✓ 8 proxy tests
# ✓ 7 CLI tests
# ✓ 5 FRP tests
# ✓ 3 integration tests
```

---

## 2. GitHub Repository Setup

### 2.1 Create GitHub Repository

1. **Go to GitHub:** https://github.com/new
2. **Repository Details:**
   - Name: `M-ACT`
   - Description: `Mirrored Active Collaborative Tunnel - A Git-driven collaborative development platform`
   - Visibility: `Public` (or Private if preferred)
   - Initialize: **DON'T** add README, .gitignore, or license (we have them)

### 2.2 Push Local Code to GitHub

```bash
cd /home/int33k/Desktop/M-ACT

# Add GitHub remote (replace int33k)
git remote add origin https://github.com/int33k/M-ACT.git

# Verify current branch
git branch -M main

# Push all code
git push -u origin main

# Push tags if any
git push --tags
```

### 2.3 Create GitHub Release (Optional but Recommended)

```bash
# Tag the current version
git tag -a v1.0.0 -m "MACT v1.0.0 - Production Ready"
git push origin v1.0.0
```

**On GitHub:**
1. Go to Releases → Draft a new release
2. Tag: `v1.0.0`
3. Title: `MACT v1.0.0 - Production Release`
4. Description:
   ```markdown
   ## 🚀 MACT v1.0.0 - Production Ready
   
   First stable release of MACT (Mirrored Active Collaborative Tunnel)
   
   ### Features
   - Room-based collaboration
   - Git-driven active developer switching
   - WebSocket-powered real-time dashboard
   - Zero-config tunnel setup
   - Production-ready security
   
   ### Deployment
   See [PRODUCTION_DEPLOYMENT_GUIDE.md](.docs/PRODUCTION_DEPLOYMENT_GUIDE.md)
   ```

### 2.4 Update Repository Settings

**On GitHub → Settings:**
- Add description and topics: `collaboration`, `tunneling`, `git`, `flask`, `real-time`
- Add website: `https://m-act.live`
- Enable Issues and Discussions

---

## 3. DigitalOcean Droplet Setup

### 3.1 Create Droplet

**Login to DigitalOcean:**
1. Go to: https://cloud.digitalocean.com/droplets
2. Click "Create" → "Droplets"

**Configuration:**
- **Image:** Ubuntu 22.04 (LTS) x64
- **Plan:** Basic
- **CPU Options:** Regular (2 vCPUs, 2GB RAM, 50GB SSD) - **$12/month**
- **Datacenter:** Choose closest to your users (e.g., Bangalore, San Francisco)
- **Authentication:** SSH Key (upload your public key)
- **Hostname:** `mact-production`
- **Tags:** `mact`, `production`

**Advanced Options:**
- ✅ Enable IPv6
- ✅ Enable monitoring

### 3.2 Note Your Droplet IP

After creation, note your server's IP address:
```
Example: 164.92.xxx.xxx
```

### 3.3 Initial SSH Connection

```bash
# SSH into your droplet (replace with your IP)
ssh root@164.92.xxx.xxx

# Update system
apt-get update && apt-get upgrade -y

# Set timezone (optional)
timedatectl set-timezone Asia/Kolkata
```

---

## 4. DNS Configuration

### 4.1 Configure Name.com DNS

**Login to Name.com:**
1. Go to: https://www.name.com/account/domain
2. Select your domain: `m-act.live`
3. Click "DNS Records"

**Add the following A records:**

| Type | Host | Answer | TTL |
|------|------|--------|-----|
| A | @ | 164.92.xxx.xxx (your droplet IP) | 300 |
| A | * | 164.92.xxx.xxx (wildcard for rooms) | 300 |
| A | *.dev | 164.92.xxx.xxx (wildcard for developer subdomains) | 300 |

**Example:**
```
A     @         164.92.123.45    300
A     *         164.92.123.45    300
A     *.dev     164.92.123.45    300
```

### 4.2 Point Nameservers to DigitalOcean (Optional)

For better DNS management, you can use DigitalOcean's nameservers:

**On Name.com:**
1. Go to domain settings
2. Change nameservers to:
   - `ns1.digitalocean.com`
   - `ns2.digitalocean.com`
   - `ns3.digitalocean.com`

**On DigitalOcean:**
1. Go to Networking → Domains
2. Add domain: `m-act.live`
3. Add the same A records as above

### 4.3 Verify DNS Propagation

```bash
# Wait 5-10 minutes, then test
dig m-act.live
dig app.m-act.live
dig dev-user1.m-act.live

# All should point to your droplet IP
```

---

## 5. Server Initial Setup

### 5.1 Create Deployment User

```bash
# Still logged in as root
adduser deploy
usermod -aG sudo deploy

# Copy SSH keys to deploy user
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

### 5.2 Configure Firewall

```bash
# Install and configure UFW
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 7100/tcp comment 'FRP Control'
ufw allow 7101/tcp comment 'FRP HTTP Vhost'
ufw status verbose
```

### 5.3 Install Fail2Ban (Security)

```bash
apt-get install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 6. MACT Installation

### 6.1 Install System Dependencies

```bash
# Switch to deploy user
su - deploy

# Become root for installations
sudo apt-get update
sudo apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    nginx \
    git \
    certbot \
    python3-certbot-nginx \
    curl \
    htop \
    supervisor
```

### 6.2 Clone MACT Repository

```bash
# As deploy user
cd /opt
sudo mkdir mact
sudo chown deploy:deploy mact
cd mact

# Clone from GitHub (replace with your repo URL)
git clone https://github.com/int33k/M-ACT.git .

# Verify files
ls -la
```

### 6.3 Setup Python Environment

```bash
cd /opt/mact

# Create virtual environment
python3.12 -m venv .venv

# Activate and install dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install CLI tools (client + admin)
pip install -e .

# Verify installation
pip list
mact --help          # Client CLI
mact-admin --help    # Admin CLI
pytest tests/ -q     # Quick test run
```

### 6.4 Configure Environment Files

```bash
# Copy templates
cp deployment/mact-backend.env.template deployment/mact-backend.env
cp deployment/mact-proxy.env.template deployment/mact-proxy.env
cp deployment/mact-frps.env.template deployment/mact-frps.env

# Edit backend environment
nano deployment/mact-backend.env
```

**Update `mact-backend.env`:**
```bash
FLASK_ENV=production
BACKEND_PORT=5000
BACKEND_HOST=127.0.0.1
ADMIN_AUTH_TOKEN=your-secure-random-token-here
CORS_ORIGINS=https://m-act.live,https://*.m-act.live
LOG_LEVEL=INFO
```

**Generate secure token:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Use this output for ADMIN_AUTH_TOKEN
```

**Update `mact-proxy.env`:**
```bash
FLASK_ENV=production
PROXY_PORT=9000
PROXY_HOST=127.0.0.1
BACKEND_URL=http://127.0.0.1:5000
PUBLIC_DOMAIN=m-act.live
LOG_LEVEL=INFO
FRP_VHOST_PORT=7101
```

**Update `mact-frps.env`:**
```bash
FRPS_BIND_PORT=7100
FRPS_VHOST_HTTP_PORT=7101
FRPS_TOKEN=your-secure-frp-token-here
LOG_LEVEL=INFO
```

### 6.5 Update FRP Configuration

```bash
nano third_party/frp/mact.frps.toml
```

**Update with production settings:**
```toml
# MACT Production FRP Server Config
bindPort = 7100

# HTTP Vhost (for subdomain tunnels)
vhostHTTPPort = 7101

# Authentication
auth.method = "token"
auth.token = "your-secure-frp-token-here"

# Logging
log.to = "/opt/mact/logs/frps.log"
log.level = "info"
log.maxDays = 7

# Limits
transport.maxPoolCount = 50
transport.tcpKeepalive = true
```

### 6.6 Create Log Directory

```bash
mkdir -p /opt/mact/logs
chmod 755 /opt/mact/logs
```

---

## 7. SSL Certificate Setup

### 7.1 Stop Nginx (for standalone certbot)

```bash
sudo systemctl stop nginx
```

### 7.2 Obtain SSL Certificate

```bash
# For wildcard SSL, use DNS challenge
sudo certbot certonly \
    --manual \
    --preferred-challenges dns \
    -d m-act.live \
    -d "*.m-act.live" \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email

# Certbot will ask you to add DNS TXT records
# Example:
# _acme-challenge.m-act.live → "xyz123..."
```

**Add TXT Record on Name.com:**
1. Go to DNS Records
2. Type: `TXT`
3. Host: `_acme-challenge`
4. Answer: (paste the value from certbot)
5. TTL: `300`

**Wait 2-3 minutes, then verify:**
```bash
dig TXT _acme-challenge.m-act.live
```

**Press Enter in certbot** to continue verification.

### 7.3 Setup Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Enable automatic renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check renewal timer
sudo systemctl status certbot.timer
```

---

## 8. Service Configuration

### 8.1 Install Systemd Services

```bash
cd /opt/mact

# Copy systemd service files
sudo cp deployment/systemd/mact-backend.service /etc/systemd/system/
sudo cp deployment/systemd/mact-proxy.service /etc/systemd/system/
sudo cp deployment/systemd/mact-frps.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable mact-frps
sudo systemctl enable mact-backend
sudo systemctl enable mact-proxy
```

### 8.2 Configure Nginx

```bash
# Update nginx config with correct domain
sudo cp deployment/nginx/m-act.live.conf /etc/nginx/sites-available/m-act.live
sudo cp deployment/nginx/frp-tunnels.conf /etc/nginx/sites-available/frp-tunnels

# Create SSL snippet for reuse
sudo nano /etc/nginx/snippets/ssl-m-act.live.conf
```

**Add to `ssl-m-act.live.conf`:**
```nginx
ssl_certificate /etc/letsencrypt/live/m-act.live/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/m-act.live/privkey.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

**Enable sites:**
```bash
# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Enable MACT sites
sudo ln -sf /etc/nginx/sites-available/m-act.live /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/frp-tunnels /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Should output:
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## 9. Starting Services

### 9.1 Start in Order

```bash
# 1. Start FRP Server first (tunnels need this)
sudo systemctl start mact-frps
sudo systemctl status mact-frps

# 2. Start Backend API
sudo systemctl start mact-backend
sleep 2
sudo systemctl status mact-backend

# 3. Start Proxy
sudo systemctl start mact-proxy
sleep 2
sudo systemctl status mact-proxy

# 4. Start Nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

### 9.2 Check Service Logs

```bash
# Backend logs
sudo journalctl -u mact-backend -f

# Proxy logs
sudo journalctl -u mact-proxy -f

# FRP logs
sudo journalctl -u mact-frps -f

# Nginx access logs
sudo tail -f /var/log/nginx/mact-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/mact-error.log
```

---

## 10. Verification & Testing

### 10.1 Health Checks

```bash
# From the server
curl http://localhost:5000/health
# Expected: {"status":"healthy","rooms_count":0}

curl http://localhost:9000/health
# Expected: {"status":"ok"}

# From external (your laptop)
curl https://m-act.live/health
# Expected: {"status":"healthy","rooms_count":0}
```

### 10.2 Test Wildcard DNS

```bash
# Test subdomain routing
curl https://test-room.m-act.live/health
# Should get proxy health response
```

### 10.3 View Admin Dashboard

```bash
# Get admin auth token from env file
grep ADMIN_AUTH_TOKEN /opt/mact/deployment/mact-backend.env

# Test admin endpoint
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     https://m-act.live/admin/rooms
# Expected: {"rooms":[]}
```

---

## 11. Client Setup for End Users

### 11.1 Create Client Installation Script

**On your laptop (not server), create a script:**

```bash
nano /opt/mact/scripts/install-mact-cli.sh
```

**Content:**
```bash
#!/bin/bash
# MACT CLI Installer
set -e

echo "Installing MACT CLI..."

# Clone repository
git clone https://github.com/int33k/M-ACT.git ~/mact-cli
cd ~/mact-cli

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create config template
mkdir -p ~/.mact
cat > ~/.mact/config.json << EOF
{
  "backend_url": "https://m-act.live",
  "frp_server": "m-act.live",
  "frp_port": 7100
}
EOF

echo "MACT CLI installed!"
echo "Initialize with: cd ~/mact-cli && source .venv/bin/activate && python -m cli.cli init --name YOUR_NAME"
```

**Push to GitHub:**
```bash
git add scripts/install-mact-cli.sh
git commit -m "Add client installation script"
git push origin main
```

### 11.2 Update README for End Users

The main README.md already has installation instructions. Update the Quick Start section to use production URL:

```bash
nano /opt/mact/README.md
```

**Update to:**
```markdown
## 🚀 Quick Start for Users

### Install MACT CLI

```bash
# Download and install
curl -fsSL https://raw.githubusercontent.com/int33k/M-ACT/main/scripts/install-mact-cli.sh | bash

# OR clone manually
git clone https://github.com/int33k/M-ACT.git ~/mact-cli
cd ~/mact-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Create Your First Room

```bash
cd ~/mact-cli
source .venv/bin/activate

# Initialize with your name
python -m cli.cli init --name your-name

# Navigate to your project (must be a git repo)
cd ~/your-project

# Create a room
python -m cli.cli create \
  --project my-app \
  --subdomain dev-yourname-myapp \
  --local-port 3000

# Your room is live at:
# 🪞 Mirror:    https://my-app.m-act.live/
# 📊 Dashboard: https://my-app.m-act.live/dashboard
```
```

---

## 12. Monitoring & Maintenance

### 12.1 Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/mact
```

**Add:**
```
/opt/mact/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 deploy deploy
    sharedscripts
    postrotate
        systemctl reload mact-backend mact-proxy mact-frps
    endscript
}
```

### 12.2 Setup Monitoring (Optional)

**Install monitoring tools:**
```bash
sudo apt-get install -y prometheus prometheus-node-exporter
```

**Or use DigitalOcean Monitoring:**
- Go to Droplet → Monitoring
- Enable alerts for:
  - CPU usage > 80%
  - Memory usage > 85%
  - Disk usage > 90%

### 12.3 Backup Strategy

**Create backup script:**
```bash
sudo nano /opt/mact/scripts/backup.sh
```

**Content:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/mact-backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup code and config
tar -czf "$BACKUP_DIR/mact_backup_$TIMESTAMP.tar.gz" \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='logs/*' \
    /opt/mact

# Keep only last 7 backups
cd "$BACKUP_DIR"
ls -t mact_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup created: $BACKUP_DIR/mact_backup_$TIMESTAMP.tar.gz"
```

**Schedule with cron:**
```bash
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/mact/scripts/backup.sh
```

### 12.4 Regular Updates

```bash
# Pull latest code
cd /opt/mact
git pull origin main

# Update dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -q

# Restart services
sudo systemctl restart mact-backend mact-proxy
```

---

## 13. Troubleshooting

### 13.1 Service Won't Start

```bash
# Check service status
sudo systemctl status mact-backend
sudo systemctl status mact-proxy
sudo systemctl status mact-frps

# Check logs
sudo journalctl -u mact-backend -n 50
sudo journalctl -u mact-proxy -n 50
sudo journalctl -u mact-frps -n 50

# Common fixes:
# 1. Port already in use
sudo lsof -i :5000  # Backend
sudo lsof -i :9000  # Proxy
sudo lsof -i :7100  # FRP

# 2. Permission issues
sudo chown -R deploy:deploy /opt/mact
sudo chmod -R 755 /opt/mact

# 3. Missing dependencies
cd /opt/mact
source .venv/bin/activate
pip install -r requirements.txt
```

### 13.2 SSL Certificate Issues

```bash
# Check certificate
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Check nginx SSL config
sudo nginx -t
sudo systemctl reload nginx
```

### 13.3 DNS Not Resolving

```bash
# Check DNS from server
dig m-act.live
dig app.m-act.live

# Flush local DNS (on client)
sudo systemd-resolve --flush-caches

# Wait for propagation (up to 24 hours)
```

### 13.4 Tunnel Connection Failed

```bash
# Check FRP server
sudo systemctl status mact-frps
sudo journalctl -u mact-frps -f

# Check firewall
sudo ufw status
sudo ufw allow 7100/tcp
sudo ufw allow 7101/tcp

# Test FRP port
nc -zv m-act.live 7100
```

### 13.5 WebSocket Connection Failed

```bash
# Check nginx WebSocket config
sudo nginx -t

# Verify upgrade headers in nginx config
# Should have:
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection $connection_upgrade;

# Reload nginx
sudo systemctl reload nginx
```

---

## 14. Admin CLI Setup and Usage

After deployment, configure the admin CLI for server management:

### 14.1 Set Admin Environment Variable

```bash
# Set ADMIN_AUTH_TOKEN for CLI usage
export ADMIN_AUTH_TOKEN=$(grep ADMIN_AUTH_TOKEN /opt/mact/deployment/mact-backend.env | cut -d'=' -f2)

# Add to .bashrc for persistence
echo "export ADMIN_AUTH_TOKEN=$(grep ADMIN_AUTH_TOKEN /opt/mact/deployment/mact-backend.env | cut -d'=' -f2)" >> ~/.bashrc
```

### 14.2 Verify Admin CLI Works

```bash
# Test commands
mact-admin --help
mact-admin system health
mact-admin rooms list
```

### 14.3 Common Admin Tasks

```bash
# Check system status
mact-admin system health

# View usage statistics
mact-admin system stats

# List all rooms
mact-admin rooms list

# Delete a specific room
mact-admin rooms delete room-name

# Clean up empty rooms
mact-admin rooms cleanup

# View logs
mact-admin system logs backend -n 100
mact-admin system logs proxy -f    # Follow logs
```

**Complete admin reference:** [ADMIN_CLI_GUIDE.md](ADMIN_CLI_GUIDE.md)

---

## 📚 Additional Resources

- **GitHub Repository:** https://github.com/int33k/M-ACT
- **Project Documentation:** [.docs/PROJECT_CONTEXT.md](.docs/PROJECT_CONTEXT.md)
- **Client Installation Guide:** [.docs/CLIENT_INSTALLATION_GUIDE.md](.docs/CLIENT_INSTALLATION_GUIDE.md)
- **Admin CLI Guide:** [.docs/ADMIN_CLI_GUIDE.md](.docs/ADMIN_CLI_GUIDE.md)
- **CLI Comparison:** [.docs/CLI_COMPARISON.md](.docs/CLI_COMPARISON.md)
- **API Reference:** [backend/README.md](backend/README.md)

---

## ✅ Deployment Checklist

- [ ] GitHub repository created and code pushed
- [ ] DigitalOcean droplet created (2GB RAM, Ubuntu 22.04)
- [ ] DNS records configured (A, wildcard A records)
- [ ] SSH access configured with key-based authentication
- [ ] Firewall configured (UFW)
- [ ] MACT code cloned to /opt/mact
- [ ] Python environment setup with dependencies
- [ ] Environment files configured with secure tokens
- [ ] SSL certificate obtained (wildcard for *.m-act.live)
- [ ] Systemd services installed and enabled
- [ ] Nginx configured and tested
- [ ] All services started successfully
- [ ] Health checks passing
- [ ] Test room created and verified
- [ ] Client installation guide published
- [ ] Monitoring setup
- [ ] Backup strategy in place

---

**Deployment Status:** Ready for production ✅  
**Domain:** m-act.live  
**Server:** DigitalOcean (Ubuntu 22.04)  
**Estimated Setup Time:** 45-60 minutes
