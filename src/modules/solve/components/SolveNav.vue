<template>
  <div class="solve-nav-bar">
    <div class="solve-nav-inner">
      <button 
        :class="['sub-btn', { active: currentSubTab === 'methods' }]"
        @click="$emit('switch-sub-tab', 'methods')"
      >
        <span class="icon">📚</span>
        <span class="label">方法库</span>
      </button>

      <button 
        :class="['sub-btn', { active: currentSubTab === 'practice' }]"
        @click="$emit('switch-sub-tab', 'practice')"
      >
        <span class="icon">✍️</span>
        <span class="label">分类刷题</span>
      </button>

      <button 
        :class="['sub-btn', { active: currentSubTab === 'blind' }]"
        @click="$emit('switch-sub-tab', 'blind')"
      >
        <span class="icon">🎯</span>
        <span class="label">盲测识坑</span>
      </button>

      <button 
        :class="['sub-btn', { active: currentSubTab === 'mock' }]"
        @click="$emit('switch-sub-tab', 'mock')"
      >
        <span class="icon">⏱️</span>
        <span class="label">限时模考</span>
      </button>

      <button 
        :class="['sub-btn', { active: currentSubTab === 'dashboard' }]"
        @click="$emit('switch-sub-tab', 'dashboard')"
      >
        <span class="icon">📊</span>
        <span class="label">统计看板</span>
      </button>

      <button 
        :class="['sub-btn', { active: currentSubTab === 'mistakes' }]"
        @click="$emit('switch-sub-tab', 'mistakes')"
      >
        <span class="icon">📕</span>
        <span class="label">解题错题</span>
        <span v-if="mistakeCount > 0" class="badge-pill">{{ mistakeCount }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentSubTab: {
    type: String,
    default: 'methods'
  },
  mistakeCount: {
    type: Number,
    default: 0
  }
})

defineEmits(['switch-sub-tab'])
</script>

<style scoped>
.solve-nav-bar {
  background: #ffffff;
  border-bottom: 1px solid var(--border-card);
  padding: 8px 16px;
  position: sticky;
  top: 60px;
  z-index: 90;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

.solve-nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}

.solve-nav-inner::-webkit-scrollbar {
  display: none;
}

.sub-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg-warm);
  border: 1px solid var(--border-light);
  white-space: nowrap;
  transition: all 0.15s ease;
}

.sub-btn:hover {
  color: var(--text-main);
  border-color: var(--border-card);
}

.sub-btn.active {
  background: var(--primary-accent-bg);
  color: var(--primary-accent);
  border-color: var(--primary-accent);
}

.badge-pill {
  background: var(--danger-accent);
  color: #ffffff;
  font-size: 11px;
  font-weight: bold;
  padding: 1px 6px;
  border-radius: 10px;
}

@media (max-width: 768px) {
  .solve-nav-bar {
    padding: 6px 10px;
    top: 52px;
  }
  .sub-btn {
    padding: 5px 11px;
    font-size: 12px;
  }
}
</style>
