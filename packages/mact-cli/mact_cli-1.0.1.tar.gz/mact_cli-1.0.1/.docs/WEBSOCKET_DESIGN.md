# WebSocket/HTTP Upgrade Bridge - Design Document
**Date**: 2025-11-06  
**Status**: Design Phase  
**Priority**: Medium (deferred from Unit 2)

---

## 1. Problem Statement

### Current Limitation
The MACT proxy currently **rejects WebSocket/HTTP Upgrade requests** with a 501 status:

```python
if request.headers.get('Upgrade', '').lower() == 'websocket':
    return jsonify({"error": "WebSocket not yet supported"}), 501
```

### Impact
- Modern dev servers with live-reload (HMR) fail to connect
- WebSocket-based applications cannot be previewed
- Limits developer experience for real-time applications

### Use Cases Blocked
1. Vite/Webpack HMR (Hot Module Replacement)
2. Next.js Fast Refresh
3. WebSocket APIs (Socket.IO, native WebSocket)
4. Server-Sent Events over upgraded connections

---

## 2. Solution Approach

### Option A: Full ASGI Migration (Recommended)
Migrate from Flask (WSGI) to **Starlette/FastAPI** (ASGI).

**Pros:**
- ✅ Native WebSocket support
- ✅ Async/await for better performance
- ✅ HTTP/2 support potential
- ✅ Modern Python async ecosystem
- ✅ Well-tested ASGI servers (uvicorn, hypercorn)

**Cons:**
- ❌ Requires rewriting proxy/app.py (~400 lines)
- ❌ Test suite needs ASGI test client
- ❌ Breaking change (different server)
- ❌ ~2-3 days work

### Option B: WebSocket Bridge (Not Recommended)
Keep Flask WSGI, add separate WebSocket forwarder.

**Pros:**
- ✅ Minimal changes to existing code
- ✅ Keeps Flask familiar

**Cons:**
- ❌ Requires dual-server setup (Flask + WS bridge)
- ❌ Complex port management
- ❌ No standard libraries (custom TCP/WebSocket code)
- ❌ Hard to maintain

### **Decision: Option A (ASGI Migration)**

---

## 3. Migration Strategy

### Phase 1: Preparation
1. **Audit dependencies**
   - Replace `Flask` with `Starlette` or `FastAPI`
   - Replace `requests` with `httpx` (async HTTP client)
   - Add `uvicorn[standard]` as ASGI server
   - Add `websockets` library

2. **Create feature branch**
   ```bash
   git checkout -b feature/asgi-migration
   ```

3. **Backup current proxy**
   ```bash
   cp proxy/app.py proxy/app.py.flask-backup
   ```

### Phase 2: Implementation
1. **Rewrite proxy/app.py with Starlette**
   - Convert routes to Starlette path operations
   - Replace `@app.route` with `@app.route` (Starlette syntax)
   - Migrate middleware
   - Convert streaming responses to Starlette `StreamingResponse`

2. **Add WebSocket mirror endpoint**
   - New route: `/rooms/{room_code}/ws`
   - WebSocket handshake
   - Bidirectional forwarding (client ↔ active dev tunnel)
   - Error handling for disconnects

3. **Update HTTP mirror endpoint**
   - Use `httpx.AsyncClient` instead of `requests`
   - Maintain streaming behavior
   - Preserve all current features

4. **Update dashboard endpoint**
   - Migrate HTML rendering to Starlette templates
   - Maintain all current features

### Phase 3: Testing
1. **Refactor test suite**
   - Use `from starlette.testclient import TestClient`
   - Update all 8 proxy tests
   - Verify integration tests still pass

2. **Add WebSocket tests**
   ```python
   def test_websocket_mirror_forwards_messages():
       # Test WebSocket connection and message forwarding
   
   def test_websocket_mirror_handles_close():
       # Test graceful disconnect
   
   def test_websocket_mirror_no_active_dev():
       # Test WebSocket when no active developer
   ```

3. **Manual testing**
   - Test with Vite dev server HMR
   - Test with Next.js Fast Refresh
   - Test with Socket.IO app

### Phase 4: Documentation
1. Update `proxy/README.md` with WebSocket support
2. Add WebSocket usage examples
3. Update `PROJECT_CONTEXT.md`
4. Update main `README.md`

---

## 4. Technical Design

### Starlette Proxy Architecture

```python
from starlette.applications import Starlette
from starlette.responses import StreamingResponse, HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket
import httpx

app = Starlette(debug=True, routes=[
    Route('/rooms/{room_code}/mirror', mirror_http),
    Route('/rooms/{room_code}/mirror/{path:path}', mirror_http),
    Route('/rooms/{room_code}/dashboard', dashboard),
    WebSocketRoute('/rooms/{room_code}/ws', websocket_mirror),
    Route('/health', health),
])

async def mirror_http(request):
    """HTTP mirror with streaming"""
    room_code = request.path_params['room_code']
    active_url = await get_active_url_async(room_code)
    
    async with httpx.AsyncClient() as client:
        async with client.stream(
            method=request.method,
            url=f"{active_url}{request.url.path}",
            headers=forward_headers(request.headers),
        ) as response:
            return StreamingResponse(
                response.aiter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )

async def websocket_mirror(websocket: WebSocket):
    """WebSocket mirror endpoint"""
    await websocket.accept()
    room_code = websocket.path_params['room_code']
    
    try:
        active_url = await get_active_url_async(room_code)
        ws_url = active_url.replace('http://', 'ws://').replace('https://', 'wss://')
        
        async with websockets.connect(f"{ws_url}/ws") as upstream_ws:
            # Bidirectional forwarding
            await forward_websocket(websocket, upstream_ws)
    
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
```

