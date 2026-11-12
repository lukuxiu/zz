<template>
  <div class="app-layout">
    <!-- 顶部统一导航栏 -->
    <Navbar 
      :current-tab="currentTab"
      :due-count="dueCards.length"
      :mistake-count="mistakeCards.length"
      @navigate="switchTab"
      @open-settings="showSettingsModal = true"
    />

    <!-- 内容主视口 -->
    <div class="app-content">
      <!-- 首页 -->
      <HomeView 
        v-if="currentTab === 'home'" 
        @navigate="switchTab"
        @start-card-recite="startReciteSingle"
      />

      <!-- 知识库浏览 -->
      <BrowseView 
        v-else-if="currentTab === 'browse'"
        :font-size="state.settings.fontSizeLevel"
        :initial-card-id="browseTargetId"
        @view-image="openImageModal"
        @start-recite="startReciteSingle"
        @card-changed="onBrowseCardChanged"
      />

      <!-- 智能背诵 -->
      <ReciteView 
        v-else-if="currentTab === 'recite'"
        :font-size="state.settings.fontSizeLevel"
        :default-mode="state.settings.defaultClozeMode"
        :target-card-id="reciteTargetId"
        @navigate="switchTab"
        @view-image="openImageModal"
      />

      <!-- 随机抽查 -->
      <QuizView 
        v-else-if="currentTab === 'quiz'"
        :font-size="state.settings.fontSizeLevel"
        @view-image="openImageModal"
      />

      <!-- 错题本 -->
      <MistakesView 
        v-else-if="currentTab === 'mistakes'"
        @view-image="openImageModal"
        @recite-single="startReciteSingle"
        @start-batch-recite="startReciteSingle"
      />

      <!-- 解题方法刷题模块 -->
      <SolveModuleRoot 
        v-else-if="currentTab === 'solve'"
        :initial-sub-tab="solveSubTab"
        :initial-method-id="solveMethodId"
        @update-route="handleSolveRouteChange"
      />
    </div>

    <!-- PDF 原文裁切大图弹窗 -->
    <ImageModal 
      :visible="showImageModal"
      :card="activeImageCard"
      @close="showImageModal = false"
    />

    <!-- 数据备份与系统设置弹窗 -->
    <DataBackupModal 
      :visible="showSettingsModal"
      :current-font-size="state.settings.fontSizeLevel"
      :current-default-mode="state.settings.defaultClozeMode"
      @change-font-size="updateFontSize"
      @change-default-mode="updateDefaultMode"
      @close="showSettingsModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, defineAsyncComponent } from 'vue'
import Navbar from './components/Navbar.vue'
import HomeView from './views/HomeView.vue'

const BrowseView = defineAsyncComponent(() => import('./views/BrowseView.vue'))
const ReciteView = defineAsyncComponent(() => import('./views/ReciteView.vue'))
const QuizView = defineAsyncComponent(() => import('./views/QuizView.vue'))
const MistakesView = defineAsyncComponent(() => import('./views/MistakesView.vue'))
const SolveModuleRoot = defineAsyncComponent(() => import('./modules/solve/SolveModuleRoot.vue'))
const ImageModal = defineAsyncComponent(() => import('./components/ImageModal.vue'))
const DataBackupModal = defineAsyncComponent(() => import('./components/DataBackupModal.vue'))

import { setKnowledgeCards, useUserState } from './services/storage/userState'
import knowledgeData from '../data/knowledge.json'

const VALID_TABS = ['home', 'browse', 'recite', 'quiz', 'mistakes', 'solve']

