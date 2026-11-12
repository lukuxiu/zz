<template>
  <div class="mock-view-container">
    <!-- 准备开始界面 -->
    <div v-if="mockState === 'idle'" class="mock-idle-card">
      <div class="idle-badge">⏱️ 限时实战模考</div>
      <h2 class="idle-title">全真真题限时模拟</h2>
      <p class="idle-desc">
        真实考场时间压力训练。按真实考研选择题标准计时，交卷后自动生成分析报告并归集错题。
      </p>

      <div class="mock-config-group">
        <div class="config-label">模考模式选择：</div>
        <div class="mode-cards-grid">
          <div 
            :class="['mode-card', { active: mockMode === 'random16' }]"
            @click="mockMode = 'random16'"
          >
            <div class="mode-header">🎲 随机 16 题综合模考</div>
            <p class="mode-sub">自动抽取 8 道单选题 + 8 道多选题，限时 25 分钟。</p>
          </div>

          <div 
            :class="['mode-card', { active: mockMode === 'byYear' }]"
            @click="mockMode = 'byYear'"
          >
            <div class="mode-header">📅 按真题年份专练</div>
            <p class="mode-sub">选取近十年某一年份的全部真题选择题进行专项限时演练。</p>
          </div>
        </div>

        <div v-if="mockMode === 'byYear'" class="year-selector-wrap">
          <label class="year-label">选择年份：</label>
          <div class="year-chips">
            <button 
              v-for="yr in availableYears" 
              :key="yr"
              :class="['yr-chip', { active: selectedYear === yr }]"
              @click="selectedYear = yr"
            >
              {{ yr }} ({{ getYearCount(yr) }}题)
            </button>
          </div>
        </div>
      </div>

      <button class="start-mock-btn" @click="startMock">
        🚀 开始限时模考
      </button>
    </div>

    <!-- 模考进行中界面 -->
    <div v-else-if="mockState === 'running'" class="mock-running-container">
      <!-- 顶部时间与交卷条 -->
      <div class="mock-timer-bar">
        <div class="timer-display" :class="{ 'timer-urgent': remainingSeconds < 300 }">
          <span class="timer-icon">⏱️</span>
          <span>剩余时间：<strong>{{ formatTime(remainingSeconds) }}</strong></span>
        </div>

        <div class="answered-summary">
          已答 {{ answeredCount }} / {{ mockPool.length }} 题
        </div>

        <button class="finish-btn" @click="handleConfirmFinish">
          📝 确认交卷
        </button>
      </div>

      <!-- 答题卡卡片快捷横条 -->
      <div class="mock-sheet-strip">
        <button 
          v-for="(q, idx) in mockPool" 
          :key="q.id"
          :class="[
            'sheet-dot', 
            { active: idx === currentIndex },
            { filled: (userAnswers[q.id] || []).length > 0 }
          ]"
          @click="currentIndex = idx"
        >
          {{ idx + 1 }}
        </button>
      </div>

      <!-- 当前试题 -->
      <div v-if="currentMockQuestion" class="mock-card-box">
        <div class="mock-question-header">
          <span class="q-badge">第 {{ currentIndex + 1 }} 题 ({{ currentMockQuestion.year }}.{{ currentMockQuestion.no }})</span>
          <span :class="['q-badge-type', currentMockQuestion.type]">
            {{ currentMockQuestion.type === 'single' ? '单选题' : '多选题' }}
          </span>
        </div>

        <div class="mock-stem">
          {{ currentMockQuestion.stem || '题干请参考下方高清真题图：' }}
        </div>

        <div v-if="currentMockQuestion.image" class="mock-img-wrap">
          <img :src="currentMockQuestion.image" class="mock-raw-img" />
        </div>

        <!-- 选项交互 -->
        <div class="mock-options-list">
          <div 
            v-for="optKey in ['A', 'B', 'C', 'D']" 
            :key="optKey"
            :class="[
              'mock-opt-item', 
              { selected: (userAnswers[currentMockQuestion.id] || []).includes(optKey) }
            ]"
            @click="toggleMockOption(currentMockQuestion.id, currentMockQuestion.type, optKey)"
          >
            <div class="opt-bubble">{{ optKey }}</div>
            <div class="opt-text">
              {{ currentMockQuestion.options[optKey] || `(选项 ${optKey} 见切图)` }}
            </div>
          </div>
        </div>

        <!-- 试卷底部导航 -->
        <div class="mock-nav-actions">
          <button class="mock-nav-btn" :disabled="currentIndex <= 0" @click="currentIndex--">
            ◀ 上一题
          </button>

          <span class="mock-curr-indicator">{{ currentIndex + 1 }} / {{ mockPool.length }}</span>

          <button class="mock-nav-btn" :disabled="currentIndex >= mockPool.length - 1" @click="currentIndex++">
            下一题 ▶
          </button>
        </div>
      </div>
    </div>

    <!-- 模考报告结果界面 -->
    <div v-else-if="mockState === 'finished'" class="mock-result-card">
      <div class="result-header">
        <div class="score-circle">
          <span class="score-num">{{ mockResult.score }}</span>
          <span class="score-total">/ 100 分</span>
        </div>
        <div class="result-headline">
          <h3>{{ mockResult.title }}</h3>
          <p class="result-sub">
            答对 {{ mockResult.correctCount }} 题 · 答错 {{ mockResult.wrongCount }} 题 · 正确率 <strong>{{ mockResult.accuracy }}%</strong>
          </p>
          <p class="time-spent">耗时：{{ formatTime(mockResult.timeSpent) }}</p>
        </div>
      </div>

      <div class="result-actions-row">
        <button class="action-restart-btn" @click="mockState = 'idle'">
          🔄 再练一套
        </button>
        <button class="action-export-btn" @click="$emit('switch-tab', 'mistakes')">
          📕 查看解题错题本
        </button>
      </div>

      <!-- 试题答卷明细清单 -->
      <div class="result-details-section">
        <h4 class="section-title">试卷作答详尽明细：</h4>
        <div class="review-questions-list">
          <div 
            v-for="(item, idx) in mockResult.items" 
            :key="item.q.id"
            :class="['review-item', item.isCorrect ? 'is-correct' : 'is-wrong']"
          >
            <div class="review-item-header">
              <span class="review-idx">第 {{ idx + 1 }} 题 ({{ item.q.year }}.{{ item.q.no }})</span>
              <span :class="['review-status', item.isCorrect ? 'text-green' : 'text-red']">
                {{ item.isCorrect ? '✓ 正确' : '✕ 错误' }}
              </span>
            </div>

            <div class="review-stem-short">{{ item.q.stem || '(图文题)' }}</div>

            <div class="review-ans-row">
              <span>您的作答：<strong>{{ item.userAns.join('') || '未作答' }}</strong></span>
              <span>正确答案：<strong class="correct-text">{{ item.q.answer.join('') }}</strong></span>
            </div>

            <div class="review-tip">
              💡 <strong>一页纸批注：</strong>{{ item.q.tip }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useSolveState } from '../services/solveState'

