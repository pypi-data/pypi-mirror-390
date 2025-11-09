# FRP Tunnel Automation in MACT

## Overview

MACT automatically sets up FRP tunnels when developers create or join rooms using the CLI. **No manual configuration needed!**

## How It Works

### Architecture

1. **CLI Commands** (`mact create` / `mact join`) automatically:
   - Create/join room via backend API
   - Install git post-commit hook
   - Start FRP tunnel (frpc client)

2. **FrpcManager** (`cli/frpc_manager.py`):
   - Finds frpc binary (vendored in `third_party/frp/`)
   - Generates TOML config for each developer
   - Starts frpc subprocess
   - Manages tunnel lifecycle

3. **Tunnel Mapping**:
   - Developer's `localhost:PORT` → `subdomain.localhost:7101`
   - Example: `localhost:3000` → `dev-alice-demo.localhost:7101`

4. **Mirror Endpoint**:
   - Proxy queries backend for active developer
   - Fetches content from active developer's tunnel
   - Returns proxied content (no redirects!)

## Code Flow

### When User Runs: `mact create --project demo --local-port 3000`

```python
# cli/cli.py lines 100-130
def create_command():
    # 1. Create room via backend API
    response = requests.post(f"{backend_url}/rooms/create", json=payload)
    
    # 2. Install git hook
    install_post_commit(room_code, developer_id, backend_url)
    
    # 3. Start FRP tunnel
    frpc = FrpcManager()
    tunnel = TunnelConfig(
        room_code=room_code,
        developer_id=developer_id,
        local_port=local_port,
        remote_subdomain=subdomain,
        server_addr="127.0.0.1",
        server_port=7100
    )
    frpc.start_tunnel(tunnel)  # ← Automatic!
```

### FrpcManager Implementation

```python
# cli/frpc_manager.py
class FrpcManager:
    def start_tunnel(self, tunnel: TunnelConfig) -> bool:
        # 1. Generate frpc TOML config
        config = self._generate_config(tunnel)
        
        # 2. Write to temp file
        config_file = Path(tempfile.mkdtemp()) / f"frpc_{tunnel.room_code}.toml"
        config_file.write_text(config)
        
        # 3. Start frpc subprocess
        proc = subprocess.Popen(
            [self.frpc_binary, "-c", str(config_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._processes[key] = proc
        return True
```

## Testing

### End-to-End Test with Real Tunnels

Use the new test script that exercises the ACTUAL CLI commands:

```bash
./scripts/e2e_with_tunnels.sh
```

This test:
- ✅ Uses real `mact create` and `mact join` commands
- ✅ Automatically starts FRP tunnels via FrpcManager
- ✅ Verifies git hooks are installed
- ✅ Tests commit-triggered active developer switching
- ✅ Confirms mirror endpoint proxies to active developer's tunnel

### What Gets Automated

| Action | Git Hook | FRP Tunnel | Backend Registration |
|--------|----------|------------|---------------------|
| `mact create` | ✅ Auto-installed | ✅ Auto-started | ✅ Room created |
| `mact join` | ✅ Auto-installed | ✅ Auto-started | ✅ Developer joined |
| `git commit` | ✅ Auto-reports | - | ✅ Active dev updated |

## Verifying Tunnels

### Check if frpc is running:

```bash
ps aux | grep frpc
# Should show: frpc -c /tmp/.../frpc_mact-demo-e2e.toml
```

### Test tunnel directly:

```bash
# User1's tunnel
curl http://dev-alice-demo.localhost:7101

# User2's tunnel  
curl http://dev-bob-demo.localhost:7101

# Mirror (proxies to active developer)
curl http://localhost:9000/rooms/mact-demo-e2e/mirror
```

### Check FRP server logs:

```bash
# Should show proxy registrations
tail -f /tmp/mact_frps.log
# Look for: [dev-alice-demo] registered
```

## Configuration

### Default Settings

| Setting | Value | Location |
|---------|-------|----------|
| FRP Server | 127.0.0.1:7100 | `cli/cli.py` |
| FRP Vhost Port | 7101 | `third_party/frp/mact.frps.toml` |
| frpc Binary | `third_party/frp/frpc` | `cli/frpc_manager.py` |

