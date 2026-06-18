import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import DownloadResult from '../../src/components/DownloadResult.vue'

describe('DownloadResult', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders a download link when status is completed', () => {
    const wrapper = mount(DownloadResult, {
      props: { status: 'completed', jobId: 'test-job-id' },
    })
    const link = wrapper.find('a.download-link')
    expect(link.exists()).toBe(true)
    expect(link.attributes('href')).toBe('/api/download/test-job-id/file')
  })

  it('does not render when status is not completed', () => {
    const wrapper = mount(DownloadResult, {
      props: { status: 'downloading', jobId: 'test-job-id' },
    })
    expect(wrapper.find('a.download-link').exists()).toBe(false)
  })

  it('does not render when status is null', () => {
    const wrapper = mount(DownloadResult, {
      props: { status: null, jobId: 'test-job-id' },
    })
    expect(wrapper.find('a.download-link').exists()).toBe(false)
  })

  it('shows an error message instead of downloading when the file is not available', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ detail: '다운로드 파일을 찾을 수 없습니다' }),
    })
    vi.stubGlobal('fetch', fetchMock)
    const locationMock = { href: '' }
    vi.stubGlobal('location', locationMock)

    const wrapper = mount(DownloadResult, {
      props: { status: 'completed', jobId: 'test-job-id' },
    })
    await wrapper.find('a.download-link').trigger('click')
    await vi.waitFor(() => {
      expect(wrapper.find('.download-error').exists()).toBe(true)
    })

    expect(wrapper.find('.download-error').text()).toBe('다운로드 파일을 찾을 수 없습니다')
    expect(fetchMock).toHaveBeenCalledWith('/api/download/test-job-id/file', { method: 'HEAD' })
    expect(locationMock.href).toBe('')
  })

  it('navigates to the file URL to trigger browser download when the file is available', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true })
    vi.stubGlobal('fetch', fetchMock)
    const locationMock = { href: '' }
    vi.stubGlobal('location', locationMock)

    const wrapper = mount(DownloadResult, {
      props: { status: 'completed', jobId: 'test-job-id' },
    })
    await wrapper.find('a.download-link').trigger('click')
    await vi.waitFor(() => {
      expect(locationMock.href).toBe('/api/download/test-job-id/file')
    })

    expect(wrapper.find('.download-error').exists()).toBe(false)
  })
})
