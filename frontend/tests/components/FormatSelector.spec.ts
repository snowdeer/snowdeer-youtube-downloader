import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import FormatSelector from '../../src/components/FormatSelector.vue'

describe('FormatSelector', () => {
  it('renders mp4 and mp3 options', () => {
    const wrapper = mount(FormatSelector, { props: { modelValue: 'mp4' } })
    const labels = wrapper.findAll('.option-label').map((el) => el.text())
    expect(labels).toContain('MP4')
    expect(labels).toContain('MP3')
  })

  it('has mp4 selected by default when modelValue is mp4', () => {
    const wrapper = mount(FormatSelector, { props: { modelValue: 'mp4' } })
    const mp4Radio = wrapper.find('input[value="mp4"]')
    expect((mp4Radio.element as HTMLInputElement).checked).toBe(true)
  })

  it('emits update:modelValue when mp3 is selected', async () => {
    const wrapper = mount(FormatSelector, { props: { modelValue: 'mp4' } })
    await wrapper.find('input[value="mp3"]').trigger('change')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['mp3'])
  })

  it('disables inputs when disabled prop is true', () => {
    const wrapper = mount(FormatSelector, { props: { modelValue: 'mp4', disabled: true } })
    const radios = wrapper.findAll('input[type="radio"]')
    radios.forEach((r) => {
      expect((r.element as HTMLInputElement).disabled).toBe(true)
    })
  })
})
