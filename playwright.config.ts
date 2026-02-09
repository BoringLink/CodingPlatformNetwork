import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  webServer: [
    {
      command: "cd backend && pnpm run start:dev",
      port: 3001,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: "cd frontend && pnpm run dev",
      port: 5173,
      reuseExistingServer: !process.env.CI,
    },
  ],
  reporter: [["html"]],
  use: {
    baseURL: "http://localhost:5173",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
    {
      name: "firefox",
      use: { browserName: "firefox" },
    },
    {
      name: "webkit",
      use: { browserName: "webkit" },
    },
  ],
});
