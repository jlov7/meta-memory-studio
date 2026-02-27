import { mkdir } from "node:fs/promises";
import path from "node:path";

import { chromium } from "@playwright/test";

const API_BASE = process.env.API_URL ?? "http://localhost:8000/api";
const WEB_BASE = process.env.WEB_URL ?? "http://localhost:3000";
const outputDir = path.resolve(process.cwd(), "../docs/assets/screenshots");

async function requestJson(url, init) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed ${response.status} ${response.statusText}: ${text}`);
  }
  return response.json();
}

async function main() {
  await mkdir(outputDir, { recursive: true });

  const workspace = await requestJson(`${API_BASE}/workspaces`, {
    method: "POST",
    body: JSON.stringify({ name: `Gallery Workspace ${Date.now()}` }),
  });

  const workspaceId = workspace.id;
  await requestJson(`${API_BASE}/workspaces/${workspaceId}/import/demo`, { method: "POST" });
  await requestJson(`${API_BASE}/workspaces/${workspaceId}/policy/evolve`, { method: "POST" });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1720, height: 980 } });
  const page = await context.newPage();

  await page.goto(`${WEB_BASE}/`, { waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(outputDir, "landing.png"), fullPage: true });

  await page.goto(`${WEB_BASE}/workspaces/${workspaceId}`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Runs" }).waitFor({ timeout: 15_000 });
  await page.screenshot({ path: path.join(outputDir, "workspace-overview.png"), fullPage: true });

  await page.goto(`${WEB_BASE}/workspaces/${workspaceId}/memory`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Memory Library" }).waitFor({ timeout: 15_000 });
  await page.screenshot({ path: path.join(outputDir, "memory-library.png"), fullPage: true });

  await page.goto(`${WEB_BASE}/workspaces/${workspaceId}/drift`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Drift Detection" }).waitFor({ timeout: 15_000 });
  await page.screenshot({ path: path.join(outputDir, "drift-dashboard.png"), fullPage: true });

  await browser.close();
  process.stdout.write(`Screenshots saved to ${outputDir}\n`);
}

main().catch((error) => {
  process.stderr.write(`${String(error)}\n`);
  process.exit(1);
});
