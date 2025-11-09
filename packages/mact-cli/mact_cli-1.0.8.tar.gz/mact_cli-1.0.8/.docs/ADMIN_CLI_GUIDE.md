# MACT Admin CLI Guide

**Last Updated:** November 8, 2025  
**Version:** 1.0  
**Target Audience:** Server administrators managing the DigitalOcean droplet

---

## Overview

The **MACT Admin CLI** (`mact-admin`) is a server-side administration tool for managing rooms, users, and system health on the production server. It provides commands that should only be run by administrators with SSH access to the DigitalOcean droplet.

### Key Differences from Client CLI

| Feature | Client CLI (`mact`) | Admin CLI (`mact-admin`) |
|---------|---------------------|--------------------------|
| **Users** | Developers creating rooms | Server administrators |
| **Installation** | `pip install` from GitHub | Pre-installed on server |
| **Access** | Public (anyone can use) | Requires SSH + admin token |
| **Purpose** | Create/join rooms | Delete rooms, view stats, manage system |
| **Location** | Developer's laptop | DigitalOcean droplet only |

---

## Installation on Server

The admin CLI is automatically installed when you set up the MACT server:

```bash
# During initial deployment
cd /opt/mact
source venv/bin/activate
pip install -e .

# Verify installation
mact-admin --help
```

### Setting Admin Authentication Token

The admin CLI requires an authentication token to access protected endpoints:

```bash
# Edit the backend environment file
sudo nano /opt/mact/deployment/mact-backend.env

# Add this line (generate a secure random token)
ADMIN_AUTH_TOKEN=your-secure-random-token-here

# Restart backend to apply changes
sudo systemctl restart mact-backend

# Set the token for CLI usage
export ADMIN_AUTH_TOKEN=your-secure-random-token-here

# Add to your ~/.bashrc for persistence
echo 'export ADMIN_AUTH_TOKEN=your-secure-random-token-here' >> ~/.bashrc
```

**Generating a secure token:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Command Reference

### Rooms Management

#### `mact-admin rooms list`
List all rooms in the system with participant count and commit history.

```bash
mact-admin rooms list
```

**Output:**
```
📊 Total Rooms: 3

Room Code            Participants    Commits    Active Developer    
===========================================================================
telegram-bot         2               15         alice               
weather-app          1               8          bob                 
chat-server          0               3          None                
```

---

#### `mact-admin rooms info <room-code>`
Show detailed information about a specific room.

```bash
mact-admin rooms info telegram-bot
```

**Output:**
```
📦 Room: telegram-bot
============================================================
Active Developer: alice
Latest Commit: abc123def456
Total Commits: 15

Participants (2):
  🟢 alice
  ⚪ bob

Recent Commits (last 10):
  Time                 Developer       Hash         Message                       
  -------------------------------------------------------------------------------
  2025-11-08 14:30:15  alice          abc123de     Add webhook handler           
  2025-11-08 14:15:42  bob            def456ab     Fix message parsing           
  ...
```

---

#### `mact-admin rooms delete <room-code>`
Delete a specific room (with confirmation prompt).

```bash
mact-admin rooms delete chat-server
```

**Confirmation:**
```
⚠️  Are you sure you want to delete room 'chat-server'?
   This will remove all participants and commit history.
   Type 'yes' to confirm: yes
✅ Room 'chat-server' deleted successfully.
```

**Skip confirmation (use with caution):**
```bash
mact-admin rooms delete chat-server --force
```

---

#### `mact-admin rooms cleanup`
Delete all empty rooms (rooms with no participants).

```bash
mact-admin rooms cleanup
```

**Output:**
```
🧹 Found 2 empty room(s) to clean up:
   - old-project
   - test-room

Proceed with cleanup? (yes/no): yes
   ✅ Deleted: old-project
   ✅ Deleted: test-room

✅ Cleanup complete. Deleted 2/2 rooms.
```

**Auto-confirm:**
```bash
mact-admin rooms cleanup --force
```

---

### Users Management

#### `mact-admin users list`
List all active users across all rooms.

```bash
mact-admin users list
```

**Output:**
```
👥 Total Active Users: 5

Developer ID         Rooms      Room Codes                              
===========================================================================
alice                3          telegram-bot, weather-app, api-server  
bob                  2          telegram-bot, chat-server              
charlie              1          weather-app                            
dave                 1          api-server                             
eve                  1          chat-server                            
```

---

#### `mact-admin users kick <developer-id> <room-code>`
Remove a specific user from a room.

