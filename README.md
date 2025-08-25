# Phone ↔ PC Sync Emulator
Initial commit - project setup
Phone-PC Sync Emulator
======================

Quickstart
----------

1) Install deps

```
pip3 install -r requirements.txt
```

2) Run server

```
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

3) Visit UI at `http://localhost:8000/`

Data directories
----------------

- Phone root: `/workspace/data/phone`
- PC root: `/workspace/data/pc`

Environment variables
---------------------

- `EMULATOR_DATA_ROOT`: base data dir (default `/workspace/data`)
- `EMULATOR_PLUGINS_DIR`: plugin directory (default `/workspace/plugins`)
- `EMULATOR_STATIC_DIR`: static files dir (default `/workspace/server/static`)
