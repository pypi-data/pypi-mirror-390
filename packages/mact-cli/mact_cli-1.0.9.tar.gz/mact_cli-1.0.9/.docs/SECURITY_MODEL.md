# MACT Security Model & Access Control

**Last Updated:** November 8, 2025  
**Version:** 1.0  
**Purpose:** Explain who can access what and how authentication works

---

## Overview

MACT has **two distinct access levels** with different authentication requirements:

| Access Level | Users | Authentication | Tools Available |
|--------------|-------|----------------|-----------------|
| **Public** | Developers (clients) | None | `mact` CLI only |
| **Admin** | Server administrators | Required | `mact-admin` CLI + full system access |

---

## 1. Public Access (Developers)

### Who Has Access?
- ✅ Any developer who installs the client CLI
- ✅ Anyone with `pip install git+https://github.com/...`
- ✅ No registration or authentication required

### What Can They Do?
```bash
mact create ProjectName -port 3000   # Create rooms
mact join room-code -port 3000       # Join rooms
mact status                          # View room status
mact leave                           # Leave rooms
```

### What They CANNOT Do?
- ❌ Delete rooms created by others
- ❌ View all rooms in the system
- ❌ Kick other users from rooms
- ❌ View system logs or health status
- ❌ Access server-side administration features
- ❌ Install or run `mact-admin` CLI

### Why No Authentication?
By design, MACT is an **open collaboration platform**:
- Developers should be able to instantly create rooms
- No barrier to entry (no signup, no API keys)
- Similar to how GitHub Pages or Heroku free tier works
- Abuse prevention through rate limiting (not authentication)

---

## 2. Admin Access (Server Administrators)

### Who Has Access?
- ✅ Only people with SSH access to the DigitalOcean droplet
- ✅ Only people with the `ADMIN_AUTH_TOKEN`
- ✅ Typically: 1-2 system administrators

### What Can They Do?
```bash
mact-admin rooms delete room-name     # Delete any room
mact-admin rooms cleanup              # Remove empty rooms
mact-admin users kick user room       # Kick users
mact-admin system health              # View system status
mact-admin system logs backend        # View service logs
```

### Authentication Required
**Two-layer security:**

1. **SSH Access** - Must be able to SSH into the server
   ```bash
   ssh root@m-act.live
   ```

2. **Admin Token** - Must have `ADMIN_AUTH_TOKEN` set
   ```bash
   export ADMIN_AUTH_TOKEN=your-secure-token
   ```

### Why Two Layers?
- **SSH prevents remote access** - Admin CLI only works on the server itself (connects to localhost:5000)
- **Token prevents privilege escalation** - Even if someone gets SSH access, they need the token
- **Defense in depth** - Two independent barriers

---

## 3. Client CLI Installation (Public)

### What Gets Installed
When a developer runs:
```bash
pip install git+https://github.com/YOUR_USERNAME/M-ACT.git
```

**Files included:**
- ✅ `cli/` package (client CLI code)
- ✅ `third_party/frp/frpc` (tunnel client binary)
- ✅ Git hook scripts

**Files excluded:**
- ❌ `admin_cli.py` (admin CLI code)
- ❌ `backend/` (coordination backend)
- ❌ `proxy/` (routing proxy)
- ❌ `mact-admin` command

**Result:** Developers get `mact` command only.

### Why Exclude Admin CLI?
1. **No dependencies** - Client doesn't need Flask, Starlette, etc.
2. **Smaller package** - ~10MB instead of ~50MB
3. **Cleaner interface** - Only relevant commands visible
4. **Security** - Can't accidentally run admin commands

---

## 4. Server Installation (Admin Only)

### What Gets Installed
On the DigitalOcean droplet:
```bash
cd /opt/mact
source .venv/bin/activate
./scripts/install_server.sh
# OR manually:
pip install -r requirements.txt
pip install -e .
```

**Files included:**
- ✅ Everything (full repository)
- ✅ `cli/` (client CLI)
- ✅ `admin_cli.py` (admin CLI)
- ✅ `backend/` (coordination backend)
- ✅ `proxy/` (routing proxy)
- ✅ All dependencies

**Commands available:**
- ✅ `mact` (client CLI)
- ✅ `mact-admin` (admin CLI)

---

## 5. Admin Token Configuration

### Where to Set the Token

#### A. In Backend Environment File (Required)
```bash
# Edit environment file
sudo nano /opt/mact/deployment/mact-backend.env

# Add this line:
ADMIN_AUTH_TOKEN=your-secure-random-token-here
```

