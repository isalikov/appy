import { fileURLToPath, URL } from 'node:url'
import { appViteConfig } from '@appy/config/vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import { mergeConfig } from 'vite'
import { defineConfig } from 'vitest/config'

// Port (LANDING_PORT) and public URLs (PUBLIC_*) come from the root .env.
export default defineConfig(env => mergeConfig(appViteConfig('landing', env), {
  plugins: [vue(), UnoCSS()],
  resolve: {
    alias: { '~': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  ssgOptions: {
    script: 'async',
    formatting: 'minify',
    dirStyle: 'nested',
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.ts'],
  },
}))
