import { afterEach, describe, expect, it } from 'vitest'
import { appLink, appUrl } from './index'

describe('appUrl', () => {
  afterEach(() => {
    delete window.__APPY_ENV__
  })

  it('prefers runtime config and strips the trailing slash', () => {
    window.__APPY_ENV__ = { PUBLIC_WEB_URL: 'https://app.example.com/' }
    expect(appUrl('web')).toBe('https://app.example.com')
  })

  it('ignores unrendered Caddy placeholders', () => {
    window.__APPY_ENV__ = { PUBLIC_WEB_URL: '{{env `PUBLIC_WEB_URL`}}' }
    expect(appUrl('web')).toBe(import.meta.env.PUBLIC_WEB_URL?.replace(/\/+$/, ''))
  })

  it('builds cross-app links with query parameters', () => {
    window.__APPY_ENV__ = {
      PUBLIC_WEB_URL: 'http://localhost:5173',
      PUBLIC_LANDING_URL: 'http://localhost:5174',
    }
    expect(appLink('web', 'login', { redirect: appLink('landing') })).toBe(
      'http://localhost:5173/login?redirect=http%3A%2F%2Flocalhost%3A5174%2F',
    )
  })
})