**Generate a secure token:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Example output: Kx3mP8nQ2rT5vL9wZ1aB4cD6eF7gH0iJ
```

#### B. For CLI Usage (Required)
```bash
# Export for current session
export ADMIN_AUTH_TOKEN=your-secure-random-token-here

# Add to .bashrc for persistence
echo 'export ADMIN_AUTH_TOKEN=your-secure-random-token-here' >> ~/.bashrc
source ~/.bashrc
```

#### C. Verification
```bash
# Check if set
echo $ADMIN_AUTH_TOKEN

# Test it works
mact-admin rooms list
# Should NOT show "Authentication failed" error
```

### Important Notes

1. **Same token in both places** - Backend env file and CLI export must match
2. **Keep it secret** - Never commit to git, never share in chat
3. **Rotate regularly** - Change every 90 days
4. **Strong token** - Use at least 32 characters, random

---

## 6. How Authentication Works

### Client API Calls (No Auth)
```python
# Creating a room - NO authentication required
POST /rooms/create
{
  "project_name": "my-project",
  "developer_id": "alice",
  "subdomain_url": "http://dev-alice-my-project.m-act.live"
}
# Returns: 201 Created
```

### Admin API Calls (Auth Required)
```python
# Listing all rooms - REQUIRES authentication
GET /admin/rooms
Headers: {
  "Authorization": "Bearer your-secure-token-here"
}
# Returns: 200 OK with room list

# Without token:
# Returns: 401 Unauthorized
```

### Token Validation in Backend
```python
# backend/security.py
@require_admin_auth
def list_all_rooms():
    # This decorator checks:
    # 1. Authorization header present?
    # 2. Token matches ADMIN_AUTH_TOKEN?
    # 3. If not, return 401/403
    ...
```

---

## 7. Preventing Client Access to Admin CLI

### Method 1: Package Exclusion (Current)
The `setup.py` **does not** include `admin_cli.py` in the pip package:

```python
# setup.py
packages=find_packages(exclude=["tests", "backend", "proxy", ...])
# admin_cli.py is at root level (not in a package)
# Therefore NOT included in pip install
```

**Result:** Developers who `pip install` don't get `admin_cli.py` at all.

### Method 2: Token Requirement (Backup)
Even if someone somehow gets `admin_cli.py`:

```python
# admin_cli.py
ADMIN_TOKEN = os.getenv("ADMIN_AUTH_TOKEN", "")

if not ADMIN_TOKEN:
    print("⚠️  Warning: ADMIN_AUTH_TOKEN not set. Some commands may fail.")
```

**Result:** Without the token, admin commands fail with 401 errors.

### Method 3: Localhost-Only Backend (Backup)
Backend only listens on `127.0.0.1:5000`:

```python
# backend/app.py
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)  # Localhost only!
```

**Result:** Admin CLI can only connect from the server itself (not remotely).

---

## 8. Attack Scenarios & Mitigations

### Scenario 1: Developer Tries to Delete Rooms

**Attack:**
```bash
# Developer tries to call admin endpoint directly
curl -X DELETE https://m-act.live/admin/rooms/someone-elses-room
```

**Defense:**
1. ❌ No `Authorization` header → 401 Unauthorized
2. ❌ Even with header, wrong token → 403 Forbidden
3. ✅ Request blocked by backend

---

### Scenario 2: Developer Installs Admin CLI

**Attack:**
```bash
# Developer tries to install and run admin CLI
pip install git+https://github.com/YOUR_USERNAME/M-ACT.git
mact-admin rooms list
```

**Defense:**
1. ❌ `admin_cli.py` not included in pip package → command not found
2. Even if they manually download it:
   - ❌ No `ADMIN_AUTH_TOKEN` set → commands fail
   - ❌ Backend not reachable (localhost only) → connection refused
3. ✅ Cannot access admin features

---

### Scenario 3: Someone Steals Admin Token

**Attack:**
```bash
# Attacker gets the token somehow
export ADMIN_AUTH_TOKEN=stolen-token
mact-admin rooms delete important-room
```

**Defense:**
1. ❌ Admin CLI connects to localhost:5000 → connection refused (not on server)
2. If they SSH to server:
   - ✅ SSH requires key-based auth (if configured properly)
   - ✅ Defense: disable password auth, use strong SSH keys
3. ✅ Two-factor protection (SSH + token)

**Mitigation:** Rotate token immediately if compromised.

---

### Scenario 4: Malicious Room Creation

**Attack:**
```bash
# Someone creates 1000 rooms to DDoS the system
for i in {1..1000}; do
  mact create spam-$i -port 3000
