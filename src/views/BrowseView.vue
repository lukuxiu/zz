<template>
  <div class="browse-layout">
    <!-- 移动端抽屉遮罩 (Backdrop) -->
    <div 
      v-if="isDrawerOpen" 
      class="drawer-backdrop" 
      @click="isDrawerOpen = false"
    ></div>

    <!-- 左侧考点目录（桌面端侧边栏 / 移动端滑动抽屉） -->
    <aside :class="['browse-sidebar', { 'drawer-open': isDrawerOpen }]">
      <!-- 抽屉头部（移动端显示关闭按钮） -->
      <div class="sidebar-header">
        <div class="sidebar-title">
          <span>📚 考点目录</span>
          <span class="count-pill">{{ filteredCards.length }} 条</span>
        </div>
        <button class="drawer-close-btn" @click="isDrawerOpen = false" title="关闭目录">✕</button>
      </div>

      <!-- 搜索过滤 -->
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          type="text" 
          class="search-input" 
          placeholder="搜索知识点编号、标题或原文..." 
        />
        <button v-if="searchQuery" class="clear-search-btn" @click="searchQuery = ''">✕</button>
      </div>

      <!-- 科目过滤标签 -->
      <div class="subject-tabs">
        <button 
          v-for="sub in subjects" 
          :key="sub"
          :class="['sub-tab', { active: selectedSubject === sub }]"
          @click="selectedSubject = sub"
        >
          {{ sub }}
        </button>
      </div>

      <!-- 知识点卡片列表 -->
      <div class="card-nav-list">
        <div 
          v-for="c in filteredCards" 
          :key="c.id"
          :class="['nav-card-item', { active: currentCard?.id === c.id }]"
          @click="selectCard(c)"
        >
          <div class="item-head">
            <span class="sid-badge">考点 {{ c.sourceId }}</span>
            <div class="item-indicators">
              <span v-if="isFavorite(c.id)" class="fav-icon" title="已收藏">★</span>
              <span v-if="isMistake(c.id)" class="mistake-dot" title="在错题本中">•</span>
            </div>
          </div>
          <div class="item-title">{{ c.title }}</div>
          <div class="item-meta">
            <span class="meta-section">{{ c.subject }} · {{ c.section }}</span>
            <span class="meta-page">P{{ c.sourcePage[0] }}</span>
          </div>
        </div>

        <div v-if="filteredCards.length === 0" class="empty-list">
          没有找到匹配的知识点
        </div>
      </div>
    </aside>

    <!-- 右侧卡片浏览主体 -->
    <main class="browse-main">
      <!-- 顶部控制条：目录抽屉唤起、切卡导航、字号微调、一键背诵 -->
      <div class="browse-controls">
        <div class="controls-left">
          <!-- 移动端打开考点目录按钮 -->
          <button class="ctrl-btn drawer-trigger-btn" @click="isDrawerOpen = true">
            <span>📋</span>
            <span class="btn-text">目录 ({{ currentIndex + 1 }}/{{ filteredCards.length }}) ▾</span>
          </button>

          <!-- 桌面端切卡按钮 -->
          <div class="desktop-arrows">
            <button class="ctrl-btn" :disabled="currentIndex <= 0" @click="prevCard">
              ◀ 上一条
            </button>
            <span class="index-indicator">{{ currentIndex + 1 }} / {{ filteredCards.length }}</span>
            <button class="ctrl-btn" :disabled="currentIndex >= filteredCards.length - 1" @click="nextCard">
              下一条 ▶
            </button>
          </div>
        </div>

        <div class="controls-right">
          <!-- 随卡背诵遮挡切换器 -->
          <div class="cloze-mode-stepper" title="切换背诵遮挡模式">
            <button
              v-for="m in [
                { key: 'none', label: '原文' },
                { key: 'keyword', label: '挖词' },
                { key: 'random', label: '随机' },
                { key: 'full', label: '全遮' }
              ]"
              :key="m.key"
              :class="['mode-step-btn', { active: browseClozeMode === m.key }]"
              @click="browseClozeMode = m.key"
            >{{ m.label }}</button>
          </div>

          <!-- 快捷字号缩放 -->
          <div class="font-stepper" title="切换显示字号">
            <button 
              :class="['font-btn', { active: fontSize === 'small' }]" 
              @click="setFontSize('small')"
            >小</button>
            <button 
              :class="['font-btn', { active: fontSize === 'medium' }]" 
              @click="setFontSize('medium')"
            >中</button>
            <button 
              :class="['font-btn', { active: fontSize === 'large' }]" 
              @click="setFontSize('large')"
            >大</button>
          </div>
        </div>
      </div>

      <!-- 核心卡片展示区 (支持手机手势左右滑动手势切卡) -->
      <div 
        ref="cardAreaRef" 
        class="card-display-area"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <!-- 移动端手势滑动提示条 -->
        <div class="swipe-hint">
          <span>👈 左右滑动可无缝切换考点 👉</span>
        </div>

        <CardViewer 
          v-if="currentCard"
          :card="currentCard"
          :mode="browseClozeMode"
          :font-size="fontSize"
          :is-favorite="isFavorite(currentCard.id)"
          @toggle-fav="toggleFavorite"
          @view-image="$emit('view-image', $event)"
        />
      </div>

      <!-- 移动端吸底大拇指友好切卡栏 -->
      <div class="mobile-bottom-bar">
        <button 
          class="mobile-nav-btn prev-btn" 
          :disabled="currentIndex <= 0" 
          @click="prevCard"
        >
          <span>◀ 上一卡</span>
        </button>

        <div class="mobile-index-chip" @click="isDrawerOpen = true">
          <span class="chip-curr">{{ currentIndex + 1 }}</span>
          <span class="chip-sep">/</span>
          <span class="chip-total">{{ filteredCards.length }} ▾</span>
        </div>

        <button 
          class="mobile-nav-btn next-btn" 
          :disabled="currentIndex >= filteredCards.length - 1" 
          @click="nextCard"
        >
          <span>下一卡 ▶</span>
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import CardViewer from '../components/CardViewer.vue'
import { getAllCards, useUserState } from '../services/storage/userState'

