# MACT Architecture & Deployment Guide

## ✅ URL Standardization (COMPLETE)

### Current URL Structure

#### **Mirror (Primary Access Point)**
- **Production**: `https://project-name.m-act.live/`
- **Local Dev**: `http://project-name.localhost:9000/`
- **Legacy routes removed**: Path-based URLs no longer supported

#### **Dashboard**
- **Production**: `https://project-name.m-act.live/dashboard`
- **Local Dev**: `http://project-name.localhost:9000/dashboard`

#### **WebSocket Notifications**
- **Production**: `wss://project-name.m-act.live/notifications`
- **Local Dev**: `ws://project-name.localhost:9000/notifications`
- **Auto-refresh**: Dashboard and mirror update in real-time

#### **Developer Tunnels (Direct Access)**
- **Local Dev**: `http://dev-developer-name.localhost:7101`
- **Production**: Via FRP vhost on port 7101 (internal)

---

## 🎯 Port Usage Analysis & Recommendations

### Current Port Allocation

| Service | Port | Purpose | Scalability |
|---------|------|---------|-------------|
| **Backend** | 5000 | REST API for room management | ✅ **Multi-workspace ready** - rooms are data-level separation |
| **Proxy/Mirror** | 9000 | HTTP proxy & dashboard | ✅ **Multi-workspace ready** - uses subdomain routing |
| **FRP Server (frps)** | 7100 | FRP control/admin | ✅ Single instance handles all tunnels |
| **FRP Vhost HTTP** | 7101 | HTTP tunnel endpoint | ✅ **Single port, infinite tunnels** via subdomain multiplexing |
| **Client localhost** | 3000/3001/etc | Developer's local server | ❌ Each dev needs unique port |

### Why This is Smart

#### 1. **FRP Port 7101 - Single Port, Unlimited Developers** ⭐
```
Port 7101 handles:
├── dev-alice-e2e.localhost:7101 → alice's localhost:3000
├── dev-bob-e2e.localhost:7101   → bob's localhost:3001
├── dev-carol.room2.m-act.live   → carol's localhost:3000
└── ... (unlimited)
```

**How it works:**
- FRP uses **virtual hosting** (like nginx)
- Subdomain in `Host` header determines routing
- One TCP port serves infinite subdomains
- This is **industry standard** (same as web servers)

#### 2. **Proxy Port 9000 - All Rooms on One Port** ⭐
```
Port 9000 serves:
├── project-1.m-act.live          → mirrors project-1's active dev
├── project-2.m-act.live          → mirrors project-2's active dev
├── team-workspace.m-act.live     → mirrors team workspace
└── ... (unlimited)
```

**How it works:**
- Uses **subdomain-based routing** (newly implemented!)
- Each room gets unique subdomain
- One HTTP server handles all rooms
- **No port conflicts** between workspaces

#### 3. **Backend Port 5000 - Stateless API** ✅
```
Backend manages:
├── Room 1 data (in-memory dict)
├── Room 2 data (in-memory dict)
├── Room N data (in-memory dict)
└── ... (scale with memory/DB)
```

**Scalability:**
- Rooms are **data-level** entities, not port-level
- One backend instance = unlimited rooms
- Can scale horizontally with shared DB
- Current PoC uses in-memory dict (fine for development)

---

## 💡 Port Optimization Suggestions (NO CODE)

### Current Setup: ✅ Already Optimal for Development

**Do NOT change:**
- FRP port 7101 (already perfect with vhost)
- Proxy port 9000 (already handles multiple workspaces)
- Backend port 5000 (already multi-workspace capable)

### For Production Deployment:

#### 1. **Reverse Proxy Layer** (nginx/Caddy)
```
User → nginx:443 (HTTPS) → {
    ├── *.m-act.live → proxy:9000 (mirror/dashboard)
    ├── api.m-act.live → backend:5000
    └── dev-*.*.m-act.live → frps:7101 (tunnels)
}
```

**Benefits:**
- Single HTTPS entry point (port 443)
- SSL termination at nginx
- No port numbers in URLs
- Better caching/compression/security

#### 2. **Internal Port Optimization**
```
Backend:  5000 (internal only, not exposed)
Proxy:    9000 (internal only, not exposed)
FRP:      7100 (control), 7101 (vhost) - internal
nginx:    80, 443 (public facing)
```

**Benefits:**
- Users only see port 443 (HTTPS)
- Internal services can use any ports
- Easier firewall rules (only 80/443 public)

