# VNCSSD System - AI Continuation Document

> **Last Updated:** 2026-01-02 00:19:00 UTC+7
> **Last AI Session:** Implementing VNCSSDetector Running Modes & WebSocket Client

---

## 🎯 Project Overview

**VNCSSD (Viet Nam Cell Site Simulation Detector)** is a system for detecting IMSI-catchers (fake cell towers used for SMS fraud). The project consists of:

| Component | Technology | Path |
|-----------|------------|------|
| **vncssd-server** | NestJS + TypeScript + Prisma | `vncssd-server/` |
| **vncssd_client** | Flutter + Riverpod | `vncssd_client/` |
| **vncssdectector** | Rust daemon + Svelte web UI | `vncssdectector/` |

---

## 📋 Current Implementation Status

### ✅ Completed

#### Server (vncssd-server)
- [x] User authentication (JWT)
- [x] Workspace management
- [x] Node CRUD operations
- [x] Events & notifications system
- [x] FCM push notifications
- [x] **API key generation** (`/api/api-keys`)
- [x] **Node location fields** (latitude, longitude, locationName)
- [x] **Real-time WebSocket** (`/client` namespace, 3s updates)
- [x] **ALERT handler** in NodesGateway for IMSI-catcher detection
- [x] **AlertsService** with proximity-based notifications (Haversine formula)

#### Flutter Client (vncssd_client)
- [x] Authentication flow
- [x] Dashboard with node stats
- [x] Node list & detail screens
- [x] Events screen
- [x] Notifications screen
- [x] **flutter_map integration** with node markers
- [x] **Real-time service** (socket.io client)
- [ ] Client-side caching (Hive) - dependencies added, not implemented
- [ ] Safety warning when in threat proximity

#### VNCSSDetector (vncssdectector)
- [x] IMSI-catcher detection (core library)
- [x] Web daemon with Svelte UI
- [x] **RunningMode enum** (Standalone/Node/Swarm)
- [x] **Config fields**: running_mode, server_ip, api_key
- [x] **Mode API endpoints**: GET/POST /api/mode, POST /api/node-config
- [x] **NodeModePanel.svelte** - API key + Server IP modal
- [x] **ModeStatusBadge.svelte** - connection status badge
- [x] **SwarmModeView.svelte** - locked minimal UI
- [x] **SystemStatsTable updated** with "Chế độ" row
- [x] **vncssd_client.rs** - WebSocket client module (created, not integrated)

### 🚧 Remaining Work

1. **Integrate vncssd_client.rs into main.rs**
   - Add `mod vncssd_client;` to main.rs
   - Add `connection_state` to ServerState initialization
   - Start WebSocket client when in Node/Swarm mode
   - Forward alerts from analysis to WebSocket client

2. **Heuristic Test Integration**
   - When `test_heuristic: true` in config and warning generated → mark `is_heuristic_passed = true`
   - Update SwarmModeView to show passed status

3. **Add mode API routes to Axum router**
   - GET/POST `/api/mode`
   - POST `/api/node-config`
   - POST `/api/heuristic-test`

4. **Flutter client threat warnings**
   - Show alert when in proximity of IMSI-catcher node
   - Threat markers on map

---

## 🔧 Key Code Locations

### VNCSSDetector Daemon
```
vncssdectector/daemon/
├── Cargo.toml          # Dependencies (added tokio-tungstenite, url)
├── src/
│   ├── main.rs         # Entry point, needs vncssd_client integration
│   ├── config.rs       # RunningMode, ConnectionStatus, NodeConnectionState
│   ├── server.rs       # Axum handlers + mode endpoints (added but not routed)
│   ├── vncssd_client.rs # WebSocket client (NEW - needs integration)
│   └── analysis.rs     # Where to hook alert forwarding
└── web/src/
    ├── routes/+page.svelte              # Main page with mode support
    └── lib/components/
        ├── NodeModePanel.svelte         # API key/Server IP modal
        ├── ModeStatusBadge.svelte       # Status badge
        ├── SwarmModeView.svelte         # Locked Swarm UI
        └── SystemStatsTable.svelte      # Mode row added
```

