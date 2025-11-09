# MACT Production Deployment Guide
**Version**: 1.1  
**Last Updated**: 2025-11-06  
**Target Platform**: Ubuntu 22.04 LTS / DigitalOcean Droplet  
**Status**: ✅ **READY FOR DEPLOYMENT** - Unit 6 Security Complete

> **Note:** All security hardening (Unit 6) is complete. All backend endpoints are secured with input validation, authentication, and proper error handling. Infrastructure files updated for production deployment with gunicorn (backend) and uvicorn (proxy).

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Server Setup](#initial-server-setup)
3. [DNS Configuration](#dns-configuration)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [MACT Installation](#mact-installation)
6. [Service Management](#service-management)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 22.04 LTS
- **RAM**: Minimum 2GB (4GB recommended)
- **CPU**: 2 cores minimum
- **Storage**: 20GB minimum
- **Network**: Public IP address

### Domain Requirements
- Domain name (e.g., `m-act.live`)
- DNS access for creating records
- SSL certificate capability

### Local Requirements
- SSH access to server
- Git installed locally
- Basic Linux command line knowledge

---

## Initial Server Setup

### 1. Create DigitalOcean Droplet

```bash
# Via DigitalOcean web interface:
# - Choose Ubuntu 22.04 LTS
# - Select droplet size (2GB RAM minimum)
# - Choose datacenter region
# - Add SSH key
# - Create droplet
```

### 2. Initial SSH Connection

```bash
ssh root@YOUR_SERVER_IP
```

### 3. Run Automated Setup Script

```bash
# Copy setup script to server
scp deployment/scripts/setup.sh root@YOUR_SERVER_IP:/root/

# SSH into server
ssh root@YOUR_SERVER_IP

# Make script executable and run
chmod +x /root/setup.sh
./setup.sh
```

The setup script will:
- ✅ Update system packages
- ✅ Install Python 3.12, nginx, certbot
- ✅ Create `mact` user
- ✅ Clone MACT repository to `/opt/mact`
- ✅ Set up Python virtual environment
- ✅ Install dependencies
- ✅ Create systemd service units
- ✅ Configure nginx
- ✅ Configure firewall (UFW)
- ✅ Obtain SSL certificates

### 4. Manual Configuration Steps

After setup script completes, customize these files:

```bash
cd /opt/mact

# Backend environment
nano deployment/mact-backend.env
# Set: FLASK_ENV=production, LOG_LEVEL=INFO, MACT_ADMIN_API_KEY=<generate_secure_key>

# Proxy environment
nano deployment/mact-proxy.env
# Set: BACKEND_BASE_URL=http://127.0.0.1:5000

# FRP server environment
nano deployment/mact-frps.env
# (Usually no changes needed)

# FRP server configuration
nano third_party/frp/mact.frps.toml
# Update bindAddr, bindPort if needed
```

---

## DNS Configuration

### Required DNS Records

#### Option A: Manual DNS Setup

Add these records in your DNS provider (Name.com, Cloudflare, etc.):

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_SERVER_IP | 3600 |
| A | * | YOUR_SERVER_IP | 3600 |
| A | dev-* | YOUR_SERVER_IP | 3600 |

**Example:**
```
A     m-act.live          →  1.2.3.4
A     *.m-act.live        →  1.2.3.4
A     dev-*.m-act.live    →  1.2.3.4
```

#### Option B: DigitalOcean DNS

```bash
# Add domain to DigitalOcean
# In DigitalOcean control panel:
# 1. Go to Networking → Domains
# 2. Add domain: m-act.live
# 3. Add records:
#    - @ (A record) → Droplet IP
#    - * (A record) → Droplet IP
# 4. Update nameservers at registrar to:
#    - ns1.digitalocean.com
#    - ns2.digitalocean.com
#    - ns3.digitalocean.com
```

### Verify DNS Propagation

```bash
# Check A record
dig m-act.live +short
# Should return: YOUR_SERVER_IP

# Check wildcard
dig myapp.m-act.live +short
# Should return: YOUR_SERVER_IP

# Check dev subdomain
dig dev-alice.m-act.live +short
# Should return: YOUR_SERVER_IP
```

---

## SSL Certificate Setup

### Option A: Let's Encrypt with DNS Challenge (Recommended for Wildcard)

```bash
# Install certbot with DNS plugin
apt-get install -y python3-certbot-dns-<provider>
# Replace <provider> with your DNS provider (cloudflare, digitalocean, etc.)

# For DigitalOcean:
apt-get install -y python3-certbot-dns-digitalocean

# Create API credentials file
nano /root/.secrets/certbot/digitalocean.ini
# Add: dns_digitalocean_token = YOUR_DO_API_TOKEN

chmod 600 /root/.secrets/certbot/digitalocean.ini

# Obtain wildcard certificate
certbot certonly \
  --dns-digitalocean \
  --dns-digitalocean-credentials /root/.secrets/certbot/digitalocean.ini \
  -d m-act.live \
  -d '*.m-act.live' \
  --email admin@m-act.live \
  --agree-tos \
  --non-interactive

# Test auto-renewal
certbot renew --dry-run
```

### Option B: Let's Encrypt with HTTP Challenge (No Wildcard)

```bash
# Stop nginx temporarily
systemctl stop nginx

# Obtain certificate for main domain
certbot certonly --standalone \
  -d m-act.live \
  --email admin@m-act.live \
  --agree-tos \
  --non-interactive

# Start nginx
systemctl start nginx

# Note: This won't work for wildcard (*.m-act.live)
# You'll need separate certs for each subdomain or use DNS challenge
```

### Auto-Renewal Setup

```bash
# Enable certbot timer
systemctl enable certbot.timer
systemctl start certbot.timer

# Check timer status
systemctl status certbot.timer

# Test renewal
certbot renew --dry-run
```

---

## MACT Installation

### Start Services

```bash
# Start FRP server
systemctl start mact-frps
systemctl status mact-frps

# Start backend
systemctl start mact-backend
systemctl status mact-backend

# Start proxy
systemctl start mact-proxy
systemctl status mact-proxy

# Enable services to start on boot
systemctl enable mact-frps mact-backend mact-proxy
```

### Verify Installation

```bash
# Check backend health
curl http://localhost:5000/health
# Expected: {"status":"healthy","rooms_count":0}

# Check proxy health
curl http://localhost:9000/health
# Expected: {"status":"ok"}

# Check FRP server
netstat -tlnp | grep 7100
# Should show frps listening on port 7100

# Check nginx
nginx -t
systemctl status nginx

# Test full stack (from external machine)
curl https://m-act.live/health
# Expected: {"status":"healthy","rooms_count":0}
```

---

## Service Management

### Systemd Commands

```bash
# Status
systemctl status mact-backend
systemctl status mact-proxy
systemctl status mact-frps

# Start
systemctl start mact-backend
systemctl start mact-proxy
systemctl start mact-frps

# Stop
systemctl stop mact-backend
systemctl stop mact-proxy
systemctl stop mact-frps

# Restart
systemctl restart mact-backend
systemctl restart mact-proxy
systemctl restart mact-frps

# Enable on boot
systemctl enable mact-backend mact-proxy mact-frps

# Disable
systemctl disable mact-backend mact-proxy mact-frps

# View logs
journalctl -u mact-backend -f
journalctl -u mact-proxy -f
journalctl -u mact-frps -f
```

### Deployment Updates

```bash
# Deploy new version
cd /opt/mact
sudo ./deployment/scripts/deploy.sh

# Rollback to previous version
sudo ./deployment/scripts/rollback.sh /opt/mact-backups/mact_backup_TIMESTAMP.tar.gz
```

---

## Monitoring & Logging

### Log Files

```bash
# Application logs
tail -f /opt/mact/logs/backend.log
tail -f /opt/mact/logs/proxy.log

# Systemd journal logs
journalctl -u mact-backend -n 100
journalctl -u mact-proxy -n 100
journalctl -u mact-frps -n 100

# Nginx logs
tail -f /var/log/nginx/mact-access.log
tail -f /var/log/nginx/mact-error.log
tail -f /var/log/nginx/frp-tunnels-access.log
```

### Health Monitoring

Create a simple monitoring script:

```bash
#!/bin/bash
# /opt/mact/deployment/scripts/health-check.sh

# Backend
if curl -f -s http://localhost:5000/health > /dev/null; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
    systemctl restart mact-backend
fi

# Proxy
if curl -f -s http://localhost:9000/health > /dev/null; then
    echo "Proxy: OK"
else
    echo "Proxy: FAILED"
    systemctl restart mact-proxy
fi

# FRP
if netstat -tlnp | grep :7100 > /dev/null; then
    echo "FRP: OK"
else
    echo "FRP: FAILED"
    systemctl restart mact-frps
fi
```

Add to cron:
```bash
# Run health check every 5 minutes
*/5 * * * * /opt/mact/deployment/scripts/health-check.sh >> /var/log/mact-health.log 2>&1
```

### Metrics Collection (Optional)

For production monitoring, consider:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **node_exporter**: Server metrics
- **blackbox_exporter**: Endpoint monitoring

---

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# /opt/mact/deployment/scripts/backup.sh

BACKUP_DIR="/opt/mact-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mact_backup_$TIMESTAMP.tar.gz"

# Create backup
tar -czf "$BACKUP_FILE" \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='logs/*' \
    /opt/mact

# Keep only last 30 days
find "$BACKUP_DIR" -name "mact_backup_*.tar.gz" -mtime +30 -delete

echo "Backup created: $BACKUP_FILE"
```

Add to cron:
```bash
# Daily backup at 2 AM
0 2 * * * /opt/mact/deployment/scripts/backup.sh >> /var/log/mact-backup.log 2>&1
```

### Recovery

```bash
# Stop services
systemctl stop mact-proxy mact-backend

# Restore from backup
cd /opt/mact-backups
tar -xzf mact_backup_TIMESTAMP.tar.gz -C / --strip-components=2

# Restore dependencies
cd /opt/mact
sudo -u mact .venv/bin/pip install -r requirements.txt

# Start services
systemctl start mact-backend mact-proxy
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check systemd status
systemctl status mact-backend -l

# Check logs
journalctl -u mact-backend -n 50

# Common issues:
# 1. Port already in use
netstat -tlnp | grep 5000
# 2. Permission denied
ls -la /opt/mact
chown -R mact:mact /opt/mact
# 3. Python dependencies missing
sudo -u mact /opt/mact/.venv/bin/pip install -r /opt/mact/requirements.txt
```

### SSL Certificate Issues

```bash
# Check certificate
certbot certificates

# Renew manually
certbot renew

# Test nginx config
nginx -t

# Check certificate files
ls -la /etc/letsencrypt/live/m-act.live/
```

### DNS Not Resolving

```bash
# Check DNS from server
dig m-act.live +short

# Check DNS from external
dig @8.8.8.8 m-act.live +short

# Verify nginx is listening
netstat -tlnp | grep :443

# Check firewall
ufw status
```

### Proxy Not Mirroring

```bash
# Test backend directly
curl http://localhost:5000/get-active-url?room=test

# Test proxy directly
curl http://localhost:9000/rooms/test/mirror

# Check nginx proxy pass
tail -f /var/log/nginx/mact-error.log

# Verify backend is reachable from proxy
curl -v http://127.0.0.1:5000/health
```

### Performance Issues

```bash
# Check CPU/RAM usage
top
htop

# Check disk space
df -h

# Check open files
lsof | wc -l

# Check network connections
netstat -an | grep ESTABLISHED | wc -l

# Review rate limiting
grep "rate limit" /var/log/nginx/mact-error.log
```

---

## Security Checklist

- [ ] Firewall (UFW) enabled with only necessary ports open
- [ ] SSH key-based authentication (disable password auth)
- [ ] Fail2ban installed and configured
- [ ] SSL certificates installed and auto-renewing
- [ ] Admin API key set (MACT_ADMIN_API_KEY)
- [ ] Rate limiting enabled in nginx
- [ ] Regular security updates (`apt-get update && apt-get upgrade`)
- [ ] Non-root user (mact) for services
- [ ] Logs monitored regularly
- [ ] Backups automated and tested

---

## Maintenance Schedule

### Daily
- Check service health (automated)
- Review error logs

### Weekly
- Check disk space
- Review backup logs
- Update security patches

### Monthly
- Test backup restoration
- Review monitoring metrics
- Update dependencies if needed

---

## Production Checklist

Before going live:

- [ ] DNS records configured and propagated
- [ ] SSL certificates installed
- [ ] All services running and enabled
- [ ] Health checks passing
- [ ] Nginx configuration tested
- [ ] Firewall configured
- [ ] Backups configured
- [ ] Monitoring in place
- [ ] Documentation updated
- [ ] Admin API key changed from default
- [ ] Test complete workflow (create room, make commit, access via public URL)

---

## Support & Resources

- **GitHub**: https://github.com/yourusername/M-ACT
- **Documentation**: `/opt/mact/.docs/`
- **Logs**: `/opt/mact/logs/` and `/var/log/nginx/`
- **Systemd Services**: `/etc/systemd/system/mact-*.service`

---

**Last Updated**: 2025-11-06  
**Version**: 1.0
