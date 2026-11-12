<template>
  <div class="recite-container">
    <!-- 顶部状态栏：进度、模式切换 -->
    <div class="recite-topbar">
      <div class="progress-info">
        <span class="queue-badge">待复习队列</span>
        <span class="progress-count">{{ currentIndex + 1 }} / {{ queue.length }}</span>
      </div>

      <div class="mode-selector">
        <span class="mode-label">遮挡模式:</span>
        <select v-model="clozeMode" class="mode-select">
          <option value="none">显示全部 (不进行遮挡)</option>
          <option value="keyword">关键词遮挡 (默认)</option>
          <option value="sentence">分句遮挡</option>
          <option value="random">随机挖空</option>
          <option value="full">整卡遮挡</option>
        </select>
      </div>
    </div>

    <!-- 背诵完成庆祝界面 -->
    <div v-if="isSessionFinished || queue.length === 0" class="finished-card">
      <div class="finish-icon">🎉</div>
      <h2 class="finish-title">太棒了！本轮背诵任务已全部完成</h2>
      <p class="finish-sub">本次会话共完成复习 {{ sessionFinishedCount }} 次</p>

      <div class="finish-actions">
        <button class="finish-btn btn-more" @click="loadMoreNewCards">
          <span>📖</span> 继续学习新卡片 (10条)
        </button>
        <button class="finish-btn btn-quiz" @click="$emit('navigate', 'quiz')">
          <span>🎲</span> 进入随机抽查
        </button>
        <button class="finish-btn btn-home" @click="$emit('navigate', 'home')">
          <span>🏠</span> 返回首页
        </button>
      </div>
    </div>

    <!-- 核心卡片与自我评价区 -->
    <div v-else class="recite-main">
      <CardViewer 
        v-if="currentCard"
        :card="currentCard"
        :mode="clozeMode"
        :font-size="fontSize"
        :is-favorite="isFavorite(currentCard.id)"
        @toggle-fav="toggleFavorite"
        @view-image="$emit('view-image', $event)"
      />

      <!-- 四档自我评价组件 -->
      <div class="evaluation-panel">
        <SelfEvaluation @evaluate="handleEvaluation" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import CardViewer from '../components/CardViewer.vue'
import SelfEvaluation from '../components/SelfEvaluation.vue'
import { useUserState, getAllCards, getCardById } from '../services/storage/userState'
import { insertWithoutImmediateRepeat } from '../services/srs/srsAlgorithm'

const props = defineProps({
  fontSize: { type: String, default: 'medium' },
  defaultMode: { type: String, default: 'keyword' },
  targetCardId: { type: String, default: '' }
})

const emit = defineEmits(['navigate', 'view-image'])

const { state, dueCards, mistakeCards, recordReview, toggleFavorite } = useUserState()
const allCards = getAllCards()

const clozeMode = ref(props.defaultMode)
const queue = ref([])
const currentIndex = ref(0)
const sessionFinishedCount = ref(0)
const isSessionFinished = ref(false)

const isFavorite = (id) => !!state.records[id]?.isFavorite

// 初始化复习队列
onMounted(() => {
  initQueue()
})

watch(() => props.targetCardId, (targetId) => {
  if (targetId) {
    const card = getCardById(targetId)
    if (card) {
      queue.value = [card]
      currentIndex.value = 0
      isSessionFinished.value = false
    }
  }
})

function initQueue() {
  if (props.targetCardId) {
    const card = getCardById(props.targetCardId)
    if (card) {
      queue.value = [card]
      currentIndex.value = 0
      return
    }
  }

  // 优先选取到期卡片
  if (dueCards.value.length > 0) {
    queue.value = [...dueCards.value]
  } else if (mistakeCards.value.length > 0) {
    // 其次选取错题
    queue.value = [...mistakeCards.value]
  } else {
    // 否则选取未学过的新卡片（10张）
    const unlearned = allCards.filter(c => !state.records[c.id])
    queue.value = unlearned.slice(0, 10)
  }

  currentIndex.value = 0
  isSessionFinished.value = false
}

const currentCard = computed(() => {
  if (currentIndex.value >= queue.value.length) return null
  return queue.value[currentIndex.value]
})

function handleEvaluation(grade) {
  if (!currentCard.value) return
  const card = currentCard.value
  
  // 记录到 SRS 系统中
  recordReview(card.id, grade, clozeMode.value)
  sessionFinishedCount.value++

  // 若为“完全不会”，为了防短期记忆错觉，将卡片再次排入本轮队列末尾
  if (grade === 'again') {
    queue.value = insertWithoutImmediateRepeat(queue.value, card)
  }

  // 流转到下一张
  if (currentIndex.value < queue.value.length - 1) {
    currentIndex.value++
  } else {
    isSessionFinished.value = true
  }
}

function loadMoreNewCards() {
  const unlearned = allCards.filter(c => !state.records[c.id])
  if (unlearned.length === 0) {
    // 全书都已学过，载入全部卡片循环巩固
    queue.value = [...allCards].sort(() => Math.random() - 0.5).slice(0, 10)
  } else {
    queue.value = unlearned.slice(0, 10)
  }
  currentIndex.value = 0
  isSessionFinished.value = false
}
</script>

<style scoped>
.recite-container {
  max-width: 820px;
  margin: 0 auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recite-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-card);
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.queue-badge {
  background: var(--primary-accent-bg);
  color: var(--primary-accent);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.progress-count {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
}

.mode-selector {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mode-label {
  font-size: 12px;
  color: var(--text-muted);
}

.mode-select {
  padding: 4px 8px;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  font-size: 12px;
  background: #ffffff;
  color: var(--text-main);
}

.recite-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.evaluation-panel {
  position: sticky;
  bottom: 16px;
  z-index: 50;
}

/* 完成结算卡片 */
.finished-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow-sm);
}

.finish-icon {
  font-size: 48px;
}

.finish-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
}

.finish-sub {
  font-size: 13px;
  color: var(--text-muted);
}

.finish-actions {
  display: flex;
  gap: 12px;
  margin-top: 14px;
  flex-wrap: wrap;
  justify-content: center;
}

.finish-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  border: 1px solid var(--border-card);
}

.btn-more {
  background: var(--primary-accent);
  color: white;
  border: none;
}

.btn-quiz {
  background: var(--bg-beige);
  color: #7c4a1e;
}

.btn-home {
  background: #fff;
  color: var(--text-regular);
}
</style>