const props = defineProps({
  fontSize: { type: String, default: 'medium' },
  initialCardId: { type: String, default: '' }
})

const emit = defineEmits(['view-image', 'start-recite', 'change-font-size', 'card-changed'])

const { state, toggleFavorite, updateSettings } = useUserState()
const allCards = getAllCards()

const isDrawerOpen = ref(false)
const searchQuery = ref('')
const selectedSubject = ref('全部')
const browseClozeMode = ref('none')

function getInitialCard() {
  if (props.initialCardId) {
    const target = allCards.find(c => c.id === props.initialCardId)
    if (target) return target
  }
  try {
    const savedCardId = localStorage.getItem('zhengz_last_browse_card')
    if (savedCardId) {
      const target = allCards.find(c => c.id === savedCardId)
      if (target) return target
    }
  } catch (e) {}
  return allCards[0] || null
}

const currentCard = ref(getInitialCard())
const cardAreaRef = ref(null)

const subjects = ['全部', '马原', '政经', '史纲', '其他']

const isFavorite = (id) => !!state.records[id]?.isFavorite
const isMistake = (id) => !!state.records[id]?.inMistakeBook

// 监听当前卡片变化，持久化并通知父组件同步 URL
watch(currentCard, (newCard) => {
  if (newCard) {
    try {
      localStorage.setItem('zhengz_last_browse_card', newCard.id)
    } catch (e) {}
    emit('card-changed', newCard.id)
  }
}, { immediate: true })

// 外部定位指定卡片
watch(() => props.initialCardId, (newId) => {
  if (newId) {
    const target = allCards.find(c => c.id === newId)
    if (target && target.id !== currentCard.value?.id) {
      currentCard.value = target
    }
  }
})

const filteredCards = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  const sub = selectedSubject.value

  return allCards.filter(c => {
    if (sub !== '全部' && c.subject !== sub) return false
    if (q) {
      const inId = c.id.toLowerCase().includes(q) || c.sourceId.includes(q)
      const inTitle = c.title.toLowerCase().includes(q)
      const inContent = c.content.toLowerCase().includes(q)
      if (!inId && !inTitle && !inContent) return false
    }
    return true
  })
})

const currentIndex = computed(() => {
  if (!currentCard.value) return -1
  return filteredCards.value.findIndex(c => c.id === currentCard.value.id)
})

function scrollToTop() {
  if (cardAreaRef.value) {
    cardAreaRef.value.scrollTop = 0
  }
}

function selectCard(c) {
  currentCard.value = c
  isDrawerOpen.value = false
  scrollToTop()
}