defineEmits(['switch-tab'])

const { allQuestions, recordAnswer } = useSolveState()

const mockState = ref('idle') // idle | running | finished
const mockMode = ref('random16')
const selectedYear = ref(2024)

const mockPool = ref([])
const currentIndex = ref(0)
const userAnswers = ref({})
const remainingSeconds = ref(25 * 60)
let timerId = null

const availableYears = [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2010]

function getYearCount(yr) {
  return allQuestions.filter(q => q.year === yr).length
}

const answeredCount = computed(() => {
  return Object.values(userAnswers.value).filter(arr => arr && arr.length > 0).length
})

const currentMockQuestion = computed(() => {
  return mockPool.value[currentIndex.value] || null
})

function formatTime(sec) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

function startMock() {
  if (mockMode.value === 'random16') {
    const singles = allQuestions.filter(q => q.type === 'single').sort(() => Math.random() - 0.5).slice(0, 8)
    const multis = allQuestions.filter(q => q.type === 'multi').sort(() => Math.random() - 0.5).slice(0, 8)
    mockPool.value = [...singles, ...multis]
    remainingSeconds.value = 25 * 60
  } else {
    mockPool.value = allQuestions.filter(q => q.year === selectedYear.value)
    remainingSeconds.value = Math.max(10 * 60, mockPool.value.length * 90)
  }

  currentIndex.value = 0
  userAnswers.value = {}
  mockState.value = 'running'

  if (timerId) clearInterval(timerId)
  timerId = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--
    } else {
      finishMock()
    }
  }, 1000)
}

