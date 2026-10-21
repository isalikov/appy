/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly PUBLIC_LANDING_URL?: string
  readonly PUBLIC_WEB_URL?: string
  readonly PUBLIC_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
