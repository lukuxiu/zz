<template>
  <div v-if="question" class="q-modal-backdrop" @click.self="$emit('close')">
    <div class="q-modal-container" role="dialog" aria-modal="true">
      <!-- 弹窗顶栏 -->
      <div class="q-modal-header">
        <div class="q-header-badges">
          <span :class="['q-source-tag', question.sourceType === '真题' ? 'tag-true' : 'tag-mock']">
            {{ question.sourceType === '真题' ? '🔴 历年真题' : '🔵 名师模拟题' }}
          </span>
          <span class="q-label-tag">{{ question.label }}</span>
          <span class="q-kind-tag">{{ question.kind }}</span>
        </div>
        <button class="q-close-btn" @click="$emit('close')" aria-label="关闭">✕</button>
      </div>

      <!-- 题目主体 -->
      <div class="q-modal-body">
        <!-- 题干 -->
        <div class="q-stem-text">
          <span class="q-num-prefix" v-if="currentIndex !== undefined">({{ currentIndex + 1 }}/{{ totalCount }})</span>
          {{ question.stem }}
        </div>

        <!-- 选项列表 -->
        <div class="q-options-list">
          <div
            v-for="opt in formattedOptions"
            :key="opt.letter"
            :class="[
              'q-option-item',
              {
                selected: selectedOptions.has(opt.letter),
                correct: hasSubmitted && isOptionCorrect(opt.letter),
                wrong: hasSubmitted && selectedOptions.has(opt.letter) && !isOptionCorrect(opt.letter)
              }
            ]"
            @click="handleOptionClick(opt.letter)"
          >
            <div class="q-opt-letter-box">
              <span class="q-letter">{{ opt.letter }}</span>
            </div>
            <div class="q-opt-content">{{ opt.text }}</div>
            <div v-if="hasSubmitted" class="q-opt-feedback-icon">
              <span v-if="isOptionCorrect(opt.letter)" class="icon-right">✓ 正确</span>
              <span v-else-if="selectedOptions.has(opt.letter)" class="icon-wrong">✗ 你的选择</span>
            </div>
          </div>
        </div>

        <!-- 提交与重做栏 -->
        <div class="q-action-bar">
          <button 
            v-if="!hasSubmitted"
            class="q-submit-btn" 
            :disabled="selectedOptions.size === 0"
            @click="submitAnswer"
          >
            确认提交答案
          </button>
          <div v-else class="q-submitted-actions">
            <div :class="['q-result-banner', isCorrect ? 'result-right' : 'result-wrong']">
              <span class="result-icon">{{ isCorrect ? '🎉' : '⚠️' }}</span>
              <span class="result-text">
                {{ isCorrect ? '回答正确！' : `回答错误，正确答案是：${normalizedCorrectAnswer}` }}
              </span>
            </div>
            <button class="q-retry-btn" @click="resetQuestion">重做本题</button>
          </div>
        </div>

        <!-- 答案解析 (提交后展示) -->
        <div v-if="hasSubmitted && question.explanation" class="q-explanation-card">
          <div class="q-exp-title">📖 答案与详细解析</div>
          <div class="q-exp-content">{{ question.explanation }}</div>
        </div>

        <!-- 关联考点归属 -->
        <div v-if="card" class="q-linked-kp-box">
          <span class="q-linked-tip">📌 考点归属：</span>
          <span class="q-linked-name">考点 {{ card.sourceId || card.id }} · {{ card.title }}</span>
        </div>
      </div>

      <!-- 弹窗底栏导航 -->
      <div class="q-modal-footer">
        <div class="q-footer-nav">
          <button 
            class="q-nav-step-btn" 
            :disabled="currentIndex <= 0"
            @click="$emit('prev')"
          >
            ← 上一题
          </button>
          <span class="q-footer-counter" v-if="totalCount > 1">
            {{ currentIndex + 1 }} / {{ totalCount }}
          </span>
          <button 
            class="q-nav-step-btn" 
            :disabled="currentIndex >= totalCount - 1"
            @click="$emit('next')"
          >
            下一题 →
          </button>
        </div>
        <button class="q-footer-done-btn" @click="$emit('close')">完成 / 返回卡片</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  question: { type: Object, default: null },
  card: { type: Object, default: null },
  currentIndex: { type: Number, default: 0 },
  totalCount: { type: Number, default: 1 }
})

const emit = defineEmits(['close', 'prev', 'next', 'record-answer'])

const selectedOptions = ref(new Set())
const hasSubmitted = ref(false)
const isCorrect = ref(false)

