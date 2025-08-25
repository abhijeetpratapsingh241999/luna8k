import asyncio
import json
import os
import sys
import time
import uuid
import hashlib
import pathlib
import httpx
import websockets
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SERVER = os.environ.get("SYNC_SERVER", "http://127.0.0.1:8000")
API_KEY = None


def load_api_key() -> str:
	global API_KEY
	if API_KEY:
		return API_KEY
	# fetch from server health/key for demo
	r = httpx.get(f"{SERVER}/health/key", timeout=5)
	r.raise_for_status()
	API_KEY = r.json()["api_key"]
	return API_KEY


def get_device_id() -> str:
	device_id_file = pathlib.Path.home() / ".sync_emulator_device_id"
	if device_id_file.exists():
		return device_id_file.read_text().strip()
	did = uuid.uuid4().hex
	device_id_file.write_text(did)
	return did


async def register_device(client: httpx.AsyncClient, device_id: str):
	payload = {
		"id": device_id,
		"name": os.environ.get("EMULATOR_NAME", "PhoneEmu"),
		"platform": "emulator",
		"capabilities": {"files": True, "contacts": True, "messages": True},
	}
	resp = await client.post("/devices/register", json=payload)
	resp.raise_for_status()
	return resp.json()


class Hasher:
	@staticmethod
	def sha256_of_file(path: pathlib.Path) -> str:
		h = hashlib.sha256()
		with path.open("rb") as fh:
			for chunk in iter(lambda: fh.read(8192), b""):
				h.update(chunk)
		return h.hexdigest()


class FileSyncHandler(FileSystemEventHandler):
	def __init__(self, device_id: str, client: httpx.AsyncClient, root: pathlib.Path):
		self.device_id = device_id
		self.client = client
		self.root = root

	def on_any_event(self, event):
		if event.is_directory:
			return
		path = pathlib.Path(event.src_path)
		if not path.exists():
			return
		asyncio.run(self.sync_file(path))

	async def sync_file(self, path: pathlib.Path):
		rel = str(path.relative_to(self.root))
		stat = path.stat()
		file_id = hashlib.sha1(f"{self.device_id}:{rel}".encode()).hexdigest()
		digest = Hasher.sha256_of_file(path)
		headers = {"x-api-key": load_api_key()}
		# Preflight
		pre = httpx.post(
			f"{SERVER}/files/preflight",
			json={
				"id": file_id,
				"device_id": self.device_id,
				"path": rel,
				"size": stat.st_size,
				"mtime": stat.st_mtime,
				"hash": digest,
			},
			headers=headers,
			timeout=15,
		)
		pre.raise_for_status()
		action = pre.json().get("action")
		if action == "skip":
			return
		# Upload
		form = {
			"id": file_id,
			"device_id": self.device_id,
			"path": rel,
			"size": str(stat.st_size),
			"mtime": str(stat.st_mtime),
			"force": "false",
		}
		files = {"content": (path.name, path.open("rb"))}
		r = httpx.post(f"{SERVER}/files/put", data=form, files=files, headers=headers, timeout=60)
		if r.status_code == 409:
			# Conflict: for emulator, resolve by force upload
			form["force"] = "true"
			r = httpx.post(f"{SERVER}/files/put", data=form, files=files, headers=headers, timeout=60)
		r.raise_for_status()


async def heartbeat(device_id: str):
	key = load_api_key()
	uri = f"{SERVER.replace('http', 'ws')}/ws/heartbeat?device_id={device_id}&api_key={key}"
	while True:
		try:
			async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as ws:
				while True:
					await ws.send("ping")
					await asyncio.sleep(10)
		except Exception:
			await asyncio.sleep(5)


async def main():
	load_api_key()
	device_id = get_device_id()
	headers = {"x-api-key": API_KEY}
	async with httpx.AsyncClient(base_url=SERVER, headers=headers, timeout=10) as client:
		await register_device(client, device_id)

	# Start heartbeat task
	hb = asyncio.create_task(heartbeat(device_id))

	# Start watchdog on a demo folder
	root = pathlib.Path(os.environ.get("EMULATOR_SYNC_DIR", str(pathlib.Path.cwd() / "emu_files")))
	root.mkdir(parents=True, exist_ok=True)
	observer = Observer()
	handler = FileSyncHandler(device_id, None, root)
	observer.schedule(handler, str(root), recursive=True)
	observer.start()
	try:
		# initial scan
		for p in root.rglob("*"):
			if p.is_file():
				await handler.sync_file(p)
		while True:
			await asyncio.sleep(1)
	except KeyboardInterrupt:
		pass
	finally:
		observer.stop()
		observer.join()
		hb.cancel()


if __name__ == "__main__":
	asyncio.run(main())