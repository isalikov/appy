import { createApiClient } from '@appy/api-client'
import { appUrl } from '@appy/config'

// The API is called directly at PUBLIC_API_URL; it allows this origin via CORS.
export const api = createApiClient(appUrl('api'))
