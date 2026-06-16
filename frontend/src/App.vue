<template>
  <div class="app">
    <header class="header">
      <h1>🎬 유튜브 동영상 다운로더</h1>
    </header>

    <main class="main">
      <section class="card">
        <UrlInput
          :disabled="isDownloading"
          @submit="handleUrlSubmit"
        />

        <div v-if="store.isLoading" class="loading">영상 정보를 불러오는 중...</div>

        <div v-if="store.error && !store.isLoading" class="error-banner">
          {{ store.error }}
        </div>

        <VideoPreview v-if="store.videoInfo" :video-info="store.videoInfo" />

        <template v-if="store.videoInfo && !isDownloading">
          <FormatSelector v-model="store.format" />
          <button class="download-btn" @click="handleDownload">⬇ 다운로드 시작</button>
        </template>

        <ProgressBar
          v-if="store.status"
          :progress="store.progress"
          :status="store.status"
          :error-message="store.status === 'failed' ? (store.error ?? undefined) : undefined"
        />

        <DownloadResult v-if="store.jobId" :status="store.status" :job-id="store.jobId" />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DownloadResult from './components/DownloadResult.vue'
import FormatSelector from './components/FormatSelector.vue'
import ProgressBar from './components/ProgressBar.vue'
import UrlInput from './components/UrlInput.vue'
import VideoPreview from './components/VideoPreview.vue'
import { useDownloadStore } from './stores/downloadStore'

const store = useDownloadStore()

const isDownloading = computed(() =>
  store.status === 'pending' || store.status === 'downloading' || store.status === 'processing',
)

async function handleUrlSubmit(url: string) {
  await store.fetchVideoInfo(url)
}

async function handleDownload() {
  await store.startDownloadJob()
}
</script>

<style scoped>
.app { max-width: 720px; margin: 0 auto; padding: 24px 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.header { text-align: center; margin-bottom: 32px; }
.header h1 { font-size: 28px; color: #1a1a1a; }
.card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.loading { color: #718096; font-size: 14px; margin-top: 12px; }
.error-banner { background: #fff5f5; border: 1px solid #fc8181; color: #c53030; padding: 10px 14px; border-radius: 6px; margin-top: 12px; font-size: 14px; }
.download-btn { width: 100%; margin-top: 16px; padding: 12px; background: #ff0000; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.download-btn:hover { background: #cc0000; }
</style>
