import path from 'node:path';
import { defineConfig } from '@playwright/test';

const repoRoot = path.resolve(import.meta.dirname, '..');

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:5173',
    channel: 'chrome',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  globalSetup: './e2e/global-setup.ts',
  webServer: [
    {
      command: `"${path.join(repoRoot, '.venv', 'Scripts', 'python.exe')}" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`,
      cwd: repoRoot,
      env: { GERAPOP_DATA_DIR: path.join(repoRoot, '.e2e-data') },
      url: 'http://127.0.0.1:8000/api/health',
      reuseExistingServer: true,
      timeout: 30_000,
    },
    {
      command: 'npm run dev',
      cwd: import.meta.dirname,
      url: 'http://localhost:5173',
      reuseExistingServer: true,
      timeout: 30_000,
    },
  ],
});