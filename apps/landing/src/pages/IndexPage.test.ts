import { createHead } from '@unhead/vue/client'
import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'
import IndexPage from './IndexPage.vue'

describe('indexPage', () => {
  afterEach(() => {
    delete window.__APPY_ENV__
  })

  it('renders the headline and links to the web app', () => {
    window.__APPY_ENV__ = { PUBLIC_WEB_URL: 'https://app.example.com' }
    const wrapper = mount(IndexPage, { global: { plugins: [createHead()] } })

    expect(wrapper.get('h1').text()).toBe('Hello from Appy')
    expect(wrapper.get('a').attributes('href')).toBe('https://app.example.com/')
  })
})
