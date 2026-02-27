#!/usr/bin/env python3
"""Import demo traces into the MetaMemory Studio backend.

Usage:
    uv run python scripts/import_demo.py --input examples/sample_traces

Steps:
  1. Create (or reuse) a workspace named "Demo"
  2. Upload each .jsonl file via POST /api/workspaces/{id}/ingest
  3. Trigger evolution to compute contributions and weight updates
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://localhost:8000"


def request(method: str, path: str, data: bytes | None = None, content_type: str | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR {e.code} from {method} {path}: {body}", file=sys.stderr)
        raise


def multipart_body(field: str, filename: str, data: bytes, boundary: str) -> bytes:
    lines = [
        f"--{boundary}",
        f'Content-Disposition: form-data; name="{field}"; filename="{filename}"',
        "Content-Type: application/octet-stream",
        "",
        "",
    ]
    header = "\r\n".join(lines).encode()
    footer = f"\r\n--{boundary}--\r\n".encode()
    return header + data + footer


def get_or_create_workspace(name: str) -> str:
    workspaces = request("GET", "/api/workspaces")["workspaces"]
    for ws in workspaces:
        if ws["name"] == name:
            print(f"  Reusing existing workspace: {ws['id']}")
            return ws["id"]

    result = request(
        "POST",
        "/api/workspaces",
        data=json.dumps({"name": name}).encode(),
        content_type="application/json",
    )
    ws_id = result["id"]
    print(f"  Created workspace: {ws_id}")
    return ws_id


def main():
    ap = argparse.ArgumentParser(description="Import demo traces into MetaMemory Studio")
    ap.add_argument("--input", required=True, help="Folder containing .jsonl trace files")
    ap.add_argument("--workspace", default="Demo", help="Workspace name (default: Demo)")
    ap.add_argument("--base-url", default=BASE_URL, help="Backend base URL")
    args = ap.parse_args()

    global BASE_URL
    BASE_URL = args.base_url.rstrip("/")

    folder = Path(args.input)
    files = sorted(folder.glob("*.jsonl"))
    if not files:
        raise SystemExit(f"No .jsonl files found in {folder}")

    print(f"Found {len(files)} trace file(s):")
    for f in files:
        print(f"  - {f.name}")

    # 1. Get or create workspace
    print(f"\nEnsuring workspace '{args.workspace}'...")
    ws_id = get_or_create_workspace(args.workspace)

    # 2. Import each file
    boundary = "----MetaMemoryBoundary"
    for fpath in files:
        print(f"\nImporting {fpath.name}...")
        data = fpath.read_bytes()
        body = multipart_body("file", fpath.name, data, boundary)
        content_type = f"multipart/form-data; boundary={boundary}"
        try:
            result = request("POST", f"/api/workspaces/{ws_id}/ingest", data=body, content_type=content_type)
            print(f"  runs={result.get('run_count', 0)}  "
                  f"memories={result.get('memory_count', 0)}  "
                  f"events={result.get('event_count', 0)}  "
                  f"pii={result.get('pii_level', '?')}  "
                  f"hash_valid={result.get('hash_valid', '?')}")
            if result.get("errors"):
                for err in result["errors"]:
                    print(f"  WARN: {err}")
        except urllib.error.HTTPError:
            print(f"  Skipping {fpath.name} due to error above.")

    # 3. Evolve to compute contributions + weights
    print(f"\nEvolving workspace '{args.workspace}' ({ws_id})...")
    try:
        evo = request("POST", f"/api/workspaces/{ws_id}/evolve")
        print(f"  contributions_created={evo.get('contributions_created', 0)}  "
              f"weight_updates={evo.get('weight_updates', 0)}")
    except urllib.error.HTTPError:
        print("  Evolution step failed (may be OK if no cross-run pairs exist).")

    print(f"\nDone! Open http://localhost:3000 and select the '{args.workspace}' workspace.")


if __name__ == "__main__":
    main()
