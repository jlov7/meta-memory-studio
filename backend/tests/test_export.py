"""Tests for Memory Review Pack export endpoint."""

import io
import json
import zipfile

from app.database import get_db
from app.models.memory import MemoryItem


def test_export_review_pack_empty_workspace(client):
    """Export from empty workspace returns valid zip with summary."""
    ws = client.post("/api/workspaces", json={"name": "Export Empty"}).json()
    ws_id = ws["id"]

    resp = client.post(f"/api/workspaces/{ws_id}/export/review-pack")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    names = zf.namelist()
    assert "summary.md" in names
    assert "memories.json" in names
    assert "weight_history.json" in names


def test_export_review_pack_with_data(client):
    """Export after import contains memories in expected format."""
    ws = client.post("/api/workspaces", json={"name": "Export WS"}).json()
    ws_id = ws["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    resp = client.post(f"/api/workspaces/{ws_id}/export/review-pack")
    assert resp.status_code == 200

    zf = zipfile.ZipFile(io.BytesIO(resp.content))

    # summary.md has content
    summary_text = zf.read("summary.md").decode()
    assert len(summary_text) > 0
    assert "MetaMemory Studio" in summary_text or "Memory" in summary_text

    # memories.json is valid JSON list
    memories = json.loads(zf.read("memories.json"))
    assert isinstance(memories, list)
    assert len(memories) > 0
    for m in memories:
        assert "id" in m
        assert "title" in m
        assert "content" in m
        assert "current_weight" in m


def test_export_pii_redacted(client):
    """PII in memory content is redacted in the export."""
    ws = client.post("/api/workspaces", json={"name": "PII WS"}).json()
    ws_id = ws["id"]

    # Insert a memory with PII directly via session
    session = next(get_db())
    item = MemoryItem(
        workspace_id=ws_id,
        title="Contact info",
        content="Call John at john@example.com or +1-555-867-5309",
        memory_type="episodic",
        status="active",
    )
    session.add(item)
    session.commit()

    resp = client.post(f"/api/workspaces/{ws_id}/export/review-pack")
    assert resp.status_code == 200

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    memories = json.loads(zf.read("memories.json"))

    for m in memories:
        assert "john@example.com" not in m["content"]
        assert "867-5309" not in m["content"]


def test_export_content_disposition(client):
    """Response has correct Content-Disposition header."""
    ws = client.post("/api/workspaces", json={"name": "Header WS"}).json()
    ws_id = ws["id"]

    resp = client.post(f"/api/workspaces/{ws_id}/export/review-pack")
    assert resp.status_code == 200
    cd = resp.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert ".zip" in cd
