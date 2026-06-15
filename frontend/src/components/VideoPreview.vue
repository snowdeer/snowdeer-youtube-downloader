<template>
  <div v-if="videoInfo" class="video-preview">
    <img
      v-if="videoInfo.thumbnail_url"
      :src="videoInfo.thumbnail_url"
      :alt="videoInfo.title"
      class="thumbnail"
    />
    <div class="info">
      <h3 class="title">{{ videoInfo.title }}</h3>
      <p v-if="videoInfo.channel" class="channel">채널: {{ videoInfo.channel }}</p>
      <p v-if="videoInfo.duration_seconds" class="duration">
        재생시간: {{ formatDuration(videoInfo.duration_seconds) }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { VideoInfo } from '../types'

defineProps<{ videoInfo: VideoInfo | null }>()

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}분 ${s}초`
}
</script>

<style scoped>
.video-preview { display: flex; gap: 16px; padding: 16px; background: #f9f9f9; border-radius: 8px; margin-top: 16px; }
.thumbnail { width: 160px; height: 90px; object-fit: cover; border-radius: 4px; }
.info { flex: 1; }
.title { font-size: 16px; font-weight: 600; margin: 0 0 8px; }
.channel, .duration { font-size: 13px; color: #666; margin: 4px 0; }
</style>
