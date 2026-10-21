// Loaded natively by Node when Vite reads app configs: keep `.ts` extensions.
import type { ConfigEnv, Plugin, UserConfig } from 'vite'
import type { AppName } from './apps.ts'
import process from 'node:process'
import { fileURLToPath, URL } from 'node:url'
import { loadEnv } from 'vite'
import { APPS } from './apps.ts'

/** Root of the monorepo: the single .env lives here. */
export const ROOT_DIR = fileURLToPath(new URL('../../..', import.meta.url))

/** Only PUBLIC_* variables are exposed to browser bundles. */
export const PUBLIC_ENV_PREFIX = 'PUBLIC_'

/** Root .env merged with process env, `${VAR}` references expanded. */
export function rootEnv(mode = process.env.NODE_ENV ?? 'development'): Record<string, string> {
  return { ...loadEnv(mode, ROOT_DIR, ''), ...(process.env as Record<string, string>) }
}

/** Local port of an app from `<APP>_PORT`. Fails loudly when it is not set. */
export function appPort(app: AppName, env: Record<string, string> = rootEnv()): number {
  const key = `${APPS[app]}_PORT`
  const port = Number(env[key])
  if (!Number.isInteger(port) || port <= 0)
    throw new Error(`${key} is not set: copy .env.example to .env (mise run setup)`)
  return port
}

/**
 * Shared Vite settings for a frontend app: root .env, PUBLIC_ prefix and
 * `localhost:<APP>_PORT` for both dev and preview servers. Builds and unit
 * tests do not listen on a port, so they do not require it (Docker builds
 * run without a .env).
 */
export function appViteConfig(app: AppName, { command, mode }: ConfigEnv): UserConfig {
  const config: UserConfig = {
    envDir: ROOT_DIR,
    envPrefix: PUBLIC_ENV_PREFIX,
    // `mise run up` multiplexes the logs of every app into one terminal.
    clearScreen: false,
    plugins: [runtimeEnvStub()],
  }
  if (command === 'serve' && !process.env.VITEST) {
    const port = appPort(app, rootEnv(mode))
    config.server = { host: 'localhost', port, strictPort: true }
    config.preview = { host: 'localhost', port, strictPort: true }
  }
  return config
}

/**
 * Serves and emits an empty `/env.js` so the page loads cleanly in dev and in
 * `vite preview`; values then fall back to build-time PUBLIC_* variables.
 * In containers Caddy replaces it with infra/caddy/env.js rendered from the
 * container environment.
 */
function runtimeEnvStub(): Plugin {
  const source = 'window.__APPY_ENV__ = window.__APPY_ENV__ || {}\n'
  return {
    name: 'appy:runtime-env-stub',
    configureServer(server) {
      server.middlewares.use('/env.js', (_req, res) => {
        res.setHeader('Content-Type', 'text/javascript')
        res.end(source)
      })
    },
    generateBundle() {
      this.emitFile({ type: 'asset', fileName: 'env.js', source })
    },
  }
}