const isMultiChoice = computed(() => {
  if (!props.question) return false
  return props.question.kind?.includes('多项') || props.question.type === 'multi'
})

const normalizedCorrectAnswer = computed(() => {
  if (!props.question?.answer) return ''
  if (Array.isArray(props.question.answer)) {
    return props.question.answer.join('')
  }
  return String(props.question.answer).toUpperCase()
})

const formattedOptions = computed(() => {
  if (!props.question?.options) return []
  if (Array.isArray(props.question.options)) {
    return props.question.options
  }
  // If options is object {'A': '...', 'B': '...'}
  return Object.keys(props.question.options).sort().map(letter => ({
    letter,
    text: props.question.options[letter]
  }))
})

// 监听题目切换，加载历史做题记录或重置
watch(() => props.question?.id, (newId) => {
  if (!newId) return
  hasSubmitted.value = false
  selectedOptions.value = new Set()

  try {
    const records = JSON.parse(localStorage.getItem('zhengz_question_records') || '{}')
    const rec = records[newId]
    if (rec) {
      hasSubmitted.value = true
      isCorrect.value = rec.status === 'right'
      if (rec.selected && Array.isArray(rec.selected)) {
        selectedOptions.value = new Set(rec.selected)
      }
    }
  } catch (e) {
    console.error('Failed to load question record:', e)
  }
}, { immediate: true })

function handleOptionClick(letter) {
  if (hasSubmitted.value) return // 提交后不可直接点选改答案，需点击重做
  if (isMultiChoice.value) {
    if (selectedOptions.value.has(letter)) {
      selectedOptions.value.delete(letter)
    } else {
      selectedOptions.value.add(letter)
    }
    // trigger reactivity
    selectedOptions.value = new Set(selectedOptions.value)
  } else {
    selectedOptions.value = new Set([letter])
  }
}

function isOptionCorrect(letter) {
  return normalizedCorrectAnswer.value.includes(letter)
}

function submitAnswer() {
  if (selectedOptions.value.size === 0) return

  const userAns = Array.from(selectedOptions.value).sort().join('')
  const correctAns = normalizedCorrectAnswer.value.split('').sort().join('')
  const correct = userAns === correctAns

  hasSubmitted.value = true
  isCorrect.value = correct

  // 记录到本地存储
  try {
    const records = JSON.parse(localStorage.getItem('zhengz_question_records') || '{}')
    records[props.question.id] = {
      status: correct ? 'right' : 'wrong',
      selected: Array.from(selectedOptions.value),
      answeredAt: Date.now()
    }
    localStorage.setItem('zhengz_question_records', JSON.stringify(records))
  } catch (e) {
    console.error('Failed to save question record:', e)
  }

  emit('record-answer', {
    questionId: props.question.id,
    isCorrect: correct
  })
}

function resetQuestion() {
  hasSubmitted.value = false
  selectedOptions.value = new Set()
}
</script>

<style scoped>
.q-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  animation: fadeIn 0.18s ease-out;
}