```bash
mact-admin users kick bob telegram-bot
```

**Use cases:**
- User is causing issues (committing spam, etc.)
- User requested to be removed but can't access their machine
- Emergency room cleanup

**With force flag:**
```bash
mact-admin users kick bob telegram-bot --force
```

---

### System Management

#### `mact-admin system health`
Check the health of all MACT services.

```bash
mact-admin system health
```

**Output:**
```
🏥 MACT System Health Check

============================================================

1. Backend API (Port 5000)
   ✅ Status: healthy
   📊 Rooms: 5

2. Routing Proxy (Port 9000)
   ✅ Status: Healthy

3. Systemd Services
   ✅ mact-backend: Running
   ✅ mact-proxy: Running
   ✅ mact-frps: Running

4. Nginx
   ✅ nginx: Running

============================================================
```

**What it checks:**
- Backend API connectivity and room count
- Proxy routing service
- All systemd services (backend, proxy, frps)
- Nginx reverse proxy

---

#### `mact-admin system stats`
Show usage statistics and metrics.

```bash
mact-admin system stats
```

**Output:**
```
📊 MACT System Statistics

============================================================
Total Rooms:        8
  Active:           6
  Empty:            2

Total Participants: 12
Total Commits:      143

Average per room:
  Participants:     1.5
  Commits:          17.9

============================================================
```

**Use cases:**
- Monthly reports
- Resource planning
- Monitoring system growth

---

#### `mact-admin system logs <service>`
View logs for a specific service using journalctl.

```bash
# View last 50 lines (default)
mact-admin system logs backend

# View last 100 lines
mact-admin system logs backend -n 100

# Follow logs in real-time (like tail -f)
mact-admin system logs proxy -f
```

**Available services:**
- `backend` - Coordination backend (Flask)
- `proxy` - Routing proxy (Starlette)
- `frps` - FRP server

**Output example:**
```
📋 Showing logs for mact-backend (last 50 lines)

Nov 08 14:30:15 mact systemd[1]: Started MACT Backend Service.
Nov 08 14:30:16 mact python[1234]: INFO: Backend started on port 5000
Nov 08 14:35:20 mact python[1234]: POST /rooms/create - 201
Nov 08 14:36:45 mact python[1234]: POST /report-commit - 200
...
```

**Stop following logs:**
Press `Ctrl+C`

---

## Common Administrative Tasks

### 1. Clean Up Empty Rooms (Weekly)

```bash
# Check for empty rooms
mact-admin rooms list | grep "0 "

# Clean them up
mact-admin rooms cleanup --force
```

---

### 2. Monitor System Health (Daily)

```bash
# Quick health check
mact-admin system health

# Check detailed stats
mact-admin system stats

# If issues found, view logs
mact-admin system logs backend -n 200
```

---

### 3. Remove Inactive Room

```bash
# Get room details
mact-admin rooms info old-project

# Confirm it's inactive (no recent commits)
# Delete it
mact-admin rooms delete old-project
```

---

### 4. Handle User Issues

**Scenario: User reports they can't access a room**

```bash
# Check room exists
mact-admin rooms info problematic-room

# Check if user is in the room
mact-admin users list | grep username

# View recent logs for clues
mact-admin system logs backend -n 100 | grep problematic-room
```

---

### 5. Emergency Room Deletion

```bash
# If a room is causing issues (infinite redirects, etc.)
mact-admin rooms delete problem-room --force

# Restart services if needed
sudo systemctl restart mact-proxy
sudo systemctl restart mact-backend
```

---

## Security Best Practices

### 1. Protect the Admin Token

```bash
# Store token securely
chmod 600 ~/.bashrc  # Ensure only you can read it

# Never commit token to git
# Never share token in chat/email
# Rotate token every 90 days
```

---

### 2. Limit SSH Access

```bash
# Only allow key-based authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no

# Restart SSH
sudo systemctl restart sshd
```

---

### 3. Regular Audits

```bash
# Weekly: Check who's using the system
mact-admin users list

# Monthly: Review room activity
mact-admin system stats

# Quarterly: Clean up old rooms
mact-admin rooms cleanup
```

---

## Troubleshooting

### Error: "Authentication failed. Check ADMIN_AUTH_TOKEN"

**Problem:** The token is not set or incorrect.

**Solution:**
```bash
# Check if token is set
echo $ADMIN_AUTH_TOKEN

# If empty, set it
export ADMIN_AUTH_TOKEN=your-token-here

# Verify backend has the same token
sudo cat /opt/mact/deployment/mact-backend.env | grep ADMIN_AUTH_TOKEN
```

