# MACT Live Demonstration Guide

**For Project Presentations & Demos**  
**Duration:** 15-20 minutes  
**Last Updated:** November 8, 2025

---

## 📋 Table of Contents
1. [Pre-Demo Setup](#pre-demo-setup)
2. [Demo Scenario](#demo-scenario)
3. [Step-by-Step Demo Script](#step-by-step-demo-script)
4. [Talking Points](#talking-points)
5. [Backup Plans](#backup-plans)
6. [FAQ Preparation](#faq-preparation)

---

## Pre-Demo Setup

### 1. Server Readiness (Do This 1 Hour Before)

```bash
# SSH into your server
ssh deploy@m-act.live

# Check all services are running
sudo systemctl status mact-backend
sudo systemctl status mact-proxy
sudo systemctl status mact-frps

# Verify health
curl https://m-act.live/health
# Expected: {"status":"healthy","rooms_count":0}

# Check SSL certificate
sudo certbot certificates

# Verify DNS
dig m-act.live
dig demo.m-act.live
```

### 2. Prepare Two Demo Workspaces

**Workspace 1: React App (Developer A)**
```bash
mkdir -p ~/demo/dev-a
cd ~/demo/dev-a

# Create React app
npx create-react-app demo-app
cd demo-app

# Initialize as demo developer
cd ~/mact-cli
source .venv/bin/activate
python -m cli.cli init --name developer-a

# Start dev server (keep running)
cd ~/demo/dev-a/demo-app
npm start  # Runs on port 3000
```

**Workspace 2: React App (Developer B)**
```bash
mkdir -p ~/demo/dev-b
cd ~/demo/dev-b

# Clone same project
cp -r ~/demo/dev-a/demo-app ~/demo/dev-b/demo-app
cd demo-app

# Initialize as different developer
cd ~/mact-cli
source .venv/bin/activate
python -m cli.cli init --name developer-b

# Start dev server on different port
cd ~/demo/dev-b/demo-app
PORT=3001 npm start  # Runs on port 3001
```

### 3. Verify Local Setup

```bash
# Check Developer A's app
curl http://localhost:3000

# Check Developer B's app
curl http://localhost:3001

# Both should return React HTML
```

### 4. Open Required Browser Tabs

**Before demo starts, open:**
1. `https://m-act.live/` (main site)
2. `https://demo-room.m-act.live/` (will be created - keep ready)
3. `https://demo-room.m-act.live/dashboard` (dashboard)
4. `http://localhost:3000` (Dev A's localhost)
5. `http://localhost:3001` (Dev B's localhost)

### 5. Prepare Terminal Windows

**Layout (use tmux or split terminals):**
```
┌─────────────────────┬─────────────────────┐
│   Developer A       │   Developer B       │
│   (Terminal 1)      │   (Terminal 2)      │
│                     │                     │
│   ~/demo/dev-a/     │   ~/demo/dev-b/     │
│   demo-app/         │   demo-app/         │
└─────────────────────┴─────────────────────┘
```

---

## Demo Scenario

**Title:** "Real-Time Collaborative Development with Git-Driven URL Mirroring"

**Story:**
> Two developers, Alice (Developer A) and Bob (Developer B), are working on the same React application from different machines. They need to share their work-in-progress with each other and stakeholders instantly, without waiting for deployment. MACT gives them one persistent URL that automatically mirrors whoever made the latest commit.

**Key Points to Demonstrate:**
1. ✅ Room creation with zero configuration
2. ✅ Automatic tunnel setup
3. ✅ Git-driven active developer switching
4. ✅ Real-time dashboard updates
5. ✅ Persistent public URL
6. ✅ Support for modern frameworks (React with HMR)

---

## Step-by-Step Demo Script

### Introduction (2 minutes)

**[Show title slide or README.md]**

> "Today I'm demonstrating MACT - Mirrored Active Collaborative Tunnel - a platform that solves the preview problem in collaborative development.
>
> Traditional tools like Vercel require build-and-deploy cycles. Tunnels like ngrok are single-user. MACT combines the best of both: persistent room URLs that auto-mirror the developer with the latest Git commit."

**[Show architecture diagram from PROJECT_CONTEXT.md]**

> "The system has four components: a coordination backend that tracks rooms and commits, a routing proxy that handles subdomains, FRP for tunneling, and a CLI that developers use to create and join rooms."

---

### Act 1: Room Creation (3 minutes)

**[Switch to Terminal 1 - Developer A]**

> "Let's say Alice is starting work on a new feature. She has a React app running on her localhost port 3000."

```bash
# Show localhost
curl http://localhost:3000
# (or open in browser to show React app)
```

> "She wants to share this with her team. With MACT, it's one command:"

```bash
cd ~/demo/dev-a/demo-app
python -m cli.cli create \
  --project demo-room \
  --subdomain dev-alice-demo \
  --local-port 3000
```

**[Point out the output]**

```
✅ Room created successfully!

Room Details:
  Room Code: demo-room
  Public URL: https://demo-room.m-act.live/
  Dashboard: https://demo-room.m-act.live/dashboard
  
Your Tunnel:
  Subdomain: dev-alice-demo.m-act.live
  Local Port: 3000
  Status: Connected ✅
```

> "Notice what happened automatically:
> 1. Room created on backend
> 2. Git hook installed
> 3. FRP tunnel established
> 4. Public URL is live"

**[Switch to browser - https://demo-room.m-act.live/]**

> "And here's Alice's localhost:3000, now accessible at a public URL. No deployment, no build step - instant."

**[Open dashboard - https://demo-room.m-act.live/dashboard]**

> "The dashboard shows Alice is the only participant and is currently active."

---

### Act 2: Collaborative Joining (3 minutes)

**[Switch to Terminal 2 - Developer B]**

> "Now Bob wants to collaborate. He has the same project on his machine, running on port 3001."

```bash
cd ~/demo/dev-b/demo-app
python -m cli.cli join \
  --room demo-room \
  --subdomain dev-bob-demo \
  --local-port 3001
```

**[Show output]**

```
✅ Joined room successfully!

Room Details:
  Room Code: demo-room
  Public URL: https://demo-room.m-act.live/
  
Your Tunnel:
  Subdomain: dev-bob-demo.m-act.live
  Local Port: 3001
  Status: Connected ✅

Other Participants:
  - developer-a (active)
  - developer-b (you)
```

> "Bob is now in the room. His tunnel is running, but notice - Alice is still active."

**[Switch to dashboard]**

> "The dashboard updates automatically via WebSocket. We now see both developers."

---

### Act 3: Active Developer Switching (4 minutes)

**[Keep dashboard visible in one half, terminals in other half]**

> "Here's where the magic happens. Watch what happens when Bob makes a commit."

**[Terminal 2 - Developer B]**

```bash
# Make a visible change
echo "/* Bob's feature */" >> src/App.js

# Commit
git add .
git commit -m "feat: Add Bob's feature"
```

**[Immediately show dashboard]**

> "The git hook automatically reported the commit to the backend. Watch the dashboard..."

**[Dashboard should update within 1-2 seconds showing developer-b as active]**

> "Bob is now active! And if we refresh the public URL..."

**[Refresh https://demo-room.m-act.live/]**

> "The public URL now shows Bob's localhost:3001. No manual switching, no configuration - Git commits drive the routing."

**[Terminal 1 - Developer A]**

> "Alice can commit too:"

```bash
# Make a change
echo "/* Alice's feature */" >> src/App.css

# Commit
git add .
git commit -m "feat: Add Alice's feature"
```

**[Show dashboard switching back]**

> "Active developer switches back to Alice. The URL now shows her work."

---

### Act 4: Real-Time Dashboard Features (3 minutes)

**[Focus on dashboard tab]**

> "The dashboard provides real-time visibility into the room state."

**[Point out features]**

1. **Active Developer Badge**
   > "Green badge shows who's currently active"

2. **Participant Cards**
   > "All team members listed with their tunnel URLs"

3. **Commit History**
   > "Chronological list of all commits with messages and authors"

4. **Live Search**
   > "We can filter commits in real-time"
   
   ```
   [Type in search box: "Bob"]
   ```
   
   > "Instantly filters to Bob's commits only"

5. **Auto-Refresh**
   > "Updates every 5 seconds automatically, or instantly via WebSocket"

---

### Act 5: Framework Support (2 minutes)

**[Split screen: localhost and public URL]**

> "MACT supports modern development frameworks. Let me show React Hot Module Replacement."

**[Edit App.js in Developer A's workspace]**

```javascript
// Change something visible
<h1>Hello MACT Demo!</h1>
```

**[Save file - don't commit yet]**

> "On localhost, React HMR updates instantly..."

**[Show localhost:3000 updates]**

> "Now I commit:"

```bash
git add .
git commit -m "Update heading"
```

**[Show public URL]**

> "And the public URL updates too. WebSocket forwarding means Vite, Next.js, and Socket.IO all work seamlessly."

---

### Conclusion (2 minutes)

**[Show PROJECT_COMPLETION_REPORT.md or summary slide]**

> "Let me summarize what we've seen:
>
> **Features Demonstrated:**
> - ✅ Zero-config room creation
> - ✅ Automatic tunnel setup
> - ✅ Git-driven active developer switching
> - ✅ Real-time WebSocket dashboard
> - ✅ Framework support (React HMR)
> - ✅ Persistent public URLs
>
> **Technical Highlights:**
> - 36 tests passing (100% coverage)
> - Production-ready security
> - Supports 5-10 developers per room
> - Wildcard SSL with Let's Encrypt
> - Systemd services with auto-restart
>
> **Use Cases:**
> - Remote team collaboration
> - Client demos (no deployment needed)
> - Code reviews with live previews
> - Educational settings (multiple students, one URL)
>
> MACT is open-source, production-ready, and running at m-act.live. Thank you!"

---

## Talking Points

### When Asked: "How is this different from ngrok?"

**Answer:**
> "ngrok is great for single-user tunneling, but it doesn't support collaboration. Each developer gets their own URL, and there's no automatic switching. MACT gives you **one persistent URL** for the entire room that **automatically mirrors** whoever made the latest commit. It's designed for teams, not individuals."

### When Asked: "Why not just use Vercel Preview Deployments?"

**Answer:**
> "Vercel is excellent for production deployments, but previews require build and deploy cycles - typically 2-5 minutes. With MACT, changes are **instant**. You commit, and the public URL updates in under a second. Plus, Vercel previews are per-branch, not per-developer. MACT tracks individual developers in real-time."

### When Asked: "What if I don't want to commit to switch?"

**Answer:**
> "That's by design. MACT uses Git commits as the source of truth because commits represent meaningful progress. If you need to share un-committed changes, you can use `git commit --amend` or make throwaway commits. The goal is to encourage good Git hygiene."

### When Asked: "Can this scale to large teams?"

**Answer:**
> "Currently, MACT is optimized for 5-10 developers per room, which covers most agile teams. For larger teams, we recommend creating multiple rooms (e.g., by feature branch). The architecture can scale horizontally by adding more proxy instances, which is a future enhancement."

### When Asked: "Is my code secure?"

**Answer:**
> "Absolutely. Your code stays on your machine - MACT never stores or accesses it. We only receive commit metadata (hash, message, branch) and tunnel HTTP requests. All communication is over SSL/TLS in production, and tunnels use token authentication."

---

## Backup Plans

### If Internet Fails

**Switch to Local Demo:**
```bash
# Show localhost-only demo
# Change URLs to:
# - http://demo-room.localhost:9000/
# - http://demo-room.localhost:9000/dashboard

# Show all services running locally
python -m backend.app  # Port 5000
python -m proxy.app    # Port 9000
./scripts/run_frp_local.sh  # Port 7100

# Demo works identically on localhost
```

### If Services Are Down

**Show Pre-Recorded Screen Recording:**
- Have a backup video of the full demo
- Play while narrating live
- Emphasize it's the same workflow

### If Time Is Short (10-minute version)

**Condensed Demo:**
1. Introduction (1 min)
2. Room creation (2 min)
3. Commit and switch demo (4 min)
4. Dashboard overview (2 min)
5. Conclusion (1 min)

**Skip:**
- Second developer joining
- Framework-specific features
- Deep dashboard exploration

---

## FAQ Preparation

### Technical Questions

**Q: What happens if two developers commit at the same time?**

**A:** The backend processes commits sequentially. The last commit to reach the backend wins. In practice, this is rare, and developers can see the switch on the dashboard.

---

**Q: Can I roll back to a previous developer?**

**A:** Not currently. The active developer is always the one with the latest commit. To "roll back," that developer would need to commit again. This is a future enhancement.

---

**Q: Does it work with mobile apps / desktop apps?**

**A:** MACT is designed for web applications that run HTTP servers. For mobile/desktop, you could proxy the development API, but the dashboard and mirror are web-focused.

---

**Q: What's the latency?**

**A:** Typical request latency is < 100ms (proxy) + your localhost response time. WebSocket updates are near-instant (< 50ms).

---

### Business Questions

**Q: Is MACT open-source?**

**A:** Yes, MIT License. Free to use, modify, and distribute.

---

**Q: Can I self-host MACT?**

**A:** Absolutely. We provide full deployment scripts for Ubuntu 22.04 + nginx + systemd. See PRODUCTION_DEPLOYMENT_GUIDE.md.

---

**Q: What's the pricing model?**

**A:** The public instance (m-act.live) is free for academic/personal use. For commercial/enterprise, contact us for support and SLAs.

---

**Q: Can I get support?**

**A:** Community support via GitHub Issues and Discussions. Paid support available for enterprises.

---

## Post-Demo

### Invite Action

> "Interested in trying MACT? Here's how to get started:
>
> 1. **Clone the repo:**
>    ```bash
>    git clone https://github.com/int33k/M-ACT.git
>    ```
>
> 2. **Read the docs:**
>    - Quick Start: README.md
>    - Installation: .docs/CLIENT_INSTALLATION_GUIDE.md
>    - Deployment: .docs/PRODUCTION_DEPLOYMENT_GUIDE.md
>
> 3. **Join the community:**
>    - Star the repo on GitHub
>    - Open issues for bugs
>    - Contribute via pull requests
>
> **Links:**
> - GitHub: https://github.com/int33k/M-ACT
> - Production: https://m-act.live
> - Documentation: https://github.com/int33k/M-ACT/tree/main/.docs"

### Follow-Up Materials

**Send to attendees:**
- Link to GitHub repository
- Link to PROJECT_COMPLETION_REPORT.md
- Link to CLIENT_INSTALLATION_GUIDE.md
- Demo video (if recorded)
- Slides (if used)

---

## Demo Checklist

### 1 Day Before
- [ ] Verify server is running
- [ ] Check SSL certificate expiry
- [ ] Test full demo flow locally
- [ ] Prepare backup video
- [ ] Charge laptop

### 1 Hour Before
- [ ] Check internet connection
- [ ] Verify all services running
- [ ] Test health endpoints
- [ ] Open browser tabs
- [ ] Setup terminal layouts
- [ ] Run through demo once

### 5 Minutes Before
- [ ] Close unnecessary applications
- [ ] Disable notifications
- [ ] Increase terminal font size
- [ ] Verify mic/audio (if remote)
- [ ] Open demo script
- [ ] Take a deep breath 😊

### During Demo
- [ ] Speak slowly and clearly
- [ ] Point out key features
- [ ] Show dashboard updates
- [ ] Engage with audience
- [ ] Leave time for Q&A

### After Demo
- [ ] Thank attendees
- [ ] Share links
- [ ] Collect feedback
- [ ] Follow up on questions

---

**Demo Duration:** 15-20 minutes  
**Preparation Time:** 30 minutes  
**Difficulty:** Easy  
**Success Rate:** High (with prep)

**Good luck with your demo! 🚀**
