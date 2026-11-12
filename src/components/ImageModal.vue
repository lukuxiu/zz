<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title">
          <span>原书 PDF 裁切真迹对照 · [知识点 {{ card?.sourceId }}] {{ card?.title }}</span>
          <span class="modal-meta">PDF P{{ card?.sourcePage[0] }} (原书第 {{ card?.bookPage[0] }} 页)</span>
        </div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="modal-body">
        <img 
          :src="imageUrl" 
          :alt="card?.title" 
          class="preview-img" 
          @error="handleImgError"
        />
        <p v-if="imgError" class="error-msg">⚠️ 对应裁切图片加载失败: {{ imageUrl }}</p>
      </div>

      <div class="modal-footer">
        <span class="footer-hint">💡 建议对比原文排版、手写标记及原书真实颜色</span>
        <button class="btn-confirm" @click="$emit('close')">关闭预览</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  card: { type: Object, default: null }
})

defineEmits(['close'])

const imgError = ref(false)

watch(() => props.card, () => {
  imgError.value = false
})

const imageUrl = computed(() => {
  if (!props.card || !props.card.sourceImages || !props.card.sourceImages.length) {
    return ''
  }
  const rawPath = props.card.sourceImages[0].replace(/^[\\/]+/, '')
  // 支持绝对、相对以及以 ./ 开头的部署环境
  if (rawPath.startsWith('http') || rawPath.startsWith('data:')) {
    return rawPath
  }
  return '/' + rawPath
})

function handleImgError() {
  imgError.value = true
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 27, 24, 0.75);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  animation: fadeIn 0.15s ease;
}

.modal-dialog {
  background: #ffffff;
  border-radius: var(--radius-lg);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  background: var(--bg-beige);
  border-bottom: 1px solid var(--border-light);
}

.modal-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-weight: 700;
  font-size: 15px;
  color: var(--text-main);
}

.modal-meta {
  font-size: 12px;
  font-weight: normal;
  color: var(--text-muted);
}

.close-btn {
  background: transparent;
  font-size: 18px;
  color: var(--text-muted);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(0,0,0,0.06);
  color: var(--text-main);
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  text-align: center;
  background: #f4efe8;
}

.preview-img {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #e5ded2;
}

.error-msg {
  color: var(--danger-accent);
  margin-top: 10px;
  font-size: 13px;
}

.modal-footer {
  padding: 10px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-light);
  background: #fff;
}

.footer-hint {
  font-size: 12px;
  color: var(--text-muted);
}

.btn-confirm {
  background: var(--primary-accent);
  color: white;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