function toggleMockOption(qid, type, optKey) {
  const current = userAnswers.value[qid] ? [...userAnswers.value[qid]] : []
  if (type === 'single') {
    userAnswers.value[qid] = [optKey]
  } else {
    const idx = current.indexOf(optKey)
    if (idx >= 0) {
      current.splice(idx, 1)
    } else {
      current.push(optKey)
      current.sort()
    }
    userAnswers.value[qid] = current
  }
}

function handleConfirmFinish() {
  const unans = mockPool.value.length - answeredCount.value
  let msg = '确定交卷并查看考生成绩报告吗？'
  if (unans > 0) {
    msg = `您还有 ${unans} 道题未作答，确定提前交卷吗？`
  }
  if (confirm(msg)) {
    finishMock()
  }
}

const mockResult = ref({})

function finishMock() {
  if (timerId) clearInterval(timerId)

  let correctCount = 0
  const items = []

  mockPool.value.forEach(q => {
    const userAns = userAnswers.value[q.id] || []
    const isCorrect = [...q.answer].sort().join('') === [...userAns].sort().join('')
    if (isCorrect) correctCount++

    // 录入学习系统
    recordAnswer(q.id, userAns)

    items.push({
      q,
      userAns,
      isCorrect
    })
  })

  const total = mockPool.value.length
  const accuracy = total > 0 ? Math.round((correctCount / total) * 100) : 0
  const score = total > 0 ? Math.round((correctCount / total) * 100) : 0

  mockResult.value = {
    title: mockMode.value === 'random16' ? '随机 16 题限时模拟' : `${selectedYear.value} 年真题限时演练`,
    score,
    accuracy,
    correctCount,
    wrongCount: total - correctCount,
    total,
    timeSpent: (mockMode.value === 'random16' ? 25 * 60 : mockPool.value.length * 90) - remainingSeconds.value,
    items
  }

  mockState.value = 'finished'
}

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
})
</script>

<style scoped>
.mock-view-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px 16px 60px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mock-idle-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.idle-badge {
  align-self: flex-start;
  background: #fdf5ea;
  color: #b46b1d;
  font-weight: 700;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.idle-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-main);
}

.idle-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
}

.mock-config-group {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-label {
  font-weight: 700;
  font-size: 14px;
}

.mode-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.mode-card {
  border: 1.5px solid var(--border-light);
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  background: var(--bg-warm);
  transition: all 0.15s ease;
}

.mode-card.active {
  border-color: var(--primary-accent);
  background: var(--primary-accent-bg);
}

.mode-header {
  font-weight: 700;
  font-size: 15px;
  color: var(--text-main);
  margin-bottom: 4px;
}

.mode-sub {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.year-selector-wrap {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.year-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
}

.year-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.yr-chip {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  border: 1px solid var(--border-card);
  font-weight: 600;
}

.yr-chip.active {
  background: var(--primary-accent);
  color: #fff;
  border-color: var(--primary-accent);
}

.start-mock-btn {
  margin-top: 10px;
  background: var(--primary-accent);
  color: #fff;
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 800;
}

/* 模考进行中 */
.mock-running-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mock-timer-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid var(--border-card);
  box-shadow: var(--shadow-sm);
}

.timer-display {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 6px;
}

.timer-urgent {
  color: var(--danger-accent);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}

.answered-summary {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 600;
}

.finish-btn {
  background: var(--danger-accent);
  color: #fff;
  font-weight: 700;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
}

.mock-sheet-strip {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 4px 0;
}

.sheet-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--border-card);
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.sheet-dot.filled {
  background: var(--primary-accent);
  color: #fff;
  border-color: var(--primary-accent);
}

