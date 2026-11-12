<template>
  <div class="practice-view-container">
    <!-- 顶部筛选与状态栏 -->
    <div class="practice-control-bar">
      <!-- 方法筛选器 -->
      <div class="method-select-wrap">
        <label class="filter-label">分类:</label>
        <select v-model="selectedMethodId" class="method-dropdown" @change="handleMethodChange">
          <option value="all">🌟 全部 68 道真题</option>
          <option v-if="weakMethods.length > 0" value="weak">
            🎯 薄弱手法攻坚 ({{ weakMethods.length }} 个待强化手法)
          </option>
          <option v-for="m in allMethods" :key="m.id" :value="m.id">
            {{ m.name }} ({{ m.questionIds.length }}题)
          </option>
        </select>
      </div>

      <!-- 题目序号与抽屉快捷开关 -->
      <div class="practice-progress-chip" @click="showDrawer = true">
        <span class="curr-no">{{ currentIndex + 1 }}</span>
        <span class="sep">/</span>
        <span class="total-no">{{ filteredQuestions.length }} ▾</span>
      </div>

      <!-- 快速切换 -->
      <div class="quick-nav-actions">
        <button class="nav-arrow-btn" :disabled="currentIndex <= 0" @click="prevQuestion">
          ◀ 上一题
        </button>
        <button class="nav-arrow-btn" :disabled="currentIndex >= filteredQuestions.length - 1" @click="nextQuestion">
          下一题 ▶
        </button>
      </div>
    </div>

    <!-- 当前题目展示卡片 -->
    <div v-if="currentQuestion" class="practice-card-area">
      <QuestionCard 
        :question="currentQuestion"
        :record="getRecord(currentQuestion.id)"
        :all-methods="allMethods"
        :blind-mode="false"
        @answer-submitted="handleAnswerSubmit"
        @evaluate="handleEvaluate"
        @toggle-fav="toggleFavorite"
        @toggle-mistake="toggleMistake"
        @view-method="handleViewMethod"
      />
    </div>

    <div v-else class="empty-questions-alert">
      当前分类下暂无题目
    </div>

    <!-- 底部大拇指快速切题栏 (移动端适配) -->
    <div class="mobile-practice-bottom-bar">
      <button 
        class="mob-btn" 
        :disabled="currentIndex <= 0" 
        @click="prevQuestion"
      >
        ◀ 上一题
      </button>

      <div class="mob-sheet-trigger" @click="showDrawer = true">
        <span>题卡 {{ currentIndex + 1 }}/{{ filteredQuestions.length }} ▾</span>
      </div>

      <button 
        class="mob-btn" 
        :disabled="currentIndex >= filteredQuestions.length - 1" 
        @click="nextQuestion"
      >
        下一题 ▶
      </button>
    </div>

    <!-- 答题卡快速跳转抽屉 -->
    <div v-if="showDrawer" class="drawer-overlay" @click.self="showDrawer = false">
      <div class="drawer-dialog">
        <div class="drawer-header">
          <span class="drawer-title">📋 题目答题卡 (共 {{ filteredQuestions.length }} 题)</span>
          <button class="drawer-close-btn" @click="showDrawer = false">✕</button>
        </div>
        <div class="drawer-grid">
          <button 
            v-for="(q, idx) in filteredQuestions" 
            :key="q.id"
            :class="[
              'drawer-q-chip',
              { active: idx === currentIndex },
              getQuestionStatusClass(q.id)
            ]"
            @click="selectIndex(idx)"
          >
            {{ q.year.toString().slice(2) }}.{{ q.no }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useSolveState } from '../services/solveState'
import QuestionCard from '../components/QuestionCard.vue'

