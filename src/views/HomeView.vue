<template>
  <div class="home-container">
    <!-- 欢迎与进度概览看板 -->
    <div class="welcome-card">
      <div class="welcome-header">
        <div>
          <h1 class="welcome-title">考研政治一页纸 · 智能记忆</h1>
          <p class="welcome-sub">原书 100 个核心知识点 · 122 张卡片逐条回溯</p>
        </div>
        <div class="progress-ring">
          <span class="ring-val">{{ progressPercent }}%</span>
          <span class="ring-lbl">总体掌握</span>
        </div>
      </div>

      <!-- 四大核心记忆指标 -->
      <div class="stat-grid">
        <div class="stat-box box-due" @click="$emit('navigate', 'recite')">
          <div class="stat-num">{{ dueCount }}</div>
          <div class="stat-label">今日待复习</div>
          <div class="stat-hint">基于 SRS 算法排期</div>
        </div>

        <div class="stat-box box-mistake" @click="$emit('navigate', 'mistakes')">
          <div class="stat-num">{{ mistakeCount }}</div>
          <div class="stat-label">薄弱错题</div>
          <div class="stat-hint">完全不会 / 模糊</div>
        </div>

        <div class="stat-box box-learned">
          <div class="stat-num">{{ learnedCount }}</div>
          <div class="stat-label">已学知识点</div>
          <div class="stat-hint">总计 {{ totalCount }} 条</div>
        </div>

        <div class="stat-box box-mastered">
          <div class="stat-num">{{ masteredCount }}</div>
          <div class="stat-label">已熟练掌握</div>
          <div class="stat-hint">连续 2 次以上掌握</div>
        </div>
      </div>
    </div>

    <!-- 快捷操作行动区 -->
    <div class="action-grid">
      <button class="action-card card-primary" @click="$emit('navigate', 'recite')">
        <div class="card-icon">🧠</div>
        <div class="card-text">
          <div class="action-title">开始今日背诵</div>
          <div class="action-sub">
            <span v-if="dueCount > 0">优先复习 {{ dueCount }} 条到期卡片</span>
            <span v-else>太棒了！今日无到期，建议学习新知识点</span>
          </div>
        </div>
        <span class="arrow-icon">→</span>
      </button>

      <button class="action-card card-secondary" @click="$emit('navigate', 'quiz')">
        <div class="card-icon">🎲</div>
        <div class="card-text">
          <div class="action-title">随机专项抽查</div>
          <div class="action-sub">按学科或全书随机挖空，检验记忆牢固度</div>
        </div>
        <span class="arrow-icon">→</span>
      </button>

      <button class="action-card card-solve" @click="$emit('navigate', 'solve')">
        <div class="card-icon">🎯</div>
        <div class="card-text">
          <div class="action-title">解题方法刷题</div>
          <div class="action-sub">10类老头命题挖坑手法 · 68道真题分类刷与盲测</div>
        </div>
        <span class="arrow-icon">→</span>
      </button>
    </div>

    <!-- 待复习知识点推荐流 -->
    <div class="focus-section">
      <div class="section-title-bar">
        <h3 class="section-title">📌 优先复习队列</h3>
        <span class="section-badge">{{ focusCards.length }} 条</span>
      </div>

      <div v-if="focusCards.length === 0" class="empty-hint">
        <span>🎉 当前没有待复习知识点，去“浏览”看看新知识点吧！</span>
      </div>

      <div v-else class="cards-preview-list">
        <div 
          v-for="card in focusCards.slice(0, 5)" 
          :key="card.id"
          class="preview-card-item"
          @click="$emit('start-card-recite', card.id)"
        >
          <div class="item-left">
            <span class="id-badge">{{ card.sourceId }}</span>
            <div class="item-info">
              <span class="item-title">{{ card.title }}</span>
              <span class="item-sub">{{ card.subject }} · {{ card.section }} | PDF P{{ card.sourcePage[0] }}</span>
            </div>
          </div>
          <div class="item-right">
            <span v-if="getCardStatusLabel(card.id)" class="status-tag">
              {{ getCardStatusLabel(card.id) }}
            </span>
            <span class="arrow-btn">背诵 →</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近学习动态 -->
    <div v-if="recentHistory.length > 0" class="focus-section">
      <div class="section-title-bar">
        <h3 class="section-title">🕒 最近复习记录</h3>
      </div>
      <div class="history-list">
        <div v-for="(h, idx) in recentHistory" :key="idx" class="history-item">
          <div class="h-left">
            <span class="h-grade" :class="`grade-${h.grade}`">{{ gradeNameMap[h.grade] }}</span>
            <span class="h-title">[知识点 {{ h.sourceId }}] {{ h.title }}</span>
          </div>
          <span class="h-time">{{ formatTime(h.timestamp) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserState, getAllCards } from '../services/storage/userState'

const emit = defineEmits(['navigate', 'start-card-recite'])

const { 
  state,
  totalCardsCount, 
  dueCards, 
  learnedCardsCount, 
  mistakeCards, 
  masteredCardsCount 
} = useUserState()

const totalCount = totalCardsCount
const dueCount = computed(() => dueCards.value.length)
const learnedCount = learnedCardsCount
const mistakeCount = computed(() => mistakeCards.value.length)
const masteredCount = masteredCardsCount

const progressPercent = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((masteredCount.value / totalCount.value) * 100)
})