function parseHash() {
  try {
    const rawHash = window.location.hash.replace(/^#\/?/, '')
    if (!rawHash) return null
    const [pathPart, queryPart] = rawHash.split('?')
    const segments = pathPart.split('/')
    const rootPath = segments[0]

    let tab = 'browse'
    let subTab = 'methods'
    let methodId = 'all'
    let cardId = ''

    if (['home', 'browse', 'recite', 'quiz', 'mistakes'].includes(rootPath)) {
      tab = rootPath
    } else if (['solve', 'methods', 'practice', 'blind', 'mock', 'dashboard', 'solve-mistakes'].includes(rootPath)) {
      tab = 'solve'
      if (rootPath === 'practice') {
        subTab = 'practice'
        if (segments[1]) methodId = segments[1]
      } else if (rootPath === 'solve-mistakes') {
        subTab = 'mistakes'
      } else if (rootPath !== 'solve') {
        subTab = rootPath
      }
    }

    if (queryPart) {
      const params = new URLSearchParams(queryPart)
      cardId = params.get('card') || ''
      if (params.get('method')) {
        methodId = params.get('method')
      }
    }
    return { tab, subTab, methodId, cardId }
  } catch (e) {
    return null
  }
}

function getInitialState() {
  const fromHash = parseHash()
  if (fromHash && fromHash.tab) {
    return {
      tab: fromHash.tab,
      subTab: fromHash.subTab || 'methods',
      methodId: fromHash.methodId || 'all',
      cardId: fromHash.cardId || (typeof localStorage !== 'undefined' ? localStorage.getItem('zhengz_last_browse_card') || '' : '')
    }
  }
  let savedTab = 'browse'
  let savedCardId = ''
  let savedSubTab = 'methods'
  let savedMethodId = 'all'
  try {
    savedTab = localStorage.getItem('zhengz_active_tab') || 'home'
    if (!['home', 'browse', 'recite', 'quiz', 'mistakes', 'solve'].includes(savedTab)) savedTab = 'home'
    savedCardId = localStorage.getItem('zhengz_last_browse_card') || ''
    savedSubTab = localStorage.getItem('solve_active_subtab') || 'methods'
  } catch (e) {}
  return {
    tab: savedTab,
    subTab: savedSubTab,
    methodId: savedMethodId,
    cardId: savedCardId
  }
}

const initial = getInitialState()
const currentTab = ref(initial.tab)
const solveSubTab = ref(initial.subTab)
const solveMethodId = ref(initial.methodId)
const browseTargetId = ref(initial.cardId)
const reciteTargetId = ref('')

const showImageModal = ref(false)
const activeImageCard = ref(null)
const showSettingsModal = ref(false)

const { state, dueCards, mistakeCards, updateSettings } = useUserState()

function updateUrlAndStorage(tab, cardId = null) {
  try {
    localStorage.setItem('zhengz_active_tab', tab)
    let hashStr = `#/${tab}`
    if (tab === 'browse') {
      const cId = cardId || browseTargetId.value || localStorage.getItem('zhengz_last_browse_card')
      if (cId) {
        hashStr += `?card=${encodeURIComponent(cId)}`
      }
    } else if (tab === 'solve') {
      localStorage.setItem('solve_active_subtab', solveSubTab.value)
      if (solveSubTab.value === 'practice' && solveMethodId.value && solveMethodId.value !== 'all') {
        hashStr = `#/practice/${solveMethodId.value}`
      } else if (solveSubTab.value === 'mistakes') {
        hashStr = `#/solve-mistakes`
      } else {
        hashStr = `#/${solveSubTab.value}`
      }
    }
    if (window.location.hash !== hashStr) {
      window.history.replaceState(null, '', hashStr)
    }
  } catch (e) {}
}

function switchTab(tab) {
  currentTab.value = tab
  updateUrlAndStorage(tab)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleSolveRouteChange({ subTab, methodId }) {
  solveSubTab.value = subTab
  if (methodId) solveMethodId.value = methodId
  updateUrlAndStorage('solve')
}

function onBrowseCardChanged(cardId) {
  browseTargetId.value = cardId
  if (currentTab.value === 'browse') {
    updateUrlAndStorage('browse', cardId)
  }
}

function handleHashChange() {
  const parsed = parseHash()
  if (parsed && parsed.tab) {
    currentTab.value = parsed.tab
    if (parsed.subTab) solveSubTab.value = parsed.subTab
    if (parsed.methodId) solveMethodId.value = parsed.methodId
    if (parsed.cardId) browseTargetId.value = parsed.cardId
  }
}

// 应用启动时加载知识库数据并恢复路由
onMounted(() => {
  if (knowledgeData && knowledgeData.records) {
    setKnowledgeCards(knowledgeData.records)
  }
  updateUrlAndStorage(currentTab.value, browseTargetId.value)
  window.addEventListener('hashchange', handleHashChange)
})

function startReciteSingle(cardId) {
  reciteTargetId.value = cardId
  currentTab.value = 'recite'
  updateUrlAndStorage('recite')
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openImageModal(card) {
  activeImageCard.value = card
  showImageModal.value = true
}

function updateFontSize(size) {
  updateSettings({ fontSizeLevel: size })
}

function updateDefaultMode(mode) {
  updateSettings({ defaultClozeMode: mode })
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-warm);
}

.app-content {
  flex: 1;
}
</style>
