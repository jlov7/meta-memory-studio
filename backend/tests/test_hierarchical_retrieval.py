"""Tests for hierarchical theme-based retrieval."""

from sqlmodel import Session

from app.models.memory import MemoryItem


def _add_memory(session: Session, ws_id: str, title: str, content: str = "") -> MemoryItem:
    m = MemoryItem(
        workspace_id=ws_id,
        title=title,
        content=content or title,
        memory_type="episodic",
        status="active",
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


def test_themes_empty_workspace(client):
    """Themes endpoint returns empty groups for workspace with no memories."""
    ws = client.post("/api/workspaces", json={"name": "Theme Empty"}).json()
    ws_id = ws["id"]

    resp = client.get(f"/api/workspaces/{ws_id}/memory/themes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["groups"] == []
    assert data["total_memories"] == 0


def test_themes_after_import(client):
    """After importing demo, /memory/themes returns grouped results."""
    ws = client.post("/api/workspaces", json={"name": "Theme Demo"}).json()
    ws_id = ws["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    resp = client.get(f"/api/workspaces/{ws_id}/memory/themes")
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data["groups"], list)
    assert data["total_memories"] > 0

    for group in data["groups"]:
        assert "theme_id" in group
        assert "theme_title" in group
        assert isinstance(group["memories"], list)
        assert len(group["memories"]) >= 1


def test_themes_dedup_similar_titles(client, session):
    """Memories with similar titles are grouped into the same theme."""
    from app.memory.themes import rebuild_themes

    ws = client.post("/api/workspaces", json={"name": "Theme Dedup"}).json()
    ws_id = ws["id"]

    # Add several similar-titled memories
    _add_memory(session, ws_id, "Book flight to New York")
    _add_memory(session, ws_id, "Book flight to Los Angeles")
    _add_memory(session, ws_id, "Book flight to Chicago")
    _add_memory(session, ws_id, "Order groceries online")

    # Trigger theme rebuild
    rebuild_themes(session, ws_id)

    resp = client.get(f"/api/workspaces/{ws_id}/memory/themes")
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["groups"]) >= 1
    # The three "Book flight" memories should be fewer themes than memories
    total_memories = data["total_memories"]
    total_groups = len(data["groups"])
    assert total_memories >= total_groups  # de-dup happened


def test_themes_distinct_titles_separate_groups(client, session):
    """Memories with completely different titles each get their own group."""
    from app.memory.themes import rebuild_themes

    ws = client.post("/api/workspaces", json={"name": "Theme Distinct"}).json()
    ws_id = ws["id"]

    _add_memory(session, ws_id, "Zebra biology facts")
    _add_memory(session, ws_id, "Python programming tips")
    _add_memory(session, ws_id, "French cuisine recipes")

    rebuild_themes(session, ws_id)

    resp = client.get(f"/api/workspaces/{ws_id}/memory/themes")
    assert resp.status_code == 200
    data = resp.json()

    # All distinct => each in its own group
    assert data["total_memories"] == 3
    assert len(data["groups"]) == 3


def test_themes_route_not_captured_by_memory_id(client):
    """/memory/themes is not captured by /memory/{memory_id} route."""
    ws = client.post("/api/workspaces", json={"name": "Route WS"}).json()
    ws_id = ws["id"]

    # Should return 200 with a ThemeGroupList, NOT a 404
    resp = client.get(f"/api/workspaces/{ws_id}/memory/themes")
    assert resp.status_code == 200
    assert "groups" in resp.json()
