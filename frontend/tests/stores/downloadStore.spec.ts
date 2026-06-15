import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../../src/services/api', () => ({
  getVideoInfo: vi.fn(),
  startDownload: vi.fn(),
  createProgressStream: vi.fn(),
}))

describe('downloadStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default values', async () => {
    const { useDownloadStore } = await import('../../src/stores/downloadStore')
    const store = useDownloadStore()
    expect(store.url).toBe('')
    expect(store.format).toBe('mp4')
    expect(store.videoInfo).toBeNull()
    expect(store.progress).toBe(0)
    expect(store.status).toBeNull()
    expect(store.error).toBeNull()
  })

  it('fetchVideoInfo updates videoInfo on success', async () => {
    const { getVideoInfo } = await import('../../src/services/api')
    const mockInfo = {
      url: 'https://www.youtube.com/watch?v=test',
      title: 'Test Video',
      thumbnail_url: 'https://example.com/thumb.jpg',
      duration_seconds: 120,
      channel: 'Test Channel',
    }
    vi.mocked(getVideoInfo).mockResolvedValue(mockInfo)

    const { useDownloadStore } = await import('../../src/stores/downloadStore')
    const store = useDownloadStore()
    await store.fetchVideoInfo('https://www.youtube.com/watch?v=test')

    expect(store.videoInfo).toEqual(mockInfo)
    expect(store.error).toBeNull()
  })

  it('fetchVideoInfo sets error on failure', async () => {
    const { getVideoInfo } = await import('../../src/services/api')
    vi.mocked(getVideoInfo).mockRejectedValue({
      response: { data: { detail: '유효한 유튜브 URL이 아닙니다' } },
    })

    const { useDownloadStore } = await import('../../src/stores/downloadStore')
    const store = useDownloadStore()
    await store.fetchVideoInfo('https://www.google.com')

    expect(store.videoInfo).toBeNull()
    expect(store.error).toBe('유효한 유튜브 URL이 아닙니다')
  })

  it('startDownloadJob calls startDownload and subscribes to progress', async () => {
    const { startDownload, createProgressStream } = await import('../../src/services/api')
    const mockJob = {
      job_id: 'test-job-123',
      url: 'https://www.youtube.com/watch?v=test',
      format: 'mp4' as const,
      status: 'pending' as const,
      progress_percent: 0,
      created_at: '2026-06-15T00:00:00Z',
    }
    vi.mocked(startDownload).mockResolvedValue(mockJob)
    const mockEventSource = { close: vi.fn(), onmessage: null, onerror: null }
    vi.mocked(createProgressStream).mockReturnValue(mockEventSource as unknown as EventSource)

    const { useDownloadStore } = await import('../../src/stores/downloadStore')
    const store = useDownloadStore()
    store.url = 'https://www.youtube.com/watch?v=test'
    await store.startDownloadJob()

    expect(startDownload).toHaveBeenCalledWith('https://www.youtube.com/watch?v=test', 'mp4')
    expect(store.jobId).toBe('test-job-123')
    expect(createProgressStream).toHaveBeenCalled()
  })
})
