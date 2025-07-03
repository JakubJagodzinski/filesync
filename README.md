# FileSync

A lightweight CLI tool for reliable one-way file synchronization over TCP, using dynamic UDP multicast discovery. Designed for network transparency, robustness, and simplicity.

---

## Overview

**FileSync** is a Python-based client-server application that enables automatic, reliable synchronization of files from a client archive directory to a server directory.

The system handles:
- dynamic server discovery (no hardcoded IPs),
- delta file sync (based on timestamps),
- disconnection tolerance and resume logic,
- single active session with queueing.

---

## Features

- **UDP multicast discovery** – client finds servers dynamically.
- **Unidirectional sync** – from client to server only.
- **Smart file detection** – only changed or new files are transferred.
- **Thread-safe queuing** – only one client syncs at a time.
- **Nested directory support** – full recursive sync of folders.
- **Resilient to disconnects** – clients automatically retry.

---

## Architecture

FileSync uses a **two-phase protocol**:

1. **Discovery Phase (UDP)**
   - Client broadcasts `DISCOVER` message to a multicast group.
   - Server responds with an `OFFER` message containing TCP port.

2. **Synchronization Phase (TCP)**
   - Client connects to server and exchanges sync metadata using JSON.
   - Server replies with `TASKS`, then receives files via binary stream.
   - Ends with `NEXT_SYNC` instruction.

---

## Prerequisites

To run this project, you need:

- Python **3.9+**
- `pip` package manager
- Supported OS: Linux / macOS / Windows with UDP multicast enabled

### Required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

### Server

```bash
python server.py
```

You'll be prompted to configure:
- TCP port
- Sync interval (seconds between syncs per client)

### Client

```bash
python client.py
```

You can provide:
- Optional Client ID (used to generate unique sync path)
- Optional manual server IP and port (to skip discovery)

The client continuously:
- discovers the server,
- connects and syncs,
- waits for the next scheduled sync.

---

## Message Protocol

All messages between client and server are JSON-based. Key types include:

- `DISCOVER` / `OFFER` – for discovery
- `CLIENT_FILES_INFO` / `TASKS` – sync planning
- `FILE_HEADER` – before file transfer
- `NEXT_SYNC` – indicates next scheduled sync

See full protocol documentation in [`documentation`](./documentation.pdf).

---

## License

This project is licensed under the MIT License.

---

## Author

Jakub Jagodziński
