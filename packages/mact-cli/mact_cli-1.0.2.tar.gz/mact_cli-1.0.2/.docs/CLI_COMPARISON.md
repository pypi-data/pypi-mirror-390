# MACT CLI Overview: Client vs Admin

**Last Updated:** November 8, 2025  
**Purpose:** Quick reference showing the difference between the two CLI tools

---

## Two CLI Tools, Two Audiences

MACT provides **two separate command-line interfaces** for different users:

### 1. Client CLI (`mact`) - For Developers 👨‍💻

**Who uses it:** Developers collaborating on projects  
**Where installed:** Developer's laptop/workstation  
**Installation:** `pip install git+https://github.com/YOUR_USERNAME/M-ACT.git`  
**Purpose:** Create rooms, join rooms, manage local tunnels

**Key Commands:**
```bash
mact init --name alice                 # Set your developer ID
mact create TelegramBot -port 3000     # Create a new room
mact join telegram-bot -port 3000      # Join existing room
mact status                            # Check room status
```

---

### 2. Admin CLI (`mact-admin`) - For Server Administrators 🔧

**Who uses it:** System administrators managing the DigitalOcean droplet  
**Where installed:** Production server (m-act.live droplet)  
**Installation:** Pre-installed during server setup  
**Purpose:** Delete rooms, manage users, monitor system health

**Key Commands:**
```bash
mact-admin rooms list                  # List all rooms
mact-admin rooms delete room-name      # Delete a room
mact-admin rooms cleanup               # Remove empty rooms
mact-admin users list                  # Show all active users
mact-admin system health               # Check service status
mact-admin system logs backend         # View logs
```

---

## Side-by-Side Comparison

| Feature | Client CLI (`mact`) | Admin CLI (`mact-admin`) |
|---------|---------------------|--------------------------|
| **Target Users** | Developers | Server administrators |
| **Installation Location** | Developer's machine | DigitalOcean droplet |
| **Installation Method** | `pip install` from GitHub | Included in server setup |
| **Authentication** | None (public) | Requires `ADMIN_AUTH_TOKEN` |
| **Primary Actions** | Create/join rooms | Delete rooms, monitor system |
| **Network Access** | Connects to m-act.live | Connects to localhost:5000 |
| **Documentation** | [CLIENT_INSTALLATION_GUIDE.md](.docs/CLIENT_INSTALLATION_GUIDE.md) | [ADMIN_CLI_GUIDE.md](.docs/ADMIN_CLI_GUIDE.md) |

---

## Common Workflows

### Developer Workflow (Client CLI)

```bash
# Day 1: Create a room
cd ~/my-telegram-bot
mact init --name alice
mact create TelegramBot -port 3000
# Share room code with team: telegram-bot

# Day 2: Teammate joins
# Teammate Bob runs:
mact init --name bob
mact join telegram-bot -port 3001

# Day 3+: Just code and commit
git commit -m "Add webhook handler"
# Git hook auto-reports commit
# Alice becomes active developer
# https://telegram-bot.m-act.live now mirrors Alice's localhost:3000
```

---

### Admin Workflow (Server Management)

```bash
# Weekly: Check system health
mact-admin system health

# Monthly: Review usage stats
mact-admin system stats

# As needed: Clean up empty rooms
mact-admin rooms cleanup

# Emergency: Delete problematic room
mact-admin rooms delete spam-room --force

# Troubleshooting: View recent logs
mact-admin system logs backend -n 200
```

---

## Quick Command Cheatsheet

### Client CLI Commands

```bash
# Setup
mact init --name <your-name>           # One-time setup
mact version                           # Check CLI version

# Room Management
mact create <ProjectName> -port <port> # Create new room
mact join <room-code> -port <port>     # Join existing room
mact status                            # Check current room status
mact leave                             # Leave current room

# Troubleshooting
mact tunnel check                      # Verify tunnel is working
mact logs                              # Show local logs
```

### Admin CLI Commands

```bash
# Room Management
mact-admin rooms list                  # List all rooms
mact-admin rooms info <room>           # Room details
mact-admin rooms delete <room>         # Delete room
mact-admin rooms cleanup               # Remove empty rooms

# User Management
mact-admin users list                  # List all users
mact-admin users kick <user> <room>    # Kick user from room

# System Management
mact-admin system health               # Health check
mact-admin system stats                # Usage statistics
mact-admin system logs <service>       # View logs
```

---

## When to Use Which CLI

### Use Client CLI (`mact`) when:
- ✅ You're a developer working on a project
- ✅ You want to create or join a room
- ✅ You need to check your room's status
- ✅ You're troubleshooting your local tunnel

### Use Admin CLI (`mact-admin`) when:
- ✅ You're managing the production server
- ✅ You need to delete a room
- ✅ You want to see overall system statistics
- ✅ You're monitoring server health
- ✅ You need to view service logs
- ✅ A user reported an issue and you're investigating

---

## Installation Differences

### Client CLI (Developers)

