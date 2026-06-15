<template>
  <div class="format-selector">
    <label class="label">저장 형식 선택</label>
    <div class="options">
      <label
        v-for="opt in options"
        :key="opt.value"
        class="option"
        :class="{ active: modelValue === opt.value }"
      >
        <input
          type="radio"
          :value="opt.value"
          :checked="modelValue === opt.value"
          :disabled="disabled"
          @change="$emit('update:modelValue', opt.value)"
        />
        <span class="option-label">{{ opt.label }}</span>
        <span class="option-desc">{{ opt.desc }}</span>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DownloadFormat } from '../types'

withDefaults(
  defineProps<{ modelValue: DownloadFormat; disabled?: boolean }>(),
  { disabled: false }
)
defineEmits<{ 'update:modelValue': [value: DownloadFormat] }>()

const options = [
  { value: 'mp4' as DownloadFormat, label: 'MP4', desc: '동영상 (최고 화질)' },
  { value: 'mp3' as DownloadFormat, label: 'MP3', desc: '음원 추출 (192kbps)' },
]
</script>

<style scoped>
.format-selector { margin-top: 16px; }
.label { font-size: 14px; font-weight: 600; display: block; margin-bottom: 8px; }
.options { display: flex; gap: 12px; }
.option { display: flex; align-items: center; gap: 8px; padding: 10px 16px; border: 2px solid #e2e8f0; border-radius: 8px; cursor: pointer; transition: border-color 0.2s; }
.option.active { border-color: #ff0000; background: #fff5f5; }
.option input { accent-color: #ff0000; }
.option-label { font-weight: 600; font-size: 14px; }
.option-desc { font-size: 12px; color: #718096; }
</style>