function prevCard() {
  if (currentIndex.value > 0) {
    currentCard.value = filteredCards.value[currentIndex.value - 1]
    scrollToTop()
  }
}

function nextCard() {
  if (currentIndex.value < filteredCards.value.length - 1) {
    currentCard.value = filteredCards.value[currentIndex.value + 1]
    scrollToTop()
  }
}

function setFontSize(lvl) {
  updateSettings({ fontSizeLevel: lvl })
}

// 手机端滑动手势检测：防边缘手势冲突 + 提高防误触阈值 + 兼容双指缩放
let touchStartX = 0
let touchStartY = 0
let touchStartTime = 0
let isEdgeTouch = false
let isMultiTouch = false

function handleTouchStart(e) {
  if (e.touches && e.touches.length > 1) {
    isMultiTouch = true
    return
  }
  isMultiTouch = false
  if (e.changedTouches && e.changedTouches.length > 0) {
    const t = e.changedTouches[0]
    touchStartX = t.clientX
    touchStartY = t.clientY
    touchStartTime = Date.now()
    const screenW = window.innerWidth || document.documentElement.clientWidth
    isEdgeTouch = touchStartX < 40 || touchStartX > screenW - 40
  }
}

function handleTouchMove(e) {
  if (e.touches && e.touches.length > 1) {
    isMultiTouch = true
  }
}

function handleTouchEnd(e) {
  if (isMultiTouch) {
    if (!e.touches || e.touches.length === 0) {
      isMultiTouch = false
    }
    return
  }
  if (e.touches && e.touches.length > 0) return
  if (!e.changedTouches || e.changedTouches.length === 0) return
  if (isEdgeTouch) return

  const t = e.changedTouches[0]
  const deltaX = t.clientX - touchStartX
  const deltaY = t.clientY - touchStartY
  const dt = Date.now() - touchStartTime

  // 水平滑动位移 >= 70px，且水平位移显著超过垂直位移 2 倍，且滑动时长 < 600ms
  if (Math.abs(deltaX) >= 70 && Math.abs(deltaX) > Math.abs(deltaY) * 2.0 && dt < 600) {
    if (deltaX < 0) {
      nextCard()
    } else {
      prevCard()
    }
  }
}
</script>

<style scoped>
.browse-layout {
  display: flex;
  height: calc(100vh - 61px);
  overflow: hidden;
  position: relative;
}

/* 侧边导航目录 */
.browse-sidebar {
  width: 320px;
  background: #ffffff;
  border-right: 1px solid var(--border-card);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 10;
}

.sidebar-header {
  display: none;
  padding: 14px 16px;
  background: var(--bg-beige);
  border-bottom: 1px solid var(--border-light);
  justify-content: space-between;
  align-items: center;
}

.sidebar-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-pill {
  font-size: 11px;
  background: var(--primary-accent-bg);
  color: var(--primary-accent);
  padding: 2px 7px;
  border-radius: 10px;
  font-weight: 700;
}

.drawer-close-btn {
  background: rgba(0,0,0,0.06);
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--text-muted);
}

.search-box {
  padding: 12px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-beige-light);
  position: relative;
}

.search-input {
  width: 100%;
  padding: 9px 30px 9px 12px;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: #ffffff;
}

.search-input:focus {
  outline: 2px solid #bfdbfe;
  border-color: var(--primary-accent);
}

.clear-search-btn {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  color: var(--text-muted);
  font-size: 13px;
  padding: 4px;
}

.subject-tabs {
  display: flex;
  padding: 8px 10px;
  gap: 4px;
  background: #fafaf8;
  border-bottom: 1px solid var(--border-light);
  overflow-x: auto;
}

.sub-tab {
  flex: 1;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  background: transparent;
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  text-align: center;
  font-weight: 500;
}

.sub-tab.active {
  background: var(--bg-beige);
  color: #78350f;
  font-weight: 700;
}

.card-nav-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.nav-card-item {
  padding: 9px 12px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.15s ease;
}

.nav-card-item:hover {
  background: var(--bg-beige-light);
}

.nav-card-item.active {
  background: #fbf5ec;
  border-color: #ebd9bf;
  box-shadow: 0 1px 3px rgba(120, 53, 15, 0.08);
}

.item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 3px;
}

.sid-badge {
  font-size: 11px;
  font-weight: 700;
  color: #78350f;
  background: #fef3c7;
  padding: 1px 6px;
  border-radius: 4px;
}

