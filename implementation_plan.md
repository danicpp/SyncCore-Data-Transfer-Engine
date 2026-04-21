# Implementation Plan - High-Performance Data Sync Engine

Build a cross-platform data synchronization system for high-speed file transfer between Android (Mobile) and PC, using a "Hot-Buffer" architecture for reliability and atomic transfers.

## User Review Required

> [!IMPORTANT]
> **Networking Mode**: I will implement a dual-mode communication strategy:
> 1. **WebRTC**: For peer-discovery and NAT traversal if devices are on different subnets.
> 2. **Raw TCP Sockets**: For maximum local (USB/Wi-Fi 6) throughput if devices can reach each other directly.
> Please confirm if you prefer one over the other for the primary data path.

> [!WARNING]
> **ADB Permissions**: The "Agent-led troubleshooting terminal" will require `adb` to be available on the system path. I will provide a fallback guide if it's missing.

> [!NOTE]
> **Database**: I will use **PostgreSQL** running in a Docker container as the 'Hot-Buffer' to ensure high-performance chunk storage and atomicity during resume operations.

## Proposed Changes

The project will be split into two main components: `backend` (Python) and `frontend` (Svelte 5).

### 1. Backend (Python/FastAPI)

#### [NEW] [main.py](file:///d:/My%20Projects/Data%20Transfer%20APP/backend/main.py)
The FastAPI entry point. It will handle the control plane, management of the Transfer Manifest, and the troubleshooting terminal API.

#### [NEW] [streamer.py](file:///d:/My%20Projects/Data%20Transfer%20APP/backend/streamer.py)
A high-performance `asyncio` TCP server that handles raw byte streams.
- **Chunking**: Splits incoming data into optimal 4MB-16MB chunks.
- **Parallel Hashing**: Uses `concurrent.futures.ProcessPoolExecutor` to offload SHA-256 calculations to avoid GIL bottlenecks.

#### [NEW] [db.py](file:///d:/My%20Projects/Data%20Transfer%20APP/backend/db.py)
PostgreSQL schema using `SQLAlchemy` or `Tortoise-ORM` (async).
- **Table `chunks`**: Stores `offset`, `size`, `hash`, and `buffer_data`.
- **Table `transfers`**: Stores the 'Manifest Map' and current progress.

#### [NEW] [docker-compose.yml](file:///d:/My%20Projects/Data%20Transfer%20APP/backend/docker-compose.yml)
Configuration for the PostgreSQL instance.

---

### 2. Frontend (Svelte 5 + Capacitor)

#### [NEW] [frontend/](file:///d:/My%20Projects/Data%20Transfer%20APP/frontend/)
Initialized with Svelte 5 (Runes).
- **Real-time Dashboard**: Svelte 5 runes for low-latency UI updates of throughput and health.
- **Terminal Emulator**: A component to show ADB logs and agent-led troubleshooting.

#### [NEW] [transfer-engine.ts](file:///d:/My%20Projects/Data%20Transfer%20APP/frontend/src/lib/transfer-engine.ts)
Logic for the mobile device to scan the filesystem, generate the 'Manifest Map' (hashes), and stream data over TCP/WebRTC.

---

### 3. Transfer Logic

- **Manifest Map**: Pre-calculated SHA-256 hashes for all files in the source directory.
- **Checkpoint & Resume**: Before sending a chunk, the sender checks the Manifest Map. The receiver (PC) acknowledges chunk hashes before committing to the final file location.
- **USB 3.0 Optimization**: If connected via USB, we can use `adb reverse` to bridge the TCP connection for maximum wire-speed.

## Open Questions

1. **Which specific Android directories should be the default source?** (e.g., DCIM, Downloads, or a custom picker?)
2. **PostgreSQL vs SQLite?** SQLite is easier to set up without Docker, but PostgreSQL (as requested) is better for high-concurrency buffers. Should I proceed with Docker + PostgreSQL?
3. **Multi-device?** Do you need to sync from multiple Android devices simultaneously to one PC?

## Verification Plan

### Automated Tests
- `pytest` for the backend streaming logic (mocking socket connections).
- Integration tests for SHA-256 hash matching between sender and receiver.

### Manual Verification
- Deploying to a real Android device via Capacitor.
- Testing a transfer, killing the app mid-way, and verifying the **Resume** logic works without re-downloading existing chunks.
- Monitoring throughput via the Svelte 5 dashboard to ensure it hits > 1Gbps on Wi-Fi 6 / USB 3.0.
