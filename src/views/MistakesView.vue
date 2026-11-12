<template>
  <div class="mistakes-container">
    <!-- 头部看板 -->
    <div class="mistakes-header-card">
      <div class="header-main">
        <div>
          <h2 class="title">📕 薄弱知识点错题本</h2>
          <p class="subtitle">集中消灭“完全不会”与“模糊”的难点卡片 · 连续 2 次掌握将自动移出</p>
        </div>
        <div class="stat-badge">
          <span class="count-num">{{ filteredMistakes.length }}</span>
          <span class="count-lbl">待攻克</span>
        </div>
      </div>

      <!-- 操作与过滤栏 -->
      <div class="filter-bar">
        <div class="sub-filters">
          <button 
            v-for="sub in ['全部', '马原', '政经', '史纲', '其他']" 
            :key="sub"
            :class="['filter-btn', { active: currentSubject === sub }]"
            @click="currentSubject = sub"
          >
            {{ sub }}
          </button>
        </div>

        <button 
          v-if="filteredMistakes.length > 0"
          class="batch-recite-btn"
          @click="$emit('start-batch-recite', filteredMistakes[0]?.id)"
        >
          <span>🎯</span> 错题专项突击背诵
        </button>
      </div>
    </div>

    <!-- 错题为空的提示 -->
    <div v-if="filteredMistakes.length === 0" class="empty-mistakes">
      <div class="empty-icon">🌟</div>
      <h3>太棒了！当前没有任何错题</h3>
      <p>在背诵或抽查中评价为“完全不会”或“模糊”的卡片将自动归集到此处。</p>
    </div>

    <!-- 错题卡片列表 -->
    <div v-else class="mistakes-grid">
      <div 
        v-for="card in filteredMistakes" 
        :key="card.id"
        class="mistake-card-item"
      >
        <div class="item-header">
          <div class="header-tags">
            <span class="sid-tag">知识点 {{ card.sourceId }}</span>
            <span class="sec-tag">{{ card.subject }} · {{ card.section }}</span>
            <span class="status-tag" :class="`status-${getLastGrade(card.id)}`">
              {{ getLastGradeLabel(card.id) }}
            </span>
          </div>

          <div class="item-actions">
            <button class="action-btn text-muted" title="手动移出错题本" @click="removeFromMistakes(card.id)">
              移出
            </button>
          </div>
        </div>

        <div class="item-body">
          <h4 class="card-item-title">{{ card.title }}</h4>
          <p class="card-item-snippet">{{ getCleanSnippet(card.content) }}</p>

          <div v-if="card.distinctions && card.distinctions.length" class="dist-preview">
            <span class="dist-tag">含 {{ card.distinctions.length }} 条辨析判断</span>
          </div>
        </div>

        <div class="item-footer">
          <div class="history-info">
            <span>复习 {{ getReviewCount(card.id) }} 次</span>
            <span v-if="getConsecutive(card.id) > 0" class="consec-tag">连续掌握 {{ getConsecutive(card.id) }}/2 次</span>
          </div>

          <div class="footer-btns">
            <button class="view-btn btn-img" @click="$emit('view-image', card)">
              <span>🖼️</span> 原图
            </button>
            <button class="view-btn btn-recite" @click="$emit('recite-single', card.id)">
              <span>🧠</span> 突击背诵
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserState } from '../services/storage/userState'

defineEmits(['view-image', 'start-batch-recite', 'recite-single'])

const { state, mistakeCards, removeFromMistakes } = useUserState()

const currentSubject = ref('全部')

const filteredMistakes = computed(() => {
  if (currentSubject.value === '全部') {
    return mistakeCards.value
  }
  return mistakeCards.value.filter(c => c.subject === currentSubject.value)
})

function getLastGrade(cardId) {
  return state.records[cardId]?.lastGrade || 'again'
}

function getLastGradeLabel(cardId) {
  const g = state.records[cardId]?.lastGrade
  if (g === 'again') return '完全不会'
  if (g === 'hard') return '模糊'
  return '待巩固'
}

function getReviewCount(cardId) {
  return state.records[cardId]?.reviewCount || 0
}

function getConsecutive(cardId) {
  return state.records[cardId]?.consecutiveGood || 0
}

function getCleanSnippet(content) {
  if (!content) return ''
  return content.replace(/\{\{([^}]+)\}\}/g, '$1').replace(/\n+/g, ' ').slice(0, 90) + '...'
}
</script>

<style scoped>
.mistakes-container {
  max-width: 860px;
  margin: 0 auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mistakes-header-card {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
}

.subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

.stat-badge {
  background: #fdf2f2;
  border: 1px solid #fed7d7;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  text-align: center;
}

.count-num {
  font-size: 20px;
  font-weight: 800;
  color: var(--danger-accent);
}

.count-lbl {
  font-size: 10px;
  color: #9b2c2c;
  display: block;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  border-top: 1px solid var(--border-light);
  padding-top: 12px;
}

.sub-filters {
  display: flex;
  gap: 6px;
}

.filter-btn {
  padding: 5px 10px;
  border-radius: var(--radius-sm);
  background: var(--bg-beige-light);
  border: 1px solid var(--border-card);
  font-size: 12px;
  color: var(--text-regular);
}

.filter-btn.active {
  background: var(--bg-beige);
  border-color: #7c4a1e;
  color: #7c4a1e;
  font-weight: 700;
}

.batch-recite-btn {
  background: var(--danger-accent);
  color: white;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.empty-mistakes {
  background: #ffffff;
  border: 1px dashed var(--border-card);
  border-radius: var(--radius-lg);
  padding: 60px 20px;
  text-align: center;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 44px;
  margin-bottom: 8px;
}

.empty-mistakes h3 {
  font-size: 16px;
  color: var(--text-main);
  margin-bottom: 4px;
}

.empty-mistakes p {
  font-size: 13px;
}

.mistakes-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mistake-card-item {
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: var(--shadow-sm);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sid-tag {
  font-size: 12px;
  font-weight: 700;
  color: #7c4a1e;
  background: var(--bg-beige);
  padding: 2px 6px;
  border-radius: 4px;
}

.sec-tag {
  font-size: 12px;
  color: var(--text-muted);
}

.status-tag {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-again { background: #fee2e2; color: #b91c1c; }
.status-hard { background: #fef3c7; color: #b45309; }

.action-btn {
  background: transparent;
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 6px;
  border-radius: 4px;
}

.action-btn:hover {
  background: #f1f5f9;
  color: var(--danger-accent);
}

.card-item-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}

.card-item-snippet {
  font-size: 13px;
  color: var(--text-regular);
  line-height: 1.6;
}

.dist-preview {
  margin-top: 6px;
}

.dist-tag {
  background: #fef2f2;
  color: #b91c1c;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}

.item-footer {
  border-top: 1px solid var(--border-light);
  padding-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
}

.consec-tag {
  color: var(--success-accent);
  font-weight: 600;
}

.footer-btns {
  display: flex;
  gap: 8px;
}

.view-btn {
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-img {
  background: #fff;
  border: 1px solid var(--border-card);
  color: var(--text-regular);
}

.btn-recite {
  background: var(--primary-accent-bg);
  border: 1px solid var(--primary-accent);
  color: var(--primary-accent);
}
</style>
