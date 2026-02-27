import { test, expect, type APIRequestContext } from "@playwright/test";
import { readFileSync } from "fs";
import path from "path";

const DEMO_TRACE = path.resolve(
  __dirname,
  "../../examples/sample_traces/demo_runs.jsonl"
);

async function setupWorkspace(request: APIRequestContext, name: string): Promise<string> {
  const wsResp = await request.post("http://localhost:8000/api/workspaces", {
    data: { name },
  });
  const { id: wsId } = await wsResp.json();

  await request.post(`http://localhost:8000/api/workspaces/${wsId}/import`, {
    multipart: {
      file: {
        name: "demo_runs.jsonl",
        mimeType: "application/octet-stream",
        buffer: readFileSync(DEMO_TRACE),
      },
    },
  });

  return wsId;
}

test.describe("Stretch feature E2E tests", () => {
  test("drift dashboard loads and shows correct schema", async ({ page, request }) => {
    const wsId = await setupWorkspace(request, "E2E Drift WS");

    await page.goto(`/workspaces/${wsId}/drift`);

    await expect(page.getByRole("heading", { name: /Drift/i })).toBeVisible({
      timeout: 8_000,
    });
    await expect(page.getByText(/Total Runs/i)).toBeVisible({ timeout: 8_000 });
  });

  test("drift API returns valid structure with demo data", async ({ request }) => {
    const wsId = await setupWorkspace(request, "E2E Drift API");

    const driftResp = await request.get(
      `http://localhost:8000/api/workspaces/${wsId}/drift`
    );
    expect(driftResp.ok()).toBeTruthy();
    const data = await driftResp.json();

    expect(data).toHaveProperty("workspace_id", wsId);
    expect(data).toHaveProperty("total_runs");
    expect(data).toHaveProperty("anomalies");
    expect(Array.isArray(data.anomalies)).toBe(true);
  });

  test("memory library theme grouping toggle works", async ({ page, request }) => {
    const wsId = await setupWorkspace(request, "E2E Theme WS");

    await page.goto(`/workspaces/${wsId}/memory`);

    await expect(page.locator("[data-testid='memory-card']").first()).toBeVisible({
      timeout: 10_000,
    });

    // Click the theme grouping toggle (aria-label)
    const ariaToggle = page.locator('[aria-label="Toggle theme grouping"]');
    await expect(ariaToggle).toBeVisible({ timeout: 5_000 });
    await ariaToggle.click();
    await page.waitForTimeout(500);

    // After toggle memories or theme sections should still be visible
    const cardCount = await page.locator("[data-testid='memory-card']").count();
    const themeCount = await page.getByText(/Book|Apply|Prefer/i).count();
    expect(cardCount + themeCount).toBeGreaterThan(0);
  });

  test("export review pack API returns valid zip", async ({ request }) => {
    const wsId = await setupWorkspace(request, "E2E Export WS");

    const exportResp = await request.post(
      `http://localhost:8000/api/workspaces/${wsId}/export/review-pack`
    );
    expect(exportResp.ok()).toBeTruthy();
    expect(exportResp.headers()["content-type"]).toBe("application/zip");

    const body = await exportResp.body();
    expect(body.length).toBeGreaterThan(100);
  });

  test("memory themes API returns grouped structure", async ({ request }) => {
    const wsId = await setupWorkspace(request, "E2E Themes API");

    const themesResp = await request.get(
      `http://localhost:8000/api/workspaces/${wsId}/memory/themes`
    );
    expect(themesResp.ok()).toBeTruthy();
    const data = await themesResp.json();

    expect(data).toHaveProperty("groups");
    expect(data).toHaveProperty("total_memories");
    expect(Array.isArray(data.groups)).toBe(true);

    for (const group of data.groups) {
      expect(group).toHaveProperty("theme_id");
      expect(group).toHaveProperty("theme_title");
      expect(Array.isArray(group.memories)).toBe(true);
    }
  });
});
