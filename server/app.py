from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .models import (
    DeviceName,
    FileEntry,
    FileListResponse,
    FileOperation,
    FileOperationRequest,
    HealthResponse,
    SyncDirection,
    SyncPlan,
    SyncRequest,
)
from .state import EmulatorState, EventHub, device_root, get_data_root
from .plugins import plugin_manager


APP_TITLE = "Phone-PC Sync Emulator"
APP_VERSION = "0.1.0"


state = EmulatorState()
events = EventHub()

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    # Ensure data roots exist
    get_data_root()
    device_root("phone")
    device_root("pc")
    # Load plugins if present
    plugins_dir = Path(os.getenv("EMULATOR_PLUGINS_DIR", "/workspace/plugins"))
    plugin_manager.load_plugins(plugins_dir)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.get("/files", response_model=FileListResponse)
async def list_files(device: DeviceName = Query(..., description="Target device: phone or pc")) -> FileListResponse:
    files = await state.list_files(device)
    return FileListResponse(device=device, root=str(device_root(device)), files=files)


@app.post("/upload")
async def upload_file(
    device: DeviceName = Query(...),
    path: str = Query(..., description="Relative path under the device root"),
    file: UploadFile = File(...),
):
    await state.save_upload(device, path, file)
    payload = {"type": "file_uploaded", "device": device, "path": path}
    await events.broadcast(payload)
    plugin_manager.on_event(payload)
    return {"status": "ok"}


@app.post("/op")
async def file_operation(req: FileOperationRequest):
    if req.operation == FileOperation.delete:
        await state.delete_path(req.device, req.path, recursive=req.recursive)
    elif req.operation == FileOperation.mkdir:
        await state.make_dir(req.device, req.path)
    elif req.operation == FileOperation.move:
        if not req.dest_path:
            raise HTTPException(status_code=400, detail="dest_path required for move")
        await state.move_path(req.device, req.path, req.dest_path)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported operation: {req.operation}")

    payload = {
        "type": "file_operation",
        "operation": req.operation,
        "device": req.device,
        "path": req.path,
        "dest_path": req.dest_path,
        "recursive": req.recursive,
    }
    await events.broadcast(payload)
    plugin_manager.on_event(payload)
    return {"status": "ok"}


@app.post("/sync/plan", response_model=SyncPlan)
async def sync_plan(req: SyncRequest) -> SyncPlan:
    plan = await state.compute_sync_plan(req.direction)
    return plan


@app.post("/sync/execute")
async def sync_execute(req: SyncRequest):
    plan = await state.compute_sync_plan(req.direction)
    await state.execute_sync_plan(plan)
    payload = {"type": "sync_executed", "direction": req.direction, "summary": plan.summary}
    await events.broadcast(payload)
    plugin_manager.on_event(payload)
    return {"status": "ok", "summary": plan.summary}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await events.register(websocket)
    try:
        while True:
            # Echo pings or ignore; we keep the socket open
            try:
                _ = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                try:
                    await websocket.send_text("\n")
                except Exception:
                    pass
    except WebSocketDisconnect:
        await events.unregister(websocket)
    except Exception:
        await events.unregister(websocket)


# Static files and simple UI
static_dir = Path(os.getenv("EMULATOR_STATIC_DIR", "/workspace/server/static"))
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index_page() -> HTMLResponse:
    index_path = static_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text())
    return HTMLResponse("""
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>Phone-PC Sync Emulator</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <style>
    body { font-family: sans-serif; margin: 20px; }
    pre { background: #f5f5f5; padding: 10px; border-radius: 6px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; }
    .row { display: flex; gap: 8px; align-items: center; }
    button { padding: 6px 10px; }
  </style>
}</head>
<body>
  <h1>Phone-PC Sync Emulator</h1>
  <div class=\"row\">
    <button onclick=\"sync('bidirectional')\">Sync Bidirectional</button>
    <button onclick=\"sync('phone_to_pc')\">Sync Phone ➜ PC</button>
    <button onclick=\"sync('pc_to_phone')\">Sync PC ➜ Phone</button>
  </div>
  <div class=\"grid\">
    <div class=\"card\">
      <h3>Phone Files</h3>
      <pre id=\"phone\">Loading...</pre>
    </div>
    <div class=\"card\">
      <h3>PC Files</h3>
      <pre id=\"pc\">Loading...</pre>
    </div>
  </div>
  <script>
    async function list(device){
      const res = await fetch('/files?device='+device);
      const data = await res.json();
      const txt = (data.files||[]).map(f => (f.is_dir? '[D] ':'[F] ')+f.path + (f.is_dir?'':` (${f.size_bytes} bytes)`)).join('\n');
      document.getElementById(device).textContent = txt;
    }
    async function sync(direction){
      const res = await fetch('/sync/execute', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({direction})});
      await res.json();
      await refresh();
    }
    async function refresh(){
      await Promise.all([list('phone'), list('pc')]);
    }
    function connect(){
      const ws = new WebSocket((location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/ws');
      ws.onmessage = () => refresh();
      ws.onclose = () => setTimeout(connect, 1000);
    }
    connect();
    refresh();
  </script>
</body>
</html>
""")

