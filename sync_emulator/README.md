Phone–PC Sync Emulator

Overview

Emulates syncing phone data (contacts, messages, files, notifications) to a PC 
backend. Includes:

- FastAPI backend with SQLite
- WebSocket echo channel (`/ws`)
- Sync endpoints (`/sync/*`) with basic last-write-wins upserts
- Query endpoints (`/query/*`) for dashboard use
- Minimal web dashboard (`/`) to view devices and data
- CLI phone simulator to generate sample data

Quick start

1) Install dependencies
   pip install --user --break-system-packages -r requirements.txt

2) Run the server (from project root)
   PYTHONPATH=. uvicorn sync_emulator.app.main:app --host 127.0.0.1 --port 8000 --reload

3) Open the dashboard
   http://127.0.0.1:8000/

4) Simulate a phone sync
   python3 -m sync_emulator.cli

API

- Health: GET /health/
- Register device: POST /sync/device
  Body: { "device_id": "abc", "name": "MyPhone" }
- Upsert contacts: POST /sync/{device_id}/contacts:upsert
- Upsert messages: POST /sync/{device_id}/messages:upsert
- Upsert files: POST /sync/{device_id}/files:upsert
- Create notification: POST /sync/{device_id}/notifications

- List devices: GET /query/devices
- List contacts: GET /query/{device_id}/contacts
- List messages: GET /query/{device_id}/messages
- List files: GET /query/{device_id}/files
- List notifications: GET /query/{device_id}/notifications

Notes

- Conflict handling uses `updated_at` to perform last-write-wins merges.
- SQLite DB lives at `sync_emulator/app/data.sqlite3` and is auto-created.