### Override Options

```bash
# Custom FRP server
mact create --project demo --local-port 3000 \
  --frp-server "frp.example.com" \
  --frp-port 7000

# Custom backend
mact create --project demo --local-port 3000 \
  --backend "https://backend.m-act.live"
```

## Troubleshooting

### Tunnel not working?

1. **Check if frpc binary exists:**
   ```bash
   ls -lh third_party/frp/frpc
   # Should be executable
   ```

2. **Check if frps is running:**
   ```bash
   ps aux | grep frps
   # Should show frps process on port 7100
   ```

3. **Check frpc logs:**
   ```bash
   # FrpcManager redirects to DEVNULL by default
   # For debugging, modify cli/frpc_manager.py:
   # stdout=subprocess.DEVNULL → stdout=subprocess.PIPE
   ```

4. **Test FrpcManager directly:**
   ```bash
   cd /home/int33k/Desktop/M-ACT
   source .venv/bin/activate
   python3 << EOF
   from cli.frpc_manager import FrpcManager, TunnelConfig
   
   fm = FrpcManager()
   print(f"frpc binary: {fm.frpc_binary}")
   
   tunnel = TunnelConfig(
       room_code="test",
       developer_id="alice",
       local_port=3000,
       remote_subdomain="test-alice",
       server_addr="127.0.0.1",
       server_port=7100
   )
   
   if fm.start_tunnel(tunnel):
       print("✓ Tunnel started!")
   else:
       print("✗ Tunnel failed!")
   EOF
   ```

### Mirror returns 404?

1. **Verify active developer is set:**
   ```bash
   curl "http://localhost:5000/get-active-url?room=mact-demo-e2e"
   # Should return: {"active_url": "http://dev-alice-demo.localhost:7101"}
   ```

2. **Check if tunnel is reachable:**
   ```bash
   curl "http://dev-alice-demo.localhost:7101"
   # Should show user's localhost content
   ```

3. **Verify proxy routing logic:**
   ```bash
   # Check proxy logs
   tail -f /tmp/mact_proxy.log
   ```

## Implementation Details

### Generated frpc Config

For each developer, FrpcManager generates:

```toml
# /tmp/.../frpc_mact-demo-e2e.toml
serverAddr = "127.0.0.1"
serverPort = 7100

[[proxies]]
name = "mact-demo-e2e-alice"
type = "http"
localIP = "127.0.0.1"
localPort = 3000
subdomain = "dev-alice-demo"
```

### Process Management

- Each tunnel runs as a separate subprocess
- Stored in `FrpcManager._processes` dict
- Cleanup handled by `stop_tunnel()` or `stop_all()`
- Config files stored in temp directories

### Security Considerations

- **PoC Stage**: No authentication on tunnels
- **Unit 5 (Production)**: Will add:
  - TLS for tunnels
  - Token-based tunnel authentication  
  - Rate limiting
  - Network isolation

## Next Steps

- [x] Implement FrpcManager (DONE)
- [x] Integrate with CLI commands (DONE)
- [x] Auto-install git hooks (DONE)
- [x] Create E2E test with real tunnels (DONE)
- [ ] Add tunnel health monitoring
- [ ] Implement automatic reconnection
- [ ] Add tunnel metrics/logging
- [ ] Production deployment (Unit 5)

## Summary

**Zero Manual Configuration Required!**

```bash
# Developer workflow (EVERYTHING automatic):
mact init --name alice
mact create --project demo --local-port 3000
# ✓ Room created
# ✓ Git hook installed
# ✓ FRP tunnel started
# → Ready to code!

# Collaborator joins:
mact init --name bob
mact join --room demo --local-port 3001
# ✓ Joined room
# ✓ Git hook installed  
# ✓ FRP tunnel started
# → Ready to collaborate!

# Magic happens:
git commit -m "my changes"
# ✓ Hook auto-reports commit
# ✓ Backend updates active developer
# ✓ Mirror switches to your tunnel
# → http://demo.m-act.live now shows YOUR localhost!
```
