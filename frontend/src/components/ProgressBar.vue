<template>
  <div v-if="status" class="progress-container">
    <div class="status-row">
      <span class="status-label">{{ statusLabel }}</span>
      <span class="percent">{{ progress }}%</span>
    </div>
    <div class="bar-track">
      <div
        class="bar-fill"
        :style="{ width: `${progress}%` }"
        :class="barClass"
      />
    </div>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DownloadStatus } from '../types'

const props = defineProps<{
  progress: number
  status: DownloadStatus | null
  errorMessage?: string
}>()

const statusLabel = computed(() => {
  switch (props.status) {
    case 'pending': return '대기 중...'
    case 'downloading': return '다운로드 중...'
    case 'processing': return '변환 중...'
    case 'completed': return '✅ 완료'
    case 'failed': return '❌ 실패'
    default: return ''
  }
})

const barClass = computed(() => ({
  'bar-completed': props.status === 'completed',
  'bar-failed': props.status === 'failed',
}))
</script>

<style scoped>
.progress-container { margin-top: 16px; }
.status-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px; }
.status-label { font-weight: 500; }
.percent { color: #555; }
.bar-track { height: 10px; background: #e2e8f0; border-radius: 9999px; overflow: hidden; }
.bar-fill { height: 100%; background: #ff0000; border-radius: 9999px; transition: width 0.4s ease; }
.bar-completed { background: #38a169; }
.bar-failed { background: #e53e3e; }
.error-message { color: #e53e3e; font-size: 13px; margin-top: 8px; }
</style>
