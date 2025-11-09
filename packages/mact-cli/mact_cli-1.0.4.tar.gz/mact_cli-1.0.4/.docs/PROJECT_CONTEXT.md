# Project Context Brief: MACT (Mirrored Active Collaborative Tunnel)
_Last Updated: 2025-10-19_

This document is the single source of truth for the MACT project. All AI-assisted coding and architectural discussions must adhere to this brief to ensure consistency and prevent chaos.

---
## 1. Project Vision & Core Concept 🎯

-   **Project Name:** MACT
-   **University Version:** MANUU Active Collaborative Tunnel
-   **Professional Version:** Mirrored Active Collaborative Tunnel
-   **Domain:** `m-act.live`

**Core Concept:** MACT is a collaborative development platform that provides a **single, persistent public URL** for a project "room." This URL acts as a **live mirror**, automatically and instantaneously showing the `localhost` environment of the developer within that room who has the most recent Git commit.

**Problem Solved:** It eliminates the delays of deployment-based previews (like Vercel) and the limitations of single-user tunnels (like ngrok), enabling true real-time, Git-synced, collaborative previews for agile teams.

**Novelty:** The innovation lies in the **unique architectural pattern** that integrates live tunneling, Git-driven dynamic routing, and multi-user session management into a unified system.

---
## 2. Research Hypothesis 🔬

> "A **centralized coordination backend**, capable of monitoring the Git state of multiple distributed developer environments, can create a **unified, live, and persistent public preview URL**. This architecture solves the limitations of both single-user tunnels and slow, deployment-based previews, thereby accelerating collaborative development cycles."

---
## 3. System Architecture (Room-Based Model) 🏗️

The system is a distributed application composed of four primary components, designed to support multiple, isolated collaborative "rooms."



### A. Tunnel Client (Developer's Local Machine)

-   **Description:** A command-line interface (CLI) that developers use to create and join collaborative rooms.
-   **Responsibilities:**
    1.  Parse user commands (`mact init`, `mact create`, `mact join`). 
    <!-- The init command performs a one-time setup to store a unique developer_id (name for simpler implementation) in a local configuration file. e.g. mact init --name siddhant -->
    2.  Communicate with the Coordination Backend to manage room state.
    3.  **Automatically install a `post-commit` Git hook** into the user's local repository.
    4.  Run and manage the `frpc` tunnel client process in the background.

### B. Coordination Backend (Central Server)
- **Description:** The "brain" of the system, implemented as a Python/Flask API.
- **Responsibilities:**
    1. Manage the lifecycle of collaborative rooms (create, join).
    2. Track the participants in each room and their individual tunnel URLs.
    3. Receive real-time Git state updates from Tunnel Clients via the `/report-commit` endpoint.
    4. **Maintain a historical log of commits for each room.**
    5. Determine which developer is "active" for each room based on the latest commit.
    6. Provide room status and commit history to the Web Dashboard.
    7. **State Storage (PoC):** Uses an in-memory Python dictionary. The value for each room will contain a **list to store the commit history**.

### C. Public Routing Proxy (Central Server)

-   **Description:** The public-facing entry point for all project rooms, also a Python/Flask application.
-   **Responsibilities:**
    1.  Run the `frps` tunnel server to accept connections from all `frpc` clients.
    2.  Act as a **true reverse proxy** (NO HTTP REDIRECTS).
    3.  When a request arrives for a room URL (e.g., `alpha-bravo-77.m-act.live`), it extracts the room code.
    4.  It queries the Coordination Backend to get the active developer's tunnel URL.
    5.  It **internally fetches content** from the active developer's tunnel and serves it to the user.
    6.  Serve the Web Dashboard page and a fallback page if no developer is active.

### D. Web Dashboard (UI Component)
- **Description:** A simple web page served by the Public Routing Proxy.
- **Responsibilities:**
    1. Accessed via a specific URL (e.g., `<room_code>.m-act.live/dashboard`).
    2. Displays real-time status for a specific room: active developer, all participants, latest commit hash.
    3. **Displays a chronological list of recent commits, including the commit message and author (developer_id).**
    4. Fetches this data by making an API call to the Coordination Backend.

---
## 4. Technology Stack 🛠️

