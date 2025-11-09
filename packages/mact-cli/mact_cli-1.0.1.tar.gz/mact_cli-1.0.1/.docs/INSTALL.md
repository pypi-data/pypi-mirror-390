# MACT CLI - Installation & Usage Guide

## 🚀 Quick Install

### Option 1: Install from PyPI (Production - Future)
```bash
pip install mact-cli
```

### Option 2: Install from Source (Current)
```bash
# Clone the repository
git clone https://github.com/mact/mact.git
cd mact

# Install in development mode
pip install -e .
```

### Option 3: Install as Package
```bash
# Build and install
pip install .
```

## 📋 Verify Installation

After installation, verify the `mact` command is available:

```bash
mact --help
```

You should see:
```
usage: mact [-h] {init,create,join,leave,status} ...

MACT CLI - Collaborative Development Tunnel

positional arguments:
  {init,create,join,leave,status}
    init                Initialize developer identity
    create              Create a new room
    join                Join an existing room
    leave               Leave a room
    status              Show active room memberships
```

## 🎯 Usage Workflow

### 1. Initialize Your Developer Identity (One-time setup)

```bash
mact init --name alice
```

This creates `~/.mact_config.json` with your developer ID.

**Output:**
```
Initialized developer_id=alice (saved to /home/alice/.mact_config.json)
```

---

### 2. Create a Room (First Developer)

```bash
cd /path/to/your/project  # Must be a git repository
mact create --project my-awesome-app --subdomain http://dev-alice.m-act.live
```

**What happens automatically:**
1. ✅ Room created on backend
2. ✅ FRP tunnel started (localhost → public subdomain)
3. ✅ **Git post-commit hook installed** in `.git/hooks/post-commit`
4. ✅ Room membership saved to `~/.mact_rooms.json`

**Output:**
```
✓ Room created: my-awesome-app -> http://my-awesome-app.m-act.live
✓ Room membership saved
✓ Tunnel started: dev-alice -> localhost:3000
✓ Git post-commit hook installed
```

---

### 3. Join a Room (Additional Developers)

```bash
cd /path/to/your/project  # Your local clone of the project
mact join --room my-awesome-app --subdomain http://dev-bob.m-act.live
```

**What happens automatically:**
1. ✅ Joined room on backend
2. ✅ FRP tunnel started for your localhost
3. ✅ **Git post-commit hook installed** in `.git/hooks/post-commit`
4. ✅ Room membership saved

**Output:**
```
✓ Joined room: my-awesome-app
✓ Room membership saved
✓ Tunnel started: dev-bob -> localhost:3000
✓ Git post-commit hook installed
```

---

### 4. Work Normally - Git Hooks Do the Magic! ✨

Now just work normally:

```bash
# Make changes to your code
echo "new feature" >> index.html

# Commit as usual
git add .
git commit -m "feat: added new feature"
```

**The git hook automatically:**
- Extracts commit hash, message, branch
- Calls backend `/report-commit` API
- Updates active developer status
- **No manual steps required!**

**Terminal output after commit:**
```
[main abc1234] feat: added new feature
 1 file changed, 1 insertion(+)
✓ Commit reported to MACT (Room: my-awesome-app)
```

---

### 5. Check Status

```bash
mact status
```

**Output:**
```
Active Room Memberships:
  • my-awesome-app (developer: alice)
    Local: localhost:3000
    Subdomain: http://dev-alice.m-act.live
    Backend: http://localhost:5000
```

---

### 6. Leave a Room

```bash
mact leave --room my-awesome-app
```

**What happens:**
1. ✅ Tunnel stopped
2. ✅ Leaves room on backend
3. ✅ Room membership removed from config
4. ℹ️  Git hook remains (you can remove manually if needed)

---

## 🔧 Advanced Options

### Custom Backend URL
```bash
export BACKEND_BASE_URL=https://api.m-act.live
mact create --project myapp --subdomain http://dev-alice.m-act.live
```

### Custom FRP Server
```bash
export FRP_SERVER_ADDR=frp.m-act.live
export FRP_SERVER_PORT=7100
mact create --project myapp --subdomain http://dev-alice.m-act.live
```

### Custom Local Port
```bash
mact create --project myapp --subdomain http://dev-alice.m-act.live --local-port 8080
```

### Skip Tunnel (Testing)
```bash
mact create --project myapp --subdomain http://dev-alice.m-act.live --no-tunnel
```

### Skip Git Hook (Testing)
```bash
mact create --project myapp --subdomain http://dev-alice.m-act.live --no-hook
```

---

## 📁 Configuration Files

### Developer Config: `~/.mact_config.json`
```json
{
  "developer_id": "alice"
}
```

### Room Memberships: `~/.mact_rooms.json`
```json
{
  "rooms": [
    {
      "room_code": "my-awesome-app",
      "developer_id": "alice",
      "subdomain_url": "http://dev-alice.m-act.live",
      "local_port": 3000,
      "backend_url": "http://localhost:5000"
    }
  ]
}
```

### Git Hook: `.git/hooks/post-commit`
```bash
#!/usr/bin/env bash
# MACT post-commit hook - Auto-generated
BACKEND_URL=http://localhost:5000
DEVELOPER_ID=alice
ROOM_CODE=my-awesome-app

COMMIT_HASH=$(git rev-parse --short HEAD)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
MSG=$(git log -1 --pretty=%B)

curl -s -X POST "$BACKEND_URL/report-commit" \
  -H "Content-Type: application/json" \
  -d "{\"room_code\": \"$ROOM_CODE\", \"developer_id\": \"$DEVELOPER_ID\", \"commit_hash\": \"$COMMIT_HASH\", \"branch\": \"$BRANCH\", \"commit_message\": \"$MSG\"}" >/dev/null
```

---

## 🎓 Complete Example Workflow

### Developer 1 (Alice):
```bash
# One-time setup
mact init --name alice

# Start new project
cd ~/projects/my-app
git init
echo "Hello World" > index.html
git add .
git commit -m "Initial commit"

# Create MACT room
mact create --project my-app --subdomain http://dev-alice.m-act.live

# Work normally
echo "Feature 1" >> index.html
git add .
git commit -m "feat: added feature 1"  # ← Git hook auto-reports!
```

### Developer 2 (Bob):
```bash
# One-time setup
mact init --name bob

# Clone project
cd ~/projects
git clone https://github.com/team/my-app.git
cd my-app

# Join MACT room
mact join --room my-app --subdomain http://dev-bob.m-act.live

# Work normally
echo "Feature 2" >> index.html
git add .
git commit -m "feat: added feature 2"  # ← Git hook auto-reports!
```

### Result:
- Public URL `http://my-app.m-act.live` automatically shows Bob's localhost (latest commit)
- Dashboard shows both developers and commit history
- No manual intervention needed!

---

## 🐛 Troubleshooting

### "Developer ID not set"
```bash
mact init --name your-name
```

### "Not a git repository"
```bash
cd /path/to/your/project
git init
```

### Hook not executing
```bash
# Check if hook exists and is executable
ls -la .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

### Tunnel connection issues
```bash
# Check FRP server is running
curl http://localhost:7100  # Should respond

# Check backend is running
curl http://localhost:5000/health  # Should return {"status":"healthy"}
```

---

## 📚 Documentation

- [Project Context](.docs/PROJECT_CONTEXT.md)
- [CLI Documentation](cli/README.md)
- [Backend API](backend/README.md)
- [Deployment Guide](.docs/DEPLOYMENT.md)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) file.