---

### Error: "Failed to fetch rooms: Connection refused"

**Problem:** Backend is not running.

**Solution:**
```bash
# Check backend status
sudo systemctl status mact-backend

# If inactive, start it
sudo systemctl start mact-backend

# View logs for errors
mact-admin system logs backend -n 100
```

---

### Command Not Found: `mact-admin`

**Problem:** Admin CLI not installed or not in PATH.

**Solution:**
```bash
# Reinstall from source
cd /opt/mact
source venv/bin/activate
pip install -e .

# Verify
which mact-admin
```

---

### Logs Show "Permission Denied"

**Problem:** Journalctl requires sudo for some services.

**Solution:**
```bash
# Add your user to systemd-journal group
sudo usermod -aG systemd-journal $USER

# Log out and back in
exit
# SSH back in
```

---

## Integration with Monitoring

### Cron Jobs for Automated Maintenance

```bash
# Edit crontab
crontab -e

# Add weekly cleanup (Sundays at 3 AM)
0 3 * * 0 /opt/mact/venv/bin/mact-admin rooms cleanup --force >> /var/log/mact-cleanup.log 2>&1

# Add daily health check (every day at midnight)
0 0 * * * /opt/mact/venv/bin/mact-admin system health >> /var/log/mact-health.log 2>&1
```

---

### Simple Monitoring Script

```bash
#!/bin/bash
# /opt/mact/scripts/monitor.sh

source /opt/mact/venv/bin/activate
export ADMIN_AUTH_TOKEN=your-token-here

# Check health
if ! mact-admin system health | grep -q "✅"; then
    echo "ALERT: MACT system unhealthy!" | mail -s "MACT Alert" admin@yourdomain.com
fi

# Check disk space
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERT: Disk usage at ${DISK_USAGE}%" | mail -s "MACT Disk Alert" admin@yourdomain.com
fi
```

**Make it executable:**
```bash
chmod +x /opt/mact/scripts/monitor.sh

# Run every hour
crontab -e
# Add: 0 * * * * /opt/mact/scripts/monitor.sh
```

---

## FAQ

### Q: Can I use `mact-admin` from my laptop?
**A:** No. The admin CLI must run on the DigitalOcean droplet where the backend is running. It connects to `localhost:5000` by default.

### Q: What happens when I delete a room?
**A:** All room data is immediately deleted from memory:
- Participant list removed
- Commit history deleted
- Public URL becomes inactive
- Users can create a new room with the same name

### Q: Can I recover a deleted room?
**A:** No. MACT uses in-memory storage for Unit 1 (PoC). Once deleted, data is gone forever. Be careful with the `delete` command.

### Q: How do I export room data before deletion?
**A:** Currently not supported in Unit 1. You can manually copy commit history:
```bash
curl "http://localhost:5000/rooms/my-room/commits" > room-backup.json
```

### Q: Why use `mact-admin` instead of direct API calls?
**A:** 
- Better UX (formatted output, colors, confirmations)
- Safer (prevents accidental deletions)
- Easier to remember commands
- Includes system checks beyond the API (journalctl, systemd)

### Q: Can multiple admins use the CLI simultaneously?
**A:** Yes, as long as they all have the same `ADMIN_AUTH_TOKEN` set.

---

## Related Documentation

- [PRODUCTION_DEPLOYMENT_GUIDE.md](.docs/PRODUCTION_DEPLOYMENT_GUIDE.md) - Initial server setup
- [CLIENT_INSTALLATION_GUIDE.md](.docs/CLIENT_INSTALLATION_GUIDE.md) - How developers install `mact`
- [TROUBLESHOOTING_GUIDE.md](.docs/TROUBLESHOOTING_GUIDE.md) - General debugging
- [QUICK_START.md](.docs/QUICK_START.md) - 30-second overview

---

## Support

For issues with the admin CLI:
1. Check `/var/log/mact-*.log` files
2. Run `mact-admin system health` to diagnose
3. View service logs with `mact-admin system logs backend`
4. Consult [TROUBLESHOOTING_GUIDE.md](.docs/TROUBLESHOOTING_GUIDE.md)

For code changes or feature requests:
- GitHub Repository: https://github.com/YOUR_USERNAME/M-ACT
- Issues: https://github.com/YOUR_USERNAME/M-ACT/issues

---

**Remember:** With great power comes great responsibility. The admin CLI can delete rooms and kick users instantly. Always double-check before confirming destructive operations.
