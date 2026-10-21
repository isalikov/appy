import { defineConfig } from 'vitest/config'
import { PUBLIC_ENV_PREFIX, ROOT_DIR } from './src/vite'

export default defineConfig({
  envDir: ROOT_DIR,
  envPrefix: PUBLIC_ENV_PREFIX,
  test: { environment: 'jsdom', include: ['src/**/*.test.ts'] },
})