.q-modal-container {
  background: #ffffff;
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.q-modal-header {
  padding: 14px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.q-header-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.q-source-tag {
  font-size: 0.78em;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}

.tag-true {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.tag-mock {
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
}

.q-label-tag {
  font-size: 0.85em;
  font-weight: 700;
  color: #334155;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 6px;
}

.q-kind-tag {
  font-size: 0.8em;
  color: #64748b;
}

.q-close-btn {
  background: none;
  border: none;
  font-size: 1.2em;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.15s;
}

.q-close-btn:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.q-modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  -webkit-overflow-scrolling: touch;
}

.q-stem-text {
  font-size: 1.05em;
  line-height: 1.65;
  color: #1e293b;
  font-weight: 600;
}

.q-num-prefix {
  color: var(--primary-accent, #98521c);
  margin-right: 4px;
}

.q-options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.q-option-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}

.q-option-item:hover:not(.correct):not(.wrong) {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.q-option-item.selected:not(.correct):not(.wrong) {
  border-color: var(--primary-accent, #98521c);
  background: #fdf8f4;
}

.q-option-item.selected .q-opt-letter-box {
  background: var(--primary-accent, #98521c);
  color: #ffffff;
  border-color: var(--primary-accent, #98521c);
}

.q-opt-letter-box {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1.5px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.88em;
  font-weight: 700;
  color: #475569;
  flex-shrink: 0;
  transition: all 0.15s;
}

.q-opt-content {
  flex: 1;
  font-size: 0.95em;
  color: #334155;
  line-height: 1.5;
}

/* 判分后选项高亮 */
.q-option-item.correct {
  border-color: #22c55e;
  background: #f0fdf4;
}

.q-option-item.correct .q-opt-letter-box {
  background: #22c55e;
  border-color: #22c55e;
  color: #ffffff;
}

.q-option-item.wrong {
  border-color: #ef4444;
  background: #fef2f2;
}

.q-option-item.wrong .q-opt-letter-box {
  background: #ef4444;
  border-color: #ef4444;
  color: #ffffff;
}

.q-opt-feedback-icon {
  font-size: 0.8em;
  font-weight: 700;
}

.icon-right {
  color: #16a34a;
}

.icon-wrong {
  color: #dc2626;
}

/* 按钮操作区 */
.q-action-bar {
  margin-top: 4px;
}

.q-submit-btn {
  width: 100%;
  padding: 12px;
  background: var(--primary-accent, #98521c);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 1em;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
}

.q-submit-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  opacity: 0.7;
}

.q-submit-btn:not(:disabled):hover {
  opacity: 0.92;
}

.q-submitted-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.q-result-banner {
  padding: 12px 16px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95em;
  font-weight: 700;
}

.result-right {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.result-wrong {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.q-retry-btn {
  align-self: flex-end;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #475569;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.85em;
  font-weight: 600;
  cursor: pointer;
}

.q-retry-btn:hover {
  background: #e2e8f0;
}

/* 答案解析 */
.q-explanation-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid var(--primary-accent, #98521c);
  border-radius: 8px;
  padding: 14px 16px;
  font-size: 0.9em;
  line-height: 1.65;
  color: #334155;
  animation: fadeIn 0.2s ease-out;
}

.q-exp-title {
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}

.q-exp-content {
  white-space: pre-wrap;
}

/* 关联考点 */
.q-linked-kp-box {
  padding: 8px 12px;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 8px;
  font-size: 0.85em;
  color: #92400e;
}

.q-linked-name {
  font-weight: 700;
}

/* 弹窗底栏 */
.q-modal-footer {
  padding: 12px 20px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.q-footer-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.q-nav-step-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.85em;
  font-weight: 600;
  cursor: pointer;
}

.q-nav-step-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.q-nav-step-btn:not(:disabled):hover {
  background: #f1f5f9;
}

.q-footer-counter {
  font-size: 0.85em;
  color: #64748b;
  font-weight: 600;
}

.q-footer-done-btn {
  background: #ffffff;
  border: 1.5px solid var(--primary-accent, #98521c);
  color: var(--primary-accent, #98521c);
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 0.88em;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}

.q-footer-done-btn:hover {
  background: var(--primary-accent, #98521c);
  color: #ffffff;
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes slideUpSheet {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

/* 手机端底部抽屉式 (Bottom Sheet) 深度优化 */
@media (max-width: 768px) {
  .q-modal-backdrop {
    align-items: flex-end;
    padding: 0;
  }
  .q-modal-container {
    max-width: 100%;
    max-height: 88vh;
    max-height: 88dvh;
    border-radius: 18px 18px 0 0;
    border-bottom: none;
    animation: slideUpSheet 0.22s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .q-modal-header {
    padding: 12px 14px;
  }
  .q-header-badges {
    gap: 6px;
  }
  .q-source-tag, .q-label-tag, .q-kind-tag {
    font-size: 12px;
  }
  .q-modal-body {
    padding: 14px;
    gap: 12px;
  }
  .q-stem-text {
    font-size: 0.98em;
    line-height: 1.6;
  }
  .q-options-list {
    gap: 8px;
  }
  .q-option-item {
    padding: 10px 12px;
    gap: 10px;
  }
  .q-opt-letter-box {
    width: 26px;
    height: 26px;
    font-size: 0.82em;
  }
  .q-opt-content {
    font-size: 0.92em;
    line-height: 1.45;
  }
  .q-submit-btn {
    padding: 11px;
    font-size: 0.95em;
  }
  .q-explanation-card {
    padding: 12px;
    font-size: 0.88em;
  }
  .q-modal-footer {
    padding: 10px 14px calc(12px + env(safe-area-inset-bottom, 10px));
    gap: 8px;
    flex-wrap: nowrap;
  }
  .q-footer-nav {
    gap: 6px;
  }
  .q-nav-step-btn {
    padding: 6px 10px;
    font-size: 12px;
    white-space: nowrap;
  }
  .q-footer-counter {
    font-size: 12px;
    white-space: nowrap;
  }
  .q-footer-done-btn {
    padding: 6px 12px;
    font-size: 12px;
    white-space: nowrap;
  }
}
</style>
