import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path

import http.client


def rand_id(prefix: str = "id") -> str:
    return prefix + "_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def post_json(host: str, path: str, payload):
    conn = http.client.HTTPConnection(host)
    body = json.dumps(payload)
    headers = {"Content-Type": "application/json"}
    conn.request("POST", path, body=body, headers=headers)
    resp = conn.getresponse()
    data = resp.read().decode()
    conn.close()
    return resp.status, data


def simulate(host: str = "127.0.0.1:8000"):
    device_id = rand_id("device")
    status, data = post_json(host, "/sync/device", {"device_id": device_id, "name": "EmuPhone"})
    print("register:", status, data)

    now = datetime.utcnow()
    contacts = [
        {"name": "Alice", "phone": "+12025550100", "email": "alice@example.com", "updated_at": now.isoformat()},
        {"name": "Bob", "phone": "+12025550101", "email": None, "updated_at": now.isoformat()},
    ]
    status, data = post_json(host, f"/sync/{device_id}/contacts:upsert", contacts)
    print("contacts:", status, data)

    messages = [
        {
            "external_id": rand_id("msg"),
            "sender": "+12025550100",
            "recipient": "+12025550101",
            "content": "Hello from emulator",
            "sent_at": (now - timedelta(minutes=1)).isoformat(),
            "updated_at": now.isoformat(),
        }
    ]
    status, data = post_json(host, f"/sync/{device_id}/messages:upsert", messages)
    print("messages:", status, data)

    files = [
        {
            "external_id": rand_id("file"),
            "path": "/sdcard/DCIM/Camera/img001.jpg",
            "mime_type": "image/jpeg",
            "size_bytes": 123456,
            "updated_at": now.isoformat(),
        }
    ]
    status, data = post_json(host, f"/sync/{device_id}/files:upsert", files)
    print("files:", status, data)

    status, data = post_json(host, f"/sync/{device_id}/notifications", {"title": "Sync", "body": "Completed"})
    print("notification:", status, data)


if __name__ == "__main__":
    simulate()

