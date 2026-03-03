"""Integration tests for API endpoints."""

from app.config import settings


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_create_workspace(client):
    resp = client.post("/api/workspaces", json={"name": "Test Workspace"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Workspace"
    assert "id" in data


def test_list_workspaces(client):
    client.post("/api/workspaces", json={"name": "WS1"})
    client.post("/api/workspaces", json={"name": "WS2"})

    resp = client.get("/api/workspaces")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["workspaces"]) >= 2


def test_import_demo_and_list_runs(client):
    # Create workspace
    ws_resp = client.post("/api/workspaces", json={"name": "Demo WS"})
    ws_id = ws_resp.json()["id"]

    # Import demo
    resp = client.post(f"/api/workspaces/{ws_id}/import/demo")
    assert resp.status_code == 200
    import_data = resp.json()
    assert import_data["run_count"] == 2
    assert import_data["hash_valid"] is True

    # List runs
    runs_resp = client.get(f"/api/workspaces/{ws_id}/runs")
    assert runs_resp.status_code == 200
    runs_data = runs_resp.json()
    assert len(runs_data["runs"]) == 2


def test_run_detail_with_timeline(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Timeline WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    runs_resp = client.get(f"/api/workspaces/{ws_id}/runs")
    run_id = runs_resp.json()["runs"][0]["id"]

    detail_resp = client.get(f"/api/workspaces/{ws_id}/runs/{run_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert "timeline" in detail
    assert len(detail["timeline"]) > 0


def test_memory_library(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Memory WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    mem_resp = client.get(f"/api/workspaces/{ws_id}/memory")
    assert mem_resp.status_code == 200
    mem_data = mem_resp.json()
    assert len(mem_data["memories"]) > 0

    # Check specific memory exists
    titles = [m["title"] for m in mem_data["memories"]]
    assert "Apply airline preference before booking" in titles


def test_memory_detail(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Detail WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    mem_resp = client.get(f"/api/workspaces/{ws_id}/memory")
    mem_id = mem_resp.json()["memories"][0]["id"]

    detail_resp = client.get(f"/api/workspaces/{ws_id}/memory/{mem_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert "memory" in detail
    assert detail["memory"]["title"] is not None
    assert detail["memory"]["content"] is not None
    assert "weight_history" in detail
    assert "contributions" in detail


def test_evolve_creates_contributions(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Evolve WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    # Verify both runs exist (baseline + guided)
    runs_resp = client.get(f"/api/workspaces/{ws_id}/runs")
    runs = runs_resp.json()["runs"]
    assert len(runs) == 2
    external_ids = {r["external_id"] for r in runs}
    assert "run_demo_001" in external_ids
    assert "run_demo_002" in external_ids

    # Evolve — no body, just workspace_id in path
    evolve_resp = client.post(f"/api/workspaces/{ws_id}/policy/evolve")
    assert evolve_resp.status_code == 200
    evolve_data = evolve_resp.json()
    assert "contributions_created" in evolve_data
    assert "weight_updates" in evolve_data


def test_soft_delete_memory(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Delete WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    mem_resp = client.get(f"/api/workspaces/{ws_id}/memory")
    mem_id = mem_resp.json()["memories"][0]["id"]

    # Soft delete (deprecate) — returns MemoryOut directly
    dep_resp = client.patch(f"/api/workspaces/{ws_id}/memory/{mem_id}/deprecate")
    assert dep_resp.status_code == 200
    assert dep_resp.json()["status"] == "deprecated"

    # GET detail — returns MemoryDetail with nested memory object
    detail_resp = client.get(f"/api/workspaces/{ws_id}/memory/{mem_id}")
    assert detail_resp.json()["memory"]["status"] == "deprecated"


def test_hard_delete_memory(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Forget WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    mem_resp = client.get(f"/api/workspaces/{ws_id}/memory")
    mem_id = mem_resp.json()["memories"][0]["id"]

    # Hard delete (forget) — returns {"deleted": True}
    forget_resp = client.delete(f"/api/workspaces/{ws_id}/memory/{mem_id}")
    assert forget_resp.status_code == 200
    assert forget_resp.json()["deleted"] is True

    # GET detail — tombstone still exists in DB, content wiped
    detail_resp = client.get(f"/api/workspaces/{ws_id}/memory/{mem_id}")
    assert detail_resp.json()["memory"]["status"] == "deleted"
    assert detail_resp.json()["memory"]["content"] == "[REDACTED]"


def test_integrity_check(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Integrity WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    resp = client.get(f"/api/workspaces/{ws_id}/integrity")
    assert resp.status_code == 200
    data = resp.json()
    assert data["all_valid"] is True
    assert len(data["results"]) > 0
    assert all(f["valid"] for f in data["results"])


def test_request_id_header_added_and_propagated(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.headers.get("x-request-id")

    custom_request_id = "req-test-123"
    resp = client.get("/api/health", headers={"x-request-id": custom_request_id})
    assert resp.status_code == 200
    assert resp.headers.get("x-request-id") == custom_request_id


def test_import_payload_limit_rejected(client):
    old_limit = settings.MAX_IMPORT_BYTES
    settings.MAX_IMPORT_BYTES = 8
    try:
        ws_resp = client.post("/api/workspaces", json={"name": "Payload WS"})
        ws_id = ws_resp.json()["id"]
        resp = client.post(
            f"/api/workspaces/{ws_id}/import",
            files={
                "file": (
                    "payload.jsonl",
                    b'{"type":"run_start","payload":{}}\n',
                    "application/json",
                )
            },
        )
        assert resp.status_code == 413
        detail = resp.json()["detail"]
        assert detail["error"]["code"] == "payload_too_large"
    finally:
        settings.MAX_IMPORT_BYTES = old_limit


def test_import_idempotent_duplicate_content(client, demo_jsonl):
    ws_resp = client.post("/api/workspaces", json={"name": "Idempotent WS"})
    ws_id = ws_resp.json()["id"]

    first = client.post(
        f"/api/workspaces/{ws_id}/import",
        files={"file": ("demo_runs.jsonl", demo_jsonl.encode("utf-8"), "application/json")},
    )
    assert first.status_code == 200
    first_data = first.json()
    assert first_data["success"] is True
    assert first_data["duplicate"] is False
    assert first_data["run_count"] == 2

    second = client.post(
        f"/api/workspaces/{ws_id}/import",
        files={"file": ("demo_runs.jsonl", demo_jsonl.encode("utf-8"), "application/json")},
    )
    assert second.status_code == 200
    second_data = second.json()
    assert second_data["success"] is True
    assert second_data["duplicate"] is True
    assert second_data["raw_file_id"] == first_data["raw_file_id"]
    assert second_data["duplicate_of_raw_file_id"] == first_data["raw_file_id"]
    assert second_data["run_count"] == 0
    assert second_data["memory_count"] == 0

    runs_resp = client.get(f"/api/workspaces/{ws_id}/runs")
    assert runs_resp.status_code == 200
    assert runs_resp.json()["total"] == 2


def test_runs_pagination(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Runs Paging WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    page1_resp = client.get(f"/api/workspaces/{ws_id}/runs?limit=1&offset=0")
    page2_resp = client.get(f"/api/workspaces/{ws_id}/runs?limit=1&offset=1")

    assert page1_resp.status_code == 200
    assert page2_resp.status_code == 200
    page1 = page1_resp.json()
    page2 = page2_resp.json()
    assert page1["total"] == 2
    assert page1["limit"] == 1
    assert page1["offset"] == 0
    assert len(page1["runs"]) == 1
    assert page2["offset"] == 1
    assert len(page2["runs"]) == 1
    assert page1["runs"][0]["id"] != page2["runs"][0]["id"]


def test_memory_pagination(client):
    ws_resp = client.post("/api/workspaces", json={"name": "Memory Paging WS"})
    ws_id = ws_resp.json()["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    page1_resp = client.get(f"/api/workspaces/{ws_id}/memory?status=&limit=1&offset=0")
    page2_resp = client.get(f"/api/workspaces/{ws_id}/memory?status=&limit=1&offset=1")

    assert page1_resp.status_code == 200
    assert page2_resp.status_code == 200
    page1 = page1_resp.json()
    page2 = page2_resp.json()
    assert page1["total"] >= 1
    assert page1["limit"] == 1
    assert page1["offset"] == 0
    assert len(page1["memories"]) == 1
    assert page2["offset"] == 1
    assert len(page2["memories"]) in (0, 1)
    if page2["memories"]:
        assert page1["memories"][0]["id"] != page2["memories"][0]["id"]


def test_rate_limit_on_mutating_endpoint(client):
    old_enabled = settings.RATE_LIMIT_ENABLED
    old_limit = settings.RATE_LIMIT_PER_MINUTE
    settings.RATE_LIMIT_ENABLED = True
    settings.RATE_LIMIT_PER_MINUTE = 2
    try:
        ws_resp = client.post("/api/workspaces", json={"name": "Rate Limit WS"})
        ws_id = ws_resp.json()["id"]

        first = client.post(f"/api/workspaces/{ws_id}/import/demo")
        second = client.post(f"/api/workspaces/{ws_id}/import/demo")
        third = client.post(f"/api/workspaces/{ws_id}/import/demo")

        assert first.status_code == 200
        assert second.status_code == 200
        assert third.status_code == 429
        detail = third.json()["detail"]
        assert detail["error"]["code"] == "rate_limited"
    finally:
        settings.RATE_LIMIT_ENABLED = old_enabled
        settings.RATE_LIMIT_PER_MINUTE = old_limit
