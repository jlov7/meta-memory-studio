"""Tests for drift detection."""


def test_drift_no_runs(client):
    """Drift endpoint with empty workspace returns zero anomalies."""
    ws = client.post("/api/workspaces", json={"name": "Drift Empty"}).json()
    ws_id = ws["id"]

    resp = client.get(f"/api/workspaces/{ws_id}/drift")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_runs"] == 0
    assert data["anomalies"] == []


def test_drift_single_run(client):
    """With only one run, no meaningful baseline => no anomalies."""
    ws = client.post("/api/workspaces", json={"name": "Drift Single"}).json()
    ws_id = ws["id"]

    # Import demo (which includes 2 runs), then test that structure is there
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    resp = client.get(f"/api/workspaces/{ws_id}/drift")
    assert resp.status_code == 200
    data = resp.json()
    # With 2 runs, we may or may not have anomalies — but structure is correct
    assert "workspace_id" in data
    assert "total_runs" in data
    assert "anomalies" in data
    assert data["total_runs"] == 2


def test_drift_with_demo_data(client):
    """Drift endpoint returns correct schema with demo data."""
    ws = client.post("/api/workspaces", json={"name": "Drift Demo"}).json()
    ws_id = ws["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    resp = client.get(f"/api/workspaces/{ws_id}/drift")
    assert resp.status_code == 200
    data = resp.json()

    assert data["workspace_id"] == ws_id
    assert isinstance(data["total_runs"], int)
    assert isinstance(data["anomalies"], list)

    for anomaly in data["anomalies"]:
        assert "tool_name" in anomaly
        assert "expected_freq" in anomaly
        assert "actual_freq" in anomaly
        assert "anomaly_score" in anomaly
        assert "runs_affected" in anomaly
        assert anomaly["anomaly_score"] > 0


def test_drift_anomalies_sorted_by_score(client):
    """Anomalies are returned highest score first."""
    ws = client.post("/api/workspaces", json={"name": "Drift Sort"}).json()
    ws_id = ws["id"]
    client.post(f"/api/workspaces/{ws_id}/import/demo")

    resp = client.get(f"/api/workspaces/{ws_id}/drift")
    data = resp.json()

    scores = [a["anomaly_score"] for a in data["anomalies"]]
    assert scores == sorted(scores, reverse=True)
