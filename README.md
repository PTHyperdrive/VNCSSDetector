# VNCSSD System

> VNCSSDetector Management Server + Flutter Mobile Client

## Overview

This repository contains a complete system for managing VNCSSDetector agents across multiple nodes:

- **vncssd-server**: NestJS backend server (TypeScript)
- **vncssd_client**: Flutter mobile app (Dart)

## Quick Start

### Server (Docker)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f server
```

### Flutter App

```bash
cd vncssd_client
flutter pub get
flutter run
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Flutter App   │────▶│  VNCSSD-Server   │◀────│ VNCSSDetector   │
│  (REST + FCM)   │     │  (REST + WS)     │     │   (WebSocket)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │    │
                    ┌─────────┴────┴─────────┐
                    │         │              │
                    ▼         ▼              ▼
               PostgreSQL   Redis         Firebase
```

## Documentation

See the `implementation_plan.md` for detailed:
- Database schema
- REST API specification
- WebSocket protocol
- Security checklist

## License

MIT
