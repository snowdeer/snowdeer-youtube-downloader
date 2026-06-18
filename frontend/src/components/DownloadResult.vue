<template>
  <div v-if="status === 'completed'" class="download-result">
    <a class="download-link" :href="fileUrl" download @click="handleClick">⬇ 파일 다운로드</a>
    <p v-if="error" class="download-error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { getFileDownloadUrl } from '../services/api'
import type { DownloadStatus } from '../types'

const props = defineProps<{ status: DownloadStatus | null; jobId: string }>()

const fileUrl = computed(() => getFileDownloadUrl(props.jobId))
const error = ref<string | null>(null)

async function handleClick(event: MouseEvent) {
  event.preventDefault()
  error.value = null

  const response = await fetch(fileUrl.value, { method: 'HEAD' })
  if (!response.ok) {
    try {
      const getResponse = await fetch(fileUrl.value)
      const data = await getResponse.json()
      error.value = data.detail ?? '파일을 다운로드할 수 없습니다'
    } catch {
      error.value = '파일을 다운로드할 수 없습니다'
    }
    return
  }

  // Content-Disposition: attachment 응답이므로 브라우저가 페이지 이동 없이 파일을 저장한다.
  window.location.href = fileUrl.value
}
</script>

<style scoped>
.download-result { margin-top: 16px; text-align: center; }
.download-link {
  display: inline-block;
  padding: 12px 24px;
  background: #2f855a;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
}
.download-link:hover { background: #276749; }
.download-error { margin-top: 8px; color: #c53030; font-size: 14px; }
</style>
