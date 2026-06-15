import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import UrlInput from '../../src/components/UrlInput.vue'

describe('UrlInput', () => {
  it('renders URL input field', () => {
    const wrapper = mount(UrlInput)
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
  })

  it('emits submit event with URL when valid YouTube URL is entered', async () => {
    const wrapper = mount(UrlInput)
    await wrapper.find('input[type="text"]').setValue('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('submit')).toBeTruthy()
    expect(wrapper.emitted('submit')![0]).toEqual(['https://www.youtube.com/watch?v=dQw4w9WgXcQ'])
  })

  it('shows error message when invalid URL is submitted', async () => {
    const wrapper = mount(UrlInput)
    await wrapper.find('input[type="text"]').setValue('https://www.google.com')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('.error-message').exists()).toBe(true)
    expect(wrapper.find('.error-message').text()).toContain('유튜브 URL')
    expect(wrapper.emitted('submit')).toBeFalsy()
  })

  it('shows error when URL is empty on submit', async () => {
    const wrapper = mount(UrlInput)
    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })
})
