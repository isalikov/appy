import type { paths } from './schema'
import createClient from 'openapi-fetch'

export type { components, paths } from './schema'

/**
 * Typed client for the Appy API. Types are generated from the API's OpenAPI
 * schema: run `mise run api:openapi` after changing any route or model.
 */
export function createApiClient(baseUrl: string, init: { headers?: HeadersInit } = {}) {
  return createClient<paths>({ baseUrl, ...init })
}

export type ApiClient = ReturnType<typeof createApiClient>
