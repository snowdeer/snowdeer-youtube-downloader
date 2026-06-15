import axios from 'axios'
import type { DownloadJob, DownloadProgress, VideoInfo } from '../types'

const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export async function getVideoInfo(url: string): Promise<VideoInfo> {
  const { data } = await apiClient.post<VideoInfo>('/video/info', { url })
  return data
}

export async function startDownload(url: string, format: string): Promise<DownloadJob> {
  const { data } = await apiClient.post<DownloadJob>('/download/start', { url, format })
  return data
}

export async function getDownloadStatus(jobId: string): Promise<DownloadJob> {
  const { data } = await apiClient.get<DownloadJob>(`/download/${jobId}/status`)
  return data
}

export function createProgressStream(
  jobId: string,
  onProgress: (progress: DownloadProgress) => void,
  onError: (error: Event) => void,
): EventSource {
  const eventSource = new EventSource(`/api/download/${jobId}/progress`)
  eventSource.onmessage = (event) => {
    const progress: DownloadProgress = JSON.parse(event.data)
    onProgress(progress)
  }
  eventSource.onerror = onError
  return eventSource
}