-   **Server Hosting:** DigitalOcean Droplet (Ubuntu 22.04 LTS) from GitHub Student Pack.
-   **Domain & DNS:** `m-act.live` from Name.com + DigitalOcean DNS for wildcard records.
-   **Tunneling:** `frp` (Fast Reverse Proxy).
-   **Backend & Proxy:** Python 3 with Flask.
-   **Client CLI:** Python 3 (using `argparse` for commands).
-   **Automation:** Bash script for the `post-commit` Git hook.

---
## 5. API Contract (Coordination Backend) 📜

### `POST /rooms/create`
- **Description:** Creates a new collaborative room.
- **Request Body (JSON):** `{ "project_name": "WebApp-Beta", "developer_id": "siddhant", "subdomain_url": "http://dev-siddhant.m-act.live" }`
- **Response (JSON):** `{ "room_code": "webapp-beta", "public_url": "http://webapp-beta.m-act.live" }`

### `POST /rooms/join`
- **Description:** Adds a developer to an existing room.
- **Request Body (JSON):** `{ "room_code": "webapp-beta", "developer_id": "alisha", "subdomain_url": "http://dev-alisha.m-act.live" }`
- **Response (JSON):** `{ "status": "success", "public_url": "http://webapp-beta.m-act.live" }`

### `POST /rooms/leave`
- **Description:** Removes a developer from a room.
- **Request Body (JSON):** `{ "room_code": "webapp-beta", "developer_id": "siddhant" }`
- **Response (JSON):** `{ "status": "success" }`

