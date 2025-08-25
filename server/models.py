from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


DeviceName = Literal["phone", "pc"]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class FileEntry(BaseModel):
    path: str
    is_dir: bool
    size_bytes: int = 0
    modified_ms: int = 0


class FileListResponse(BaseModel):
    device: DeviceName
    root: str
    files: List[FileEntry]


class FileOperation(str, Enum):
    upload = "upload"
    delete = "delete"
    mkdir = "mkdir"
    move = "move"


class FileOperationRequest(BaseModel):
    device: DeviceName
    operation: FileOperation
    path: str
    dest_path: Optional[str] = None
    recursive: bool = False


class SyncDirection(str, Enum):
    phone_to_pc = "phone_to_pc"
    pc_to_phone = "pc_to_phone"
    bidirectional = "bidirectional"


class PlannedOperation(BaseModel):
    operation: FileOperation
    device_src: DeviceName
    device_dst: Optional[DeviceName] = None
    path: str
    dest_path: Optional[str] = None
    reason: str = ""


class SyncRequest(BaseModel):
    direction: SyncDirection


class SyncPlan(BaseModel):
    direction: SyncDirection
    operations: List[PlannedOperation] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)

