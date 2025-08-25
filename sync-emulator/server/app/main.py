from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.database import engine, Base
from .api import devices, files, health, contacts, messages, realtime
from .web import routes as web_routes

app = FastAPI(title="PC Sync Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(health.router)
app.include_router(devices.router)
app.include_router(files.router)
app.include_router(contacts.router)
app.include_router(messages.router)
app.include_router(realtime.router)
app.include_router(web_routes.router)
