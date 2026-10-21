/**
 * Registry of every app in the monorepo. Each app runs on
 * http://localhost:<APP>_PORT locally and is reachable by browsers at
 * PUBLIC_<APP>_URL (both come from the root .env).
 *
 * Adding an app: add it here, to .env.example and to infra/caddy/env.js.
 */
export const APPS = {
  landing: 'LANDING',
  web: 'WEB',
  api: 'API',
} as const

export type AppName = keyof typeof APPS
export type AppEnvKey = (typeof APPS)[AppName]
export type PublicUrlKey = `PUBLIC_${AppEnvKey}_URL`

export function publicUrlKey(app: AppName): PublicUrlKey {
  return `PUBLIC_${APPS[app]}_URL`
}
