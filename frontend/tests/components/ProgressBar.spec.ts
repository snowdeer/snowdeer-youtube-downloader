import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ProgressBar from '../../src/components/ProgressBar.vue'

describe('ProgressBar', () => {
  it('renders progress percentage', () => {
    const wrapper = mount(ProgressBar, { props: { progress: 45, status: 'downloading' } })
    expect(wrapper.find('.percent').text()).toBe('45%')
  })

  it('shows "다운로드 중" label when status is downloading', () => {
    const wrapper = mount(ProgressBar, { props: { progress: 50, status: 'downloading' } })
    expect(wrapper.find('.status-label').text()).toContain('다운로드 중')
  })

  it('shows "완료" label when status is completed', () => {
    const wrapper = mount(ProgressBar, { props: { progress: 100, status: 'completed' } })
    expect(wrapper.find('.status-label').text()).toContain('완료')
  })

  it('shows "실패" label when status is failed', () => {
    const wrapper = mount(ProgressBar, { props: { progress: 0, status: 'failed' } })
    expect(wrapper.find('.status-label').text()).toContain('실패')
  })

  it('renders bar fill with correct width', () => {
    const wrapper = mount(ProgressBar, { props: { progress: 75, status: 'downloading' } })
    const fill = wrapper.find('.bar-fill')
    expect((fill.element as HTMLElement).style.width).toBe('75%')
  })

  it('shows error message when provided', () => {
    const wrapper = mount(ProgressBar, {
      props: { progress: 0, status: 'failed', errorMessage: '네트워크 오류' },
    })
    expect(wrapper.find('.error-message').text()).toBe('네트워크 오류')
  })

  it('does not render when status is null', () => {
    const wrapper = mount(ProgressBar, { props: { progress: 0, status: null } })
    expect(wrapper.find('.progress-container').exists()).toBe(false)
  })
})
