// Runtime config for browser bundles, rendered by Caddy `templates` on every
// request from the container environment. Keep keys in sync with
// packages/config/src/apps.ts and .env.example.
window.__APPY_ENV__ = {
  PUBLIC_LANDING_URL: '{{env `PUBLIC_LANDING_URL`}}',
  PUBLIC_WEB_URL: '{{env `PUBLIC_WEB_URL`}}',
  PUBLIC_API_URL: '{{env `PUBLIC_API_URL`}}',
}
