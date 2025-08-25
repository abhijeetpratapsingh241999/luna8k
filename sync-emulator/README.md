PC Sync Emulator
================

Components
----------
- PC Sync Hub (FastAPI + SQLite) in `server/`
- Phone Emulator (Python) in `client/`
- Shared helpers in `shared/`

Setup
-----
1) Create venv and install deps (done already):
   - `. .venv/bin/activate`
2) Start the server:
   - `python server/run_server.py`
3) Visit web status: `http://127.0.0.1:8000/`
4) Get API key for emulator: `curl http://127.0.0.1:8000/health/key`

Run Emulator
------------
1) In another shell: `. .venv/bin/activate`
2) Optionally set sync directory: `export EMULATOR_SYNC_DIR=$PWD/emu_files`
3) Run: `python client/emulator.py`

Features
--------
- Device registration: `POST /devices/register`
- Heartbeat WebSocket: `GET /ws/heartbeat?device_id=...&api_key=...`
- File sync:
  - Preflight: `POST /files/preflight`
  - Upload: `POST /files/put` (multipart)
  - List metadata: `GET /files/meta/{device_id}`
- Contacts: `POST /contacts/bulk`, `GET /contacts/{device_id}`
- Messages: `POST /messages/bulk`, `GET /messages/{device_id}`

Notes
-----
- This is an emulator demo; API key is exposed via `/health/key` for ease of use.
- Conflict policy: client preflights; if server older or same, upload; if newer, client can force.