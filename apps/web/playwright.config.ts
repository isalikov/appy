import { appPort, rootEnv } from '@appy/config/vite'
import { defineConfig, devices } from '@playwright/test'

// E2E runs against the production build served by `vite preview` on WEB_PORT.
const env = rootEnv('production')
const baseURL = `http://localhost:${appPort('web', env)}`

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!env.CI,
  retries: env.CI ? 2 : 0,
  reporter: env.CI ? 'github' : 'list',
  use: {
    baseURL,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'pnpm build && pnpm preview',
    url: baseURL,
    reuseExistingServer: !env.CI,
  },
})
