<template>
  <div class="url-input">
    <form @submit.prevent="handleSubmit">
      <div class="input-row">
        <input
          v-model="inputUrl"
          type="text"
          placeholder="유튜브 URL을 입력하세요 (예: https://www.youtube.com/watch?v=...)"
          class="url-field"
          :disabled="disabled"
        />
        <button type="submit" class="submit-btn" :disabled="disabled">조회</button>
      </div>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

withDefaults(defineProps<{ disabled?: boolean }>(), { disabled: false })
const emit = defineEmits<{ submit: [url: string] }>()

const inputUrl = ref('')
const errorMessage = ref('')

const YOUTUBE_PATTERN = /https:\/\/(www\.)?youtube\.com\/watch\?v=|https:\/\/youtu\.be\//

function handleSubmit() {
  errorMessage.value = ''
  if (!inputUrl.value.trim()) {
    errorMessage.value = 'URL을 입력해 주세요'
    return
  }
  if (!YOUTUBE_PATTERN.test(inputUrl.value)) {
    errorMessage.value = '유효한 유튜브 URL을 입력해 주세요'
    return
  }
  emit('submit', inputUrl.value.trim())
}
</script>

<style scoped>
.url-input { width: 100%; }
.input-row { display: flex; gap: 8px; }
.url-field { flex: 1; padding: 10px 14px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; }
.submit-btn { padding: 10px 20px; background: #ff0000; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.error-message { color: #e53e3e; font-size: 13px; margin-top: 6px; }
</style>
