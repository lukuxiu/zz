<template>
  <div class="mistakes-view-container">
    <!-- 错题本概览头部 -->
    <div class="mistakes-header-card">
      <div class="mistakes-badge">📕 靶向攻坚</div>
      <h2 class="mistakes-title">解题方法错题本</h2>
      <p class="mistakes-desc">
        错题按 10 类老头命题挖坑手法归类聚合，严格遵循艾宾浩斯间隔复习规范：连续 2 次答对并自评良好即可从活跃错题本中自动移出。
      </p>

      <!-- 错题分类统计徽章流 -->
      <div class="method-mistake-chips">
        <button 
          :class="['m-chip', { active: filterMethodId === 'all' }]"
          @click="filterMethodId = 'all'"
        >
          全部错题 ({{ mistakeQuestions.length }})
        </button>

        <button 
          v-for="m in allMethods" 
          :key="m.id"
          :class="['m-chip', { active: filterMethodId === m.id }]"
          @click="filterMethodId = m.id"
        >
          {{ m.name }}
          <span v-if="getMethodMistakeCount(m.id) > 0" class="chip-num">
            {{ getMethodMistakeCount(m.id) }}
          </span>
        </button>
      </div>
    </div>

    <!-- 错题列表 -->
    <div v-if="displayQuestions.length > 0" class="mistakes-list">
      <div 
        v-for="q in displayQuestions" 
        :key="q.id"
        class="mistake-item-box"
      >
        <div class="mistake-meta-bar">
          <span class="m-status-tag">
            连续答对: <strong>{{ getRecord(q.id).consecutiveGood || 0 }} / 2</strong> 次
            <span v-if="(getRecord(q.id).consecutiveGood || 0) >= 1" class="m-hint-tag">（再答对 1 次即可移出）</span>
          </span>
          <button class="remove-btn" @click="toggleMistake(q.id)">
            移出错题本 ✕
          </button>
        </div>

        <QuestionCard 
          :question="q"
          :record="getRecord(q.id)"
          :all-methods="allMethods"
          :blind-mode="false"
          @answer-submitted="handleAnswerSubmit"
          @evaluate="handleEvaluate"
          @toggle-fav="toggleFavorite"
          @toggle-mistake="toggleMistake"
          @view-method="$emit('view-method', $event)"
        />
      </div>
    </div>

    <div v-else class="empty-mistakes-box">
      <span class="empty-icon">🎉</span>
      <h3 class="empty-title">当前无错题记录！</h3>
      <p class="empty-desc">太棒了，所有做过的该分类真题均已掌握或已连续 2 次复习达标！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSolveState } from '../services/solveState'
import QuestionCard from '../components/QuestionCard.vue'

defineEmits(['view-method'])

const { 
  allMethods, 
  mistakeQuestions, 
  getRecord, 
  recordAnswer, 
  toggleFavorite, 
  toggleMistake 
} = useSolveState()

const filterMethodId = ref('all')

function getMethodMistakeCount(mid) {
  return mistakeQuestions.value.filter(q => q.methods.includes(mid)).length
}

const displayQuestions = computed(() => {
  if (filterMethodId.value === 'all') {
    return mistakeQuestions.value
  }
  return mistakeQuestions.value.filter(q => q.methods.includes(filterMethodId.value))
})

function handleAnswerSubmit({ qid, userSelected, chosenMethod }) {
  recordAnswer(qid, userSelected, chosenMethod)
}

function handleEvaluate({ qid, grade, userSelected, chosenMethod }) {
  recordAnswer(qid, userSelected, chosenMethod, grade)
}
</script>

<style scoped>
.mistakes-view-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 16px 16px 60px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mistakes-header-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mistakes-badge {
  align-self: flex-start;
  background: #fdf1f1;
  color: var(--danger-accent);
  font-weight: 700;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.mistakes-title {
  font-size: 18px;
  font-weight: 800;
}

.mistakes-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
}

.method-mistake-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
  padding-top: 10px;
  border-top: 1px dashed var(--border-light);
}

.m-chip {
  padding: 5px 10px;
  border-radius: 16px;
  font-size: 12px;
  background: var(--bg-warm);
  border: 1px solid var(--border-card);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.m-chip.active {
  background: #fdf1f1;
  color: var(--danger-accent);
  border-color: var(--danger-accent);
}

.chip-num {
  background: var(--danger-accent);
  color: #fff;
  padding: 0 5px;
  border-radius: 8px;
  font-size: 11px;
}

.mistakes-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.mistake-item-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mistake-meta-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 6px;
}

.m-status-tag {
  font-size: 12px;
  color: var(--text-muted);
}

.m-status-tag strong {
  color: var(--primary-accent);
}

.m-hint-tag {
  color: var(--success-accent);
}

.remove-btn {
  background: none;
  color: var(--text-muted);
  font-size: 12px;
  border: 1px solid var(--border-light);
  padding: 2px 8px;
  border-radius: 4px;
}

.remove-btn:hover {
  color: var(--danger-accent);
  border-color: var(--danger-accent);
}

.empty-mistakes-box {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 50px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.empty-icon {
  font-size: 40px;
}

.empty-title {
  font-size: 18px;
  font-weight: 800;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-muted);
}
</style>
