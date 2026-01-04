# VNCSSDetector Development Continuation Guide

## Project Overview

VNCSSDetector is a system for detecting fake cell tower stations. It consists of:
- **vncssd-web** - Centralized web server (Python FastAPI + SvelteKit)
- **vncssdectector (daemon)** - Rust daemon running on detection nodes
- **vncssd_client** - Flutter mobile app for users

## Current Status (2026-01-04)

### ✅ Completed

#### Backend (vncssd-web/backend)
- FastAPI application structure
- MySQL database schema with tables: users, nodes, recordings, analysis_results, alerts, system_logs, audit_logs
- Authentication service using bcrypt (NOT passlib due to compatibility issues)
- JWT-based auth with access/refresh tokens
- API routers: auth, users, nodes, recordings, alerts, dashboard
- WebSocket handlers for real-time node communication

#### Frontend (vncssd-web/frontend)
- SvelteKit 2 + Tailwind CSS setup
- Login page with Vietnamese UI
- Dashboard with stats, alerts, node table
- API client with TypeScript types
- Auth store for state management

#### Deployment
- systemd service file
- Nginx configuration (HTTP-only dev version working)
- Install script for Ubuntu 24.04

#### WebSocket Endpoints (in main.py)
- `ws://server/ws/node?uuid=xxx&api_key=xxx` - Node connections
- `ws://server/ws/dashboard` - Dashboard real-time updates

### ⚠️ Needs Fixing

1. **Login Error Display** - Currently shows `[object Object]` instead of error message
   - Fixed in `frontend/src/lib/api.ts` - improved error parsing
   - Need to rebuild frontend and redeploy

2. **Dashboard Redirect After Login** - Not redirecting properly
   - Check `frontend/src/routes/login/+page.svelte` - uses `goto('/')`
   - May need to update `+layout.svelte` to handle auth state properly

3. **Branding Updates Needed**:
   - Changed `vncssd.local` to `vncssd.notrespond.com`
   - Changed year to 2026
   - Removed HUTECH University
   - Need to rebuild frontend

---

## Planned Features

### 1. Real-time Data Sync (Client ↔ Server)

**Server Side (vncssd-web)**:
```python
# WebSocket endpoint for dashboard clients
# Already exists at app/websocket/handlers.py
# Broadcasts to dashboard connections every 3 seconds:
# - Online nodes count
# - Offline nodes count
# - Active alerts
```

**Caching Strategy**:
- Persistent data (node ID, node info): Cache on client, update on change
- Dynamic data (node status, alerts): Real-time push via WebSocket

### 2. Node Management

**API Key Generation** - Already implemented:
- `POST /api/nodes` creates node and returns API key
- `POST /api/nodes/{id}/regenerate-key` regenerates API key

**Location Update**:
- `PUT /api/nodes/{id}` with `location_lat`, `location_lng`, `location_name`

### 3. Client Map View

**Requirements**:
- Show all nodes on map
- Green dot = online node
- Red dot = offline node
- Use `GET /api/dashboard/node-map` endpoint

### 4. Alert System

**Node → Server**:
- WebSocket message with alert data
- Server creates alert in database
- Broadcasts to dashboard clients

**Client Notifications**:
- When client is near an alerted node
- Show notification: "This place is not safe, beware of SMS fraud"
- Location-based using node GPS coordinates

---

## Daemon Running Modes (✅ IMPLEMENTED)

> All daemon running modes are fully implemented in the codebase.

### Mode Types

1. **Standalone** - Normal operation, independent device
2. **Node** - Connected to VNCSSD server + local standalone
3. **Swarm** - Node-only, web UI locked

### Implemented Files

| File | Description | Status |
|------|-------------|--------|
| `daemon/src/vncssd_client.rs` | WebSocket client | ✅ Done |
| `daemon/src/server.rs` | Mode API endpoints | ✅ Done |
| `daemon/src/config.rs` | RunningMode enum | ✅ Done |
| `daemon/web/src/lib/components/NodeModePanel.svelte` | Config UI | ✅ Done |
| `daemon/web/src/lib/components/ModeStatusBadge.svelte` | Status badge | ✅ Done |
| `daemon/web/src/lib/components/SwarmModeView.svelte` | Locked view | ✅ Done |

### API Endpoints (daemon)

```
GET  /api/mode          - Get running mode and connection status
POST /api/mode          - Set running mode
POST /api/node-config   - Set server IP and API key
POST /api/heuristic-test - Start heuristic test
```

### WebSocket Client Features

- Auto-reconnect on disconnection
- API key authentication
- Heartbeat every 30 seconds
- Alert forwarding to server
- Commands from server (TODO: implement handlers)

---

## File Structure Reference

```
vncssd-web/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry
│   │   ├── config.py               # Settings
│   │   ├── database.py             # SQLAlchemy setup
│   │   ├── models/                 # ORM models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Business logic
│   │   │   └── auth_service.py     # Uses bcrypt directly!
│   │   ├── routers/                # API endpoints
│   │   └── websocket/              # WebSocket handlers
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   ├── stores/auth.ts      # Auth state
│   │   │   └── components/         # UI components
│   │   └── routes/                 # Pages
│   └── package.json
├── database/
│   └── schema.sql                   # MySQL schema
└── deploy/
    ├── install.sh                   # Ubuntu installer
    ├── nginx-dev.conf               # HTTP config
    └── vncssd-web.service           # systemd

vncssdectector/
├── daemon/
│   ├── src/
│   │   ├── main.rs
│   │   ├── config.rs               # Add RunningMode
│   │   ├── server.rs               # API endpoints
│   │   └── ws_client.rs            # NEW: WebSocket client
│   └── web/
│       └── src/
│           ├── lib/
│           │   └── components/
│           │       ├── NodeModePanel.svelte    # Mode config
│           │       └── ModeStatusBadge.svelte  # Status display
│           └── routes/
│               └── +page.svelte
└── lib/
    └── src/
        └── analysis/analyzer.rs     # Detection logic
```

---

## Key Technical Notes

### Password Hashing
**DO NOT USE passlib** - Compatibility issues with bcrypt 4.x
Use bcrypt directly:
```python
import bcrypt
bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
bcrypt.checkpw(password.encode(), hash.encode())
```

### SQLAlchemy Enum
Use `values_callable` for enums stored as lowercase values:
```python
Enum(UserRole, values_callable=lambda x: [e.value for e in x])
```

### Email Validation
Pydantic's EmailStr rejects `.local` domains. Use real domains like `notrespond.com`.

### Default Credentials
- Email: `admin@vncssd.notrespond.com`
- Password: `admin123`

---

## Next Steps Priority

1. [ ] Fix login error display (rebuild frontend)
2. [ ] Fix dashboard redirect after login
3. [ ] Add daemon running modes (Standalone/Node/Swarm)
4. [ ] Implement Rust WebSocket client in daemon
5. [ ] Add connection state UI to daemon web
6. [ ] Implement alert forwarding from node to server
7. [ ] Add Flutter client map view with node markers
8. [ ] Add client location-based notifications
9. [ ] Test heuristic pass/fail for Swarm mode

---

## Commands Reference

**Ubuntu Server**:
```bash
# Restart backend
sudo systemctl restart vncssd-web

# View logs
sudo journalctl -u vncssd-web -f

# Test login
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@vncssd.notrespond.com", "password": "admin123"}'

# Rebuild frontend
cd ~/VNCSSDetector/vncssd-web/frontend
npm run build
sudo cp -r build/* /opt/vncssd-web/frontend/
```

**API Docs**: http://localhost:8000/docs