### WebSocket Forwarding Logic

```python
async def forward_websocket(client_ws: WebSocket, upstream_ws):
    """Forward messages bidirectionally"""
    async def forward_client_to_upstream():
        async for message in client_ws.iter_text():
            await upstream_ws.send(message)
    
    async def forward_upstream_to_client():
        async for message in upstream_ws:
            await client_ws.send_text(message)
    
    # Run both directions concurrently
    await asyncio.gather(
        forward_client_to_upstream(),
        forward_upstream_to_client(),
        return_exceptions=True
    )
```

---

## 5. Migration Checklist

### Code Changes
- [ ] Install Starlette, uvicorn, httpx, websockets
- [ ] Rewrite proxy/app.py with Starlette
- [ ] Add WebSocket mirror endpoint
- [ ] Convert HTTP mirror to async with httpx
- [ ] Migrate dashboard rendering
- [ ] Update FrpsManager integration
- [ ] Update FrpSupervisor integration

### Testing
- [ ] Update tests/test_proxy.py for ASGI
- [ ] Add WebSocket-specific tests (3+ tests)
- [ ] Verify 8 existing tests still pass
- [ ] Update integration tests
- [ ] Manual testing with live dev servers

### Documentation
- [ ] Update proxy/README.md
- [ ] Update PROJECT_CONTEXT.md
- [ ] Update main README.md
- [ ] Add WebSocket examples
- [ ] Document migration process

### Deployment
- [ ] Update systemd service (if created)
- [ ] Update nginx config for WebSocket (upgrade headers)
- [ ] Test production deployment

---

## 6. Breaking Changes

### Server Command
**Before (Flask):**
```bash
python proxy/app.py
```

**After (Starlette/uvicorn):**
```bash
uvicorn proxy.app:app --host 0.0.0.0 --port 9000
```

### Environment Variables
- Same: `BACKEND_BASE_URL`, `PROXY_PORT`, `FRPS_BIN`, `FRPS_CONFIG`
- New: None (backward compatible)

### API Contract
- All HTTP endpoints remain the same
- New: `/rooms/{room_code}/ws` for WebSocket connections
- No breaking changes to existing clients

---

## 7. Testing Strategy

### Unit Tests (tests/test_proxy.py)
```python
from starlette.testclient import TestClient
from proxy.app import app

client = TestClient(app)

def test_mirror_http_success():
    # Existing test, updated for ASGI client
    pass

def test_websocket_mirror_connection():
    with client.websocket_connect("/rooms/myapp/ws") as websocket:
        websocket.send_text("hello")
        data = websocket.receive_text()
        assert data == "hello"
```

### Integration Tests
- Backend + ASGI Proxy with WebSocket
- Test HMR scenario
- Test Socket.IO scenario

### Manual Testing Scenarios
1. **Vite Dev Server**
   ```bash
   # Terminal 1: Start Vite app on 3000
   npm run dev
   
   # Terminal 2: Create room and tunnel
   mact create --project vite-app --subdomain http://dev-rahbar.m-act.live
   
   # Browser: Connect to myapp.m-act.live
   # Verify: HMR works when editing files
   ```

2. **Socket.IO App**
   - Test real-time messaging
   - Test reconnection logic
   - Test multiple clients

---

## 8. Rollback Plan

If ASGI migration fails:

1. **Restore Flask version**
   ```bash
   git checkout proxy/app.py.flask-backup
   cp proxy/app.py.flask-backup proxy/app.py
   ```

2. **Restore dependencies**
   ```bash
   pip uninstall starlette uvicorn httpx websockets
   pip install flask requests
   ```

3. **Restore tests**
   ```bash
   git checkout tests/test_proxy.py
   ```

4. **Continue with 501 for WebSocket**
   - Document limitation clearly
   - Advise developers to use HTTP-only for PoC

---

## 9. Timeline Estimate

| Phase | Tasks | Time |
|-------|-------|------|
| Design | This document | ✅ Complete |
| Setup | Dependencies, branch | 1 hour |
| Implementation | Rewrite proxy, add WebSocket | 1 day |
| Testing | Unit + integration tests | 4 hours |
| Documentation | Update all docs | 2 hours |
| Manual Testing | Live dev servers | 2 hours |
| **Total** | | **~2 days** |

---

## 10. Success Criteria

- [ ] All 8 existing proxy tests pass with ASGI
- [ ] 3+ new WebSocket tests pass
- [ ] Integration tests pass
- [ ] Manual test: Vite HMR works through proxy
- [ ] Manual test: Socket.IO app works through proxy
- [ ] Documentation updated
- [ ] No regressions in HTTP mirroring
- [ ] Performance equal or better than Flask

---

## 11. Alternative: Defer WebSocket

If WebSocket is not critical for PoC:

**Option**: Keep Flask, document limitation, proceed to production deployment.

**Rationale**:
- Most PoC demos work fine without WebSocket
- Can add later if needed
- Focus on core functionality first

**Decision**: Implement ASGI migration (2-3 days) or defer to post-PoC.

---

## 12. Next Steps

**If proceeding with ASGI migration:**
1. Create feature branch
2. Install dependencies
3. Start proxy rewrite
4. Implement WebSocket endpoint
5. Update tests
6. Manual validation
7. Merge to main

**If deferring:**
1. Document limitation in README
2. Proceed to production deployment
3. Revisit after PoC validation

---

**Recommendation**: Defer WebSocket to post-PoC. Focus on deployment and security first, then add WebSocket once core platform is validated in production.
