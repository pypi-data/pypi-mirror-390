# MACT Client Installation & Usage Guide

**For End Users** - How to install and use the MACT tunnel client  
**Last Updated:** November 8, 2025

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [First-Time Setup](#first-time-setup)
5. [Creating Your First Room](#creating-your-first-room)
6. [Joining an Existing Room](#joining-an-existing-room)
7. [Daily Workflow](#daily-workflow)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Quick Start

**TL;DR - Get running in 3 commands:**

```bash
# 1. Install
git clone https://github.com/int33k/M-ACT.git ~/mact-cli
cd ~/mact-cli && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 2. Initialize
python -m cli.cli init --name your-name

# 3. Create room (from your project directory)
cd ~/your-project
python -m cli.cli create --project my-app --subdomain dev-yourname-myapp --local-port 3000

# 🎉 Your room is live at: https://my-app.m-act.live/
```

---

## System Requirements

### Operating System
- ✅ Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- ✅ macOS (11.0 Big Sur+)
- ⚠️ Windows (WSL2 recommended, native support limited)

### Software
- **Python:** 3.10 or higher
- **Git:** 2.25 or higher
- **Internet:** Stable connection (for tunnel)
- **Ports:** Ensure your firewall allows outbound connections

### Hardware
- **RAM:** 512MB minimum
- **Disk:** 100MB free space
- **CPU:** Any modern processor

### Verify Your System

```bash
# Check Python version (need 3.10+)
python3 --version

# Check Git version (need 2.25+)
git --version

# Check internet connection
ping -c 3 m-act.live
```

---

## Installation

### Method 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/int33k/M-ACT.git ~/mact-cli

# Navigate to directory
cd ~/mact-cli

# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -m cli.cli --help
```

**Expected Output:**
```
usage: cli.py [-h] {init,create,join,leave,status} ...

MACT - Mirrored Active Collaborative Tunnel CLI

positional arguments:
  {init,create,join,leave,status}
    init                Initialize MACT with your developer identity
    create              Create a new room
    join                Join an existing room
    leave               Leave a room
    status              Show your current room memberships
```

### Method 2: One-Line Installer

```bash
curl -fsSL https://raw.githubusercontent.com/int33k/M-ACT/main/scripts/install-cli.sh | bash
```

This will:
- Clone the repository to `~/mact-cli`
- Setup Python environment
- Install dependencies
- Show next steps

### Method 3: Download ZIP

1. Go to: https://github.com/int33k/M-ACT
2. Click "Code" → "Download ZIP"
3. Extract to `~/mact-cli`
4. Follow Method 1 steps from "Create Python virtual environment"

### Create a Convenient Alias (Optional)

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# MACT CLI Alias
alias mact='cd ~/mact-cli && source .venv/bin/activate && python -m cli.cli'
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

Now you can use: `mact create ...` instead of full path!

---

## First-Time Setup

### Step 1: Initialize Your Identity

```bash
cd ~/mact-cli
source .venv/bin/activate

# Set your developer name
python -m cli.cli init --name YOUR_NAME

# Example:
python -m cli.cli init --name siddhant
```

**What This Does:**
- Creates `~/.mact/config.json` with your identity
- Sets backend URL (production: https://m-act.live)
- Sets FRP server details

**Example Output:**
```
✅ MACT initialized successfully!
Developer ID: siddhant
Backend URL: https://m-act.live
Config saved to: /home/siddhant/.mact/config.json

Next steps:
1. Navigate to your project directory (must be a git repository)
2. Run: python -m cli.cli create --project <name> --local-port <port>
```

### Step 2: Prepare Your Project

MACT works with **Git repositories** only. Ensure your project has Git initialized:

```bash
cd ~/your-project

# If not a git repo yet:
git init
git add .
git commit -m "Initial commit"
```

### Step 3: Start Your Development Server

```bash
# Example for different frameworks:

# React/Vite (usually port 5173)
npm run dev

# Next.js (usually port 3000)
npm run dev

# Python Flask (usually port 5000)
flask run

# Node/Express (usually port 3000)
npm start

# Any static HTTP server
python3 -m http.server 8000
```

**Note:** Remember which port your app runs on - you'll need it next!

---

## Creating Your First Room

### Command Syntax

```bash
python -m cli.cli create \
  --project <room-name> \
  --subdomain <your-subdomain> \
  --local-port <your-app-port>
```

### Parameters Explained

| Parameter | Description | Example | Rules |
|-----------|-------------|---------|-------|
| `--project` | Room name (becomes URL) | `my-app` | Lowercase, hyphens only |
| `--subdomain` | Your personal subdomain | `dev-siddhant-myapp` | Must start with `dev-` |
| `--local-port` | Port your app runs on | `3000` | 1-65535 |

### Full Example

```bash
# Make sure you're in your project directory
cd ~/my-awesome-app

# Ensure your dev server is running
npm run dev  # (in another terminal)

# Create the room
python -m cli.cli create \
  --project my-awesome-app \
  --subdomain dev-siddhant-myapp \
  --local-port 3000
```

### What Happens Automatically

1. ✅ **Room created** on backend API
2. ✅ **Git hook installed** in `.git/hooks/post-commit`
3. ✅ **FRP tunnel started** (connects to m-act.live:7100)
4. ✅ **Subdomain mapped** (dev-siddhant-myapp.m-act.live → localhost:3000)

### Success Output

```
✅ Room created successfully!

Room Details:
  Room Code: my-awesome-app
  Public URL: https://my-awesome-app.m-act.live/
  Dashboard: https://my-awesome-app.m-act.live/dashboard
  
Your Tunnel:
  Subdomain: dev-siddhant-myapp.m-act.live
  Local Port: 3000
  Status: Connected ✅

Git Hook:
  Hook installed: .git/hooks/post-commit
  Commits will automatically report to backend

Next Steps:
  1. Make a commit to become the active developer
  2. Share the room URL with teammates
  3. View dashboard at: https://my-awesome-app.m-act.live/dashboard
```

### Verify It Works

```bash
# In your browser, visit:
https://my-awesome-app.m-act.live/

# You should see your localhost:3000 content!
```

---

## Joining an Existing Room

When a teammate has already created a room, you can join it.

### Get the Room Code

Ask your teammate for the room code. For example:
```
Room Code: my-awesome-app
```

### Join Command

```bash
# Navigate to YOUR local copy of the project
cd ~/my-local-copy-of-project

# Join the room
python -m cli.cli join \
  --room my-awesome-app \
  --subdomain dev-YOUR_NAME-myapp \
  --local-port 3001
```

**Important Notes:**
- Use a **different port** than your teammate (e.g., 3001 instead of 3000)
- Use a **unique subdomain** (include your name)
- Be in **the same project** (Git repo)

### Success Output

```
✅ Joined room successfully!

Room Details:
  Room Code: my-awesome-app
  Public URL: https://my-awesome-app.m-act.live/
  Dashboard: https://my-awesome-app.m-act.live/dashboard
  
Your Tunnel:
  Subdomain: dev-alice-myapp.m-act.live
  Local Port: 3001
  Status: Connected ✅

Other Participants:
  - siddhant (active)
  - alice (you)

Next Steps:
  1. Make a commit to become the active developer
  2. View dashboard at: https://my-awesome-app.m-act.live/dashboard
```

---

## Daily Workflow

### Morning: Start Working

```bash
# 1. Navigate to project
cd ~/my-project

# 2. Start your dev server
npm run dev  # (in terminal 1)

# 3. Your tunnel is already running (if created/joined)
# Check status:
python -m cli.cli status
```

### During Development: Making Commits

```bash
# 1. Make changes to your code
vim src/components/Header.js

# 2. Test locally
# Visit: http://localhost:3000

# 3. Commit your changes
git add .
git commit -m "Update header design"

# 🎉 Automatic magic happens:
#    - Git hook reports commit to backend
#    - You become the active developer
#    - Public URL (my-awesome-app.m-act.live) now shows YOUR localhost
#    - Dashboard updates in real-time
```

### Checking Room Status

```bash
# See all your rooms
python -m cli.cli status
```

**Output:**
```
📊 Your MACT Room Memberships:

Room: my-awesome-app
  Public URL: https://my-awesome-app.m-act.live/
  Dashboard: https://my-awesome-app.m-act.live/dashboard
  Your Subdomain: dev-siddhant-myapp.m-act.live
  Local Port: 3000
  Status: Connected ✅
  
Room: another-project
  Public URL: https://another-project.m-act.live/
  Your Subdomain: dev-siddhant-another.m-act.live
  Local Port: 3001
  Status: Disconnected ⚠️
```

### Sharing Your Work

**Send teammates:**
- 🪞 **Mirror URL:** `https://my-awesome-app.m-act.live/` (shows active developer)
- 📊 **Dashboard:** `https://my-awesome-app.m-act.live/dashboard` (shows status)

They can view your live localhost instantly - no deployment needed!

### Evening: Leave Room (Optional)

```bash
# When you're done for the day
python -m cli.cli leave --room my-awesome-app
```

**This will:**
- ✅ Remove you from room participants
- ✅ Stop your FRP tunnel
- ✅ Remove git hook (optional)
- ❌ Won't delete the room (stays for others)

---

## Troubleshooting

### Issue: "Command not found: python"

**Solution:**
```bash
# Try python3 instead
python3 -m cli.cli --help

# Or create alias
alias python=python3
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure you're in the right directory
cd ~/mact-cli

# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Tunnel won't connect

**Symptoms:**
```
❌ Failed to start FRP tunnel
```

**Solution:**
```bash
# Check if FRP server is reachable
nc -zv m-act.live 7100

# Check if port is already in use
lsof -i :3000

# Try a different local port
python -m cli.cli create --project app --local-port 3001
```

### Issue: "Not a git repository"

**Symptoms:**
```
❌ Error: Not in a git repository
```

**Solution:**
```bash
# Initialize git in your project
cd ~/your-project
git init
git add .
git commit -m "Initial commit"
```

### Issue: Public URL shows 404

**Possible Causes:**
1. Your localhost server is not running
2. Wrong port specified
3. Tunnel disconnected

**Solution:**
```bash
# 1. Verify your dev server is running
curl http://localhost:3000

# 2. Check tunnel status
python -m cli.cli status

# 3. Restart tunnel (leave and re-join/create)
python -m cli.cli leave --room my-app
python -m cli.cli create --project my-app --local-port 3000
```

### Issue: Dashboard shows wrong active developer

**Solution:**
```bash
# Make a commit to become active
git commit --allow-empty -m "Update active developer"
```

### Issue: Git hook not working

**Solution:**
```bash
# Check if hook exists
ls -la .git/hooks/post-commit

# Manually reinstall hook
python -m cli.cli create --project my-app --local-port 3000
# (hook reinstalls on create/join)

# Test hook manually
bash .git/hooks/post-commit
```

### Get Help

```bash
# CLI help
python -m cli.cli --help
python -m cli.cli create --help

# Check logs
# (CLI logs to stdout, check terminal output)

# Report issues
# GitHub: https://github.com/int33k/M-ACT/issues
```

---

## FAQ

### Q: Do I need to keep the terminal open?

**A:** Yes, the FRP tunnel runs as a subprocess. If you close the terminal, the tunnel stops. Use `tmux` or `screen` for persistent sessions, or run in background (future feature).

### Q: Can I work on multiple projects simultaneously?

**A:** Yes! Join/create multiple rooms with different ports:
```bash
# Project 1
cd ~/project1
python -m cli.cli create --project proj1 --local-port 3000

# Project 2
cd ~/project2
python -m cli.cli create --project proj2 --local-port 3001
```

### Q: What happens if I commit while someone else is active?

**A:** You become the new active developer! The public URL instantly switches to your localhost. The dashboard updates in real-time to show you as active.

### Q: Can I use MACT with non-web projects?

**A:** MACT works best with HTTP servers (web apps). For non-HTTP services, you'd need custom configuration (not currently supported).

### Q: Is my code sent to MACT servers?

**A:** No! Your code stays on your machine. MACT only:
- Receives commit metadata (hash, message, branch)
- Tunnels HTTP requests to your localhost
- Never stores or inspects your actual code

### Q: Can I use a custom domain?

**A:** Not in v1.0. All rooms use `*.m-act.live` subdomains. Custom domains are a future feature.

### Q: How many developers can be in one room?

**A:** Recommended: 5-10 developers per room. Technical limit: 50+ (depends on server resources).

### Q: Does MACT work with Vite/Next.js hot reload?

**A:** Yes! MACT supports WebSocket forwarding, so Vite HMR and Next.js Fast Refresh work seamlessly.

### Q: What if I don't have a domain?

**A:** For local development/testing, use `localhost:9000` instead of `m-act.live`. See `INSTALL.md` for local setup.

### Q: Can I see other developers' localhosts?

**A:** No. The public URL only shows the **active** developer. To see someone else's work, they need to make a commit to become active.

### Q: Is MACT free?

**A:** Yes, MACT is open-source (MIT License). The public instance at `m-act.live` is free for academic/personal use.

---

## Quick Reference Card

```bash
# Initialize (once)
python -m cli.cli init --name YOUR_NAME

# Create room (room creator)
python -m cli.cli create --project ROOM --subdomain dev-YOU-ROOM --local-port PORT

# Join room (team members)
python -m cli.cli join --room ROOM --subdomain dev-YOU-ROOM --local-port PORT

# Check status
python -m cli.cli status

# Leave room
python -m cli.cli leave --room ROOM

# URLs
Mirror:    https://ROOM.m-act.live/
Dashboard: https://ROOM.m-act.live/dashboard
```

---

## Next Steps

1. ✅ **Install MACT CLI** (you've done this!)
2. ✅ **Initialize your identity**
3. ✅ **Create or join a room**
4. 🚀 **Start collaborating!**

**Need help?**
- 📖 Full documentation: [.docs/PROJECT_CONTEXT.md](.docs/PROJECT_CONTEXT.md)
- 🐛 Report bugs: https://github.com/int33k/M-ACT/issues
- 💬 Discussions: https://github.com/int33k/M-ACT/discussions

---

**Happy Collaborating! 🎉**