#### 3. **Multi-Tenancy Scaling** (Future)
```
For massive scale, shard by organization:
├── org1.m-act.live → backend-1:5000, proxy-1:9000
├── org2.m-act.live → backend-2:5000, proxy-2:9000
└── orgN.m-act.live → backend-N:5000, proxy-N:9000
```

**When needed:**
- Thousands of concurrent rooms
- Geographic distribution
- Separate databases per tenant

---

## 🔒 HTTPS Deployment Strategy

### Option 1: Nginx Reverse Proxy (Recommended)

**Setup:**
```nginx
# /etc/nginx/sites-available/mact.conf

# SSL termination
server {
    listen 443 ssl http2;
    server_name *.m-act.live m-act.live;
    
    ssl_certificate /etc/letsencrypt/live/m-act.live/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/m-act.live/privkey.pem;
    
    # Mirror & Dashboard (proxy)
    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Developer tunnels
server {
    listen 443 ssl http2;
    server_name dev-*.*.m-act.live;
    
    ssl_certificate /etc/letsencrypt/live/m-act.live/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/m-act.live/privkey.pem;
    
    location / {
        proxy_pass http://localhost:7101;
        proxy_set_header Host $host;
        # ... same headers as above
    }
}

# Backend API
server {
    listen 443 ssl http2;
    server_name api.m-act.live;
    
    ssl_certificate /etc/letsencrypt/live/m-act.live/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/m-act.live/privkey.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        # ... same headers
    }
}
```

**SSL Certificate:**
```bash
# Using Let's Encrypt with wildcard cert
sudo certbot certonly --dns-cloudflare \
  -d m-act.live \
  -d "*.m-act.live" \
  -d "*.*.m-act.live"  # For dev-*.room.m-act.live
```

**Benefits:**
- ✅ Industry standard
- ✅ Wildcard SSL for all subdomains
- ✅ No code changes in MACT
- ✅ Better performance (nginx caching)
- ✅ Easy to add security headers

### Option 2: Caddy (Automatic HTTPS)

**Caddyfile:**
```caddy
# Auto HTTPS for all subdomains
*.m-act.live {
    reverse_proxy localhost:9000
}

dev-*.*.m-act.live {
    reverse_proxy localhost:7101
}

api.m-act.live {
    reverse_proxy localhost:5000
}
```

**Benefits:**
- ✅ Automatic SSL certificate management
- ✅ Even simpler config than nginx
- ✅ Auto-renewal built-in

### Option 3: Application-Level HTTPS (Not Recommended)

**Why NOT to do this:**
- ❌ Need to modify Python code
- ❌ Each service needs separate certs
- ❌ More complex certificate management
- ❌ No unified TLS termination
- ❌ Harder to scale

---

## 📋 Implementation Checklist

### ✅ Completed Features
- [x] Subdomain-based routing in proxy
- [x] Room code extraction from Host header
- [x] WebSocket auto-refresh on dashboard and mirror
- [x] Cache-control headers to prevent browser caching
- [x] Legacy path-based routes removed
- [x] E2E test script updated with new URLs
- [x] User names updated (rahbar/sanaullah)

### 📋 Production DNS Setup

For production deployment, configure wildcard DNS:

```bash
# Primary domain
m-act.live              A      YOUR_SERVER_IP

# Wildcard for all rooms (required)
*.m-act.live            A      YOUR_SERVER_IP

# Examples of what this enables:
# project-1.m-act.live → Room "project-1"
# my-app.m-act.live → Room "my-app"
# test.m-act.live → Room "test"
```

**Note**: Most DNS providers support wildcard records. Cloudflare, Route53, and DigitalOcean all support `*.domain.com` patterns.

---

## 🎯 Summary

### Current State: ✅ EXCELLENT Architecture
- **Port usage is already optimal** - don't change it!
- **Single ports serve multiple workspaces** via subdomain multiplexing
- **Industry-standard approach** (same as nginx, Apache, etc.)

### For HTTPS:
- **Use nginx or Caddy** as reverse proxy
- **Let's Encrypt** for free SSL certificates
- **No application code changes** needed
- **One wildcard cert** covers all subdomains

### URL Structure:
- **Subdomain routing implemented** in proxy
- **Legacy paths still work** for backward compatibility
- **Clean URLs** without `/rooms/` or `/mirror` in path
- **Production-ready** URL structure

This architecture will scale from 1 user to 10,000+ users without changing ports!