done
```

**Defense:**
1. ✅ Rate limiting on backend (planned for Unit 2)
2. ✅ Admin can cleanup: `mact-admin rooms cleanup`
3. ✅ Monitoring alerts admin of unusual activity

---

## 9. Security Best Practices

### For Administrators

#### ✅ DO:
- Use strong, random admin tokens (32+ characters)
- Rotate tokens every 90 days
- Store token in environment files only (not code)
- Restrict SSH access (key-based auth only)
- Monitor `mact-admin system logs` regularly
- Keep token in `~/.bashrc` with proper permissions (`chmod 600`)

#### ❌ DON'T:
- Commit tokens to git
- Share tokens via email/chat
- Use simple tokens like "admin123"
- Allow password-based SSH login
- Run admin commands on untrusted machines
- Expose backend port (5000) to internet

---

### For Developers

#### ✅ DO:
- Install via official pip command
- Use reasonable room names
- Report abuse to administrators

#### ❌ DON'T:
- Try to access admin endpoints
- Attempt to brute force tokens
- Create excessive rooms for testing

---

## 10. Summary

### Security Model

| Feature | Public (Developers) | Admin (Server) |
|---------|---------------------|----------------|
| **Access Method** | `pip install` from GitHub | SSH + local install |
| **Authentication** | None | `ADMIN_AUTH_TOKEN` |
| **CLI Tool** | `mact` only | `mact` + `mact-admin` |
| **Can Create Rooms** | ✅ Yes | ✅ Yes |
| **Can Delete Rooms** | ❌ No | ✅ Yes (any room) |
| **Can View All Rooms** | ❌ No | ✅ Yes |
| **Can Access Logs** | ❌ No | ✅ Yes |
| **Remote Access** | ✅ Yes (public API) | ❌ No (SSH only) |

---

## 11. Configuration Checklist

### Initial Setup (One-Time)

```bash
# 1. Generate secure token
TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "Generated token: $TOKEN"

# 2. Set in backend config
echo "ADMIN_AUTH_TOKEN=$TOKEN" >> /opt/mact/deployment/mact-backend.env

# 3. Set for CLI
echo "export ADMIN_AUTH_TOKEN=$TOKEN" >> ~/.bashrc
source ~/.bashrc

# 4. Restart backend
sudo systemctl restart mact-backend

# 5. Test admin CLI
mact-admin system health
```

### Verification

```bash
# Check backend has token
sudo cat /opt/mact/deployment/mact-backend.env | grep ADMIN_AUTH_TOKEN

# Check CLI has token
echo $ADMIN_AUTH_TOKEN

# Test admin command works
mact-admin rooms list

# Should NOT see "Authentication failed" error
```

---

## 12. FAQ

### Q: Can developers access admin features?
**A:** No. The admin CLI is not included in the pip package, and admin API endpoints require authentication.

### Q: What if someone copies admin_cli.py?
**A:** It won't work without:
1. SSH access to the server
2. The admin token
3. Backend running on localhost:5000

### Q: Should I make admin endpoints public?
**A:** No. Backend should only listen on 127.0.0.1:5000 (localhost). Nginx proxies public traffic, but admin endpoints remain localhost-only.

### Q: How do I change the admin token?
**A:** 
```bash
# Generate new token
NEW_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update backend env
sudo sed -i "s/ADMIN_AUTH_TOKEN=.*/ADMIN_AUTH_TOKEN=$NEW_TOKEN/" /opt/mact/deployment/mact-backend.env

# Update your shell
export ADMIN_AUTH_TOKEN=$NEW_TOKEN
sed -i "s/ADMIN_AUTH_TOKEN=.*/ADMIN_AUTH_TOKEN=$NEW_TOKEN/" ~/.bashrc

# Restart backend
sudo systemctl restart mact-backend
```

### Q: Can I have multiple admin users?
**A:** Yes. Share the same token with trusted co-administrators via secure channels (not email/Slack). Each admin sets the token in their shell.

### Q: What if I forget the admin token?
**A:** Check the backend environment file:
```bash
sudo cat /opt/mact/deployment/mact-backend.env | grep ADMIN_AUTH_TOKEN
```

---

## Related Documentation

- [ADMIN_CLI_GUIDE.md](ADMIN_CLI_GUIDE.md) - Complete admin CLI reference
- [CLIENT_INSTALLATION_GUIDE.md](CLIENT_INSTALLATION_GUIDE.md) - How developers install
- [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md) - Server setup
- [CLI_COMPARISON.md](CLI_COMPARISON.md) - Client vs Admin CLI

---

**Remember:** 
- 🔓 Public API = No auth needed (by design)
- 🔒 Admin API = Token required (SSH + token)
- 🔐 Two-layer security = SSH access + admin token