.sheet-dot.active {
  box-shadow: 0 0 0 2px #ff8800;
}

.mock-card-box {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mock-question-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.q-badge {
  font-weight: 800;
  font-size: 14px;
  color: var(--text-main);
}

.q-badge-type {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.q-badge-type.single { background: #eef4fb; color: var(--primary-accent); }
.q-badge-type.multi { background: #fdf1f1; color: var(--danger-accent); }

.mock-stem {
  font-size: 16px;
  line-height: 1.7;
  font-weight: 500;
}

.mock-img-wrap {
  text-align: center;
}

.mock-raw-img {
  max-width: 100%;
  border-radius: 6px;
}

.mock-options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mock-opt-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1.5px solid var(--border-light);
  background: var(--bg-card);
  cursor: pointer;
}

.mock-opt-item.selected {
  border-color: var(--primary-accent);
  background: var(--primary-accent-bg);
}

.opt-bubble {
  min-width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--bg-warm);
  border: 1px solid var(--border-card);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
}

.mock-opt-item.selected .opt-bubble {
  background: var(--primary-accent);
  color: #fff;
  border-color: var(--primary-accent);
}

.opt-text {
  font-size: 15px;
  line-height: 1.5;
  padding-top: 2px;
}

.mock-nav-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
}

.mock-nav-btn {
  background: var(--bg-warm);
  border: 1px solid var(--border-card);
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 13px;
}

.mock-nav-btn:disabled {
  opacity: 0.3;
}

.mock-curr-indicator {
  font-size: 13px;
  color: var(--text-muted);
}

/* 结果报告 */
.mock-result-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 24px;
}

.score-circle {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: var(--primary-accent-bg);
  border: 3px solid var(--primary-accent);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.score-num {
  font-size: 32px;
  font-weight: 900;
  color: var(--primary-accent);
  line-height: 1;
}

.score-total {
  font-size: 11px;
  color: var(--text-muted);
}

.result-headline h3 {
  font-size: 20px;
  font-weight: 800;
}

.result-sub {
  font-size: 14px;
  color: var(--text-regular);
  margin-top: 4px;
}

.time-spent {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.result-actions-row {
  display: flex;
  gap: 12px;
}

.action-restart-btn {
  flex: 1;
  background: var(--primary-accent);
  color: #fff;
  padding: 10px;
  border-radius: 6px;
  font-weight: 700;
}

.action-export-btn {
  flex: 1;
  background: var(--bg-warm);
  border: 1px solid var(--border-card);
  padding: 10px;
  border-radius: 6px;
  font-weight: 700;
}

.result-details-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
}

.review-questions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.review-item {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px 14px;
  background: var(--bg-warm);
}

.review-item.is-correct {
  border-left: 4px solid var(--success-accent);
}

.review-item.is-wrong {
  border-left: 4px solid var(--danger-accent);
}

.review-item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.review-idx {
  font-weight: 700;
  font-size: 13px;
}

.review-status {
  font-size: 12px;
  font-weight: 700;
}

.text-green { color: var(--success-accent); }
.text-red { color: var(--danger-accent); }

.review-stem-short {
  font-size: 14px;
  color: var(--text-main);
  margin-bottom: 6px;
}

.review-ans-row {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.correct-text {
  color: var(--success-accent);
}

.review-tip {
  font-size: 12px;
  color: #8c5210;
  background: #fdfaf4;
  padding: 6px 8px;
  border-radius: 4px;
  margin-top: 4px;
}
</style>
