import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createProgressStream, getVideoInfo, startDownload } from '../services/api'
import type { DownloadFormat, DownloadProgress, DownloadStatus, VideoInfo } from '../types'

export const useDownloadStore = defineStore('download', () => {
  const url = ref('')
  const format = ref<DownloadFormat>('mp4')
  const videoInfo = ref<VideoInfo | null>(null)
  const jobId = ref<string | null>(null)
  const progress = ref(0)
  const status = ref<DownloadStatus | null>(null)
  const error = ref<string | null>(null)
  const isLoading = ref(false)

  let eventSource: EventSource | null = null

  function reset() {
    videoInfo.value = null
    jobId.value = null
    progress.value = 0
    status.value = null
    error.value = null
    isLoading.value = false
    closeProgressStream()
  }

  function closeProgressStream() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
  }

  async function fetchVideoInfo(inputUrl: string) {
    reset()
    url.value = inputUrl
    isLoading.value = true
    try {
      videoInfo.value = await getVideoInfo(inputUrl)
    } catch (err: unknown) {
      error.value = getErrorMessage(err)
    } finally {
      isLoading.value = false
    }
  }

  async function startDownloadJob() {
    if (!url.value) return
    error.value = null
    status.value = 'pending'
    try {
      const job = await startDownload(url.value, format.value)
      jobId.value = job.job_id
      subscribeToProgress(job.job_id)
    } catch (err: unknown) {
      error.value = getErrorMessage(err)
      status.value = 'failed'
    }
  }

  function subscribeToProgress(id: string) {
    closeProgressStream()
    eventSource = createProgressStream(
      id,
      (prog: DownloadProgress) => {
        progress.value = prog.progress_percent
        status.value = prog.status
        if (prog.status === 'completed' || prog.status === 'failed') {
          if (prog.status === 'failed' && prog.message) {
            error.value = prog.message
          }
          closeProgressStream()
        }
      },
      () => {
        if (status.value !== 'completed') {
          error.value = '진행률 스트림 연결 오류'
          closeProgressStream()
        }
      },
    )
  }

  function getErrorMessage(err: unknown): string {
    if (err && typeof err === 'object' && 'response' in err) {
      const res = (err as { response?: { data?: { detail?: string } } }).response
      return res?.data?.detail ?? '알 수 없는 오류가 발생했습니다'
    }
    return '알 수 없는 오류가 발생했습니다'
  }

  return {
    url,
    format,
    videoInfo,
    jobId,
    progress,
    status,
    error,
    isLoading,
    fetchVideoInfo,
    startDownloadJob,
    subscribeToProgress,
    reset,
  }
})
