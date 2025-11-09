# MACT Security Threat Model
**Version**: 1.0  
**Last Updated**: 2025-11-06  
**Status**: Production Ready (with noted limitations)

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Threat Actors](#threat-actors)
3. [Assets & Data](#assets--data)
4. [Threat Scenarios](#threat-scenarios)
5. [Security Controls](#security-controls)
6. [Known Limitations](#known-limitations)
7. [Mitigation Strategies](#mitigation-strategies)
8. [Security Best Practices](#security-best-practices)

---

## System Overview

### Architecture
MACT consists of:
1. **Backend API** (Flask) - Coordination and state management
2. **Proxy** (Flask) - Public-facing reverse proxy
3. **FRP Server** (frps) - Tunnel server for developer connections
4. **CLI** (Python) - Developer-side tunnel client

### Trust Boundaries
- **Public Internet** ↔ **Nginx** ↔ **Proxy** ↔ **Backend**
- **Developer Machines** ↔ **FRP Client** ↔ **FRP Server** ↔ **Proxy**

### Data Flow
1. Developer creates room → Backend stores state
2. Developer starts tunnel → FRP establishes connection
3. Public user accesses room URL → Proxy mirrors active developer's tunnel
4. Developer commits code → Git hook reports to Backend

---

## Threat Actors

### 1. External Attackers
**Motivation**: Disrupt service, steal data, gain unauthorized access  
**Capabilities**: Internet access, common hacking tools  
**Attack Vectors**: HTTP requests, DDoS, injection attacks

### 2. Malicious Developers
**Motivation**: Abuse resources, access other developers' projects  
**Capabilities**: Legitimate CLI access, knowledge of system internals  
**Attack Vectors**: API abuse, tunnel hijacking, commit spam

### 3. Curious Users
**Motivation**: Explore system, find vulnerabilities  
**Capabilities**: Basic HTTP tools (curl, browser)  
**Attack Vectors**: URL manipulation, brute force, information disclosure

---

## Assets & Data

### Critical Assets
| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| Backend API | High | Complete system failure |
| Room State Data | Medium | Information disclosure |
| Developer Tunnels | High | Unauthorized access to dev environments |
| Admin API Key | Critical | Full admin access |
| SSL Private Keys | Critical | Man-in-the-middle attacks |

### Data Types
| Data Type | Storage | Persistence | Sensitivity |
|-----------|---------|-------------|-------------|
| Room Codes | In-memory (Backend) | Session | Low |
| Developer IDs | In-memory (Backend) | Session | Low |
| Subdomain URLs | In-memory (Backend) | Session | Medium |
| Commit Hashes | In-memory (Backend) | Session | Low |
| Commit Messages | In-memory (Backend) | Session | Low-Medium |
| Developer Config | ~/.mact_config.json | Persistent | Low |
| Room Memberships | ~/.mact_rooms.json | Persistent | Medium |
| Admin API Key | Environment Variable | Persistent | Critical |

---

## Threat Scenarios

### T1: DDoS Attack
**Description**: Attacker floods proxy or backend with requests  
**Impact**: Service unavailability, legitimate users blocked  
**Likelihood**: High  
**Severity**: High  

**Mitigations**:
- ✅ Nginx rate limiting (100 req/min default)
- ✅ Flask-Limiter on backend endpoints
- ⚠️ CloudFlare recommended for production (not implemented)

---

### T2: SQL Injection
**Description**: Attacker injects SQL commands via input fields  
**Impact**: Data breach, unauthorized access  
**Likelihood**: Low (no database used)  
**Severity**: N/A  

**Mitigations**:
- ✅ No SQL database (in-memory state)
- ✅ Input validation on all fields
- N/A for current architecture

---

### T3: Cross-Site Scripting (XSS)
**Description**: Attacker injects malicious JavaScript via commit messages or room names  
**Impact**: User session hijacking, phishing  
**Likelihood**: Medium  
**Severity**: Medium  

**Mitigations**:
- ✅ HTML tag stripping in security.py
- ✅ Input validation and sanitization
- ✅ Content-Security-Policy headers (nginx)
- ⚠️ Dashboard templates need review

---

### T4: Unauthorized Admin Access
**Description**: Attacker guesses or steals admin API key  
**Impact**: Full system control, room manipulation  
**Likelihood**: Medium (if weak key used)  
**Severity**: Critical  

**Mitigations**:
- ✅ API key authentication required for /admin/* endpoints
- ✅ Rate limiting on admin endpoints (10 req/min)
- ⚠️ No IP whitelist (recommended for production)
- ⚠️ No audit logging (recommended)

**Recommendations**:
- Use strong, randomly generated API key (32+ chars)
- Rotate API key regularly
- Add IP whitelist for admin endpoints
- Implement audit logging

---

### T5: Tunnel Hijacking
**Description**: Attacker intercepts or redirects another developer's tunnel  
**Impact**: Unauthorized access to developer's localhost  
**Likelihood**: Low  
**Severity**: High  

**Mitigations**:
- ✅ FRP authentication (configured in frps.toml)
- ✅ Developer-specific subdomain URLs
- ⚠️ No tunnel encryption beyond HTTPS (FRP limitation)
- ⚠️ No developer authentication (beyond subdomain)

**Recommendations**:
- Use FRP token authentication
- Consider VPN for sensitive projects
- Implement developer authentication in CLI

---

### T6: Room Code Enumeration
**Description**: Attacker brute-forces room codes to discover projects  
**Impact**: Information disclosure, unauthorized room access  
**Likelihood**: Medium  
**Severity**: Low-Medium  

**Mitigations**:
- ✅ Rate limiting on API endpoints
- ⚠️ Room codes are predictable (project-name based)
- ⚠️ No authentication required to view rooms

**Recommendations**:
- Add random suffix to room codes (e.g., myapp-a1b2c3)
- Implement room authentication/passwords
- Hide room list from public API

---

### T7: Commit Spam
**Description**: Attacker floods room with fake commits  
**Impact**: Disrupts active developer selection, log pollution  
**Likelihood**: Medium  
**Severity**: Low  

**Mitigations**:
- ✅ Rate limiting on /report-commit (100 req/hour)
- ✅ Must be room member to report commits
- ⚠️ No commit signature verification

**Recommendations**:
- Verify Git commit signatures
- Add commit rate limits per developer
- Implement commit validation

---

### T8: Host Header Injection
**Description**: Attacker manipulates Host header to poison cache or redirect  
**Impact**: Phishing, cache poisoning  
**Likelihood**: Low  
**Severity**: Medium  

**Mitigations**:
- ✅ Nginx validates server_name
- ✅ Proxy sets X-Forwarded-Host
- ⚠️ No explicit host validation in application

**Recommendations**:
- Add allowed hosts whitelist in proxy
- Validate Host header in backend
- Log suspicious host headers

---

### T9: SSL/TLS Downgrade
**Description**: Attacker forces HTTP instead of HTTPS  
**Impact**: Man-in-the-middle, credential theft  
**Likelihood**: Low  
**Severity**: High  

**Mitigations**:
- ✅ HTTPS redirect in nginx (301 redirect)
- ✅ HSTS header recommended (add to nginx)
- ⚠️ No HSTS preload

**Recommendations**:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

---

### T10: Information Disclosure
**Description**: Attacker gathers system information from error messages  
**Impact**: Reconnaissance, system fingerprinting  
**Likelihood**: Medium  
**Severity**: Low  

**Mitigations**:
- ✅ Generic error messages in production
- ✅ Flask debug=False in production
- ⚠️ Stack traces may leak in logs

**Recommendations**:
- Implement custom error handlers
- Sanitize error responses
- Use error tracking (Sentry)

---

## Security Controls

### Implemented Controls

#### 1. Input Validation
**Location**: `backend/security.py`  
**Coverage**:
- Room codes: alphanumeric + hyphens, max 50 chars
- Developer IDs: alphanumeric + underscore/hyphen, max 30 chars
- URLs: HTTP/HTTPS format validation
- Commit hashes: 7-40 hex characters
- Branch names: Git-safe characters
- Commit messages: HTML stripped, max 200 chars

**Test Coverage**: Unit tests in `tests/test_security.py` (to be created)

#### 2. Rate Limiting
**Implementation**: Flask-Limiter + Nginx  
**Limits**:
- General: 200 req/hour, 50 req/min
- Room creation: 10 req/min
- Commit reporting: 100 req/hour
- Admin endpoints: 10 req/min
- Per-developer: 200 req/min (nginx zone)

**Configuration**: `deployment/nginx/m-act.live.conf`

#### 3. Authentication
**Admin Endpoints**: API key via Authorization header or query param  
**Key Storage**: Environment variable `MACT_ADMIN_API_KEY`  
**Endpoints Protected**: `/admin/*`

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://m-act.live/admin/rooms
```

#### 4. HTTPS/TLS
**Certificate**: Let's Encrypt wildcard certificate  
**Configuration**: Nginx SSL configuration  
**Protocols**: TLSv1.2, TLSv1.3  
**Ciphers**: HIGH:!aNULL:!MD5  

#### 5. Firewall
**Implementation**: UFW (Uncomplicated Firewall)  
**Open Ports**:
- 22 (SSH)
- 80 (HTTP → HTTPS redirect)
- 443 (HTTPS)
- 7100 (FRP server)

**Configuration**: See `deployment/scripts/setup.sh`

#### 6. Security Headers
**Nginx Configuration**:
```nginx
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer-when-downgrade
```

**Recommended Additions**:
```nginx
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
```

---

## Known Limitations

### 1. In-Memory State
**Issue**: All room data lost on backend restart  
**Impact**: Service disruption, data loss  
**Severity**: High  
**Mitigation**: Implement persistent storage (Redis, PostgreSQL)  
**Workaround**: Backup state periodically, document restart procedures

### 2. No Developer Authentication
**Issue**: Anyone with subdomain URL can report commits  
**Impact**: Unauthorized commit reporting  
**Severity**: Medium  
**Mitigation**: Add developer authentication tokens  
**Workaround**: Keep subdomain URLs private

### 3. WebSocket Not Supported
**Issue**: WebSocket connections rejected with 501  
**Impact**: No HMR support for dev servers  
**Severity**: Low  
**Mitigation**: Implement ASGI migration (see WEBSOCKET_DESIGN.md)  
**Workaround**: Use HTTP polling for dev servers

### 4. No Audit Logging
**Issue**: Admin actions not logged  
**Impact**: No forensics capability  
**Severity**: Medium  
**Mitigation**: Implement structured logging with audit trail  
**Workaround**: Review systemd journal logs

### 5. Predictable Room Codes
**Issue**: Room codes derived from project names  
**Impact**: Easy to guess/enumerate rooms  
**Severity**: Low-Medium  
**Mitigation**: Add random suffix to room codes  
**Workaround**: Use obscure project names

---

## Mitigation Strategies

### Priority 1: Critical (Implement Immediately)

1. **Strong Admin API Key**
   ```bash
   # Generate secure key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Set in environment
   export MACT_ADMIN_API_KEY="YOUR_SECURE_KEY"
   ```

2. **HSTS Header**
   ```nginx
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
   ```

3. **IP Whitelist for Admin**
   ```nginx
   location /admin {
       allow 1.2.3.4;  # Your IP
       deny all;
       # ... rest of config
   }
   ```

### Priority 2: High (Implement Soon)

1. **Audit Logging**
   - Log all admin actions
   - Log authentication attempts
   - Log rate limit violations

2. **Persistent Storage**
   - Migrate from in-memory to Redis/PostgreSQL
   - Implement data backup

3. **Developer Authentication**
   - Add token-based auth for CLI
   - Verify developer identity on commit reports

### Priority 3: Medium (Implement as Resources Allow)

1. **Room Authentication**
   - Optional passwords for rooms
   - Access control lists

2. **Random Room Codes**
   - Add random suffix to prevent enumeration

3. **Improved Error Handling**
   - Custom error pages
   - Error tracking (Sentry)

### Priority 4: Low (Nice to Have)

1. **WebSocket Support**
   - ASGI migration
   - WebSocket proxying

2. **Monitoring Dashboard**
   - Prometheus metrics
   - Grafana visualization

3. **Automated Security Scanning**
   - OWASP ZAP integration
   - Dependency vulnerability scanning

---

## Security Best Practices

### For Administrators

1. **Change Default API Key Immediately**
   ```bash
   nano /opt/mact/deployment/mact-backend.env
   # Set strong MACT_ADMIN_API_KEY
   ```

2. **Regular Security Updates**
   ```bash
   apt-get update && apt-get upgrade
   systemctl restart mact-backend mact-proxy
   ```

3. **Monitor Logs Daily**
   ```bash
   tail -f /var/log/nginx/mact-error.log
   journalctl -u mact-backend -f
   ```

4. **Backup Regularly**
   ```bash
   # Automated daily backups configured in setup.sh
   ls -lh /opt/mact-backups/
   ```

5. **Use Fail2ban**
   ```bash
   # Monitor SSH brute force
   fail2ban-client status sshd
   ```

### For Developers

1. **Keep Subdomain URLs Private**
   - Don't share dev-*.m-act.live URLs publicly
   - Use .env files for configuration

2. **Use HTTPS for Tunnels**
   - Always use https:// in subdomain URLs
   - Verify SSL certificates

3. **Review Commit Messages**
   - No sensitive data in commit messages
   - Messages are visible in dashboard

4. **Secure CLI Configuration**
   ```bash
   chmod 600 ~/.mact_config.json
   chmod 600 ~/.mact_rooms.json
   ```

5. **Update CLI Regularly**
   ```bash
   cd /path/to/M-ACT
   git pull origin main
   pip install -r requirements.txt
   ```

### For End Users

1. **Verify HTTPS**
   - Always check for green padlock
   - Verify domain is *.m-act.live

2. **Report Suspicious Behavior**
   - Unexpected redirects
   - SSL certificate warnings
   - Content that doesn't match project

3. **Don't Share Room URLs**
   - Room URLs are semi-public
   - Anyone with URL can access

---

## Security Checklist

### Development
- [ ] All inputs validated
- [ ] HTML sanitized
- [ ] Rate limiting tested
- [ ] Authentication tested
- [ ] Security tests passing

### Deployment
- [ ] Strong admin API key set
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] HSTS header added
- [ ] IP whitelist for admin (optional)

### Operations
- [ ] Logs monitored
- [ ] Backups automated
- [ ] Updates scheduled
- [ ] Audit logging (future)
- [ ] Incident response plan

---

## Incident Response

### If Backend Compromised
1. Stop services immediately
2. Review logs for attack vector
3. Change admin API key
4. Restore from clean backup
5. Patch vulnerability
6. Restart services

### If Developer Tunnel Compromised
1. Identify affected developer
2. Remove developer from room
3. Notify developer
4. Rotate FRP tokens
5. Review access logs

### If DDoS Attack
1. Enable CloudFlare (if available)
2. Tighten rate limits temporarily
3. Block attacking IPs in UFW
4. Consider fail2ban rules

---

## Security Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Flask Security**: https://flask.palletsprojects.com/en/2.3.x/security/
- **Nginx Security**: https://nginx.org/en/docs/http/ngx_http_ssl_module.html
- **Let's Encrypt**: https://letsencrypt.org/docs/

---

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email: security@m-act.live (if configured)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work to patch critical issues immediately.

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-06  
**Next Review**: 2026-01-06 (or after security incident)
