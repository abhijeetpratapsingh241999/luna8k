from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from fastapi import UploadFile

from .models import (
    DeviceName,
    FileEntry,
    FileOperation,
    PlannedOperation,
    SyncDirection,
    SyncPlan,
)


def get_data_root() -> Path:
    root = Path(os.getenv("EMULATOR_DATA_ROOT", "/workspace/data"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def device_root(device: DeviceName) -> Path:
    root = get_data_root() / device
    root.mkdir(parents=True, exist_ok=True)
    return root


class EventHub:
    def __init__(self) -> None:
        self._connections: Set = set()
        self._lock = asyncio.Lock()

    async def register(self, websocket) -> None:
        async with self._lock:
            self._connections.add(websocket)

    async def unregister(self, websocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, event: dict) -> None:
        async with self._lock:
            connections = list(self._connections)
        if not connections:
            return
        data = event
        for ws in connections:
            try:
                await ws.send_json(data)
            except Exception:
                # Drop broken connections silently
                pass


class EmulatorState:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    async def list_files(self, device: DeviceName) -> List[FileEntry]:
        root = device_root(device)
        entries: List[FileEntry] = []
        for base, dirs, files in os.walk(root):
            rel_base = str(Path(base).relative_to(root))
            rel_base = "" if rel_base == "." else rel_base
            for d in dirs:
                p = Path(rel_base) / d
                full = root / p
                stat = full.stat()
                entries.append(
                    FileEntry(
                        path=str(p).replace("\\", "/"),
                        is_dir=True,
                        size_bytes=0,
                        modified_ms=int(stat.st_mtime * 1000),
                    )
                )
            for f in files:
                p = Path(rel_base) / f
                full = root / p
                stat = full.stat()
                entries.append(
                    FileEntry(
                        path=str(p).replace("\\", "/"),
                        is_dir=False,
                        size_bytes=int(stat.st_size),
                        modified_ms=int(stat.st_mtime * 1000),
                    )
                )
        entries.sort(key=lambda e: (e.path, not e.is_dir))
        return entries

    async def save_upload(self, device: DeviceName, path: str, file: UploadFile) -> None:
        root = device_root(device)
        dest = root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with self._lock:
            with open(dest, "wb") as fh:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    fh.write(chunk)

    async def delete_path(self, device: DeviceName, path: str, recursive: bool = False) -> None:
        root = device_root(device)
        target = root / path
        if target.is_dir():
            if recursive:
                for child in sorted(target.rglob("*"), reverse=True):
                    if child.is_file():
                        child.unlink(missing_ok=True)
                    else:
                        child.rmdir()
                target.rmdir()
            else:
                target.rmdir()
        else:
            target.unlink(missing_ok=True)

    async def make_dir(self, device: DeviceName, path: str) -> None:
        root = device_root(device)
        (root / path).mkdir(parents=True, exist_ok=True)

    async def move_path(self, device: DeviceName, src: str, dest: str) -> None:
        root = device_root(device)
        src_p = root / src
        dest_p = root / dest
        dest_p.parent.mkdir(parents=True, exist_ok=True)
        src_p.rename(dest_p)

    async def compute_sync_plan(self, direction: SyncDirection) -> SyncPlan:
        phone_files = await self.list_files("phone")
        pc_files = await self.list_files("pc")

        phone_map = {e.path: e for e in phone_files if not e.is_dir}
        pc_map = {e.path: e for e in pc_files if not e.is_dir}

        all_paths = sorted(set(phone_map.keys()) | set(pc_map.keys()))
        ops: List[PlannedOperation] = []

        def plan_copy(src_device: DeviceName, dst_device: DeviceName, rel_path: str, reason: str) -> None:
            ops.append(
                PlannedOperation(
                    operation=FileOperation.upload,
                    device_src=src_device,
                    device_dst=dst_device,
                    path=rel_path,
                    dest_path=rel_path,
                    reason=reason,
                )
            )

        for p in all_paths:
            ph = phone_map.get(p)
            pc = pc_map.get(p)
            if ph and not pc:
                if direction in (SyncDirection.phone_to_pc, SyncDirection.bidirectional):
                    plan_copy("phone", "pc", p, "missing on pc")
            elif pc and not ph:
                if direction in (SyncDirection.pc_to_phone, SyncDirection.bidirectional):
                    plan_copy("pc", "phone", p, "missing on phone")
            else:
                # both exist, compare modified time and size
                if ph.modified_ms != pc.modified_ms or ph.size_bytes != pc.size_bytes:
                    if direction == SyncDirection.phone_to_pc:
                        plan_copy("phone", "pc", p, "overwrite from phone")
                    elif direction == SyncDirection.pc_to_phone:
                        plan_copy("pc", "phone", p, "overwrite from pc")
                    else:
                        # bidirectional - pick newer
                        if ph.modified_ms >= pc.modified_ms:
                            plan_copy("phone", "pc", p, "newer on phone")
                        else:
                            plan_copy("pc", "phone", p, "newer on pc")

        summary = {
            "total": len(ops),
            "phone_files": len(phone_map),
            "pc_files": len(pc_map),
        }
        return SyncPlan(direction=direction, operations=ops, summary=summary)

    async def execute_sync_plan(self, plan: SyncPlan) -> None:
        for op in plan.operations:
            if op.operation != FileOperation.upload:
                continue
            assert op.device_dst is not None
            src_root = device_root(op.device_src)
            dst_root = device_root(op.device_dst)
            src_path = src_root / op.path
            dst_path = dst_root / (op.dest_path or op.path)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            if src_path.is_file():
                dst_path.write_bytes(src_path.read_bytes())
                # Preserve mtime
                stat = src_path.stat()
                os.utime(dst_path, (stat.st_atime, stat.st_mtime))

