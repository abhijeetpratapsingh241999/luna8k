from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import health
from .routers import sync as sync_router
from .routers import query as query_router
from .db import engine, Base


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Phone–PC Sync Emulator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for simple dashboard assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include simple routers
app.include_router(health.router)
app.include_router(sync_router.router)
app.include_router(query_router.router)


@app.get("/")
async def root_index():
    index_file = STATIC_DIR / "index.html"
    return FileResponse(index_file)


@app.websocket("/ws")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"type": "welcome", "message": "Connected to Sync Emulator WS"})
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "message": message})
    except Exception:
        # Client disconnected or error; close silently
        try:
            await websocket.close()
        except Exception:
            pass


@app.on_event("startup")
async def on_startup():
    # Initialize database tables (no-op if already created)
    Base.metadata.create_all(bind=engine)

