<template>
  <div class="quiz-container">
    <!-- 抽查配置面板 (未开始时展示) -->
    <div v-if="!isQuizRunning" class="quiz-config-card">
      <div class="config-header">
        <h2 class="config-title">🎲 随机知识点抽查</h2>
        <p class="config-sub">设定范围进行无规律抽查，检验记忆的随机提取与抗干扰能力</p>
      </div>

      <div class="config-options">
        <div class="option-row">
          <label class="option-label">抽查范围:</label>
          <div class="scope-tags">
            <button 
              v-for="s in scopes" 
              :key="s.id"
              :class="['scope-btn', { active: selectedScope === s.id }]"
              @click="selectedScope = s.id"
            >
              {{ s.label }} ({{ getScopeCount(s.id) }})
            </button>
          </div>
        </div>

        <div class="option-row">
          <label class="option-label">抽查题量:</label>
          <div class="scope-tags">
            <button 
              v-for="c in [5, 10, 20, 30]" 
              :key="c"
              :class="['scope-btn', { active: quizCount === c }]"
              @click="quizCount = c"
            >
              {{ c }} 题
            </button>
          </div>
        </div>
      </div>

      <div class="config-footer">
        <button 
          class="start-quiz-btn" 
          :disabled="getScopeCount(selectedScope) === 0"
          @click="startQuiz"
        >
          开始抽查 (共 {{ Math.min(quizCount, getScopeCount(selectedScope)) }} 题)
        </button>
      </div>
    </div>

    <!-- 抽查进行中 -->
    <div v-else class="quiz-active-area">
      <!-- 进度与控制 -->
      <div class="quiz-topbar">
        <div class="quiz-progress">
          <span class="quiz-badge">抽查进行中</span>
          <span class="progress-text">第 {{ currentQuizIndex + 1 }} 题 / 共 {{ quizPool.length }} 题</span>
        </div>
        <button class="quit-btn" @click="endQuiz">提前结束</button>
      </div>

      <!-- 题目卡片（默认遮挡，用户作答回忆） -->
      <CardViewer 
        v-if="currentQuizCard"
        :card="currentQuizCard"
        :mode="isRevealed ? 'none' : 'keyword'"
        :font-size="fontSize"
        :is-favorite="isFavorite(currentQuizCard.id)"
        @toggle-fav="toggleFavorite"
        @view-image="$emit('view-image', $event)"
      />

      <!-- 答题状态控制 -->
      <div class="quiz-controls-card">
        <div v-if="!isRevealed" class="reveal-prompt">
          <p class="prompt-text">尝试在脑海中回忆该知识点的核心重点词、口诀或辨析</p>
          <button class="reveal-btn" @click="isRevealed = true">
            揭晓答案与完整解析 👁️
          </button>
        </div>

        <div v-else class="post-reveal">
          <p class="prompt-text">核对完毕，请记录本次掌握情况：</p>
          <SelfEvaluation @evaluate="handleQuizEvaluation" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CardViewer from '../components/CardViewer.vue'
import SelfEvaluation from '../components/SelfEvaluation.vue'
import { getAllCards, useUserState } from '../services/storage/userState'

defineProps({
  fontSize: { type: String, default: 'medium' }
})

defineEmits(['view-image'])

const { state, mistakeCards, favoriteCards, recordReview, toggleFavorite } = useUserState()
const allCards = getAllCards()

const isFavorite = (id) => !!state.records[id]?.isFavorite

const scopes = [
  { id: 'all', label: '全书范围' },
  { id: 'mayuan', label: '马原' },
  { id: 'zhengjing', label: '政经' },
  { id: 'shigang', label: '史纲' },
  { id: 'other', label: '其他' },
  { id: 'mistakes', label: '仅错题' },
  { id: 'fav', label: '仅收藏' }
]

const selectedScope = ref('all')
const quizCount = ref(10)

const isQuizRunning = ref(false)
const quizPool = ref([])
const currentQuizIndex = ref(0)
const isRevealed = ref(false)

function getScopeCount(scopeId) {
  return getPoolByScope(scopeId).length
}

function getPoolByScope(scopeId) {
  switch (scopeId) {
    case 'mayuan': return allCards.filter(c => c.subject === '马原')
    case 'zhengjing': return allCards.filter(c => c.subject === '政经')
    case 'shigang': return allCards.filter(c => c.subject === '史纲')
    case 'other': return allCards.filter(c => c.subject === '其他')
    case 'mistakes': return mistakeCards.value
    case 'fav': return favoriteCards.value
    default: return allCards
  }
}

function startQuiz() {
  const candidates = [...getPoolByScope(selectedScope.value)]
  if (candidates.length === 0) return

  // 严格随机打乱（Fisher-Yates 洗牌算法保证去重）
  for (let i = candidates.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [candidates[i], candidates[j]] = [candidates[j], candidates[i]]
  }

  // 截取指定题量
  quizPool.value = candidates.slice(0, quizCount.value)
  currentQuizIndex.value = 0
  isRevealed.value = false
  isQuizRunning.value = true
}

const currentQuizCard = () => {
  return quizPool.value[currentQuizIndex.value] || null
}

function handleQuizEvaluation(grade) {
  const card = quizPool.value[currentQuizIndex.value]
  if (card) {
    recordReview(card.id, grade, 'random')
  }

  if (currentQuizIndex.value < quizPool.value.length - 1) {
    currentQuizIndex.value++
    isRevealed.value = false
  } else {
    alert(`🎉 恭喜！已完成本轮 ${quizPool.value.length} 道随机抽查！`)
    endQuiz()
  }
}

function endQuiz() {
  isQuizRunning.value = false
  quizPool.value = []
}
</script>

<style scoped>
.quiz-container {
  max-width: 820px;
  margin: 0 auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quiz-config-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-header {
  border-bottom: 1px solid var(--border-light);
  padding-bottom: 14px;
}

.config-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}

.config-sub {
  font-size: 13px;
  color: var(--text-muted);
}

.config-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
}

.scope-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.scope-btn {
  padding: 7px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-card);
  background: #fff;
  font-size: 13px;
  color: var(--text-regular);
}

.scope-btn:hover {
  background: var(--bg-beige-light);
}

.scope-btn.active {
  background: var(--bg-beige);
  border-color: #7c4a1e;
  color: #7c4a1e;
  font-weight: 700;
}

.config-footer {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.start-quiz-btn {
  background: var(--primary-accent);
  color: white;
  padding: 10px 24px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 700;
}

.start-quiz-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 抽查中 */
.quiz-active-area {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.quiz-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-card);
}

.quiz-badge {
  background: var(--bg-beige);
  color: #7c4a1e;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 8px;
}

.progress-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
}

.quit-btn {
  background: #fff;
  border: 1px solid var(--border-light);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-muted);
}

.quiz-controls-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 16px;
  text-align: center;
}

.prompt-text {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.reveal-btn {
  background: var(--primary-accent-bg);
  border: 1px solid var(--primary-accent);
  color: var(--primary-accent);
  padding: 10px 24px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 700;
}

.reveal-btn:hover {
  background: #dbeafe;
}
</style>