### `POST /report-commit`
- **Description:** Receives Git state updates from a developer's client (triggered by the hook).
- **Request Body (JSON):**
  ```json
  {
    "room_code": "webapp-beta",
    "developer_id": "siddhant",
    "commit_hash": "a1b2c3d4",
    "branch": "main",
    "commit_message": "feat: Add user login button"
  }

### `GET /get-active-url`
- **Description:** Returns the active developer's individual tunnel URL for a given room. **Always returns a URL** if the room has participants (never null).
- **Active Logic:** 
  - No commits: First developer who joined (by join order)
  - With commits: Developer with latest commit
  - Developer leaves: Falls back to next participant
- **Query Parameter:** `?room=webapp-beta`
- **Response (JSON):** `{ "active_url": "http://dev-siddhant.m-act.live" }` or `{ "active_url": null }` if no participants.

### `GET /rooms/status`
- **Description:** Returns detailed status information for a room for the dashboard.
- **Query Parameter:** `?room=webapp-beta`
- **Response (JSON):** `{ "room_code": "webapp-beta", "active_developer": "siddhant", "latest_commit": "a1b2c3d4", "participants": ["siddhant", "alisha"] }`

### `GET /rooms/<room_code>/commits`
- **Description:** Returns commit history for a room.
- **Response (JSON):** `{ "room_code": "webapp-beta", "commits": [{"commit_hash": "a1b2c3d4", "developer_id": "siddhant", "branch": "main", "commit_message": "feat: Add login", "timestamp": 1729512345.67}] }`

### `GET /admin/rooms`
- **Description:** Lists all rooms (admin endpoint).
- **Response (JSON):** `{ "rooms": [{"room_code": "webapp-beta", "participants": ["siddhant", "alisha"], "commit_count": 3}] }`

### `GET /health`
- **Description:** Health check endpoint.
- **Response (JSON):** `{ "status": "healthy", "rooms_count": 2 }`

### Validation Rules
- **Room creation:** Returns 409 if room with same project name already exists
- **Room joining:** Returns 409 if developer already in room (no duplicate joins)
- **Commit reporting:** Returns 403 if developer not in room (must join first)
- **CORS:** Enabled for dashboard API calls
- **Active URL:** Always available if room has participants (uses join order as fallback)

---
## 6. Port Allocation & Workflow 🔌

### Development Environment Ports
- **Coordination Backend (API)**: Port 5000
- **Developer Projects (localhost)**: Ports 3000, 3001, 3002, etc.
- **Public Routing Proxy**: Port 9000 (reflects active developer's project)

### Active Developer Selection
1. **No commits**: First developer who created/joined the room
2. **After commits**: Developer with the most recent commit
3. **Developer leaves**: System falls back to remaining participants

---
## 7. Development Plan 🗺️

We are building this project in testable units, **locally first**, before deploying to the DigitalOcean server.

**Current Status (Updated: 2025-11-06):**
✅ **Unit 1: The Coordination Backend API** – **100% COMPLETE** (13 pytest cases passing, all endpoints secured)
   - All CRUD endpoints for rooms (create, join, leave) ✅
   - Commit reporting and tracking ✅
   - Active developer logic ✅
   - **Security integration complete** ✅ **NEW**
   - Input validation for all endpoints (room_code, developer_id, URLs, commit hashes, branches) ✅ **NEW**
   - @require_admin_auth decorator for admin endpoints ✅ **NEW**
   - Proper error handling with ValidationError responses ✅ **NEW**
   
✅ **Unit 2: The Public Routing Proxy** – **100% COMPLETE** (7 proxy tests + 1 integration test passing)
   - Mirror endpoint with async streaming support ✅
   - **WebSocket mirror endpoint with bidirectional forwarding** ✅
   - Dashboard rendering with room status + commits ✅
   - FRP process management (frps/frpc supervisor) ✅
   - Vendored frp v0.65.0 binaries + helper scripts ✅
   - **Migrated from Flask (WSGI) to Starlette (ASGI)** ✅
   - **Supports Vite HMR, Next.js Fast Refresh, Socket.IO, native WebSockets** ✅
   
✅ **Unit 3: Tunnel Client CLI** – **100% COMPLETE** (7 tests passing)
   - `mact init/create/join/leave/status` commands ✅
   - **Automatic frpc subprocess management via FrpcManager** ✅
   - **Zero-config tunnel setup: `mact create/join` auto-starts FRP tunnels** ✅
   - Git post-commit hook installation (automatic on create/join) ✅
   - Room membership tracking (`~/.mact_rooms.json`) ✅
   - **Complete automation: one command sets up room + git hook + tunnel** ✅
   - FrpcManager: Binary detection, TOML config generation, process lifecycle ✅
   
✅ **Unit 6: Security Hardening** – **100% COMPLETE** ✅ **NEW**
   - Input validation module (backend/security.py - 295 lines) ✅
   - All backend endpoints secured with validation decorators ✅
   - Authentication system with Bearer token for admin endpoints ✅
   - XSS prevention (HTML sanitization in commit messages) ✅
   - Comprehensive error handling with proper HTTP status codes ✅
   - **Test Infrastructure**: pytest.ini configured, all 33 tests passing (1 skipped)

✅ **Unit 4: Dashboard Polish** – COMPLETE
   - Modern responsive UI with gradient design and glassmorphism effects ✅
   - Auto-refresh every 5 seconds (pauses during search) ✅
   - Live search/filter for commits by hash, message, or developer ✅
   - Participant cards with active developer highlighting ✅
   - Status badges showing active developer, participant count, commit count ✅
   - Mobile-responsive design with breakpoints ✅
   - Error pages with modern gradient styling ✅
   - **Test Infrastructure**: All 7 dashboard/proxy tests passing

❌ **Unit 5: Production Deployment** – INFRASTRUCTURE READY (systemd services, nginx configs, deployment scripts exist)

---

## 🎯 FRP Tunnel Automation - COMPLETE

**Full automation achieved for FRP tunnel setup!**

### What Works:
- ✅ **`mact create --project X --local-port 3000`** → Automatically:
  - Creates room via backend API
  - Installs git post-commit hook
  - Starts FRP tunnel (localhost:3000 → subdomain.localhost:7101)
  
- ✅ **`mact join --room X --local-port 3001`** → Automatically:
  - Joins room via backend API
  - Installs git post-commit hook
  - Starts FRP tunnel (localhost:3001 → subdomain.localhost:7101)

- ✅ **Git commits** → Automatically:
  - Post-commit hook reports to backend
  - Backend updates active developer
  - Mirror endpoint switches to active developer's tunnel

### Implementation:
- **FrpcManager** (`cli/frpc_manager.py`): Manages frpc subprocess lifecycle
- **Binary Detection**: Finds vendored frpc binary (`third_party/frp/frpc`)
- **Config Generation**: Creates TOML config per developer
- **Process Management**: Starts/stops frpc subprocesses
- **Integration**: Called automatically by `mact create/join` commands

### Testing:
- **E2E Test**: `./scripts/e2e_with_tunnels.sh` - Uses real `mact` CLI commands
- **Documentation**: `FRP_AUTOMATION.md` - Complete implementation guide
- **Status**: All components working, ready for end-to-end verification

---

**Next Priority Options:**
- **Option A**: Unit 5 production deployment (infrastructure 100% ready in deployment/ directory)
- **Option B**: End-to-end testing with live FRP tunnels (validate full workflow)
- **Option C**: Performance optimization and load testing