.item-indicators {
  display: flex;
  align-items: center;
  gap: 4px;
}

.fav-icon {
  color: #d97706;
  font-size: 12px;
}

.mistake-dot {
  color: var(--danger-accent);
  font-size: 16px;
  line-height: 1;
}

.item-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  font-size: 11px;
  color: var(--text-muted);
  display: flex;
  justify-content: space-between;
  margin-top: 3px;
}

.empty-list {
  padding: 30px 10px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}

/* 主体浏览区 */
.browse-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-warm);
  position: relative;
}

.browse-controls {
  padding: 10px 20px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 5;
}

.controls-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.controls-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.drawer-trigger-btn {
  display: none;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--text-main);
  background: var(--bg-beige);
  border: 1px solid var(--border-card);
  padding: 7px 12px;
  border-radius: var(--radius-sm);
}

.desktop-arrows {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ctrl-btn {
  background: #ffffff;
  border: 1px solid var(--border-card);
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-regular);
  display: flex;
  align-items: center;
  gap: 4px;
}

.ctrl-btn:hover:not(:disabled) {
  background: var(--bg-beige-light);
}

.ctrl-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.index-indicator {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 600;
}

.cloze-mode-stepper {
  display: flex;
  background: var(--bg-beige-light);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  padding: 2px;
}

.mode-step-btn {
  padding: 4px 8px;
  background: transparent;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  border-radius: 4px;
  white-space: nowrap;
}

.mode-step-btn.active {
  background: var(--primary-accent);
  color: #ffffff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.font-stepper {
  display: flex;
  background: var(--bg-beige-light);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  padding: 2px;
}

.font-btn {
  padding: 4px 8px;
  background: transparent;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  border-radius: 4px;
}

.font-btn.active {
  background: #ffffff;
  color: var(--primary-accent);
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}

.card-display-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  max-width: 860px;
  width: 100%;
  margin: 0 auto;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.swipe-hint {
  display: none;
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

/* 移动端吸底条：紧凑且防浏览器底栏遮挡 */
.mobile-bottom-bar {
  display: none;
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--border-card);
  padding: 8px 12px calc(12px + env(safe-area-inset-bottom, 10px));
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  z-index: 50;
  box-shadow: 0 -4px 16px rgba(0,0,0,0.06);
}

.mobile-nav-btn {
  flex: 1;
  max-width: 115px;
  padding: 8px 10px;
  background: #ffffff;
  border: 1px solid var(--border-card);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-nav-btn:disabled {
  opacity: 0.35;
}

.mobile-index-chip {
  padding: 6px 14px;
  background: var(--bg-beige);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  color: #78350f;
  cursor: pointer;
  user-select: none;
}

.chip-sep {
  margin: 0 3px;
  color: var(--text-muted);
}

/* 移动端抽屉遮罩 */
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  z-index: 999;
}

/* ================= 移动端适配 (< 768px) ================= */
@media (max-width: 768px) {
  .browse-layout {
    height: calc(100vh - 52px);
    height: calc(100dvh - 52px);
  }

  /* 侧边栏转换为全高滑动抽屉 */
  .browse-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 84%;
    max-width: 320px;
    height: 100vh;
    height: 100dvh;
    z-index: 1000;
    transform: translateX(-100%);
    box-shadow: none;
  }

  .browse-sidebar.drawer-open {
    transform: translateX(0);
    box-shadow: 4px 0 25px rgba(0, 0, 0, 0.2);
  }

  .sidebar-header {
    display: flex;
  }

  .drawer-trigger-btn {
    display: flex;
    padding: 5px 9px;
    font-size: 12px;
  }

  .desktop-arrows {
    display: none !important;
  }

  .browse-controls {
    padding: 6px 10px;
    gap: 6px;
    flex-wrap: wrap;
  }

  .controls-right {
    gap: 6px;
  }

  .mode-step-btn, .font-btn {
    padding: 4px 6px;
    font-size: 11px;
  }

  .card-display-area {
    padding: 8px 8px calc(86px + env(safe-area-inset-bottom, 16px)) 8px;
    touch-action: pan-y pinch-zoom;
  }

  .swipe-hint {
    display: block;
    font-size: 10.5px;
    margin-bottom: 6px;
  }

  .mobile-bottom-bar {
    display: flex !important;
  }
}
</style>