### VNCSSD Server
```
vncssd-server/src/
├── app.module.ts           # AlertsModule added
├── alerts/                 # IMSI-catcher alert handling
│   ├── alerts.service.ts   # Proximity notifications
│   └── alerts.controller.ts
├── realtime/              # Client WebSocket updates
│   └── client.gateway.ts  # 3s interval updates
├── nodes/
│   ├── nodes.gateway.ts   # ALERT handler added
│   └── nodes.service.ts   # updateLocation method
└── api-keys/              # API key generation
```

---

## 🔗 Integration Points

### 1. main.rs Integration (TODO)
```rust
// Add to main.rs imports:
mod vncssd_client;
use crate::vncssd_client::start_vncssd_client;
use crate::config::NodeConnectionState;

// In run_with_config(), before creating ServerState:
let connection_state = Arc::new(RwLock::new(NodeConnectionState::default()));

// Start WebSocket client if in Node/Swarm mode:
let _alert_sender = start_vncssd_client(
    config.running_mode.clone(),
    config.server_ip.clone(),
    config.api_key.clone(),
    connection_state.clone(),
).await;

// Add connection_state to ServerState
let state = Arc::new(ServerState {
    // ... existing fields
    connection_state,
});
```

### 2. Router Integration (TODO)
```rust
// Add to get_router() in main.rs:
.route("/api/mode", get(server::get_mode))
.route("/api/mode", post(server::set_mode))
.route("/api/node-config", post(server::set_node_config))
.route("/api/heuristic-test", post(server::start_heuristic_test))
```

### 3. Alert Forwarding (TODO)
In `diag.rs` or `analysis.rs`, when IMSI-catcher warning is generated:
```rust
// Send alert via WebSocket client
if let Some(sender) = alert_sender.as_ref() {
    let _ = sender.send(AlertData {
        alert_type: "IMSI_CATCHER_DETECTED".to_string(),
        alert_message: warning_message,
        data: serde_json::json!({ /* detection data */ }),
    }).await;
}
```

---

## 🧪 Testing Commands

### Server
```bash
cd vncssd-server
npm install
npx prisma generate
npx prisma migrate dev --name add_location_apikey
npm run start:dev
```

### VNCSSDetector Web Build
```bash
cd vncssdectector/daemon/web
npm install
npm run build
```

### VNCSSDetector Daemon Build
```bash
cd vncssdectector
# Cross-compile for ARM (Orbic device)
cargo build --target aarch64-unknown-linux-musl --profile firmware-devel
```

### Flutter Client
```bash
cd vncssd_client
flutter pub get
flutter run
```

---

## 📊 Data Flow

```
VNCSSDetector (Rust)    →    VNCSSD Server (NestJS)    →    Flutter Client
        ↓                           ↓                            ↓
 Detects IMSI-catcher       Stores event, calculates       Shows warning if
 → Sends ALERT via WS       proximity, sends FCM push       user is nearby
```

---

## ⚠️ Known Issues

1. **Server lint errors**: Run `npm install` and `npx prisma generate` to resolve
2. **Svelte a11y warnings**: NodeModePanel.svelte has accessibility warnings
3. **Flutter unused import warnings**: realtime_service.dart has unused imports
4. **rootshell Unix errors**: Windows-specific, ignore for cross-compilation

---

## 📝 Configuration Example

### VNCSSDetector config.toml
```toml
qmdl_store_path = "/data/vncssdetector/qmdl"
port = 8080
debug_mode = false
device = "Orbic"

# Running mode: standalone, node, or swarm
running_mode = "node"
server_ip = "192.168.1.100:3000"
api_key = "vnc_xxxxxxxxxxxxxxxx"

[analyzers]
enable_lte_analysis = true
```

---

## 🎓 Next AI Instructions

1. **Integrate vncssd_client module into main.rs**
2. **Add mode routes to Axum router**
3. **Connect alert generation to WebSocket client**
4. **Implement heuristic test pass logic** (set `is_heuristic_passed = true` when warning generated)
5. **Build and test on target device**

Good luck! 🐳
