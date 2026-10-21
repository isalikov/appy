import type { AppName, PublicUrlKey } from './apps'
import { APPS, publicUrlKey } from './apps'

export { type AppName, APPS, publicUrlKey, type PublicUrlKey } from './apps'

type PublicEnvValues = Partial<Record<PublicUrlKey, string>>

declare global {
  interface Window {
    /** Runtime config rendered by Caddy into /env.js inside the container. */
    __APPY_ENV__?: PublicEnvValues
  }
}

// Build-time values (Vite inlines PUBLIC_* from the root .env). Listed
// explicitly because Vite only replaces static `import.meta.env.X` accesses.
const BUILD_TIME: Record<PublicUrlKey, string | undefined> = {
  PUBLIC_LANDING_URL: import.meta.env.PUBLIC_LANDING_URL,
  PUBLIC_WEB_URL: import.meta.env.PUBLIC_WEB_URL,
  PUBLIC_API_URL: import.meta.env.PUBLIC_API_URL,
}

function usable(value: string | undefined): value is string {
  // An unrendered Caddy template ("{{env ...}}") means "not configured".
  return !!value && !value.includes('{{')
}

/**
 * Public URL of an app, without a trailing slash. Runtime config wins over
 * build-time values so one image can be promoted across environments.
 */
export function appUrl(app: AppName): string {
  const key = publicUrlKey(app)
  const runtime = typeof window === 'undefined' ? undefined : window.__APPY_ENV__?.[key]
  // During SSG pre-rendering inside Docker the build-time value is the Caddy
  // placeholder itself; it ends up in the HTML and Caddy renders it per request.
  const value = usable(runtime) ? runtime : BUILD_TIME[key]
  if (!value)
    throw new Error(`${key} is not configured (see .env.example)`)
  return value.replace(/\/+$/, '')
}

/**
 * Absolute link into another app, e.g. the landing's "Log in" button:
 * `appLink('web', '/login', { redirect: appLink('web', '/') })`.
 */
export function appLink(app: AppName, path = '/', query: Record<string, string> = {}): string {
  const search = new URLSearchParams(query).toString()
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${appUrl(app)}${normalized}${search ? `?${search}` : ''}`
}

/** All public app URLs, e.g. for diagnostics pages. */
export function appUrls(): Record<AppName, string> {
  return Object.fromEntries(
    (Object.keys(APPS) as AppName[]).map(app => [app, appUrl(app)]),
  ) as Record<AppName, string>
}
