<template>
  <div class="blind-view-container">
    <!-- 顶部盲测说明横幅 -->
    <div class="blind-header-card">
      <div class="blind-badge">🎯 高阶实战训练</div>
      <h2 class="blind-title">盲测模式 · 识别命题老头挖坑手法</h2>
      <p class="blind-desc">
        真题分类已被完全隐藏。先独立做题，提交答案后判定命题手法。只有在无提示下识破挖坑逻辑，考场上才能真正临危不乱！
      </p>

      <div class="blind-stats-bar">
        <span class="stat-pill">本轮进度: {{ currentIndex + 1 }} / {{ randomPool.length }}</span>
        <span class="stat-pill">已识破手法: {{ hitCount }} 次</span>
        <button class="shuffle-btn" @click="reshufflePool">🔀 重新洗牌</button>
      </div>
    </div>

    <!-- 题目主卡片 -->
    <div v-if="currentQuestion" class="blind-card-area">
      <QuestionCard 
        :question="currentQuestion"
        :record="getRecord(currentQuestion.id)"
        :all-methods="allMethods"
        :blind-mode="true"
        @answer-submitted="handleAnswerSubmit"
        @evaluate="handleEvaluate"
        @toggle-fav="toggleFavorite"
        @toggle-mistake="toggleMistake"
        @view-method="$emit('view-method', $event)"
      />
    </div>

    <!-- 下一题操作区 -->
    <div class="blind-bottom-actions">
      <button 
        class="next-blind-btn"
        :disabled="currentIndex >= randomPool.length - 1"
        @click="nextBlindQuestion"
      >
        进入下一题 ➔
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSolveState } from '../services/solveState'
import QuestionCard from '../components/QuestionCard.vue'

defineEmits(['view-method'])

const { 
  allMethods, 
  allQuestions, 
  getRecord, 
  recordAnswer, 
  toggleFavorite, 
  toggleMistake 
} = useSolveState()

const randomPool = ref([])
const currentIndex = ref(0)
const hitCount = ref(0)

function reshufflePool() {
  const shuffled = [...allQuestions].sort(() => Math.random() - 0.5)
  randomPool.value = shuffled
  currentIndex.value = 0
}

onMounted(() => {
  reshufflePool()
})

const currentQuestion = computed(() => {
  if (randomPool.value.length === 0) return null
  return randomPool.value[currentIndex.value]
})

function handleAnswerSubmit({ qid, userSelected, chosenMethod }) {
  const res = recordAnswer(qid, userSelected, chosenMethod)
  if (res?.methodHit) {
    hitCount.value++
  }
}

function handleEvaluate({ qid, grade, userSelected, chosenMethod }) {
  recordAnswer(qid, userSelected, chosenMethod, grade)
  nextBlindQuestion()
}

function nextBlindQuestion() {
  if (currentIndex.value < randomPool.value.length - 1) {
    currentIndex.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
</script>

<style scoped>
.blind-view-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px 16px 60px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.blind-header-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.blind-badge {
  align-self: flex-start;
  background: #eef4fb;
  color: var(--primary-accent);
  font-weight: 700;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.blind-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-main);
}

.blind-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
}

.blind-stats-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
  padding-top: 10px;
  border-top: 1px dashed var(--border-light);
  flex-wrap: wrap;
}

.stat-pill {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-regular);
}

.shuffle-btn {
  margin-left: auto;
  background: var(--bg-warm);
  border: 1px solid var(--border-card);
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.blind-card-area {
  display: flex;
  flex-direction: column;
}

.blind-bottom-actions {
  display: flex;
  justify-content: flex-end;
}

.next-blind-btn {
  background: var(--primary-accent);
  color: #fff;
  font-weight: 700;
  font-size: 15px;
  padding: 10px 24px;
  border-radius: 8px;
}

.next-blind-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
