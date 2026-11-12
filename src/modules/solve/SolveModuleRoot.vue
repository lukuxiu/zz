<template>
  <div class="solve-module-root">
    <!-- 解题刷题模块内部统一导航栏 -->
    <SolveNav 
      :current-sub-tab="currentSubTab"
      :mistake-count="mistakeQuestions.length"
      @switch-sub-tab="switchSubTab"
    />

    <!-- 内容子视口 -->
    <main class="solve-module-content">
      <!-- 1. 方法库 -->
      <MethodsView 
        v-if="currentSubTab === 'methods'"
        @start-practice="goToPracticeWithMethod"
      />

      <!-- 2. 分类刷题 -->
      <PracticeView 
        v-else-if="currentSubTab === 'practice'"
        :initial-method-id="practiceMethodId"
        @view-method="goToPracticeWithMethod"
      />

      <!-- 3. 盲测识坑 -->
      <BlindPracticeView 
        v-else-if="currentSubTab === 'blind'"
        @view-method="goToPracticeWithMethod"
      />

      <!-- 4. 限时模考 -->
      <MockPracticeView 
        v-else-if="currentSubTab === 'mock'"
        @switch-tab="switchSubTab"
      />

      <!-- 5. 统计看板 -->
      <DashboardView 
        v-else-if="currentSubTab === 'dashboard'"
        @start-practice="goToPracticeWithMethod"
      />

      <!-- 6. 解题错题本 -->
      <SolveMistakesView 
        v-else-if="currentSubTab === 'mistakes'"
        @view-method="goToPracticeWithMethod"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import SolveNav from './components/SolveNav.vue'
import MethodsView from './views/MethodsView.vue'
import PracticeView from './views/PracticeView.vue'
import BlindPracticeView from './views/BlindPracticeView.vue'
import MockPracticeView from './views/MockPracticeView.vue'
import DashboardView from './views/DashboardView.vue'
import SolveMistakesView from './views/SolveMistakesView.vue'
import { useSolveState } from './services/solveState'

const props = defineProps({
  initialSubTab: {
    type: String,
    default: 'methods'
  },
  initialMethodId: {
    type: String,
    default: 'all'
  }
})

const emit = defineEmits(['update-route'])

const { mistakeQuestions } = useSolveState()

const currentSubTab = ref(props.initialSubTab || 'methods')
const practiceMethodId = ref(props.initialMethodId || 'all')

watch(() => props.initialSubTab, (newTab) => {
  if (newTab && newTab !== currentSubTab.value) {
    currentSubTab.value = newTab
  }
})

watch(() => props.initialMethodId, (newMId) => {
  if (newMId) {
    practiceMethodId.value = newMId
  }
})

function switchSubTab(tab) {
  currentSubTab.value = tab
  emit('update-route', { subTab: tab, methodId: practiceMethodId.value })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToPracticeWithMethod(mid) {
  practiceMethodId.value = mid
  currentSubTab.value = 'practice'
  emit('update-route', { subTab: 'practice', methodId: mid })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
.solve-module-root {
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background-color: var(--bg-warm);
}

.solve-module-content {
  flex: 1;
}
</style>