// 优先队列：到期卡片优先，其次为错题卡片
const focusCards = computed(() => {
  if (dueCards.value.length > 0) {
    return dueCards.value
  }
  return mistakeCards.value
})

function getCardStatusLabel(cardId) {
  const rec = state.records[cardId]
  if (!rec) return '新卡片'
  if (rec.inMistakeBook) return '错题中'
  if (rec.lastGrade === 'again') return '完全不会'
  if (rec.lastGrade === 'hard') return '模糊'
  return ''
}

const gradeNameMap = {
  again: '完全不会',
  hard: '模糊',
  good: '基本掌握',
  easy: '熟练掌握'
}

// 整理最近 5 次评价动态
const recentHistory = computed(() => {
  const allCards = getAllCards()
  const cardMap = new Map(allCards.map(c => [c.id, c]))
  const list = []

  for (const [id, rec] of Object.entries(state.records)) {
    if (rec.history && rec.history.length > 0) {
      const card = cardMap.get(id)
      rec.history.forEach(h => {
        list.push({
          cardId: id,
          sourceId: card?.sourceId || '---',
          title: card?.title || '知识点',
          timestamp: h.timestamp,
          grade: h.grade,
        })
      })
    }
  }

  list.sort((a, b) => b.timestamp - a.timestamp)
  return list.slice(0, 5)
})

function formatTime(ts) {
  const diff = Date.now() - ts
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  return `${days} 天前`
}
</script>

<style scoped>
.home-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px 16px 40px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 欢迎卡片 */
.welcome-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 22px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}

.welcome-sub {
  font-size: 13px;
  color: var(--text-muted);
}

.progress-ring {
  background: var(--bg-beige);
  border: 2px solid var(--border-card);
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-val {
  font-size: 17px;
  font-weight: 800;
  color: var(--primary-accent);
}

.ring-lbl {
  font-size: 10px;
  color: var(--text-muted);
}

/* 四大指标卡 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-box {
  background: var(--bg-beige-light);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 12px;
  text-align: center;
  transition: all 0.15s ease;
  cursor: pointer;
}

.stat-box:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.stat-num {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-main);
}

.stat-label {
  font-size: 13px;
  font-weight: 600;
  margin-top: 2px;
}

.stat-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.box-due .stat-num { color: var(--primary-accent); }
.box-mistake .stat-num { color: var(--danger-accent); }
.box-mastered .stat-num { color: var(--success-accent); }

/* 行动卡片 */
.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.action-card {
  padding: 18px 20px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  gap: 14px;
  text-align: left;
  border: 1px solid transparent;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-primary {
  background: #fbf6ec;
  border-color: #eeddc3;
}

.card-secondary {
  background: #f4f8fd;
  border-color: #d7e6f8;
}

.card-solve {
  background: #fef8f3;
  border-color: #f7dac4;
}

.card-icon {
  font-size: 32px;
}

.card-text {
  flex: 1;
}

.action-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 3px;
}

.action-sub {
  font-size: 12px;
  color: var(--text-muted);
}

.arrow-icon {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-muted);
}

/* 优先队列 */
.focus-section {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
}

.section-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
}

.section-badge {
  background: var(--bg-beige);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.empty-hint {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-size: 14px;
}

.cards-preview-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-card-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: var(--bg-beige-light);
  cursor: pointer;
  transition: all 0.15s ease;
}

.preview-card-item:hover {
  background: var(--bg-beige);
  border-color: #dfd4c2;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.id-badge {
  font-size: 12px;
  font-weight: 700;
  color: #7c4a1e;
  background: #fff;
  padding: 3px 6px;
  border-radius: 4px;
  border: 1px solid var(--border-light);
}

.item-info {
  display: flex;
  flex-direction: column;
}

.item-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.item-sub {
  font-size: 11px;
  color: var(--text-muted);
}

.item-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tag {
  background: #fee2e2;
  color: #b91c1c;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.arrow-btn {
  font-size: 12px;
  color: var(--primary-accent);
  font-weight: 600;
}

/* 历史列表 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  background: #fafaf8;
  font-size: 13px;
}

.h-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.h-grade {
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
}

.grade-again { background: #fee2e2; color: #b91c1c; }
.grade-hard { background: #fef3c7; color: #b45309; }
.grade-good { background: #e0f2fe; color: #0369a1; }
.grade-easy { background: #dcfce7; color: #15803d; }

.h-title {
  color: var(--text-regular);
}

.h-time {
  font-size: 11px;
  color: var(--text-muted);
}

@media (max-width: 640px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>
