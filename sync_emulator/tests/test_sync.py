import json
from pathlib import Path

import httpx


BASE_URL = "http://127.0.0.1:8000"


def test_health_and_device_flow():
    # health
    r = httpx.get(BASE_URL + "/health/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    # register device
    device_id = "test_device_123"
    r = httpx.post(BASE_URL + "/sync/device", json={"device_id": device_id, "name": "Test"})
    assert r.status_code == 200
    body = r.json()
    assert body["device_id"] == device_id

    # upsert a contact
    r = httpx.post(BASE_URL + f"/sync/{device_id}/contacts:upsert", json=[{"name": "Zed", "phone": "+100", "email": None}])
    assert r.status_code == 200
    contacts = r.json()
    assert isinstance(contacts, list) and len(contacts) == 1

    # list contacts
    r = httpx.get(BASE_URL + f"/query/{device_id}/contacts")
    assert r.status_code == 200
    assert any(c["phone"] == "+100" for c in r.json())

