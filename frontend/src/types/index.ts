export type DownloadFormat = 'mp4' | 'mp3'

export type DownloadStatus =
  | 'pending'
  | 'downloading'
  | 'processing'
  | 'completed'
  | 'failed'

export interface VideoInfo {
  url: string
  title: string
  thumbnail_url?: string
  duration_seconds?: number
  channel?: string
}

export interface DownloadJob {
  job_id: string
  url: string
  format: DownloadFormat
  status: DownloadStatus
  progress_percent: number
  file_name?: string
  error_message?: string
  created_at: string
}

export interface DownloadProgress {
  job_id: string
  status: DownloadStatus
  progress_percent: number
  message?: string
}
