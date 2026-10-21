import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import HomePage from './HomePage.vue'

describe('homePage', () => {
  it('greets the world', () => {
    const wrapper = mount(HomePage)
    expect(wrapper.get('h1').text()).toBe('Hello world')
  })
})