const props = defineProps({
  initialMethodId: {
    type: String,
    default: 'all'
  },
  initialQuestionId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['view-method'])

const { 
  allMethods, 
  allQuestions, 
  getRecord, 
  recordAnswer, 
  toggleFavorite, 
  toggleMistake,
  weakMethods,
  weakMethodQuestions
} = useSolveState()

const selectedMethodId = ref(props.initialMethodId || 'all')
const currentIndex = ref(0)
const showDrawer = ref(false)

// 过滤题目池
const filteredQuestions = computed(() => {
  if (selectedMethodId.value === 'all') {
    return allQuestions
  }
  if (selectedMethodId.value === 'weak') {
    return weakMethodQuestions.value.length > 0 ? weakMethodQuestions.value : allQuestions
  }
  return allQuestions.filter(q => q.methods.includes(selectedMethodId.value))
})

const currentQuestion = computed(() => {
  if (filteredQuestions.value.length === 0) return null
  return filteredQuestions.value[currentIndex.value] || filteredQuestions.value[0]
})

// 监听路由/外部传入的 methodId
watch(() => props.initialMethodId, (newMId) => {
  if (newMId) {
    selectedMethodId.value = newMId
    currentIndex.value = 0
  }
})

// 监听路由/外部传入的 questionId
watch(() => props.initialQuestionId, (newQId) => {
  if (newQId) {
    const idx = filteredQuestions.value.findIndex(q => q.id === newQId)
    if (idx >= 0) {
      currentIndex.value = idx
    }
  }
})

function handleMethodChange() {
  currentIndex.value = 0
}

function prevQuestion() {
  if (currentIndex.value > 0) {
    currentIndex.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function nextQuestion() {
  if (currentIndex.value < filteredQuestions.value.length - 1) {
    currentIndex.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function selectIndex(idx) {
  currentIndex.value = idx
  showDrawer.value = false
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleAnswerSubmit({ qid, userSelected, chosenMethod }) {
  recordAnswer(qid, userSelected, chosenMethod)
}

function handleEvaluate({ qid, grade, userSelected, chosenMethod }) {
  recordAnswer(qid, userSelected, chosenMethod, grade)
}

function handleViewMethod(mid) {
  selectedMethodId.value = mid
  currentIndex.value = 0
  emit('view-method', mid)
}

function getQuestionStatusClass(qid) {
  const rec = getRecord(qid)
  if (!rec || !rec.history || rec.history.length === 0) return 'unanswered'
  const last = rec.history[rec.history.length - 1]
  return last?.isCorrect ? 'status-correct' : 'status-wrong'
}
</script>

<style scoped>
.practice-view-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px 16px 60px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.practice-control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-card);
  box-shadow: var(--shadow-sm);
  gap: 10px;
  flex-wrap: wrap;
}

.method-select-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
}

.method-dropdown {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--border-card);
  background: var(--bg-warm);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  outline: none;
}

.practice-progress-chip {
  background: var(--bg-warm);
  border: 1px solid var(--border-light);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  font-weight: 700;
}

.curr-no { color: var(--primary-accent); }
.sep { margin: 0 2px; color: var(--text-muted); }
.total-no { color: var(--text-muted); }

.quick-nav-actions {
  display: flex;
  gap: 8px;
}

.nav-arrow-btn {
  background: var(--bg-warm);
  border: 1px solid var(--border-light);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-regular);
}

.nav-arrow-btn:hover:not(:disabled) {
  background: var(--primary-accent-bg);
  color: var(--primary-accent);
}

.nav-arrow-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.practice-card-area {
  display: flex;
  flex-direction: column;
}

.empty-questions-alert {
  background: #fff;
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-card);
}

/* 移动端底部操作条 */
.mobile-practice-bottom-bar {
  display: none;
}

@media (max-width: 768px) {
  .practice-control-bar .quick-nav-actions {
    display: none;
  }
  .mobile-practice-bottom-bar {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    border-top: 1px solid var(--border-card);
    padding: 10px 16px;
    z-index: 95;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.06);
  }
  .mob-btn {
    background: var(--bg-warm);
    border: 1px solid var(--border-card);
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 700;
  }
  .mob-btn:disabled {
    opacity: 0.3;
  }
  .mob-sheet-trigger {
    font-size: 13px;
    font-weight: 700;
    color: var(--primary-accent);
  }
}

/* 抽屉 */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.drawer-dialog {
  background: #ffffff;
  width: 100%;
  max-width: 600px;
  border-radius: 16px 16px 0 0;
  padding: 18px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-light);
  padding-bottom: 10px;
}

.drawer-title {
  font-weight: 700;
  font-size: 15px;
}

.drawer-close-btn {
  background: none;
  font-size: 18px;
}

.drawer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(65px, 1fr));
  gap: 8px;
  overflow-y: auto;
  padding-bottom: 10px;
}

.drawer-q-chip {
  padding: 8px 4px;
  border-radius: 6px;
  border: 1px solid var(--border-card);
  background: var(--bg-warm);
  font-size: 12px;
  font-weight: 600;
}

.drawer-q-chip.active {
  border-color: var(--primary-accent);
  box-shadow: 0 0 0 2px var(--primary-accent);
}

.drawer-q-chip.status-correct {
  background: var(--success-accent-bg);
  border-color: var(--success-accent);
  color: var(--success-accent);
}

.drawer-q-chip.status-wrong {
  background: var(--danger-accent-bg);
  border-color: var(--danger-accent);
  color: var(--danger-accent);
}
</style>
