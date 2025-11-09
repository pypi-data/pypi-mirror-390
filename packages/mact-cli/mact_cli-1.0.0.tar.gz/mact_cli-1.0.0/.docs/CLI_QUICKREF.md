# MACT CLI - Quick Reference Card

## 📦 Installation

```bash
# From source (development)
cd /path/to/mact
pip install -e .

# Verify installation
mact --help
```

## 🚀 Commands

### `mact init`
Initialize your developer identity (one-time setup)

```bash
mact init --name alice
```

**Creates:** `~/.mact_config.json`

---

### `mact create`
Create a new room and start collaboration

```bash
mact create --project my-app --subdomain http://dev-alice.m-act.live
```

**What it does:**
- ✅ Creates room on backend
- ✅ Starts FRP tunnel (localhost → subdomain)
- ✅ **Installs git post-commit hook** in `.git/hooks/post-commit`
- ✅ Saves room membership

**Options:**
- `--local-port PORT` - Local server port (default: 3000)
- `--no-tunnel` - Skip tunnel setup
- `--no-hook` - Skip git hook installation

---

### `mact join`
Join an existing room

```bash
mact join --room my-app --subdomain http://dev-bob.m-act.live
```

**What it does:**
- ✅ Joins room on backend
- ✅ Starts FRP tunnel
- ✅ **Installs git post-commit hook**
- ✅ Saves room membership

**Options:**
- `--local-port PORT` - Local server port (default: 3000)
- `--no-tunnel` - Skip tunnel setup
- `--no-hook` - Skip git hook installation

---

### `mact leave`
Leave a room and cleanup

```bash
mact leave --room my-app
```

**What it does:**
- ✅ Stops tunnel
- ✅ Leaves room on backend
- ✅ Removes room membership

---

### `mact status`
Show active room memberships

```bash
mact status
```

**Output:**
```
Active Room Memberships:
  • my-app (developer: alice)
    Local: localhost:3000
    Subdomain: http://dev-alice.m-act.live
    Backend: http://localhost:5000
```

---

## 🔥 The Magic: Git Hooks

After `mact create` or `mact join`, a git hook is automatically installed at:

```
.git/hooks/post-commit
```

**What the hook does:**
1. Runs automatically after every `git commit`
2. Extracts: commit hash, message, branch, timestamp
3. Calls backend `/report-commit` API
4. Updates active developer status
5. **Zero manual intervention needed!**

**Example:**
```bash
# Just commit normally
git add .
git commit -m "feat: new feature"

# Output:
[main abc1234] feat: new feature
 1 file changed, 1 insertion(+)
✓ Commit reported to MACT (Room: my-app)  ← Automatic!
```

---

## 🌍 Environment Variables

```bash
# Backend URL (default: http://localhost:5000)
export BACKEND_BASE_URL=https://api.m-act.live

# FRP server (default: 127.0.0.1:7100)
export FRP_SERVER_ADDR=frp.m-act.live
export FRP_SERVER_PORT=7100
```

---

## 📂 Files Created

| File | Purpose |
|------|---------|
| `~/.mact_config.json` | Your developer ID |
| `~/.mact_rooms.json` | Active room memberships |
| `.git/hooks/post-commit` | Auto-reports commits to backend |

---

## 🎯 Typical Workflow

```bash
# Developer 1 (First time)
mact init --name alice
cd ~/projects/my-app
git init
mact create --project my-app --subdomain http://dev-alice.m-act.live

# Work normally
git add .
git commit -m "feat: added feature"  # ← Auto-reports!

# Developer 2 (Joining)
mact init --name bob
cd ~/projects/my-app
mact join --room my-app --subdomain http://dev-bob.m-act.live

# Work normally
git add .
git commit -m "fix: bug fix"  # ← Auto-reports! Now Bob is active!
```

---

## ✨ Key Features

1. **One Command Setup**: `mact create` does everything
2. **Automatic Hooks**: Git hook installed automatically
3. **Zero Manual Work**: Just commit, hook handles the rest
4. **Active Developer Tracking**: Latest commit → active developer
5. **Persistent Rooms**: Room stays active until left
6. **Multi-Developer**: Multiple devs, one public URL

---

## 🐛 Common Issues

**"Developer ID not set"**
```bash
mact init --name your-name
```

**"Not a git repository"**
```bash
cd /path/to/project
git init
```

**Hook not executing**
```bash
chmod +x .git/hooks/post-commit
```

---

## 📚 More Help

```bash
mact --help
mact create --help
mact join --help
```

Full docs: [INSTALL.md](INSTALL.md)
