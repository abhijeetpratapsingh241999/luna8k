from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.database import get_db
from ..models import FileItem
from ..services.security import get_api_key
import hashlib
import datetime as dt

router = APIRouter(prefix="/files", tags=["files"], dependencies=[Depends(get_api_key)])

class FileMeta(BaseModel):
    id: str
    device_id: str
    path: str
    size: int
    mtime: float
    hash: str

@router.post("/put")
async def put_file(
    id: str = Form(...),
    device_id: str = Form(...),
    path: str = Form(...),
    size: int = Form(...),
    mtime: float = Form(...),
    force: bool = Form(default=False),
    content: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
):
    digest = None
    data_bytes = None
    if content is not None:
        data_bytes = await content.read()
        digest = hashlib.sha256(data_bytes).hexdigest()
    result = await db.execute(select(FileItem).where(FileItem.id == id))
    existing = result.scalar_one_or_none()
    # Convert mtime (epoch seconds) to timezone-aware datetime
    mtime_dt = dt.datetime.fromtimestamp(float(mtime), tz=dt.timezone.utc)
    if existing:
        existing.device_id = device_id
        existing.path = path
        existing.size = size
        # conflict detection: if server newer and hash differs
        if existing.mtime and existing.mtime > mtime_dt and (digest and existing.hash and existing.hash != digest):
            if not force:
                raise HTTPException(status_code=409, detail={
                    "reason": "conflict",
                    "server_mtime": existing.mtime.timestamp(),
                    "server_hash": existing.hash,
                })
        existing.mtime = mtime_dt
        existing.hash = digest or existing.hash
        if data_bytes is not None:
            existing.content = data_bytes
        await db.commit()
        return {"status": "updated", "hash": existing.hash}
    file_item = FileItem(
        id=id,
        device_id=device_id,
        path=path,
        size=size,
        mtime=mtime_dt,
        hash=digest,
        content=data_bytes,
    )
    db.add(file_item)
    await db.commit()
    return {"status": "created", "hash": digest}

@router.get("/meta/{device_id}")
async def list_file_meta(device_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileItem).where(FileItem.device_id == device_id))
    items = result.scalars().all()
    return [
        {
            "id": i.id,
            "device_id": i.device_id,
            "path": i.path,
            "size": i.size,
            "mtime": i.mtime.timestamp() if i.mtime else None,
            "hash": i.hash,
            "has_content": i.content is not None,
        }
        for i in items
    ]

@router.get("/content/{file_id}")
async def get_file_content(file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileItem).where(FileItem.id == file_id))
    item = result.scalar_one_or_none()
    if not item or not item.content:
        raise HTTPException(status_code=404, detail="File content not found")
    return Response(content=item.content, media_type="application/octet-stream")

class PreflightIn(BaseModel):
    id: str
    device_id: str
    path: str
    size: int
    mtime: float
    hash: str

@router.post("/preflight")
async def preflight(meta: PreflightIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileItem).where(FileItem.id == meta.id))
    existing = result.scalar_one_or_none()
    if not existing:
        return {"action": "upload"}
    # If hashes match, can skip
    if existing.hash and existing.hash == meta.hash:
        return {"action": "skip"}
    # If server newer, report conflict
    mtime_dt = dt.datetime.fromtimestamp(float(meta.mtime), tz=dt.timezone.utc)
    if existing.mtime and existing.mtime > mtime_dt:
        return {
            "action": "conflict",
            "server": {
                "mtime": existing.mtime.timestamp(),
                "hash": existing.hash,
                "size": existing.size,
                "path": existing.path,
            },
        }
    return {"action": "upload"}