**One-time installation on laptop:**
```bash
pip install git+https://github.com/YOUR_USERNAME/M-ACT.git
mact --help
```

**What gets installed:**
- `mact` command (globally accessible)
- CLI code only (no backend/proxy)
- FRP client binary (`frpc`)
- Git hook script

**Package size:** ~10MB (includes frpc binary)

---

### Admin CLI (Administrators)

**Pre-installed during server setup:**
```bash
# Already done in deployment script
cd /opt/mact
source venv/bin/activate
pip install -e .
```

**What gets installed:**
- `mact-admin` command
- Full codebase (backend, proxy, CLI)
- FRP server + client binaries
- All dependencies

**Package size:** Full repository

---

## Security Considerations

### Client CLI Security
- ✅ No authentication required (public access)
- ✅ Rate limiting on backend prevents abuse
- ✅ Subdomain validation prevents injection attacks
- ⚠️ Anyone can create rooms (by design)

### Admin CLI Security
- 🔒 Requires `ADMIN_AUTH_TOKEN` environment variable
- 🔒 Only accessible via SSH to droplet
- 🔒 Token should be rotated every 90 days
- 🔒 Confirmation prompts for destructive operations

**Setting admin token:**
```bash
# Generate secure token
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in backend config
echo "ADMIN_AUTH_TOKEN=<token>" >> /opt/mact/deployment/mact-backend.env
sudo systemctl restart mact-backend

# Set for CLI usage
export ADMIN_AUTH_TOKEN=<token>
echo 'export ADMIN_AUTH_TOKEN=<token>' >> ~/.bashrc
```

---

## Documentation Links

### Client CLI
- [QUICK_START.md](.docs/QUICK_START.md) - 30-second install guide
- [CLIENT_INSTALLATION_GUIDE.md](.docs/CLIENT_INSTALLATION_GUIDE.md) - Complete installation
- [CLI_QUICKREF.md](CLI_QUICKREF.md) - Command reference

### Admin CLI
- [ADMIN_CLI_GUIDE.md](.docs/ADMIN_CLI_GUIDE.md) - Complete admin reference
- [PRODUCTION_DEPLOYMENT_GUIDE.md](.docs/PRODUCTION_DEPLOYMENT_GUIDE.md) - Server setup
- [TROUBLESHOOTING_GUIDE.md](.docs/TROUBLESHOOTING_GUIDE.md) - Debugging

---

## Example Scenarios

### Scenario 1: Developer Creates Room
```bash
# Alice (on her laptop)
cd ~/telegram-bot
mact init --name alice
mact create TelegramBot -port 3000

# Output:
# ✅ Room created: telegram-bot
# 🔗 Public URL: https://telegram-bot.m-act.live
# 📊 Dashboard: https://telegram-bot.m-act.live/dashboard
```

### Scenario 2: Admin Deletes Old Room
```bash
# Admin (SSH'd into droplet)
ssh root@m-act.live

mact-admin rooms list
# Shows: old-test-project (0 participants, 2 commits)

mact-admin rooms delete old-test-project
# Confirmation prompt...
# ✅ Room 'old-test-project' deleted successfully.
```

### Scenario 3: Admin Monitors System
```bash
# Admin checks weekly health
mact-admin system health
# All services ✅

mact-admin system stats
# Total Rooms: 25
# Total Participants: 48
# Total Commits: 523

mact-admin rooms cleanup
# Found 3 empty rooms to clean up
# ✅ Cleanup complete. Deleted 3/3 rooms.
```

---

## Troubleshooting

### Client CLI Issues
**Problem:** `mact: command not found`

**Solution:**
```bash
# Ensure pip installed correctly
pip show mact-cli

# If missing, reinstall
pip install --force-reinstall git+https://github.com/YOUR_USERNAME/M-ACT.git

# Check PATH
which mact
```

---

### Admin CLI Issues
**Problem:** `Authentication failed. Check ADMIN_AUTH_TOKEN`

**Solution:**
```bash
# Check token is set
echo $ADMIN_AUTH_TOKEN

# If empty, set it
export ADMIN_AUTH_TOKEN=your-token-here

# Verify backend has same token
sudo cat /opt/mact/deployment/mact-backend.env | grep ADMIN_AUTH_TOKEN
```

---

## Summary

**Two CLIs, Two Purposes:**

| CLI | Audience | Location | Purpose |
|-----|----------|----------|---------|
| `mact` | Developers | Laptop | Create/join rooms, develop collaboratively |
| `mact-admin` | Admins | Droplet | Delete rooms, monitor system, manage users |

**Key Takeaway:** If you're coding, use `mact`. If you're managing the server, use `mact-admin`.

---

## Related Files

- **Client CLI Code:** `cli/cli.py`
- **Admin CLI Code:** `admin_cli.py`
- **Entry Points:** `setup.py` (defines both `mact` and `mact-admin` commands)

---

**Remember:** 
- Developers use `mact` to build cool stuff 🚀
- Admins use `mact-admin` to keep the platform running smoothly 🔧
