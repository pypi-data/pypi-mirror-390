# MACT Quick Start Guide - For End Users

**Install in 30 seconds, create your first room in 2 minutes!**

---

## 🚀 Installation (Choose One Method)

### Method 1: pip install (Recommended - Super Easy!)

```bash
# Install directly from GitHub
pip install git+https://github.com/int33k/M-ACT.git

# Verify installation
mact --help
```

**Done!** The `mact` command is now available globally.

---

### Method 2: pipx install (Isolated Installation)

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install MACT
pipx install git+https://github.com/int33k/M-ACT.git

# Verify
mact --help
```

---

### Method 3: Local clone (For development)

```bash
git clone https://github.com/int33k/M-ACT.git ~/mact-cli
cd ~/mact-cli
pip install -e .

# Verify
mact --help
```

---

## 🎯 Quick Start - Create Your First Room

### Step 1: Initialize (One-time setup)

```bash
mact init --name YourName
```

### Step 2: Start your dev server

```bash
# Example: React app on port 3000
cd ~/my-react-app
npm start
```

### Step 3: Create a room (one command!)

```bash
# Syntax: mact create PROJECT_NAME -port PORT_NUMBER
mact create TelegramBot -port 5000
```

**That's it!** 🎉 Your room is now live at:
- 🪞 **Mirror:** https://telegrambot.m-act.live/
- 📊 **Dashboard:** https://telegrambot.m-act.live/dashboard

**What happened automatically:**
- ✅ Room created on backend
- ✅ Git post-commit hook installed
- ✅ FRP tunnel started (localhost:5000 → public URL)
- ✅ You're the active developer

---

## 👥 Join an Existing Room

Your teammate shares a room code with you: `my-project`

```bash
# Start your dev server on a different port
cd ~/my-local-copy
npm start  # runs on port 3001

# Join the room
mact join my-project -port 3001
```

**Done!** You're now in the room. Make a commit to become the active developer.

---

## 🔄 Daily Workflow

### Morning: Check status

```bash
mact status
```

Shows all your active rooms.

### During development: Just commit!

```bash
# Make changes
vim src/components/Header.js

# Commit (this makes you active!)
git add .
git commit -m "Update header design"

# 🎉 Public URL now shows YOUR localhost automatically
```

### Evening: Leave room (optional)

```bash
mact leave my-project
```

---

## 📖 Command Reference

### Initialize
```bash
mact init --name YourName
```

### Create Room
```bash
# Basic
mact create ProjectName -port 3000

# With custom subdomain
mact create ProjectName -port 3000 --subdomain dev-custom-name
```

### Join Room
```bash
# Basic
mact join ROOM-CODE -port 3001

# Alternative syntax
mact join -join ROOM-CODE -port 3001
```

### Leave Room
```bash
mact leave --room ROOM-CODE
```

### Check Status
```bash
mact status
```

---

## 🆘 Troubleshooting

### "mact: command not found"

**Fix:**
```bash
# Ensure pip bin directory is in PATH
python3 -m pip show mact-cli

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc
```

### "Developer ID not set"

**Fix:**
```bash
mact init --name YourName
```

### Tunnel won't connect

**Check:**
```bash
# Is the backend reachable?
curl https://m-act.live/health

# Is your port correct?
curl http://localhost:3000
```

### Public URL shows 404

**Causes:**
1. Your dev server isn't running
2. Wrong port specified
3. You're not the active developer

**Fix:**
```bash
# Ensure dev server is running
curl http://localhost:YOUR_PORT

# Make a commit to become active
git commit --allow-empty -m "Make me active"
```

---

## 💡 Pro Tips

### Tip 1: Alias for convenience

Add to `~/.bashrc`:
```bash
alias mcreate='mact create'
alias mjoin='mact join'
alias mstatus='mact status'
```

### Tip 2: Multiple projects

You can have multiple rooms active:
```bash
# Project 1
cd ~/project1
mact create project1 -port 3000

# Project 2
cd ~/project2
mact create project2 -port 3001
```

### Tip 3: Auto-start on shell startup

Add to `~/.bashrc`:
```bash
# Auto-show MACT status
if command -v mact &> /dev/null; then
    mact status
fi
```

---

## 🔗 Links

- **Production:** https://m-act.live
- **GitHub:** https://github.com/int33k/M-ACT
- **Docs:** https://github.com/int33k/M-ACT/tree/main/.docs
- **Issues:** https://github.com/int33k/M-ACT/issues

---

## ❓ FAQ

**Q: Do I need to install anything besides pip?**  
A: No! pip install handles everything.

**Q: Can I uninstall?**  
A: Yes: `pip uninstall mact-cli`

**Q: Does it work on Windows?**  
A: WSL2 recommended. Native Windows support is limited.

**Q: Is my code sent to MACT servers?**  
A: No! Only commit metadata. Your code stays on your machine.

**Q: Can I use without git?**  
A: MACT requires git for commit tracking. Initialize with `git init`.

---

**Installation time:** 30 seconds  
**First room:** 2 minutes  
**Learning curve:** Minimal

**Get started now!** 🚀
