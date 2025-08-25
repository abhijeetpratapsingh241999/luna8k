from pathlib import Path
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..db.database import get_db
from ..models import Device, FileItem

router = APIRouter(tags=["web"])  # no auth for simple local status page

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/")
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    devices = (await db.execute(select(Device))).scalars().all()
    file_counts = {}
    for d in devices:
        count = (
            (await db.execute(select(func.count()).select_from(FileItem).where(FileItem.device_id == d.id)))
            .scalar_one()
        )
        file_counts[d.id] = count
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "devices": devices,
            "file_counts": file_counts,
        },
    )

